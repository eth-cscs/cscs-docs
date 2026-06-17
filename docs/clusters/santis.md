[](){#ref-cluster-santis}
# Santis

Santis is an Alps cluster that provides GPU accelerators and file systems designed to meet the needs of climate and weather models for the [CWP][ref-platform-cwp].

## Cluster specification

### Compute nodes

Santis consists of around 430 [Grace-Hopper nodes][ref-alps-gh200-node].

The number of nodes can change when nodes are added or removed from other clusters on Alps.

There are four login nodes, labelled `santis-ln00[1-4]`.
You will be assigned to one of the four login nodes when you ssh onto the system, from where you can edit files, compile applications and start simulation jobs.

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|-----------------| ----------------- | ---------- |
| [gh200][ref-alps-gh200-node] | 430 | 1,720      | 1,720 |

### Storage and file systems

Santis uses the [CWP filesystems and storage policies][ref-cwp-storage].

## Getting started

### Logging into Santis

To connect to Santis via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to santis using `ssh santis`.
    ```
    Host santis
        HostName santis.alps.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```

### Software

CSCS and the user community provide software environments tailored to  [uenv][ref-uenv] are also available on Santis.

Currently, the following uenv are provided for the climate and weather community

* `icon/25.1`
* `climana/25.1`

In addition to the climate and weather uenv, all of the

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

It is also possible to use HPC containers on Santis:

* Jobs using containers can be easily set up and submitted using the [container engine][ref-container-engine].
* To build images, see the [guide to building container images on Alps][ref-build-containers].


## Running jobs on Santis

### Slurm

Santis uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

There are two [Slurm partitions][ref-slurm-partitions] on the system:

* the `normal` partition is for all production workloads.
* the `debug` partition can be used to access a small allocation for up to 30 minutes for debugging and testing purposes.
* the `xfer` partition is for [internal data transfer][ref-data-xfer-internal] at CSCS.

| name | nodes  | max nodes per job | time limit |
| --   | --     | --                | -- |
| `normal` | 1266       | -    | 24 hours |
| `debug`  | 32         | 2    | 30 minutes |
| `xfer`   | 2          | 1    | 24 hours |

* nodes in the `normal` and `debug` partitions are not shared
* nodes in the `xfer` partition can be shared

See the Slurm documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

### FirecREST

Santis can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/ml/firecrest/v2` API endpoint.

!!! warning "The FirecREST v1 API is still available, but deprecated"

## Maintenance and status

### Scheduled maintenance

Wednesday morning 8-12 CET is reserved for periodic updates, with services potentially unavailable during this timeframe. If the queues must be drained (redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, and on the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2026-06-17"
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
        - AWS OFI NCCL hook: NCCL, CXI and OFI evnrionment variables are now aligned with those set in Alps Extended Images
        - PMIx hook: Use PMIx environment variables instead of `scontrol` call to determine bind mount paths(reflects change in upstream Enroot code)
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
    These changes should reduce the frequency of compute nodes being marked as `NOT_RESPONDING` by the workload manager, while we continue to investigate the issue

??? change "2025-03-05 container engine updated"
    now supports better containers that go faster. Users do not to change their workflow to take advantage of these updates.

??? change "2024-10-07 old event"
    this is an old update. Use `???` to automatically fold the update.

### Known issues

