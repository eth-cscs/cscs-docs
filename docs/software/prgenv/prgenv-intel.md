[](){#ref-uenv-prgenv-intel}
# prgenv-intel

The `prgenv-intel` uenv provides the Intel OneAPI compiler, cray-mpich, python and some I/O libraries.
It can be used for applications that require the Intel Fortran compiler.

!!! note
    The `prgenv-intel` uenv does not have as many packages as the full [`prgenv-gnu`][ref-uenv-prgenv-gnu] environment.

    Try using the `prgenv-gnu` uenv first, because it is better tested, better supported, and has more software packages available

!!! note "only on [zen2][ref-alps-zen2-node] nodes"
    Only available on [Eiger][ref-cluster-eiger], and provides fewer general libraries than the full GNU environment.

[](){#ref-uenv-prgenv-intel-versioning}
## Versioning

The naming scheme is `prgenv-intel/<version>`, where `<version>` has the `YYYY.M[M]` format that matches the version of the [Intel OneAPI compilers](https://packages.spack.io/package.html?name=intel-oneapi-compilers) in the uenv.

The release schedule is not fixed, with new versions will be released when there is a compelling reason to update.

We are constrained by the pre-compiled versions of cray-mpich provided by HPE - they need to release cray-mpich built with the target compiler.
When HPE release cray-mpich as open source, we will be able to provide more options, because we will be able to rebuild it with any compiler.

| version            | node types | system    | released  |
|--------------------|------------|-----------|-----------|
| 2022.1             | zen2       | eiger     | 2026-04   |


### Deprecation policy

There is no fixed deprecation policy.
We will continue to provide each version as long as practically possible, however system upgrades might force us to provide updated versions, and users to recompile their software.

### Versions

=== "2022.1"

    ??? info "all packages exposed via the `default` and `modules` views in `v1`"
        * [cmake@3.31.11](https://packages.spack.io/package.html?name=cmake)
        * [cray-mpich/8.1.32](https://packages.spack.io/package.html?name=cray-mpich)
        * [fftw/3.3.10](https://packages.spack.io/package.html?name=fftw)
        * [gcc/14.3.0](https://packages.spack.io/package.html?name=gcc)
        * [gsl/2.8](https://packages.spack.io/package.html?name=gsl)
        * [hdf5/1.14.6](https://packages.spack.io/package.html?name=hdf5)
        * [intel-oneapi-compilers/2022.1.0](https://packages.spack.io/package.html?name=intel-oneapi-compilers)
        * [libfabric/1.22.0](https://packages.spack.io/package.html?name=libfabric)
        * [netcdf-c/4.9.3](https://packages.spack.io/package.html?name=netcdf-c)
        * [netcdf-cxx/4.2](https://packages.spack.io/package.html?name=netcdf-cxx)
        * [netcdf-fortran/4.6.2](https://packages.spack.io/package.html?name=netcdf-fortran)
        * [osu-micro-benchmarks/7.5.2](https://packages.spack.io/package.html?name=osu-micro-benchmarks)
        * [python/3.14.3](https://packages.spack.io/package.html?name=python)
        * [squashfs/4.6.1](https://packages.spack.io/package.html?name=squashfs)

[](){#ref-uenv-prgenv-intel-how-to-use}
## How to use

The environment provides a set of tools and libraries based on the GNU compiler toolchain for building scientific applications.

There are three ways to access the software provided by prgenv-intel, once it has been started.

=== "the `oneapi` view"

    The simplest way to get started is to use the `oneapi` file system view, which automatically loads all of the packages when the uenv is started.

    !!! example "test mpi compilers and python provided by prgenv-intel/2022.1"
        ```console
        # start using the oneapi view
        $ uenv start --view=oneapi prgenv-intel/2022.1

        # the python executable provided by the uenv is the default, and is a recent version
        $ which python
        /user-environment/env/oneapi/bin/python
        $ python --version 
        Python 3.14.3

        # the mpi compiler wrappers are also available
        $ which mpicc
        /user-environment/env/oneapi/bin/mpicc
        $ mpicc --version
        Intel(R) oneAPI DPC++/C++ Compiler 2022.1.0 (2022.1.0.20220316)
        Target: x86_64-unknown-linux-gnu
        Thread model: posix
        InstalledDir: /user-environment/linux-zen2/intel-oneapi-compilers-2022.1.0-conxt3vqgxsvxr22tzakwekhewt7loso/compiler/2022.1.0/linux/bin-llvm
        Configuration file: /user-environment/linux-zen2/intel-oneapi-compilers-2022.1.0-conxt3vqgxsvxr22tzakwekhewt7loso/compiler/2022.1.0/linux/bin/icx.cfg
        ```

=== "modules"

    The uenv provides modules for all of the software packages, which can be made available by using the `modules` view in 
    No modules are loaded when a uenv starts, and have to be loaded individually using `module load`.

    !!! example "starting prgenv-intel and listing the provided modules"
        ```console
        $ uenv start prgenv-intel/2022.1:v1 --view=modules
        $ module avail
            ------------------------ /user-environment/modules ------------------------
                   cmake/3.31.11                      libfabric/1.22.0
                   cray-mpich/8.1.32                  netcdf-c/4.9.3
                   fftw/3.3.10                        netcdf-cxx/4.2
                   gcc/14.3.0                         netcdf-fortran/4.6.2
                   gsl/2.8                            osu-micro-benchmarks/7.5.2
                   hdf5/1.14.6                        python/3.14.3
                   intel-oneapi-compilers/2022.1.0    squashfs/4.6.1
        ```

=== "Spack"

    The gnu programming environment is a very good base for building software with Spack, because it provides compilers, MPI, Python and common packages like hdf5.

    [Check out the guide for using Spack with uenv][ref-build-uenv-spack].

