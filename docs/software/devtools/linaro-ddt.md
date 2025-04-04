[](){#ref-devtools-ddt}
# Linaro DDT

DDT allows source-level debugging of Fortran, C, C++ and Python codes.
It can be used for debugging serial, multi-threaded (OpenMP), multi-process (MPI), and accelerated (CUDA, OpenACC) programs running on research and production systems, including the CSCS [Alps][ref-alps] system.
DDT can be executed either with its graphical user interface or from the command-line.

!!! note
    Linaro DDT is provided in the `linaro-forge` [uenv][ref-uenv].
    Before using DDT, please read the [`linaro-forge` uenv documentation][ref-uenv-linaro], which explains how to download and set up the latest version.

## User guide

The following guide will walk through the steps required to build and debug an application using DDT.

### Set up the user environment and build the executable

Once the uenv is loaded and activated, the program to debug must be compiled with the `-g` (for CPU) and `-G` (for GPU) debugging flags.
For example, we can build a CUDA test with a user environment:

```bash
uenv start prgenv-gnu:24.11:v1 --view=default
nvcc -c -arch=sm_90 -g -G test_gpu.cu
mpicxx -g test_cpu.cpp test_gpu.o -o myexe
```

### Launch Linaro DDT

To use the DDT client with uenv, it must be launched in `Manual Launch` mode
(assuming that it is connected to [Alps][ref-alps] via `Remote Launch`):

=== "On local machine"

    Start DDT, and connect to the target cluster using the drop down menu for `Remote Launch`.
    If you don't have a target cluster,
    the [`linaro-forge` uenv documentation][ref-uenv-linaro] explains how to set up the connection the first time.

    Click on `Manual launch`, set the number of processes to listen to, then wait for the Slurm job to start 
    (see the "on Alps" tab for how to start the Slurm job).

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/0.png" width="600" />

=== "On Alps"

    Log into the system and launch with the `srun` command:

    ```console
    $ uenv start prgenv-gnu/24.11:v1,linaro-forge/24.1.1:v1 --view=prgenv-gnu:default # (1)!
    $ source /user-tools/activate
    $ srun -N1 -n4 -t15 -pdebug ./cuda_visible_devices.sh   ddt-client   ./myexe
    ```

    1. Start a session with both the uenv used to build your application and the `linaro-forge` uenv mounted.



### Start debugging

By default, DDT will pause execution on the call to `MPI_Init`:
<img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/1.png" width="600" />

There are two mechanisms for controlling program execution:

=== "Breakpoint"

    Breakpoint(s) can be set by clicking in the margin to the left of the line number:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/3.png" width="600" />

=== "Stop at"

    Execution can be paused in every CUDA kernel launch by activating the default breakpoints from the `Control` menu:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/4.png" width="400" />


??? example  "Debugging with 128 GPUs"
    
    This screenshot shows a debugging session on 128 GPUs:

    ![DDTgpus](https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/5.png)

More informations regarding how to use Linaro DDT are provided in the Forge [User Guide](https://docs.linaroforge.com/latest/html/forge/index.html).

## Troubleshooting

See the troubleshooting guide for the [`linaro-forge` uenv][ref-uenv-linaro-troubleshooting].
