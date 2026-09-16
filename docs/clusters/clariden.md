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

Most nodes are in the [`normal` Slurm partition][ref-slurm-partition-normal], while a few nodes are in the [`debug` partition][ref-slurm-partition-debug].

### Storage and file systems

Clariden uses the [MLP filesystems and storage policies][ref-mlp-storage].

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
* The [Nvidia NGC Catalog](https://catalog.ngc.nvidia.com/containers) provides containers with pre-built ML software stacks:
    * **Recommended**: [Alps extended images][ref-software-extended-images] provided by CSCS are customized versions of NGC images optimized for the Alps network.
    * Or start with base images from the [Nvidia NGC Catalog](https://catalog.ngc.nvidia.com/containers), for example the [HPC](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc) and [PyTorch](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch) images --- note that you will have to use [container hooks][ref-ce-annotations] to get optimal network performance.

Alternatively, [uenv][ref-uenv] are also available on Clariden. Currently deployed on Clariden:

* [prgenv-gnu][ref-uenv-prgenv-gnu]
* [pytorch][ref-uenv-pytorch]

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

For detailed instructions and best practices with ML frameworks, please refer to the dedicated pages under [ML software][ref-software-ml].

## Running Jobs on Clariden

### Slurm

Clariden uses [Slurm][ref-slurm] as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

#### Partitions

There are six Slurm partitions on the system:

* the `highprio` partition is reserved for persons requiring a large number of nodes.
* the `preemptable` partition is for all production workloads, has access to the largest number of nodes, but its jobs might be stopped.
* the `normal` partition is for all production workloads, and its jobs cannot be stopped by highprio jobs.
* the `debug` partition is intended for short debugging and testing jobs. It is configured on top of the same node pool as `normal`, with tight per-user limits to keep it focused on its intended use case.
* the `low` partition is a low-priority partition, which might be available to projects having exhausted their credit early (downscaled resource).
* the `xfer` partition is for [internal and S3 data transfer][ref-data-xfer-internal] at CSCS.

| name          | nodes  | nodes per job | time limit |
| --            | --     | --                | -- |
| `highprio`    | several nodes | >128    | 24 hours |
| `preemptable` | most nodes | 1-128    | 24 hours |
| `normal`  | several nodes| 1-128 | 12 hours |
| `debug`  | most nodes (shared with `preemptable`) <br> plus a few dedicated | 1-4 | 1.5 node-hours |
| `low`    | most nodes (shared with `preemptable`) | 1-10    | 6 hours |
| `xfer`   | 2         | 1    | 24 hours |

* jobs in the `highprio`, `preemptable` `normal`, `debug`, and `low` partitions get exclusive use of their allocated nodes (one job per node)
* the `low` partition shares the exact same node pool as `normal`, while `debug` shares that pool *and* adds a small set of nodes dedicated to debugging: short debug jobs therefore always have capacity available, even when `preemptable` is full
* `preemptable` and  `normal`have the same priority, but preemptable can use more nodes
* because these partitions overlap, a node may belong to more than one of them at the same time
* nodes in the `xfer` partition can be shared

#### `highprio` partition

The `highprio` partition is usable only with the highprio qos, which is provided only to users needing to run large jobs and not abusing it.
It allows to use the resources more efficiently (smaller startup time).
Both partition and qos have to be set (`--partions=highprio` `--qos=highprio`).

#### Debug partition

Nodes in the `debug` queue have a 1.5 node-hour time limit. This means you could for example request 2 nodes for 45 minutes each, or 1 single node for the full time limit.

The `debug` partition has additional per-user limits enforced by its QoS:

* max 1 running job per user
* max 2 submitted jobs per user (1 running + 1 pending)
* max 90 node·minutes per job (e.g. 1 node × 90 min, 2 nodes × 45 min, or 4 nodes × 22 min)

The `debug` partition is scheduled at a higher priority than `normal`, so debug jobs are placed ahead of `normal` jobs in the queue and typically start sooner. Preemption is disabled, so debug jobs never interrupt running `normal` jobs: they simply use idle nodes as soon as these become available. The tight per-user limits make the partition unsuitable for production workloads while keeping it responsive for short debug sessions.

!!! warning "The `debug` partition is for debugging and testing only"
    The `debug` partition is reserved for short, interactive debugging and testing sessions, and must not be used to run production workloads or to otherwise circumvent the per-user limits.
    Usage of the partition is monitored: workloads that are not genuine debugging or testing will be flagged and reported.

#### `preemptable` partition

When using the `preemptable` partition
It is possible to handle the TERM signal in the sbatch script, for example with
```bash
#!/bin/bash
## use your account here
#SBATCH --account=csstaff
## setting a meaningful time-min ensures that this jobs can be scheduled efficiently
## also with backfill or reservations
#SBATCH --time-min=1:00
#SBATCH --time=10:00
## a name is nice to quickly find it in the queue
#SBATCH --job-name=preemptable
## the partition should be preemptable
#SBATCH --partition=preemptable

should_stop=
function stop_request()
{
   let should_stop="early_stop"
}
tstart=$(date +%s)
trap "stop_request" SIGTERM
for i in 1 2 3; do
  srun a_command_that_will_also_recieve_sigterm
  if [[ -n "\$should_stop" ]]; then
    echo "Stopping due to interrupt"
    break
  fi
done
tend=$(date +%s)
echo "script-preemptable-$SLURM_JOB_ID ended after $((tend-tstart)) $should_stop"
```
Some pytorch training scripts already implement something, and otherwise you can do it using [python signal module](https://docs.python.org/3/library/signal.html).

#### Requeueing

If a job is stopped to start a highprio jobs it is not automatically requeued unless you submit the job with the `--requeue` flag.
When requeued a job maintains its priority.

If you request requeuing you have to be careful about not overwriting files (for example file redirect >output).
The variable `$SLURM_RESTART_COUNT`can be used to disambiguate the file names between different runs (SLURM_JOB_ID will be the same).

See the Slurm documentation for instructions on how to run jobs on the [Grace-Hopper nodes][ref-slurm-gh200].

??? example "how to check the number of nodes on the system"
    You can check the size of the system by running the following command in the terminal:
    ```console
    $ sinfo --format "| %20R | %10D | %10s | %10l | %10A |"
    | PARTITION            | NODES      | JOB_SIZE   | TIMELIMIT  | NODES(A/I) |
    | debug                | 1384       | 1-4        | 1:30:00    | 1260/82    |
    | normal               | 1359       | 1-infinite | 12:00:00   | 1254/65    |
    | low                  | 1359       | 1-infinite | 1-00:00:00 | 1254/65    |
    | xfer                 | 2          | 1          | 1-00:00:00 | 2/0        |
    ```
    The last column shows the number of nodes that have been allocated in currently running jobs (`A`) and the number of jobs that are idle (`I`).

### FirecREST

Clariden can also be accessed using [FirecREST][ref-firecrest] at the `https://api.cscs.ch/ml/firecrest/v1` API endpoint.

## Maintenance and status

### Scheduled Maintenance

Wednesday morning 8-12 CET is reserved for periodic updates, with services potentially unavailable during this timeframe. If the queues must be drained (redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window. 

Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, and on the [CSCS status page](https://status.cscs.ch).

### Change log

!!! change "2026-08-26"
    !!! note "Login node limits"
        To enforce our [fair usage of shared resources][ref-policies-fair-use-login-node] policies, we have enabled limits on the login nodes.
        Please note that some limits apply to individual processes, while other limits apply to the sum of your running processes.
        In addition, each login session is pinned to a subset of the cores of the node.
        Agentic tools and VSCode might be affected by these limits.
        Compute intensive tasks will also be affected by the limits.
        Any compute intensive task that is beyond the limits should be submitted to a compute node.

    !!! note "Enforce performance cpufreq governor"
        Due to a bug the cpu frequency governor has not always been set to `performance`.
        This bug has been fixed and the frequency governor will always be set to `performance` (instead of the default `ondemand`)

    !!! note "Container Engine"
        - Updated Container Engine to v26.08.1
        - Podman-5.8.6
        - NVIDIA Container Toolkit to 1.20.0
        - crun 1.29.1
        - sarusctl 0.6.0
        - Skybox 0.3.0
        - Sarus Suite Performance Extensions 26.08.1
        - The default netstack artifact version is now 26.08.1.
          There are no software changes: only the naming format of the variants has changed.
    
    !!! note "OS updates"
        - Kernel update to solve CVEs
        - VAST client update to 4.5.8

    !!! note "New file system"
        The Lustre file system `/iopsstor/datacache/cscs` is now mounted on the compute nodes and on the nodes of the `xfer` partition.

??? change "2025-03-05 container engine updated"
    now supports better containers that go faster. Users do not to change their workflow to take advantage of these updates.

??? change "2024-10-07 old event"
    this is an old update. Use `???` to automatically fold the update.

### Known issues

