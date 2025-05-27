[](){#ref-cluster-eiger}
# Eiger

Eiger is an Alps cluster that provides compute nodes and file systems designed to meet the needs of CPU-only workloads for the [HPC Platform][ref-platform-hpcp].

!!! under-construction
    This documentation is for `eiger.alps.cscs.ch` - an updated version of Eiger that will replace the existing `eiger.cscs.ch` cluster.
    For help using the existing Eiger, see the [Eiger User Guide](https://confluence.cscs.ch/spaces/KB/pages/284426490/Alps+Eiger+User+Guide) on the legacy KB documentation site.

    The target date for full deployment of the new Eiger is **July 1, 2025**.

!!! change "Important changes"
    The redeployment of `eiger.cscs.ch` as `eiger.alps.cscs.ch` introduces changes that may affect some users.

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

    ### Unimplemented features

    !!! under-construction "FirecREST is not yet available"
        [FirecREST][ref-firecrest] has not been configured on `eiger.alps` - it is still running on the old Eiger.

        **It will be deployed, and this documentation updated when it is.**

    ### Minor changes

    !!! change "Slurm is updated from version 23.02.6 to 24.05.4"

## Cluster specification

### Compute nodes

!!! under-construction
    During this Early Access phase, there are 19 compute nodes for you to test and port your workflows to the new Eiger deployment. There is one compute node in the `debug` partition and one in the `xfer` partition for internal data transfer.  The remaining compute nodes will be moved from `eiger.cscs.ch` to `eiger.alps.cscs.ch` at a later date (provisionally, 1 July 2025).

Eiger consists of 19 [AMD Epyc Rome][ref-alps-zen2-node] compute nodes. 

There is one login node, `eiger-ln010`. 

[//]: # (TODO: You will be assigned to one of the four login nodes when you ssh onto the system, from where you can edit files, compile applications and start simulation jobs.)

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|-----------------| ----------------- | ---------- |
| [zen2][ref-alps-zen2-node] | 19 | 38      | -          |

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

    The CPE is deprecated and will be removed completely at a future date.

## Running jobs on Eiger

### Slurm

Eiger uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor workloads on compute nodes.

There are four [Slurm partitions][ref-slurm-partitions] on the system:

* the `normal` partition is for all production workloads.
* the `debug` partition can be used to access a small allocation for up to 30 minutes for debugging and testing purposes.
* the `xfer` partition is for [internal data transfer][ref-data-xfer-internal].
* the `low` partition is a low-priority partition, which may be enabled for specific projects at specific times.

| name | nodes  | max nodes per job | time limit |
| --   | --     | --                | -- |
| `normal` | unlim       | -    | 24 hours |
| `debug`  | 32         | 1    | 30 minutes |
| `xfer`   | 2          | 1    | 24 hours |
| `low`    | unlim       | -    | 24 hours |

* nodes in the `normal` and `debug` partitions are not shared
* nodes in the `xfer` partition can be shared

See the Slurm documentation for instructions on how to run jobs on the [AMD CPU nodes][ref-slurm-amdcpu].

### FirecREST

!!! under-construction "FirecREST is not yet available"
    [FirecREST][ref-firecrest] has not been configured on `eiger.alps` - it is still running on the old Eiger.

    **It will be deployed, and this documentation updated when it is.**

## Maintenance and status

### Scheduled maintenance

Wednesday mornings 8:00-12:00 CET are reserved for periodic updates, with services potentially unavailable during this time frame. If the batch queues must be drained (for redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, and on the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2025-06-02 Early access phase"
    Early access phase is open

??? change "2025-05-23 Creation of Eiger on Alps"
    Eiger is deployed as a vServices-enalbed cluster

### Known issues


