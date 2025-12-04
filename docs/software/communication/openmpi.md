[](){#ref-communication-openmpi}
# OpenMPI

[Cray MPICH][ref-communication-cray-mpich] is the recommended MPI implementation on Alps, particularly if you are using [uenv][ref-uenv].

However, [OpenMPI](https://www.open-mpi.org/) can be used as an alternative in some cases, with limited support from CSCS.
OpenMPI is available for use in both uenv and containers.

To use OpenMPI on Alps, it must be built against [libfabric][ref-communication-libfabric] with support for the [Slingshot 11 network][ref-alps-hsn].

[](){#ref-communication-openmpi-using}
## Using OpenMPI

[](){#ref-communication-openmpi-uenv}
### uenv

!!! under-construction
    Building and using OpenMPI in uenv on Alps is work in progress.

    The instructions found on this page may be inaccurate, but are a good starting point to using OpenMPI on Alps.

OpenMPI is provided through a [uenv][ref-uenv] similar to [`prgenv-gnu`][ref-uenv-prgenv-gnu].
Once the uenv is loaded, compiling and linking with OpenMPI and libfabric is transparent.
At runtime, some additional options must be set to correctly use the Slingshot network.

First, when launching applications through Slurm, [PMIx](https://pmix.github.com) must be used for application launching.
This is done with the `--mpi` flag of `srun`:
```bash
srun --mpi=pmix ...
```

Additionally, the following environment variables should be set:
```bash
export PMIX_MCA_psec="native" # (1)!
export FI_PROVIDER="cxi"      # (2)!
export OMPI_MCA_pml="^ucx"    # (3)!
export OMPI_MCA_mtl="ofi"     # (4)!
```

1. Ensures PMIx uses the same security domain as Slurm. Otherwise PMIx will print warnings at startup.
2. Use the CXI (Slingshot) provider.
3. Use anything except [UCX](https://openucx.org/documentation/) for [point-to-point communication](https://docs.open-mpi.org/en/v5.0.x/mca.html#selecting-which-open-mpi-components-are-used-at-run-time). The `^` signals that OpenMPI should exclude all listed components.
4. Use libfabric for the [Matching Transport Layer](https://docs.open-mpi.org/en/v5.0.x/mca.html#frameworks).

!!! info "CXI provider does all communication through the network interface cards (NICs)"
    When using the libfabric CXI provider, all communication goes through NICs, including intra-node communication.
    This means that intra-node communication can not make use of shared memory optimizations and the maximum bandwidth will not be severely limited.

    Libfabric has a new [LINKx](https://ofiwg.github.io/libfabric/v2.1.0/man/fi_lnx.7.html) provider, which allows using different libfabric providers for inter- and intra-node communication.
    This provider is not as well tested, but can in theory perform better for intra-node communication, because it can use shared memory.
    To use the LINKx provider, set the following, instead of `FI_PROVIDER=cxi`:

    ```bash
    export FI_PROVIDER="lnx"           # (1)!
    export FI_LNX_PROV_LINKS="shm+cxi" # (2)!
    ```

    1. Use the libfabric LINKx provider, to allow using different libfabric providers for inter- and intra-node communication.
    2. Use the shared memory provider for intra-node communication and the CXI (Slingshot) provider for inter-node communication.

[](){#ref-communication-openmpi-ce}
### Containers

To install OpenMPI in a container, libfabric (and possibly UCX if the container should be portable to other centers), should be installed.
Then OpenMPI is built, and configured to use at least libfabric.
Note that OpenMPI v5 is the first version with full support for libfabric, required for good performance.

!!! note
    The version of MPI in the containers provided by NVIDIA is OpenMPI v4 provided by NVIDIA's [HPC-X](https://developer.nvidia.com/networking/hpc-x) toolkit.
    This version is not suitable for use on Alps for two reasons:

    * OpenMPI version 5 is required for full libfabric support.
    * It is linked against UCX only, and can't be modified to use the system libfabric.

    See the [performance section][ref-communication-openmpi-performance] below for examples of the level of performance loss caused by using HPC-X.


!!! example "Installing OpenMPI in a container for NVIDIA nodes"
    The following Dockerfile instructions install OpenMPI from source in an Ubuntu image that already contains CUDA, libfabric and UCX.

    ```Dockerfile
    --8<-- "docs/software/communication/dockerfiles/openmpi"
    ```

    * The `--with-ofi` and `--with-ucx` flags configure OpenMPI with the libfabric and UCX back ends respectively.
    * The `--enable-oshmem` flag builds OpenSHMEM as part of the OpenMPI installation, which is useful to support SHMEM implementations like [NVSHMEM][ref-communication-nvshmem].

    Expand the box below to see an example of a full Containerfile that can be used to create an OpenMPI container on the gh200 nodes of Alps:

    ??? note "The full Containerfile"
        This is an example of a complete Containerfile that installs OpenMPI based on the a "base image" that provides gdrcopy, libfabric and UCX on top of an NVIDIA container that provides CUDA:

        ```Dockerfile
        --8<-- "docs/software/communication/dockerfiles/base"
        --8<-- "docs/software/communication/dockerfiles/libfabric"
        --8<-- "docs/software/communication/dockerfiles/ucx"
        --8<-- "docs/software/communication/dockerfiles/openmpi"
        --8<-- "docs/software/communication/dockerfiles/osu"
        ```

        * The container also installs the [OSU MPI micro-benchmarks](https://mvapich.cse.ohio-state.edu/benchmarks) so that the implementation can be tested.

The EDF file for the container should contain the following:

```toml
[env]
PMIX_MCA_psec="native" # (1)!
```

1. Ensures PMIx uses the same security domain as Slurm. Otherwise PMIx will print warnings at startup.

!!! todo
    Above are the suggested environment variables from the CE pull request.
    Do we also set the environment variables in the uenv section above?

    We might want to consolidate these into a single location.

[](){#ref-communication-openmpi-performance}
## OpenMPI Performance

We present some performance numbers for OpenMPI, obtained using the OSU benchmarks compiled in the above image.

!!! warning "no version information available"
    The following warning message was generated by each rank running the benchmarks below, and can safely be ignored.
    ```
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    ```

The first performance benchmarks are for the OSU point-to-point bandwidth test `osu_bw`.

* inter-node tests place the two ranks on different nodes, so that all communication is over the Slingshot network
* intra-node tests place two ranks on the same node, so that communication is via NVLINK or memory copies in the CPU-CPU case

!!! note "impact of disabling the CXI hook"
    On many Alps vClusters, the Container Engine is configured with the [CXI hook][ref-ce-cxi-hook] enabled by default, enabling transparent access to the Slingshot interconnect.

    The inter node tests marked with `(*)` were run with the CXI container hook disabled, to demonstrate the effect of not using an optimised network configuration.
    If you see similar performance degradation in your tests, the first thing to investigate is whether your setup is using the libfabric optimised back end.

=== "CPU-to-CPU inter-node"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation
    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.95              Pass
    2                       1.90              Pass
    4                       3.80              Pass
    8                       7.61              Pass
    16                     15.21              Pass
    32                     30.47              Pass
    64                     60.72              Pass
    128                   121.56              Pass
    256                   242.28              Pass
    512                   484.54              Pass
    1024                  968.30              Pass
    2048                 1943.99              Pass
    4096                 3870.29              Pass
    8192                 6972.95              Pass
    16384               13922.36              Pass
    32768               18835.52              Pass
    65536               22049.82              Pass
    131072              23136.20              Pass
    262144              23555.35              Pass
    524288              23758.39              Pass
    1048576             23883.95              Pass
    2097152             23949.94              Pass
    4194304             23982.18              Pass
    ```

=== "CPU-to-CPU inter-node (*)"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi-no-cxi ./pt2pt/osu_bw --validation
    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.16              Pass
    2                       0.32              Pass
    4                       0.65              Pass
    8                       1.31              Pass
    16                      2.59              Pass
    32                      5.26              Pass
    64                     10.37              Pass
    128                    20.91              Pass
    256                    41.49              Pass
    512                    74.26              Pass
    1024                  123.99              Pass
    2048                  213.82              Pass
    4096                  356.13              Pass
    8192                  468.55              Pass
    16384                 505.89              Pass
    32768                 549.59              Pass
    65536                2170.64              Pass
    131072               2137.95              Pass
    262144               2469.63              Pass
    524288               2731.85              Pass
    1048576              2919.18              Pass
    2097152              3047.21              Pass
    4194304              3121.42              Pass
    ```

=== "GPU-to-GPU inter-node"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation D D
    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.90              Pass
    2                       1.82              Pass
    4                       3.65              Pass
    8                       7.30              Pass
    16                     14.56              Pass
    32                     29.03              Pass
    64                     57.49              Pass
    128                   118.30              Pass
    256                   227.18              Pass
    512                   461.26              Pass
    1024                  926.30              Pass
    2048                 1820.46              Pass
    4096                 3611.70              Pass
    8192                 6837.89              Pass
    16384               13361.25              Pass
    32768               18037.71              Pass
    65536               22019.46              Pass
    131072              23104.58              Pass
    262144              23542.71              Pass
    524288              23758.69              Pass
    1048576             23881.02              Pass
    2097152             23955.49              Pass
    4194304             23989.54              Pass
    ```

=== "GPU-to-GPU inter-node  (*)"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi-no-cxi ./pt2pt/osu_bw --validation D D
    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.06              Pass
    2                       0.12              Pass
    4                       0.24              Pass
    8                       0.48              Pass
    16                      0.95              Pass
    32                      1.91              Pass
    64                      3.85              Pass
    128                     7.57              Pass
    256                    15.28              Pass
    512                    19.87              Pass
    1024                   53.06              Pass
    2048                   97.29              Pass
    4096                  180.73              Pass
    8192                  343.75              Pass
    16384                 473.72              Pass
    32768                 530.81              Pass
    65536                1268.51              Pass
    131072               1080.83              Pass
    262144               1435.36              Pass
    524288               1526.12              Pass
    1048576              1727.31              Pass
    2097152              1755.61              Pass
    4194304              1802.75              Pass
    ```



=== "CPU-to-CPU intra-node"
    ```console
    $ srun -N1 -n2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation
    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.96              Pass
    2                       1.92              Pass
    4                       3.85              Pass
    8                       7.68              Pass
    16                     15.40              Pass
    32                     30.78              Pass
    64                     61.26              Pass
    128                   122.23              Pass
    256                   240.96              Pass
    512                   483.12              Pass
    1024                  966.52              Pass
    2048                 1938.09              Pass
    4096                 3873.67              Pass
    8192                 7100.56              Pass
    16384               14170.44              Pass
    32768               18607.68              Pass
    65536               21993.95              Pass
    131072              23082.11              Pass
    262144              23546.09              Pass
    524288              23745.05              Pass
    1048576             23879.79              Pass
    2097152             23947.23              Pass
    4194304             23980.15              Pass
    ```

=== "GPU-to-GPU intra-node"
    ```console
    $ srun -N1 -n2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation D D
    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.91              Pass
    2                       1.83              Pass
    4                       3.73              Pass
    8                       7.47              Pass
    16                     14.99              Pass
    32                     29.98              Pass
    64                     59.72              Pass
    128                   119.13              Pass
    256                   241.88              Pass
    512                   481.52              Pass
    1024                  963.60              Pass
    2048                 1917.15              Pass
    4096                 3840.96              Pass
    8192                 6942.05              Pass
    16384               13911.45              Pass
    32768               18379.14              Pass
    65536               21761.73              Pass
    131072              23069.72              Pass
    262144              23543.98              Pass
    524288              23750.83              Pass
    1048576             23882.44              Pass
    2097152             23951.34              Pass
    4194304             23989.44              Pass
    ```


Next is the all to all latency test `osu_alltoall`, for 8 ranks spread over nodes (4 ranks per node, 1 rank per GPU).

=== "CPU-to-CPU"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmix --environment=omb-ompi ./collective/osu_alltoall --validation
    # OSU MPI All-to-All Personalized Exchange Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                      12.46              Pass
    2                      12.05              Pass
    4                      11.99              Pass
    8                      11.84              Pass
    16                     11.87              Pass
    32                     11.84              Pass
    64                     11.95              Pass
    128                    12.22              Pass
    256                    13.21              Pass
    512                    13.23              Pass
    1024                   13.37              Pass
    2048                   13.52              Pass
    4096                   13.88              Pass
    8192                   17.32              Pass
    16384                  18.98              Pass
    32768                  23.72              Pass
    65536                  36.53              Pass
    131072                 62.96              Pass
    262144                119.44              Pass
    524288                236.43              Pass
    1048576               519.85              Pass
    ```

=== "CPU-to-CPU (*)"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmix --environment=omb-ompi-no-cxi ./collective/osu_alltoall --validation
    # OSU MPI All-to-All Personalized Exchange Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                     137.85              Pass
    2                     133.47              Pass
    4                     134.03              Pass
    8                     131.14              Pass
    16                    134.45              Pass
    32                    135.35              Pass
    64                    137.21              Pass
    128                   137.03              Pass
    256                   139.90              Pass
    512                   140.70              Pass
    1024                  165.05              Pass
    2048                  197.14              Pass
    4096                  255.02              Pass
    8192                  335.75              Pass
    16384                 543.12              Pass
    32768                 928.81              Pass
    65536                 782.28              Pass
    131072               1812.95              Pass
    262144               2284.26              Pass
    524288               3213.63              Pass
    1048576              5688.27              Pass
    ```

=== "GPU-to-GPU"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmix --environment=omb-ompi ./collective/osu_alltoall --validation -d cuda
    # OSU MPI-CUDA All-to-All Personalized Exchange Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                      22.26              Pass
    2                      22.08              Pass
    4                      22.15              Pass
    8                      22.19              Pass
    16                     22.25              Pass
    32                     22.11              Pass
    64                     22.22              Pass
    128                    21.98              Pass
    256                    22.19              Pass
    512                    22.20              Pass
    1024                   22.37              Pass
    2048                   22.58              Pass
    4096                   22.99              Pass
    8192                   27.22              Pass
    16384                  28.55              Pass
    32768                  32.60              Pass
    65536                  44.88              Pass
    131072                 70.15              Pass
    262144                123.30              Pass
    524288                234.89              Pass
    1048576               486.89              Pass
    ```

=== "GPU-to-GPU (*)"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmix --environment=omb-ompi-no-cxi ./collective/osu_alltoall --validation -d cuda
    # OSU MPI-CUDA All-to-All Personalized Exchange Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                     186.92              Pass
    2                     180.80              Pass
    4                     180.72              Pass
    8                     179.45              Pass
    16                    209.53              Pass
    32                    181.73              Pass
    64                    182.20              Pass
    128                   182.84              Pass
    256                   188.29              Pass
    512                   189.35              Pass
    1024                  237.31              Pass
    2048                  231.73              Pass
    4096                  298.73              Pass
    8192                  396.10              Pass
    16384                 589.72              Pass
    32768                 983.72              Pass
    65536                 786.48              Pass
    131072               1127.39              Pass
    262144               2144.57              Pass
    524288               3107.62              Pass
    1048576              5545.28              Pass
    ```
