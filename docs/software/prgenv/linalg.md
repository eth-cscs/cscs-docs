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
| 24.11 | gh200, zen2 | daint, eiger |

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
