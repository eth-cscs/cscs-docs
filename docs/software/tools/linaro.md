[](){#uenv-linaro}
# Linaro Forge

[Linaro Forge](https://www.linaroforge.com/downloadForge) is a suite of profiling and debugging tools.
It includes Linaro DDT debugger and Linaro MAP profiler.
These tools allow source-level debugging and profiling of Fortran, C, C++ and Python codes.
They can be used for debugging and profiling serial, multi-threaded (OpenMP), multi-process (MPI) and accelerated (Cuda, OpenACC) programs running on research and production systems, including CSCS Alps system.
They can be executed either as a graphical user interface or from the command-line.

## Quickstart guide

The name of the uenv image is `linaro-forge`, and the available versions on a
cluster can be determined using the `uenv image find` command, for example:
```
> uenv image find linaro-forge
uenv/version:tag            uarch     date       id               size
linaro-forge/23.1.2:latest  gh200     2024-04-10 ea67dbb33801c7c3 342MB
```

The linaro tools are configured to be mounted in the `/user-tools` path so that
they can be used alongside application and development uenv mounted at
`user-environment`.

=== "sidecar"

    When using alongside another uenv, start a uenv session with both uenv with `linaro-forge` after the main uenv, to mount the images at the respective `/user-environment` and `/user-tools` locations:

    ```bash
    uenv start prgenv-gnu/24.2:v3 linaro-forge/23.1.2

    # test that everything has been mounted correctly
    # (will give warnings if there are problems)
    uenv status

    source /user-tools/activate
    uenv view prgenv-gnu:default

    # check that ddt is in the path
    ddt --version
    ```

    The `/user-tools/activate` script will make the forge executables available in your environment, and **must be run before**
    any other uenv view command otherwise the environment variables set from the other uenv will be overwritten.

=== "standalone"

    When using the uenv with no other environment mounted, you will need to explicitly set the `/user-tools` mount point:

    ```bash
    uenv start linaro-forge/23.1.2:/user-tools

    source /user-tools/activate

    # check that ddt is in the path
    ddt --version
    ```

    The `/user-tools/activate` script will make the forge executables available in your environment.

## User guide

In order to debug your code on Alps, you need to:

1. pull the linaro-forge uenv on the target Alps vCluster
- install the Linaro Forge client on your local system (desktop/laptop)
- build an executable with debug flags
- launch a job with the debugger on Alps
- start debugging/profiling

### Pull the Linaro Forge uenv on the Alps cluster

The first step is to download the latest version of linaro-forge that is
available on the cluster. First, SSH into the target system, then use the
`uenv image find` command to list the available versions on the system:

```
> uenv image find linaro-forge
uenv/version:tag                        uarch date       id               size
linaro-forge/23.1.2:latest              gh200 2024-04-10 ea67dbb33801c7c3 342MB
```

In this example, there is a single version available. Next we pull the image so
that it is available locally.

```
> uenv image pull linaro-forge/23.1.2:latest
```

It will take a few seconds to download the image. Once complete, check that it
was downloaded using the `uenv image ls` command:

```
> uenv image ls linaro-forge
uenv/version:tag                        uarch date       id               size
linaro-forge/23.1.2:latest              gh200 2024-04-05 ea67dbb33801c7c3 342MB
```

### Install and configure the client on your local machine

We recommend installing the [desktop client](https://www.linaroforge.com/downloadForge) 
on your local workstation/laptop. 
It can be downloaded for a selection of operating systems.

The client can be configured to connect with the debug jobs running on Alps, offering a
better user experience compared to running with X11 forwarding. 

Once installed, the client needs to be configured to connect to the vCluster on
which you are working. First, start the client on your laptop:

=== "Linux"

    The path will change if you have installed a different version, or if it has been installed in a non-standard installation location.

    ```bash
    $HOME/linaro/forge/23.0.1/bin/ddt
    ```

=== "MacOS"

    The path will change if you have installed a different version, or if it has been installed in a non-standard installation location.

    ```bash
    open /Applications/Linaro\ Forge\ Client\ 23.0.1.app/
    ```

Next, configure a connection to the target system.
Open the *Remote Launch* menu and click on *configure* then *Add*. 
Examples of the settings are below.

=== "Eiger"

    | Field       | Value                                   |
    | ----------- | --------------------------------------- |
    | Connection  | `eiger`                                |
    | Host Name   | `cscsusername@ela.cscs.ch cscsusername@eiger.cscs.ch`  |
    | Remote Installation Directory | `uenv run linaro-forge/23.1.2:/user-tools -- /user-tools/env/forge/` |
    | Private Key | `$HOME/.ssh/cscs-key` |

=== "Daint"

    | Field       | Value                                   |
    | ----------- | --------------------------------------- |
    | Connection  | `daint`                                  |
    | Host Name   | `cscsusername@ela.cscs.ch cscsusername@daint.cscs.ch`  |
    | Remote Installation Directory | `uenv run linaro-forge/23.1.2:/user-tools -- /user-tools/env/forge/` |    

=== "Santis"

    | Field       | Value                                   |
    | ----------- | --------------------------------------- |
    | Connection  | `santis`                                |
    | Host Name   | `cscsusername@ela.cscs.ch cscsusername@santis.cscs.ch`  |
    | Remote Installation Directory | `uenv run linaro-forge/23.1.2:/user-tools -- /user-tools/env/forge/` |
    | Private Key | `$HOME/.ssh/cscs-key` |


Some notes on the examples above:

* SSH Forwarding via `ela.cscs.ch` is used to access the cluster.
* replace the username `cscsusername` with your CSCS user name that you would normally use to open an SSH connection to CSCS.
* `Remote Installation Path` is pointing to the install directotory of ddt inside the image
* private keys should be the ones generated for CSCS MFA, and this field does not need to be set if you have added the key to your [SSH agent][ssh-ssh-agent].

Once configured, test and save the configuration:

1. check whether the configuration is correct, click `Test Remote Launch`.
2. Click on `ok` and `close` to save the configuration.
3. You can now connect by going to `Remote Launch` and choose the `Alps` entry. If the client fails to connect, look at the message, check your ssh configuration and make sure you can ssh without the client.

### Setup the user environment and build the executable

Once the uenv is loaded and activated, the program to debug must be compiled
with the `-g` (for cpu) and `-G` (for gpu) debugging flags. For example, we can
build a cuda test with a user environment:

```bash
uenv start prgenv-gnu:24.2:v2
uenv view default

nvcc -c -arch=sm_90 -g -G test_gpu.cu
mpicxx -g test_cpu.cpp test_gpu.o -o myexe
```

### Launch Linaro Forge

#### Linaro DDT

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
    uenv start prgenv-gnu/24.2 linaro-forge/23.1.2
    uenv view prgenv-gnu:default
    source /user-tools/activate

    srun -N1 -n4 -t15 -pdebug \
        ./cuda_visible_devices.sh   ddt-client   ./myexe
    ```

##### Start debugging

By default, DDT will pause execution on the call to MPI_Init:
<img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/1.png" width="600" />

There are more than 1 mechanism for controlling program execution:

=== "Breakpoint"

    Breakpoint(s) can be set by clicking in the margin to the left of the line number:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/3.png" width="600" />

=== "Stop at"

    Execution can be paused in every CUDA kernel launch by activating the default:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/4.png" width="400" />


This screenshot shows a debugging session on 128 gpus: ![DDTgpus](https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/5.png)

More information regarding how to use Linaro DDT be found in the Forge [User Guide](https://docs.linaroforge.com/latest/html/forge/index.html).

#### Linaro MAP

Linaro MAP can be used to profile an application either by the GUI or by the CLI. In the first case the user can set the profiling configuration using the GUI and then see the results. In the latter, the user can use the MAP executable to launch the application they want to profile which will generate a report file that can then be opened from the GUI.

##### Profile application

We'll focus here on the profiling using the CLI but the same configuration applies in the other case as well.

To debug an MPI application on Alps the following script is necessary:

```bash
map -n <num_of_procs> --mpi=slurm --mpiargs="<slurm_arguments>" --profile <executable> <executable_arguments>
```

This will generate a profile report in a binary file with suffix `.map`.

To open this file we can open the Linaro Forge Client on our local machine, navigate to the `linaro MAP` tab, connect to the corresponding `Remote` and then select `LOAD PROFILE DATA FILE` to locate the file.

After loading the report file we'll be in the home of Linaro MAP.

<img src="https://raw.githubusercontent.com/iomaganaris/alps-uenv/refs/heads/linaro_map_docs_archive/docs/images/map-home.png" width="800" />

More information regarding how to use Linaro MAP can be found in the Forge [User Guide](https://docs.linaroforge.com/latest/html/forge/index.html).

Linaro MAP also allows the generation of a high level Performance Report in HTML format that shows key metrics of the profiled application. To see this we can click in the toolbar `Reports > View HTML Performance Report in browser`. This will look like the following:

<img src="https://raw.githubusercontent.com/iomaganaris/alps-uenv/refs/heads/linaro_map_docs_archive/docs/images/perf-report.png" width="800" />

## Troubleshooting

Notes on using specific systems:

=== "santis,todi"

    !!! warning

        Some clusters are not connected directly to the internet, hence some environment variables need to be set so that the tool can connect to the license server.

        ```bash
        export https_proxy=proxy.cscs.ch:8080
        export http_proxy=proxy.cscs.ch:8080
        export no_proxy=".local, .cscs.ch, localhost, 148.187.0.0/16, 10.0.0.0/8, 172.16.0.0/12"
        ```

        ???- note "default value of `http_proxy`"

            By default the `https_proxy` and `http_proxy` variables are set to `http://proxy.cscs.ch:8080`, as the transport is required for some other services to work. You will have to set them for a debugging session.


