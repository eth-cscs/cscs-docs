[](){#ref-uenv-prgenv-gnu}
# prgenv-gnu

Provides a set of tools and libraries built around the GNU compiler toolchain.
It is the go to programming environment on all systems and target node types, that is it is the first that you should try out when starting to compile an application or create a python virtual environment.

!!! note "alternatives to prgenv-gnu"

    The [`prgenv-nvfortran`][ref-uenv-prgenv-nvfortran] is for applications that require the NVIDIA Fortran compiler - typically because they need to use OpenACC or CUDA Fortran.

    The [`linalg`][ref-uenv-linalg] environment is similar to prgenv-gnu, with additional linear algebra and mesh partitioning algorithms.

    The [`prgenv-gnu-openmpi`][ref-uenv-prgenv-gnu-openmpi] is otherwise similar to `prgenv-gnu`, but provides OpenMPI instead of Cray MPICH.

    The [`prgenv-intel`][ref-uenv-prgenv-intel] is similar to `prgenv-gnu`, but provides the intel OneAPI compiler.
    Only available on [Eiger][ref-cluster-eiger], and provides fewer general libraries than the full GNU environment.

[](){#ref-uenv-prgenv-gnu-versioning}
## Versioning

The naming scheme is `prgenv-gnu/<version>`, where `<version>` has the `YY.M[M]` format, for example November 2024 is `24.11`, and January 2025 would be `25.1`.

The release schedule is not fixed, with new versions will be released roughly every 3-6 months, when there is a compelling reason to update.

| version            | node types        | system                                  |
|--------------------|-------------------|-----------------------------------------|
| 26.3               | gh200, zen2       | daint, eiger, santis, clariden          |
| 25.11              | gh200, zen2       | daint, eiger, santis, clariden          |
| 25.6               | gh200, zen2       | daint, eiger, santis, clariden          |

??? note "Removed versions"
    The following versions have been removed:

    | version            | Removal date |
    |--------------------|--------------|
    | 24.11              | April 2026   |
    | 24.7               | April 2026   |

### Deprecation policy

We will provide full support for 12 months after the uenv image is released, and remove the images when they are no longer being used or when system upgrades break their functionality on the system.

* It is recommended to document how you compiled and set up your workflow using `prgenv-gnu` so that you can recreate it with future versions.

### Versions

=== "26.3"

    The key updates in version 26.3 compared to 25.11 are upgrading CUDA to version 13.1 and Cray MPICH to 9.1.0.

    ??? info "all packages exposed via the `default` and `modules` views in `v1`"
        * [aws-ofi-nccl@1.17.2](https://packages.spack.io/package.html?name=aws-ofi-nccl)
        * [boost@1.89.0](https://packages.spack.io/package.html?name=boost)
        * [cmake@3.31.11](https://packages.spack.io/package.html?name=cmake)
        * [cray-mpich@9.1.0](https://packages.spack.io/package.html?name=cray-mpich)
        * [cuda@13.1.1](https://packages.spack.io/package.html?name=cuda)
        * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
        * [fmt@12.1.0](https://packages.spack.io/package.html?name=fmt)
        * [gcc@14.3.0](https://packages.spack.io/package.html?name=gcc)
        * [gmp@6.3.0](https://packages.spack.io/package.html?name=gmp)
        * [gsl@2.8](https://packages.spack.io/package.html?name=gsl)
        * [hdf5@1.14.6](https://packages.spack.io/package.html?name=hdf5)
        * [kokkos@4.7.02](https://packages.spack.io/package.html?name=kokkos)
        * [kokkos-kernels@4.7.02](https://packages.spack.io/package.html?name=kokkos-kernels)
        * [kokkos-tools@develop](https://packages.spack.io/package.html?name=kokkos-tools)
        * [libfabric@2.4.0](https://packages.spack.io/package.html?name=libfabric)
        * [libtree@3.1.1](https://packages.spack.io/package.html?name=libtree)
        * [lua@5.4.8](https://packages.spack.io/package.html?name=lua)
        * [lz4@1.10.0](https://packages.spack.io/package.html?name=lz4)
        * [meson@1.10.1](https://packages.spack.io/package.html?name=meson)
        * [nccl@2.29.2-1](https://packages.spack.io/package.html?name=nccl)
        * [nccl-tests@2.17.6](https://packages.spack.io/package.html?name=nccl-tests)
        * [netcdf-c@4.9.3](https://packages.spack.io/package.html?name=netcdf-c)
        * [netcdf-cxx@4.2](https://packages.spack.io/package.html?name=netcdf-cxx)
        * [netcdf-cxx4@4.3.1](https://packages.spack.io/package.html?name=netcdf-cxx4)
        * [netcdf-fortran@4.6.2](https://packages.spack.io/package.html?name=netcdf-fortran)
        * [netlib-scalapack@2.2.2](https://packages.spack.io/package.html?name=netlib-scalapack)
        * [ninja@1.13.2](https://packages.spack.io/package.html?name=ninja)
        * [openblas@0.3.30](https://packages.spack.io/package.html?name=openblas)
        * [osu-micro-benchmarks@7.5.2](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
        * [papi@7.2.0](https://packages.spack.io/package.html?name=papi)
        * [python@3.14.3](https://packages.spack.io/package.html?name=python)
        * [superlu@7.0.1](https://packages.spack.io/package.html?name=superlu)
        * [xcb-util-cursor@0.1.5](https://packages.spack.io/package.html?name=xcb-util-cursor)
        * [zlib-ng@2.3.3](https://packages.spack.io/package.html?name=zlib-ng)

=== "25.11"

    The key update in version 25.11 compared to 25.6 is that libfabric was updated from the system-provided version 1.22 to a a newer version 2.3.1 built from [source](https://github.com/ofiwg/libfabric).
    This newer version brings stability and performance improvements, in particular to NCCL workloads.

    `netcdf-cxx4` also was added to the uenv, alongside the other NetCDF packages `netcdf-c`, `netcdf-cxx`, and `netcdf-fortran`.

    ??? info "all packages exposed via the `default` and `modules` views in `v1`"
        * [aws-ofi-nccl@1.16.3](https://packages.spack.io/package.html?name=aws-ofi-nccl)
        * [boost@1.88.0](https://packages.spack.io/package.html?name=boost)
        * [cmake@3.31.9](https://packages.spack.io/package.html?name=cmake)
        * [cray-mpich@8.1.32](https://packages.spack.io/package.html?name=cray-mpich)
        * [cuda@12.9.0](https://packages.spack.io/package.html?name=cuda)
        * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
        * [fmt@12.0.0](https://packages.spack.io/package.html?name=fmt)
        * [gcc@14.2.0](https://packages.spack.io/package.html?name=gcc)
        * [gsl@2.8](https://packages.spack.io/package.html?name=gsl)
        * [hdf5@1.14.6](https://packages.spack.io/package.html?name=hdf5)
        * [kokkos@4.7.01](https://packages.spack.io/package.html?name=kokkos)
        * [kokkos-kernels@4.7.01](https://packages.spack.io/package.html?name=kokkos-kernels)
        * [kokkos-tools@develop](https://packages.spack.io/package.html?name=kokkos-tools)
        * [libfabric@2.3.1](https://packages.spack.io/package.html?name=libfabric)
        * [libtree@3.1.1](https://packages.spack.io/package.html?name=libtree)
        * [lua@5.4.6](https://packages.spack.io/package.html?name=lua)
        * [lz4@1.10.0](https://packages.spack.io/package.html?name=lz4)
        * [meson@1.8.5](https://packages.spack.io/package.html?name=meson)
        * [nccl@2.28.3-1](https://packages.spack.io/package.html?name=nccl)
        * [nccl-tests@2.16.3](https://packages.spack.io/package.html?name=nccl-tests)
        * [netcdf-c@4.9.3](https://packages.spack.io/package.html?name=netcdf-c)
        * [netcdf-cxx@4.2](https://packages.spack.io/package.html?name=netcdf-cxx)
        * [netcdf-cxx4@4.3.1](https://packages.spack.io/package.html?name=netcdf-cxx4)
        * [netcdf-fortran@4.6.2](https://packages.spack.io/package.html?name=netcdf-fortran)
        * [netlib-scalapack@2.2.2](https://packages.spack.io/package.html?name=netlib-scalapack)
        * [ninja@1.13.0](https://packages.spack.io/package.html?name=ninja)
        * [openblas@0.3.30](https://packages.spack.io/package.html?name=openblas)
        * [osu-micro-benchmarks@7.5.1](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
        * [papi@7.2.0](https://packages.spack.io/package.html?name=papi)
        * [python@3.14.0](https://packages.spack.io/package.html?name=python)
        * [superlu@7.0.0](https://packages.spack.io/package.html?name=superlu)
        * [xcb-util-cursor@0.1.5](https://packages.spack.io/package.html?name=xcb-util-cursor)
        * [zlib-ng@2.2.4](https://packages.spack.io/package.html?name=zlib-ng)

=== "25.6"

    The key updates in version 25.6 compared to 24.11 are:

    * upgrading GCC to version 14 and CUDA to version 12.9
    * upgrading cray-mpich to version 8.1.32
    * adding xcb-util-cursor to the default view to allow the [NVIDIA Nsight UIs][ref-devtools-nsight] to be used without manual workarounds

    The spack version used to build the packages was also upgraded to 1.0.

    v2 of the uenv fixes the `modules` view, where `gcc` was missing in v1.

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

[](){#ref-uenv-prgenv-gnu-how-to-use}
## How to use

The environment provides a set of tools and libraries based on the GNU compiler toolchain for building scientific applications.

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

    [Check out the guide for using Spack with uenv][ref-build-uenv-spack].

