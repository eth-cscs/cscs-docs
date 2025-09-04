[](){#ref-uenv-prgenv-gnu}
# prgenv-gnu

Provides a set of tools and libraries built around the GNU compiler toolchain.
It is the go to programming environment on all systems and target node types, that is it is the first that you should try out when starting to compile an application or create a python virtual environment.

!!! note "alternatives to prgenv-gnu"

    The [`prgenv-nvfortran`][ref-uenv-prgenv-nvfortran] is for applications that require the NVIDIA Fortran compiler - typically because they need to use OpenACC or CUDA Fortran.

    The [`linalg`][ref-uenv-linalg] environment is similar to prgenv-gnu, with additional linear algebra and mesh partitioning algorithms.

[](){#ref-uenv-prgenv-gnu-versioning}
## Versioning

The naming scheme is `prgenv-gnu/<version>`, where `<version>` has the `YY.M[M]` format, for example November 2024 is `24.11`, and January 2025 would be `25.1`.

The release schedule is not fixed, with new versions will be released roughly every 3-6 months, when there is a compelling reason to update.

| version            | node types        | system                                  |
|--------------------|-------------------|-----------------------------------------|
| 25.6               | gh200             | daint, eiger, santis, clariden          |
| 24.11              | a100, gh200, zen2 | daint, eiger, santis, clariden, bristen |
| 24.7               | gh200, zen2       | daint, eiger, todi                      |

### Deprecation policy

We will provide full support for 12 months after the uenv image is released, and remove the images when they are no longer being used or when system upgrades break their functionality on the system.

* It is recommended to document how you compiled and set up your workflow using `prgenv-gnu` so that you can recreate it with future versions.
* The 24.7 release is no longer supported and will be removed at the end of July 2025 - users are encouraged to update to 24.11 or later, before requesting support.

### Versions

=== "25.6"

    The key updates in version 25.6 compared to 24.11 are:

    * upgrading GCC to version 14 and CUDA to version 12.9
    * upgrading cray-mpich to version 8.1.32
    * adding xcb-util-cursor to the default view to allow the [NVIDIA Nsight UIs][ref-devtools-nsight] to be used without manual workarounds

    The spack version used to build the packages was also upgraded to 1.0.

    ??? info "all packages exposed via the `default` and `modules` views in `v1`"
        * [aws-ofi-nccl@1.16.0](https://packages.spack.io/package.html?name=aws-ofi-nccl)
        * [boost@1.88.0](https://packages.spack.io/package.html?name=boost)
        * [cmake@3.31.8](https://packages.spack.io/package.html?name=cmake)
        * [cray-mpich@8.1.32](https://packages.spack.io/package.html?name=cray-mpich)
        * [cuda@12.9.0](https://packages.spack.io/package.html?name=cuda)
        * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
        * [fmt@11.2.0](https://packages.spack.io/package.html?name=fmt)
        * [gcc@14.2.0](https://packages.spack.io/package.html?name=gcc)
        * [gsl@2.8](https://packages.spack.io/package.html?name=gsl)
        * [hdf5@1.14.6](https://packages.spack.io/package.html?name=hdf5)
        * [kokkos@4.6.01](https://packages.spack.io/package.html?name=kokkos)
        * [kokkos-kernels@4.6.01](https://packages.spack.io/package.html?name=kokkos-kernels)
        * [kokkos-tools@develop](https://packages.spack.io/package.html?name=kokkos-tools)
        * [libtree@3.1.1](https://packages.spack.io/package.html?name=libtree)
        * [lua@5.4.6](https://packages.spack.io/package.html?name=lua)
        * [lz4@1.10.0](https://packages.spack.io/package.html?name=lz4)
        * [meson@1.7.0](https://packages.spack.io/package.html?name=meson)
        * [nccl@2.27.5-1](https://packages.spack.io/package.html?name=nccl)
        * [nccl-tests@2.16.3](https://packages.spack.io/package.html?name=nccl-tests)
        * [netcdf-c@4.9.2](https://packages.spack.io/package.html?name=netcdf-c)
        * [netcdf-cxx@4.2](https://packages.spack.io/package.html?name=netcdf-cxx)
        * [netcdf-fortran@4.6.1](https://packages.spack.io/package.html?name=netcdf-fortran)
        * [netlib-scalapack@2.2.2](https://packages.spack.io/package.html?name=netlib-scalapack)
        * [ninja@1.12.1](https://packages.spack.io/package.html?name=ninja)
        * [openblas@0.3.29](https://packages.spack.io/package.html?name=openblas)
        * [osu-micro-benchmarks@7.5](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
        * [papi@7.1.0](https://packages.spack.io/package.html?name=papi)
        * [python@3.13.5](https://packages.spack.io/package.html?name=python)
        * [superlu@7.0.0](https://packages.spack.io/package.html?name=superlu)
        * [xcb-util-cursor@0.1.5](https://packages.spack.io/package.html?name=xcb-util-cursor)
        * [zlib-ng@2.2.4](https://packages.spack.io/package.html?name=zlib-ng)

=== "24.11"

    The key updates in version 24.11:v1 from the 24.7 version were:

    * upgrading the versions of gcc@13 and cuda@12.6
    * upgrading cray-mpich to version 8.1.30
    * adding kokkos
    * adding gsl

    ??? info "all packages exposed via the `default` and `modules` views in `v1`"
        * [aws-ofi-nccl@git.v1.9.2-aws_1.9.2](https://packages.spack.io/package.html?name=aws-ofi-nccl)
        * [boost@1.86.0](https://packages.spack.io/package.html?name=boost)
        * [cmake@3.30.5](https://packages.spack.io/package.html?name=cmake)
        * [cray-mpich@8.1.30](https://packages.spack.io/package.html?name=cray-mpich)
        * [cuda@12.6.2](https://packages.spack.io/package.html?name=cuda)
            * in the `gh200` and `a100` images
        * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
        * [fmt@11.0.2](https://packages.spack.io/package.html?name=fmt)
        * [gcc@13.3.0](https://packages.spack.io/package.html?name=gcc)
        * [gsl@2.8](https://packages.spack.io/package.html?name=gsl)
        * [hdf5@1.14.5](https://packages.spack.io/package.html?name=hdf5)
        * [kokkos-kernels@4.4.01](https://packages.spack.io/package.html?name=kokkos-kernels)
        * [kokkos-tools@develop](https://packages.spack.io/package.html?name=kokkos-tools)
        * [kokkos@4.4.01](https://packages.spack.io/package.html?name=kokkos)
        * [libtree@3.1.1](https://packages.spack.io/package.html?name=libtree)
        * [lua@5.4.6](https://packages.spack.io/package.html?name=lua)
        * [lz4@1.10.0](https://packages.spack.io/package.html?name=lz4)
        * [meson@1.5.1](https://packages.spack.io/package.html?name=meson)
        * [nccl-tests@2.13.6](https://packages.spack.io/package.html?name=nccl-tests)
        * [nccl@2.22.3-1](https://packages.spack.io/package.html?name=nccl)
        * [netlib-scalapack@2.2.0](https://packages.spack.io/package.html?name=netlib-scalapack)
        * [ninja@1.12.1](https://packages.spack.io/package.html?name=ninja)
        * [openblas@0.3.28](https://packages.spack.io/package.html?name=openblas)
            * built with the OpenMP threading back end
        * [osu-micro-benchmarks@5.9](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
        * [papi@7.1.0](https://packages.spack.io/package.html?name=papi)
        * [python@3.12.5](https://packages.spack.io/package.html?name=python)
        * [superlu@5.3.0](https://packages.spack.io/package.html?name=superlu)
        * [zlib-ng@2.2.1](https://packages.spack.io/package.html?name=zlib-ng)

    ??? info "24.7:v2 changelog"
        The `v2` update added `netcdf`, specifically the following packages:

        * [netcdf-c@4.9.2](https://packages.spack.io/package.html?name=netcdf-c)
        * [netcdf-cxx@4.2](https://packages.spack.io/package.html?name=netcdf-cxx)
        * [netcdf-fortran@4.6.1](https://packages.spack.io/package.html?name=netcdf-fortran)

[](){#ref-uenv-prgenv-gnu-how-to-use}
## How to use

The environment is designed as a fairly minimal set of 

There are three ways to access the software provided by prgenv-gnu, once it has been started.

=== "the `default` view"

    The simplest way to get started is to use the `default` file system view, which automatically loads all of the packages when the uenv is started.

    !!! example "test mpi compilers and python provided by prgenv-gnu/24.11"
        ```console
        # start using the default view
        $ uenv start --view=default prgenv-gnu/25.6:v1

        # the python executable provided by the uenv is the default, and is a recent version
        $ which python
        /user-environment/env/default/bin/python
        $ python --version 
        Python 3.13.5

        # the mpi compiler wrappers are also available
        $ which mpicc
        /user-environment/env/default/bin/mpicc
        $ mpicc --version
        gcc (Spack GCC) 14.2.0
        $ gcc --version # the compiler wrapper uses the gcc provided by the uenv
        gcc (Spack GCC) 14.2.0
        ```

=== "modules"

    The uenv provides modules for all of the software packages, which can be made available by using the `modules` view in 
    No modules are loaded when a uenv starts, and have to be loaded individually using `module load`.

    !!! example "starting prgenv-gnu and listing the provided modules"
        ```console
        $ uenv start prgenv-gnu/25.6:v1 --view=modules
        $ module avail
            ---------------------------- /user-environment/modules ----------------------------
               aws-ofi-nccl/1.16.0      meson/1.7.0
               boost/1.88.0             nccl-tests/2.16.3
               cmake/3.31.8             nccl/2.27.5-1
               cray-mpich/8.1.32        netcdf-c/4.9.2
               cuda/12.9.0              netcdf-cxx/4.2
               fftw/3.3.10              netcdf-fortran/4.6.1
               fmt/11.2.0               netlib-scalapack/2.2.2
               gsl/2.8                  ninja/1.12.1
               hdf5/1.14.6              openblas/0.3.29
               kokkos-kernels/4.6.01    osu-micro-benchmarks/7.5
               kokkos-tools/develop     papi/7.1.0
               kokkos/4.6.01            python/3.13.5
               libfabric/1.22.0         squashfs/4.6.1
               libtree/3.1.1            superlu/7.0.0
               lua/5.4.6                xcb-util-cursor/0.1.5
               lz4/1.10.0               zlib-ng/2.2.4
        ```

=== "Spack"

    The gnu programming environment is a very good base for building software with Spack, because it provides compilers, MPI, Python and common packages like hdf5.

    [Check out the guide for using Spack with uenv][ref-building-uenv-spack].

