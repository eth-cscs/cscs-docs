[](){#ref-uenv-prgenv-gnu-openmpi}
# prgenv-gnu-openmpi

The `prgenv-gnu-openmpi` uenv is otherwise similar to [`prgenv-gnu`][ref-uenv-prgenv-gnu] except it provides OpenMPI instead of Cray MPICH.

!!! warning "OpenMPI is not officially supported on CSCS systems"
    Cray MPICH is the preferred, and officially supported, MPI implementation on CSCS systems.
    OpenMPI is provided on a best effort basis.
    While most applications should work correctly with OpenMPI, there may be missing features, broken functionality, or bad performance compared to Cray MPICH.
    Issues are best reported upstream, but CSCS is happy to help facilitate and coordinate issue reporting if you [get in touch][ref-get-in-touch].
    
Use of the uenv is similar to [`prgenv-gnu`][ref-uenv-prgenv-gnu].
See the [OpenMPI documentation][ref-communication-openmpi] for important information on configuring OpenMPI to take advantage of the Slingshot network.
    
### Versions

=== "25.12"
    25.12 is the first release of the `prgenv-gnu-openmpi` uenv.

    ??? info "Packages exposed by the `default` and `modules` views"
        * [aws-ofi-nccl@1.17.1](https://packages.spack.io/package.html?name=aws-ofi-nccl)
        * [boost@1.88.0](https://packages.spack.io/package.html?name=boost)
        * [cmake@3.31.9](https://packages.spack.io/package.html?name=cmake)
        * [cuda@12.9.1](https://packages.spack.io/package.html?name=cuda)
        * [fftw@3.3.10](https://packages.spack.io/package.html?name=fftw)
        * [fmt@12.1.0](https://packages.spack.io/package.html?name=fmt)
        * [gcc@14.3.0](https://packages.spack.io/package.html?name=gcc)
        * [gmp@6.3.0](https://packages.spack.io/package.html?name=gmp)
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
        * [nccl@2.28.9-1](https://packages.spack.io/package.html?name=nccl)
        * [nccl-tests@2.17.6](https://packages.spack.io/package.html?name=nccl-tests)
        * [netcdf-c@4.9.3](https://packages.spack.io/package.html?name=netcdf-c)
        * [netcdf-cxx@4.2](https://packages.spack.io/package.html?name=netcdf-cxx)
        * [netcdf-cxx4@4.3.1](https://packages.spack.io/package.html?name=netcdf-cxx4)
        * [netcdf-fortran@4.6.2](https://packages.spack.io/package.html?name=netcdf-fortran)
        * [netlib-scalapack@2.2.2](https://packages.spack.io/package.html?name=netlib-scalapack)
        * [ninja@1.13.0](https://packages.spack.io/package.html?name=ninja)
        * [openblas@0.3.30](https://packages.spack.io/package.html?name=openblas)
        * [openmpi@5.0.9](https://packages.spack.io/package.html?name=openmpi)
        * [osu-micro-benchmarks@7.5.1](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
        * [papi@7.2.0](https://packages.spack.io/package.html?name=papi)
        * [python@3.14.0](https://packages.spack.io/package.html?name=python)
        * [squashfs@4.6.1](https://packages.spack.io/package.html?name=squashfs)
        * [superlu@7.0.1](https://packages.spack.io/package.html?name=superlu)
        * [xcb-util-cursor@0.1.5](https://packages.spack.io/package.html?name=xcb-util-cursor)
        * [xpmem@2.8.2](https://packages.spack.io/package.html?name=xpmem)
        * [zlib-ng@2.2.4](https://packages.spack.io/package.html?name=zlib-ng)
