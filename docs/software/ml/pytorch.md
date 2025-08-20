[](){#ref-software-ml-pytorch}
# PyTorch

PyTorch is available both as a container with the [Container Engine (CE)][ref-container-engine] and a [uenv][ref-uenv] software stack. The best choice for your use case depends on the amount of control required over the lower level libraries.

While NGC provides an optimized build of PyTorch with many dependencies included, uenv allows a more flexible choice of lower level libraries and represents a thinner layer over the host system. Both options can be customized - a container via a Dockerfile and a uenv (in advanced use cases) via its recipe and both, additionally, via Python virtual environments built on top. Due to the simplicity and reproducible performance, containers are generally the recommended default for most users.

[](){#ref-ce-pytorch}
## Running PyTorch with the Container Engine (recommended)

Running PyTorch from a container ensures maximum portability, reproducibility, and ease of use across machines. This is achieved by 

1. selecting an appropriate base image and customizing it in a Dockerfile
2. defining the container runtime environment in an EDF
3. (optionally) extending with a virtual environment
4. submitting jobs with CE in SLURM 

These steps are illustrated in the [machine learning platform tutorials][ref-software-ml-tutorials] and the instructions detailed in the [podman build guide][ref-build-containers].

!!! info "Preliminary steps"
    Before proceeding with the next steps, make sure you have storage for podman configured as in the [build guide][ref-build-containers-configure-podman] and make sure to apply [recommended Lustre settings][ref-guides-storage-lustre] to every directory (e.g. `$SCRATCH/ce-images`) dedicated to container images before importing them with enroot. This is necessary to guarantee good filesystem performance.

    ```bash
    lfs setstripe -E 4M -c 1 -E 64M -c 4 -E -1 -c -1 -S 4M $SCRATCH/ce-images # (1)!
    ```

    1. This makes sure that files stored subsequently end up on the same storage node (up to 4 MB), on 4 storage nodes (between 4 and 64 MB) or are striped across all storage nodes (above 64 MB)


### Select the base image

For most applications, the [PyTorch NGC container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch) is a good base image as PyTorch comes pre-installed with an optimized build including many dependencies. The [Release Notes](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/index.html) give an overview on installed packages and compatibility. This image can be further customized in a Dockerfile and built with podman as detailed in the [podman build guide][ref-build-containers].

### Define Container Runtime Environment

Having built and imported a container image with podman and enroot, the next step is to configure the runtime environment with an environment definition file (EDF). In particular, this includes specifying the image, any directories mounted and a working directory to for the processes in the container to start in as in the [quickstart examples for CE][ref-container-engine].

Besides this, there are specific features relevant for machine learning available through [annotations][ref-ce-annotations], which customize the container at runtime.

* When using NCCL inside the container, you want to include the [aws-ofi-nccl][ref-ce-aws-ofi-hook] plugin which enables the container to interface with the host's libfabric and, thus, make use of Alps Slingshot high-speed interconnect. This is crucial for multi-node communication performance.
* An [SSH annotation][ref-ce-ssh-hook] allows adding a light-weight SSH server to the container without the need to modify the container image

A resulting example TOML file following best practices may look like

```toml  title="$HOME/my-app/ngc-pytorch-my-app-25.06.toml"
image = "${SCRATCH}/ce-images/ngc-pytorch-my-app+25.06.sqsh" # (1)!

mounts = [
    "/capstor",
    "/iopsstor",
    "/users/${USER}/my-app"
] # (2)!

workdir = "${HOME}/my-app" # (3)!

[annotations]
com.hooks.aws_ofi_nccl.enabled = "true" # (4)!
com.hooks.aws_ofi_nccl.variant = "cuda12"

[env]
NCCL_DEBUG = "INFO" # (5)!
CUDA_CACHE_DISABLE = "1" # (6)!
TORCH_NCCL_ASYNC_ERROR_HANDLING = "1" # (7)!
MPICH_GPU_SUPPORT_ENABLED = "0" # (8)!
```

1. It is important to use curly braces for environment variables used in the EDF
2. The path `/users` is not mounted as a whole since it often contains user-specific initialization scripts for the host environment and many frameworks leave temporary data behind that can lead to non-trivial runtime errors when swapping container images. Thus, it is recommended to selectively mount specific subfolders under `${HOME}` if needed.
3. You can use `${PWD}` as an alternative to use the path submitted from when the container is started
4. This enables NCCL installed in the container to make effective use of the Slingshot interconnect on Alps by interfacing with the [AWS OFI NCCL plugin][ref-ce-aws-ofi-hook] with libfabric. While not strictly needed for single node workloads, it is good practice to keep it always on.
5. This makes NCCL output debug info during initialization, which can be useful to spot communication-related issues in a distributed scenario (see later tutorials). Subsystems with debug log can be configured with `NCCL_DEBUG_SUBSYS`.
6. Disable CUDA JIT cache
7. Async error handling when an exception is observed in NCCL watchdog: aborting NCCL communicator and tearing down process upon error
8. Disable GPU support in MPICH, as it can lead to deadlocks when using together with NCCL

??? note "Access to SLURM from inside the container"
    In case access to SLURM is required from inside the container, you can add the following lines to the mounts above:

    ```toml
    ...

    mounts = [
       "/capstor",
       "/iopsstor",
       "/users/${USER}/my-app",
       "/etc/slurm", # (1)!
       "/usr/lib64/libslurm-uenv-mount.so",
       "/etc/container_engine_pyxis.conf"
    ]

    ...
    ```

    1. Enable Slurm commands (together with two subsequent mounts)

!!! note "Best practice for large-scale jobs"

    For stability and reproducibility, use self-contained containers for large scale jobs. Using code mounted from the distributed filesystem may leave compiled artefacts behind that can result in unintentional runtime errors when e.g. swapping the container image. In particular, it is recommended to avoid mounting all of `$HOME`, so that environments are properly isolated and e.g. the Triton cache (that by default ends up in `$HOME/.triton`) resides in an ephemeral location of the filesystem.

!!! note "Collaborating in Git"

     For reproducibility, it is recommended to always track the Dockerfile, EDF and an optional virtual environment specification alongside your application code in a Git repository.

### (Optionally) extend container with virtual environment

While production jobs should include as many dependencies as possible in the container image, during development it can be convenient to manage frequently changing packages in a virtual environment built on top of the container image. This can include both dependencies and actively developed packages (that can be installed in editable mode with `pip install -e .`).

To create such a virtual environment, _inside the container_ use the Python `venv` module with the option `--system-site-packages` to ensure that packages are installed _in addition_ to the existing packages. Without this option, packages may accidentally be re-installed shadowing a version that is already present in the container.
A workflow installing additional packages in a virtual environment may look like this:

```console
[clariden-lnXXX]$ srun -A <ACCOUNT> \
  --environment=./ngc-pytorch-my-app-25.06.toml --pty bash # (1)!
user@nidYYYYYY$ python -m venv --system-site-packages venv-ngc-pt-25.06 # (2)!
user@nidYYYYYY$ source venv-ngc-pt-25.06/bin/activate # (3)!
(venv-ngc-pt-25.06) user@nidYYYYYY$ pip install <package>  # (3)!
(venv-ngc-pt-25.06) user@nidYYYYYY$ exit
```

1. Allocate an interactive session on a compute node
2. Create a virtual environment on top of the existing Python installation in the container (only necessary the first time)
3. Activate the newly created virtual environment (always necessary when running a Slurm job)
4. Install additional packages (only run this from a single process to avoid race conditions)

The changes made to the virtual environment will outlive the container as they are persisted on the distributed filesystem.

!!! note
    Keep in mind that

     * this virtual environment is _specific_ to this particular container and won't actually work unless you are using it from inside this container - it relies on the resources packaged inside the container.
     * every Slurm job making use of this virtual environment will need to activate it first (_inside_ the `srun` command). 


### Submit jobs with the Container Engine in Slurm 

A general template for a Pytorch distributed training job with Slurm in analogy to the [last tutorial][software-ml-llm-nanotron-tutorial] may look like

```bash title="$HOME/my-app/submit-dist-train.sh"
#!/bin/bash
#SBATCH --account=<ACCOUNT>
#SBATCH --job-name=dist-train-ddp
#SBATCH --time=01:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --output=logs/slurm-%x-%j.log
# (1)!

set -x

ulimit -c 0 # (2)!

 # (3)!
 # (4)!
srun -ul --environment=./ngc-pytorch-my-app-25.06.toml bash -c "
    . venv-ngc-pt-25.06/bin/activate  # activate (optional) venv

--8<-- "docs/software/ml/torch_distributed_env_vars"
    python dist-train.py <dist-train-args>
"
```

1. If `#SBATCH --error=...` is not specified, `#SBATCH --output` will also contain stderr (error messages)
2. In case the application crashes, it may leave behind large core dump files that contain an image of the process memory at the time of the crash. While these can be useful for debugging the reason of a specific crash (by e.g. loading them with `cuda-gdb` and looking at the stack trace with `bt`), they may accumulate over time and occupy a large space on the filesystem. For this reason, it is recommended to disable their creation (unless needed) by adding this line.
3. Loading the virtual environment is mandatory within every `srun` command if it is used to manage packages.
4. The environment variables are set to initialize PyTorch's distributed module through the environment (cf. [docs](https://docs.pytorch.org/docs/stable/distributed.html#environment-variable-initialization)).


For further details on execution logic, job monitoring and data management, please refer to the [nanotron tutorial][software-ml-llm-nanotron-tutorial] (which in particular also explains the usage of `torchrun` with Slurm). Make sure to apply [recommended Lustre settings][ref-guides-storage-lustre] to datasets, models and container images persisted to the distributed filesystem.

!!! warning "#SBATCH --environment"
    The operations performed before the `srun` command are executed in the host environment of a single compute node in the allocation. If you need to perform these steps in the container environment as well, you can alternatively use the `#SBATCH --environment=path/to/ngc-pytorch-my-app-25.06.toml` option _instead of_ using `--environment` with `srun`.

    Use of the `--environment` option for `sbatch` is still considered experimental and could result in unexpected behavior. In particular, avoid mixing `#SBATCH --environment` and `srun --environment` in the same job.

    Use of `--environment` is currently only recommended for the `srun` command. 

!!! note "Optimizing large-scale training jobs"
    The following settings were established to **improve compute throughput** of LLM training in `Megatron-LM`:

    * Extensively evaluate all possible parallelization dimensions, including data-, tensor- and pipeline parallelism (including virtual pipeline parallelism) and more, when available. In `Megatron-LM`, avoid using the option '--defer-embedding-wgrad-compute` to defer the embedding gradient computation. Identify storage-related bottlenecks by isolating data loading/generation operations into a separate benchmark.

    * Disabling transparent huge pages and enabling the Nvidia [vboost](https://docs.nvidia.com/nemo-framework/user-guide/latest/performance/performance-guide.html#gpu-core-clock-optimization) feature has been observed to improve performance in large-scale LLM training in `Megatron-LM`. This can be achieved by adding these constraints to the sbatch script:
       ```bash
       #SBATCH -C thp_never&nvidia_vboost_enabled
       ```

    * The argument `--ddp-bucket-size` controls the level of grouping of many small data-parallel communications into bigger ones and setting it to a high value such as can improve throughput (model-dependent, e.g. `10000000000`).

    * If in doubt about communication performance with NCCL at scale, use [nccl-tests](https://github.com/NVIDIA/nccl-tests) with the relevant communication patterns to check if scaling behavior can be reproduced.

    Additionally, consider the **best practice for checkpointing and data management**:

    * Following the advice on [filesystems][ref-storage-fs], write checkpoints (sequential write) to `/capstor/scratch` and place randomly accessed training data (many small random reads) on `/iopsstor/scratch`. Use the [data transfer instructions][ref-data-xfer] to move data to/from `/capstor/store`. Make sure to apply recommended [Lustre settings][ref-guides-storage-lustre] on all directories containing significant amount of data, including those containing container images and managed by other tools (e.g. the HuggingFace cache, see [`HF_HOME`](https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables#hfhome) in the [this tutorial][software-ml-llm-inference-tutorial]).

    * Regularly adjust checkpoint writing intervals to the overhead induced by writing a checkpoint ($T_1$) and the mean time between job failures ($T_2$). As a first order approximation use a checkpointing interval of $\sqrt{2 T_1 T_2}$ (derived by [Young](https://doi.org/10.1145/361147.361115) and [Daly](https://doi.org/10.1016/j.future.2004.11.016)).

    Adjust for **cluster availability**:

    * Submit your jobs with a Slurm time limit compatible with reservations (such as maintenance windows, cf. `scontrol show res`) to be able to get scheduled.


[](){#ref-uenv-pytorch}
## Running PyTorch with a uenv

The PyTorch software stack was designed with the intention of being able to run [Megatron-LM](https://github.com/NVIDIA/Megatron-LM)-based pre-training workloads out of the box.
Thus, it comes with batteries included and does not just provide the bare [PyTorch framework](https://github.com/pytorch/pytorch).

!!! note "uenv"

    [PyTorch][ref-uenv-pytorch] is provided via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.

### Versioning

The PyTorch uenv is versioned according to the PyTorch version it provides.

| version   | node types | system                  |
|-----------|------------|-------------------------|
| v2.6.0     | gh200      | clariden, daint         |

=== "v2.6.0"

    ??? info "non-Python packages exposed via the `default` view"

        | Package             | Version          |
        |---------------------|------------------|
        | `abseil-cpp` | 20240722.0 |
        | `alsa-lib` | 1.2.3.2 |
        | `autoconf` | 2.72 |
        | `automake` | 1.16.5 |
        | `aws-ofi-nccl` | 1.14.0 |
        | `berkeley-db` | 18.1.40 |
        | `bison` | 3.8.2 |
        | `boost` | 1.86.0 |
        | `bzip2` | 1.0.8 |
        | `ca-certificates-mozilla` | 2023-05-30 |
        | `cmake` | 3.30.5 |
        | `cpuinfo` | 2024-09-26 |
        | `cray-gtl` | 8.1.32 |
        | `cray-mpich` | 8.1.32 |
        | `cray-pals` | 1.3.2 |
        | `cray-pmi` | 6.1.15 |
        | `cuda` | 12.6.0 |
        | `cudnn` | 9.2.0.82-12 |
        | `curl` | 8.10.1 |
        | `cutensor` | 2.0.1.2 |
        | `diffutils` | 3.10 |
        | `eigen` | 3.4.0 |
        | `elfutils` | 0.191 |
        | `expat` | 2.6.4 |
        | `faiss` | 1.8.0 |
        | `ffmpeg` | 5.1.4 |
        | `fftw` | 3.3.10 |
        | `findutils` | 4.9.0 |
        | `flac` | 1.4.3 |
        | `fmt` | 11.0.2 |
        | `fp16` | 2020-05-14 |
        | `fxdiv` | 2020-04-17 |
        | `gawk` | 4.2.1 |
        | `gcc` | 13.3.0 |
        | `gcc-runtime` | 13.3.0 |
        | `gdb` | 15.2 |
        | `gdbm` | 1.23 |
        | `gettext` | 0.22.5 |
        | `git` | 2.47.0 |
        | `glibc` | 2.31 |
        | `gloo` | 2023-12-03 |
        | `gmake` | 4.4.1 |
        | `gmp` | 6.3.0 |
        | `gmp` | 6.3.0 |
        | `gnuconfig` | 2024-07-27 |
        | `googletest` | 1.12.1 |
        | `gperftools` | 2.16 |
        | `hdf5` | 1.14.5 |
        | `hwloc` | 2.11.1 |
        | `hydra` | 4.2.1 |
        | `krb5` | 1.21.3 |
        | `libaio` | 0.3.113 |
        | `libarchive` | 3.7.6 |
        | `libbsd` | 0.12.2 |
        | `libedit` | 3.1-20240808 |
        | `libfabric` | 1.15.2.0 |
        | `libffi` | 3.4.6 |
        | `libgit2` | 1.8.0 |
        | `libiconv` | 1.17 |
        | `libidn2` | 2.3.7 |
        | `libjpeg-turbo` | 3.0.3 |
        | `libmd` | 1.0.4 |
        | `libmicrohttpd` | 0.9.50 |
        | `libogg` | 1.3.5 |
        | `libpciaccess` | 0.17 |
        | `libpng` | 1.6.39 |
        | `libsigsegv` | 2.14 |
        | `libssh2` | 1.11.1 |
        | `libtool` | 2.4.6 |
        | `libtool` | 2.4.7 |
        | `libunistring` | 1.2 |
        | `libuv` | 1.48.0 |
        | `libvorbis` | 1.3.7 |
        | `libxcrypt` | 4.4.35 |
        | `libxml2` | 2.13.4 |
        | `libyaml` | 0.2.5 |
        | `lz4` | 1.10.0 |
        | `lzo` | 2.10 |
        | `m`4 | 1.4.19 |
        | `magma` | master |
        | `meson` | 1.5.1 |
        | `mpc` | 1.3.1 |
        | `mpfr` | 4.2.1 |
        | `nasm` | 2.16.03 |
        | `nccl` | 2.26.2-1 |
        | `nccl-tests` | 2.13.6 |
        | `ncurses` | 6.5 |
        | `nghttp2` | 1.63.0 |
        | `ninja` | 1.12.1 |
        | `numactl` | 2.0.18 |
        | `nvtx` | 3.1.0 |
        | `openblas` | 0.3.28 |
        | `openssh` | 9.9p1 |
        | `openssl` | 3.4.0 |
        | `opus` | 1.5.2 |
        | `osu-micro-benchmarks` | 7.5 |
        | `patchelf` | 0.17.2 |
        | `pcre` | 8.45 |
        | `pcre2` | 10.44 |
        | `perl` | 5.40.0 |
        | `pigz` | 2.8 |
        | `pkgconf` | 2.2.0 |
        | `protobuf` | 3.28.2 |
        | `psimd` | 2020-05-17 |
        | `pthreadpool` | 2023-08-29 |
        | `python` | 3.13.0 |
        | `python-venv` | 1.0 |
        | `rdma-core` | 31.0 |
        | `re2c` | 3.1 |
        | `readline` | 8.2 |
        | `rust` | 1.81.0 |
        | `rust-bootstrap` | 1.81.0 |
        | `sentencepiece` | 0.1.99 |
        | `sleef` | 3.6.0_2024-03-20 |
        | `sox` | 14.4.2 |
        | `sqlite` | 3.46.0 |
        | `swig` | 4.1.1 |
        | `tar` | 1.34 |
        | `texinfo` | 7.1 |
        | `util-linux-uuid` | 2.40.2 |
        | `util-macros` | 1.20.1 |
        | `valgrind` | 3.23.0 |
        | `xpmem` | 2.9.6 |
        | `xz` | 5.4.6 |
        | `yasm` | 1.3.0 |
        | `zlib-ng` | 2.2.1 |
        | `zstd` | 1.5.6 |

    ??? info "Python packages exposed via the `default` view"

        | Package             | Version          |
        |---------------------|------------------|
        | `aniso8601`           | 9.0.1 |
        | `annotated-types`     | 0.7.0 |
        | `apex`                | 0.1 |
        | `appdirs`             | 1.4.4 |
        | `astunparse`          | 1.6.3 |
        | `blinker`             | 1.6.2 |
        | `certifi`             | 2023.7.22 |
        | `charset-normalizer`  | 3.3.0 |
        | `click`               | 8.1.7 |
        | `coverage`            | 7.2.6 |
        | `Cython`              | 3.0.11 |
        | `docker-pycreds`      | 0.4.1 |
        | `donfig`              | 0.8.1.post1 |
        | `einops`              | 0.8.0 |
        | `faiss`               | 1.8.0 |
        | `filelock`            | 3.12.4 |
        | `flash_attn`          | 2.6.3 |
        | `Flask`               | 2.3.2 |
        | `Flask-RESTful`       | 0.3.9 |
        | `fsspec`              | 2024.5.0 |
        | `gitdb`               | 4.0.9 |
        | `GitPython`           | 3.1.40 |
        | `huggingface_hub`     | 0.26.2 |
        | `idna`                | 3.4 |
        | `importlib_metadata`  | 7.0.1 |
        | `iniconfig`           | 2.0.0 |
        | `itsdangerous`        | 2.1.2 |
        | `Jinja2`              | 3.1.4 |
        | `joblib`              | 1.2.0 |
        | `lightning-utilities` | 0.11.2 |
        | `MarkupSafe`          | 2.1.3 |
        | `mpmath`              | 1.3.0 |
        | `networkx`            | 3.1 |
        | `nltk`                | 3.9.1 |
        | `numcodecs`           | 0.15.0 |
        | `numpy`               | 2.1.2 |
        | `nvtx`                | 0.2.5 |
        | `packaging`           | 24.1 |
        | `pillow`              | 11.0.0 |
        | `pip`                 | 23.1.2 |
        | `platformdirs`        | 3.10.0 |
        | `pluggy`              | 1.5.0 |
        | `protobuf`            | 5.28.2 |
        | `psutil`              | 7.0.0 |
        | `pybind11`            | 2.13.6 |
        | `pydantic`            | 2.10.1 |
        | `pydantic_core`       | 2.27.1 |
        | `pytest`              | 8.2.1 |
        | `pytest-asyncio`      | 0.23.5 |
        | `pytest-cov`          | 4.0.0 |
        | `pytest-mock`         | 3.10.0 |
        | `pytest-random-order` | 1.0.4 |
        | `pytz`                | 2023.3 |
        | `PyYAML`              | 6.0.2 |
        | `regex`               | 2022.8.17 |
        | `requests`            | 2.32.3 |
        | `safetensors`         | 0.4.5 |
        | `sentencepiece`       | 0.1.99 |
        | `sentry-sdk`          | 2.22.0 |
        | `setproctitle`        | 1.1.10 |
        | `setuptools`          | 69.2.0 |
        | `six`                 | 1.16.0 |
        | `smmap`               | 5.0.0 |
        | `sympy`               | 1.13.1 |
        | `tiktoken`            | 0.4.0 |
        | `tokenizers`          | 0.21.0 |
        | `torch`               | 2.6.0 |
        | `torchaudio`          | 2.6.0a0+d883142 |
        | `torchmetrics`        | 1.5.2 |
        | `torchvision`         | 0.21.0 |
        | `tqdm`                | 4.66.3 |
        | `transformer_engine`  | 2.3.0.dev0+dd4c17d |
        | `transformers`        | 4.48.3 |
        | `triton`              | 3.2.0+gitc802bb4f |
        | `typing_extensions`   | 4.12.2 |
        | `urllib3`             | 2.1.0 |
        | `versioneer`          | 0.29 |
        | `wandb`               | 0.19.9 |
        | `Werkzeug`            | 3.0.4 |
        | `wheel`               | 0.41.2 |
        | `wrapt`               | 1.15.0 |
        | `zarr`                | 3.0.1 |
        | `zipp`                | 3.17.0 |


[](){#ref-uenv-pytorch-how-to-use}
### How to use

There are two ways to access the software provided by the uenv, once it has been started.

=== "the default view"

    The simplest way to get started is to use the `default` file system view, which automatically loads all of the packages when the uenv is started.

    ```console title="Test mpi compilers and python provided by pytorch/v2.6.0"
    $ uenv start pytorch/v2.6.0:v1 --view=default # (1)!

    $ which python # (2)!
    /user-environment/env/default/bin/python
    $ python --version
    Python 3.13.0

    $ which mpicc # (3)!
    /user-environment/env/default/bin/mpicc
    $ mpicc --version
    gcc (Spack GCC) 13.3.0
    $ gcc --version # the compiler wrapper uses the gcc provided by the uenv
    gcc (Spack GCC) 13.3.0

    $ exit # (4)!
    ```

    1. Start using the default view.
    2. The python executable provided by the uenv is the default, and is a recent version.
    3. The MPI compiler wrappers are also available.
    4. Exit the uenv.

=== "Spack"

    The pytorch uenv can also be used as a base for building software with Spack, because it provides compilers, MPI, Python and common packages like HDF5.

    [Check out the guide for using Spack with uenv][ref-building-uenv-spack].

[](){#ref-uenv-pytorch-venv}
### Adding Python packages on top of the uenv

Uenvs are read-only, and cannot be modified. However, it is possible to add Python packages on top of the uenv using virtual environments analogous to the setup with containers.

```console title="Creating a virtual environment on top of the uenv"
$ uenv start pytorch/v2.6.0:v1 --view=default # (1)!

$ python -m venv --system-site-packages venv-uenv-pt2.6-v1 # (2)!

$ source venv-uenv-pt2.6-v1/bin/activate # (3)!

(venv-uenv-pt2.6-v1) $ pip install <package> # (4)!

(venv-uenv-pt2.6-v1) $ deactivate # (5)!

$ exit # (6)!
```

1. The `default` view is recommended, as it loads all the packages provided by the uenv.
   This is important for PyTorch to work correctly, as it relies on the CUDA and NCCL libraries provided by the uenv.
2. The virtual environment is created in the current working directory, and can be activated and deactivated like any other Python virtual environment.
3. Activating the virtual environment will override the Python executable provided by the uenv, and use the one from the virtual environment instead.
   This is important to ensure that the packages installed in the virtual environment are used.
4. The virtual environment can be used to install any Python package.
5. The virtual environment can be deactivated using the `deactivate` command.
   This will restore the original Python executable provided by the uenv.
6. The uenv can be exited using the `exit` command or by typing `ctrl-d`.


!!! note "Squashing the virtual environment"
    Python virtual environments can be slow on the parallel Lustre file system due to the amount of small files and potentially many processes accessing it.
    If this becomes a bottleneck, consider [squashing the venv][ref-guides-storage-venv] into its own memory-mapped, read-only file system to enhance scalability and reduce load times.

??? bug "Python packages from uenv shadowing those in a virtual environment"
    When using uenv with a virtual environment on top, the site-packages under `/user-environment` currently take precedence over those in the activated virtual environment. This is due to the uenv paths being included in the `PYTHONPATH` environment variable. As a consequence, despite installing a different version of a package in the virtual environment from what is available in the uenv, the uenv version will still be imported at runtime. A possible workaround is to prepend the virtual environment's site-packages to `PYTHONPATH` whenever activating the virtual environment.
    ```bash
    export PYTHONPATH="$(python -c 'import site; print(site.getsitepackages()[0])'):$PYTHONPATH"
    ```
    It is recommended to apply this workaround if you are constrained by a Python package version installed in the uenv that you need to change for your application.

Alternatively one can use the uenv as [upstream Spack instance][ref-building-uenv-spack] to to add both Python and non-Python packages.
However, this workflow is more involved and intended for advanced Spack users.

### Running PyTorch jobs with Slurm

```bash title="Slurm sbatch script"
#!/bin/bash
#SBATCH --account=<ACCOUNT>
#SBATCH --job-name=dist-train-ddp
#SBATCH --time=01:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --output=logs/slurm-%x-%j.log
# (1)!
#SBATCH --uenv=pytorch/v2.6.0:/user-environment
#SBATCH --view=default

#################################
# OpenMP environment variables #
#################################
export OMP_NUM_THREADS=8 # (2)!

#################################
# PyTorch environment variables #
#################################
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1 # (3)!
export TRITON_HOME=/dev/shm/ # (4)!

#################################
# MPICH environment variables   #
#################################
export MPICH_GPU_SUPPORT_ENABLED=0 # (5)!

#################################
# CUDA environment variables    #
#################################
export CUDA_CACHE_DISABLE=1 # (6)!

############################################
# NCCL and Fabric environment variables    #
############################################
# (7)!
--8<-- "docs/software/communication/nccl_env_vars"

# (8)!
# (9)!
srun bash -c "
    . ./venv-uenv-pt2.6-v1/bin/activate

--8<-- "docs/software/ml/torch_distributed_env_vars"
    python dist-train.py <dist-train-args>
"
```

1. The `--uenv` option is used to specify the uenv to use for the job.
   The `--view=default` option is used to load all the packages provided by the uenv.
2. Set `OMP_NUM_THREADS` if you are using OpenMP in your code.
   The number of threads should be not greater than the number of cores per task (`$SLURM_CPUS_PER_TASK`).
   The optimal number depends on the workload and should be determined by testing.
   Consider for example that typical workloads using PyTorch may fork the processes, so the number of threads should be around the number of cores per task divided by the number of processes.
3. Enable more graceful exception handling, see [PyTorch documentation](https://pytorch.org/docs/stable/torch_nccl_environment_variables.html)
4. Set the Triton home to a local path (e.g. `/dev/shm`) to avoid writing to the (distributed) file system.
   This is important for performance, as writing to the Lustre file system can be slow due to the amount of small files and potentially many processes accessing it. Avoid this setting with the container engine as it may lead to errors related to mount settings of `/dev/shm` (use a filesystem path inside the container instead).
5. Disable GPU support in MPICH, as it [can lead to deadlocks](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/mpi.html#inter-gpu-communication-with-cuda-aware-mpi) when using together with nccl.
6. Avoid writing JITed binaries to the (distributed) file system, which could lead to performance issues.
7. These variables should always be set for correctness and optimal performance when using NCCL with uenv, see [the detailed explanation][ref-communication-nccl].
8. Activate the virtual environment created on top of the uenv (if any).
   Please follow the guidelines for [python virtual environments with uenv][ref-guides-storage-venv] to enhance scalability and reduce load times. 
9. The environment variables are used by PyTorch to initialize the distributed backend.
   The `MASTER_ADDR`, `MASTER_PORT` variables are used to determine the address and port of the master node.
   Additionally we also need `RANK` and `LOCAL_RANK` and `WORLD_SIZE` to identify the position of each rank within the Slurm step and node, respectively.

