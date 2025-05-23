# uenv Documentation

## Versioning and Labeling

The following naming scheme is employed in the OCI container artifactory for uenv images:

```text
/cluster/uarch/name/version:release
```

The different fields are described in the following table:

| label | meaning |
|-------|---------|
| `uarch` | node microarchitecture |
| `cluster` | name of the vCluster |
| `name` | name of the uenv |
| `version` | version of the uenv |
| `release` | incremental tag |

??? example "uenv names"

    The latest release for an uenv providing GROMACS 2023 for a multicore architcture ([Eiger][ref-cluster-eiger])
    would be the following:

    ```text
    /eiger/zen2/gromacs/2023:latest
    ```

By default, if no release tag is provided, `latest` is used.

### uenv Recipes and Definitions

The uenv recipes are maintained in a public GitHub repository: [eth-cscs/alps-uenv](https://github.com/eth-cscs/alps-uenv).

The recipes for each uenv version are stored in the `recipes` subdirectory. 
Specific uenv recipes are stored in `recipes/name/version/uarch/`.

The `cluster` is specified when building and deploying the uenv, while the `release` is specified when deploying the uenv.

## uenv Deployment

### Deployment Rules

A recipe can be built for deployment on different vClusters, and for multiple targets.

??? example
    
    * A multicore recipe could be built for `zen2` or `zen3` nodes
    * A GROMACS recipe that is tuned for A100 GPUs can be built and deployed on any vCluster supporting the A100 architecture

However, it is not desirable to build every recipe on every possible target system.

??? example 

    * An ICON development environment would only be deployed on the weather and climate platform
    * A GROMACS recipe would not be deployed on the weather and climate platrofm
    * Development builds only need to run on test and staging clusters

A YAML file `config.yaml` is maintained in the [eth-cscs/alps-uenv](https://github.com/eth-cscs/alps-uenv) repository that maps
recipes to deployed versions on mucroarchitectures.

### Permissions

Deployment/deletion requires elevated permissions.
Before you can modify the uenv registry, you need to set up credentials.

* Your CSCS username needs to be added to the `uenv-admin` group on JFrog, and
* you need to generate a new token for the [JFrog](https://jfrog.svc.cscs.ch) registry.

Once you have the token, you can save it in a file.

!!! danger

    Save the token file somwhere safe, for example in `~/.ssh/jfrog-token`.


The token file can be passed to the `uenv` command line tool using the `--token` option.

```bash
uenv image copy --token=${HOME}/.ssh/jfrog-token <SOURCE> <DESTINATION>
```

### Deploying an uenv

The CI/CD pipeline for [eth-cscs/alps-uenv](https://github.com/eth-cscs/alps-uenv) pushes images to the JFrog uenv registry in the `build::` namespace.

Deploying a uenv copies the uenv imagre from the `build::` namespace to the `deploy::` namespace. The Squashfs image itself is not copied;
a new tag for the uenv is created in the `deploy::` namespace.

The deployment is performed using the `uenv` command line tool, as demonstrated below:

```bash
uenv image copy build::<SOURCE> deploy::<DESTINATION> # (1)!
```

1. `<DESTINATION>` must be fully qualified.

!!! example "Deploy Using Image ID"
    
    Deploy an uenv from `build::` using the ID of the image:

    ```bash
    uenv image copy build::d2afc254383cef20 deploy::prgenv-nvfortran/24.11:v1
    ```

!!! example "Deploy Using Qualified Name"

    Deploy an uenv using the qualified name:

    ```
    uenv image copy build::quantumespresso/v7.4:1653244229 deploy::quantumespresso/v7.4:v1@daint%gh200
    ```

    !!! note 

        The build image uses the CI/CD pipeline ID as the tag. You will need to choose an appropriate tag.

!!! example "Deploy an uenv from One vCluster to Another"

    You can also deploy an uenv from one vCluster to another.
    For example, if the `uenv` for `prgenv-gnu` has been deployed on `daint`,
    to make it available on `santis`, you can use the following command:

    ```bash
    uenv image copy deploy::prgenv-gnu/24.11:v1@daint%gh200 deploy::prgenv-gny/24.11@santis%gh200
    ```

### Removing an uenv

To remove an uenv, you can use the `uenv` command line tool:

```bash
uenv image remove --token=${HOME}/.ssh/jfrog-token deploy::<IMAGE>
```

!!! warning 

    Removing an uenv is disruptive. Please have a look at out [uenv removal policy][ref-uenv-removal] for more information.

## uenv Soruces

Some source artifacts are stored in JFrog:

* sorce code for software that can't be downloaded directly from the internet directly,
* tar balls for custom software.

These artifacts are stored in a JFrog "generic repository" [uenv-sources].

Each software package has a sub-directory and all image paths are lower case (e.g. `uenv-resources/namd`).

By default, all packages in [uenv-sources]  are anonymous read access
to enable users to build uenv on vClusters without configuring access tokens.
However,

* access to some packages is restricted by applying access rules to the package path
* e.g. access to uenv-sources/vasp is restricted to members of the vasp6 group

A CI/CD job has access to all of [iuenv-sources] resources.

| Package | Access | Path | Notes | Contact |
|---------|--------|------|-------| ------- |
| `cray-mpich` | anonymous | `uenv-sources/cray-mpich` | `cray-mpich`, `cray-gtl`, `cray-pals`, `cray-mpi` | Simon Pintarelli, Benjamin Comming|
| `namd` | `uenv-sources-csstaff` | `uenv-sources/namd` | NAMD requires an account to download the source code | Rocco Meli |
| `vasp` | `vasp6`, `cscs-uenv-admin` | `uenv-sources/vasp` | VASP requires a paid license to access source | Simon Frasch |
| `vmd` | `uenv-sources-csstaff` | `uenv-sources/vmd` | VMD requires an account to download the source code | Alberto Invernizzi |

[uenv-sources]: https://jfrog.svc.cscs.ch/artifactory/uenv-sources/
