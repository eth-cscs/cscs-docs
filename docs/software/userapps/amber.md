[](){#ref-software-amber}
# Amber

!!! warning ""
    Amber is [user software][ref-support-user-apps] on Alps.
    This guide is provided based on our experiences helping users -- however we can't provide the same level of support as we do for [supported software][ref-support-apps].
    See the [main applications page][ref-software] for more information.

    Amber provides many options and tools.
    The process shown here might not provide exactly the tools you need --- you will have to modify the CMake commands to build your required configuration.

[Amber](https://ambermd.org) is a suite of programs for molecular dynamics simulation of biomolecular systems such as proteins, nucleic acids, and small molecules.
It is widely used in computational chemistry and structural biology, with strong GPU acceleration support through its PMEMD engine.

!!! note
    This page documents how to download and install Amber26, which can be freely downloaded and used for non-commercial academic use cases.
    Older versions had different license terms, that stop CSCS from accessing the source.

The instructions provided here are for building Amber on [daint][ref-cluster-daint] with Grace-Hopper support.

## Getting Amber

!!! info "Licensing"
    Amber is distributed under a dual license, with free access for non-profit academic users, and paid licenses for commercial use.
    CSCS is not permitted to redistribute Amber binaries or source code, instead users have to independently agree to the license term, then download the source and compile Amber themselves.

    Users are responsible for following the terms of the licensing terms that they agree to when applying for access on the Amber web site.

A full Amber installation will include both AmberTools and Amber, which are downloaded as separate tar balls.
Both packages are distributed from the [Amber website](https://ambermd.org/GetAmber.php) (see the "How to obtain AmberTools26" and "How to obtain Amber26" sections respectively), where you have to enter your name and institution for each 
If you agree to the non-commercial terms, the download will start immediately.

After downloading, the following two files will have been downloaded:

| file                  | description                 |
| ----                  | -----------                 |
| `ambertools26.tar.bz2`| source code for AmberTools  |
| `pmemd26.tar.bz2`     | source code for Amber/PMEMD |

Which need to be copied to Alps.

!!! example "copying Amber sources to Daint"
    Use ssh to create a remoted directory, and scp to copy the Amber source files to the directory.
    ```console
    $ ssh daint 'mkdir -p ~/ambersource'
    $ scp *.tar.bz2 daint:~/ambersource
    ```

## Building Amber

The `amber/26` uenv provides the compilers and libraries needed to build both a CPU-only and a CUDA-enabled installation.

!!! example "Downloading the `amber/26` uenv"

    **these docs are draft, and we currently provide release candidate `rcN` versions of the amber uenv - this will be a properly tagged and released version once it has been validated**

    ```console
    $ uenv image find amber
    uenv          arch   system  id                size(MB)  date
    amber/26:rc1  gh200  daint   763552b8968853b9   9,104    2026-06-03
    $ uenv image pull build::amber/26:rc1
    ```

After downloading the Amber source archive `pmemd26.tar.bzw`, extract both into the same directory and set the `AMBER_ROOT` environment variable:

```bash title="extract the source archives"
# create a directory where we will unpack and compile the sources
mkdir amber
cd amber
export AMBER_ROOT=$(pwd)

# copy the source code tar balls to this directory and extract them
# extracting the tar balls takes minutes
cp $HOME/ambersources/*.tar.bz2 .
tar -xjf ambertools26.tar.bz2
tar -xjf pmemd26.tar.bz2
export AMBERTOOLS_SRC=$AMBER_ROOT/ambertools26_src
export AMBER_SRC=$AMBER_ROOT/pmemd26_src
```

Then it is time to build Amber and Ambertools.
We create a single installation directory, `$AMBERHOME` in the script below, and install everything into that one directory.

It is possible to build and install different versions with and without MPI and GPU support, and install them all in the same location.
In the script below we configure which options to enable using `amber_mpi`, `amber_cuda` and `amber_openmp` variables.
You can run through the process multiple times, with different combinations of these variables.

* The `amber_mpi=off; amber_cuda=off` build is the fastest: do it first to check that everything works.
* Then build with MPI and GPU support.
* Read the notes below this script to get more hints before starting.

```bash
# start the uenv environment
uenv start --view=amber amber/26:rc1

#
# configure the build (set to on and off as need be)
#
amber_mpi=on
amber_cuda=on
amber_openmp=off
export AMBERHOME=$AMBER_ROOT/amber

#
# create build paths
#

export AMBERTOOLS_BUILD=$AMBER_ROOT/build-ambertools
export AMBER_BUILD=$AMBER_ROOT/build-amber
rm -rf $AMBERTOOLS_BUILD
rm -rf $AMBER_BUILD
mkdir $AMBERTOOLS_BUILD
mkdir $AMBER_BUILD

#
# build ambertools
#

cd $AMBERTOOLS_BUILD
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME \
      -DCOMPILER=GNU \
      -DMPI=$amber_mpi -DCUDA=$amber_cuda -DOPENMP=$amber_openmp \
      -DDOWNLOAD_MINICONDA=false -DBUILD_PYTHON=on \
      -DCMAKE_Fortran_FLAGS="-fPIC" \
      -DBUILD_QUICK=off \
      -DCHECK_UPDATES=false \
      -GNinja \
      $AMBERTOOLS_SRC
ninja  -j64 2> error.log
ninja install

#
# build amber
#

cd $AMBER_BUILD
cmake -DCMAKE_INSTALL_PREFIX=$AMBERHOME \
      -DCOMPILER=GNU \
      -DMPI=$amber_mpi -DCUDA=$amber_cuda -DOPENMP=$amber_openmp \
      -DDOWNLOAD_MINICONDA=false -DBUILD_PYTHON=on \
      -DCMAKE_Fortran_FLAGS="-fPIC" \
      -DPMEMD_ONLY=true \
      -DBUILD_QUICK=off \
      -DCHECK_UPDATES=false \
      -GNinja \
      $AMBER_SRC
ninja -j64 2> error.log
ninja install
```

Notes:

* Amber generates an avelanche of warnings, so we pipe stderr to `error.log`
    * if `make install` fails on one of the steps above, it will print where the error occurred.
* The `fPIC` flag is required to work around problems with the size of the `COMMON` block on Grace-Hopper
* Building the Quick tool takes a long time when building AmberTools took hours to build the GPU versions
    * it is disabled when building AmberTools in the script above (`-DBUILD_QUICK=false`).
    * remove this if you need Quick, and expect to wait for the build to finish.

## Advanced Notes

!!! note
    These notes are for CSCS staff and adventurous users who want to update or modify the `amber` uenv.

Installing Amber is challenging if you want to build only Amber, and have it use dependencies provided via a uenv/container/Spack environment, because Amber:

* vendors dependencies like boost into its source tree, and builds them if they are not found in the calling env
* installs conda which is, in turn, used to install Python packages.

We want to avoid this, because it will greatly increas the build time of Amber, and lead to the creation of many small files.

!!! warning
    The Conda environment installed by the Amber CMake workflow contains 115,000 inodes, which will murder a distributed filesystem.

A specific uenv was configured because of the following requirements:

* CUDA 12.8 is the most recent version of CUDA supported by Ambewr26.
* GCC 12.5 is the most recent non-deprecated version of GCC that is compatible with CUDA 12.8.
* Python with [tkinter](https://docs.python.org/3/library/tkinter.html) support is required by Amber (i.e. `python +tkinter`), which is not the default configuration installed in the `prgenv` uenv.
    * We had to roll back to Python 3.12 as the most recent version

The Amber CMake configuration will use versions of required Python packages that are installed on the system, if it can find them during configuration.
We add all required Python packages to the uenv environment.

One of the dependencies, [`freesasa`](https://pypi.org/project/freesasa/) is not available in Spack, so we install it separately in a `post-install` script.

Putting this together took the best part of a week of work, and there was still some unfinished business:

* Amber has a policy of silently ignoring packages, and trying to build its own copies, for example:
    * The uenv provides well optimised `fftw`, but when building with MPI support, Amber builds its own copy.
    * Amber simply refused to use boost provided by uenv: try to fix that.
    * Every package you can get into the uenv improves build time because Amber builds the dependencies on a single core, and floods output with warning messages while doing so.
* Amber is 2-3 years behind in terms of package versions that it supports, and it might be worth trying to lower the versions of some packages for improved stability
    * e.g. an older version of CMake would produce less warnings.
