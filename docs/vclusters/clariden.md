[](){#ref-cluster-clariden}
# Clariden

Clariden is an Alps cluster that provides GPU accelerators and file systems designed to meet the needs of machine learning workloads in the [MLP][ref-platform-mlp].

## Cluster Specification

### Compute Nodes

Clariden consists of ~1200 [Grace-Hopper nodes][ref-alps-gh200-node].

| node type | number of nodes | total CPU sockets | total GPUs |
|-----------|--------| ----------------- | ---------- |
| [gh200][ref-alps-gh200-node] | 1,200 | 4,800 | 4,800 |

!!! note
    The size of the cluster can change.


Most nodes are in the [`normal` slurm partition][ref-slurm-partition-normal], while a few nodes are in the [`debug` partition][ref-slurm-partition-debug].

### File Systems and Storage

The scratch filesystem is hosted on [IOPStore][ref-storage-iopstor], but also the capacity storage [Capstor][ref-storage-capstor] is mounted at `/capstor/scratch/cscs`.
The variables `STORE` and are not set on Clariden.
The home directory is hosted on [VAST][ref-storage-vast].

As usual, an overview of your quota on the different filesystems, can be obtained by the `quota` command.

!!! todo "quota docs"

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

Clariden can also be accessed using [FircREST][ref-firecrest] at the `https://api.cscs.ch/ml/firecrest/v1` API endpoint.

### Software

Users are encouraged to use containers on Clariden.

* Jobs using containers can be easily set up and submitted using the [container engine][ref-container-engine].
* To build images, see the [guide to building container images on Alps][ref-build-containers].

Alternatively, [uenv][ref-tool-uenv] are also available on Clariden. Currently the only uenv that is deployed on Clariden is [prgenv-gnu][ref-uenv-prgenv-gnu].

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

Clariden uses [SLURM][slurm] as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

See detailed instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

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

