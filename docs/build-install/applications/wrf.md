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

## Installing by hand

The process for building by hand is more difficult -- so try the Spack approach first, before contacting us.

