[](){#ref-communication-nccl}
# NCCL

[NCCL](https://developer.nvidia.com/nccl) is an optimized inter-GPU communication library for NVIDIA GPUs.
It is commonly used in machine learning frameworks, but traditional scientific applications can also benefit from NCCL.

## Using NCCL

To use the Slingshot network on Alps, the [`aws-ofi-nccl`](https://github.com/aws/aws-ofi-nccl) plugin must be used.
With the container engine, the [AWS OFI NCCL hook][ref-ce-aws-ofi-hook] can be used to load the plugin into the container and configure NCCL to use it.

While the container engine does this automatically, regardless of application, the following environment variable should always be set when using NCCL:

```bash
export NCCL_NET_PLUGIN="ofi"
```

This forces NCCL to use the libfabric plugin, enabling full use of the Slingshot network.
Conversely, if the plugin can not be found, applications will fail to start instead of falling back to e.g. TCP, which would be significantly slower than with the plugin.

!!! warning "GPU-aware MPI with NCCL"
    Using GPU-aware MPI together with NCCL [can easily lead to deadlocks](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/mpi.html#inter-gpu-communication-with-cuda-aware-mpi).
    Unless care is taken to ensure that the two methods of communication are not used concurrently, we recommend not using GPU-aware MPI with NCCL.
    To explicitly disable GPU-aware MPI with Cray MPICH, explicitly set `MPICH_GPU_SUPPORT_ENABLED=0`.
    Note that this option may be set to `1` by default on some Alps clusters.
    See [the Cray MPICH documentation][ref-communication-cray-mpich] for more details on GPU-aware MPI with Cray MPICH.

!!! todo
    More options?
