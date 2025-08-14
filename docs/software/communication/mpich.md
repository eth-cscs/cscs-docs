[](){#ref-communication-mpich}
# MPICH

MPICH is an open-source MPI implementation actively developed in this [github repository](https://github.com/pmodels/mpich).
It can be installed inside containers directly from the source code manually, or using Spack or similar package managers.

## MPICH inside containers
MPICH can be built inside containers, however for native Slingshot performance special care has to be taken, to ensure that communication is optimal for all cases:

* Intra-node communication (this is via shared memory, especially `xpmem`)
* Inter-node communication (this should go through the OpenFabrics Interface - OFI)
* Host-to-Host memory communication
* Device-to-Device memory communication

To achieve native performance one needs to ensure to build MPICH with `libfabric` and `xpmem` support.
Additionally, when building for GH200 nodes one needs to ensure to build `libfabric` and `mpich` with `CUDA` support.

At container runtime the [CXI hook][ref-ce-cxi-hook] will replace the libraries `xpmem` and `libfabric` inside the container, with the libraries on the host system.
This will ensure native performance when doing MPI communication.

These are example Dockerfiles that can be used on [Eiger][ref-cluster-eiger] and [Daint][ref-cluster-daint] to build a container image with MPICH and best communication performance.

They are quite explicit and building manually the necessary packages, however for real-life one should fall back to Spack to do the building.
=== "Dockerfile.cpu"
    ```Dockerfile
    FROM docker.io/ubuntu:24.04

    ARG libfabric_version=1.22.0
    ARG mpi_version=4.3.1
    ARG osu_version=7.5.1

    RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential ca-certificates automake autoconf libtool make gdb strace wget python3 git gfortran \
        && rm -rf /var/lib/apt/lists/*

    RUN git clone https://github.com/hpc/xpmem \
        && cd xpmem/lib \
        && gcc -I../include -shared -o libxpmem.so.1 libxpmem.c \
        && ln -s libxpmem.so.1 libxpmem.so \
        && mv libxpmem.so* /usr/lib64 \
        && cp ../include/xpmem.h /usr/include/ \
        && ldconfig \
        && cd ../../ \
        && rm -Rf xpmem

    RUN wget -q https://github.com/ofiwg/libfabric/archive/v${libfabric_version}.tar.gz \
        && tar xf v${libfabric_version}.tar.gz \
        && cd libfabric-${libfabric_version} \
        && ./autogen.sh \
        && ./configure --prefix=/usr \
        && make -j$(nproc) \
        && make install \
        && ldconfig \
        && cd .. \
        && rm -rf v${libfabric_version}.tar.gz libfabric-${libfabric_version}

    RUN wget -q https://www.mpich.org/static/downloads/${mpi_version}/mpich-${mpi_version}.tar.gz \
        && tar xf mpich-${mpi_version}.tar.gz \
        && cd mpich-${mpi_version} \
        && ./autogen.sh \
        && ./configure --prefix=/usr --enable-fast=O3,ndebug --enable-fortran --enable-cxx --with-device=ch4:ofi --with-libfabric=/usr --with-xpmem=/usr \
        && make -j$(nproc) \
        && make install \
        && ldconfig \
        && cd .. \
        && rm -rf mpich-${mpi_version}.tar.gz mpich-${mpi_version}

    RUN wget -q http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-v${osu_version}.tar.gz \
        && tar xf osu-micro-benchmarks-v${osu_version}.tar.gz \
        && cd osu-micro-benchmarks-v${osu_version} \
        && ./configure --prefix=/usr/local CC=$(which mpicc) CFLAGS=-O3 \
        && make -j$(nproc) \
        && make install \
        && cd .. \
        && rm -rf osu-micro-benchmarks-v${osu_version} osu-micro-benchmarks-v${osu_version}.tar.gz
    ```

=== "Dockerfile.gpu"
    ```Dockerfile
    FROM docker.io/nvidia/cuda:12.8.1-devel-ubuntu24.04

    ARG libfabric_version=1.22.0
    ARG mpi_version=4.3.1
    ARG osu_version=7.5.1

    RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends build-essential ca-certificates automake autoconf libtool make gdb strace wget python3 git gfortran \
        && rm -rf /var/lib/apt/lists/*

    RUN echo '/usr/local/cuda/lib64/stubs' > /etc/ld.so.conf.d/cuda_stubs.conf && ldconfig

    RUN git clone https://github.com/hpc/xpmem \
        && cd xpmem/lib \
        && gcc -I../include -shared -o libxpmem.so.1 libxpmem.c \
        && ln -s libxpmem.so.1 libxpmem.so \
        && mv libxpmem.so* /usr/lib \
        && cp ../include/xpmem.h /usr/include/ \
        && ldconfig \
        && cd ../../ \
        && rm -Rf xpmem

    RUN wget -q https://github.com/ofiwg/libfabric/archive/v${libfabric_version}.tar.gz \
        && tar xf v${libfabric_version}.tar.gz \
        && cd libfabric-${libfabric_version} \
        && ./autogen.sh \
        && ./configure --prefix=/usr --with-cuda=/usr/local/cuda \
        && make -j$(nproc) \
        && make install \
        && ldconfig \
        && cd .. \
        && rm -rf v${libfabric_version}.tar.gz libfabric-${libfabric_version}

    RUN wget -q https://www.mpich.org/static/downloads/${mpi_version}/mpich-${mpi_version}.tar.gz \
        && tar xf mpich-${mpi_version}.tar.gz \
        && cd mpich-${mpi_version} \
        && ./autogen.sh \
        && ./configure --prefix=/usr --enable-fast=O3,ndebug --enable-fortran --enable-cxx --with-device=ch4:ofi --with-libfabric=/usr --with-xpmem=/usr --with-cuda=/usr/local/cuda \
        && make -j$(nproc) \
        && make install \
        && ldconfig \
        && cd .. \
        && rm -rf mpich-${mpi_version}.tar.gz mpich-${mpi_version}

    RUN wget -q http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-v${osu_version}.tar.gz \
        && tar xf osu-micro-benchmarks-v${osu_version}.tar.gz \
        && cd osu-micro-benchmarks-v${osu_version} \
        && ./configure --prefix=/usr/local --with-cuda=/usr/local/cuda CC=$(which mpicc) CFLAGS=-O3 \
        && make -j$(nproc) \
        && make install \
        && cd .. \
        && rm -rf osu-micro-benchmarks-v${osu_version} osu-micro-benchmarks-v${osu_version}.tar.gz

    RUN rm /etc/ld.so.conf.d/cuda_stubs.conf && ldconfig
    ```

!!! important "GPU-to-GPU inter-node communication"
    To make sure that GPU-to-GPU performance is good for inter-node communication one must set the variable
    ```console
    $ export MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1
    ```

Once the container is built and pushed to a registry, one can create a [container environment][ref-container-engine].
To verify performance, one can run the `osu_bw` benchmark, which is doing a bandwidth benchmark for different message sizes between two ranks.
For reference this is the expected performance for different memory residency, with inter-node and intra-node communication:
=== "CPU-to-CPU memory intra-node"
    ```console
    $ export MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1
    $ srun --mpi=pmi2 -t00:05:00 --environment=$PWD/osu_gpu.toml -n2 -N1 /usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw H H
    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)
    1                       1.19
    2                       2.37
    4                       4.78
    8                       9.61
    16                      8.71
    32                     38.38
    64                     76.89
    128                   152.89
    256                   303.63
    512                   586.09
    1024                 1147.26
    2048                 2218.82
    4096                 4303.92
    8192                 8165.95
    16384                7178.94
    32768                9574.09
    65536               43786.86
    131072              53202.36
    262144              64046.90
    524288              60504.75
    1048576             36400.29
    2097152             28694.38
    4194304             23906.16
    ```

=== "CPU-to-CPU memory inter-node"
    ```console
    $ export MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1
    $ srun --mpi=pmi2 -t00:05:00 --environment=$PWD/osu_gpu.toml -n2 -N2 /usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw H H
    # OSU MPI Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)
    1                       0.97
    2                       1.95
    4                       3.91
    8                       7.80
    16                     15.67
    32                     31.24
    64                     62.58
    128                   124.99
    256                   249.13
    512                   499.63
    1024                 1009.57
    2048                 1989.46
    4096                 3996.43
    8192                 7139.42
    16384               14178.70
    32768               18920.35
    65536               22169.18
    131072              23226.08
    262144              23627.48
    524288              23838.28
    1048576             23951.16
    2097152             24007.73
    4194304             24037.14
    ```

=== "GPU-to-GPU memory intra-node"
    ```console
    $ export MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1
    $ srun --mpi=pmi2 -t00:05:00 --environment=$PWD/osu_gpu.toml -n2 -N1 /usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw D D
    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)
    1                       0.14
    2                       0.29
    4                       0.58
    8                       1.16
    16                      2.37
    32                      4.77
    64                      9.87
    128                    19.77
    256                    39.52
    512                    78.29
    1024                  158.19
    2048                  315.93
    4096                  633.14
    8192                 1264.69
    16384                2543.21
    32768                5051.02
    65536               10069.17
    131072              20178.56
    262144              38102.36
    524288              64397.91
    1048576             84937.73
    2097152            104723.15
    4194304            115214.94
    ```

=== "GPU-to-GPU memory inter-node"
    ```console
    $ export MPIR_CVAR_CH4_OFI_ENABLE_HMEM=1
    $ srun --mpi=pmi2 -t00:05:00 --environment=$PWD/osu_gpu.toml -n2 -N2 /usr/local/libexec/osu-micro-benchmarks/mpi/pt2pt/osu_bw D D
    # OSU MPI-CUDA Bandwidth Test v7.5
    # Datatype: MPI_CHAR.
    # Size      Bandwidth (MB/s)
    1                       0.09
    2                       0.18
    4                       0.37
    8                       0.74
    16                      1.48
    32                      2.96
    64                      5.91
    128                    11.80
    256                   227.08
    512                   463.72
    1024                  923.58
    2048                 1740.73
    4096                 3505.87
    8192                 6351.56
    16384               13377.55
    32768               17226.43
    65536               21416.23
    131072              22733.04
    262144              23335.00
    524288              23624.70
    1048576             23821.72
    2097152             23928.62
    4194304             23974.34
    ```
