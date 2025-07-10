[](){#ref-software-packages-wrf}
# WRF

[The Weather Research & Forecasting Model](https://www.mmm.ucar.edu/models/wrf) (WRF) is a numerical weather prediction system designed for both atmospheric research and weather forecasting.

It is used for CPU-only simulation on [Eiger][ref-cluster-eiger], for which this guide applies.

## Using Spack

Spack provides the [wrf](https://packages.spack.io/package.html?name=wrf) package, which we can install using the [uenv-spack][ref-building-uenv-spack] tool.

First create a working directory where you will install the software.
Here, we create it in your project's [Store][ref-storage-store] path, where the package can be accessed by all users in your project.
```bash
mkdir $STORE/wrf
cd $STORE/wrf
```

Then follow the steps in the [uenv-spack][ref-building-uenv-spack] guide to install `uenv-spack`

```bash
git clone https://github.com/eth-cscs/uenv-spack.git
(cd uenv-spack && ./bootstrap)
```

The [`prgenv-gnu`][ref-uenv-prgenv-gnu] uenv is suitable for building WRF.
```
uenv start prgenv-gnu/24.11:v2 --view=spack
```
In this example we use the latest version of `prgenv-gnu` on Eiger at the time of writing -- check the `prgenv-gnu` [guide][ref-uenv-prgenv-gnu] for the latest version.

```bash
# build the latest version provided by the version of Spack used by prgenv-gnu
$ uenv-spack/uenv-spack $PWD/build --uarch=zen2 --specs=wrf

# build a specific version
$ uenv-spack/uenv-spack $PWD/build --uarch=zen2 --specs=wrf@4.5.2

# build a specific version with WRF-Chem enabled
$ uenv-spack/uenv-spack $PWD/build --uarch=zen2 --specs=wrf@4.5.2 +chem
```

!!! note
    See the wrf Spack [package documentation](https://packages.spack.io/package.html?name=wrf) for information about options that can be enabled or disabled.

Finally, it is time to build the software:

```
cd build
./build
```

This will take 30-60 minutes, while Spack builds some dependencies then WRF.

### Using the Spack installation

The installation creates a module file in the `wrf/build` path, that you created.
Assuming you have installed it in the `$STORE` path for your project, add the following to the top of your sbatch script:

```bash
#SBATCH --uenv=prgenv-gnu/24.11:v2

module use $STORE/wrf/build/modules
module load wrf
```

!!! example "Modules installed by Spack"
    Spack creates a module for every installed package:
    ```console
    $ module use $STORE/wrf/build/modules
    $ module avail

    ------------------ /capstor/store/cscs/cscs/csstaff/wrf/build/modules ------------------
       boost/1.86.0             kokkos-tools/develop    netlib-scalapack/2.2.0
       cmake/3.30.5             kokkos/4.4.01           ninja/1.12.1
       cray-mpich/8.1.30        libtree/3.1.1           openblas/0.3.28
       fftw/3.3.10              lua/5.4.6               osu-micro-benchmarks/5.9
       fmt/11.0.2               lz4/1.10.0              python/3.12.5
       gcc/13.3.0               meson/1.5.1             superlu/5.3.0
       gsl/2.8                  netcdf-c/4.9.2          wrf/4.6.1
       hdf5/1.14.5              netcdf-cxx/4.2          zlib-ng/2.2.1
       kokkos-kernels/4.4.01    netcdf-fortran/4.6.1

    $ module load wrf
    $ which wrf.exe
    /capstor/store/cscs/cscs/csstaff/wrf/build/store/linux-sles15-zen2/gcc-13.3.0/wrf-4.6.1-owj2dsfeslzkulaobdqbad4kh6ojh6n5/main/wrf.exe
    ```

## CRYOWRF

[CRYOWRF](https://gitlabext.wsl.ch/atmospheric-models/CRYOWRF) is a coupled atmosphere-snow cover model with WRF acting as the atmospheric core and SNOWPACK acting as snow cover model.

Building CRYOWRF is a three step process:

1. install the dependencies like [`parallel-netcdf`](https://packages.spack.io/package.html?name=parallel-netcdf)
1. build the SNOWPACK extension
1. Build the bundled WRF

!!! note
    This workflow was developed in July 2025 using the most recent commit `8f83858f` of [CRYOWRF](https://gitlabext.wsl.ch/atmospheric-models/CRYOWRF) (committed in August 2023).

    It isn't very easy to install, and we have tried to streamline the process as much as possible, so take your time and follow the instructions closely.

!!! warning "Eiger only"
    This guide is for building on [Eiger][ref-cluster-eiger], which is an x86-based system.

    Building on the Grace-Hopper clusters like [Daint][ref-cluster-daint] is 

We use [`prgenv-gnu/24.11:v2`][ref-uenv-prgenv-gnu] [uenv][ref-uenv].

### Step 1: install required packages

The first step is to create an empty directory where everything will be installed.
Here, we create it in your project's [Store][ref-storage-store] path, where the package can be accessed by all users in your project.
```bash
export WRFROOT=$STORE/wrf
mkdir $WRFROOT
cd $WRFROOT
```

The following dependencies that are not provided by `prgenv-gnu` are required:

* `parallel-netcdf`: used by WRF.
* `jasper~shared`: used by WPS (`~shared` will build static libraries, required by WPS).
* `zlib-ng` and `libpng`: used by WPS.

Then follow the steups in the [uenv-spack][ref-building-uenv-spack] guide to install `uenv-spack`, which will be used to install the dependencies

```bash
# start the uenv with the spack view enabled
uenv start prgenv-gnu/24.11:v2 --view=spack

# download and install uenv-spack
cd $WRFROOT
git clone https://github.com/eth-cscs/uenv-spack.git
(cd uenv-spack && ./bootstrap)
```

Now we configure and build the environment (the final "build" phase will take a while - 5-10 minutes typically)
```bash
export WRFDEPS=$WRFROOT/dependencies
$WRFROOT/uenv-spack/uenv-spack $WRFDEPS --uarch=zen2 --specs='parallel-netcdf,jasper~shared,libpng,zlib-ng'
cd $WRFDEPS
./build
```

Now the dependencies are installed, finish the uenv spack session:

```bash
exit
```

!!! warning
    This step is performed once, and will install the software in `$WRFDEPS`, where they can be used to build and run WRF.

### Step 2: build SNOWPACK

Use the `default` view of `prgenv-gnu` to build SNOWPACK, WRF and WPS:

```
export WRFROOT=$STORE/wrf
uenv start prgenv-gnu/24.11:v2 --view=default
```

!!! note
    You don't need to load any modules: the `default` view will add everything to your environment.

First download the CRYOWRF software:

```bash
git clone https://gitlabext.wsl.ch/atmospheric-models/CRYOWRF.git $WRFROOT/CRYOWRF
cd $WRFROOT/CRYOWRF
```

Set the following environment variables:

```bash
export NETCDF=/user-environment/env/default
export HDF5=/user-environment/env/default
export PNETCDF=$WRFDEPS/view
export JASPERLIB=$WRFDEPS/view/lib64
export JASPERINC=$WRFDEPS/view/include

export WRF_EM_CORE=1
export WRF_NMM_CORE=0
export WRF_DA_CORE=0

export WRF_CHEM=0
export WRF_KPP=0

export NETCDF4=1
export WRFIO_NCD_LARGE_FILE_SUPPORT=1
export WRFIO_NCD_NO_LARGE_FILE_SUPPORT=0

export CC=mpicc
export FC=mpifort
export CXX=mpic++
```

Then compile SNOWPACK:

```
./clean.sh
./compiler_snow_libs.sh
```

### Step 3: build WRF

The CRYOWRF repository includes a copy of WRF v4.2.1, that has been modified to integrate the SNOWPACK extension build in the previous step.

```bash
export SNOWLIBS=$WRFROOT/CRYOWRF/snpack_for_wrf
cd $WRFROOT/CRYOWRF/WRF
./clean -a
# [choose option 34][nesting: choose option 1] when prompted by configure
./configure
```

!!! info "Set `SNOWLIBS`"
    The `SNOWLIBS` environment variable needs to be set so that WRF can find the extension we compiled earlier.

Open the configure.wrf file that was generated by calling `./configure`, and update the following lines:

```bash
SFC             =    gfortran
SCC             =    gcc
CCOMP           =    gcc
DM_FC           =    mpif90
DM_CC           =    mpicc
FC              =    mpif90
FCBASEOPTS      =    $(FCBASEOPTS_NO_G) $(FCDEBUG) -fallow-argument-mismatch -fallow-invalid-boz -g
NETCDFPATH      =    /user-environment/env/default
```

And apply the following "patch":
```bash
sed -i 's|hdf5hl|hdf5_hl|g' configure.wrf
```

Now compile WRF, which will take a while:

```
./compile em_real -j 64 &> log_compile
```

The compilation output is captured in `log_compile`.
On success, the log should have the message `Executables successfully built`:

```console
$ tail -n14 log_compile

==========================================================================
build started:   Thu 10 Jul 2025 04:54:53 PM CEST
build completed: Thu 10 Jul 2025 05:17:41 PM CEST

--->                  Executables successfully built                  <---

-rwxr-xr-x 1 bcumming csstaff 121952104 Jul 10 17:16 main/ndown.exe
-rwxr-xr-x 1 bcumming csstaff 121728120 Jul 10 17:17 main/real.exe
-rwxr-xr-x 1 bcumming csstaff 120519144 Jul 10 17:17 main/tc.exe
-rwxr-xr-x 1 bcumming csstaff 141159472 Jul 10 17:14 main/wrf.exe

==========================================================================
```

### Step 4: build WPS

Using the same environment as above

```bash
export WRFDEPS=$WRFROOT/dependencies

export NETCDF=/user-environment/env/default
export HDF5=/user-environment/env/default
export PNETCDF=$WRFDEPS/view
export JASPERLIB=$WRFDEPS/view/lib64
export JASPERINC=$WRFDEPS/view/include

cd $WRFROOT/CRYOWRF/WPS-4.2
./configure # choose option 1
```

Update `configure.wps` as follows:
```
SFC                 = gfortran
SCC                 = gcc
DM_FC               = mpif90
DM_CC               = mpicc
FC                  = gfortran
CC                  = gcc
LD                  = $(FC)
FFLAGS              = -ffree-form -O -fconvert=big-endian -frecord-marker=4 -fallow-argument-mismatch -fallow-invalid-boz
F77FLAGS            = -ffixed-form -O -fconvert=big-endian -frecord-marker=4 -fallow-argument-mismatch -fallow-invalid-boz
```

Note the arguments `-fallow-argument-mismatch -fallow-invalid-boz` added to `FFLAGS` and `F77FLAGS`.

Then compile:
```
./compile &> log_compile
```

### Running CRYOWRF

Add the following to your SBATCH job script:
```bash
#SBATCH --uenv=prgenv-gnu/24.11:v2
#SBATCH --view=default

# set LD_LIBRARY_PATH to find the dependencies installed in step 1
export WRFROOT=$STORE/wrf
export WRFDEPS=$WRFROOT/dependencies
export LD_LIBRARY_PATH=$WRFDEPS/view/lib:$WRFDEPS/view/lib64:$LD_LIBRARY_PATH

# set other environment variables

# then run wrf.exe
wrf.exe
```
