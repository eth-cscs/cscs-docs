[](){#ref-software-cesm}
# CESM

!!! warning ""
    CESM is [user software][ref-support-user-apps] on Alps.
    This guide is provided based on our experiences helping users -- however we can't provide the same level of support as we do for [supported software][ref-support-apps].
    See the [main applications page][ref-software] for more information.

The [Community Earth System Model (CESM)](https://www.cesm.ucar.edu/) is a fully coupled global Earth system model.

This guide demonstrates a uenv-based workflow that CSCS has developed with CESM users on [Eiger][ref-cluster-eiger].
Specifically, the workflow is for users of CESM version 3, which is currently in beta release, on multi-core x86 CPUs.

The uenv is named `esmf` because it provides all of the dependencies of CESM, of which the [Earth System Modeling Framework (ESMF)](https://earthsystemmodeling.org/) is the main dependency.

[](){#ref-uenv-cesm-versioning}
## Versioning

The naming scheme is `esmf/<version>`, where `<version>` has the `YY.M[M]` format, for example February 2026 is `26.2`.

### Versions

=== "26.2"

    The 26.2 version provides two views for building CESM with and without MPI.

    Both views are based on the following base:

    - gcc@14.3.0
    - python@3.14.0

    and standard build tools like:

    - cmake
    - subversion
    - gmake

    and the following version of ESMF and ParallelIO:

    - **esmf@8.8.0**
    - **parallelio@2.6.6**

    ???  "`esmf` view"

        The following core dependencies are provided:

        - hdf5@1.14.6
        - netcdf-c@4.9.3
        - netcdf-cxx@4.2
        - netcdf-fortran@4.6.2
        - openblas@0.3.30
        - parallel-netcdf@1.14.1

        They are compiled with MPI support, based on the following communication libraries:

        - cray-mpich@8.1.32
        - libfabric@2.3.1

    ??? "`esmf-serial` view"

        The following core dependencies are provided:

        - hdf5@1.14.6
        - netcdf-c@4.9.3
        - netcdf-cxx@4.2
        - netcdf-fortran@4.6.2
        - openblas@0.3.30

        No MPI is included in this view, and `parallelio` and `esmf` do not link to `parallel-netcdf`, which also is not provided by the view.


[](){#ref-uenv-cesm-gnu-how-to-use}
## How to use

On Eiger, search for `esmf` images:

```console
$ uenv image find esmf
uenv          arch  system  id                size(MB)  date
esmf/26.2:v1  zen2  eiger   02f1427403db1adb     679    2026-03-02
$ uenv image pull esmf/26.2:v1
```

!!! note
    The uenv must be loaded when configuring and building CESM use cases, and also when running those use cases.

Start the uenv with either the `esmf` view or `esmf-serial` view.
If this is your first time you can verify that key environment variables have been set by grepping for `NETCDF` and `ESMF` in the output of `printenv`:

!!! example "starting the esmf uenv with the `esmf` view for distributed simulations"
    ```console
    $ uenv start --view=esmf esmf/26.2:v1

    $ printenv | grep -e NETCDF -e ESMF
    ESMF_LIBDIR=/user-environment/env/esmf/lib
    ESMFMKFILE=/user-environment/env/esmf/lib/esmf.mk
    NETCDF_PATH=/user-environment/env/esmf
    PNETCDF_PATH=/user-environment/env/esmf
    ```

The uenv provides two views for parallel and serial builds, `esmf` and `esmf-serial` respectively.
The views set environment variables that are used to configure CESM builds:

- `MACHINE_PATH`: location of the machine and batch XML configuration files, and the cmake configuration, needed to build CESM.
- `ESMF_LIBDIR`: path where the ESMF libraries are installed, used by CESM build configuration.
- `NETCDF_PATH`: path where netcdf is installed, used by CESM build configuration.
- `PNETCDF_PATH`: path where parallel-netcdf is installed, used by CESM build configuration.
    - not set by the `esmf-serial` view, which does not provide parallel-netcdf.

!!! example "building CESM `cesm3_0_beta_7`"

    Build a beta release of CESM 3.0 with MPI support, which uses the `esmf` view.

    ```console
    # start the environment
    $ uenv start --view=esmf esmf/26.2:v1

    $ CESMROOT=$PWD/CESM

    # download CESM and check out the desired version
    $ cesm_version='cesm3_0_beta07'
    $ git clone https://github.com/ESCOMP/CESM.git $CESMROOT
    $ cd $CESMROOT;
    $ git checkout ${cesm_version}

    # configure dependencies
    $ ./bin/git-fleximod update

    # set up the machine file
    # use the MACHINE_PATH variable set by the view
    $ cp -rv $MACHINE_PATH $CESMROOT/ccs_config/machines/
    ```

    The last step copied machine configuration files for eiger from the uenv into the CESM source code.

    You will have to update the `config_machines.xml` file with relevant directories, and also check the `config_batch.xml` file.
    The `gnu_eiger.cmake` should not need modification - if it does, contact CSCS support (or Ben Cumming on CSCS user slack) to see whether we can update the configuration in future releases of the ESMF uenv image.

    Now it is time to configure the use case (modify the `case`, `compset` and `res` arguments for your use case):

    ```console
    $ cd $CESMROOT/cime/scripts
    $ ./create_newcase --case test_cscs \
                       --compset FHIST \
                       --res f09_g17 \
                       --machine eiger \
                       --run-unsupported \
                       --compiler gnu
    $ cd test_cscs
    $ ./case.setup
    $ ./case.build
    ```

    !!! note
        This workflow works for the `FHIST` compset - it will need to be changed to support your use case.

!!! warning
    The uenv must be loaded when SLURM jobs are launched, which requires that the correct flags are passed to srun.

    The flags to pass to srun are `srun --uenv=esmf/26.2:v1 --view=esmf` (or `--view=esmf-serial`).

    The machine files provided by the uenv should set these fields correctly, however it is worth checking that the `env_mach_specific.xml` file generated by `create_newcase` in your case directory matches the uenv and view that you used to configure and compile CESM.
