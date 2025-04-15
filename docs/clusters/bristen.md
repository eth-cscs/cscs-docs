[](){#ref-cluster-bristen}
# Bristen

Bristen is an Alps cluster that provides GPU accelerators and filesystems designed to meet the needs of machine learning workloads in the [MLP][ref-platform-mlp].

## Cluster Specification

### Compute Nodes
Bristen consists of 32 A100 nodes [NVIDIA A100 nodes][ref-alps-a100-node]. The number of nodes can change when nodes are added or removed from other clusters on Alps.

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|--------| ----------------- | ---------- |
| [a100][ref-alps-a100-node] | 32 | 32 | 128 |

Nodes are in the [`normal` slurm partition][ref-slurm-partition-normal].

### Storage and file systems

Bristen uses the [MLp filesystems and storage policies][ref-mlp-storage].

## Getting started

### Logging into Bristen

To connect to Bristen via SSH, first refer to the [ssh guide][ref-ssh].

!!! example "`~/.ssh/config`"
    Add the following to your [SSH configuration][ref-ssh-config] to enable you to directly connect to bristen using `ssh bristen`.
    ```
    Host bristen
        HostName bristen.alps.cscs.ch
        ProxyJump ela
        User cscsusername
        IdentityFile ~/.ssh/cscs-key
        IdentitiesOnly yes
    ```

### Software

Users are encouraged to use containers on Bristen.

* Jobs using containers can be easily set up and submitted using the [container engine][ref-container-engine].
* To build images, see the [guide to building container images on Alps][ref-build-containers].

## Running Jobs on Bristen

### SLURM

Bristen uses [SLURM][ref-slurm] as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

There is currently a single slurm partition on the system:

* the `normal` partition is for all production workloads.
    + nodes in this partition are not shared.

| name | nodes  | max nodes per job | time limit |
| --   | --     | --                | -- |
| `normal` | 32       | -    | 24 hours |

<!--
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
-->

### FirecREST

Bristen can also be accessed using [FircREST][ref-firecrest] at the `https://api.cscs.ch/ml/firecrest/v1` API endpoint.

### Scheduled Maintenance

Wednesday morning 8-12 CET is reserved for periodic updates, with services potentially unavailable during this timeframe. If the queues must be drained (redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, and on the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2025-03-05 container engine updated"
    now supports better containers that go faster. Users do not to change their workflow to take advantage of these updates.

### Known issues