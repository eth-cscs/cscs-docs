[](){#ref-devtools-ddt}
# Linaro DDT

DDT allows source-level debugging of Fortran, C, C++ and Python codes.
It can be used for debugging serial, multi-threaded (OpenMP), multi-process (MPI) and accelerated (CUDA, OpenACC) programs running on research and production systems, including the CSCS Alps system.
DDT can be executed either with its graphical user interface or from the command-line.

!!! note
    Linaro DDT is provided in the `linaro-forge` uenv.
    Before using DDT, please read the [`linaro-forge` documentation][ref-uenv-linaro], which explains how to download and set up the latest version and set it up.

## User guide

The following guid will walk through the steps required to build and debug an application using DDT.

### Set up the user environment and build the executable

Once the uenv is loaded and activated, the program to debug must be compiled with the `-g` (for CPU) and `-G` (for GPU) debugging flags.
For example, we can build a CUDA test with a user environment:

```terminal
uenv start prgenv-gnu:24.11:v1 --view=default
nvcc -c -arch=sm_90 -g -G test_gpu.cu
mpicxx -g test_cpu.cpp test_gpu.o -o myexe
```

### Launch Linaro DDT

To use the DDT client with uenv, it must be launched in `Manual Launch` mode
(assuming that it is connected to Alps via `Remote Launch`):

=== "on local machine"

    Start DDT, and connect to the target cluster using the drop down menu for `Remote Launch`.

    Click on `Manual launch`, set the number of processes to listen to, then wait for the slurm job to start (see the "on Alps" tab).

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/0.png" width="600" />

=== "on Alps"

    Log into the system and launch with the `srun` command:

    ```terminal
    # start a session with both the PE used to build your application
    # and the linaro-forge uenv mounted
    > uenv start prgenv-gnu/24.11:v1,linaro-forge/24.1.1:v1 --view=prgenv-gnu:default
    > source /user-tools/activate

    > srun -N1 -n4 -t15 -pdebug ./cuda_visible_devices.sh   ddt-client   ./myexe
    ```

### Start debugging

By default, DDT will pause execution on the call to `MPI_Init`:
<img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/1.png" width="600" />

There are two mechanisms for controlling program execution:

=== "Breakpoint"

    Breakpoint(s) can be set by clicking in the margin to the left of the line number:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/3.png" width="600" />

=== "Stop at"

    Execution can be paused in every CUDA kernel launch by activating the default breakpoints from the Control menu:

    <img src="https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/4.png" width="400" />


This screenshot shows a debugging session on 128 gpus:

![DDTgpus](https://raw.githubusercontent.com/jgphpc/cornerstone-octree/ddt/scripts/img/ddt/5.png)

More informations regarding how to use Linaro DDT are provided in the Forge [User Guide](https://docs.linaroforge.com/latest/html/forge/index.html).

## Troubleshooting

See the troubleshooting guide for the [`linaro-forge` uenv][ref-uenv-linaro-troubleshooting].
