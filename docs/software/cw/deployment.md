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

## Getting access

Uenv recipes are stored in the GitHub repository [C2SM/software-stack-recipes](https://github.com/C2SM/software-stack-recipes), with a pipeline based on the CSCS [CI/CD service](https://github.com/C2SM/software-stack-recipes) that builds and tests uenv.
The GitHub repository is public, and anybody with a GitHub account can make a pull request with a new recipe, or a modification to an existing repository.
However, to trigger CI/CD builds your GitHub user account must be given permission to trigger builds.

Contact one of the following people with your **GitHub user name** to request access:

- [Dr. Matthieu Leclair](https://c2sm.ethz.ch/the-center/people/person-detail.html?persid=221860) at C2SM
- Ben Cumming at CSCS
- Mikael Simberg at CSCS

They will perform the following steps:

- Give you permission to trigger builds in the *climate-weather-uenv* [CI/CD project](https://cicd-ext-mw.cscs.ch);
- Give you write permission to the [C2SM/software-stack-recipes](https://github.com/C2SM/software-stack-recipes) (only if strictly required - most users will only need permission to trigger pipelines).

## Creating a new image

- Create a fork,
- make a branch
- add recipe
- edit config.yaml
- make a PR comment

- creating a new recipe
- creating a new version

## Triggering a build

- make a comment on build

