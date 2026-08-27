[](){#ref-cluster-santis}
# Santis

Santis is the main [Climate and Weather Platform][ref-platform-cwp] cluster that provides compute nodes and file systems for GPU-enabled climate and weather workloads.

## Cluster specification

### Compute nodes

Santis consists of 302 [Grace-Hopper nodes][ref-alps-gh200-node].

The number of nodes can vary as nodes are added or removed from other clusters on Alps.
See the [Slurm documentation][ref-slurm-partitions-nodecount] for information on how to check the number of nodes.

There are two login nodes, `santis-ln00[1,2]`, which are repurposed compute nodes from the pool of 302 GH200 nodes.
You will be assigned to one of the two login nodes when you ssh onto the system, from where you can edit files, compile applications and launch batch jobs.
This leaves 300 nodes available for compute jobs.

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|-----------------| ----------------- | ---------- |
| [gh200][ref-alps-gh200-node] | 302 | 1,208      | 1,208 |

### Storage and file systems

Santis uses the [CWP filesystems and storage policies][ref-cwp-storage].

## Getting started

### Logging into Santis

To connect to Santis via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to Santis using `ssh santis`.
    ```
    Host santis
        HostName santis.alps.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```

### Software

[](){#ref-cluster-santis-uenv}
#### uenv

Santis provides uenv to deliver programming environments and application software for the climate and weather community.
Please refer to the [uenv documentation][ref-uenv] for detailed information on how to use the uenv tools on the system.

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Climate and Weather Applications__

    Provide software stacks for climate and weather workflows on Santis.

     * [ICON][ref-software-icon]
     * [netcdf-tools][ref-uenv-netcdf-tools]

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

??? example "using uenv provided for other clusters"
    You can run uenv that were built for other Alps clusters using the `@` notation.
    For example, to use uenv images for [daint][ref-cluster-daint]:
    ```bash
    # list all images available for daint
    uenv image find @daint

    # download an image for daint
    uenv image pull namd/3.0:v3@daint

    # start the uenv
    uenv start namd/3.0:v3@daint
    ```

[](){#ref-cluster-santis-containers}
#### Containers

Santis supports container workloads using the [container engine][ref-container-engine].

To build images, see the [guide to building container images on Alps][ref-build-containers].

## Running jobs on Santis

### Slurm

Santis uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor compute-intensive workloads.

There are four [Slurm partitions][ref-slurm-partitions] on the system:

| name | node type | max nodes per job | time limit | purpose |
| --   | --        | --                | --         | -- |
| `normal` | GH200 | unlimited | 24 hours | standard compute (default) |
| `debug`  | GH200 | 2         | 30 minutes | short testing |
| `low`    | GH200 | unlimited | 24 hours | overflow / quota-exhausted projects |
| `xfer`   | x86   | 1         | 24 hours | [internal data transfer][ref-data-xfer-internal] at CSCS |

#### Node sharing and GPU requests

All GH200 partitions on Santis use **node sharing**. A job no longer receives a full node by default. Instead, resources are allocated at the granularity of one GH200 chip:

* request 1 GPU → receive 1 chip (72 cores, ~217 GB RAM)
* request 4 GPUs → receive the whole node

Jobs must request GPUs explicitly, for example:

```bash
sbatch --gres=gpu:2 ...
# or
sbatch --gpus-per-node=2 ...
```

If no GPU is requested, the job may receive only a minimal CPU allocation and will not run on an exclusive node.

#### Multi-GPU jobs with P2P/IPC

Because device isolation is enforced via cgroups, multi-GPU jobs that rely on GPU P2P/IPC (for example MPI across GPUs on the same node) must add to the `srun` command (NB: this does not work being specified in the `#SBATCH` definition block):

```bash
--gres-flags=allow-task-sharing
```

This keeps all GPUs allocated to a job visible to all tasks of that job while preserving per-task `CUDA_VISIBLE_DEVICES` bindings. Without this flag, intra-node GPU-GPU communication will fail.

!!! information
    Alternatively, you can set the environment variable `SLURM_GRES_FLAGS` in your job submission script, e.g.:
    `export SLURM_GRES_FLAGS="allow-task-sharing"` (if you have other flags set, you can add them as a comma-separated list)
    

#### CPU Power Capping

This power capping feature allows to optimize power distribution on the GH200 nodes in favour of the GPUs for applications using CPU and GPU simultaneously.
You can find more details and instructions how to activate the power capping in your runs [here][ref-slurm-gh200-power-capping].

#### Low-priority overflow partition

The `low` partition is available to all users for work that should only run when the higher-priority partitions have idle capacity. It is intended for:

* quota-exhausted projects that still need some resources before the next quarterly reset
* work that does not need fast turnaround

Jobs in `low` have lower scheduling priority and **are not preempted**.

#### Concurrent job limit

Each user may have at most **10 jobs running at the same time** across `normal`, `debug`, and `low`. Submissions are not limited; additional jobs queue until one of the running jobs finishes.

See the Slurm documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

### FirecREST

Santis can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/cw/firecrest/v2` API endpoint.

!!! warning "The FirecREST v1 API is still available, but deprecated"

## Maintenance and status

### Scheduled maintenance

One Wednesday per month is reserved for planned maintenance (usually around the middle of the month, 8-12 CET), with services potentially unavailable during this timeframe. If the queues must be drained (redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window.

Exceptional and non-disruptive updates may happen outside this time frame and will be announced via the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2026-08-26"
    !!! note "Login node limits"
        To enforce our [fair usage of shared resources][ref-policies-fair-use-login-node] policies, we have enabled limits on the login nodes.
        Please note that some limits apply to individual processes, while other limits apply to the sum of your running processes.
        Agentic tools and VSCode might be affected by these limits.
        Compute intensive tasks will also be affected by the limits.
        Any compute intensive task that is beyond the limits should be submitted to a compute node.

    !!! note "Slurm"
        - Enable node sharing on all GH200 compute partitions. Resources are allocated per GH200 chip: one requested GPU corresponds to 72 cores and approximately 217 GB RAM.
        - Introduce the `low` partition for overflow work and quota-exhausted projects.
        - Enforce a per-user limit of 10 concurrently running jobs.
        - Multi-GPU jobs relying on intra-node P2P/IPC must add `--gres-flags=allow-task-sharing` to the `srun` command or `export SLURM_GRES_FLAGS=allow-task-sharing`.

    !!! warning "Known limitation"
        - SLURM accounting still bills per node-hour. A single-chip job is currently accounted as one full node-hour until chip-level accounting is implemented. Compensation for node-hours lost due to this lag will be evaluated on a case-by-case basis.

??? change "2026-06-17"
    !!! note "Operating Environment and Networking Stack"
    - Update HPE Cray Supercomputing User Services Software (USS) from 1.3.1 to version 1.4.0
    - Update Slingshot Host Software (SHS) from version 12.0.1 to version 13.1.0.

    !!! note "Container Engine"
    - Update to Container Engine v26.06.1

    - General version updates
        - Enroot CSCS_2026_05_1
        - Podman 5.8.2
        - NVIDIA Container Toolkit 1.19.1
        - crun 1.28

    - Enroot updates
        - Updated default Enroot to CSCS_2026_05_1
            - Merged updates and fixes from NVIDIA upstream code v4.x releases.
            - Fixed import of images with multi-line OCI labels
        - AWS OFI NCCL hook: NCCL, CXI and OFI environment variables are now aligned with those set in Alps Extended Images
        - PMIx hook: Use PMIx environment variables instead of `scontrol` call to determine bind mount paths (reflects change in upstream Enroot code)
        - DCGM hook: libraries with full ABI string versions are no longer mounted
        - `mksquashfs` now exits upon encountering errors which would be ignored by default and could result in incomplete squashfs images being created during import.

    - Additional notes
        - This update keeps Enroot hooks as they currently operate, using host HPE libraries as default resources for network libraries. Other GH200 production vClusters have adopted netstacks as default.

    !!! note "Uenv"
    - Upgrade uenv from version 9.2.0 to 10.0.1.
    - Features:
        - TOML configuration format and improved repository management: multiple named repositories can be configured and selected by name.
        - Default views: uenv images can declare a view to load automatically when no --view flag is given.
        - Advanced Slurm workflows: the --uenv-passthrough flag controls whether a loaded uenv is forwarded to nested srun, sbatch, or salloc calls.
        - New global --system flag to override the cluster name on the CLI (e.g. uenv --system='*' image find).
        - Improved bash completion for uenv labels and file paths.
    - Fixes:
        - Changed a hard error to a warning when image metadata is not attached in the registry.
        - Fixed a latent bug parsing date strings in image metadata.
    - [uenv changelog][ref-uenv-release-notes-v10.0]

??? change "2025-05-21"
    Minor enhancements to system configuration have been applied.
    These changes should reduce the frequency of compute nodes being marked as `NOT_RESPONDING` by the workload manager, while we continue to investigate the issue.

### Known issues

