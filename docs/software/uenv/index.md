[](){#ref-uenv}
# uenv

Uenv are user environments that provide scientific applications, libraries and tools.
This page will explain how to find, download and use uenv on the command line, and how to enable them in Slurm jobs.

Uenv are typically application-specific, domain-specific or tool-specific - each uenv contains only what is required for the application or tools that it provides.

Each uenv is packaged in a single file (in the [Squashfs](https://docs.kernel.org/filesystems/squashfs.html) file format), that stores a compressed directory tree that contains all of the software, tools and other information like modules, required to provide a rich environment.

Each environment contains a software stack, comprised of compilers, libraries, tools and scientific applications - built using Spack.


<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Building uenv__

    More adventurous users can create their own uenv for personal use, and for other users in their team and community.

    [:octicons-arrow-right-24: Building uenv][ref-uenv-build]

-   :fontawesome-solid-layer-group: __Configuring uenv__

    Users can customize the behavior of uenv using a configuration file.

    [:octicons-arrow-right-24: Configuring uenv][ref-uenv-configure]

-   :fontawesome-solid-layer-group: __Deploying uenv__

    Documentation on how CSCS deploys uenv images, that might also be of interest to users.

    [:octicons-arrow-right-24: Deploying uenv][ref-uenv-deploy]

-   :fontawesome-solid-layer-group: __Release notes__

    Release notes for the uenv tools (CLI and Slurm plugin).

    [:octicons-arrow-right-24: Deploying uenv][ref-uenv-release-notes]

</div>

## Before starting

After logging into an [Alps cluster][ref-alps-clusters], you can quickly check the availability of uenv with the following commands:

```console
$ uenv status
there is no uenv loaded
$ uenv --version
8.1.0
```

On Alps clusters the most recent version 8.1.0 is installed.

??? warning "Out of date uenv version on Eiger and Balfrin"

    The uenv tool available on Eiger and Balfrin is a different version than the one described below, and some commands will be different to those documented here.

    !!! note
        This note only applies to the current `eigen.cscs.ch` deployment.

        The new [`eiger.alps.cscs.ch`][ref-cluster-eiger] deployment has version 8.1.0 of uenv installed.

    Please refer to `uenv --help` for the correct usage on these systems.

## Finding uenv

Uenv for programming environments, tools and applications are provided by CSCS on each Alps system.

!!! info
    The same uenv are not installed on every system.
    Instead uenv that are supported for the users of that platform are provided.

The available uenv images are stored in a registry, that can be queried using the `uenv image find`  command:

!!! example  "uenv image find"
    ```console
    $ uenv image find
    uenv                       arch  system  id                size(MB)  date
    cp2k/2024.1:v1             zen2  eiger   2a56f1df31a4c196   2,693    2024-07-01
    cp2k/2024.2:v1             zen2  eiger   f83e95328d654c0f   2,739    2024-08-23
    cp2k/2024.3:v1             zen2  eiger   7c7369b64b5fabe5   2,740    2024-09-18
    editors/24.7:rc1           zen2  eiger   e5fb284962908eed   1,030    2024-07-18
    editors/24.7:v2            zen2  eiger   4f0f2770616135b1   1,062    2024-09-04
    julia/24.9:v1              zen2  eiger   0ff97a74dfcaa44e     539    2024-11-09
    linalg/24.11:rc1           zen2  eiger   b69f4664bf0cd1c4     770    2024-11-20
    linalg/24.11:v1            zen2  eiger   c11f6c85028abf5b     776    2024-12-03
    linalg-complex/24.11:v1    zen2  eiger   846a04b4713d469b     792    2024-12-03
    linaro-forge/24.0.2:v1     zen2  eiger   65734ce35494a5f5     313    2024-07-18
    linaro-forge/24.1:v1       zen2  eiger   b65d7c85adfb317a     344    2024-11-27
    netcdf-tools/2024:v1       zen2  eiger   e7e508c34cf40ccd   3,706    2024-11-14
    prgenv-gnu/24.11:rc4       zen2  eiger   811469b00f030493     570    2024-11-21
    prgenv-gnu/24.11:v1        zen2  eiger   0b6ab5fc4907bb38     572    2024-11-27
    prgenv-gnu/24.7:v1         zen2  eiger   7f68f4c8099de257     478    2024-07-01
    quantumespresso/v7.3.1:v1  zen2  eiger   61d1f21881a65578     864    2024-11-08
    ```

The output above lists all of the uenv that are available on the current system ([Eiger][ref-cluster-eiger] in this case).
The search can be refined by providing a [label][ref-uenv-labels].

??? example "Using labels to refine search"
    ```bash
    # find all uenv with name prgenv-gnu
    uenv image find prgenv-gnu

    # find all uenv with name and version prgenv-gnu/24.11
    uenv image find prgenv-gnu/24.11

    # find all uenv available for daint
    uenv image find @daint

    # find all prgenv-gnu uenv available on a cluster
    uenv image find prgenv-gnu@daint

    # find all uenv in the service namespace with name myenv
    uenv image find service::myenv
    ```

!!! info
    All uenv commands that take a [label][ref-uenv-labels] as an argument use the same flexible syntax [label descriptions][ref-uenv-labels-examples].

## Downloading uenv

??? note "Using uenv for the first time on Balfrin and Eiger"
    With the old version of uenv installed on Balfrin and Eiger, before downloading your first image, a local directory for storing the images must first be created, otherwise you will receive an error message that the repository does not exist.

    To create a repo in the default location, use the following command:

    ```bash title="Create default uenv image repository"
    uenv repo create
    ```

To use a uenv, it first has to be pulled from the registry to local storage where you can access it.
For example, to use the `prgenv-gnu` uenv, use the uenv image pull command:

!!! example "uenv image pull"
    ```bash
    # The following commands have the same effect

    # method 1: pull using the name of the uenv
    uenv image pull prgenv-gnu/24.2:v1

    # method 2: pull using the id of the image
    uenv image pull 3ea1945046d884ee
    ```

Some images can be large, over 10 GB, and it can take a while to download them from the registry.

To view all uenv that have been pulled, and are ready to use use the `uenv image ls` command:

!!! example "listing downloaded uenv"
    ```console
    $ uenv image ls
    uenv                           arch   system  id                size(MB)  date
    editors/24.7:v2                gh200  daint   e7b0d930df729da5   1,270    2024-09-04
    gromacs/2024:v1                gh200  daint   b58e6406810279d5   3,658    2024-09-12
    julia/24.9:v1                  gh200  daint   7a4269abfdadc046   3,939    2024-11-09
    linalg/24.11:v1                gh200  daint   e1640cf6aafdca01   4,461    2024-12-03
    linaro-forge/23.1.2:v1         gh200  daint   fd67b726a90318d6     341    2024-08-26
    namd/3.0:v3                    gh200  daint   49bc65c6905eb5da   4,028    2024-12-12
    netcdf-tools/2024:v1           gh200  daint   2a799e99a12b7c13   1,260    2024-09-04
    prgenv-gnu/24.11:v1            gh200  daint   b81fd6ba25e88782   4,191    2024-11-27
    prgenv-gnu/24.7:v3             gh200  daint   b50ca0d101456970   3,859    2024-08-23
    prgenv-nvfortran/24.11:v1      gh200  daint   d2afc254383cef20   8,703    2025-01-30
    ```

[](){#ref-uenv-restricted-software}
### Accessing restricted software

By default, uenv can be pulled by all users on a system, with no restrictions.

Some uenv are not available to all users, for example the `vasp` images are only available for users with a [VASP][ref-uenv-vasp] license, who are added to the `vasp` group once then have provided CSCS with a copy of their license.

To be able to pull such images a token that authorizes access must be provided.
Tokens are created by CSCS, and stored on SCRATCH in a file that only users who have access to the software can read.

!!! example  "using a token to access VASP"
    ```bash
    uenv image pull \
        --token=/capstor/scratch/cscs/bcumming/tokens/vasp6 \
        --username=vasp6 \
        vasp/v6.4.3:v1
    ```

!!! note
    As of June 2025, the only restricted software is VASP.

!!! note
    Better token management is under development - tokens will be stored in a central location and will be easier to use.

[](){#ref-uenv-start}
## Starting a uenv session

The `uenv start` command will start a new shell with one or more uenv images mounted.
This is very useful for interactive sessions, for example if you want to work in the terminal to compile an application, or set up a Python virtual environment.

!!! example "start an interactive shell to compile an application"
    Here we want to compile an MPI + CUDA application "affinity".

    ```console
    # start the prgenv-gnu uenv, which provides MPI, cuda and CMake
    # use the "default" view, which will load all of the software in the uenv
    $ uenv start prgenv-gnu/24.11:v1 --view=default

    # clone the software and set up the build directory
    $ git clone https://github.com/bcumming/affinity.git
    $ mkdir -p affinity/build
    $ cd affinity/build/

    # configure the build with CMake, then call make to build
    # mpicc, mpic++ and cmake are all provided by the uenv
    $ CXX=mpic++ CC=mpicc cmake ..
    $ make -j

    # run the affinity executable on two nodes - note how the uenv is
    # automatically loaded by slurm on the compute nodes, because CUDA and MPI from
    # the uenv are required to run.
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
The image can be a label, the hash/id of the uenv, or a file:

!!! example "uenv start"
    ```console
    # start the image using the name of the uenv
    $ uenv start netcdf-tools/2024:v1

    # or use the unique id of the uenv
    $ uenv start 499c886f2947538e

    # or provide the path to a squashfs file
    $ uenv start $SCRATCH/my-uenv/gromacs.squashfs
    ```


??? info "what does 'uenv start' actually do?" 
    uenv are [squashfs images](https://docs.kernel.org/filesystems/squashfs.html), which are a compressed file that contains a directory tree.
    The squashfs image of a uenv is a directory that contains all of the software provided by the uenv, along with useful meta data.
    When you run `uenv start` (or `uenv run`, or use the `--uenv` flag with Slurm) the squashfs file is mounted at the mount location for the uenv, which is most often `/user-environment`.

    ```console
    # log into daint
    $ ssh daint.alps.cscs.ch

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

    Loading an environment has no impact on other users or other terminal sessions that you have open on the same node – the mounted environment is only visible in your terminal.
    This means that multiple users on a login node can mount their own environment at the same mount point, without interfering with one-another.

### Views

Running `uenv start $label` on its own will create a shell with the software at `/user-environment` or `/user-tools`, however no changes are made to environment variables like `$PATH`.

Uenv images provide **views**, which will set environment variables that load the software into your environment.
Views are loaded using the `--view` flag for `uenv start` (also for `uenv run` and the Slurm plugin, documented below)

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

#### Modules

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

#### Spack

uenv images provide a full upstream Spack configuration to facilitate building your own software with Spack using the packages installed inside as dependencies.
No view needs to be loaded to use Spack, however all uenv provide a `spack` view that sets some environment variables that contain useful information like the location of the Spack configuration, and the version of Spack that was used to build the uenv.
For more information, see our guide on building software with [Spack and uenv][ref-building-uenv-spack].

[](){#ref-uenv-run}
## Running a uenv

The `uenv run` command can be used to run an application or script in a uenv environment, and return control to the calling shell when the command has finished running.

??? info "how is `uenv run` different from `uenv start`?"
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
    Call `cmake` to configure a build with the `default` view loaded
    ```console
    # run a command
    $ uenv run prgenv-gnu/24.11:v1 --view=default -- cmake -DUSE_GPU=cuda ..
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
```
# mount the uenv prgenv-gnu with the view named default
> srun --uenv=prgenv-gnu/24.7:v3 --view=default ...

# mount an image at an explicit location (/user-tools)
> srun --uenv=$IMAGES/myenv.squashfs:/user-tools ...

# mount multiple images: use a comma to separate the different options
> srun --uenv=prgenv-gnu/24.7:v3,editors/24.7:v2 --view=default,editors:modules ...
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

[](){#ref-uenv-installation}
## Installing the uenv tool

The command line tool can be installed from source, if you are working on a cluster that does not have uenv installed, or if you need to test a new version.

!!! note
    uenv is installed already on CSCS clusters, so installation is not required.

    Only follow these steps if you are advised to test out a new version (e.g. if it has a fix for an issues that you are encountering).

```bash
git clone https://github.com/eth-cscs/uenv2.git
cd uenv2

./install-alps-local.sh # (1)!

# update bashrc
echo "export PATH=\$HOME/.local/\$(uname -m)/bin:\$PATH" >> $HOME/.bashrc 
echo "unset -f uenv" >> $HOME/.bashrc
```

1. Run installation script. This will install uenv in `$HOME/.local/$(uname -m)/bin/`.

!!! warning
    Before uenv can be used, you need to log out then back in again and type `which uenv` to verify that uenv has been installed in your `$HOME` path.

[](){#ref-uenv-labels}
## uenv labels

Uenv are referred to using **labels**, where a label has the following form

```
name/version:tag@system%uarch
```

The different fields are described in the following table:

| label | meaning |
|-------|---------|
| `uarch`   | node microarchitecture: one of `gh200`, `a100`, `zen2`, `mi200`, `mi300a`, `zen3`    |
| `cluster` | name of the cluster, e.g. `daint`, `clariden`, `eiger` or `santis` |
| `name`    | name of the uenv, e.g. `gromacs`, `prgenv-gnu`  |
| `version` | version of the uenv: e.g. `v8.7`, `2025.01` |
| `tag`     | a tag applied by CSCS     |

!!! example "Example labels"
    ??? note "`prgenv-gnu/24.11:v2@daint%gh200`"
        The `prgenv-gnu` programming environment, built on [Daint][ref-cluster-daint] for the Grace-Hopper GH200 (`gh200`) architecture.

        * the _version_ `24.11` refers to the version
        * the _tag_ `v2` refers to a minor update to the uenv (e.g. a bug fix or addition of a new package).

    ??? note "`cp2k/2025.1:v3@eiger%zen2`"
        The uenv provides version 2025.1 of the CP2K simulation code, built for the AMD Rome (`zen2`) architecture of [Eiger][ref-cluster-eiger].

        * the _version_ `2025.1` refers to the CP2K version [v2025.1](https://github.com/cp2k/cp2k/releases/tag/v2025.1)
        * the _tag_ `v2` refers to a minor update by CSCS to the original `v1` version of the uenv that had a bug.

For more information about the labeling scheme, see the [uenv deployment][ref-uenv-deploy-versions] docs.

[](){#ref-uenv-labels-examples}
### Using labels

The uenv command line has a flexible interface for filtering uenv by providing only part of the full label:

```bash
# search for all uenv on the current system that have the name prgenv-gnu
uenv image find prgenv-gnu

# search for all uenv with version 24.11
uenv image find /24.11

# search for all uenv with tag v1
uenv image find :v1

# search for a specific version
uenv image find prgenv-gnu/24.11:v1
```

By default, the `uenv` filters results to uenv that were built on the current cluster.
The name of the current cluster is always available via the `CLUSTER_NAME` environment variable.

```bash
# log into the eiger vCluster
ssh eiger

# this command will search for all prgenv-gnu uenv on _eiger_
uenv image find prgenv-gnu

# use @ to search on a specific system, e.g. on daint:
uenv image find prgenv-gnu@daint

# this can be used to search for all uenv on daint:
uenv image find @daint

# the '*' is a wildcard used meaning "all systems"
# this will show all images on all systems
# NOTE: the * character must be quoted in single quotes
uenv image find @'*'

# search for all images on Alps that were built for gh200 nodes.
uenv image find @'*'%gh200
```

!!! note
    The wild card `*` used for "all systems" must always be escaped in single quotes: `@'*'`.
