[](){#ref-cluster-daint}
# Daint

Daint is the main [HPC Platform][ref-platform-hpcp] cluster that provides compute nodes and file systems for GPU-enabled workloads.

## Cluster specification

### Compute nodes

Daint consists of around 800-1000 [Grace-Hopper nodes][ref-alps-gh200-node].

The number of nodes can vary as nodes are added or removed from other clusters on Alps.
See the [Slurm documentation][ref-slurm-partitions-nodecount] for information on how to check the number of nodes.

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

    The CPE is still installed on Daint, however it will receive no support or updates, and will be [replaced with a container][ref-cpe] in a future update.

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
| `normal` | unlimited  | -    | 24 hours |
| `debug`  | 24         | 2    | 30 minutes |
| `xfer`   | 2          | 1    | 24 hours |
| `low`    | unlimited  | -    | 24 hours |

* nodes in the `normal` and `debug` (and `low`) partitions are not shared
* nodes in the `xfer` partition can be shared

See the Slurm documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

### FirecREST

Daint can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/hpc/firecrest/v2` API endpoint.

!!! warning "The FirecREST v1 API is still available, but deprecated"

## Maintenance and status

### Scheduled maintenance

One Wednesday per month is reserved for planned maintenance (usually around the middle of the month). If the batch queues must be drained (for redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

Exceptional and non-disruptive updates may happen outside this time frame and will be announced via the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2026-06-17"
    !!! note "Operating Environment and Networking Stack"
    - Updated HPE Cray Supercomputing User Services Software (USS) from 1.3.1 to version 1.4.0
    - Updated Slingshot Host Software (SHS) from version 12.0.1 to version 13.1.0.
    - Improved Ritom performance, see also [VAST tuning][ref-guides-storage-vast-ritom] for individual IO tuning parameters

    !!! note "Container Engine"
    - Updated Container Engine to v26.06.1
    - Slingshot-related hooks now use Network Stack Artifacts (also called "netstacks") as default resources for the components, libraries and dependencies mounted inside containers (e.g., libfabric, AWS OFI NCCL, Slingshot dependencies). Previously, the host stack was the default: see [our docs][ref-ce-netstack-source]
        - To enable the previous behaviour, you should use `com.hooks.netstack.source = "host"`
    - Fixed an issue with importing images using multi-line LABEL, e.g., ubuntu-26.04 based images.
    - Environment variables:
    We introduced a few new (or changed) default environment variables when running with the Container Engine hook `aws_ofi_nccl.enabled="true"`. These variables have the same values as the [Alps Extended Images][ref-software-extended-images], i.e., they bring both environments into sync.
    ```
    CUDA_CACHE_DISABLE="1"
    ```
    This will disable the CUDA-JIT cache. For some time, the default value for `CUDA_CACHE_PATH` has been a subdirectory in `/dev/shm`. However, `/dev/shm` is cleaned up after every job, so it is of little use to cache a result there, since it will be cleared after the job finishes.
    Further information regarding the CUDA cache can be found at [https://developer.nvidia.com/blog/cuda-pro-tip-understand-fat-binaries-jit-caching/](https://developer.nvidia.com/blog/cuda-pro-tip-understand-fat-binaries-jit-caching/).
    ```
    NCCL_CROSS_NIC="0":, (changed from "1")
    NCCL_PXN_DISABLE="1" (previously unset)
    NCCL_P2P_LEVEL="NVL" (previously unset)
    NCCL_NET_GDR_C2C="1" (previously unset)
    NCCL_NET_GDR_READ="1" (previously unset)
    NCCL_PROTO="^LL128" (previously unset)
    NCCL_NCHANNELS_PER_NET_PEER="4" (previously unset)
    ```
    Information about the variables can be found at [https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html)
    ```
    FI_CXI_RDZV_PROTO="alt_read" (previously unset)
    FI_CXI_RDZV_EAGER_SIZE="0" (previously unset)
    FI_CXI_RDZV_GET_MIN="0" (previously unset)
    FI_CXI_RDZV_THRESHOLD="0" (previously unset)
    FI_MR_CACHE_MAX_SIZE="-1" (previously unset)
    FI_MR_CACHE_MAX_COUNT="524288" (previously unset)
    FI_CXI_SAFE_DEVMEM_COPY_THRESHOLD="16777216" (previously unset)
    ```
    Information about the variables can be found at [https://ofiwg.github.io/libfabric/v2.3.0/man/fi_cxi.7.html](https://ofiwg.github.io/libfabric/v2.3.0/man/fi_cxi.7.html).

    Our testing has shown performance gains from these new defaults. Please contact us if you observe any performance degradation. 

    !!! note "Uenv"
    - Upgraded Uenv from version 9.2.0 to 10.0.1.
    - Features:
        - TOML configuration format and improved repository management: multiple named repositories can be configured and selected by name.
        - Default views: Uenv images can declare a view to load automatically when no `--view` flag is given.
        - Advanced Slurm workflows: the `--uenv-passthrough` flag controls whether a loaded uenv is forwarded to nested srun, sbatch, or salloc calls.
        - New global `--system` flag to override the cluster name on the CLI (e.g. `uenv --system='*' image find`).
        - Improved bash completion for uenv labels and file paths.
    - Fixes:
        - Changed a hard error to a warning when image metadata is not attached in the registry.
        - Fixed a latent bug parsing date strings in image metadata.
    - [uenv changelog][ref-uenv-release-notes-v10.0]

??? change "2025-05-21"
    Minor enhancements to system configuration have been applied.
    These changes should reduce the frequency of compute nodes being marked as `NOT_RESPONDING` by the workload manager, while we continue to investigate the issue

??? change "2025-05-14"
    ??? note "Performance hotfix"
        The [access-counter-based memory migration feature](https://developer.nvidia.com/blog/cuda-toolkit-12-4-enhances-support-for-nvidia-grace-hopper-and-confidential-computing/#access-counter-based_migration_for_nvidia_grace_hopper_memory) in the NVIDIA driver for Grace Hopper is disabled to address performance issues affecting NCCL-based workloads (e.g. LLM training)

    ??? note "NVIDIA boost slider"
        Added [an option to enable the NVIDIA boost slider (vboost)][ref-slurm-features-vboost] via Slurm using the `-C nvidia_vboost_enabled` flag.
        This feature, disabled by default, may increase GPU frequency and performance while staying within the power budget

    ??? note "Enroot update"
        The container runtime is upgraded from version 2.12.0 to 2.13.0. This update includes libfabric version 1.22.0 (previously 1.15.2.0), which has demonstrated improved performance during LLM checkpointing

??? change "2025-04-30"
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
