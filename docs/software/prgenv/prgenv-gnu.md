[](){#ref-uenv-prgenv-gnu}
# prgenv-gnu

Provides a set of tools and libraries built around the GNU compiler toolchain.
It is the go to programming environment on all systems and target node types, that is it is the first that you should try out when starting to compile an application or create a python virtual environment.

!!! note "alternatives to prgenv-gnu"

    The [`prgenv-nvfortran`][ref-uenv-prgenv-nvfortran] is for applications that require the NVIDIA Fortran compiler - typically because they need to use OpenACC or CUDA Fortran.

    The [`linalg`][ref-uenv-linalg] environment is similar to prgenv-gnu, with additional linear algebra and mesh partitioning algorithms.

## Versioning

The naming scheme is `prgenv-gnu/<version>`, where `<version>` has the `YY.M[M]` format, for example November 2024 is `24.11`, and January 2025 would be `25.1`.

The release schedule is not fixed, with new versions will be released roughly every 3-6 months, when there is a compelling reason to update.

| version   | node types | system |
|-----------|-----------|--------|
| 24.7      | gh200, zen2 | daint, eiger, todi |
| 24.11     | a100, gh200, zen2 | daint, eiger, santis, clariden, bristen |

=== "24.11"

    The key updates in version 24.11 were:

    * upgrading the versions of gcc@13 and cuda@12.6
    * upgrading cray-mpich to version 8.1.30
    * adding kokkos
    * adding gsl

    A complete list of packages exposed via the `default` and `modules` views is:

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

## How to use

The environment is designed as a fairly minimal set of 

There are three ways to access the software provided by prgenv-gnu, once it has been started.

=== "the default view"

    The simplest way to get started is to use the `default` file system view, which automatically loads all of the packages when the uenv is started.

    !!! example "test mpi compilers and python provided by prgenv-gnu/24.11"
        ```bash
        # start using the default view
        > uenv start --view=default prgenv-gnu/24.11:v1

        # the python executable provided by the uenv is the default, and is a recent version
        > which python
        /user-environment/env/default/bin/python
        > python --version 
        Python 3.12.5

        # the mpi compiler wrappers are also available
        > which mpicc
        /user-environment/env/default/bin/mpicc
        > mpicc --version
        gcc (Spack GCC) 13.3.0
        > gcc --version # the compiler wrapper uses the gcc provided by the uenv
        gcc (Spack GCC) 13.3.0
        ```

=== "modules"

    The uenv provides modules for all of the software packages, which can be made available by using the `modules` view in 
    No modules are loaded when a uenv starts, and have to be loaded individually using `module load`.

    !!! example "starting prgenv-gnu and listing the provided modules"
        ```bash
        > uenv start prgenv-gnu/24.11:v1 --view=modules
        > module avail
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
        ```

=== "Spack"

    The gnu programming environment is a very good base for building software with Spack, because it provides compilers, MPI, Python and common packages like hdf5.

    [Check out the guide for using Spack with uenv][ref-building-uenv-spack].

