[](){#ref-cluster-eiger}
# Eiger

Eiger is an Alps cluster that provides compute nodes and file systems designed to meet the needs of CPU-only workloads for the [HPC Platform][ref-platform-hpcp].

!!! note
    This documentation is for the updated cluster `Eiger.Alps` reachable at `eiger.alps.cscs.ch`, that replaced the former cluster as on July 1 2025.

??? change "Important changes from Eiger"
    The redeployment of `eiger.cscs.ch` as `eiger.alps.cscs.ch` has introduced changes that may affect some users.

    ### Breaking changes

    !!! warning "Sarus is replaced with the Container Engine"
        The Sarus container runtime is replaced with the [Container Engine][ref-container-engine].

        If you are using Sarus to run containers on Eiger, you will have to [rebuild][ref-build-containers] and adapt your containers for the Container Engine.

    !!! warning "Cray modules and EasyBuild are no longer supported"
        The Cray Programming Environment (accessed via the `cray` module) is no longer supported by CSCS, along with software that CSCS provided using EasyBuild.

        The same version of the Cray modules is still available, along with software that was installed using them, however they will not receive updates or support from CSCS.

        You are strongly encouraged to start using [uenv][ref-cluster-eiger-uenv] to access supported applications and to rebuild your own applications.

        * The versions of compilers, `cray-mpich`, Python and libraries in uenv are up to date.
        * The scientific application uenv have up to date versions of the supported applications.

    ### Minor changes

    !!! change "Slurm is updated from version 23.02.6 to 24.05.4"

## Cluster specification

### Compute nodes

Eiger consists of multicore [AMD Epyc Rome][ref-alps-zen2-node] compute nodes: please note that the total number of available compute nodes on the system might vary over time.
See the [Slurm documentation][ref-slurm-partitions-nodecount] for information on how to check the number of nodes.

Additionally, there are four login nodes with host names `eiger-ln00[1-4]`.

### Storage and file systems

Eiger uses the [HPCP filesystems and storage policies][ref-hpcp-storage].

## Getting started

### Logging into Eiger

To connect to Eiger via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to eiger using `ssh eiger.alps`.
    ```
    Host eiger.alps
        HostName eiger.alps.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```

### Software

[](){#ref-cluster-eiger-uenv}
#### uenv

CSCS and the user community provide [uenv][ref-uenv] software environments on Eiger.


<div class="grid cards" markdown>

-    :fontawesome-solid-layer-group: __Scientific Applications__

    Provide the latest versions of scientific applications, tuned for Eiger, and the tools required to build your own version of the applications.

     * [CP2K][ref-uenv-cp2k]
     * [GROMACS][ref-uenv-gromacs]
     * [LAMMPS][ref-uenv-lammps]
     * [NAMD][ref-uenv-namd]
     * [Quantumespresso][ref-uenv-quantumespresso]
     * [VASP][ref-uenv-vasp]

</div>

<div class="grid cards" markdown>

-    :fontawesome-solid-layer-group: __Programming Environments__

    Provide compilers, MPI, Python, common libraries and tools used to build your own applications.

    * [prgenv-gnu][ref-uenv-prgenv-gnu]
    * [linalg][ref-uenv-linalg]
    * [julia][ref-uenv-julia]
</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Tools__

    Provide tools like 

    * [Linaro Forge][ref-uenv-linaro]
</div>

[](){#ref-cluster-eiger-users-apps}
#### User applications
For help with [user applications][ref-support-user-apps], see the following guides:

* [ORCA][ref-software-orca]
* [WRF][ref-software-wrf]

[](){#ref-cluster-eiger-containers}
#### Containers

Eiger supports container workloads using the [Container Engine][ref-container-engine].

To build images, see the [guide to building container images on Alps][ref-build-containers].

!!! warning "Sarus is not available"
    A key change with the new Eiger deployment is that the Sarus container runtime is replaced with the [Container Engine][ref-container-engine].

    If you are using Sarus to run containers on Eiger, you will have to rebuild and adapt your containers for the Container Engine.

#### Cray Modules

!!! warning
    The Cray Programming Environment (CPE), loaded using `module load cray`, is no longer supported by CSCS.

    CSCS will continue to support and update uenv and the Container Engine, and users are encouraged to update their workflows to use these methods at the first opportunity.

    The CPE is still installed on Eiger, however it will receive no support or updates, and will be [replaced with a container][ref-cpe] in a future update.

## Running jobs on Eiger

### Slurm

Eiger uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor workloads on compute nodes.

There are multiple [Slurm partitions][ref-slurm-partitions] on the system:

* the `debug` partition can be used to access a small allocation for up to 30 minutes for debugging and testing purposes
* the `prepost` partition is meant for small high priority allocations up to 30 minutes, for pre- and post-processing jobs.
* the `normal` partition is for all production workloads.
* the `xfer` partition is for [internal data transfer][ref-data-xfer-internal].
* the `low` partition is a low-priority partition, which may be enabled for specific projects at specific times.

| name | max nodes per job | time limit |
| --   |  -- | -- |
| `debug`  | 1    | 30 minutes |
| `prepost`  | 1    | 30 minutes |
| `normal` | -    | 24 hours |
| `xfer`   | 1    | 24 hours |
| `low`    | -    | 24 hours |

* nodes in the `normal` and `debug` partitions are not shared
* nodes in the `xfer` partition can be shared

See the Slurm documentation for instructions on how to run jobs on the [AMD CPU nodes][ref-slurm-amdcpu].

### JupyterHub 

A [JupyterHub][ref-jupyter] service for Eiger is available at [https://jupyter-eiger.cscs.ch](https://jupyter-eiger.cscs.ch).

### FirecREST

Eiger can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/hpc/firecrest/v2` API endpoint.

!!! warning "The FirecREST v1 API is still available, but deprecated"

## Maintenance and status

### Scheduled maintenance

Wednesday mornings 8:00-12:00 CET are reserved for periodic updates, with services potentially unavailable during this time frame. If the batch queues must be drained (for redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, the [CSCS Status Page](https://status.cscs.ch) and the [#eiger channel](https://cscs-users.slack.com/archives/C08FBP55CG1) of the [CSCS User Slack][ref-get-in-touch].

### Change log

!!! change "2025-06-05 Early access phase"
    Early access phase is open

??? change "2025-05-23 Creation of Eiger on Alps"
    Eiger is deployed as a vServices-enabled cluster

### Known issues
