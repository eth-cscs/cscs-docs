[](){#slurm}
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

[](){#gh200-slurm}
### NVIDIA GH200 GPU Nodes

!!! todo
    document how slurm can be used on the Grace-Hopper nodes.

    Note how you can link to this section from elsewhere using the anchor above, e.g.:

    ```
    [using slurm on Grace-Hopper][gh200-slurm]
    ```

Link to the [Grace-Hopper overview][gh200-node].

An example of using tabs to show srun and sbatch useage to get one GPU per MPI rank:

=== "sbatch"

    ```bash
    #!/bin/bash
    #SBATCH --job-name=affinity-test
    #SBATCH --ntasks-per-node=4
    #SBATCH --nodes=2
    #SBATCH --gpus-per-task=1

    srun affinity
    ```

=== "srun"

    ```
    > srun -n8 -N2 --gpus-per-task=1 affinity
    ```


[](){#amdcpu-slurm}
## AMD CPU

!!! todo
    document how slurm is configured on AMD CPU nodes (e.g. eiger)
