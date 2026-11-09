# Beverin

Beverin is an AMD-based GPU cluster for the purpose of testing and porting applications.

## Cluster Specification

### Login node

Beverin has one MI250X login node.

### Compute Nodes

Beverin consists of 13 MI250X and 128 MI300A compute nodes.

| Node type | Memory | Nodes | CPU sockets | GPUs |
| --- | --- | --- | --- | --- |
| mi200 | 512 GB | 13 | 13 | 104 |
| mi300 | 512 GB | 128 | 512 | 512 |

See Running jobs on Beverin for details on the associated slurm partitions.

### Storage and file systems

Beverin uses the HPCP filesystems and storage policies.

## Getting started

### Logging into Beverin

To connect to Beverin via SSH, first refer to the ssh guide.

> [!NOTE]
>
> **`~/.ssh/config`**
>
> Add the following to your SSH configuration to enable you to directly connect to Beverin using `ssh beverin`.
>
> ```text
> Host beverin
>     HostName beverin.vc.cscs.ch
>     ProxyJump ela
>     User cscsusername
>     IdentityFile ~/.ssh/cscs-key
>     IdentitiesOnly yes
> ```

### Software

Beverin provides uenv to deliver programming environments and application software. Please refer to the uenv documentation for detailed information on how to use the uenv tools on the system.

- **Programming Environments**

  Provide compilers, MPI, Python, common libraries and tools used to build your own applications.

  - prgenv-gnu
  - linalg

In addition to the base `GNU` and `linalg` programming environments, a few other dedicated environments are provided on a best effort basis:

- **Climate and Weather Applications**

  Provide software stacks for climate and weather workflows on Beverin.

  - ICON

- **Scientific Applications**

  Provide scientific applications.

  - Quantumespresso

- **Tools**

  Provide tools like

  - Linaro Forge

See the uenv quick start guide to find all programming environments available on Beverin.

#### Containers

Beverin supports container workloads using the Container Engine.

To build images, see the guide to building container images on Alps.

## Running Jobs on Beverin

### Slurm

Beverin uses Slurm as the workload manager, which is used to launch and monitor distributed workloads.

There are two Slurm partitions on the system, corresponding to the two node types:

- `mi200` (default)
- `mi300`

| Partition | Nodes | Max nodes/job | Default time | Max time |
| --- | --- | --- | --- | --- |
| `mi300` | 128 | unlimited | 01:00:00 | 1-00:00:00 |
| `mi200` (default) | 13 | unlimited | 01:00:00 | 1-00:00:00 |

The hardware available in each partition, including the Slurm features that can be selected with `--constraint`:

| Partition | Nodes | Node type | Features |
| --- | --- | --- | --- |
| `mi300` | 128 | mi300 | amdgpu |
| `mi200` | 13 | mi200 | none |

#### GPU partitioning on MI300A nodes

The GPU of each MI300A APU can be split into several logical GPUs, by grouping its six accelerator complex dies (XCDs). Select the mode with a Slurm feature on the `mi300` partition; jobs that do not select one run in SPX mode:

| Mode | Slurm constraint | GPUs per APU | XCDs per GPU | GPUs per node |
| --- | --- | --- | --- | --- |
| SPX (single partition) | `amdgpu_spx` (default) | 1 | 6 | 4 |
| TPX (triple partition) | `amdgpu_tpx` | 3 | 2 | 12 |
| CPX (core partitioned) | `amdgpu_cpx` | 6 | 1 | 24 |

run a job with each APU split into six GPUs

```bash
sbatch --partition=mi300 --constraint=amdgpu_cpx job.sh
```

The memory of the APU is not partitioned: every logical GPU can access all of it. SPX suits a single large workload per APU, while TPX and CPX allow several smaller workloads to share an APU, each on its own GPU. See the AMD documentation on [MI300A GPU partitioning](<https://instinct.docs.amd.com/projects/amdgpu-docs/en/latest/gpu-partitioning/mi300a/overview.html>) for details.

### FirecREST

Beverin can also be accessed using FirecREST at the `https://api.cscs.ch/ml/firecrest/v2` API endpoint.
