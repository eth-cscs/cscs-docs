[](){#ref-uenv-deploy}
# Deploying uenv

[](){#ref-uenv-deploy-versions}
## Versioning and labeling

Uenv images have a **label** of the following form:

```
name/version:tag@system%uarch
```

for example:

```
prgenv-gnu/24.11:v2@todi%gh200
```

### uenv name

The name of the uenv. In this case `prgenv-gnu`.

### uenv version

The version of the uenv.

The format of `version` depends on the specific uenv.
Often they use the `yy.mm` format, though they may also use the version of the software being packaged.
For example the [`namd/3.0`][ref-uenv-namd] uenv packages version 3.0 of the popular [NAMD](https://www.ks.uiuc.edu/Research/namd/) simulation tool.

### uenv tag

Used to differentiate between _releases_ of a versioned uenv.
Some examples of tags include:

* `rc1`, `rc2`: release candidates;
* `v1`: a first release typically made after some release candidates;
* `v2`: a second release, that fixes issues in `v1`

### uenv system

The name of the [Alps cluster][ref-alps-clusters] for which the uenv was built.

[](){#ref-uenv-label-uarch}
### uenv uarch

The node type (microarchitecture) that the uenv is built for.

| uarch                      | CPU | GPU | comment |
| ----- | --- | --- | ------ |
|[gh200][ref-alps-gh200-node]| 4 72-core NVIDIA Grace (`aarch64`) | 4 NVIDIA H100 GPUs | |
|[zen2][ref-alps-zen2-node]  | 2 64-core AMD Rome (`zen2`)        | - | used in Eiger|
|[a100][ref-alps-a100-node]  | 1 64-core AMD Milan (`zen3`)       | 4 NVIDIA A100 GPUs | |
|[mi200][ref-alps-mi200-node]| 1 64-core AMD Milan (`zen3`)       | 4 AMD Mi250x GPUs  | |
|[mi300][ref-alps-mi300-node]| 4 24-core AMD Genoa (`zen4`)       | 4 AMD Mi300 GPUs  | |
| zen3                       | 2 64-core AMD Milan (`zen3`)       | - | only in MCH system |

## Registries

The following naming scheme is employed in the OCI container registry for uenv images:

```text
namespace/system/uarch/name/version:tag
```

Where the fields `system`, `uarch`, `name`, `version` and `tag` are defined above.

The `namespace` is one of:

* `build`: where the CI/CD pipeline pushes uenv images.
* `deploy`: where uenv images are copied by CSCS staff when they are officially provided to users.
* `service`: where the uenv [build service][ref-uenv-build] pushes images.

!!! info "JFrog uenv registry"
    The OCI container registry used to host uenv is on JFrog, and can be browsed at [jfrog.svc.cscs.ch/artifactory/uenv/](https://jfrog.svc.cscs.ch/artifactory/uenv/) (you may have to log in with CSCS credentials from the a VPN/CSCS network).

    The address of individual uenv images is of the form
    ```
    https://jfrog.svc.cscs.ch/uenv/namespace/system/uarch/name/version:tag
    ```
    For example:
    ```
    https://jfrog.svc.cscs.ch/uenv/deploy/eiger/zen2/cp2k:2024.1
    ```

## uenv recipes and definitions

The uenv recipes are maintained in a public GitHub repository: [eth-cscs/alps-uenv](https://github.com/eth-cscs/alps-uenv).

The recipes for each uenv version are stored in the `recipes` subdirectory. 
Specific uenv recipes are stored in `recipes/name/version/uarch/`.

The `cluster` is specified when building and deploying the uenv, while the `tag` is specified when deploying the uenv.

## uenv deployment

### Deployment rules

A recipe can be built for deployment on different clusters, and for multiple targets.
For example:

* A multicore recipe could be built for `zen2` or `zen3` nodes
* A GROMACS recipe that is tuned for A100 GPUs can be built and deployed on any vCluster supporting the A100 architecture

However, it is not desirable to build every recipe on every possible target system.
For example:

* An ICON development environment would only be deployed on the weather and climate platform
* A GROMACS recipe would not be deployed on the weather and climate platform
* Development builds only need to run on test and staging clusters

A YAML file `config.yaml` is maintained in the [github.com/eth-cscs/alps-uenv](https://github.com/eth-cscs/alps-uenv/blob/main/config.yaml) repository that maps
recipes to deployed versions on microarchitectures.

### Permissions

!!! note "For CSCS staff"
    This information applies only to CSCS staff.

Deployment and deletion of uenv requires elevated permissions.
Before you can modify the uenv registry, you need to set up credentials.

* Your CSCS username needs to be added to the `uenv-admin` group on JFrog, and
* you need to generate a new token for the [JFrog](https://jfrog.svc.cscs.ch) registry.

Once you have the token, you can save it in a file.

!!! danger

    Save the token file somewhere safe, for example in `~/.ssh/jfrog-token`.


The token file can be passed to the `uenv` command line tool using the `--token` option.

```bash
uenv image copy --token=${HOME}/.ssh/jfrog-token <SOURCE> <DESTINATION>
```

### Deploying a uenv

!!! note "For CSCS staff"
    This information applies only to CSCS staff.

The CI/CD pipeline for [eth-cscs/alps-uenv](https://github.com/eth-cscs/alps-uenv) pushes images to the JFrog uenv registry in the `build::` namespace.

Deploying a uenv copies the uenv image from the `build::` namespace to the `deploy::` namespace. The Squashfs image itself is not copied;
a new tag for the uenv is created in the `deploy::` namespace.

The deployment is performed using the `uenv` command line tool, as demonstrated below:

```bash
uenv image copy build::<SOURCE> deploy::<DESTINATION> # (1)!
```

1. `<DESTINATION>` must be fully qualified.

!!! example "Deploy using image ID"
    
    Deploy a uenv from `build::` using the ID of the image:

    ```bash
    uenv image copy build::d2afc254383cef20 deploy::prgenv-nvfortran/24.11:v1@daint%gh200
    ```

!!! example "Deploy using qualified name"

    Deploy a uenv using the qualified name:

    ```
    uenv image copy build::quantumespresso/v7.4:1653244229 deploy::quantumespresso/v7.4:v1@daint%gh200
    ```

    !!! note 

        The build image uses the CI/CD pipeline ID as the tag. You will need to choose an appropriate tag.

!!! example "Deploy a uenv from one cluster to another"

    You can also deploy a uenv from one vCluster to another.
    For example, if the `uenv` for `prgenv-gnu` has been deployed on `daint`,
    to make it available on `santis`, you can use the following command:

    ```bash
    uenv image copy deploy::prgenv-gnu/24.11:v1@daint%gh200 deploy::prgenv-gny/24.11@santis%gh200
    ```

[](){#ref-uenv-remove}
### Removing a uenv

To remove a uenv, you can use the `uenv` command line tool:

```bash
uenv image delete --token=${HOME}/.ssh/jfrog-token <NAMESPACE>::<IMAGE>
```

!!! danger

    Removing a uenv that has been deployed (i.e. is in the `deploy::` namespace) is potentially disruptive for users.
    Please see the [uenv life cycle][ref-uenv-lifecycle] guide for more information.

## Source code access

Some source artifacts are stored in JFrog, including:

* source code for software that can't be downloaded directly from the internet directly;
* and tar balls for custom software.

These artifacts are stored in a JFrog "generic repository" [uenv-sources].

Each software package has a sub-directory and all image paths are lower case (e.g. `uenv-sources/namd`).

By default, all packages in [uenv-sources]  are anonymous read access
to enable users to build uenv on vClusters without configuring access tokens.
However,

* access to some packages is restricted by applying access rules to the package path
* e.g. access to `uenv-sources/vasp` is restricted to members of the vasp6 group

Permissions to access restricted resources is set on a per-pipeline basis

* For example, only the `alps-uenv` pipeline has access to the VASP source code, while the [`uenv build`][ref-uenv-build] pipeline does not.

| Package | Access | Path | Notes | Contact |
|---------|--------|------|-------| ------- |
| `cray-mpich` | anonymous | `uenv-sources/cray-mpich` | `cray-mpich`, `cray-gtl`, `cray-pals`, `cray-mpi` | Simon Pintarelli, Benjamin Cumming|
| `namd` | `uenv-sources-csstaff` | `uenv-sources/namd` | NAMD requires an account to download the source code | Rocco Meli |
| `vasp` | `vasp6`, `cscs-uenv-admin` | `uenv-sources/vasp` | VASP requires a paid license to access source | Simon Frasch |
| `vmd` | `uenv-sources-csstaff` | `uenv-sources/vmd` | VMD requires an account to download the source code | Alberto Invernizzi |

[](){#ref-uenv-lifecycle}
## uenv life cycle

Scientific applications and tools have different release cycles (e.g. annual, quarterly or irregular), and the communities that use them have different expectations (e.g. ML users expect tools released in the last 3 months, while some scientific communities value support for old versions of software).
For this reason, there is not a universal release and deprecation schedule for supported applications and programming environments - how often to release, how long to provide support, and when to remove old versions is up to the maintainer of the uenv, based on their user's requirements and the overheads of maintaining old versions.

While the frequency of updates and deprecation policy is defined by the uenv maintainer, the following release cycle with tag names should be followed when possible:

- [optional] tag pre-releases with `:rc1`, `:rc2`, etc
    - uenv tagged as release candidates are intended for early testing only, and can be removed at any point.
- Tag `:v1` for the first official release.
- [optional] release updated versions of uenv with tags ()`:v2`, `:v3`, ...) with patches and fixes.
- Remove old versions according to a deprecation policy.

A uenv's release and support policy should be part of the uenv's documentation under the "Versioning" section, see [prgenv-gnu][ref-uenv-prgenv-gnu-versioning] for example.

The versioning section should provide the following information:

* the release schedule;
* the support, update and deprecation policy for the uenv;
* details about the currently deployed versions, changelogs and relevant information how to upgrade if appropriate.

!!! example "Example deprecation policy"
    A scientific application `sciapp` is released annually by the developers, and projects using the software on CSCS systems expect support for two years.

    * Release a new version annually and version with the year, for example `sciapp/2025` being the most recent version in 2025.
    * CSCS provides full support for the current release, and partial support for old releases:
        * `sciapp/2025`: provide updates and fixes with new tags, take feature requests, and respond to questions about usage and how to upgrade to this version.
        * `sciapp/2024`: only support the most recent tag and only create new tags to fix breaking changes.
        * `sciapp/2023`: provided "as is" for the first quarter of 2025 while users have the chance to upgrade.
    * If there is a major breaking change to the system that would require a large effort to continue providing last year's version, and would require users to also update their workflow, we might choose to encourage deprecate early and help users upgrade to the latest version.

Generally speaking, uenv are removed (deleted from the `deploy::` namespace) under the following circumstances:

- when they are no longer supported as per the deprecation policy of the uenv;
- when release candidates are superceded by a new release candidate or an official `:v1` release;
- when a new tag of a `name/version` is deployed to replace a "broken" uenv:
    - there might have been a critical issue affecting security, correctness or performance that means all users should update.
    - _do not_ remove uenv tags that continue to meet the needs of users (e.g. if a new tag was introduced to fix an issue that only affected specific users or use cases).

[uenv-sources]: https://jfrog.svc.cscs.ch/artifactory/uenv-sources/
