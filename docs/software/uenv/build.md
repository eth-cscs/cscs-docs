[](){#ref-uenv-build}
# Building uenv

CSCS provides a build service for uenv that takes as its input a uenv recipe, and builds the uenv using the same pipeline used to build the officially supported uenv.

The command takes two arguments:

* `recipe`: the path to the recipe
    * A uenv recipe is a description of the software to build in the uenv.
      See the [stackinator documentation](https://eth-cscs.github.io/stackinator/recipes/) for more information.
* `label`: the label to attach, of the form `name/version@system%uarch` where:
    * `name` is the name, e.g. `prgenv-gnu`, `gromacs`, `vistools`.
    * `version` is a version string, e.g. `24.11`, `v1.2`, `2025-rc2`
    * `system` is the CSCS cluster to build on (e.g. `daint`, `santis`, `clariden`, `eiger`)
    * `uarch` is the [micro-architecture][ref-uenv-label-uarch].

!!! example "building a uenv"
    Call the 
    ```
    uenv build $SCRATCH/recipes/myapp myapp/v3@daint%gh200
    ```

    The image will be built on `daint`.
    The build tool gives you a url to a status page, that shows the progress of the build.
    After a successful build, the uenv can be pulled:
    ```
    uenv image pull service::myapp/v3:1669479716
    ```

    Note that the image is given a unique numeric tag, that you can find on the status page for the build.

!!! info
    To use an existing uenv recipe as the starting point for a custom recipe, `uenv start` the uenv and take the contents of the `meta/recipe` path in the mounted image (this is the recipe that was used to build the uenv).

All uenv built by `uenv build` are pushed into the `service` namespace, where they **can be accessed by all users logged in to CSCS**.
This makes it easy to share your uenv with other users, by giving them the name, version and tag of the image.

!!! warning
    **If, for whatever reason, your uenv can not be made publicly available, do not use the build service.**

!!! example "search user-built uenv"
    To view all of the uenv on daint that have been built by the service:
    ```
    uenv image find service::@daint
    ```

