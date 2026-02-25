[](){#ref-software-cw-deploy}
# Climate and Weather Software Deployment

The [uenv][ref-uenv] deployed on [Santis][ref-cluster-santis] and Balfrin are generated from two sources:

- **cscs managed**: uenv created and supported by CSCS, including:
    - [netcdf-tools][ref-uenv-netcdf-tools];
    - [Programming environments][ref-software-prgenvs];
    - and tools including [Linaro Forge][ref-uenv-linaro].
- **community managed** uenv recipes in the [C2SM/software-stack-recipes](https://github.com/C2SM/software-stack-recipes)
    - [icon][ref-software-icon]
    - `climana` on Santis.
    - `fdb` uenv on the MCH systems.

The community managed uenv are a distinguishing feature of the [Climate and Weather Platform][ref-platform-cwp].
They provide software for all users, focussed particularly on ICON workflows.

!!! note
    The uenv deployed on Santis and Balfrin are available to all users who can log into the respective system.
    This page describes the additional steps required to deploy uenv for users on the system.

[](){#ref-software-cw-deploy-permission}
## Permission to Trigger Pipelines

Uenv recipes are stored in the GitHub repository [C2SM/software-stack-recipes](https://github.com/C2SM/software-stack-recipes), with a pipeline based on the CSCS [CI/CD service](https://github.com/C2SM/software-stack-recipes) that builds and tests uenv.
The GitHub repository is public, and anybody with a GitHub account can make a pull request with a new recipe, or a modification to an existing repository.
However, to trigger CI/CD builds your GitHub user account must be given permission to trigger builds.

The CI/CD project is administered by staff from [C2SM](https://c2sm.ethz.ch/), [MeteoSwiss (MCH)](https://www.meteoswiss.admin.ch) and CSCS.
Contact one of the following people with your **GitHub user name** to request permission:

- [Matthieu Leclair](https://c2sm.ethz.ch/the-center/people/person-detail.html?persid=221860) at C2SM
- [Mikael Stellio](https://c2sm.ethz.ch/the-center/people/person-detail.html?persid=226434) at C2SM
- Ben Cumming at CSCS
- Mikael Simberg at CSCS
- Nina Burgdorfer at MCH
- Daniel Hupp at MCH

!!! note
    MCH staff working on MCH workflows should contact one of the MCH representatives.
    Other users should contact a representative from C2SM or CSCS.

    Permission to run CI/CD is reserved for users who contribute to uenv agreed upon by C2SM, MCH and CSCS, and is not automatically granted to all users.

    It is possible to provide software on Alps using the [uenv build service][ref-uenv-build].

They will perform the following steps:

- Give you permission to trigger builds in the *climate-weather-uenv* [CI/CD project](https://cicd-ext-mw.cscs.ch);
- Give you write permission to the [C2SM/software-stack-recipes](https://github.com/C2SM/software-stack-recipes) (only if strictly required - most users will only need permission to trigger pipelines).

## Creating a New Image

The workflow for both creating a new version of a uenv, or creating a new uenv is the same.
We follow the fork and branch workflow described in the [GitHub documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo).

1. Create a fork of the [C2SM/software-stack-recipes](https://github.com/C2SM/software-stack-recipes) repository.
2. Clone your fork, and create a branch for your changes.
3. Add the new recipe to the repository
    - if making a new version of an existing recipe (add example)
4. Update information in the [`config.yaml` configuration file](https://github.com/C2SM/software-stack-recipes/blob/main/config.yaml) with details of your new recipe.
5. Make a pull request to the main [C2sm/software-stack-recipes](https://github.com/C2SM/software-stack-recipes/pulls) repository.
    - start the title of the pull request with the name of the uenv, for example `fdb: update to fdb 5.19.0`.

Once the pull request has been opened, the pipeline does not automatically start building a uenv.

Builds are triggered using a PR comment by a user who as been [added to the CI/CD configuration][ref-software-cw-deploy-permission].

!!! example "Build fdb/5.19 on balfrin"
    Note that uenv for use on Balfrin that do not require GPU should target the `zen3` micro-architecture.

    These images can be run on both the CPU and GPU nodes of Balfrin.

    ```
    cscs-ci run alps;system=balfrin;uarch=zen3;uenv=fdb:5.19
    ```

!!! example "Build icon-dsl/25.12 on santis"
    All uenv on Santis target the `gh200` micro-architecture, even those that are only run on the Grace CPU.

    ```
    cscs-ci run alps;system=santis;uarch=gh200;uenv=icon-dsl:25.12
    ```

!!! example "Build mch/v8 on Balfrin"
    Uenv for GPU workloads on Balfrin should target the `a100` micro-architecture.
    The `mch` software stack is used by both CPU and GPU nodes, because it provides two "views": one that does not include any GPU libraries or CUDA dependencies.

    ```
    cscs-ci run alps;system=balfrin;uarch=a100;uenv=mch:v8
    ```

The build pipeline runs a job on the target system, and on success will push the image into the [`deploy` namespace][ref-uenv-deploy-registries].

You will be able to find all builds on a system by logging into the system, and using the `build::` prefix when searching.

!!! example "Finding fdb builds"
    ```console
    # search for all builds of fdb
    $ uenv image find build::fdb

    # search for builds of fdb/5.18
    $ uenv image find build::fdb/5.18
    uenv                 arch  system   id                size(MB)  date
    fdb/5.18:2110858405  zen3  balfrin  f7fb7baea157cce0     701    2025-10-21
    fdb/5.18:2162754541  zen3  balfrin  33ef8bf54533c871     786    2025-11-17
    ...
    fdb/5.18:2339783178  zen3  balfrin  6a0da38bb279de97     843    2026-02-20

    # pull a build for testing
    $ uenv image pull build::fdb/5.18:2339783178
    $ uenv start build::fdb/5.18:2339783178
    ```

## Final deployment

The final stage of deployment is to copy the uenv generated by the pipeline from the `build::` namespace to the `deploy::` namespace.

This step [can only performed][ref-uenv-deploy-permission] by CSCS staff.
Contact Mikael or Ben via email of Slack, with the a message like the following to have the image deployed.

> Please relase `build::fdb/5.18:2339783178` on Balfrin as `fdb/5.18:v2`.

Once deployed, the example above would be visible to users typing `uenv image find` or `uenv image find fdb` on Balfrin.
