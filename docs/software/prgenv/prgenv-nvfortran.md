[](){#ref-uenv-prgenv-nvfortran}
# prgenv-nvfortran

The `prgenv-nvfortran` uenv provides a set of tools and libraries for building applications that need the NVIDIA Fortran compiler
Specifically, it is intended for building and running applications that **require** one of the following:
* OpenACC for GPU acceleration;
* CUDA Fortran for GPU acceleration.

!!! note
    By default, use the `prgenv-gnu` toolchain for a generic environment for building GPU applications.
    It provides CUDA and libraries with GPU support enabled for the Grace-Hopper nodes, the gnu compiler toolchain that it provides has better C and C++ standards compliance, and it also provides more libraries and tools than this `nvfortran` uenv.

## Versioning

The naming scheme is `prgenv-nvfortran/<version>:v<i>`, where `<version>` matches the version of the NVIDIA HPC SDK.

* the SDK is released every two months, and is numbered in the `YY.M[M]` format, e.g. `24.1` and `24.11`.
* the `prgenv-nvfortran` will be released two or three times a year (every second NVHPC release).

The currently supported versions are:

| `prgenv-nvfortran` | NVHPC |
| --------------     | ----- |
| 24.11              | 24.11 |
| 25.7               | 25.7  |

??? note "I need a different version"
    If you need a version of the NVHPC SDK that is not provided, e.g. the 25.1 version that falls between 24.11 and 25.4, make a request on the [CSCS service desk](https://jira.cscs.ch/plugins/servlet/desk).

=== "25.7"

    !!! info "The v2 tag adds the `+cxx` variant to `hdf5`"

    Version 25.7 provides the following software:

    * [cmake@3.31.8](https://packages.spack.io/package.html?name=cmake)
    * [cray-mpich@8.1.32](https://packages.spack.io/package.html?name=cray-mpich)
    * [cuda@12.9.0](https://packages.spack.io/package.html?name=cuda)
    * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
    * [fmt@11.2.0](https://packages.spack.io/package.html?name=fmt)
    * [gcc@13.4.0](https://packages.spack.io/package.html?name=gcc)
    * [hdf5@1.14.6](https://packages.spack.io/package.html?name=hdf5)
    * [libtree@3.1.1](https://packages.spack.io/package.html?name=libtree)
    * [lua@5.4.6](https://packages.spack.io/package.html?name=lua)
    * [lz4@1.10.0](https://packages.spack.io/package.html?name=lz4)
    * [meson@1.7.0](https://packages.spack.io/package.html?name=meson)
    * [netcdf-c@4.9.2](https://packages.spack.io/package.html?name=netcdf-c)
    * [netcdf-fortran@4.6.1](https://packages.spack.io/package.html?name=netcdf-fortran)
    * [ninja@1.12.1](https://packages.spack.io/package.html?name=ninja)
    * [nvhpc@25.7](https://packages.spack.io/package.html?name=nvhpc)
    * [nvpl-blas@0.4.0.1](https://packages.spack.io/package.html?name=nvpl-blas)
    * [nvpl-lapack@0.3.0](https://packages.spack.io/package.html?name=nvpl-lapack)
    * [osu-micro-benchmarks@7.5](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
    * [python@3.13.5](https://packages.spack.io/package.html?name=python)
    * [zlib-ng@2.2.4](https://packages.spack.io/package.html?name=zlib-ng)

    The package main update from the previous version 24.11 is the addition of NCCL, the addition of `libfabric` to the uenv, and the SquashFS tools:

    * [aws-ofi-nccl@1.16.0](https://packages.spack.io/package.html?name=aws-ofi-nccl)
    * [nccl-tests@2.16.3](https://packages.spack.io/package.html?name=nccl-tests)
    * [nccl@2.27.5-1](https://packages.spack.io/package.html?name=nccl)
    * [libfabric@1.22.0](https://packages.spack.io/package.html?name=libfabric)
    * [squashfs@4.6.1](https://packages.spack.io/package.html?name=squashfs)

    !!! note
        Version `25.7` upgraded to Spack 1.0, so any Spack workflows based on the previous version will probably need to be updated to the latest Spack version.

=== "24.11"

    Version 24.11 provides the following software:

    * [cmake@3.30.5](https://packages.spack.io/package.html?name=cmake)
    * [cray-mpich@8.1.30](https://packages.spack.io/package.html?name=cray-mpich)
    * [cuda@12.6.0](https://packages.spack.io/package.html?name=cuda)
    * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
    * [fmt@11.0.2](https://packages.spack.io/package.html?name=fmt)
    * [gcc@13.2.0](https://packages.spack.io/package.html?name=gcc)
    * [hdf5@1.14.5](https://packages.spack.io/package.html?name=hdf5)
    * [libtree@3.1.1](https://packages.spack.io/package.html?name=libtree)
    * [lua@5.4.6](https://packages.spack.io/package.html?name=lua)
    * [lz4@1.10.0](https://packages.spack.io/package.html?name=lz4)
    * [meson@1.5.1](https://packages.spack.io/package.html?name=meson)
    * [netcdf-c@4.9.2](https://packages.spack.io/package.html?name=netcdf-c)
    * [netcdf-fortran@4.6.1](https://packages.spack.io/package.html?name=netcdf-fortran)
    * [ninja@1.12.1](https://packages.spack.io/package.html?name=ninja)
    * [nvhpc@24.11](https://packages.spack.io/package.html?name=nvhpc)
    * [nvpl-blas@0.3.0](https://packages.spack.io/package.html?name=nvpl-blas)
    * [nvpl-lapack@0.2.3.1](https://packages.spack.io/package.html?name=nvpl-lapack)
    * [osu-micro-benchmarks@5.9](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
    * [python@3.12.5](https://packages.spack.io/package.html?name=python)
    * [zlib-ng@2.2.1](https://packages.spack.io/package.html?name=zlib-ng)

## How to use

The image is only provided on Alps systems that have NVIDIA GPUs.
To see which versions have been installed on a system:

```bash
# search for uenv on the current system
uenv image find prgenv-nvfortran

# search for uenv on all systems
uenv image find prgenv-nvfortran@*

# pull a version
uenv image pull prgenv-nvfortran/25.7:v1
```

=== "the `nvfort` view"

    The `nvfort` view loads all of the packages into your environment (equivalent to loading all the modules at once):

    ```bash
    uenv start prgenv-nvfortran/25.7:v1 --view=nvfort
    mpif90 --version
    ```

    The above example shows that the MPI compiler wrappers are using the underlying NVIDIA compiler.
    The following wrappers are available:

    * `mpif77`
    * `mpif90`
    * `mpifort`

    And the following C/C++ wrappers are available:

    * `mpicc`
    * `mpicxx`

=== "the modules view"

    The modules view will start the uenv, and make a set of modules available:

    ```console
    $ uenv start prgenv-nvfortran/25.7:v1 --view=nvfort,modules
    $ module avail
    ---------------------------- /user-environment/modules ------------------------
         aws-ofi-nccl/1.16.0    libtree/3.1.1           nvhpc/25.7
         cmake/3.31.8           lua/5.4.6               nvpl-blas/0.4.0.1
         cray-mpich/8.1.32      lz4/1.10.0              nvpl-lapack/0.3.0
         cuda/12.9.0            meson/1.7.0             osu-micro-benchmarks/7.5
         fftw/3.3.10            nccl-tests/2.16.3       python/3.13.5
         fmt/11.2.0             nccl/2.27.5-1           squashfs/4.6.1
         gcc/13.4.0             netcdf-c/4.9.2          zlib-ng/2.2.4
         hdf5/1.14.6            netcdf-fortran/4.6.1
         libfabric/1.22.0       ninja/1.12.1
    ```

    None of the modules are loaded by default, so you will have to load the required modules
