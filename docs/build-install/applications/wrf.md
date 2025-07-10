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

Then follow the steups in the [uenv-spack][ref-building-uenv-spack] guide to install `uenv-spack`

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
    See the wrf Spack [package documentation](https://packages.spack.io/package.html?name=wrf) for information about options that can be enabled disabled.

Finally, it is time to build the software:

```
cd build
./build
```

This will take 30-60 minutes, while Spack builds some dependencies then WRF.

### Using the Spack installation

The installation creates a module file in the `wrf/build` path, that you created.
Let's assume you have installed it in the `$STORE` path for your project, add the following to the top of your sbatch script:

```bash
#SBATCH --uenv=prgenv-gnu/24.11:v2

module use $STORE/wrf/build/modules
module load wrf
```

!!! example "Modules installed by Spack"
    Spack creates a module for ever
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

Building CRYOWRF is a two step process:

1. build the SNOWPACK extension
2. Build the bundled WRF

!!! note
    This workflow was developed in July 2025 using the most recent commit `8f83858f` of [CRYOWRF](https://gitlabext.wsl.ch/atmospheric-models/CRYOWRF) (commited in August 2023).

    The code does not appear to be regularly updated, so we expect that it will slowly become more difficult to build as time passes.

!!! warning "Eiger only"
    This guide is for building on [Eiger][ref-cluster-eiger], which is an x86-based system.

    Building on the Grace-Hopper clusters like [Daint][ref-cluster-daint] is 

We use [`prgenv-gnu/24.11:v2`][ref-uenv-prgenv-gnu] [uenv][ref-uenv], which can be downloaded:

```bash
uenv image pull prgenv-gnu/24.11:v2
```

### Step 0: install required packages

```
mkdir $STORE/wrf
cd $STORE/wrf
export WRFPATH=$STORE/wrf
```

```
uenv start prgenv-gnu/24.11:v2 --view=spack
git clone https://github.com/eth-cscs/uenv-spack.git
(cd uenv-spack && ./bootstrap)
./uenv-spack/uenv-spack $PWD/dependencies --uarch=zen2 --specs=parallel-netcdf,jasper,libpng,zlib-ng

cd dependencies
./build
```

This step is performed once, and will install the software in `$WRFPATH/dependencies/view`

Finish the uenv session:
```
exit
```

### Step 1: build SNOWPACK


```
uenv start prgenv-gnu/24.11:v2 --view=default
```

Clone the software

```bash
cd $WRFPATH
git clone https://gitlabext.wsl.ch/atmospheric-models/CRYOWRF.git
cd CRYOWRF
```

!!! note
    You don't need to load any modules: the `default` view will add everything to your environment.


```
export NETCDF=/user-environment/env/default
export HDF5=/user-environment/env/default
export PNETCDF=$WRFPATH/dependencies/view
export WRF_EM_CORE=1
export WRF_NMM_CORE=0
export WRF_DA_CORE=0

export WRF_CHEM=0
export WRF_KPP=0

export NETCDF4=1
export WRFIO_NCD_LARGE_FILE_SUPPORT=1
export WRFIO_NCD_NO_LARGE_FILE_SUPPORT=0

export JASPERLIB=$WRFPATH/dependencies/view/lib64
export JASPERINC=$WRFPATH/dependencies/view/include

export CC=mpicc
export FC=mpifort
export CXX=mpic++

ulimit -s unlimited
ulimit -c unlimited
```

clean and compile
```
./clean.sh
./compiler_snow_libs.sh
```


### Step 2: build WRF

The CRYOWRF repository includes a copy of WRF v4.2.1, that has been modified to integrate the SNOWPACK extension build in step 1.

```
export SNOWLIBS=$WRFPATH/CRYOWRF/snpack_for_wrf
cd  WRF
./clean -a
# [choose option 35][nesting: choose option 1] when prompted by configure
./configure
```

!!! info "Set `SNOWLIBS`"
    The `SNOWLIBS` environment variable needs to be set so that WRF can find the extension we compiled earlier.

Make sure that the following lines are set in `configure.wrf`:
```
SFC             =    gfortran
SCC             =    gcc
CCOMP           =    gcc
DM_FC           =    mpif90
DM_CC           =    mpicc
FC              =    mpif90
FCBASEOPTS      =    $(FCBASEOPTS_NO_G) $(FCDEBUG) -fallow-argument-mismatch -fallow-invalid-boz -g
NETCDFPATH      =    /user-environment/env/default
```

Now compile WRF :fingers-crossed:

```
./compile em_real -j 64 &> log_compile
```
