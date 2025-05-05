[](){#ref-jlab-eiger}
# JupyterLab for Eiger

## Introduction

CSCS supports the use of JupyterLab for interactive supercomputing on compute nodes. JupyterLab is the next-generation web-based user interface for Project Jupyter. Like the Jupyter Notebook, it is an open-source web application that allows creation and sharing of documents containing live code, equations, visualizations and narrative text. It uses the same notebook document format as the classic Jupyter Notebook, but - amongst other advantages - it offers the ability to work with multiple documents (or other activities) side by side in the work area using tabs or splitters.

JupyterLab at CSCS is powered by JupyterHub. This is is a multi-user Hub that spawns, manages and proxies multiple instances of the single-user Jupyter server.

We have made JupyterLab the default interface when you spawn a server from JupyterHub, and we recommend its use as it will eventually replace the classic Notebook. If you wish to continue to use the classic Notebook, then it can be found by selecting `Launch Classic Notebook` from the JupyterLab Help menu, or by changing the URL from `/lab` to `/tree` once the server is spawned.

Please Note: When you have finished your session you must stop the server by clicking on `File` menu -> `Control Panel` -> `Stop My Server`. Failing to do so will result in the Slurm allocation persisting until the wall-time limit is reached. Note that the computing time when running a JupyterLab session is taken from your corresponding project allocation.


## Access and Setup

The JupyterHub service enables the interactive execution of JupyterLab on Eiger on single and multiple compute nodes.

The service for Eiger is accessed at [https://jupyter-eiger.cscs.ch](https://jupyter-eiger.cscs.ch/).

Once logged in, you will be redirected to the JupyterHub Spawner Options form, where typical job configuration options can be selected in order to allocate resources. These options might include the type and number of compute nodes, the wall time limit, and your project account.

Single node notebooks are launched in a dedicated queue, minimizing queueing time. For these notebooks, servers should be up and running within a few minutes. Larger multi-node notebooks are directed to the `Normal queue`. The maximum waiting time for a server to be running is 7 minutes, after which the job will be cancelled and you will be redirected back to the spawner options page. If your single-node server is not spawned within 7 minutes we encourage you to contact us.

When resources are granted the page redirects to the JupyterLab session, where you can browse, open and execute notebooks on the compute nodes. A new notebook with Python 3 kernel can be created with the menu `new` and then `Python 3` or `CSCS Python`. Under `new` it is also possible to create new text files and folders, as well as to open a terminal session on the allocated compute node.

## Debugging

The log file of a JuptyerLab server session is saved on `$SCRATCH` in a file named `jupyterhub_slurmspawner_<jobid>.log`. If you encounter problems with your JupyterLab session, the contents of this file can be a good first clue to debug the issue.

If you receive the error message `Unexpected error while saving file: disk I/O error.` it is possible that you have run out of disk quota. Quotas can be checked by logging in to Ela, and issuing the command `quota`.

## Accessing file systems

The Jupyter sessions are started in your `$HOME` folder. All non-hidden files and folders in `$HOME` are visible and accessible through the JupyterLab file browser. However, you can not browse directly to folders above `$HOME`. To enable access your `$SCRATCH` folder, it is therefore necessary to create a symbolic link to your `$SCRATCH` folder. This can be done with issuing the following command in a terminal from your `$HOME` directory:

```bash
ln -s $SCRATCH scratch
```

Alternatively, you can issue the following command directly in a notebook cell: `!ln -s $SCRATCH $HOME/scratch`.

Note on the use of h5py: The h5py package is a Python interface to the HDF5 binary data format. Due to the way that file systems are mounted from the compute nodes, h5py is only supported when reading and writing on the Lustre file system (`$SCRATCH`).

## Creating Jupyter kernels for Python

A kernel, in the context of Jupyter, is a program that runs the user code within the Jupyter notebooks. Jupyter kernels make it possible to access virtual environments, custom python installations like anaconda/miniconda or any custom python setting, from Jupyter notebooks. A kernel can be created from a shell with the script `kernel-create` which is available through the module `jupyter-utils`:

```bash
module load cray
module load cray-python
module load jupyter-utils
```

`kernel-create`, creates a jupyter kernel from an active Python virtual environment. For instance:

```bash
. myenv/bin/activate
kernel-create -n myenv-kernel
```

will create a kernel that activates the environment `myenv` when it starts.

To run `kernel-create` it is necessary to have python3 as the default python. That can be by activating an environment, or by exporting the `/path/to/custom/python/bin` of a custom python installation to `$PATH`.

Jupyter kernels are powered by [`ipykernel`](https://github.com/ipython/ipykernel). As a result, `ipykernel` must be installed in every environment that will be used as a kernel. That could be done with `pip install ipykernel`.

Information about the options of `kernel-create` can be seen by passing `--help`.

## Loading modules

If you need to load environment modules or export environment variables you can make use of a Python kernel named `CSCS Python`. This kernel internally sources a file (if it exists) named `jupyterlab-cscs.env` which should sit in your `$HOME` folder. As the file is sourced within the kernel, a kernel restart is enough to apply new changes.

As an example, let's say that in a notebook we need to import TensorFlow, which is provided as an environment module. We only need to write the line

```bash
module load TensorFlow
```

in the `jupyterlab-cscs.env` and select the `CSCS Python` kernel in JupyterLab.

## Ending your interactive session and logging out

The Jupyter servers can be shut down through the Hub. To end a JupyterLab session, please select `Control Panel` under the `File` menu and then `Stop My Server`. By contrast, clicking `Logout` will log you out of the server, but the server will continue to run until the Slurm job reaches its maximum wall time.

## MPI in the Notebook via IPyParallel and mpi4py

MPI for Python provides bindings of the Message Passing Interface (MPI) standard for Python, allowing any Python program to exploit multiple processors.

MPI can be made available on Jupyter notebooks through [IPyParallel](https://github.com/ipython/ipyparallel). This is a Python package and collection of CLI scripts for controlling clusters for Jupyter: A set of servers that act as a cluster, called engines, is created and the code in the notebook's cells will be executed within them. This cluster can be run within a single node, or spanning multiple nodes.

We provide the python package [`ipcmagic`](https://github.com/eth-cscs/ipcluster_magic) to make easier the mangement of IPyParallel clusters. `ipcmagic` can be installed by the user with

```bash
pip install ipcmagic-cscs
```

The engines and another server that moderates the cluster, called the controller, can be started an stopped with the magic `%ipcluster start -n <num-engines>` and `%ipcluster stop`, respectively. Before running the command, the python package `ipcmagic` must be imported

```
import ipcmagic
```

Information about the command, can be obtained with `%ipcluster --help`.

In order to execute MPI code on JupyterLab, it is necessary to indicate that the cells have to be run on the IPyParallel engines. This is done by adding the [IPyParallel magic command](https://ipyparallel.readthedocs.io/en/latest/tutorial/magics.html) `%%px` to the first line of each cell.

There are two important points to keep in mind when using IPyParallel. The first one is that the code executed on IPyParallel engines has no effect on non-`%%px` cells. For instance, a variable created on a `%%px`-cell will not exist on a non-`%%px`-cell. The opposite is also true. A variable created on a regular cell, will be unknown to the IPyParallel engines. The second one is that the IPyParallel engines are common for all the user's notebooks. This means that variables created on a `%%px` cell of one notebook can be accessed or modified by a different notebook.

The magic command `%autopx` can be used to make all the cells of the notebook `%%px`-cells. `%autopx` acts like a switch: running it once, activates the `%%px` and running it again deactivates it. If `%autopx` is used, then there are no regular cells and all the code will be run on the IPyParallel engines.

Examples of notebooks with `ipcmagic` can be found [here](https://github.com/eth-cscs/ipcluster_magic/tree/master/examples).

Further details on MPI for Python (mpi4py): [https://mpi4py.readthedocs.io/en/stable/](https://mpi4py.readthedocs.io/en/stable/)

## IJulia

The CSCS JupyterLab service enables running Julia notebooks using [IJulia](https://github.com/JuliaLang/IJulia.jl).

### Stacked package environment

Installing and using packages within the JupyterLab service works exactly as from the command line on Eiger and accesses _the same stacked environment_. In JupyterLab, the modules `Julia` and `JuliaExtensions` are automatically loaded. The `Julia` module contains `CUDA.jl` and `MPI.jl` when using gpu nodes, and only `MPI.jl` when using multicore nodes. Note that there is currently however no straightforward and well supported way to use MPI with Julia from within JupyterLab. Thus, JuptyerLab is at present set up for using Julia on a single node. The module `JuliaExtensions` provides additional useful Julia packages as for instance `Plots`, `HDF5` and `PyCall`. Refer to the [Julia documentation](https://docs.julialang.org/) for installing additional packages. [This notebook](https://confluence.cscs.ch/spaces/KB/pages/891453492/JupyterLab+for+Eiger.Alps#) shows a simple example of the usage of the stacked Julia environment and of using `CUDA.jl` to access a node's GPU.

## R

The CSCS JupyterLab service offers an R kernel, based on the default cray-R module.

In order to install R packages directly from notebook cells you will need to create a directory for the packages and set the $R_LIBS_USER environment variable accordingly, before you launch your notebook server. The environment variable should be set in your `.jupyterhub.env` file in your `$HOME` folder (create the file if it does not already exist):

```bash
export R_LIBS_USER=<library directory>
```

The directory for libraries must already exist and be writable from the compute nodes (i.e., it cannot be a directory in /project, for example).

When issuing the `install.packages()` command directly from a notebook cell the cell indicator will show [*] while the installation is in progress. You can monitor progress of the installation by examining the standard output which is written to the `jupyterhub_slurmspawner_<jobid>.log` file on `$SCRATCH`.

## Further Documentation

* [Jupyter](http://jupyter.org/)
* [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/)
* [JupyterHub](https://jupyterhub.readthedocs.io/en/stable)
