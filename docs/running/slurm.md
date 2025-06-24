[](){#ref-slurm}
# SLURM

CSCS uses the [SLURM](https://slurm.schedmd.com/documentation.html) as its workload manager to efficiently schedule and manage jobs on Alps vClusters.
SLURM is an open-source, highly scalable job scheduler that allocates computing resources, queues user jobs, and optimizes workload distribution across the cluster. It supports advanced scheduling policies, job dependencies, resource reservations, and accounting, making it well-suited for high-performance computing environments.

## Accounting

!!! todo
    document `--account`, `--constraint` and other generic flags.

[Confluence link](https://confluence.cscs.ch/spaces/KB/pages/794296413/How+to+run+jobs+on+Eiger)

[](){#ref-slurm-partitions}
## Partitions

At CSCS, SLURM is configured to accommodate the diverse range of node types available in our HPC clusters. These nodes vary in architecture, including CPU-only nodes and nodes equipped with different types of GPUs. Because of this heterogeneity, SLURM must be tailored to ensure efficient resource allocation, job scheduling, and workload management specific to each node type.

Each type of node has different resource constraints and capabilities, which SLURM takes into account when scheduling jobs. For example, CPU-only nodes may have configurations optimized for multi-threaded CPU workloads, while GPU nodes require additional parameters to allocate GPU resources efficiently. SLURM ensures that user jobs request and receive the appropriate resources while preventing conflicts or inefficient utilization.

!!! example "How to check the partitions and number of nodes therein?"
    You can check the size of the system by running the following command in the terminal:
    ```console
    $ sinfo --format "| %20R | %10D | %10s | %10l | %10A |"
    | PARTITION            | NODES      | JOB_SIZE   | TIMELIMIT  | NODES(A/I) |
    | debug                | 32         | 1-2        | 30:00      | 3/29       |
    | normal               | 1266       | 1-infinite | 1-00:00:00 | 812/371    |
    | xfer                 | 2          | 1          | 1-00:00:00 | 1/1        |
    ```
    The last column shows the number of nodes that have been allocated in currently running jobs (`A`) and the number of jobs that are idle (`I`).

[](){#ref-slurm-partition-debug}
### Debug partition
The SLURM `debug` partition is useful for quick turnaround workflows. The partition has a short maximum time (timelimit can be seen with `sinfo -p debug`), and a low number of maximum nodes (the `MaxNodes` can be seen with `scontrol show partition=debug`).

[](){#ref-slurm-partition-normal}
### Normal partition
This is the default partition, and will be used when you do not explicitly set a partition. This is the correct choice for standard jobs. The maximum time is usually set to 24 hours (`sinfo -p normal` for timelimit), and the maximum nodes can be as much as nodes are available.

The following sections will provide detailed guidance on how to use SLURM to request and manage CPU cores, memory, and GPUs in jobs. These instructions will help users optimize their workload execution and ensure efficient use of CSCS computing resources.

## Affinity

The following sections will document how to use Slurm on different compute nodes available on Alps.
To demonstrate the effects different Slurm parameters, we will use a little command line tool [affinity](https://github.com/bcumming/affinity) that prints the CPU cores and GPUs that are assinged to each MPI rank in a job, and which node they are run on.

We strongly recommend using a tool like affinity to understand and test the Slurm configuration for jobs, because the behavior of Slurm is highly dependent on the system configuration.
Parameters that worked on a different cluster -- or with a different Slurm version or configuration on the same cluster -- are not guaranteed to give the same results.

It is straightforward to build the affinity tool to experiment with Slurm configurations.

```console title="Compiling affinity"
$ uenv start prgenv-gnu/24.11:v2 --view=default     #(1)
$ git clone https://github.com/bcumming/affinity.git
$ cd affinity; mkdir build; cd build;
$ CC=gcc CXX=g++ cmake ..                           #(2)
$ CC=gcc CXX=g++ cmake .. -DAFFINITY_GPU=cuda       #(3)
$ CC=gcc CXX=g++ cmake .. -DAFFINITY_GPU=rocm       #(4)
```

1. Affinity can be built using [`prgenv-gnu`][ref-uenv-prgenv-gnu] on all clusters.

2. By default affinity will build with MPI support and no GPU support: configure with no additional arguments on a CPU-only system like [Eiger][ref-cluster-eiger].

3. Enable CUDA support on systems that provide NVIDIA GPUs.

4. Enable ROCM support on systems that provide AMD GPUs.

The build generates the following executables:

* `affinity.omp`: tests thread affinity with no MPI (always built).
* `affinity.mpi`: tests thread affinity with MPI (built by default).
* `affinity.cuda`: tests thread and GPU affinity with MPI (built with `-DAFFINITY_GPU=cuda`).
* `affinity.rocm`: tests thread and GPU affinity with MPI (built with `-DAFFINITY_GPU=rocm`).

??? example "Testing CPU affinity"
    Test CPU affinity (this can be used on both CPU and GPU enabled nodes).
    ```console
    $ uenv start prgenv-gnu/24.11:v2 --view=default
    $ srun -n8 -N2 -c72 ./affinity.mpi
    affinity test for 8 MPI ranks
    rank   0 @ nid006363: threads [ 0:71] -> cores [  0: 71]
    rank   1 @ nid006363: threads [ 0:71] -> cores [ 72:143]
    rank   2 @ nid006363: threads [ 0:71] -> cores [144:215]
    rank   3 @ nid006363: threads [ 0:71] -> cores [216:287]
    rank   4 @ nid006375: threads [ 0:71] -> cores [  0: 71]
    rank   5 @ nid006375: threads [ 0:71] -> cores [ 72:143]
    rank   6 @ nid006375: threads [ 0:71] -> cores [144:215]
    rank   7 @ nid006375: threads [ 0:71] -> cores [216:287]
    ```

    In this example there are 8 MPI ranks:

    * ranks `0:3` are on node `nid006363`;
    * ranks `4:7` are on node `nid006375`;
    * each rank has 72 threads numbered `0:71`;
    * all threads on each rank have affinity with the same 72 cores;
    * each rank gets 72 cores, e.g. rank 1 gets cores `72:143` on node `nid006363`.



??? example "Testing GPU affinity"
    Use `affinity.cuda` or `affinity.rocm` to test on GPU-enabled systems.

    ```console
    $ srun -n4 -N1 ./affinity.cuda                      #(1)
    GPU affinity test for 4 MPI ranks
    rank      0 @ nid005555
     cores   : [0:7]
     gpu   0 : GPU-2ae325c4-b542-26c2-d10f-c4d84847f461
     gpu   1 : GPU-5923dec6-288f-4418-f485-666b93f5f244
     gpu   2 : GPU-170b8198-a3e1-de6a-ff82-d440f71c05da
     gpu   3 : GPU-0e184efb-1d1f-f278-b96d-15bc8e5f17be
    rank      1 @ nid005555
     cores   : [72:79]
     gpu   0 : GPU-2ae325c4-b542-26c2-d10f-c4d84847f461
     gpu   1 : GPU-5923dec6-288f-4418-f485-666b93f5f244
     gpu   2 : GPU-170b8198-a3e1-de6a-ff82-d440f71c05da
     gpu   3 : GPU-0e184efb-1d1f-f278-b96d-15bc8e5f17be
    rank      2 @ nid005555
     cores   : [144:151]
     gpu   0 : GPU-2ae325c4-b542-26c2-d10f-c4d84847f461
     gpu   1 : GPU-5923dec6-288f-4418-f485-666b93f5f244
     gpu   2 : GPU-170b8198-a3e1-de6a-ff82-d440f71c05da
     gpu   3 : GPU-0e184efb-1d1f-f278-b96d-15bc8e5f17be
    rank      3 @ nid005555
     cores   : [216:223]
     gpu   0 : GPU-2ae325c4-b542-26c2-d10f-c4d84847f461
     gpu   1 : GPU-5923dec6-288f-4418-f485-666b93f5f244
     gpu   2 : GPU-170b8198-a3e1-de6a-ff82-d440f71c05da
     gpu   3 : GPU-0e184efb-1d1f-f278-b96d-15bc8e5f17be
    $ srun -n4 -N1 --gpus-per-task=1 ./affinity.cuda    #(2)
    GPU affinity test for 4 MPI ranks
    rank      0 @ nid005675
     cores   : [0:7]
     gpu   0 : GPU-a16a8dac-7661-a44b-c6f8-f783f6e812d3
    rank      1 @ nid005675
     cores   : [72:79]
     gpu   0 : GPU-ca5160ac-2c1e-ff6c-9cec-e7ce5c9b2d09
    rank      2 @ nid005675
     cores   : [144:151]
     gpu   0 : GPU-496a2216-8b3c-878e-e317-36e69af11161
    rank      3 @ nid005675
     cores   : [216:223]
     gpu   0 : GPU-766e3b8b-fa19-1480-b02f-0dfd3f2c87ff
    ```

    1. Test GPU affinity: note how all 4 ranks see the same 4 GPUs.

    2. Test GPU affinity: note how the `--gpus-per-task=1` parameter assings a unique GPU to each rank.

[](){#ref-slurm-gh200}
## NVIDIA GH200 GPU Nodes

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
### One rank per GPU

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
### Multiple ranks per GPU

Using multiple ranks per GPU can improve performance e.g. of applications that don't generate enough work for a GPU using a single rank, or ones that scale badly to all 72 cores of the Grace CPU.
In these cases SLURM jobs must be configured to assign multiple ranks to a single GPU.
This is best done using [NVIDIA's Multi-Process Service (MPS)].
To use MPS, launch your application using the following wrapper script, which will start MPS on one rank per node and assign GPUs to ranks according to the CPU mask of a rank, ensuring the closest GPU is used:

```bash title="mps-wrapper.sh"
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
## AMD CPU Nodes

Alps has nodes with two AMD Epyc Rome CPU sockets per node for CPU-only workloads, most notably in the [Eiger][ref-cluster-eiger] cluster provided by the [HPC Platform][ref-platform-hpcp].
!!! todo
    document how slurm is configured on AMD CPU nodes (e.g. eiger)
