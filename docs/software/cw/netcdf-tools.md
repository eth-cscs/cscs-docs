[](){#ref-uenv-netcdf-tools}
# netcdf-tools

The `netcdf-tools` uenv provides a set of CLI tools and GUI tools frequently used in climate and weather workflows.

The release schedule is not fixed, with new releases when required.

| version            | node types        | system                                  | status |
|--------------------|-------------------|-----------------------------------------|--------|
| 2024               | zen2, gh200       | daint, eiger, santis, clariden          | **DEPRECATED** |
| 2025               | zen2, gh200       | daint, eiger, santis, clariden          | :white_check_mark: |

!!! warning
    If you are using the `netcdf-tools/2024` version, please upgrade to the `2025` version, because the `2024` version uses an old interface that won't load views correctly.


The packages exposed via the `default` and `modules` views in `2025:v1` are:

* [cdo@2.5.2](https://packages.spack.io/package.html?name=cdo)
* [cray-mpich@8.1.32](https://packages.spack.io/package.html?name=cray-mpich)
* [eccodes@2.41.0](https://packages.spack.io/package.html?name=eccodes)
* [ferret@7.6.0](https://packages.spack.io/package.html?name=ferret)
    * Only provided in Eiger because its build configuration hard-codes x86 instructions.
* [gcc@14.3.0](https://packages.spack.io/package.html?name=gcc)
* [gdal@3.11.0](https://packages.spack.io/package.html?name=gdal)
* [geos@3.13.1](https://packages.spack.io/package.html?name=geos)
* [hdf5@1.14.6](https://packages.spack.io/package.html?name=hdf5)
* [nco@5.3.3](https://packages.spack.io/package.html?name=nco)
* [ncview@2.1.9](https://packages.spack.io/package.html?name=ncview)
* [netcdf-c@4.9.2](https://packages.spack.io/package.html?name=netcdf-c)
* [netcdf-cxx4@4.3.1](https://packages.spack.io/package.html?name=netcdf-cxx4)
* [netcdf-fortran@4.6.1](https://packages.spack.io/package.html?name=netcdf-fortran)
* [python@3.13.5](https://packages.spack.io/package.html?name=python)
* [udunits@2.2.28](https://packages.spack.io/package.html?name=udunits)

## How to use

Use the different views to access the software

=== "the `netcdf` view"

    The simplest way to get started is to use the `netcdf` file system view, which automatically loads all of the packages when the uenv is started.

    !!! example "test mpi compilers and python provided by netcdf-tools/2025"
        ```console
        # start using the netcdf view
        $ uenv start --view=netcdf netcdf-tools/2025:v1

        # the software is available
        $ which cdo
        /user-environment/env/netcdf/bin/cdo
        $ which gdal
        /user-environment/env/netcdf/bin/gdal
        $ gdal --version
        GDAL 3.11.0 "Eganville", released 2025/05/06
        ```

    !!! example "run applications directly using uenv run"
        ```console
        # run ncview without having to start a uenv session
        $ uenv run netcdf-tools/2025:v1 --view=netcdf -- ncview

        # create an alias that launches tools in netcdf-tools (add it to bashrc)
        $ alias ncx='uenv run --view=netcdf netcdf-tools/2025:v1 --'
        # then run commands:
        $ ncx ncview
        $ ncx cdo
        ```

=== "modules"

    The uenv provides modules for all of the software packages, which can be made available by using the `modules` view in 
    No modules are loaded when a uenv starts, and have to be loaded individually using `module load`.

    !!! example "starting netcdf-tools and using the provided modules"
        ```console
        $ uenv start netcdf-tools/2025:v1 --view=modules
        $ module avail
        ---------------------------- /user-environment/modules -----------------------------
           cdo/2.5.2            gdal/3.11.0         ncview/2.1.9            squashfs/4.6.1
           cray-mpich/8.1.32    geos/3.13.1         netcdf-c/4.9.2          udunits/2.2.28
           eccodes/2.41.0       hdf5/1.14.6         netcdf-cxx4/4.3.1
           ferret/7.6.0         libfabric/1.22.0    netcdf-fortran/4.6.1
           gcc/14.3.0           nco/5.3.3           python/3.13.5
        $ module load gdal
        $ gdal --version
        GDAL 3.11.0 "Eganville", released 2025/05/06
        ```
