[](){#ref-communication-nccl}
# NCCL

[NCCL](https://developer.nvidia.com/nccl) is an optimized inter-GPU communication library for NVIDIA GPUs.
It is commonly used in machine learning frameworks, but traditional scientific applications can also benefit from NCCL.

## Using NCCL

To use the Slingshot network on Alps, the [`aws-ofi-nccl`](https://github.com/aws/aws-ofi-nccl) plugin must be used.
With the container engine, the [AWS OFI NCCL hook][ref-ce-aws-ofi-hook] can be used to load the plugin into the container and configure NCCL to use it.

Most uenvs, like [`prgenv-gnu`][ref-uenv-prgenv-gnu], also contain the NCCL plugin.
When using e.g. the `default` view of `prgenv-gnu` the `aws-ofi-nccl` plugin will be available in the environment.
Alternatively, loading the `aws-ofi-nccl` module with the `modules` view also makes the plugin available in the environment.
The environment variables described below must still be set to ensure that NCCL uses the plugin.

While the container engine sets these automatically when using the NCCL hook, the following environment variables should always be set for correctness and optial performance when using NCCL:

```bash
export NCCL_NET="AWS Libfabric" # (1)
export NCCL_NET_GDR_LEVEL=PHB # (2)
export FI_CXI_DEFAULT_CQ_SIZE=131072 # (3)
export FI_CXI_DEFAULT_TX_SIZE=32768
export FI_CXI_DISABLE_HOST_REGISTER=1
export FI_CXI_RX_MATCH_MODE=software
export FI_MR_CACHE_MONITOR=userfaultfd
export MPICH_GPU_SUPPORT_ENABLED=0 # (3)
```

1. This forces NCCL to use the libfabric plugin, enabling full use of the Slingshot network. If the plugin can not be found, applications will fail to start. With the default value, applications would instead fall back to e.g. TCP, which would be significantly slower than with the plugin. [More information about `NCCL_NET`](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html#nccl-net).
2. Use GPU Direct RDMA when GPU and NIC are on the same NUMA node. [More information about `NCCL_NET_GDR_LEVEL`](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html#nccl-net-gdr-level-formerly-nccl-ib-gdr-level).
3. This and the other `FI` (libfabric) environment variables have been found to give the best performance on the Alps network across a wide range of applications. Specific applications may perform better with other values.
4. Disable GPU-aware MPI explicitly, to avoid potential deadlocks between MPI and NCCL.

!!! warning "Using NCCL with uenvs"
    The environment variables listed above are not set automatically when using uenvs.

!!! warning "GPU-aware MPI with NCCL"
    Using GPU-aware MPI together with NCCL [can easily lead to deadlocks](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/mpi.html#inter-gpu-communication-with-cuda-aware-mpi).
    Unless care is taken to ensure that the two methods of communication are not used concurrently, we recommend not using GPU-aware MPI with NCCL.
    To explicitly disable GPU-aware MPI with Cray MPICH, explicitly set `MPICH_GPU_SUPPORT_ENABLED=0`.
    Note that this option may be set to `1` by default on some Alps clusters.
    See [the Cray MPICH documentation][ref-communication-cray-mpich] for more details on GPU-aware MPI with Cray MPICH.

!!! todo
    More options?
