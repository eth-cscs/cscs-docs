# Besso

Besso is a small Alps cluster that provides development resources for porting software for the [SKA project](<https://www.skao.int/>). It is provided as is, without the same level of support as the main platform clusters.

### Storage and file systems

Besso uses the HPCP filesystems and storage policies, except that `$SCRATCH` points to the old HPCP scratch on Capstor (`$SCRATCH_OLD` on the other HPCP clusters), instead of Ritom.

The file systems provided on Besso, the environment variables that point to them, and the Alps storage system that hosts each one:

| Variable | File system | Path | Storage | Type |
| --- | --- | --- | --- | --- |
| `$HOME` | Home | `/users/$USER` | Vadret | VAST |
| `$SCRATCH` | Scratch | `/capstor/scratch/cscs/$USER` | Capstor | Lustre |
| `$STORE`, `$PROJECT` | Store | `/capstor/store/cscs/<customer>/<group_id>` | Capstor | Lustre |

## Getting started

### Logging into Besso

To connect to Besso via SSH, first refer to the ssh guide.

> [!NOTE]
>
> **`~/.ssh/config`**
>
> Add the following to your SSH configuration to enable you to directly connect to besso using `ssh besso`.
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

Instead, the prgenv-gnu programming environment is provided for the both the a100 and mi200 node types.

#### Containers

Besso supports container workloads using the Container Engine.

To build images, see the guide to building container images on Alps.

## Running jobs on Besso

### Slurm

Besso uses Slurm as the workload manager, which is used to launch and monitor workloads on compute nodes.

There are multiple Slurm partitions on the system:

- the `a100` partition contains NVIDIA A100 GPU nodes
- the `mi200` partition contains AMD Mi250x GPU nodes
- the `normal` partition contains all of the nodes in the system.

| Partition | Nodes | Max nodes/job | Default time | Max time |
| --- | --- | --- | --- | --- |
| `normal` (default) | 4 | unlimited | 01:00:00 | 1-00:00:00 |
| `a100` | 2 | unlimited | 01:00:00 | 1-00:00:00 |
| `mi200` | 2 | unlimited | 01:00:00 | 1-00:00:00 |

The hardware available in each partition, including the Slurm features that can be selected with `--constraint`:

| Partition | Nodes | Node type | Features |
| --- | --- | --- | --- |
| `normal` | 2 | a100 | none |
| `normal` | 2 | mi200 | none |
| `a100` | 2 | a100 | none |
| `mi200` | 2 | mi200 | none |

> [!NOTE]
>
> **Default MPI plugin**
>
> The default MPI plugin on Besso is `cray_shasta`. This plugin is correct for applications that use Cray MPICH, for example applications in uenv. Applications that use OpenMPI or MPICH must set `--mpi=pmix` or `--mpi=pmi2`.

See the Slurm documentation for instructions on how to run jobs.

### FirecREST

Besso can also be accessed using FirecREST at the `https://api.cscs.ch/mwa/firecrest/v2` API endpoint.

## Maintenance and status

There is no regular scheduled maintenance for this system.
