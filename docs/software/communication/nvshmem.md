[](){#ref-communication-nvshmem}
# NVSHMEM

[NVSHMEM](https://developer.nvidia.com/nvshmem) is a parallel programming interface based on OpenSHMEM that provides efficient and scalable communication for NVIDIA GPU clusters.
NVSHMEM creates a global address space for data that spans the memory of multiple GPUs and can be accessed with fine-grained GPU-initiated operations, CPU-initiated operations, and operations on CUDA streams.

The parallel programming library with support for libfabric, and demonstrates how to efficiently run said image on Alps.

This image is based on the [OpenMPI image][ref-ce-guidelines-images-ompi], and thus it is suited for hosts with NVIDIA GPUs, like Alps GH200 nodes.

A build of this image is currently hosted on the [Quay.io](https://quay.io/) registry at the following reference:
`quay.io/ethcscs/nvshmem:3.4.5-ompi5.0.8-ofi1.22-cuda12.8`.

## NVSHMEM in containers

### Installing NVSHMEM in a container

Containers provided by NVIDIA on NGC typically provide NVSHMEM as part of the NVHPC SDK in the image, however this version is built for and linked against OpenMPI and UCX in the container, which are not compatible with the Slingshot network of Alps.

To use NVSHMEM, we reccomend first installing OpenMPI with libfabric support in the container, or starting with an image that contains OpenMPI+libfabric.

NVSHMEM is built from source in the container, from a source tar ball provided by NVIDIA.
The example here provides the latest version 3.4.5 at the time of writing (November 2025).

- Notice that NVSHMEM is configured with support for libfabric explicitly enabled: `NVSHMEM_LIBFABRIC_SUPPORT=1`
- NVSHMEM is built without support for UCX and Infiniband components, because they are not needed on Alps.
- Since this image uses OpenMPI (which provides PMIx) as MPI implementation, NVSHMEM is also configured to default to PMIx for bootstrapping (`NVSHMEM_PMIX_SUPPORT=1`).

!!! note
    The image also installs the NVSHMEM performance tests, `NVSHMEM_BUILD_TESTS=1`, to demonstrate performance below.
    The performance tests, in turn, require the installation of Python dependencies.
    When building images intended solely for production purposes, you may exclude both those elements.

```dockerfile
# Build NVSHMEM from source
RUN wget -q https://developer.download.nvidia.com/compute/redist/nvshmem/3.4.5/source/nvshmem_src_cuda12-all-all-3.4.5.tar.gz \
    && tar -xvf nvshmem_src_cuda12-all-all-3.4.5.tar.gz \
    && cd nvshmem_src \
    && NVSHMEM_BUILD_EXAMPLES=0 \
       NVSHMEM_BUILD_TESTS=1 \
       NVSHMEM_DEBUG=0 \
       NVSHMEM_DEVEL=0 \
       NVSHMEM_DEFAULT_PMI2=0 \
       NVSHMEM_DEFAULT_PMIX=1 \
       NVSHMEM_DISABLE_COLL_POLL=1 \
       NVSHMEM_ENABLE_ALL_DEVICE_INLINING=0 \
       NVSHMEM_GPU_COLL_USE_LDST=0 \
       NVSHMEM_LIBFABRIC_SUPPORT=1 \
       NVSHMEM_MPI_SUPPORT=1 \
       NVSHMEM_MPI_IS_OMPI=1 \
       NVSHMEM_NVTX=1 \
       NVSHMEM_PMIX_SUPPORT=1 \
       NVSHMEM_SHMEM_SUPPORT=1 \
       NVSHMEM_TEST_STATIC_LIB=0 \
       NVSHMEM_TIMEOUT_DEVICE_POLLING=0 \
       NVSHMEM_TRACE=0 \
       NVSHMEM_USE_DLMALLOC=0 \
       NVSHMEM_USE_NCCL=1 \
       NVSHMEM_USE_GDRCOPY=1 \
       NVSHMEM_VERBOSE=0 \
       NVSHMEM_DEFAULT_UCX=0 \
       NVSHMEM_UCX_SUPPORT=0 \
       NVSHMEM_IBGDA_SUPPORT=0 \
       NVSHMEM_IBGDA_SUPPORT_GPUMEM_ONLY=0 \
       NVSHMEM_IBDEVX_SUPPORT=0 \
       NVSHMEM_IBRC_SUPPORT=0 \
       LIBFABRIC_HOME=/usr \
       NCCL_HOME=/usr \
       GDRCOPY_HOME=/usr/local \
       MPI_HOME=/usr \
       SHMEM_HOME=/usr \
       NVSHMEM_HOME=/usr \
       cmake . \
       && make -j$(nproc) \
       && make install \
   && ldconfig \
   && cd .. \
   && rm -r nvshmem_src nvshmem_src_cuda12-all-all-3.4.5.tar.gz
```

```toml
image = "quay.io#ethcscs/nvshmem:3.4.5-ompi5.0.8-ofi1.22-cuda12.8"

[env]
PMIX_MCA_psec="native" # (1)!
NVSHMEM_REMOTE_TRANSPORT="libfabric"
NVSHMEM_LIBFABRIC_PROVIDER="cxi"
NVSHMEM_DISABLE_CUDA_VMM="1" # (2)!

[annotations]
com.hooks.aws_ofi_nccl.enabled = "true"
com.hooks.aws_ofi_nccl.variant = "cuda12"
```

1. Ensures PMIx uses the same security domain as Slurm. Otherwise PMIx will print warnings at startup.
2. NVSHMEM's `libfabric` transport does not support VMM yet, so VMM must be disabled by setting the environment variable `NVSHMEM_DISABLE_CUDA_VMM=1`.

### Notes

- Since NVSHMEM has been configured in the Containerfile to use PMIx for bootstrapping, when using this image the `srun` option `--mpi=pmix` must be used to run successful multi-rank jobs.
- Other bootstrapping methods (including different PMI implementations) can be specified for NVSHMEM through the related [environment variables](https://docs.nvidia.com/nvshmem/api/gen/env.html#bootstrap-options). When bootstrapping through PMI or MPI through Slurm, ensure that the PMI implementation used by Slurm (i.e. `srun --mpi` option) matches the one expected by NVSHMEM or the MPI library.
- NCCL requires the presence of the [AWS OFI NCCL plugin](https://github.com/aws/aws-ofi-nccl) in order to correctly interface with Libfabric and (through the latter) the Slingshot interconnect. Therefore, for optimal performance the [related CE hook][ref-ce-aws-ofi-hook] must be enabled and set to match the CUDA version in the container.
- Libfabric itself is usually injected by the [CXI hook][ref-ce-cxi-hook], which is enabled by default on several Alps vClusters.
