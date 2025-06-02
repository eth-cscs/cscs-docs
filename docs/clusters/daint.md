[](){#ref-cluster-daint}
# Daint

Daint is the main [HPC Platform][ref-platform-hpcp] cluster that provides compute nodes and file systems for GPU-enabled workloads.

## Cluster specification

### Compute nodes

Daint consists of around 800-1000 [Grace-Hopper nodes][ref-alps-gh200-node].

The number of nodes can vary as nodes are added or removed from other clusters on Alps.

There are four login nodes, `daint-ln00[1-4]`.
You will be assigned to one of the four login nodes when you ssh onto the system, from where you can edit files, compile applications and launch batch jobs.

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|-----------------| ----------------- | ---------- |
| [gh200][ref-alps-gh200-node] | 1,022 | 4,088    | 4,088 |

### Storage and file systems

Daint uses the [HPCP filesystems and storage policies][ref-hpcp-storage].

## Getting started

### Logging into Daint

To connect to Daint via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to Daint using `ssh daint`.
    ```
    Host daint
        HostName daint.alps.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```

### Software

[](){#ref-cluster-daint-uenv}
#### uenv

Daint provides uenv to deliver programming environments and application software.
Please refer to the [uenv documentation][ref-uenv] for detailed information on how to use the uenv tools on the system.

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Scientific Applications__

    Provide the latest versions of scientific applications, tuned for Daint, and the tools required to build your own versions of the applications.

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
    * [prgenv-nvfortran][ref-uenv-prgenv-nvfortran]
    * [linalg][ref-uenv-linalg]
    * [julia][ref-uenv-julia]
</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Tools__

    Provide tools like 

    * [Linaro Forge][ref-uenv-linaro]
</div>

[](){#ref-cluster-daint-containers}
#### Containers

Daint supports container workloads using the [container engine][ref-container-engine].

To build images, see the [guide to building container images on Alps][ref-build-containers].

#### Cray Modules

!!! warning
    The Cray Programming Environment (CPE), loaded using `module load cray`, is no longer supported by CSCS.

    CSCS will continue to support and update uenv and container engine, and users are encouraged to update their workflows to use these methods at the first opportunity.

    The CPE is still installed on Daint, however it will receive no support or updates, and will be replaced with a container in a future update.

## Running jobs on Daint

### Slurm

Daint uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor compute-intensive workloads.

There are four [Slurm partitions][ref-slurm-partitions] on the system:

* the `normal` partition is for all production workloads.
* the `debug` partition can be used to access a small allocation for up to 30 minutes for debugging and testing purposes.
* the `xfer` partition is for [internal data transfer][ref-data-xfer-internal].
* the `low` partition is a low-priority partition, which may be enabled for specific projects at specific times.



| name | nodes  | max nodes per job | time limit |
| --   | --     | --                | -- |
| `normal` | unlim        | -    | 24 hours |
| `debug`  | 24         | 2    | 30 minutes |
| `xfer`   | 2          | 1    | 24 hours |
| `low`    | unlim        | -    | 24 hours |

* nodes in the `normal` and `debug` (and `low`) partitions are not shared
* nodes in the `xfer` partition can be shared

See the Slurm documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

### FirecREST

Daint can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/ml/firecrest/v2` API endpoint.

!!! warning "The FirecREST v1 API is still available, but deprecated"

## Maintenance and status

### Scheduled maintenance

!!! todo "move this to HPCP top level docs"
    Wednesday mornings 8:00-12:00 CET are reserved for periodic updates, with services potentially unavailable during this time frame. If the batch queues must be drained (for redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

    Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, and on the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2025-05-21"
    Minor enhancements to system configuration have been applied.
    These changes should reduce the frequency of compute nodes being marked as `NOT_RESPONDING` by the workload manager, while we continue to investigate the issue

!!! change "2025-05-14"
    ??? note "Performance hotfix"
        The [access-counter-based memory migration feature](https://developer.nvidia.com/blog/cuda-toolkit-12-4-enhances-support-for-nvidia-grace-hopper-and-confidential-computing/#access-counter-based_migration_for_nvidia_grace_hopper_memory) in the NVIDIA driver for Grace Hopper is disabled to address performance issues affecting NCCL-based workloads (e.g. LLM training)

    ??? note "NVIDIA boost slider"
        Added an option to enable the NVIDIA boost slider (vboost) via Slurm using the `-C nvidia_vboost_enabled` flag.
        This feature, disabled by default, may increase GPU frequency and performance while staying within the power budget

    ??? note "Enroot update"
        The container runtime is upgraded from version 2.12.0 to 2.13.0. This update includes libfabric version 1.22.0 (previously 1.15.2.0), which has demonstrated improved performance during LLM checkpointing

!!! change "2025-04-30"
    ??? note "uenv is updated from v7.0.1 to v8.1.0"
        [Release notes][ref-uenv-release-notes-v8.1.0]

    ??? note "Pyxis is upgraded from v24.5.0 to v24.5.3"
        * Added image caching for Enroot
        * Added support for environment variable expansion in EDFs
        * Added support for relative paths expansion in EDFs
        * Print a message about the experimental status of the --environment option when used outside of the srun command
        * Merged small features and bug fixes from upstream Pyxis releases v0.16.0 to v0.20.0
        * Internal changes: various bug fixes and refactoring

??? change "2025-03-12"
    1. The number of compute nodes has been increased to 1018
    1. The restriction on the number of running jobs per project has been lifted.
    1. A "low" priority partition has been added, which allows some project types to consume up to 130% of the project's quarterly allocation
    1. We have increased the power cap for the GH module from 624 to 660 W. You might see increased application performance as a consequence 
    1. Small changes in kernel tuning parameters

### Known issues

!!! todo
    Most of these issues (see original [KB docs](https://confluence.cscs.ch/spaces/KB/pages/868811400/Daint.Alps#Daint.Alps-Knownissues)) should be consolidated in a location where they can be linked to by all clusters.

    We have some "know issues" documented under [communication libraries][ref-communication-cray-mpich], however these might be a bit too disperse for centralised linking.
