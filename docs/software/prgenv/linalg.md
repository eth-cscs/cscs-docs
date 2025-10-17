[](){#ref-uenv-linalg}
# linalg

The `linalg` and `linalg-complex` uenvs are similar to the [`prgenv-gnu`][ref-uenv-prgenv-gnu] and [`prgenv-nvfortran`][ref-uenv-prgenv-nvfortran] uenvs in that they don't provide a specific application, but common libraries useful as a base for building other applications.
They contain linear algebra and mesh partitioning libraries for a broad range of use cases.

The two uenvs contain otherwise identical packages, except that `linalg-complex` contains `petsc` and `trilinos` with complex types enabled, but without the [`hypre`](https://packages.spack.io/package.html?name=hypre) package.
`hypre` only supports double precision.
See below for the full list of packages in each version of the uenv.
Note that many of the packages available in `linalg` and `linalg-complex` are also available in [`prgenv-gnu`][ref-uenv-prgenv-gnu].

## Versioning

The uenvs are available in the following versions on the following systems:

| version | node types | system |
|-----------|-----------|--------|
| 25.10 | gh200, zen2 | daint, eiger |
| 24.11 | gh200, zen2 | daint, eiger |

=== "25.10"
    In version 25.10, the common set of packages in both uenvs is:

    * [arpack-ng@3.9.1](https://packages.spack.io/package.html?name=arpack-ng)
    * [blaspp@2025.05.28](https://packages.spack.io/package.html?name=blaspp)
    * [blt@0.7.1](https://packages.spack.io/package.html?name=blt)
    * [boost@1.88.0](https://packages.spack.io/package.html?name=boost)
    * [camp@2025.03.0](https://packages.spack.io/package.html?name=camp)
    * [cmake@3.31.8](https://packages.spack.io/package.html?name=cmake)
    * [cray-mpich@8.1.32](https://packages.spack.io/package.html?name=cray-mpich)
    * [dla-future@0.10.0](https://packages.spack.io/package.html?name=dla-future)
    * [dla-future-fortran@0.5.0](https://packages.spack.io/package.html?name=dla-future-fortran)
    * [eigen@3.4.0](https://packages.spack.io/package.html?name=eigen)
    * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
    * [fmt@11.0.2](https://packages.spack.io/package.html?name=fmt)
    * [gsl@2.8](https://packages.spack.io/package.html?name=gsl)
    * [hdf5@1.14.6](https://packages.spack.io/package.html?name=hdf5)
    * [hwloc@2.12.2](https://packages.spack.io/package.html?name=hwloc)
    * [kokkos@4.3.01](https://packages.spack.io/package.html?name=kokkos)
    * [kokkos-kernels@4.3.01](https://packages.spack.io/package.html?name=kokkos-kernels)
    * [kokkos-tools@develop](https://packages.spack.io/package.html?name=kokkos-tools)
    * [lapackpp@2025.05.28](https://packages.spack.io/package.html?name=lapackpp)
    * [libfabric@1.22.0](https://packages.spack.io/package.html?name=libfabric)
    * [libtree@3.1.1](https://packages.spack.io/package.html?name=libtree)
    * [libxml2@2.13.5](https://packages.spack.io/package.html?name=libxml2)
    * [lua@5.4.6](https://packages.spack.io/package.html?name=lua)
    * [lz4@1.10.0](https://packages.spack.io/package.html?name=lz4)
    * [lzo@2.10](https://packages.spack.io/package.html?name=lzo)
    * [meson@1.8.5](https://packages.spack.io/package.html?name=meson)
    * [metis@5.1.0](https://packages.spack.io/package.html?name=metis)
    * [mimalloc@3.1.5](https://packages.spack.io/package.html?name=mimalloc)
    * [mumps@5.8.1](https://packages.spack.io/package.html?name=mumps)
    * [nco@5.3.4](https://packages.spack.io/package.html?name=nco)
    * [netcdf-c@4.9.3](https://packages.spack.io/package.html?name=netcdf-c)
    * [netlib-scalapack@2.2.2](https://packages.spack.io/package.html?name=netlib-scalapack)
    * [ninja@1.13.0](https://packages.spack.io/package.html?name=ninja)
    * [openblas@0.3.30](https://packages.spack.io/package.html?name=openblas)
    * [osu-micro-benchmarks@7.5.1](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
    * [p4est@2.8](https://packages.spack.io/package.html?name=p4est)
    * [parmetis@4.0.3](https://packages.spack.io/package.html?name=parmetis)
    * [petsc@3.24.0](https://packages.spack.io/package.html?name=petsc)
    * [pika@0.34.0](https://packages.spack.io/package.html?name=pika)
    * [python@3.14.0](https://packages.spack.io/package.html?name=python)
    * [stdexec@25.03.rc1](https://packages.spack.io/package.html?name=stdexec)
    * [suite-sparse@7.3.1](https://packages.spack.io/package.html?name=suite-sparse)
    * [superlu@7.0.0](https://packages.spack.io/package.html?name=superlu)
    * [superlu-dist@9.1.0](https://packages.spack.io/package.html?name=superlu-dist)
    * [swig@4.1.1](https://packages.spack.io/package.html?name=swig)
    * [trilinos@16.0.0](https://packages.spack.io/package.html?name=trilinos)
    * [umpire@2025.03.0](https://packages.spack.io/package.html?name=umpire)
    * [zlib-ng@2.2.4](https://packages.spack.io/package.html?name=zlib-ng)

=== "24.11"
    In version 24.11, the common set of packages in both uenvs is:

    * [arpack-ng](https://packages.spack.io/package.html?name=arpack-ng)
    * [aws-ofi-nccl](https://packages.spack.io/package.html?name=aws-ofi-nccl)
    * [blaspp](https://packages.spack.io/package.html?name=blaspp)
    * [blt](https://packages.spack.io/package.html?name=blt)
    * [boost](https://packages.spack.io/package.html?name=boost)
    * [camp](https://packages.spack.io/package.html?name=camp)
    * [cmake](https://packages.spack.io/package.html?name=cmake)
    * [cuda](https://packages.spack.io/package.html?name=cuda)
    * [dla-future-fortran](https://packages.spack.io/package.html?name=dla-future-fortran)
    * [dla-future](https://packages.spack.io/package.html?name=dla-future)
    * [eigen](https://packages.spack.io/package.html?name=eigen)
    * [fftw](https://packages.spack.io/package.html?name=fftw)
    * [fmt](https://packages.spack.io/package.html?name=fmt)
    * [gsl](https://packages.spack.io/package.html?name=gsl)
    * [hdf5](https://packages.spack.io/package.html?name=hdf5)
    * [hwloc](https://packages.spack.io/package.html?name=hwloc)
    * [kokkos-kernels](https://packages.spack.io/package.html?name=kokkos-kernels)
    * [kokkos-tools](https://packages.spack.io/package.html?name=kokkos-tools)
    * [kokkos](https://packages.spack.io/package.html?name=kokkos)
    * [lapackpp](https://packages.spack.io/package.html?name=lapackpp)
    * [libtree](https://packages.spack.io/package.html?name=libtree)
    * [lua](https://packages.spack.io/package.html?name=lua)
    * [lz4](https://packages.spack.io/package.html?name=lz4)
    * [meson](https://packages.spack.io/package.html?name=meson)
    * [metis](https://packages.spack.io/package.html?name=metis)
    * [mimalloc](https://packages.spack.io/package.html?name=mimalloc)
    * [mumps](https://packages.spack.io/package.html?name=mumps)
    * [nccl-tests](https://packages.spack.io/package.html?name=nccl-tests)
    * [nccl](https://packages.spack.io/package.html?name=nccl)
    * [nco](https://packages.spack.io/package.html?name=nco)
    * [netcdf-c](https://packages.spack.io/package.html?name=netcdf-c)
    * [netlib-scalapack](https://packages.spack.io/package.html?name=netlib-scalapack)
    * [ninja](https://packages.spack.io/package.html?name=ninja)
    * [openblas](https://packages.spack.io/package.html?name=openblas)
    * [osu-micro-benchmarks](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
    * [p4est](https://packages.spack.io/package.html?name=p4est)
    * [papi](https://packages.spack.io/package.html?name=papi)
    * [parmetis](https://packages.spack.io/package.html?name=parmetis)
    * [petsc](https://packages.spack.io/package.html?name=petsc)
    * [pika](https://packages.spack.io/package.html?name=pika)
    * [python](https://packages.spack.io/package.html?name=python)
    * [slepc](https://packages.spack.io/package.html?name=slepc)
    * [spdlog](https://packages.spack.io/package.html?name=spdlog)
    * [stdexec](https://packages.spack.io/package.html?name=stdexec)
    * [suite-sparse](https://packages.spack.io/package.html?name=suite-sparse)
    * [superlu-dist](https://packages.spack.io/package.html?name=superlu-dist)
    * [superlu](https://packages.spack.io/package.html?name=superlu)
    * [swig](https://packages.spack.io/package.html?name=swig)
    * [trilinos](https://packages.spack.io/package.html?name=trilinos)
    * [umpire](https://packages.spack.io/package.html?name=umpire)
    * [whip](https://packages.spack.io/package.html?name=whip)
    * [zlib-ng](https://packages.spack.io/package.html?name=zlib-ng)

## How to use

Using the `linalg` and `linalg-complex` uenvs is similar to `prgenv-gnu`.
Like `prgenv-gnu`, the `linalg` and `linalg-complex` uenvs provide `default` and `modules` views.
Please see [the `prgenv-gnu` documentation][ref-uenv-prgenv-gnu-how-to-use] for details on different ways of accessing the packages available in the uenv.
You can for example load the `modules` view to see the exact versions of the packages available in the uenv.
