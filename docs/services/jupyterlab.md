[](){#ref-jlab}
# JupyterLab

## Access and setup

The JupyterHub service enables the interactive execution of JupyterLab on [Daint][ref-cluster-daint] on a single compute node.

The service is accessed at [jupyter-daint.cscs.ch](https://jupyter-daint.cscs.ch/).

Once logged in, you will be redirected to the JupyterHub Spawner Options form, where typical job configuration options can be selected in order to allocate resources. These options might include the type and number of compute nodes, the wall time limit, and your project account.

Single-node notebooks are launched in a dedicated queue, minimizing queueing time. For these notebooks, servers should be up and running within a few minutes. The maximum waiting time for a server to be running is 5 minutes, after which the job will be cancelled and you will be redirected back to the spawner options page. If your single-node server is not spawned within 5 minutes we encourage you to [contact us](ref-get-in-touch).

When resources are granted the page redirects to the JupyterLab session, where you can browse, open and execute notebooks on the compute nodes. A new notebook with a Python 3 kernel can be created with the menu `new` and then `Python 3` . Under `new` it is also possible to create new text files and folders, as well as to open a terminal session on the allocated compute node.

## Debugging

The log file of a JupyterLab server session is saved on `$SCRATCH` in a file named `jupyterhub_<jobid>.log`. If you encounter problems with your JupyterLab session, the contents of this file can be a good first clue to debug the issue.

!!! warning "Unexpected error while saving file: disk I/O error."
    This error message indicates that you have run out of disk quota.
    You can check your quota using the command `quota`.

## Accessing file systems

The Jupyter sessions are started in your `$HOME` folder. All non-hidden files and folders in `$HOME` are visible and accessible through the JupyterLab file browser. However, you can not browse directly to folders above `$HOME`. To enable access your `$SCRATCH` folder, it is therefore necessary to create a symbolic link to your `$SCRATCH` folder. This can be done by issuing the following command in a terminal from your `$HOME` directory:

```bash
ln -s $SCRATCH $HOME/scratch
```

Alternatively, you can issue the following command directly in a notebook cell: `!ln -s $SCRATCH $HOME/scratch`.

## Creating Jupyter kernels for Python

A kernel, in the context of Jupyter, is a program that runs the user code within the Jupyter notebooks. Jupyter kernels make it possible to access virtual environments, custom python installations like anaconda/miniconda or any custom python setting, from Jupyter notebooks.

Jupyter kernels are powered by [`ipykernel`](https://github.com/ipython/ipykernel).
As a result, `ipykernel` must be installed in every environment that will be used as a kernel.
That can be done with `pip install ipykernel`.
A kernel can be created from an active Python virtual environment with the following commands

```console title="Create a Jupyter kernel"
. /myenv/bin/activate
python -m ipykernel install --user --name="<kernel-name>" --display-name="<kernel-name>"
```

## Using uenvs in JupyterLab

In the JupyterHub Spawner Options form mentioned above, it's possible to pass an uenv and a view.
The uenv will be mounted at `/user-environment`, and the specified view will be activated.

If the uenv includes the installation of a Python package, you will need to create a Jupyter kernel to make the package available in the notebooks.
If `ipykernel` is not available in the uenv, you can create a Python virtual environment in a terminal within JupyterLab and install it there

```console
cd $SCRATCH
python -m venv uenv-pyenv --system-site-packages
pip install ipykernel
```

Then with that virtual environment activated, you can run the command to create the Jupyter kernel.

!!! warning "Using remote uenv for the first time."
    If the uenv is not present in the local repository, it will be automatically fetched.
    As a result, JupyterLab may take slightly longer than usual to start.

## Ending your interactive session and logging out

The Jupyter servers can be shut down through the Hub. To end a JupyterLab session, please select `Control Panel` under the `File` menu and then `Stop My Server`. By contrast, clicking `Logout` will log you out of the server, but the server will continue to run until the Slurm job reaches its maximum wall time.

## MPI in the notebook via IPyParallel and MPI4Py

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

## Further documentation

* [Jupyter](http://jupyter.org/)
* [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/)
* [JupyterHub](https://jupyterhub.readthedocs.io/en/stable)
