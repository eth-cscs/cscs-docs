[](){#ref-jlab}
# JupyterLab

## Access and setup

The JupyterHub service enables the interactive execution of JupyterLab on [Daint][ref-cluster-daint], [Clariden][ref-cluster-clariden] and [Santis][ref-cluster-santis] on a single compute node.

The service is accessed at [jupyter-daint.cscs.ch](https://jupyter-daint.cscs.ch/), [jupyter-clariden.cscs.ch](https://jupyter-clariden.cscs.ch/) and [jupyter-santis.cscs.ch](https://jupyter-clariden.cscs.ch/), respectively.

Once logged in, you will be redirected to the JupyterHub Spawner Options form, where typical job configuration options can be selected in order to allocate resources. These options might include the type and number of compute nodes, the wall time limit, and your project account.

Single-node notebooks are launched in a dedicated queue, minimizing queueing time. For these notebooks, servers should be up and running within a few minutes. The maximum waiting time for a server to be running is 5 minutes, after which the job will be cancelled and you will be redirected back to the spawner options page. If your single-node server is not spawned within 5 minutes we encourage you to [contact us][ref-get-in-touch].

When resources are granted the page redirects to the JupyterLab session, where you can browse, open and execute notebooks on the compute nodes. A new notebook with a Python 3 kernel can be created with the menu `new` and then `Python 3` . Under `new` it is also possible to create new text files and folders, as well as to open a terminal session on the allocated compute node.

!!! tip "Debugging"
    The log file of a JupyterLab server session is saved on `$HOME` in a file named `slurm-<jobid>.out`. If you encounter problems with your JupyterLab session, the contents of this file can be a good first clue to debug the issue.

??? warning "Unexpected error while saving file: disk I/O error."
    This error message indicates that you have run out of disk quota.
    You can check your quota using the command `quota`.


[](){#ref-jlab-runtime-environment}
## Runtime environment

A Jupyter session can be started with either a [uenv][ref-uenv] or a [container][ref-container-engine] as a base image. The JupyterHub Spawner form provides a set of default images such as the [prgenv-gnu][ref-uenv-prgenv-gnu] uenv or the [NGC Pytorch container][ref-software-ml] to choose from in a dropdown menu. When using uenv, the software stack will be mounted at `/user-environment`, and the specified view will be activated. For a container, the Jupyter session will launch inside the container filesystem with only a select set of paths mounted from the host. Once you have found a suitable option, you can start the session with `Launch JupyterLab`.

??? info "Using remote uenv for the first time."
    If the uenv is not present in the local repository, it will be automatically fetched.
    As a result, JupyterLab may take slightly longer than usual to start.

!!! warning "Ending your interactive session and logging out"
    The Jupyter servers can be shut down through the Hub. To end a JupyterLab session, please select `Hub Control Panel` under the `File` menu and then `Stop My Server`. By contrast, clicking `Logout` will log you out of the server, but the server will continue to run until the Slurm job reaches its maximum wall time.

If the default base images do not meet your requirements, you can specify a custom environment instead. For this purpose, you supply either a custom uenv image/view or CE TOML file under the section `Advanced options` before launching the session. The supported uenvs are compatible with the Jupyter service out of the box, whereas container images typically require the installation of some additional packages. 

??? "Example of a custom Pytorch container"
    A container image based on recent a NGC Pytorch release requires the installation of the following additional packages to be compatible with the Jupyter service:

    ```Dockerfile
    FROM nvcr.io/nvidia/pytorch:25.05-py3

    RUN pip install --no-cache \
        jupyterlab \
        jupyterhub==4.1.6 \
        pyfirecrest==1.2.0 \
        SQLAlchemy==1.4.52 \
        oauthenticator==16.3.1 \
        notebook==7.3.3 \
        jupyterlab_nvdashboard==0.13.0 \
        git+https://github.com/eth-cscs/firecrestspawner.git
    ```

    The package [nvdashboard](https://github.com/rapidsai/jupyterlab-nvdashboard) is also installed here, which allows to monitor system metrics at runtime.
    
    A corresponding TOML file can look like

    ```toml
    image = "/capstor/scratch/cscs/${USER}/ce-images/ngc-pytorch+25.05.sqsh"

    mounts = [
        "/capstor", 
        "/iopsstor",
        "/users/${USER}/.local/share/jupyter" # (1)!
    ]

    workdir = "/capstor/scratch/cscs/${USER}" # (2)!

    writable = true

    [annotations]
    com.hooks.aws_ofi_nccl.enabled = "true" # (3)!
    com.hooks.aws_ofi_nccl.variant = "cuda12"

    [env]
    CUDA_CACHE_DISABLE = "1" # (4)!
    TORCH_NCCL_ASYNC_ERROR_HANDLING = "1" # (5)!
    MPICH_GPU_SUPPORT_ENABLED = "0" # (6)!
    ```
    
    1. avoid mounting all of `$HOME` to avoid subtle issues with cached files, but mount Jupyter kernels
    2. set working directory of Jupyter session (file browser root directory)
    3. use environment settings for optimized communication 
    4. disable CUDA JIT cache
    5. async error handling when an exception is observed in NCCL watchdog: aborting NCCL communicator and tearing down process upon error
    6. Disable GPU support in MPICH, as it can lead to deadlocks when using together with NCCL

??? tip "Accessing file systems with uenv"
    While Jupyter sessions with CE start in the directory specified with `workdir`, a uenv session always start in your `$HOME` folder. All non-hidden files and folders in `$HOME` are visible and accessible through the JupyterLab file browser. However, you can not browse directly to folders above `$HOME`. To enable access your `$SCRATCH` folder, it is therefore necessary to create a symbolic link to your `$SCRATCH` folder. This can be done by issuing the following command in a terminal from your `$HOME` directory:
    ```bash
    ln -s $SCRATCH $HOME/scratch
    ```


## Creating Jupyter kernels

A kernel, in the context of Jupyter, is a program together with environment settings that runs the user code within Jupyter notebooks. In Python, Jupyter kernels make it possible to access the (system) Python installation of a uenv or container, that of a virtual environment (on top) or any other custom Python installations like Anaconda/Miniconda from Jupyter notebooks. Alternatively, a kernel can also be created for other programming languages such as Julia, allowing e.g. the execution of Julia code in notebook cells. 

As a preliminary step to running any code in Jupyter notebooks, a kernel needs to be installed, which is described in the following for both Python and Julia.

### Using Python in Jupyter

For Python, the recommended setup consists of a uenv or container as a base image as described [above][ref-jlab-runtime-environment] that includes the stable dependencies of the software stack. Additional packages can be installed in a virtual environment _on top_ of the Python installation in the base image (mandatory for most uenvs). Having the base image loaded, such a virtual environment can be created with

```bash title="Create a virtual environment on top of a base image"
python -m venv --system-site-packages venv-<base-image-version>
```

where `<base-image-version>` can be replaced by an identifier uniquely referring to the base image (such virtual environments are specific for the base image and non-portable).

Jupyter kernels for Python are powered by [`ipykernel`](https://github.com/ipython/ipykernel).
As a result, `ipykernel` must be installed in the target environment that will be used as a kernel. That can be done with `pip install ipykernel` (either as part of a Dockerfile or in an activated virtual environment on top of a uenv/container image).

A kernel can now be created from an active Python virtual environment with the following commands

```bash title="Create an IPython Jupyter kernel"
. venv-<base-image-version>/bin/activate # (1)!
python -m ipykernel install \
    ${VIRTUAL_ENV:+--env PATH $PATH --env VIRTUAL_ENV $VIRTUAL_ENV} \
    --user --name="<kernel-name>" # (2)!
```

1. This step is only necessary when working with a virtual environment on top of the base image
2. The expression in braces makes sure the kernel's environment is properly configured when using a virtual environment (must be activated). The flag `--user` installs the kernel to a path under `${HOME}/.local/share/jupyter`. 

The `<kernel-name>` can be replaced by a name specific to the base image/virtual environment.

!!! bug "Python packages from uenv shadowing those from a virtual environment"
    When using uenv with a virtual environment on top, the site-packages under `/user-environment` currently take precedence over those in the activated virtual environment. This is due to the path being included in the `PYTHONPATH` environment variable. As a consequence, despite installing a different version of a package in the virtual environment from what is available in the uenv, the uenv version will still be imported at runtime. A possible workaround is to prepend the virtual environment's site-packages to `PYTHONPATH` whenever activating the virtual environment.
    ```bash
    export PYTHONPATH="$(python -c 'import site; print(site.getsitepackages()[0])'):$PYTHONPATH"
    ```
    Consequently, a modified command should be used to install the Jupyter kernel that carries over the changed `PYTHONPATH` to the Jupyter environment. This can be done as follows.
    ```bash
    python -m ipykernel install \
        ${VIRTUAL_ENV:+--env PATH $PATH --env VIRTUAL_ENV $VIRTUAL_ENV ${PYTHONPATH+--env PYTHONPATH $PYTHONPATH}} \
        --user --name="<kernel-name>"
    ```


### Using Julia in Jupyter

To run Julia code in Jupyter notebooks, you can use the provided uenv for this language. In particular, you need to use the following in the JupyterHub Spawner `Advanced options` forms mentioned [above][ref-jlab-runtime-environment]:
!!! important "pass a [`julia`][ref-uenv-julia] uenv and the view `jupyter`."

When Julia is first used within Jupyter, IJulia and one or more Julia kernel need to be installed. 
Type the following command in a shell within JupyterHub to install IJulia, the default Julia kernel and, on systems whith Nvidia GPUs, a Julia kernel running under Nvidia Nsight Systems:
```bash
install_ijulia
```

You can install additional custom Julia kernels by typing the following in a shell:
```bash
julia
using IJulia
installkernel(<args>) # (1)!
```

1. type `? installkernel` to learn about valid `<args>`

!!! warning "First time use of Julia"
    If you are using Julia for the first time at all, executing `install_ijulia` will automatically first trigger the installation of `juliaup` and the latest `julia` version (it is also triggered if you execute `juliaup` or `julia`).


## Parallel computing

### MPI in the notebook via IPyParallel and MPI4Py

MPI for Python provides bindings of the Message Passing Interface (MPI) standard for Python, allowing any Python program to exploit multiple processors.

MPI can be made available on Jupyter notebooks through [IPyParallel](https://github.com/ipython/ipyparallel). This is a Python package and collection of CLI scripts for controlling clusters for Jupyter: A set of servers that act as a cluster, called engines, is created and the code in the notebook's cells will be executed within them.

We provide the python package [`ipcmagic`](https://github.com/eth-cscs/ipcluster_magic) to make easier the mangement of IPyParallel clusters. `ipcmagic` can be installed by the user with

```bash
pip install ipcmagic-cscs
```

The engines and another server that moderates the cluster, called the controller, can be started an stopped with the magic `%ipcluster start -n <num-engines>` and `%ipcluster stop`, respectively. Before running the command, the python package `ipcmagic` must be imported

```bash
import ipcmagic
```

Information about the command, can be obtained with `%ipcluster --help`.

In order to execute MPI code on JupyterLab, it is necessary to indicate that the cells have to be run on the IPyParallel engines. This is done by adding the [IPyParallel magic command](https://ipyparallel.readthedocs.io/en/latest/tutorial/magics.html) `%%px` to the first line of each cell.

There are two important points to keep in mind when using IPyParallel. The first one is that the code executed on IPyParallel engines has no effect on non-`%%px` cells. For instance, a variable created on a `%%px`-cell will not exist on a non-`%%px`-cell. The opposite is also true. A variable created on a regular cell, will be unknown to the IPyParallel engines. The second one is that the IPyParallel engines are common for all the user's notebooks. This means that variables created on a `%%px` cell of one notebook can be accessed or modified by a different notebook.

The magic command `%autopx` can be used to make all the cells of the notebook `%%px`-cells. `%autopx` acts like a switch: running it once, activates the `%%px` and running it again deactivates it. If `%autopx` is used, then there are no regular cells and all the code will be run on the IPyParallel engines.

Examples of notebooks with `ipcmagic` can be found [here](https://github.com/eth-cscs/ipcluster_magic/tree/master/examples).

### Distributed training and inference for ML

While it is generally recommended to submit long-running machine learning training and inference jobs via `sbatch`, certain use cases can benefit from an interactive Jupyter environment.

A popular approach to run multi-GPU ML workloads is with `accelerate` and `torchrun` as demonstrated in the [tutorials][ref-guides-mlp-tutorials]. In particular, the `accelerate launch` script in the [LLM fine-tuning tutorial][ref-mlp-llm-finetuning-tutorial] can be directly carried over to a Jupyter cell with a `%%bash` header (to run its contents interpreted by bash). For `torchrun`, one can adapt the command from the multi-node [nanotron tutorial][ref-mlp-llm-nanotron-tutorial] to run on a single GH200 node using the following line in a Jupyter cell

```bash
!torchrun --standalone --nproc_per_node=4 run_train.py ...
```

!!! warning
    When using a virtual environment on top of a base image with Pytorch, replace `torchrun` with `python -m torch.distributed.run` to pick up the correct Python environment.
    
!!! note
    In none of these scenarios any significant memory allocations or background computations are performed on the main Jupyter process. Instead, the resources are kept available for the processes launched by `accelerate` or `torchrun`, respectively.

Alternatively to using these launchers, it is also possible to use SLURM to obtain more control over resource mappings, e.g. by launching an overlapping SLURM step onto the same node used by the Jupyter process. An example with the container engine looks like this

```bash
!srun --overlap -ul --environment /path/to/edf.toml \
    --container-workdir $PWD -n 4 bash -c "\
    MASTER_ADDR=\$(scontrol show hostnames \$SLURM_JOB_NODELIST | head -n 1) \
    MASTER_PORT=29500 \
    RANK=\$SLURM_PROCID LOCAL_RANK=\$SLURM_LOCALID WORLD_SIZE=\$SLURM_NPROCS \
    python train.py ..."
```

where `/path/to/edf.toml` should be replaced by the TOML file and `train.py` is a script using `torch.distributed` for distributed training. This can be further customized with extra SLURM options.

!!! warning "Concurrent usage of resources"
    Subtle bugs can occur when running multiple Jupyter notebooks concurrently that each assume access to the full node. Also, some notebooks may hold on to resources such as spawned child processes or allocated memory despite having completed. In this case, resources such as a GPU may still be busy, blocking another notebook from using it. Therefore, it is good practice to only keep one such notebook running that occupies the full node and restarting a kernel once a notebook has completed. If in doubt, system monitoring with `htop` and [nvdashboard](https://github.com/rapidsai/jupyterlab-nvdashboard) can be helpful for debugging.


## Further documentation

* [Jupyter](http://jupyter.org/)
* [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/)
* [JupyterHub](https://jupyterhub.readthedocs.io/en/stable)
