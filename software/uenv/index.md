# uenv

Uenvs are user environments that provide scientific applications, libraries and tools. Uenvs are typically application-specific, domain-specific or tool-specific - each uenv contains only what is required for the application or tools that it provides.

Each uenv is packaged in a single file (in the [Squashfs](<https://docs.kernel.org/filesystems/squashfs.html>) file format), that stores a compressed directory tree that contains all of the software, tools and other information like modules, required to provide a rich environment.

The following guides are a good spot to start. They cover everything you need to get started with using uenv to build your code, and set up your workflows and Slurm jobs:

- **Quick start guide**

  A quick introduction to get you started

  Quick start
- **Using uenv**

  Learn how to start uenv sessions on the command line, run commands in uenv environments, and use uenv in Slurm.

  Using uenv
- **Managing uenv**

  Uenvs need to be downloaded before they can be used.

  Learn how to search for, download and manage uenv images.

  Managing uenvs
- **uenv guides**

  How uenvs are named and referenced:

  uenv naming

  Hints and tips for creating custom environments:

  Custom environments

  How to install software on a uenv:

  Using Spack

  Python environments

The following guides provide for advanced users and CSCS staff:

- **Building uenv**

  More adventurous users can create their own uenvs for personal use, and for other users in their team and community.

  Building uenvs
- **Configuring uenv**

  Users can customize the behavior of uenv using a configuration file.

  Configuring uenvs
- **Release notes**

  Release notes for the uenv tools installed on Alps.

  Check here for changes, known issues and bugs for specific versions.

  uenv release notes
- **Deploying uenv**

  Documentation on how CSCS deploys uenv images.

  **For CSCS staff**, though it may be of interest to advanced users.

  Deploying uenvs

## Quick start

After logging into an Alps cluster, you can quickly check the availability of uenv with the following commands:

```console
$ uenv status
there is no uenv loaded
$ uenv --version
10.1.0
```

uenv v10.1.0 is installed on Daint, Eiger, Clariden and Santis.

See the uenv release notes for more information about features, fixes and known issues in each version.

The `uenv` command line tool is the main tool used to interact with uenvs. The basic workflow for using a uenv provided by CSCS is:

- search for available images using `uenv image find`
- download images using `uenv image pull`
- then start or running a uenv using `uenv start` or `uenv run`

Take the example of downloading a uenv that provides the NAMD simulation software:

```console
$ uenv image find namd
uenv         arch  system  id                size(MB)  date
namd/3.0:v1  zen2  eiger   cd8d842d108f2eb1     347    2025-05-21

$ uenv image pull namd/3.0:v1
pulling cd8d842d108f2eb1 100.00% ━━━━━━━━━━━━━━━━━━━━━━━━━ 348/348 (60.71 MB/s)
updating namd/3.0:v1@eiger%zen2

$ uenv image ls
uenv         arch  system  id                size(MB)  date
namd/3.0:v1  zen2  eiger   cd8d842d108f2eb1     347    2025-05-21

$ uenv image inspect namd/3.0:v1
repo default:/ritom/scratch/cscs/cscsusername/.uenv-images
namd/3.0:v1@eiger%zen2 mount at /user-environment
views:
  spack: configure spack upstream
  namd:
  modules: activate modules
  develop:

$ uenv start --view=namd namd/3.0:v1
$ which namd3
/user-environment/env/namd/bin/namd3
$ exit
```

> [!WARNING]
>
> To use a uenv, it must first be downloaded using `uenv image pull`. See the uenv management documentation for more information.

Once you have downloaded the correct uenv, compiled and configured your workflow, the Slurm plugin can be used to efficiently enable uenv inside Slurm jobs.
