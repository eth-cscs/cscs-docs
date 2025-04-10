[](){#ref-uenv-pytorch}
# PyTorch

The PyTorch software stack was designed with the intention of being able to run
[Megatron-LM](https://github.com/NVIDIA/Megatron-LM) based pre-training
workloads out of the box. Thus, it comes with batteries included and does not
just provide the bare [PyTorch framework](https://github.com/pytorch/pytorch).


!!! note "uenvs"

    [PyTorch][ref-uenv-pytorch] is provided via [uenv][ref-uenv].
    Please have a look at the [uenv documentation][ref-uenv] for more information about uenvs and how to use them.

## Versioning

The PyTorch uenv is versioned according to the PyTorch version it provides.

| version   | node types | system                  |
|-----------|------------|-------------------------|
| v2.6.0     | gh200      | clariden, daint         |

=== "v2.6.0"

    ??? info "non-Python packages exposed via the `default` view"

        | Package             | Version          |
        |---------------------|------------------|
        | abseil-cpp | 20240722.0 |
        | alsa-lib | 1.2.3.2 |
        | autoconf | 2.72 |
        | automake | 1.16.5 |
        | aws-ofi-nccl | 1.14.0 |
        | berkeley-db | 18.1.40 |
        | bison | 3.8.2 |
        | boost | 1.86.0 |
        | bzip2 | 1.0.8 |
        | ca-certificates-mozilla | 2023-05-30 |
        | cmake | 3.30.5 |
        | cpuinfo | 2024-09-26 |
        | cray-gtl | 8.1.32 |
        | cray-mpich | 8.1.32 |
        | cray-pals | 1.3.2 |
        | cray-pmi | 6.1.15 |
        | cuda | 12.6.0 |
        | cudnn | 9.2.0.82-12 |
        | curl | 8.10.1 |
        | cutensor | 2.0.1.2 |
        | diffutils | 3.10 |
        | eigen | 3.4.0 |
        | elfutils | 0.191 |
        | expat | 2.6.4 |
        | faiss | 1.8.0 |
        | ffmpeg | 5.1.4 |
        | fftw | 3.3.10 |
        | findutils | 4.9.0 |
        | flac | 1.4.3 |
        | fmt | 11.0.2 |
        | fp16 | 2020-05-14 |
        | fxdiv | 2020-04-17 |
        | gawk | 4.2.1 |
        | gcc | 13.3.0 |
        | gcc-runtime | 13.3.0 |
        | gdb | 15.2 |
        | gdbm | 1.23 |
        | gettext | 0.22.5 |
        | git | 2.47.0 |
        | glibc | 2.31 |
        | gloo | 2023-12-03 |
        | gmake | 4.4.1 |
        | gmp | 6.3.0 |
        | gmp | 6.3.0 |
        | gnuconfig | 2024-07-27 |
        | googletest | 1.12.1 |
        | gperftools | 2.16 |
        | hdf5 | 1.14.5 |
        | hwloc | 2.11.1 |
        | hydra | 4.2.1 |
        | krb5 | 1.21.3 |
        | libaio | 0.3.113 |
        | libarchive | 3.7.6 |
        | libbsd | 0.12.2 |
        | libedit | 3.1-20240808 |
        | libfabric | 1.15.2.0 |
        | libffi | 3.4.6 |
        | libgit2 | 1.8.0 |
        | libiconv | 1.17 |
        | libidn2 | 2.3.7 |
        | libjpeg-turbo | 3.0.3 |
        | libmd | 1.0.4 |
        | libmicrohttpd | 0.9.50 |
        | libogg | 1.3.5 |
        | libpciaccess | 0.17 |
        | libpng | 1.6.39 |
        | libsigsegv | 2.14 |
        | libssh2 | 1.11.1 |
        | libtool | 2.4.6 |
        | libtool | 2.4.7 |
        | libunistring | 1.2 |
        | libuv | 1.48.0 |
        | libvorbis | 1.3.7 |
        | libxcrypt | 4.4.35 |
        | libxml2 | 2.13.4 |
        | libyaml | 0.2.5 |
        | lz4 | 1.10.0 |
        | lzo | 2.10 |
        | m4 | 1.4.19 |
        | magma | master |
        | meson | 1.5.1 |
        | mpc | 1.3.1 |
        | mpfr | 4.2.1 |
        | nasm | 2.16.03 |
        | nccl | 2.26.2-1 |
        | nccl-tests | 2.13.6 |
        | ncurses | 6.5 |
        | nghttp2 | 1.63.0 |
        | ninja | 1.12.1 |
        | numactl | 2.0.18 |
        | nvtx | 3.1.0 |
        | openblas | 0.3.28 |
        | openssh | 9.9p1 |
        | openssl | 3.4.0 |
        | opus | 1.5.2 |
        | osu-micro-benchmarks | 7.5 |
        | patchelf | 0.17.2 |
        | pcre | 8.45 |
        | pcre2 | 10.44 |
        | perl | 5.40.0 |
        | pigz | 2.8 |
        | pkgconf | 2.2.0 |
        | protobuf | 3.28.2 |
        | psimd | 2020-05-17 |
        | pthreadpool | 2023-08-29 |
        | python | 3.13.0 |
        | python-venv | 1.0 |
        | rdma-core | 31.0 |
        | re2c | 3.1 |
        | readline | 8.2 |
        | rust | 1.81.0 |
        | rust-bootstrap | 1.81.0 |
        | sentencepiece | 0.1.99 |
        | sleef | 3.6.0_2024-03-20 |
        | sox | 14.4.2 |
        | sqlite | 3.46.0 |
        | swig | 4.1.1 |
        | tar | 1.34 |
        | texinfo | 7.1 |
        | util-linux-uuid | 2.40.2 |
        | util-macros | 1.20.1 |
        | valgrind | 3.23.0 |
        | xpmem | 2.9.6 |
        | xz | 5.4.6 |
        | yasm | 1.3.0 |
        | zlib-ng | 2.2.1 |
        | zstd | 1.5.6 |

    ??? info "Python packages exposed via the `default` view"

        | Package             | Version          |
        |---------------------|------------------|
        | aniso8601           | 9.0.1 |
        | annotated-types     | 0.7.0 |
        | apex                | 0.1 |
        | appdirs             | 1.4.4 |
        | astunparse          | 1.6.3 |
        | blinker             | 1.6.2 |
        | certifi             | 2023.7.22 |
        | charset-normalizer  | 3.3.0 |
        | click               | 8.1.7 |
        | coverage            | 7.2.6 |
        | Cython              | 3.0.11 |
        | docker-pycreds      | 0.4.1 |
        | donfig              | 0.8.1.post1 |
        | einops              | 0.8.0 |
        | faiss               | 1.8.0 |
        | filelock            | 3.12.4 |
        | flash_attn          | 2.6.3 |
        | Flask               | 2.3.2 |
        | Flask-RESTful       | 0.3.9 |
        | fsspec              | 2024.5.0 |
        | gitdb               | 4.0.9 |
        | GitPython           | 3.1.40 |
        | huggingface_hub     | 0.26.2 |
        | idna                | 3.4 |
        | importlib_metadata  | 7.0.1 |
        | iniconfig           | 2.0.0 |
        | itsdangerous        | 2.1.2 |
        | Jinja2              | 3.1.4 |
        | joblib              | 1.2.0 |
        | lightning-utilities | 0.11.2 |
        | MarkupSafe          | 2.1.3 |
        | mpmath              | 1.3.0 |
        | networkx            | 3.1 |
        | nltk                | 3.9.1 |
        | numcodecs           | 0.15.0 |
        | numpy               | 2.1.2 |
        | nvtx                | 0.2.5 |
        | packaging           | 24.1 |
        | pillow              | 11.0.0 |
        | pip                 | 23.1.2 |
        | platformdirs        | 3.10.0 |
        | pluggy              | 1.5.0 |
        | protobuf            | 5.28.2 |
        | psutil              | 7.0.0 |
        | pybind11            | 2.13.6 |
        | pydantic            | 2.10.1 |
        | pydantic_core       | 2.27.1 |
        | pytest              | 8.2.1 |
        | pytest-asyncio      | 0.23.5 |
        | pytest-cov          | 4.0.0 |
        | pytest-mock         | 3.10.0 |
        | pytest-random-order | 1.0.4 |
        | pytz                | 2023.3 |
        | PyYAML              | 6.0.2 |
        | regex               | 2022.8.17 |
        | requests            | 2.32.3 |
        | safetensors         | 0.4.5 |
        | sentencepiece       | 0.1.99 |
        | sentry-sdk          | 2.22.0 |
        | setproctitle        | 1.1.10 |
        | setuptools          | 69.2.0 |
        | six                 | 1.16.0 |
        | smmap               | 5.0.0 |
        | sympy               | 1.13.1 |
        | tiktoken            | 0.4.0 |
        | tokenizers          | 0.21.0 |
        | torch               | 2.6.0 |
        | torchaudio          | 2.6.0a0+d883142 |
        | torchmetrics        | 1.5.2 |
        | torchvision         | 0.21.0 |
        | tqdm                | 4.66.3 |
        | transformer_engine  | 2.3.0.dev0+dd4c17d |
        | transformers        | 4.48.3 |
        | triton              | 3.2.0+gitc802bb4f |
        | typing_extensions   | 4.12.2 |
        | urllib3             | 2.1.0 |
        | versioneer          | 0.29 |
        | wandb               | 0.19.9 |
        | Werkzeug            | 3.0.4 |
        | wheel               | 0.41.2 |
        | wrapt               | 1.15.0 |
        | zarr                | 3.0.1 |
        | zipp                | 3.17.0 |


[](){#ref-uenv-pytorch-how-to-use}
## How to use

There are two ways to access the software provided by the uenv, once it has been started.

=== "the default view"

    The simplest way to get started is to use the `default` file system view,
    which automatically loads all of the packages when the uenv is started.

    !!! example "test mpi compilers and python provided by pytorch/v2.6.0"
        ```console
        # start using the default view
        $ uenv start pytorch/v2.6.0:v1 --view=default

        # the python executable provided by the uenv is the default, and is a recent version
        $ which python
        /user-environment/env/default/bin/python
        $ python --version
        Python 3.13.0

        # the mpi compiler wrappers are also available
        $ which mpicc
        /user-environment/env/default/bin/mpicc
        $ mpicc --version
        gcc (Spack GCC) 13.3.0
        $ gcc --version # the compiler wrapper uses the gcc provided by the uenv
        gcc (Spack GCC) 13.3.0

        # exit the uenv
        exit
        ```

=== "Spack"

    The pytorch uenv can also be used as a base for building software with
    Spack, because it provides compilers, MPI, Python and common packages like
    hdf5.

    [Check out the guide for using Spack with uenv][ref-building-uenv-spack].

[](){#ref-uenv-pytorch-venv}
## Adding Python packages on top of the uenv

Uenvs are read-only, and cannot be modified. However, it is possible to add Python packages on top of the uenv using virtual environments.

!!! example "creating a virtual environment on top of the uenv"
    ```console
    # start the uenv
    $ uenv start pytorch/v2.6.0:v1 --view=default

    # create a virtual environment
    $ python -m venv ./my-venv

    # activate the virtual environment
    $ source ./my-venv/bin/activate

    # install packages using pip
    (my-venv) $ pip install <package>

    # deactivate the virtual environment
    (my-venv) $ deactivate

    # exit the uenv
    exit
    ```

Alternatively one can use the uenv as [upstream Spack
instance][ref-building-uenv-spack] to to add both Python and non-Python
packages, however, this workflow is more involved and intended for advanced
Spack users.


## Running PyTorch jobs with SLURM

!!! example "slurm sbatch script"
    ```bash
    #!/bin/bash
    #SBATCH --job-name=myjob
    #SBATCH --nodes=1
    #SBATCH --ntasks-per-node=4
    #SBATCH --cpus-per-task=72
    #SBATCH --time=00:30:00
    #SBATCH --uenv=pytorch/v2.6.0:/user-environment
    #SBATCH --view=default

    #################################
    # OpenMP environment variables #
    #################################
    export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK  # (1)!

    #################################
    # PyTorch environment variables #
    #################################
    export MASTER_ADDR=$(hostname) # (2)!
    export MASTER_PORT=6000
    export WORLD_SIZE=$SLURM_NPROCS
    export TORCH_NCCL_ASYNC_ERROR_HANDLING=1 # (3)!

    #################################
    # MPICH environment variables   #
    #################################
    export MPICH_GPU_SUPPORT_ENABLED=0 # (4)!

    #################################
    # CUDA environment variables    #
    #################################
    export CUDA_CACHE_DISABLE=1 # (5)!

    ############################################
    # NCCL and Fabric environment variables    #
    ############################################
    export NCCL_NET="AWS Libfabric" # (6)!
    export NCCL_NET_GDR_LEVEL=PHB
    export NCCL_CROSS_NIC=1
    export FI_CXI_DISABLE_HOST_REGISTER=1
    export FI_MR_CACHE_MONITOR=userfaultfd
    export FI_CXI_DEFAULT_CQ_SIZE=131072
    export FI_CXI_DEFAULT_TX_SIZE=32768
    export FI_CXI_RX_MATCH_MODE=software

    # (7)!
    # (8)!
    srun bash -c "
        export RANK=\$SLURM_PROCID
        export LOCAL_RANK=\$SLURM_LOCALID
        . ./my-venv/bin/activate
        python myscript.py
    "
    ```

    1. Only set `OMP_NUM_THREADS` if you are using OpenMP in your code.
    2. These variables are used by PyTorch to initialize the distributed
       backend. The `MASTER_ADDR` and `MASTER_PORT` variables are used to
       determine the address and port of the master node. Additionally we also need
       `RANK` and `LOCAL_RANK` but these must be set per-process, see below.
    3. Enable more graceful exception handling, see [PyTorch
       documentation](https://pytorch.org/docs/stable/torch_nccl_environment_variables.html)
    4. Disable GPU support in MPICH, as it [can lead to
       deadlocks](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/mpi.html#inter-gpu-communication-with-cuda-aware-mpi)
       when using together with nccl.
    5. Avoid writing JITed binaries to the (distributed) file system, which
       could lead to performance issues.
    6. These variables should always be set for correctness and optimal
       performance when using NCCL, see [the detailed
       explanation][ref-communication-nccl].
    7. `RANK` and `LOCAL_RANK` are set per-process by the SLURM job launcher.
    8. Activate the virtual environment created on top of the uenv (if any).
