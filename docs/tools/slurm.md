[](){#ref-slurm}
# SLURM

CSCS uses the [SLURM](https://slurm.schedmd.com/documentation.html) as its workload manager to efficiently schedule and manage jobs on Alps vClusters.
SLURM is an open-source, highly scalable job scheduler that allocates computing resources, queues user jobs, and optimizes workload distribution across the cluster. It supports advanced scheduling policies, job dependencies, resource reservations, and accounting, making it well-suited for high-performance computing environments.

## Accounting

!!! todo
    document `--account`, `--constrant` and other generic flags.

## Partitions

At CSCS, SLURM is configured to accommodate the diverse range of node types available in our HPC clusters. These nodes vary in architecture, including CPU-only nodes and nodes equipped with different types of GPUs. Because of this heterogeneity, SLURM must be tailored to ensure efficient resource allocation, job scheduling, and workload management specific to each node type.

Each type of node has different resource constraints and capabilities, which SLURM takes into account when scheduling jobs. For example, CPU-only nodes may have configurations optimized for multi-threaded CPU workloads, while GPU nodes require additional parameters to allocate GPU resources efficiently. SLURM ensures that user jobs request and receive the appropriate resources while preventing conflicts or inefficient utilization.

The following sections will provide detailed guidance on how to use SLURM to request and manage CPU cores, memory, and GPUs in jobs. These instructions will help users optimize their workload execution and ensure efficient use of CSCS computing resources.

[](){#ref-slurm-gh200}
### NVIDIA GH200 GPU Nodes

The [GH200 nodes on Alps][ref-alps-gh200-node] have four GPUs per node, and SLURM job submissions must be configured appropriately to best make use of the resources.
Applications that can saturate the GPUs with a single process per GPU should generally prefer this mode.
[Configuring SLURM jobs to use a single GPU per rank][ref-slurm-gh200-single-rank-per-gpu] is also the most straightforward setup.
Some applications perform badly with a single rank per GPU, and require use of [NVIDIA's Multi-Process Service (MPS)] to oversubscribe GPUs with multiple ranks per GPU.

The best SLURM configuration is application- and workload-specific, so it is worth testing which works best in your particular case.
See [Scientific Applications][ref-software-sciapps] for information about recommended application-specific SLURM configurations.

!!! warning
    The GH200 nodes have their GPUs configured in ["default" compute mode](https://docs.nvidia.com/deploy/mps/index.html#gpu-compute-modes).
    The "default" mode is used to avoid issues with certain containers.
    Unlike "exclusive process" mode, "default" mode allows multiple processes to submit work to a single GPU simultaneously.
    This also means that different ranks on the same node can inadvertently use the same GPU leading to suboptimal performance or unused GPUs, rather than job failures.
    
    Some applications benefit from using multiple ranks per GPU. However, [MPS should be used][ref-slurm-gh200-multi-rank-per-gpu] in these cases.
    
    If you are unsure about which GPU is being used for a particular rank, print the `CUDA_VISIBLE_DEVICES` variable, along with e.g. `SLURM_LOCALID`, `SLURM_PROCID`, and `SLURM_NODEID` variables, in your job script.
    If the variable is unset or empty all GPUs are visible to the rank and the rank will in most cases only use the first GPU. 

[](){#ref-slurm-gh200-single-rank-per-gpu}
#### One rank per GPU

Configuring SLURM to use one GH200 GPU per rank is easiest done using the `--ntasks-per-node=4` and `--gpus-per-task=1` SLURM flags.
For advanced users, using `--gpus-per-task` is equivalent to setting `CUDA_VISIBLE_DEVICES` to `SLURM_LOCALID`, assuming the job is using four ranks per node.
The examples below launch jobs on two nodes with four ranks per node using `sbatch` and `srun`:

```bash
#!/bin/bash
#SBATCH --job-name=gh200-single-rank-per-gpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --gpus-per-task=1

srun <application>
```
    
Omitting the `--gpus-per-task` results in `CUDA_VISIBLE_DEVICES` being unset, which will lead to most applications using the first GPU on all ranks.

[](){#ref-slurm-gh200-multi-rank-per-gpu}
#### Multiple ranks per GPU

Using multiple ranks per GPU can improve performance e.g. of applications that don't generate enough work for a GPU using a single rank, or ones that scale badly to all 72 cores of the Grace CPU.
In these cases SLURM jobs must be configured to assign multiple ranks to a single GPU.
This is best done using [NVIDIA's Multi-Process Service (MPS)].
To use MPS, launch your application using the following wrapper script, which will start MPS on one rank per node and assign GPUs to ranks according to the CPU mask of a rank, ensuring the closest GPU is used:

```bash
#!/bin/bash
# Example mps-wrapper.sh usage:
# > srun [srun args] mps-wrapper.sh [cmd] [cmd args]

# Only this path is supported by MPS
export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-log-$(id -un)

# Launch MPS from a single rank per node
if [[ $SLURM_LOCALID -eq 0 ]]; then
    CUDA_VISIBLE_DEVICES=0,1,2,3 nvidia-cuda-mps-control -d
fi

# Set CUDA device
numa_nodes=$(hwloc-calc --physical --intersect NUMAnode $(hwloc-bind --get --taskset))
export CUDA_VISIBLE_DEVICES=$numa_nodes

# Wait for MPS to start
sleep 1

# Run the command
numactl --membind=$numa_nodes "$@"
result=$?

# Quit MPS control daemon before exiting
if [[ $SLURM_LOCALID -eq 0 ]]; then
    echo quit | nvidia-cuda-mps-control
fi

exit $result
```

Save the above script as `mps-wrapper.sh` and make it executable with `chmod +x mps-wrapper.sh`.
If the `mps-wrapper.sh` script is in the current working directory, you can then launch jobs using MPS for example as follows:

```bash
#!/bin/bash
#SBATCH --job-name=gh200-multiple-ranks-per-gpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=32
#SBATCH --cpus-per-task=8

srun ./mps-wrapper.sh <application>
```

Note that in the example job above:

- `--gpus-per-node` is not set at all; the `mps-wrapper.sh` script ensures that the right GPU is visible for each rank using `CUDA_VISIBLE_DEVICES`
- `--ntasks-per-node` is set to 32; this results in 8 ranks per GPU
- `--cpus-per-task` is set to 8; this ensures that threads are not allowed to migrate across the whole GH200 node

The configuration that is optimal for your application may be different.

[NVIDIA's Multi-Process Service (MPS)]: https://docs.nvidia.com/deploy/mps/index.html

[](){#ref-slurm-amdcpu}
## AMD CPU

!!! todo
    document how slurm is configured on AMD CPU nodes (e.g. eiger)
