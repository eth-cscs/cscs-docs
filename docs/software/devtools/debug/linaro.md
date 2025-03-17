[](){#ref-software-devtools-debug-ddt}
# Linaro Forge DDT

[Linaro Forge](https://docs.linaroforge.com/latest/html/forge/index.html) is a
suite of profiling and debugging tools, it includes the Linaro DDT debugger and
the Linaro [MAP][ref-software-devtools-perf-map] profiler. DDT allows
source-level debugging of Fortran, C, C++ and Python codes. It can be used for
debugging serial, multi-threaded (OpenMP), multi-process (MPI) and accelerated
(Cuda, OpenACC) programs running on research and production systems, including
the CSCS Alps system. DDT can be executed either with its graphical user
interface or from the command-line.

## Quickstart guide

The name of the uenv image is `linaro-forge`, and the available versions on a
cluster can be determined using the `uenv image find` command, for example:
```
> uenv --version
7.0.0

> uenv image find linaro-forge
uenv                    arch   system  id                size(MB)  date
linaro-forge/24.1.1:v1  gh200  daint   e0e79f5c3e6a8ee0  365       2025-02-12

> uenv image pull linaro-forge/24.1.1:v1
pulling e0e79f5c3e6a8ee0 100.00% --- 365/365 (0.00 MB/s)
```

This uenv is configured to be mounted in the `/user-tools` path so that
they can be used alongside application and development uenv mounted at
`user-environment` (sidecar mode):

=== "sidecar"

    When using alongside another uenv, start a uenv session with both uenv as
    follows, to mount the images at the respective `/user-environment` and
    `/user-tools` locations:

    ```bash
    > uenv start prgenv-gnu/24.11:v1,linaro-forge/24.1.1:v1 --view=prgenv-gnu:default
    > source /user-tools/activate

    # test that everything has been mounted correctly
    # (will give warnings if there are problems)
    > uenv status

    # check that ddt is in the path
    > ddt --version
    Linaro DDT Part of Linaro Forge.
    Copyright (c) 2023-2024 Linaro Limited. All rights reserved.
    Version: 24.1.1
    ```

=== "standalone"


    ```bash
    > uenv start linaro-forge/24.1.1:v1:/user-tools
    > source /user-tools/activate

    # check that ddt is in the path
    ddt --version
    Linaro DDT Part of Linaro Forge.
    Copyright (c) 2023-2024 Linaro Limited. All rights reserved.
    Version: 24.1.1
    ```

When using the uenv with no other environment mounted (standalone mode), the
image will automatically be mounted in the `/user-tools` mount point. The
`/user-tools/activate` script will make the forge executables available in your
environment path.

[//]: <> (The `/user-tools/activate` script will make the forge executables available)
[//]: <> (in your environment, and **must be run before** any other uenv view command)
[//]: <> (otherwise the environment variables set from the other uenv will be)
[//]: <> (overwritten.)

## User guide

In order to debug your code on Alps, you need to:

1. pull the linaro-forge uenv on one of the target Alps vCluster
- install the Linaro Forge client on your local system (desktop/laptop)
- build an executable with debug flags
- launch a job with the debugger on Alps
- start debugging/profiling

### Pull the linaro-forge uenv on Alps

The first step is to download the latest version of linaro-forge that is
available on the system(s). First, SSH into the target system, then use the
`uenv image find` command to list the available versions on the system:

```
> uenv image find linaro-forge
uenv                    arch   system  id                size(MB)  date
linaro-forge/24.1.1:v1  gh200  daint   e0e79f5c3e6a8ee0  365       2025-02-12
```

In this example, there is a single version available. Next we pull the image so
that it is available locally.

```
> uenv image pull linaro-forge/24.1.1:v1
pulling e0e79f5c3e6a8ee0 100.00% --- 365/365 (0.00 MB/s)
```

It will take a few seconds to download the image. Once complete, check that it
was downloaded using the `uenv image ls` command:

```
> uenv image ls linaro-forge
uenv                            arch   system  id                size(MB)  date
linaro-forge/24.1.1:v1          gh200  daint   e0e79f5c3e6a8ee0     365    2025-01-22
```

### Install and configure the Linaro client on your local machine

We recommend installing the [desktop client](https://www.linaroforge.com/downloadForge) 
on your local workstation/laptop. It can be downloaded for a selection of
operating systems. The client can be configured to connect with the debug jobs
running on Alps, offering a better user experience compared to running with X11
forwarding. Once installed, the client needs to be configured to connect to
the vCluster on which you are working.

First, start the client on your laptop:

=== "Linux"

    The path will change if you have installed a different version, or if it
    has been installed in a non-standard installation location.

    ```bash
    $HOME/linaro/forge/24.1.1/bin/ddt
    ```

=== "MacOS"

    The path will change if you have installed a different version, or if it
    has been installed in a non-standard installation location.

    ```bash
    open /Applications/Linaro\ Forge\ Client\ 24.1.1.app/
    ```

Next, configure a connection to the target system.
Open the *Remote Launch* menu and click on *configure* then *Add*. 
Examples of the settings are below.

=== "Eiger"

    | Field       | Value                                   |
    | ----------- | --------------------------------------- |
    | Connection  | `eiger`                                |
    | Host Name   | `cscsusername@ela.cscs.ch cscsusername@eiger.cscs.ch`  |
    | Remote Installation Directory | `uenv run linaro-forge/24.1.1:/user-tools -- /user-tools/env/forge/` |
    | Private Key | `$HOME/.ssh/cscs-key` |

=== "Daint"

    | Field       | Value                                   |
    | ----------- | --------------------------------------- |
    | Connection  | `daint`                                  |
    | Host Name   | `cscsusername@ela.cscs.ch cscsusername@daint.cscs.ch`  |
    | Remote Installation Directory | `uenv run linaro-forge/24.1.1:/user-tools -- /user-tools/env/forge/` |    

=== "Santis"

    | Field       | Value                                   |
    | ----------- | --------------------------------------- |
    | Connection  | `santis`                                |
    | Host Name   | `cscsusername@ela.cscs.ch cscsusername@santis.cscs.ch`  |
    | Remote Installation Directory | `uenv run linaro-forge/24.1.1:/user-tools -- /user-tools/env/forge/` |
    | Private Key | `$HOME/.ssh/cscs-key` |

=== "Clariden"

    | Field       | Value                                   |
    | ----------- | --------------------------------------- |
    | Connection  | `clariden`                                |
    | Host Name   | `cscsusername@ela.cscs.ch cscsusername@clariden.cscs.ch`  |
    | Remote Installation Directory | `uenv run linaro-forge/24.1.1:/user-tools -- /user-tools/env/forge/` |
    | Private Key | `$HOME/.ssh/cscs-key` |

Some notes on the examples above:

* SSH Forwarding via `ela.cscs.ch` is used to access the cluster.
* replace the username `cscsusername` with your CSCS user name that you would normally use to open an SSH connection to CSCS.
* `Remote Installation Path` is pointing to the install directory of ddt inside the image
* private keys should be the ones generated for CSCS MFA, and this field does
  not need to be set if you have added the key to your [SSH agent][ref-ssh-agent].

Once configured, test and save the configuration:

1. check whether the configuration is correct, click `Test Remote Launch`.
2. Click on `ok` and `close` to save the configuration.
3. You can now connect by going to `Remote Launch` and choose the `Alps` entry.
   If the client fails to connect, look at the message, check your ssh
   configuration and make sure you can ssh without the client.

### Setup the user environment and build the executable

Once the uenv is loaded and activated, the program to debug must be compiled
with the `-g` (for cpu) and `-G` (for gpu) debugging flags. For example, we can
build a cuda test with a user environment:

```bash
> uenv start prgenv-gnu:24.11:v1
> uenv view default
> nvcc -c -arch=sm_90 -g -G test_gpu.cu
> mpicxx -g test_cpu.cpp test_gpu.o -o myexe
```

### Launch Linaro DDT

To use the DDT client with uenv, it must be launched in `Manual Launch` mode
(assuming that it is connected to Alps via `Remote Launch`):

=== "on local machine"

    Start DDT, and connect to the target cluster using the drop down menu for Remote Launch.

    Click on Manual launch, set the number of processes to listen to, 
    then wait for the slurm job to start (see the "on Alps" tab).
        
    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/0.png" width="600" />

=== "on Alps"

    log into the system and launch with the srun command:

    ```bash
    # start a session with both the PE used to build your application
    # and the linaro-forge uenv mounted
    > uenv start prgenv-gnu/24.11:v1,linaro-forge/24.1.1:v1 --view=prgenv-gnu:default
    > source /user-tools/activate

    > srun -N1 -n4 -t15 -pdebug \
        ./cuda_visible_devices.sh   ddt-client   ./myexe
    ```

### Start debugging

By default, DDT will pause execution on the call to MPI_Init:
<img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/1.png" width="600" />

There are more than 1 mechanism for controlling program execution:

=== "Breakpoint"

    Breakpoint(s) can be set by clicking in the margin to the left of the line number:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/3.png" width="600" />

=== "Stop at"

    Execution can be paused in every CUDA kernel launch by activating the default breakpoints from the Control menu:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/4.png" width="400" />


This screenshot shows a debugging session on 128 gpus:
![DDTgpus](https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/5.png)

More informations regarding how to use Linaro DDT are provided in the Forge
[User Guide](https://docs.linaroforge.com/latest/html/forge/index.html).

## Troubleshooting

Notes on using specific systems:

=== "alps"

    !!! warning

        Some clusters are not connected directly to the internet, hence some
        environment variables need to be set so that the tool can connect to
        the license server.

        ```bash
        export https_proxy=proxy.cscs.ch:8080
        export http_proxy=proxy.cscs.ch:8080
        export no_proxy=".local, .cscs.ch, localhost, 148.187.0.0/16, 10.0.0.0/8, 172.16.0.0/12"
        ```

        ???- note "default value of `http_proxy`"

            By default the `https_proxy` and `http_proxy` variables are set to
            `http://proxy.cscs.ch:8080`, as the transport is required for some
            other services to work. You will have to set them for a debugging
            session.

[//]: <> (The Cray Programming Environment (CPE) debugging tools:)
[//]: <> (https://cpe.ext.hpe.com/docs/latest/debugging-tools/index.html)
