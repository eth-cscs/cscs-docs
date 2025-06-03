[](){#ref-uenv-build}
# Building uenv

## uenv build service

CSCS provides a build service for uenv that takes as its input a uenv recipe, and builds the uenv using the same pipeline used to build the officially supported uenv.

The command takes two arguments:

```
uenv build <recipe> <label>
```

* `recipe`: the path to the recipe
    * A uenv recipe is a description of the software to build in the uenv.
      See the [stackinator documentation](https://eth-cscs.github.io/stackinator/recipes/) for more information.
* `label`: the label to attach, of the form `name/version@system%uarch` where:
    * `name` is the name, e.g. `prgenv-gnu`, `gromacs`, `vistools`.
    * `version` is a version string, e.g. `24.11`, `v1.2`, `2025-rc2`
    * `system` is the CSCS cluster to build on (e.g. `daint`, `santis`, `clariden`, `eiger`)
    * `uarch` is the [micro-architecture][ref-uenv-label-uarch].

!!! example "Building a uenv"
    The image will be built on `daint` for the `gh200` node type.
    ```bash
    uenv build $SCRATCH/recipes/myapp myapp/v3@daint%gh200
    ```

    The output of the above command will print a url that links to a status page, for you to follow the progress of the build.
    After a successful build, the uenv can be pulled using an address from the status page:

    ```bash
    uenv image pull service::myapp/v3:1669479716
    ```

    Note that the image is given a unique numeric tag, provided on the status page for the build.

!!! info
    To use an existing uenv recipe as the starting point for a custom recipe, `uenv start` the uenv and take the contents of the `meta/recipe` path in the mounted image (this is the recipe that was used to build the uenv).

All uenv built by `uenv build` are pushed into the `service` namespace, where they **can be accessed by all users logged in to CSCS**.
This makes it easy to share your uenv with other users, by giving them the name, version and tag of the image.

!!! danger
    **If, for whatever reason, your uenv can not be made publicly available, do not use the build service.**

!!! example "Search user-built uenv"
    To view all of the uenv on daint that have been built by the service:
    ```
    uenv image find service::@daint
    ```

## Building with Stackinator

CSCS develops and maintains the [Stackinator](https://eth-cscs.github.io/stackinator) tool that is used to configure and build uenv.

!!! note
    The tool is currently maintained for internal use, and is used by automated pipelines, including the one used by the `uenv build` command.
    As such, CSCS provide limited support for the tool.
