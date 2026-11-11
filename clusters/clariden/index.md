# Clariden

Clariden is an Alps cluster that provides GPU accelerators and file systems designed to meet the needs of machine learning workloads in the [MLP](<https://docs.cscs.ch/platforms/mlp/index.md#machine-learning-platform> "Machine learning platform").

## Cluster Specification

### Compute Nodes

Clariden consists of [Grace-Hopper nodes](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes"). The number of nodes can change when nodes are added or removed from other clusters on Alps.

| Node type | Memory | Nodes | CPU sockets | GPUs |
| --- | --- | --- | --- | --- |
| [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") | – | 1332 | 5328 | 5328 |

In addition, two [zen2](<https://docs.cscs.ch/alps/hardware/index.md#amd-rome-cpu-nodes> "AMD Rome CPU Nodes") nodes are reserved for data transfer in the `xfer` partition, and cannot run compute jobs.

Most nodes are in the [`normal` Slurm partition](<https://docs.cscs.ch/running/slurm/index.md#normal-partition> "Normal partition"), while a few nodes are in the [`debug` partition](<https://docs.cscs.ch/running/slurm/index.md#debug-partition> "Debug partition").

### Storage and file systems

Clariden uses the [MLP filesystems and storage policies](<https://docs.cscs.ch/platforms/mlp/index.md#file-systems-and-storage> "File Systems and Storage").

## Getting started

### Logging into Clariden

To connect to Clariden via SSH, first refer to the [ssh guide](<https://docs.cscs.ch/access/ssh/index.md#using-ssh> "Using SSH").

> [!NOTE]
>
> **`~/.ssh/config`**
>
> Add the following to your [SSH configuration](<https://docs.cscs.ch/access/ssh/index.md#adding-ela-as-a-jump-host-in-ssh-configuration> "Adding Ela as a jump host in SSH configuration") to enable you to directly connect to clariden using `ssh clariden`.
>
> ```text
> Host clariden
>     HostName clariden.alps.cscs.ch
>     ProxyJump ela
>     User cscsusername
>     IdentityFile ~/.ssh/cscs-key
>     IdentitiesOnly yes
> ```

### Software

Users are encouraged to use containers on Clariden.

- Jobs using containers can be easily set up and submitted using the [container engine](<https://docs.cscs.ch/software/container-engine/index.md#container-engine> "Container Engine").
- To build images, see the [guide to building container images on Alps](<https://docs.cscs.ch/build-install/containers/index.md#building-container-images-on-alps> "Building container images on Alps").
- The [Nvidia NGC Catalog](<https://catalog.ngc.nvidia.com/containers>) provides containers with pre-built ML software stacks:

  - **Recommended**: [Alps extended images](<https://docs.cscs.ch/software/alps-extended-images/index.md#alps-extended-images> "Alps Extended Images") provided by CSCS are customized versions of NGC images optimized for the Alps network.
  - Or start with base images from the [Nvidia NGC Catalog](<https://catalog.ngc.nvidia.com/containers>), for example the [HPC](<https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nvhpc>) and [PyTorch](<https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch>) images — note that you will have to use [container hooks](<https://docs.cscs.ch/software/container-engine/resource-hook/index.md#annotations> "Annotations") to get optimal network performance.

Alternatively, [uenv](<https://docs.cscs.ch/software/uenv/index.md#uenv>) are also available on Clariden. Currently deployed on Clariden:

- [prgenv-gnu](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>)
- [pytorch](<https://docs.cscs.ch/software/ml/pytorch/index.md#running-pytorch-with-a-uenv> "Running PyTorch with a uenv")

> [!NOTE]
>
> **using uenv provided for other clusters**
>
> You can run uenv that were built for other Alps clusters using the `@` notation. For example, to use uenv images for [daint](<https://docs.cscs.ch/clusters/daint/index.md#daint> "Daint"):
>
> ```bash
> # list all images available for daint
> uenv image find @daint
>
> # download an image for daint
> uenv image pull namd/3.0:v3@daint
>
> # start the uenv
> uenv start namd/3.0:v3@daint
> ```

For detailed instructions and best practices with ML frameworks, please refer to the dedicated pages under [ML software](<https://docs.cscs.ch/software/ml/index.md#machine-learning-applications-and-frameworks> "Machine learning applications and frameworks").

## Running Jobs on Clariden

### Slurm

Clariden uses [Slurm](<https://docs.cscs.ch/running/slurm/index.md#slurm>) as the workload manager, which is used to launch and monitor distributed workloads, such as training runs.

> [!WARNING]
>
> **Clariden has no default MPI plugin**
>
> On Clariden, Slurm does not select an [MPI plugin](<https://docs.cscs.ch/running/slurm/index.md#mpi-plugins> "MPI plugins") by default (`MpiDefault` is `(null)`). Set `--mpi` or `SLURM_MPI_TYPE` for each `srun` command that starts an MPI application. For example, use `--mpi=cray_shasta` for Cray MPICH in uenv, and `--mpi=pmix` for OpenMPI. If you do not set a plugin, each rank starts as a separate MPI job with one rank, and Slurm does not report an error. Applications that do not use MPI do not need this setting.

#### Partitions

There are six Slurm partitions on the system:

- the `highprio` partition is reserved for persons requiring a large number of nodes (jobs of more than 128 nodes).
- the `preemptable` partition is for all production workloads, has access to the largest number of nodes, but its jobs might be stopped.
- the `normal` partition is for all production workloads, and its jobs cannot be stopped by highprio jobs.
- the `debug` partition is intended for short debugging and testing jobs. It is configured on top of the same node pool as `normal`, with tight per-user limits to keep it focused on its intended use case.
- the `low` partition is a low-priority partition, which might be available to projects having exhausted their credit early (downscaled resource).
- the `xfer` partition is for [internal and S3 data transfer](<https://docs.cscs.ch/storage/transfer/index.md#internal-transfer> "Internal Transfer") at CSCS.

| Partition | Nodes | Max nodes in use | Max nodes/job | Default time | Max time |
| --- | --- | --- | --- | --- | --- |
| `normal` (default) | 1308 | 400 | unlimited | 01:00:00 | 12:00:00 |
| `highprio` | 1308 | 780 | unlimited | 01:00:00 | 3-00:00:00 |
| `low` | 1308 | \- | 10 | 01:00:00 | 06:00:00 |
| `preemptable` | 1308 | \- | unlimited | 01:00:00 | 1-00:00:00 |
| `debug` | 1332 | \- | 4 | 00:45:00 | 01:30:00 (90 node-minutes/job) |
| `xfer` | 2 | \- | 1 | 06:00:00 | 1-00:00:00 |

> [!NOTE]
>
> **Keep jobs in `normal` and `preemptable` to 128 nodes or fewer**
>
> The suggested largest job in the `normal` and `preemptable` partitions is 128 nodes, so that the system is used efficiently. Slurm accepts larger jobs in these partitions, but they can wait a long time in the queue before enough nodes are free at the same time, even with backfill, and the nodes that are kept free for them are unavailable for other jobs while they wait. The `highprio` partition is reserved for jobs larger than 128 nodes, and is available to selected projects.

Most partitions are configured on the same pool of nodes. The jobs in `normal` and `highprio` are also limited by a [Slurm QoS](<https://docs.cscs.ch/running/slurm/index.md#qos-limits> "QoS limits") to the number of nodes in *Max nodes in use*, which all the running jobs of the partition share. These limits are set so that `normal` and `highprio`, together with a reserve for nodes that are down and for interactive use, add up to the whole system. They may be adjusted: the table shows the current values. When the limit of a partition is reached, the jobs waiting in it are shown by `squeue` with the reason `QOSGrpNodeLimit`.

> [!WARNING]
>
> **Jobs larger than *Max nodes in use* never start**
>
> A job in `normal` or `highprio` that requests more nodes than *Max nodes in use* is accepted, but never starts: it stays pending with the reason `QOSGrpNodeLimit`. Cancel it with `scancel`, and submit it again with fewer nodes.

- jobs in the `highprio`, `preemptable` `normal`, `debug`, and `low` partitions get exclusive use of their allocated nodes (one job per node)
- the `low` partition shares the exact same node pool as `normal`, while `debug` shares that pool *and* adds a small set of nodes dedicated to debugging: short debug jobs therefore always have capacity available, even when `preemptable` is full
- `preemptable` and `normal`have the same priority, but preemptable can use more nodes
- because these partitions overlap, a node may belong to more than one of them at the same time
- nodes in the `xfer` partition can be shared

The hardware available in each partition, including the [Slurm features](<https://docs.cscs.ch/running/slurm/index.md#slurm-features>) that can be selected with `--constraint`:

| Partition | Nodes | Node type | Features |
| --- | --- | --- | --- |
| `normal` | 1308 | [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") | [vboost](<https://docs.cscs.ch/running/slurm/index.md#nvidia-vboost> "NVIDIA vboost"), [thp](<https://docs.cscs.ch/running/slurm/index.md#transparent-hugepages> "Transparent hugepages") |
| `highprio` | 1308 | [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") | [vboost](<https://docs.cscs.ch/running/slurm/index.md#nvidia-vboost> "NVIDIA vboost"), [thp](<https://docs.cscs.ch/running/slurm/index.md#transparent-hugepages> "Transparent hugepages") |
| `low` | 1308 | [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") | [vboost](<https://docs.cscs.ch/running/slurm/index.md#nvidia-vboost> "NVIDIA vboost"), [thp](<https://docs.cscs.ch/running/slurm/index.md#transparent-hugepages> "Transparent hugepages") |
| `preemptable` | 1308 | [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") | [vboost](<https://docs.cscs.ch/running/slurm/index.md#nvidia-vboost> "NVIDIA vboost"), [thp](<https://docs.cscs.ch/running/slurm/index.md#transparent-hugepages> "Transparent hugepages") |
| `debug` | 1332 | [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") | [vboost](<https://docs.cscs.ch/running/slurm/index.md#nvidia-vboost> "NVIDIA vboost"), [thp](<https://docs.cscs.ch/running/slurm/index.md#transparent-hugepages> "Transparent hugepages") |
| `xfer` | 2 | [zen2 256 GB](<https://docs.cscs.ch/alps/hardware/index.md#amd-rome-cpu-nodes> "AMD Rome CPU Nodes") | none |

#### `highprio` partition

The `highprio` partition is usable only with the highprio qos, which is provided only to users needing to run large jobs and not abusing it. It allows to use the resources more efficiently (smaller startup time). Access is restricted to selected projects. Both partition and qos have to be set (`--partition=highprio` `--qos=highprio`).

#### `debug` partition

Nodes in the `debug` queue have a 1.5 node-hour time limit. This means you could for example request 2 nodes for 45 minutes each, or 1 single node for the full time limit.

The `debug` partition has additional per-user limits enforced by its QoS:

- max 1 running job per user
- max 2 submitted jobs per user (1 running + 1 pending)
- max 90 node·minutes per job (e.g. 1 node × 90 min, 2 nodes × 45 min, or 4 nodes × 22 min)

The `debug` partition is scheduled at a higher priority than `normal`, so debug jobs are placed ahead of `normal` jobs in the queue and typically start sooner. Preemption is disabled, so debug jobs never interrupt running `normal` jobs: they simply use idle nodes as soon as these become available. The tight per-user limits make the partition unsuitable for production workloads while keeping it responsive for short debug sessions.

> [!WARNING]
>
> **The `debug` partition is for debugging and testing only**
>
> The `debug` partition is reserved for short, interactive debugging and testing sessions, and must not be used to run production workloads or to otherwise circumvent the per-user limits. Usage of the partition is monitored: workloads that are not genuine debugging or testing will be flagged and reported.

#### `preemptable` partition

When using the `preemptable` partition It is possible to handle the TERM signal in the sbatch script, for example with

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

Some pytorch training scripts already implement something, and otherwise you can do it using [python signal module](<https://docs.python.org/3/library/signal.html>).

#### Automatic requeueing

If a job is stopped to start a highprio jobs it is not automatically requeued unless you submit the job with the `--requeue` flag. When requeued a job maintains its priority.

If you request requeuing you have to be careful about not overwriting files (for example file redirect \>output). The variable `$SLURM_RESTART_COUNT`can be used to disambiguate the file names between different runs (SLURM\_JOB\_ID will be the same).

See the Slurm documentation for instructions on how to run jobs on the [Grace-Hopper nodes](<https://docs.cscs.ch/running/slurm/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes").

> [!NOTE]
>
> **how to check the number of nodes on the system**
>
> You can check the size of the system by running the following command in the terminal:
>
> ```console
> $ sinfo --format "| %20R | %10D | %10s | %10l | %10A |"
> | PARTITION            | NODES      | JOB_SIZE   | TIMELIMIT  | NODES(A/I) |
> | debug                | 1384       | 1-4        | 1:30:00    | 1260/82    |
> | normal               | 1359       | 1-infinite | 12:00:00   | 1254/65    |
> | low                  | 1359       | 1-infinite | 1-00:00:00 | 1254/65    |
> | xfer                 | 2          | 1          | 1-00:00:00 | 2/0        |
> ```
>
> The last column shows the number of nodes that have been allocated in currently running jobs (`A`) and the number of jobs that are idle (`I`).

### FirecREST

Clariden can also be accessed using [FirecREST](<https://docs.cscs.ch/access/firecrest/index.md#firecrest>) at the `https://api.cscs.ch/ml/firecrest/v2` API endpoint.

## Maintenance and status

### Scheduled Maintenance

Wednesday morning 8-12 CET is reserved for periodic updates, with services potentially unavailable during this timeframe. If the queues must be drained (redeployment of node images, rebooting of compute nodes, etc) then a Slurm reservation will be in place that will prevent jobs from running into the maintenance window.

Exceptional and non-disruptive updates may happen outside this time frame and will be announced to the users mailing list, and on the [CSCS status page](<https://status.cscs.ch>).

### Change log

> [!NOTE]
>
> **2026-08-26**
>
> > **Login node limits**
> >
> > To enforce our [fair usage of shared resources](<https://docs.cscs.ch/policies/shared/index.md#login-nodes> "Login nodes") policies, we have enabled limits on the login nodes. Please note that some limits apply to individual processes, while other limits apply to the sum of your running processes. In addition, each login session is pinned to a subset of the cores of the node. Agentic tools and VSCode might be affected by these limits. Compute intensive tasks will also be affected by the limits. Any compute intensive task that is beyond the limits should be submitted to a compute node.
>
> > **Enforce performance cpufreq governor**
> >
> > Due to a bug the cpu frequency governor has not always been set to `performance`. This bug has been fixed and the frequency governor will always be set to `performance` (instead of the default `ondemand`)
>
> > **Container Engine**
> >
> > - Updated Container Engine to v26.08.1
> > - Podman-5.8.6
> > - NVIDIA Container Toolkit to 1.20.0
> > - crun 1.29.1
> > - sarusctl 0.6.0
> > - Skybox 0.3.0
> > - Sarus Suite Performance Extensions 26.08.1
> > - The default netstack artifact version is now 26.08.1. There are no software changes: only the naming format of the variants has changed.
>
> > **OS updates**
> >
> > - Kernel update to solve CVEs
> > - VAST client update to 4.5.8
>
> > **New file system**
> >
> > The Lustre file system `/iopsstor/datacache/cscs` is now mounted on the compute nodes and on the nodes of the `xfer` partition.

**2025-03-05 container engine updated**

now supports better containers that go faster. Users do not to change their workflow to take advantage of these updates.

**2024-10-07 old event**

this is an old update. Use `???` to automatically fold the update.

### Known issues
