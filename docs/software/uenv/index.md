[](){#ref-uenv}
# uenv

Uenv are user environments that provide scientific applications, libraries and tools.
Uenv are typically application-specific, domain-specific or tool-specific - each uenv contains only what is required for the application or tools that it provides.

Each uenv is packaged in a single file (in the [Squashfs](https://docs.kernel.org/filesystems/squashfs.html) file format), that stores a compressed directory tree that contains all of the software, tools and other information like modules, required to provide a rich environment.

The following guides are a good spot to start.
They cover everything you need to get started with using uenv to build your code, and set up your workflows and Slurm jobs:

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Quick start guide__

    A quick introduction to get you started

    [:octicons-arrow-right-24: Quick start][ref-uenv-quickstart]

-   :fontawesome-solid-layer-group: __Using uenv__

    Learn how to start uenv sessions on the command line, run commands in uenv environments, and use uenv in Slurm.

    [:octicons-arrow-right-24: Using uenv][ref-uenv-using]

-   :fontawesome-solid-layer-group: __Managing uenv__

    Uenv need to be downloaded before they can be used.

    Learn how to search for, download and manage uenv images.

-   :fontawesome-solid-layer-group: __uenv guides__

    Learn about how uenv are named and referenced:

    [:octicons-arrow-right-24: uenv naming][ref-uenv-labels]

</div>

The following guides provide for advanced users and CSCS staff:

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Building uenv__

    More adventurous users can create their own uenv for personal use, and for other users in their team and community.

    [:octicons-arrow-right-24: Building uenv][ref-uenv-build]

-   :fontawesome-solid-layer-group: __Configuring uenv__

    Users can customize the behavior of uenv using a configuration file.

    [:octicons-arrow-right-24: Configuring uenv][ref-uenv-configure]

-   :fontawesome-solid-layer-group: __Release notes__

    Release notes for the uenv tools installed on Alps.

    Check here for changes, and known issues and bugs for specific versions.

    [:octicons-arrow-right-24: uenv release notes][ref-uenv-release-notes]

-   :fontawesome-solid-layer-group: __Deploying uenv__

    Documentation on how CSCS deploys uenv images.

    **For CSCS staff**, though it may be of interest to advanced users.

    [:octicons-arrow-right-24: Deploying uenv][ref-uenv-deploy]


</div>

[](){#ref-uenv-quickstart}
## Quick start

After logging into an [Alps cluster][ref-alps-clusters], you can quickly check the availability of uenv with the following commands:

```console
$ uenv status
there is no uenv loaded
$ uenv --version
9.0.0
```

On Alps clusters the current versions are available

| version | description |
| -- | -- |
| 9.0.0 | currently installed on [Eiger][ref-cluster-eiger], [Daint][ref-cluster-daint], [Clariden][ref-cluster-clariden] and [Santis][ref-cluster-santis] |
| 9.0.1 | bug fix release that will be deployed mid November 2025 |
| 9.1.0 | feature release, currently being tested. Will be deployed late November 2025  |

Uenv are fully self-contained environments stored in a single SquashFS file.
In order to use a uenv, it first has to be downloaded into a local file system.

The `uenv` command line tool is the main tool used to interact with uenv.
The basic workflow for using a uenv provided by CSCS is:

* search for available images using `uenv image find`
* download images using `uenv image pull`
* then start a uenv using `uenv start`

Take the example of downloading a uenv that provides the [NAMD][ref-uenv-namd] simulation software:

```console
$ uenv image find namd
uenv         arch  system  id                size(MB)  date
namd/3.0:v1  zen2  eiger   cd8d842d108f2eb1     347    2025-05-21

$ uenv image pull namd
pulling cd8d842d108f2eb1 100.00% ━━━━━━━━━━━━━━━━━━━━━━━━━ 348/348 (60.71 MB/s)
updating namd/3.0:v1@eiger%zen2

$ uenv image ls
uenv         arch  system  id                size(MB)  date
namd/3.0:v1  zen2  eiger   cd8d842d108f2eb1     347    2025-05-21

$ uenv start namd/3.0:v1
$ which namd3
/user-environment/env/namd/bin/namd3
$ exit
```

!!! warning
    To use a uenv, it must first be downloaded using `uenv image pull`.
    See the [uenv management][ref-uenv-find] documentation for more information.

Once you have downloaded the correct uenv, compiled and configured your workflow, the [Slurm plugin][ref-uenv-slurm] can be used to efficiently enable uenv inside Slurm jobs.

