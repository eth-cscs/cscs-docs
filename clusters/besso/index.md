# Besso

Besso is a small Alps cluster that provides development resources for porting software for the [SKA project](<https://www.skao.int/>). It is provided as is, without the same level of support as the main platform clusters.

### Storage and file systems

Besso uses the [HPCP filesystems and storage policies](<https://docs.cscs.ch/platforms/hpcp/index.md#file-systems-and-storage> "File systems and storage"), except that `$SCRATCH` points to the old HPCP scratch on [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) (`$SCRATCH_OLD` on the other HPCP clusters), instead of [Ritom](<https://docs.cscs.ch/alps/storage/index.md#ritom>).

The file systems provided on Besso, the environment variables that point to them, and the [Alps storage system](<https://docs.cscs.ch/alps/storage/index.md#alps-storage> "Alps Storage") that hosts each one:

| Variable | File system | Path | Storage | Type |
| --- | --- | --- | --- | --- |
| `$HOME` | [Home](<https://docs.cscs.ch/storage/filesystems/index.md#home>) | `/users/$USER` | [Vadret](<https://docs.cscs.ch/alps/storage/index.md#vadret>) | VAST |
| `$SCRATCH` | [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) | `/capstor/scratch/cscs/$USER` | [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) | [Lustre](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") |
| `$STORE`, `$PROJECT` | [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) | `/capstor/store/cscs/<customer>/<group_id>` | [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) | [Lustre](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") |

## Getting started

### Logging into Besso

To connect to Besso via SSH, first refer to the [ssh guide](<https://docs.cscs.ch/access/ssh/index.md#using-ssh> "Using SSH").

> [!NOTE]
>
> **`~/.ssh/config`**
>
> Add the following to your [SSH configuration](<https://docs.cscs.ch/access/ssh/index.md#adding-ela-as-a-jump-host-in-ssh-configuration> "Adding Ela as a jump host in SSH configuration") to enable you to directly connect to besso using `ssh besso`.
>
> ```text
> Host besso
>     HostName besso.vc.cscs.ch
>     ProxyJump ela
>     User cscsusername
>     IdentityFile ~/.ssh/cscs-key
>     IdentitiesOnly yes
> ```

### Software

#### uenv

Besso is a development and testing system, for which CSCS does not provide supported applications.

Instead, the [prgenv-gnu](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>) programming environment is provided for the both the [a100](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-a100-gpu-nodes> "NVIDIA A100 GPU Nodes") and [mi200](<https://docs.cscs.ch/alps/hardware/index.md#amd-mi250x-gpu-nodes> "AMD MI250x GPU Nodes") node types.

#### Containers

Besso supports container workloads using the [Container Engine](<https://docs.cscs.ch/software/container-engine/index.md#container-engine>).

To build images, see the [guide to building container images on Alps](<https://docs.cscs.ch/build-install/containers/index.md#building-container-images-on-alps> "Building container images on Alps").

## Running jobs on Besso

### Slurm

Besso uses [Slurm](<https://docs.cscs.ch/running/slurm/index.md#slurm>) as the workload manager, which is used to launch and monitor workloads on compute nodes.

There are multiple [Slurm partitions](<https://docs.cscs.ch/running/slurm/index.md#partitions> "Partitions") on the system:

- the `a100` partition contains [NVIDIA A100 GPU](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-a100-gpu-nodes> "NVIDIA A100 GPU Nodes") nodes
- the `mi200` partition contains [AMD Mi250x GPU](<https://docs.cscs.ch/alps/hardware/index.md#amd-mi250x-gpu-nodes> "AMD MI250x GPU Nodes") nodes
- the `normal` partition contains all of the nodes in the system.

| Partition | Nodes | Max nodes/job | Default time | Max time |
| --- | --- | --- | --- | --- |
| `normal` (default) | 4 | unlimited | 01:00:00 | 1-00:00:00 |
| `a100` | 2 | unlimited | 01:00:00 | 1-00:00:00 |
| `mi200` | 2 | unlimited | 01:00:00 | 1-00:00:00 |

The hardware available in each partition, including the [Slurm features](<https://docs.cscs.ch/running/slurm/index.md#slurm-features>) that can be selected with `--constraint`:

| Partition | Nodes | Node type | Features |
| --- | --- | --- | --- |
| `normal` | 2 | [a100](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-a100-gpu-nodes> "NVIDIA A100 GPU Nodes") | none |
| `normal` | 2 | [mi200](<https://docs.cscs.ch/alps/hardware/index.md#amd-mi250x-gpu-nodes> "AMD MI250x GPU Nodes") | none |
| `a100` | 2 | [a100](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-a100-gpu-nodes> "NVIDIA A100 GPU Nodes") | none |
| `mi200` | 2 | [mi200](<https://docs.cscs.ch/alps/hardware/index.md#amd-mi250x-gpu-nodes> "AMD MI250x GPU Nodes") | none |

> [!NOTE]
>
> **Default MPI plugin**
>
> The default [MPI plugin](<https://docs.cscs.ch/running/slurm/index.md#mpi-plugins> "MPI plugins") on Besso is `cray_shasta`. This plugin is correct for applications that use Cray MPICH, for example applications in uenv. Applications that use OpenMPI or MPICH must set `--mpi=pmix` or `--mpi=pmi2`.

See the Slurm documentation for instructions on how to [run jobs](<https://docs.cscs.ch/running/slurm/index.md#slurm> "Slurm").

### FirecREST

Besso can also be accessed using [FirecREST](<https://docs.cscs.ch/access/firecrest/index.md#firecrest>) at the `https://api.cscs.ch/mwa/firecrest/v2` API endpoint.

## Maintenance and status

There is no regular scheduled maintenance for this system.
