[](){#ref-communication-nvshmem}
# NVSHMEM

[NVSHMEM](https://developer.nvidia.com/nvshmem) is a parallel programming interface based on OpenSHMEM that provides efficient and scalable communication for NVIDIA GPU clusters.
NVSHMEM creates a global address space for data that spans the memory of multiple GPUs and can be accessed with fine-grained GPU-initiated operations, CPU-initiated operations, and operations on CUDA streams.

[](){#ref-communication-nvshmem-using}
## Using NVSHMEM

[](){#ref-communication-uenv-ce}
### uenv

NVSHMEM is not currently available in any uenv.
CSCS is developing support for building NVSHMEM that runs efficiently on the Alps network, and will update these docs when it is available.

[](){#ref-communication-nvshmem-ce}
### Containers

To use NVSHMEM, we recommend first installing OpenMPI with libfabric support in the container, or starting with an image that contains OpenMPI+libfabric.

This image recipe described here is based on the [OpenMPI image][ref-communication-openmpi], and thus it is suited for hosts with NVIDIA GPUs, like Alps GH200 nodes.
This image is based on the [OpenMPI image][ref-ce-guidelines-images-ompi], and thus it is suited for hosts with NVIDIA GPUs, like Alps GH200 nodes.

!!! warning "Be careful with NVSHMEM provided by NVIDIA containers"
    Containers provided by NVIDIA on NGC typically provide NVSHMEM as part of the NVHPC SDK in the image, however this version is built for and linked against OpenMPI and UCX in the container, which are not compatible with the Slingshot network of Alps.

NVSHMEM is built from source in the container, from a source tar ball provided by NVIDIA.
The example here provides the latest version 3.4.5 at the time of writing (November 2025).

- Notice that NVSHMEM is configured with support for libfabric explicitly enabled: `NVSHMEM_LIBFABRIC_SUPPORT=1`
- NVSHMEM is built without support for UCX and Infiniband components, because they are not needed on Alps.
- Since this image uses OpenMPI (which provides PMIx) as MPI implementation, NVSHMEM is also configured to default to PMIx for bootstrapping (`NVSHMEM_PMIX_SUPPORT=1`).

!!! example "Installing NVSHMEM in a container for NVIDIA nodes"
    The following example demonstrates how to download and install NVSHMEM from source in a Containerfile.

    The container image cont
    ```dockerfile
    --8<-- "docs/software/communication/dockerfiles/nvshmem"
    ```
    !!! note
        The image also installs the NVSHMEM performance tests, `NVSHMEM_BUILD_TESTS=1`, to demonstrate performance below.
        The performance tests, in turn, require the installation of Python dependencies.
        When building images intended solely for production purposes, you may exclude both those elements.

    Expand the box below to see an example of a complete Containerfile that installs NVSHMEM and all of its dependencies in an NVIDIA container.

    ??? note "The full Containerfile"
        ```dockerfile
        --8<-- "docs/software/communication/dockerfiles/base"
        --8<-- "docs/software/communication/dockerfiles/libfabric"
        --8<-- "docs/software/communication/dockerfiles/ucx"
        --8<-- "docs/software/communication/dockerfiles/openmpi"
        --8<-- "docs/software/communication/dockerfiles/nvshmem"
        ```

!!! example "Running the NVSHMEM container"
    The following EDF file sets the required environment variables and container hooks for NVSHMEM.
    It uses a pre-built container hosted on the [Quay.io](https://quay.io/) registry at the following reference: `quay.io/ethcscs/nvshmem:3.4.5-ompi5.0.8-ofi1.22-cuda12.8`.


    ```toml
    image = "quay.io#ethcscs/nvshmem:3.4.5-ompi5.0.8-ofi1.22-cuda12.8"

    [env]
    PMIX_MCA_psec="native" # (1)!
    NVSHMEM_REMOTE_TRANSPORT="libfabric"
    NVSHMEM_LIBFABRIC_PROVIDER="cxi"
    NVSHMEM_DISABLE_CUDA_VMM="1" # (2)!

    [annotations]
    com.hooks.aws_ofi_nccl.enabled = "true" # (3)!
    com.hooks.aws_ofi_nccl.variant = "cuda12"
    ```

    1. Ensures PMIx uses the same security domain as Slurm.
       Otherwise PMIx will print warnings at startup.
    2. NVSHMEM's `libfabric` transport does not support VMM yet, so VMM must be disabled by setting the environment variable `NVSHMEM_DISABLE_CUDA_VMM=1`.
    3. NCCL requires the presence of the [AWS OFI NCCL plugin](https://github.com/aws/aws-ofi-nccl) in order to correctly interface with Libfabric and (through the latter) the Slingshot interconnect.
       Therefore, for optimal performance the [related CE hook][ref-ce-aws-ofi-hook] must be enabled and set to match the CUDA version in the container.

    Libfabric itself is usually injected by the [CXI hook][ref-ce-cxi-hook], which is enabled by default on several Alps vClusters.


    ```bash
    srun -N2 --ntasks-per-node=4  \
         -mpi=pmix                \ # (1)!
         --environment=nvshmem    \
        /usr/local/nvshmem/bin/perftest/device/coll/alltoall_latency
    ```

    1. Since NVSHMEM has been configured in the Containerfile to use PMIx for bootstrapping, when using this image the `srun` option `--mpi=pmix` must be used to run successful multi-rank jobs.

    Other bootstrapping methods (including different PMI implementations) can be specified for NVSHMEM through the related [environment variables](https://docs.nvidia.com/nvshmem/api/gen/env.html#bootstrap-options).
    When bootstrapping through PMI or MPI through Slurm, ensure that the PMI implementation used by Slurm (i.e. `srun --mpi` option) matches the one expected by NVSHMEM or the MPI library.

[](){#ref-communication-nvshmem-performance}
## NVSHMEM Performance

The results of running the `alltoall_latency` benchmark provided by the NCCL test suite, built in the example container [above][ref-communication-nvshmem-ce].

```console
$ srun -N2 --ntasks-per-node=4  --mpi=pmix --environment=nvshmem /usr/local/nvshmem/bin/perftest/device/coll/alltoall_latency
Runtime options after parsing command line arguments 
min_size: 4, max_size: 4194304, step_factor: 2, iterations: 10, warmup iterations: 5, number of ctas: 32, threads per cta: 256 stride: 1, datatype: int, reduce_op: sum, threadgroup_scope: all_scopes, atomic_op: inc, dir: write, report_msgrate: 0, bidirectional: 0, putget_issue :on_stream, use_graph: 0, use_mmap: 0, mem_handle_type: 0, use_egm: 0
Note: Above is full list of options, any given test will use only a subset of these variables.
mype: 6 mype_node: 2 device name: NVIDIA GH200 120GB bus id: 1 
#alltoall_device
size(B)     count     type      scope     latency(us)       algbw(GB/s)   busbw(GB/s) 
32          8         32-bit    thread    116.220796        0.000         0.000       
64          16        32-bit    thread    112.700796        0.001         0.000       
128         32        32-bit    thread    113.571203        0.001         0.001       
256         64        32-bit    thread    111.123204        0.002         0.002       
512         128       32-bit    thread    111.075199        0.005         0.004       
1024        256       32-bit    thread    110.131204        0.009         0.008       
2048        512       32-bit    thread    111.030400        0.018         0.016       
4096        1024      32-bit    thread    110.985601        0.037         0.032       
8192        2048      32-bit    thread    111.039996        0.074         0.065       
#alltoall_device
size(B)     count     type      scope     latency(us)       algbw(GB/s)   busbw(GB/s) 
32          8         32-bit    warp      89.801598         0.000         0.000       
64          16        32-bit    warp      90.563202         0.001         0.001       
128         32        32-bit    warp      89.830399         0.001         0.001       
256         64        32-bit    warp      88.863999         0.003         0.003       
512         128       32-bit    warp      89.686400         0.006         0.005       
1024        256       32-bit    warp      88.908798         0.012         0.010       
2048        512       32-bit    warp      88.819200         0.023         0.020       
4096        1024      32-bit    warp      89.670402         0.046         0.040       
8192        2048      32-bit    warp      88.889599         0.092         0.081       
16384       4096      32-bit    warp      88.972801         0.184         0.161       
32768       8192      32-bit    warp      89.564800         0.366         0.320       
65536       16384     32-bit    warp      89.888000         0.729         0.638       
#alltoall_device
size(B)     count     type      scope     latency(us)       algbw(GB/s)   busbw(GB/s) 
32          8         32-bit    block     89.747202         0.000         0.000       
64          16        32-bit    block     88.086402         0.001         0.001       
128         32        32-bit    block     87.254399         0.001         0.001       
256         64        32-bit    block     87.401599         0.003         0.003       
512         128       32-bit    block     88.095999         0.006         0.005       
1024        256       32-bit    block     87.273598         0.012         0.010       
2048        512       32-bit    block     88.086402         0.023         0.020       
4096        1024      32-bit    block     88.940799         0.046         0.040       
8192        2048      32-bit    block     88.095999         0.093         0.081       
16384       4096      32-bit    block     87.247998         0.188         0.164       
32768       8192      32-bit    block     88.976002         0.368         0.322       
65536       16384     32-bit    block     88.121599         0.744         0.651       
131072      32768     32-bit    block     90.579200         1.447         1.266       
262144      65536     32-bit    block     91.360003         2.869         2.511       
524288      131072    32-bit    block     101.145601        5.183         4.536       
1048576     262144    32-bit    block     111.052799        9.442         8.262       
2097152     524288    32-bit    block     137.164795        15.289        13.378      
4194304     1048576   32-bit    block     183.171201        22.898        20.036      
#alltoall_device
size(B)     count     type      scope     latency(us)       algbw(GB/s)   busbw(GB/s) 
64          8         64-bit    thread    111.955202        0.001         0.001       
128         16        64-bit    thread    113.420796        0.001         0.001       
256         32        64-bit    thread    108.508801        0.002         0.002       
512         64        64-bit    thread    110.204804        0.005         0.004       
1024        128       64-bit    thread    109.487998        0.009         0.008       
2048        256       64-bit    thread    109.462404        0.019         0.016       
4096        512       64-bit    thread    110.156798        0.037         0.033       
8192        1024      64-bit    thread    109.401596        0.075         0.066       
16384       2048      64-bit    thread    108.591998        0.151         0.132       
#alltoall_device
size(B)     count     type      scope     latency(us)       algbw(GB/s)   busbw(GB/s) 
64          8         64-bit    warp      88.896000         0.001         0.001       
128         16        64-bit    warp      89.679998         0.001         0.001       
256         32        64-bit    warp      88.950402         0.003         0.003       
512         64        64-bit    warp      89.606398         0.006         0.005       
1024        128       64-bit    warp      89.775997         0.011         0.010       
2048        256       64-bit    warp      88.838398         0.023         0.020       
4096        512       64-bit    warp      90.671998         0.045         0.040       
8192        1024      64-bit    warp      89.699203         0.091         0.080       
16384       2048      64-bit    warp      89.011198         0.184         0.161       
32768       4096      64-bit    warp      89.622402         0.366         0.320       
65536       8192      64-bit    warp      88.905603         0.737         0.645       
131072      16384     64-bit    warp      89.766401         1.460         1.278       
#alltoall_device
size(B)     count     type      scope     latency(us)       algbw(GB/s)   busbw(GB/s) 
64          8         64-bit    block     89.788800         0.001         0.001       
128         16        64-bit    block     88.012803         0.001         0.001       
256         32        64-bit    block     87.353599         0.003         0.003       
512         64        64-bit    block     88.000000         0.006         0.005       
1024        128       64-bit    block     87.225598         0.012         0.010       
2048        256       64-bit    block     87.225598         0.023         0.021       
4096        512       64-bit    block     87.168002         0.047         0.041       
8192        1024      64-bit    block     88.067198         0.093         0.081       
16384       2048      64-bit    block     88.863999         0.184         0.161       
32768       4096      64-bit    block     88.723201         0.369         0.323       
65536       8192      64-bit    block     87.993598         0.745         0.652       
131072      16384     64-bit    block     88.783997         1.476         1.292       
262144      32768     64-bit    block     91.366398         2.869         2.511       
524288      65536     64-bit    block     102.060795        5.137         4.495       
1048576     131072    64-bit    block     111.846399        9.375         8.203       
2097152     262144    64-bit    block     137.107205        15.296        13.384      
4194304     524288    64-bit    block     183.100796        22.907        20.044      
```
