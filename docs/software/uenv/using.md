[](){#ref-uenv-using}
# Using uenv

To use one, it must first be loaded into your running environment.
There are three ways to use uenv:

* [**Start**][ref-uenv-start] a shell with a uenv environment for **interactive use**;
* [**Run**][ref-uenv-run] a single command in a uenv, for use in scripts or in workflows that use software provided by more than one uenv.
* Configure a [**Slurm**][ref-uenv-slurm] job to use a uenv on compute nodes.

[](){#ref-uenv-how}
## How uenv work

Uenv provide full software stacks that provide specific applications, or programming/development environments.
Uenv are [SquashFS images](https://docs.kernel.org/filesystems/squashfs.html), a compressed file that contains a directory tree.
The squashfs image of a uenv is a directory that contains all of the software provided by the uenv, along with useful meta data.


When you use [`uenv start`][ref-uenv-start], [`uenv run`][ref-uenv-run], or use the [`--uenv`][ref-uenv-slurm] flag with Slurm, the SquashFS file is mounted at the mount location for the uenv, which is most often `/user-environment`.

The following example demonstrates how a uenv mounts the software at `/user-environment`:

```console
# log into daint
$ ssh daint

# /user-environment is empty
$ ls -l /user-environment
total 0

# start a uenv
$ uenv start prgenv-nvfortran/24.11:v1

# the uenv software is now available
$ ls /user-environment/
bin  config  env  linux-sles15-neoverse_v2  meta  modules  repo

# findmnt verifies that a squashfs image has been mounted
$ findmnt /user-environment
TARGET            SOURCE      FSTYPE   OPTIONS
/user-environment /dev/loop25 squashfs ro,nosuid,nodev,relatime,errors=continue

# end the session and verify that the uenv is not longer mounted
$ exit
$ ls -l /user-environment
total 0
```

The software is available in the shell started by [`uenv start`][ref-uenv-start].
Note that the mounted software is only visible inside the uenv call: other users and sessions on the node do not see the mounted software at `/user-environment` - and they can mount different environments at the same time.

When the uenv was started above, the only change was the software stack mounted at `/user-environment`:

* the [scratch][ref-storage-scratch], [store][ref-storage-store], and [home][ref-storage-home] filesystems are still available;
* the environment variables are not modified.

As such, the environment is not necessarily very useful, because environment variables like `PATH`, `LD_LIBRARY_PATH` and `CUDA_HOME` are no set to make the software in the mounted path useable.

For example, using the [`uenv run`][ref-uenv-run] command that executes a single command inside an environment before returning, we see that the same gcc 7 is detected inside the uenv - despite it providing gcc 14:
```console
# the default gcc is installed in /usr/bin
$ which gcc
/usr/bin/gcc
$ gcc --version
gcc (SUSE Linux) 7.5.0

# inside the uenv we still see the system gcc
$ uenv run prgenv-gnu/25.6:v2 -- which gcc
/usr/bin/gcc
$ uenv run prgenv-gnu/25.6:v2 -- gcc --version
gcc (SUSE Linux) 7.5.0
```

To set environment variables, uenv provide [views][ref-uenv-views], which set additional environment variables inside the uenv:

```
# use the default view to make all software available
$ uenv run --view=default prgenv-gnu/25.6:v2 -- gcc --version
gcc (Spack GCC) 14.2.0
$ uenv run --view=default prgenv-gnu/25.6:v2 -- which gcc
/user-environment/env/default/bin/gcc

# use the modules view to make modules available
$ uenv run --view=modules prgenv-gnu/25.6:v2 -- bash -c 'module avail'
------- /user-environment/modules -------
   aws-ofi-nccl/1.16.0    gcc/14.2.0
   boost/1.88.0           gsl/2.8
   ...
```

[](){#ref-uenv-start}
## Starting a uenv session

The `uenv start` command will start a new shell with one or more uenv images mounted.
This is very useful for interactive sessions, for example if you want to work in the terminal to compile an application, or set up a Python virtual environment.

!!! example "start an interactive shell to compile an application"
    Here we want to compile an MPI + CUDA application "affinity".

    ```console
    # start the prgenv-gnu uenv, which provides MPI, cuda and CMake
    # use the "default" view, which will load all of the software in the uenv
    $ uenv start prgenv-gnu/25.6:v2 --view=default

    # clone the software and set up the build directory
    $ git clone https://github.com/bcumming/affinity.git
    $ mkdir -p affinity/build
    $ cd affinity/build/

    # configure the build with CMake, then call make to build
    # mpi, gcc, cuda and cmake are all provided by the uenv
    $ CXX=g++ CC=gcc cmake .. -DAFFINITY_GPU_BACKEND=cuda
    $ make -j

    # run the affinity executable on two nodes - note how the uenv is
    # automatically loaded by Slurm on the compute nodes, which provides CUDA and MPI from
    # the uenv so that the uenv can run.
    $ srun -n2 -N2 ./affinity.cuda
    GPU affinity test for 2 MPI ranks
    rank      0 @ nid005636
     cores   : 0-287
     gpu   0 : GPU-13a62579-bf3c-fb6b-667f-f2c588f4667b
     gpu   1 : GPU-74968c03-7401-9013-0590-8445b3623208
     gpu   2 : GPU-dfbd9ec1-a4b7-4a8d-603e-ebcc360f55a3
     gpu   3 : GPU-6a44522d-bf84-9864-decf-6d3e85078442
    rank      1 @ nid006322
     cores   : 0-287
     gpu   0 : GPU-6d96b1d5-69e9-7bd4-f59a-a37ec1f5da1c
     gpu   1 : GPU-c0508d69-a357-934e-87a0-be04adf4eee9
     gpu   2 : GPU-02a7fd85-ff41-1d81-d010-d7a85f6134d8
     gpu   3 : GPU-e07d996e-4d67-c9f4-cf75-81cfd45a1ae1

    # finish the uenv session
    $ exit
    ```

!!! note "which shell is used"
    `uenv start` starts a new shell, and by default it will use the default shell for the user.
    You can see the default shell by looking at the `$SHELL` environment variable.
    If you want to force a different shell:
    ```bash
    SHELL=`which zsh` uenv start ...
    ```

??? warning "C Shell / tcsh users"
    uenv is tested extensively with bash (the default shell), and zsh. C shell is not tested properly, and we will not make significant changes to uenv to maintain support for C shell.

    If your are one of the handful of users using `tcsh` (C shell) and you want to use uenv, we strongly recommend creating a request at the [CSCS service desk](https://jira.cscs.ch/plugins/servlet/desk) to change to either bash or zsh as your default.

??? warning "Failed to unshare the mount namespace"

    If you get the following error message when starting a uenv:
    ```console
    $ uenv start linalg/24.11:v1
    squashfs-mount: Failed to unshare the mount namespace: Operation not permitted
    ```
    you most likely already have a uenv mounted.
    The `uenv status` command will report that you have a uenv loaded if that is the case:
    ```console
    $ uenv status
    prgenv-gnu:/user-environment
      GNU Compiler toolchain with cray-mpich, Python, CMake and other development tools.
      views:
        spack: configure spack upstream
        modules: activate modules
        default:
    ```
    Unload the active uenv by exiting the current shell before loading the new uenv.

The basic syntax of uenv start is `uenv start image` where `image` is the uenv to start.
The image can be a [label][ref-uenv-labels], the hash/id of the uenv, or a file:

!!! example "uenv start"
    ```console
    # start the image using the name of the uenv
    $ uenv start netcdf-tools/2024:v1

    # or use the unique id of the uenv
    $ uenv start 499c886f2947538e

    # or provide the path to a squashfs file
    $ uenv start $SCRATCH/my-uenv/gromacs.squashfs
    ```

!!! warning "do not use `uenv start` in scripts or `~/.bashrc`"
    The `uenv start` command is only for creating interactive environments, because it creates an interactive shell.
    For Slurm jobs, and use inside scripts, use the `uenv run` and Slurm integration.

    Because uenv start and run execute commands in a new environment, they [can't be used in bashrc][ref-guides-terminal-bashrc] to configure your environment during login.
    See our guide for creating [convenient custom environments][ref-uenv-customenv] with uenv for alternatives to `module load` in your `~/.basrhc`.
    

[](){#ref-uenv-run}
## Running a uenv

The `uenv run` command can be used to run an application or script in a uenv environment, and return control to the calling shell when the command has finished running.

The run command is very useful when scripting complicated workflows, and can be used to create customized environments.
See the guide to [creating custom environments][ref-uenv-customenv] for an example.

!!! info "how is `uenv run` different from `uenv start`?"
    `uenv start` sets up the uenv environment, then starts an interactive shell in that environment.
    When you are finished, you can type `exit` to finish the session.

    `uenv run` is more generic - instead of running a shell in environment, it takes the executable and arguments to run in the shell.
    The following commands are equivalent:

    ```console
    # start a new bash shell in prgenv-gnu
    uenv start prgenv-gnu/24.11
    # start a new bash shell in prgenv-gnu
    uenv run prgenv-gnu/24.11 -- bash
    ```

!!! example "running cmake"
    Call the `cmake` provided by the uenv to configure a build with the `default` view loaded:
    ```console
    # run a command
    $ uenv run prgenv-gnu/25.6:v2 --view=default -- cmake -DUSE_GPU=cuda ..
    ```

!!! example "running an application executable"
    Run the GROMACS executable from inside the `gromacs` uenv.
    ```console
    # run an executable:
    $ uenv run --view=gromacs gromacs/2024:v1 -- gmx_mpi
    ```

!!! example "running applications with different environments"
    `uenv run` is useful for running multiple applications or scripts in a pipeline or workflow, where each application has separate requirements.
    In this example the pre and post processing stages use `prgenv-gnu`, while the simulation stage uses the `gromacs` uenv.
    ```console
    # run multiple applications, one after the other, that have different requirements
    $ uenv run --view=default prgenv-gnu/24.11:v1 -- ./pre-processing-script.sh
    $ uenv run --view=gromacs gromacs/2024:v1 -- gmx_mpi $gromacs_args
    $ uenv run --view=default prgenv-gnu/24.11:v1 -- ./post-processing-script.sh
    ```


[](){#ref-uenv-slurm}
## Slurm integration

The environment to load can be provided directly to Slurm via three arguments:

* `--uenv`:  a comma-separated list of uenv to mount
* `--view`:  a comma-separated list of views to load
* `--repo`:  an alternative (if not set, the default repo in `$SCRATCH/.uenv-images` is used)

For example, the flags can be used with srun :
```console
# mount the uenv prgenv-gnu with the view named default
$ srun --uenv=prgenv-gnu/24.7:v3 --view=default ...

# mount an image at an explicit location (/user-tools)
$ srun --uenv=$IMAGES/myenv.squashfs:/user-tools ...

# mount multiple images: use a comma to separate the different options
$ srun --uenv=prgenv-gnu/24.7:v3,editors/24.7:v2 --view=default,editors:modules ...
```

The commands can also be used in sbatch scripts to have fine-grained control:

!!! example "sbatch script for uenv"
    It is possible to provide a uenv that is loaded inside the script, and will be loaded by default by all srun commands that do not override it with their own `--uenv` parameters.
    ```
    #!/bin/bash

    #SBATCH --uenv=editors/24.7:v2
    #SBATCH --view=editors:ed
    #SBATCH --ntasks=4
    #SBATCH --nodes=1
    #SBATCH --output=out-%j.out
    #SBATCH --error=out-%j.out

    echo "==== test in script ===="
    # the fd command is provided by the ed view
    # use it to inspect the meta data in the mounted image
    fd . /user-tools/meta/recipe

    echo "==== test in srun ===="
    # use srun to launch the parallel job
    srun -n4 bash -c 'echo $SLURM_PROCID on $(hostname): $(which emacs)'

    echo "==== alternative mount ===="
    srun -n4 --uenv=prgenv-gnu --view=prgenv-gnu:default bash -c 'echo $SLURM_PROCID on $(hostname): $(which mpicc)'
    sbatch output
    ```

    The sbatch job above would generate output like the following:
    ```
    ==== test in script ====
    /user-tools/meta/recipe/compilers.yaml
    /user-tools/meta/recipe/config.yaml
    /user-tools/meta/recipe/environments.yaml
    /user-tools/meta/recipe/modules.yaml
    ==== test in srun ====
    1 on nid007144: /user-tools/env/ed/bin/emacs
    3 on nid007144: /user-tools/env/ed/bin/emacs
    0 on nid007144: /user-tools/env/ed/bin/emacs
    2 on nid007144: /user-tools/env/ed/bin/emacs
    ==== alternative mount ====
    0 on nid007144: /user-environment/env/default/bin/mpicc
    1 on nid007144: /user-environment/env/default/bin/mpicc
    2 on nid007144: /user-environment/env/default/bin/mpicc
    3 on nid007144: /user-environment/env/default/bin/mpicc
    ```

In the example above, the `#SBATCH --uenv`  and `#SBATCH --view`  parameters in the preamble of the sbatch script set the default uenv to `editors` with the view `ed`.

* `editors` is mounted and the view set in the script (the "test in script" part)
* `editors` is also mounted in the first call to srun (which does not provide a ``–-uenv` flag)

it is possible to override the default uenv by passing a different `--uenv`  and `--view`  flags to an `srun`  call inside the script, as is done in the second `srun`  call.

* Note how the second call has access to `mpicc`, provided by `prgenv-gnu`.

[](){#ref-uenv-views}
## Views

Starting a uenv runs in a process with the software mounted at `/user-environment` or `/user-tools`, however no changes are made to environment variables like `$PATH`.

Uenv images provide **views**, which will set environment variables that load the software into your environment.
Views are loaded using the `--view` flag for `uenv start`, `uenv run` and the Slurm plugin (all documented above).

!!! example "loading views"
    ```console
    # activate the view named default in prgenv-gnu
    $ uenv start --view=default prgenv-gnu/24.11:v1

    # activate both the spack and modules views in prgenv-gnu using
    # a comma-separated list of view names
    $ uenv start --view=spack,modules prgenv-gnu/24.11:v1

    # when starting multiple uenv, you can disambiguate using uenvname:viewname
    $ uenv start --view=prgenv-gnu:default,editors:ed prgenv-gnu/24.11:v1,editors
    ```

Each uenv can provide more than one view.
The  [`modules`][ref-uenv-views-modules] and [`spack`][ref-uenv-views-spack] are standard views provided by nearly all uenv.

To find a list of the views in a uenv, use the `uenv status` command when the uenv is running.
This is a little bit inconvenient, and we will add a command for finding the views in a uenv without having to run it.

!!! example "listing views in a uenv"
    Use the following `uenv run` trick to list the views in a uenv:

    ```console
    $ uenv run namd -- uenv status
    namd:/user-environment
      NAMD: Scalable Molecular Dynamics
      views:
        spack: configure spack upstream
        namd-single-node:
        namd:
        modules: activate modules
        develop-single-node:
        develop:
    ```

!!! question "why is the `default` view not the default?"
    Some uenv, for example the `prgenv-gnu`, have a view named `default`.

    This view is not loaded by default if no view is specified with the `--view` flag.
    We no longer use the name `default` in new uenv, however we continue using the name for uenv like `prgenv-gnu` to minimise user-disruption.

[](){#ref-uenv-views-modules}
### Modules view

Most uenv provide the modules, that can be accessed using the `module` command.
By default, the modules are not activated when a uenv is started, and need to be explicitly activated using the `module` view.

!!! example "using the module view"
    ```console
    $ uenv start prgenv-gnu/24.11:v1 --view=modules
    $ module avail
    ---------------------------- /user-environment/modules ----------------------------
       aws-ofi-nccl/git.v1.9.2-aws_1.9.2    lua/5.4.6
       boost/1.86.0                         lz4/1.10.0
       cmake/3.30.5                         meson/1.5.1
       cray-mpich/8.1.30                    nccl-tests/2.13.6
       cuda/12.6.2                          nccl/2.22.3-1
       fftw/3.3.10                          netlib-scalapack/2.2.0
       fmt/11.0.2                           ninja/1.12.1
       gcc/13.3.0                           openblas/0.3.28
       gsl/2.8                              osu-micro-benchmarks/5.9
       hdf5/1.14.5                          papi/7.1.0
       kokkos-kernels/4.4.01                python/3.12.5
       kokkos-tools/develop                 superlu/5.3.0
       kokkos/4.4.01                        zlib-ng/2.2.1
       libtree/3.1.1
    $ module load cuda gcc cmake
    $ nvcc --version
    nvcc: NVIDIA (R) Cuda compiler driver
    Cuda compilation tools, release 12.6, V12.6.77
    $ gcc --version
    gcc (Spack GCC) 13.3.0
    $ cmake --version
    cmake version 3.30.5
    ```

[](){#ref-uenv-error-v9modules}
??? warning "bash: module: command not found"

    Version 9.0.0 of uenv, installed on October 22 2025, has a bug that removes the module command on Santis and Clariden.

    !!! note
        The issue does not affect uenv in Slurm jobs, or on Daint and Eiger.

    !!! note
        A fix has been implemented, and will be installed as soon as possible.

    Specifically, the `module` command is not available inside `uenv start` sessions:
    ```console
    $ uenv start prgenv-gnu/24.11:v2 --view=modules
    $ module avail
    bash: module: command not found
    ```

    The workaround is to manually load the module tool after starting your uenv session:

    ```console
    $ uenv start prgenv-gnu/24.11:v2 --view=modules
    $ source /usr/share/lmod/8.7.17/init/bash
    $ module avail

    -------------- /user-environment/modules ---------------
       aws-ofi-nccl/git.v1.9.2-aws_1.9.2
       boost/1.86.0
       cmake/3.30.5
       cray-mpich/8.1.30
       cuda/12.6.0
       fftw/3.3.10
       fmt/11.0.2
       gcc/13.3.0
       ...
    ```


[](){#ref-uenv-views-spack}
### Spack view

uenv images provide a full upstream Spack configuration to facilitate building your own software with Spack using the packages installed inside as dependencies.
No view needs to be loaded to use Spack, however all uenv provide a `spack` view that sets some environment variables that contain useful information like the location of the Spack configuration, and the version of Spack that was used to build the uenv.
For more information, see our guide on building software with [Spack and uenv][ref-build-uenv-spack].

