[](){#ref-cluster-clariden}
# Clariden

Clariden is an Alps cluster that provides GPU accelerators and file systems designed to meet the needs of machine learning workloads in the [MLP][ref-platform-mlp].

## Cluster Specification

### Compute Nodes

Clariden consists of around 1200 [Grace-Hopper nodes][ref-alps-gh200-node].
The number of nodes can change when nodes are added or removed from other clusters on Alps.

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|--------| ----------------- | ---------- |
| [gh200][ref-alps-gh200-node] | 1,200 | 4,800 | 4,800 |

Most nodes are in the [`normal` slurm partition][ref-slurm-partition-normal], while a few nodes are in the [`debug` partition][ref-slurm-partition-debug].

### File Systems and Storage

There are three main file systems mounted on Clariden and Bristen.

| type |mount | filesystem |
| -- | -- | -- |
| Home | /users/$USER | [VAST][ref-alps-vast] |
| Scratch | `/iopstor/scratch/cscs/$USER` | [Iopstor][ref-alps-iopstor] |
| Project | `/capstor/store/cscs/swissai/<project>` | [Capstor][ref-alps-capstor] |

#### Home

Every user has a home path (`$HOME`) mounted at `/users/$USER` on the [VAST][ref-alps-vast] filesystem.
The home directory has 50 GB of capacity, and is intended for configuration, small software packages and scripts.

#### Scratch

Scratch filesystems provide temporary storage for high-performance I/O for executing jobs.
Use scratch to store datasets that will be accessed by jobs, and for job output.
Scratch is per user - each user gets separate scratch path and quota.

* The environment variable `SCRATCH=/iopstor/scratch/cscs/$USER` is set automatically when you log into the system, and can be used as a shortcut to access scratch.

!!! warning "scratch cleanup policy"
    Files that have not been accessed in 30 days are automatically deleted.

    **Scratch is not intended for permanant storage**: transfer files back to the capstor project storage after job runs.

!!! note
    There is an additional scratch path mounted on [Capstor][ref-alps-capstor] at `/capstor/scratch/cscs/$USER`, however this is not reccomended for ML workloads for performance reasons.

### Project

Project storage is backed up, with no cleaning policy: it provides intermediate storage space for datasets, shared code or configuration scripts that need to be accessed from different vClusters.
Project is per project - each project gets a project folder with project-specific quota.

* if you need additional storage, ask your PI to contact the CSCS service managers Fawzi or Nicholas.
* hard limits on capacity and inodes prevent users from writing to project if the quota is reached - you can check quota and available space by running the [`quota`][ref-storage-quota] command on a login node or ela 
* it is not recommended to write directly to the project path from jobs.

## Getting started

### Logging into Clariden

To connect to Clariden via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to clariden using `ssh clariden`.
    ```
    Host clariden
        HostName clariden.alps.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```
### Software

Users are encouraged to use containers on Clariden.

* Jobs using containers can be easily set up and submitted using the [container engine][ref-container-engine].
* To build images, see the [guide to building container images on Alps][ref-build-containers].

Alternatively, [uenv][ref-uenv] are also available on Clariden. Currently the only uenv that is deployed on Clariden is [prgenv-gnu][ref-uenv-prgenv-gnu].

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

## Running Jobs on Clariden

### SLURM

Clariden uses [SLURM][ref-slurm] as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

There are two slurm partitions on the system:

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

See the SLURM documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

??? example "how to check the number of nodes on the system"
    You can check the size of the system by running the following command in the terminal:
    ```terminal
    > sinfo --format "| %20R | %10D | %10s | %10l | %10A |"
    | PARTITION            | NODES      | JOB_SIZE   | TIMELIMIT  | NODES(A/I) |
    | debug                | 32         | 1-2        | 30:00      | 3/29       |
    | normal               | 1266       | 1-infinite | 1-00:00:00 | 812/371    |
    | xfer                 | 2          | 1          | 1-00:00:00 | 1/1        |
    ```
    The last column shows the number of nodes that have been allocted in currently running jobs (`A`) and the number of jobs that are idle (`I`).

### FirecREST

Clariden can also be accessed using [FircREST][ref-firecrest] at the `https://api.cscs.ch/ml/firecrest/v1` API endpoint.

## Maintenance and status

### Scheduled Maintenance

Wednesday morning 8-12 CET is reserved for periodic updates, with services potentially unavailable during this timeframe. If the queues must be drained (redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, and on the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2025-03-05 container engine updated"
    now supports better containers that go faster. Users do not to change their workflow to take advantage of these updates.

??? change "2024-10-07 old event"
    this is an old update. Use `???` to automatically fold the update.

### Known issues

