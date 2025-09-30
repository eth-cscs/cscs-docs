[](){#ref-ce-guidelines-images-mpich}
# MPICH image

This page describes a container image featuring the MPICH library as MPI (Message Passing Interface) implementation, with support for CUDA and Libfabric.

This image is based on the [communication frameworks image][ref-ce-guidelines-images-commfwk], and thus it is suited for hosts with NVIDIA GPUs, like Alps GH200 nodes.

A build of this image is currently hosted on the [Quay.io](https://quay.io/) registry at the following reference:
`quay.io/ethcscs/mpich:4.3.1-ofi1.22-cuda12.8`.

## Contents

- Ubuntu 24.04
- CUDA 12.8.1
- GDRCopy 2.5.1
- Libfabric 1.22.0
- UCX 1.19.0
- MPICH 4.3.1

## Containerfile
```Dockerfile
FROM quay.io/ethcscs/comm-fwk:ofi1.22-ucx1.19-cuda12.8

ARG MPI_VER=4.3.1
RUN wget -q https://www.mpich.org/static/downloads/${MPI_VER}/mpich-${MPI_VER}.tar.gz \
    && tar xf mpich-${MPI_VER}.tar.gz \
    && cd mpich-${MPI_VER} \
    && ./autogen.sh \
    && ./configure --prefix=/usr --enable-fast=O3,ndebug \
       --disable-fortran --disable-cxx \
       --with-device=ch4:ofi --with-libfabric=/usr \
       --with-cuda=/usr/local/cuda \
       CFLAGS="-L/usr/local/cuda/targets/sbsa-linux/lib/stubs/ -lcuda" \
       CXXFLAGS="-L/usr/local/cuda/targets/sbsa-linux/lib/stubs/ -lcuda" \
    && make -j$(nproc) \
    && make install \
    && ldconfig \
    && cd .. \
    && rm -rf mpich-${MPI_VER}.tar.gz mpich-${MPI_VER}
```

!!! tip
    This image builds MPICH without Fortran and C++ bindings. In general, C++ bindings are deprecated by the MPI standard. If you require the Fortran bindings, remove the `--disable-fortran` option in the MPICH `configure` command above.


## Performance examples

In this section we demonstrate the performance of the previously created MPICH image using it to build the OSU Micro-Benchmarks 7.5.1, and deploying the resulting image on Alps through the Container Engine to run a variety of benchmarks.

A build of the image with the OSU benchmarks is available on the [Quay.io](https://quay.io/) registry at the following reference:
`quay.io/ethcscs/osu-mb:7.5-mpich4.3.1-ofi1.22-cuda12.8`.

### OSU-MB Containerfile
```Dockerfile
FROM quay.io/ethcscs/mpich:4.3.1-ofi1.22-cuda12.8

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
image = "quay.io#ethcscs/osu-mb:7.5-mpich4.3.1-ofi1.22-cuda12.8"
```

### Notes

- **Important:** To make sure that GPU-to-GPU performance is good for inter-node communication one must set the variable `MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1`.
  This setting can negatively impact performance for other types of communication (e.g. intra-node CPU-to-CPU transfers).
- Since by default MPICH uses PMI-1 or PMI-2 for wire-up and communication between ranks, when using this image the `srun` option `--mpi=pmi2` must be used to run successful multi-rank jobs.

### Results

=== "Point-to-point bandwidth, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmi2 --environment=omb-mpich ./pt2pt/osu_bw --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.88              Pass
    2                       1.76              Pass
    4                       3.53              Pass
    8                       7.07              Pass
    16                     14.16              Pass
    32                     27.76              Pass
    64                     56.80              Pass
    128                   113.27              Pass
    256                   225.42              Pass
    512                   445.70              Pass
    1024                  883.96              Pass
    2048                 1733.54              Pass
    4096                 3309.75              Pass
    8192                 6188.29              Pass
    16384               12415.59              Pass
    32768               19526.60              Pass
    65536               22624.33              Pass
    131072              23346.67              Pass
    262144              23671.41              Pass
    524288              23847.29              Pass
    1048576             23940.59              Pass
    2097152             23980.12              Pass
    4194304             24007.69              Pass
    ```

=== "Point-to-point bandwidth, GPU-to-GPU memory, inter-node communication"
    ```console
    $ MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1 srun -N2 --mpi=pmi2 --environment=omb-mpich ./pt2pt/osu_bw --validation D D
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.92              Pass
    2                       1.80              Pass
    4                       3.72              Pass
    8                       7.45              Pass
    16                     14.91              Pass
    32                     29.66              Pass
    64                     59.65              Pass
    128                   119.08              Pass
    256                   236.90              Pass
    512                   467.70              Pass
    1024                  930.74              Pass
    2048                 1808.56              Pass
    4096                 3461.06              Pass
    8192                 6385.63              Pass
    16384               12768.18              Pass
    32768               19332.39              Pass
    65536               22547.35              Pass
    131072              23297.26              Pass
    262144              23652.07              Pass
    524288              23812.58              Pass
    1048576             23913.85              Pass
    2097152             23971.55              Pass
    4194304             23998.79              Pass
    ```


=== "Point-to-point bandwidth, CPU-to-CPU memory, intra-node communication"
    ```console
    $ srun -N1 -n2 --mpi=pmi2 --environment=omb-mpich ./pt2pt/osu_bw --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       1.28              Pass
    2                       2.60              Pass
    4                       5.20              Pass
    8                      10.39              Pass
    16                     20.85              Pass
    32                     41.56              Pass
    64                     83.23              Pass
    128                   164.73              Pass
    256                   326.92              Pass
    512                   632.98              Pass
    1024                 1209.82              Pass
    2048                 2352.68              Pass
    4096                 4613.67              Pass
    8192                 8881.00              Pass
    16384                7435.51              Pass
    32768                9369.82              Pass
    65536               11644.51              Pass
    131072              13198.71              Pass
    262144              14058.41              Pass
    524288              12958.24              Pass
    1048576             12836.55              Pass
    2097152             13117.14              Pass
    4194304             13187.01              Pass
    ```


=== "Point-to-point bandwidth, GPU-to-GPU memory, intra-node communication"
    ```console
    $ srun -N1 -n2 --mpi=pmi2 --environment=omb-mpich ./pt2pt/osu_bw --validation D D
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.13              Pass
    2                       0.27              Pass
    4                       0.55              Pass
    8                       1.10              Pass
    16                      2.20              Pass
    32                      4.40              Pass
    64                      8.77              Pass
    128                    17.50              Pass
    256                    35.01              Pass
    512                    70.14              Pass
    1024                  140.35              Pass
    2048                  278.91              Pass
    4096                  555.96              Pass
    8192                 1104.97              Pass
    16384                2214.87              Pass
    32768                4422.67              Pass
    65536                8833.18              Pass
    131072              17765.30              Pass
    262144              33834.24              Pass
    524288              59704.15              Pass
    1048576             84566.94              Pass
    2097152            102221.49              Pass
    4194304            113955.83              Pass
    ```


=== "Point-to-point bi-directional bandwidth, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmi2 --environment=omb-mpich ./pt2pt/osu_bibw --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI Bi-Directional Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       1.03              Pass
    2                       2.07              Pass
    4                       4.14              Pass
    8                       8.28              Pass
    16                     16.54              Pass
    32                     33.07              Pass
    64                     66.08              Pass
    128                   131.65              Pass
    256                   258.60              Pass
    512                   518.60              Pass
    1024                 1036.09              Pass
    2048                 2072.16              Pass
    4096                 4142.18              Pass
    8192                 7551.70              Pass
    16384               14953.49              Pass
    32768               23871.35              Pass
    65536               33767.12              Pass
    131072              39284.40              Pass
    262144              42638.43              Pass
    524288              44602.52              Pass
    1048576             45621.16              Pass
    2097152             46159.65              Pass
    4194304             46433.80              Pass
    ```


=== "Point-to-point bi-directional bandwidth, GPU-to-GPU memory, inter-node communication"
    ```console
    $ MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1 srun -N2 --mpi=pmi2 --environment=omb-mpich ./pt2pt/osu_bibw --validation D D
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_bibw: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI-CUDA Bi-Directional Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       1.05              Pass
    2                       2.10              Pass
    4                       4.20              Pass
    8                       8.40              Pass
    16                     16.84              Pass
    32                     33.63              Pass
    64                     67.01              Pass
    128                   132.11              Pass
    256                   258.74              Pass
    512                   515.52              Pass
    1024                 1025.44              Pass
    2048                 2019.51              Pass
    4096                 3844.87              Pass
    8192                 6123.96              Pass
    16384               13244.25              Pass
    32768               22521.76              Pass
    65536               34040.97              Pass
    131072              39503.52              Pass
    262144              42827.91              Pass
    524288              44663.44              Pass
    1048576             45629.24              Pass
    2097152             46167.41              Pass
    4194304             46437.18              Pass
    ```


=== "Point-to-point latency, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmi2 --environment=omb-mpich ./pt2pt/osu_latency --validation
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_latency: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)
    /usr/local/libexec/osu-micro-benchmarks/mpi/./pt2pt/osu_latency: /usr/lib/aarch64-linux-gnu/libnl-3.so.200: no version information available (required by /usr/lib64/libcxi.so.1)

    # OSU MPI Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                       3.00              Pass
    2                       2.99              Pass
    4                       2.99              Pass
    8                       3.07              Pass
    16                      2.99              Pass
    32                      3.08              Pass
    64                      3.01              Pass
    128                     3.88              Pass
    256                     4.43              Pass
    512                     4.62              Pass
    1024                    4.47              Pass
    2048                    4.57              Pass
    4096                    4.79              Pass
    8192                    7.92              Pass
    16384                   8.53              Pass
    32768                   9.48              Pass
    65536                  10.92              Pass
    131072                 13.84              Pass
    262144                 19.19              Pass
    524288                 30.05              Pass
    1048576                51.73              Pass
    2097152                94.94              Pass
    4194304               181.46              Pass
    ```


=== "All-to-all collective latency, CPU-to-CPU memory, multiple nodes"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmi2 --environment=omb-mpich ./collective/osu_alltoall --validation
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
    1                      22.25              Pass
    2                      22.34              Pass
    4                      21.83              Pass
    8                      21.72              Pass
    16                     21.74              Pass
    32                     21.71              Pass
    64                     22.02              Pass
    128                    22.35              Pass
    256                    22.84              Pass
    512                    23.42              Pass
    1024                   24.61              Pass
    2048                   24.99              Pass
    4096                   26.02              Pass
    8192                   29.17              Pass
    16384                  68.81              Pass
    32768                  95.63              Pass
    65536                 181.42              Pass
    131072                306.83              Pass
    262144                526.50              Pass
    524288                960.52              Pass
    1048576              1823.52              Pass
    ```


=== "All-to-all collective latency, GPU-to-GPU memory, multiple nodes"
    ```console
    $ MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1 srun -N2 --ntasks-per-node=4 --mpi=pmi2 --environment=omb-mpich ./collective/osu_alltoall --validation -d cuda
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
    1                      65.62              Pass
    2                      65.51              Pass
    4                      65.46              Pass
    8                      65.40              Pass
    16                     65.58              Pass
    32                     64.97              Pass
    64                     65.01              Pass
    128                    65.31              Pass
    256                    65.03              Pass
    512                    65.14              Pass
    1024                   65.67              Pass
    2048                   66.23              Pass
    4096                   66.69              Pass
    8192                   67.47              Pass
    16384                  85.99              Pass
    32768                 103.15              Pass
    65536                 120.40              Pass
    131072                135.64              Pass
    262144                162.24              Pass
    524288                213.84              Pass
    1048576               317.07              Pass
    ```


### Results without the CXI hook
On many Alps vClusters, the Container Engine is configured with the CXI hook enabled by default, enabling transparent access to the Slingshot interconnect.

This section demonstrates the performance benefit of the CXI hook by explicitly disabling it through the EDF:
```console
$ cat .edf/omb-mpich-no-cxi.toml 
image = "quay.io#ethcscs/osu-mb:7.5-mpich4.3.1-ofi1.22-cuda12.8"

[annotations]
com.hooks.cxi.enabled="false"
```

=== "Point-to-point bandwidth, CPU-to-CPU memory, inter-node communication"
    ```console
   $ srun -N2 --mpi=pmi2 --environment=omb-mpich-no-cxi ./pt2pt/osu_bw --validation

    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.14              Pass
    2                       0.28              Pass
    4                       0.56              Pass
    8                       1.15              Pass
    16                      2.32              Pass
    32                      4.55              Pass
    64                      9.36              Pass
    128                    18.20              Pass
    256                    20.26              Pass
    512                    39.11              Pass
    1024                   55.88              Pass
    2048                  108.19              Pass
    4096                  142.91              Pass
    8192                  393.95              Pass
    16384                 307.93              Pass
    32768                1205.61              Pass
    65536                1723.86              Pass
    131072               2376.59              Pass
    262144               2847.85              Pass
    524288               3277.75              Pass
    1048576              3580.23              Pass
    2097152              3697.47              Pass
    4194304              3764.11              Pass
    ```

=== "Point-to-point bandwidth, GPU-to-GPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmi2 --environment=omb-mpich-no-cxi ./pt2pt/osu_bw --validation D D

    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)        Validation
    1                       0.04              Pass
    2                       0.08              Pass
    4                       0.16              Pass
    8                       0.31              Pass
    16                      0.62              Pass
    32                      1.24              Pass
    64                      2.46              Pass
    128                     4.80              Pass
    256                     7.33              Pass
    512                    14.40              Pass
    1024                   24.43              Pass
    2048                   47.68              Pass
    4096                   85.40              Pass
    8192                  161.68              Pass
    16384                 306.15              Pass
    32768                 520.57              Pass
    65536                 818.99              Pass
    131072               1160.48              Pass
    262144               1436.44              Pass
    524288               1676.61              Pass
    1048576              2003.55              Pass
    2097152              2104.65              Pass
    4194304              2271.56              Pass
    ```

=== "Point-to-point latency, CPU-to-CPU memory, inter-node communication"
    ```console
    $ srun -N2 --mpi=pmi2 --environment=omb-mpich-no-cxi ./pt2pt/osu_latency --validation

    # OSU MPI Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                      38.25              Pass
    2                      38.58              Pass
    4                      38.49              Pass
    8                      38.43              Pass
    16                     38.40              Pass
    32                     38.49              Pass
    64                     39.18              Pass
    128                    39.23              Pass
    256                    45.17              Pass
    512                    53.49              Pass
    1024                   59.60              Pass
    2048                   48.83              Pass
    4096                   50.84              Pass
    8192                   51.45              Pass
    16384                  52.35              Pass
    32768                  58.92              Pass
    65536                  74.88              Pass
    131072                100.32              Pass
    262144                135.35              Pass
    524288                219.52              Pass
    1048576               384.61              Pass
    2097152               706.79              Pass
    4194304              1341.79              Pass
    ```


=== "All-to-all collective latency, CPU-to-CPU memory, multiple nodes"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmi2 --environment=omb-mpich-no-cxi ./collective/osu_alltoall --validation

    # OSU MPI All-to-All Personalized Exchange Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                     169.19              Pass
    2                     169.50              Pass
    4                     170.35              Pass
    8                     168.81              Pass
    16                    169.71              Pass
    32                    169.60              Pass
    64                    169.47              Pass
    128                   171.48              Pass
    256                   334.47              Pass
    512                   343.06              Pass
    1024                  703.55              Pass
    2048                  449.30              Pass
    4096                  454.68              Pass
    8192                  468.90              Pass
    16384                 532.46              Pass
    32768                 578.95              Pass
    65536                1164.92              Pass
    131072               1511.04              Pass
    262144               2287.48              Pass
    524288               3668.35              Pass
    1048576              6498.36              Pass
    ```


=== "All-to-all collective latency, GPU-to-GPU memory, multiple nodes"
    ```console
    $ srun -N2 --ntasks-per-node=4 --mpi=pmi2 --environment=omb-mpich-no-cxi ./collective/osu_alltoall --validation -d cuda

    # OSU MPI-CUDA All-to-All Personalized Exchange Latency Test v7.5
    # Datatype: MPI_CHAR.
    # Size       Avg Latency(us)        Validation
    1                     276.29              Pass
    2                     273.94              Pass
    4                     273.53              Pass
    8                     273.88              Pass
    16                    274.83              Pass
    32                    274.90              Pass
    64                    276.85              Pass
    128                   278.17              Pass
    256                   413.21              Pass
    512                   442.62              Pass
    1024                  793.14              Pass
    2048                  547.57              Pass
    4096                  561.82              Pass
    8192                  570.71              Pass
    16384                 624.20              Pass
    32768                 657.30              Pass
    65536                1168.43              Pass
    131072               1451.91              Pass
    262144               2049.24              Pass
    524288               3061.54              Pass
    1048576              5238.24              Pass
    ```
