[](){#ref-ce-guidelines-images-ompi}
# OpenMPI image

This page describes a container image featuring the OpenMPI library as MPI (Message Passing Interface) implementation, with support for CUDA, Libfabric and UCX.

This image is based on the [communication frameworks image][ref-ce-guidelines-images-commfwk], and thus it is suited for hosts with NVIDIA GPUs, like Alps GH200 nodes.

A build of this image is currently hosted on the [Quay.io](https://quay.io/) registry at the following reference:
`quay.io/ethcscs/ompi:5.0.8-ofi1.22-cuda12.8`.

## Contents

- Ubuntu 24.04
- CUDA 12.8.1
- GDRCopy 2.5.1
- Libfabric 1.22.0
- UCX 1.19.0
- OpenMPI 5.0.8

## Containerfile
```Dockerfile
FROM quay.io/ethcscs/comm-fwk:ofi1.22-ucx1.19-cuda12.8

ARG OMPI_VER=5.0.8
RUN wget -q https://download.open-mpi.org/release/open-mpi/v5.0/openmpi-${OMPI_VER}.tar.gz \
    && tar xf openmpi-${OMPI_VER}.tar.gz \
    && cd openmpi-${OMPI_VER} \
    && ./configure --prefix=/usr --with-ofi=/usr --with-ucx=/usr --enable-oshmem \
       --with-cuda=/usr/local/cuda --with-cuda-libdir=/usr/local/cuda/lib64/stubs \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf openmpi-${OMPI_VER}.tar.gz openmpi-${OMPI_VER}
```

!!! note
    This image builds OpenSHMEM as part of the OpenMPI installation. This can be useful to support other SHMEM implementations like NVSHMEM.

## Performance examples

In this section we demonstrate the performance of the previously created OpenMPI image using it to build the OSU Micro-Benchmarks 7.5.1, and deploying the resulting image on Alps through the Container Engine to run a variety of benchmarks.

A build of the image with the OSU benchmarks is available on the [Quay.io](https://quay.io/) registry at the following reference:
`quay.io/ethcscs/osu-mb:7.5-ompi5.0.8-ofi1.22-cuda12.8`.

### OSU-MB Containerfile
```Dockerfile
FROM quay.io/ethcscs/ompi:5.0.8-ofi1.22-cuda12.8

ARG omb_version=7.5.1
RUN wget -q http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-${omb_version}.tar.gz \
    && tar xf osu-micro-benchmarks-${omb_version}.tar.gz \
    && cd osu-micro-benchmarks-${omb_version} \
    && ldconfig /usr/local/cuda/targets/sbsa-linux/lib/stubs \
    && ./configure --prefix=/usr/local CC=$(which mpicc) CFLAGS="-O3 -lcuda -lnvidia-ml" \
                   --enable-cuda --with-cuda-include=/usr/local/cuda/include \
                   --with-cuda-libpath=/usr/local/cuda/lib64 \
                   CXXFLAGS="-lmpi -lcuda" \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf osu-micro-benchmarks-${omb_version} osu-micro-benchmarks-${omb_version}.tar.gz

WORKDIR /usr/local/libexec/osu-micro-benchmarks/mpi
```

### Environment Definition File
```toml
image = "quay.io#ethcscs/osu-mb:7.5-ompi5.0.8-ofi1.22-cuda12.8"

[env]
PMIX_MCA_psec="native"
```

### Notes

- Since OpenMPI uses PMIx for wire-up and communication between ranks, when using this image the `srun` option `--mpi=pmix` must be used to run successful multi-rank jobs.

### Results

=== "Point-to-point bandwidth, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

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

=== "Point-to-point bandwidth, GPU-to-GPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation D D
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

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


=== "Point-to-point bandwidth, CPU-to-CPU memory, intra-node communication"
    ```console
    $ srun -N1 -n2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

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


=== "Point-to-point bandwidth, GPU-to-GPU memory, intra-node communication"
    ```console
    $ srun -N1 -n2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bw --validation D D
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

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


=== "Point-to-point bi-directional bandwidth, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bibw --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI Bi-Directional Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.93              Pass
    2                       1.94              Pass
    4                       3.89              Pass
    8                       7.77              Pass
    16                     15.61              Pass
    32                     30.94              Pass
    64                     62.10              Pass
    128                   123.73              Pass
    256                   247.77              Pass
    512                   495.33              Pass
    1024                  988.33              Pass
    2048                 1977.44              Pass
    4096                 3953.82              Pass
    8192                 7252.82              Pass
    16384               14434.94              Pass
    32768               23610.53              Pass
    65536               33290.72              Pass
    131072              39024.03              Pass
    262144              42508.16              Pass
    524288              44482.65              Pass
    1048576             45575.40              Pass
    2097152             46124.45              Pass
    4194304             46417.59              Pass
    ```


=== "Point-to-point bi-directional bandwidth, GPU-to-GPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_bibw --validation D D
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI-CUDA Bi-Directional Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.97              Pass
    2                       1.94              Pass
    4                       3.89              Pass
    8                       7.75              Pass
    16                     15.55              Pass
    32                     31.11              Pass
    64                     61.95              Pass
    128                   123.35              Pass
    256                   250.91              Pass
    512                   500.80              Pass
    1024                 1002.29              Pass
    2048                 2003.24              Pass
    4096                 4014.15              Pass
    8192                 7289.11              Pass
    16384               14717.42              Pass
    32768               22467.65              Pass
    65536               33136.69              Pass
    131072              38970.21              Pass
    262144              42501.28              Pass
    524288              44466.34              Pass
    1048576             45554.48              Pass
    2097152             46124.56              Pass
    4194304             46417.53              Pass
    ```


=== "Point-to-point latency, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi ./pt2pt/osu_latency --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_latency: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_latency: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                       3.34              Pass
    2                       3.34              Pass
    4                       3.35              Pass
    8                       3.34              Pass
    16                      3.33              Pass
    32                      3.34              Pass
    64                      3.33              Pass
    128                     4.32              Pass
    256                     4.36              Pass
    512                     4.40              Pass
    1024                    4.46              Pass
    2048                    4.61              Pass
    4096                    4.89              Pass
    8192                    8.31              Pass
    16384                   8.95              Pass
    32768                   9.76              Pass
    65536                  11.16              Pass
    131072                 13.98              Pass
    262144                 19.41              Pass
    524288                 30.21              Pass
    1048576                52.12              Pass
    2097152                95.26              Pass
    4194304               182.39              Pass
    ```


=== "All-to-all collective latency, CPU-to-CPU memory, multiple nodes"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmix --environment=omb-ompi ./collective/osu_alltoall --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

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


=== "All-to-all collective latency, GPU-to-GPU memory, multiple nodes"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmix --environment=omb-ompi ./collective/osu_alltoall --validation -d cuda
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./collective/osu_alltoall: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

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


### Results without the CXI hook
On many Alps vClusters, the Container Engine is configured with the CXI hook enabled by default, enabling transparent access to the Slingshot interconnect.

This section demonstrates the performance benefit of the CXI hook by explicitly disabling it through the EDF:
```console
$ cat .edf/omb-ompi-no-cxi.toml 
image = "quay.io#ethcscs/osu-mb:7.5-ompi5.0.8-ofi1.22-cuda12.8"

[env]
PMIX_MCA_psec="native"

[annotations]
com.hooks.cxi.enabled="false"
```

=== "Point-to-point bandwidth, CPU-to-CPU memory, inter-node communication"
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

=== "Point-to-point bandwidth, GPU-to-GPU memory, inter-node communication"
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

=== "Point-to-point latency, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmix --environment=omb-ompi-no-cxi ./pt2pt/osu_latency --validation

    # OSU MPI Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                      28.92              Pass
    2                      28.99              Pass
    4                      29.07              Pass
    8                      29.13              Pass
    16                     29.48              Pass
    32                     29.18              Pass
    64                     29.39              Pass
    128                    30.11              Pass
    256                    32.10              Pass
    512                    34.07              Pass
    1024                   38.36              Pass
    2048                   61.00              Pass
    4096                   81.04              Pass
    8192                   80.11              Pass
    16384                 126.99              Pass
    32768                 124.97              Pass
    65536                 123.84              Pass
    131072                207.48              Pass
    262144                252.43              Pass
    524288                319.47              Pass
    1048576               497.84              Pass
    2097152               956.03              Pass
    4194304              1455.18              Pass
    ```


=== "All-to-all collective latency, CPU-to-CPU memory, multiple nodes"
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


=== "All-to-all collective latency, GPU-to-GPU memory, multiple nodes"
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
