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
    * [prgenv-gnu-openmpi][ref-uenv-prgenv-gnu-openmpi]
    * [julia][ref-uenv-julia]

</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-layer-group: __Tools__

    Provide tools for debugging and performance analysis.

    * [Linaro Forge][ref-uenv-linaro]
    * [Score-P][ref-devtools-vihps]

</div>

To list all uenv that are available on Santis, run `uenv image find`.

??? example "using uenv provided for other clusters"
    You can run uenv that were built for other Alps clusters using the `@` notation.
    For example, to use uenv images for [daint][ref-cluster-daint]:
    ```bash
    # list all images available for daint
    uenv image find @daint

    # download an image for daint
    uenv image pull namd/3.0:v3@daint

    # start the uenv
    uenv start --view=namd namd/3.0:v3@daint
    ```

[](){#ref-cluster-santis-containers}
#### Containers

Santis supports container workloads using the [container engine][ref-container-engine].

To build images, see the [guide to building container images on Alps][ref-build-containers].

## Running jobs on Santis

### Slurm

Santis uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor compute-intensive workloads.

There are four [Slurm partitions][ref-slurm-partitions] on the system:

* the `normal` partition is for standard compute, and is the default.
* the `debug` partition is for short testing.
* the `low` partition is for overflow, and for projects that have exhausted their quota.
* the `xfer` partition is for [internal data transfer][ref-data-xfer-internal] at CSCS.

<!--begin no spell check-->
--8<-- "probes/generated/santis/partitions.md"

--8<-- "probes/generated/santis/stamp.md"
<!--end no spell check-->

Slurm uses the default time when a job does not set `--time`.

The hardware available in each partition, including the [Slurm features][ref-slurm-features] that can be selected with `--constraint`:

<!--begin no spell check-->
--8<-- "probes/generated/santis/nodetypes.md"
<!--end no spell check-->

!!! note "Default MPI plugin"
    The default [MPI plugin][ref-slurm-mpi] on Santis is `cray_shasta`.
    This plugin is correct for applications that use Cray MPICH, for example applications in uenv.
    Applications that use OpenMPI or MPICH must set `--mpi=pmix` or `--mpi=pmi2`.

[](){#ref-cluster-santis-sharing}
#### Node sharing and GPU requests

All GH200 partitions on Santis use [node sharing][ref-slurm-sharing].

By default MPI ranks on Santis are given a single CPU core and no GPUs.

??? example "By default each rank gets one core and no GPUs"
    ```console title="requesting two MPI ranks gives one core per rank"
    $ srun --ntasks=2 --account=p1234 ./affinity.cuda
    GPU affinity test for 2 MPI ranks
    rank      0 @ nid005110
     cores   : 0
    rank      1 @ nid005110
     cores   : 72
    ```

Slurm is configured to allocate resources in units of one GH200 chip for each GPU that the job requests.
The GPUs assigned to each rank are configured using the `--gpus-per-task` and `--gpus-per-node` slurm flags:

* 1 GPU is a whole Grace-Hopper super-chip: 72 CPU cores, one GPU (96 GB HBM), and 115 GB host memory by default.

??? example "allocating GPUs to ranks"

    ```console title="One GPU and 72 cores for `--gpus-per-task=1`"
    $ srun --ntasks=1 --gpus-per-task=1 --account=p1234 ./affinity.cuda
    srun: job 898836 queued and waiting for resources
    srun: job 898836 has been allocated resources
    GPU affinity test for 1 MPI ranks
    rank      0 @ nid005108
     cores   : [216:287]
     gpu   0 : GPU-cc201279-83e4-96d2-ad01-87b35f2a7bc7
    ```

    ```console title="Separate GPU and 72 cores for two ranks on the same node"
    $ srun --ntasks=2 --gpus-per-task=1 --account=p1234 ./affinity.cuda
    GPU affinity test for 2 MPI ranks
    rank      0 @ nid005012
     cores   : [0:71]
     gpu   0 : GPU-5b19f465-b587-4b9e-31c4-60bf65296733
    rank      1 @ nid005012
     cores   : [72:143]
     gpu   0 : GPU-ac10eafa-4462-5be4-152e-7b92f9780b80
    ```

    Use the `--gpus-per-node` flag when MPI ranks need to share the same GPUs.

    ```console title="Two ranks share 4 gh200 (GPU and CPU cores) on the same node"
    $ srun --ntasks=2 --gpus-per-node=4 --account=p1234 ./affinity.cuda
    GPU affinity test for 2 MPI ranks
    rank      0 @ nid005303
     cores   : [0:287]
     gpu   0 : GPU-29180fbd-a8f8-0502-2545-5787e427361b
     gpu   1 : GPU-47948342-2073-f024-84a1-db54c3084812
     gpu   2 : GPU-16d309ce-af9d-6814-032a-d5109f6809d9
     gpu   3 : GPU-3fa8aa36-b463-83be-edab-f7b281c0d359
    rank      1 @ nid005303
     cores   : [0:287]
     gpu   0 : GPU-29180fbd-a8f8-0502-2545-5787e427361b
     gpu   1 : GPU-47948342-2073-f024-84a1-db54c3084812
     gpu   2 : GPU-16d309ce-af9d-6814-032a-d5109f6809d9
     gpu   3 : GPU-3fa8aa36-b463-83be-edab-f7b281c0d359
    ```

!!! warning "Charge for shared nodes"
    Your project is charged for the whole node, including when a job uses only part of it.
    For example, a job that uses one GPU is charged one node hour for each hour that it runs.
    See the [resource allocation policies][ref-policies].

[](){#ref-cluster-santis-p2p}
#### Multi-GPU jobs with P2P/IPC

Because device isolation is enforced via cgroups, multi-GPU jobs that rely on GPU P2P/IPC (for example MPI across GPUs on the same node) must add to the `srun` command (NB: this does not work being specified in the `#SBATCH` definition block):

```bash title="srun flag for GPU P2P/IPC"
--gres-flags=allow-task-sharing
```

This keeps all GPUs allocated to a job visible to all tasks of that job while preserving per-task `CUDA_VISIBLE_DEVICES` bindings. Without this flag, intra-node GPU-GPU communication will fail.

!!! info
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

[](){#ref-cluster-santis-job-limits}
#### Concurrent job limit

Slurm limits the number of jobs that each user can run at the same time:

| Partition          | QoS        | Running jobs per user | Submitted jobs per user |
| --                 | --         | --                    | -- |
| `normal`, `debug`  | `normal`   | 20 (together)         | no limit |
| `low`              | `slowdown` | 10                    | 20 |

Jobs above the running limit wait in the queue until one of your running jobs finishes.
In the `low` partition, Slurm rejects new submissions when you already have 20 jobs (running or waiting) in that partition.

To show the current limits, run:

```console title="Show the job limits on Santis"
$ sacctmgr show qos normal,slowdown format=name,maxjobspu,maxsubmitpu
      Name MaxJobsPU MaxSubmitPU
---------- --------- -----------
    normal        20
  slowdown        10          20
```

See the Slurm documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

### FirecREST

Santis can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/cw/firecrest/v2` API endpoint.

!!! warning "The FirecREST v1 API is still available, but deprecated"

## Maintenance and status

### Scheduled maintenance

One Wednesday per month is reserved for planned maintenance (usually around the middle of the month, 8-12 CET), with services potentially unavailable during this timeframe. If the queues must be drained (redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window.

Exceptional and non-disruptive updates may happen outside this time frame and will be announced via the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2026-09-17"
    !!! note "Slurm updated to 25.05.9"
        - Slurm was updated from 25.05.8 to 25.05.9
    !!! note "Container Engine updated to v26.09.1"
        - General version updates
            - `fuse-overlayfs` updated for Podman 1.18
            - Parallax updated to 26.9.2
        - Enroot updates
            - Netstack version and name settings are now ignored when not using artifacts
        - Sarus Suite (beta) updates
            - Read-only storage for Podman images changed to default to architecture-specific path
    !!! note "uenv tool updated to v10.1.0"
        - `uenv` updated from v10.0.1 to v10.1.0
        - This fixes an issue downloading images that need a token authentication

??? change "2026-08-26"
    ??? note "Login node limits"
        To enforce our [fair usage of shared resources][ref-policies-fair-use-login-node] policies, we have enabled limits on the login nodes.
        Please note that some limits apply to individual processes, while other limits apply to the sum of your running processes.
        Agentic tools and VSCode might be affected by these limits.
        Compute intensive tasks will also be affected by the limits.
        Any compute intensive task that is beyond the limits should be submitted to a compute node.

    ??? note "Slurm"
        - Enable node sharing on all GH200 compute partitions. Resources are allocated per GH200 chip: one requested GPU corresponds to 72 cores and 115 GB of host memory by default.
        - Introduce the `low` partition for overflow work and quota-exhausted projects.
        - Enforce a per-user limit on concurrently running jobs (see the current [job limits][ref-cluster-santis-job-limits]).
        - Enable the power capping feature on the GH200 nodes.
        - Multi-GPU jobs relying on intra-node P2P/IPC must add `--gres-flags=allow-task-sharing` to the `srun` command or `export SLURM_GRES_FLAGS=allow-task-sharing`.

    ??? warning "Known limitation"
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

