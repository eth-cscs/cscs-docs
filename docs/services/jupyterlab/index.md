[](){#ref-jlab}
# JupyterLab

CSCS supports the use of JupyterLab for interactive supercomputing on compute nodes. Like the Jupyter Notebook, it is an open-source web application that allows creation and sharing of documents containing live code, equations, visualizations and narrative text. It uses the same notebook document format as the classic Jupyter Notebook, but - amongst other advantages - it offers the ability to work with multiple documents (or other activities) side by side in the work area using tabs or splitters.

JupyterLab at CSCS is powered by JupyterHub. This is is a multi-user Hub that spawns, manages and proxies multiple instances of the single-user Jupyter server.

We have made JupyterLab the default interface when you spawn a server from JupyterHub, and we recommend its use as it will eventually replace the classic Notebook. If you wish to continue to use the classic Notebook, then it can be found by selecting `Launch Classic Notebook` from the JupyterLab Help menu, or by changing the URL from `/lab` to `/tree` once the server is spawned.

Please Note: When you have finished your session you must stop the server by clicking on `File` menu -> `Control Panel` -> `Stop My Server`. Failing to do so will result in the Slurm allocation persisting until the wall-time limit is reached. Note that the computing time when running a JupyterLab session is taken from your corresponding project allocation.

## Licensing Terms and Conditions

Both Jupyter and JupyterHub are licensed under the terms of the revised BSD license.

## Access

* [JupyterLab for Daint.Alps][ref-jlab-daint]
* [JupyterLab for Eiger][ref-jlab-eiger]
