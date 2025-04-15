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

### Storage and file systems

Clariden uses the [MLp filesystems and storage policies][ref-mlp-storage].

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
| `normal` | 1204       | -    | 24 hours |
| `debug`  | 24         | 2    | 1.5 node-hours |
| `xfer`   | 2          | 1    | 24 hours |

* nodes in the `normal` and `debug` partitions are not shared
* nodes in the `xfer` partition can be shared
* nodes in the `debug` queue have a 1.5 node-hour time limit. This means you could for example request 2 nodes for 45 minutes each, or 1 single node for the full time limit.

See the SLURM documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

??? example "how to check the number of nodes on the system"
    You can check the size of the system by running the following command in the terminal:
    ```console
    $ sinfo --format "| %20R | %10D | %10s | %10l | %10A |"
    | PARTITION            | NODES      | JOB_SIZE   | TIMELIMIT  | NODES(A/I) |
    | debug                | 32         | 1-2        | 30:00      | 3/29       |
    | normal               | 1266       | 1-infinite | 1-00:00:00 | 812/371    |
    | xfer                 | 2          | 1          | 1-00:00:00 | 1/1        |
    ```
    The last column shows the number of nodes that have been allocated in currently running jobs (`A`) and the number of jobs that are idle (`I`).

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

