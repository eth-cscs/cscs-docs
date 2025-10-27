[](){#ref-communication-libfabric}
# Libfabric

[Libfabric](https://ofiwg.github.io/libfabric/), or Open Fabrics Interfaces (OFI), is a low-level networking library that provides an abstract interface for networks.
Libfabric has backends for different network types, and is the interface chosen by HPE for the [Slingshot network on Alps][ref-alps-hsn], and by AWS for their [EFA network interface](https://aws.amazon.com/hpc/efa/).

To fully take advantage of the network on Alps:

* libfabric and its dependencies must be availailable in your environment (uenv or container);
* and, communication libraries like Cray MPICH, OpenMPI, NCCL, and RCCL have to be built or configured to use libfabric.

??? question "What about UCX?"
    [Unified Communication X (UCX)](https://openucx.org/) is a low level library that targets the same layer as libfabric.
    Specifically, it provides an open, standards-based, networking API.

    By targetting UCX and libfabric, MPI and NCCL do not need to implement low-level support for each network hardware.

    A downside of having two standards instead of one, is that pre-built software (for example Conda packages and Containers) have versions of MPI built for UCX, which does not provide a back end for Slingshot 11.
    Trying to run these images will lead to errors, or very poor performance.

## Using libfabric

### uenv

If you are using a uenv provided by CSCS, such as [prgenv-gnu][ref-uenv-prgenv-gnu], [Cray MPICH][ref-communication-cray-mpich] is linked to libfabric and the high speed network will be used.
No changes are required in applications.

### Container Engine

If you are using [containers][ref-container-engine], the simplest approach is to load libfabric into your container using the [CXI hook provided by the container engine][ref-ce-cxi-hook].

Alternatively, it is possible to build libfabric and its dependencies into your container.

!!! example "Installing libfabric in a container for NVIDIA nodes"
    The following lines demonstrate how to configure and 

    Note that it is assumed that CUDA has already been installed on the system.
    ```Dockerfile
    # Install libfabric
    ARG gdrcopy_version=2.5.1
    RUN git clone --depth 1 --branch v${gdrcopy_version} https://github.com/NVIDIA/gdrcopy.git \
        && cd gdrcopy \
        && export CUDA_PATH=${CUDA_HOME:-$(echo $(which nvcc) | grep -o '.*cuda')} \
        && make CC=gcc CUDA=$CUDA_PATH lib \
        && make lib_install \
        && cd ../ && rm -rf gdrcopy

    # Install libfabric
    ARG libfabric_version=1.22.0
    RUN git clone --branch v${libfabric_version} --depth 1 https://github.com/ofiwg/libfabric.git \
        && cd libfabric \
        && ./autogen.sh \
        && ./configure --prefix=/usr --with-cuda=/usr/local/cuda --enable-cuda-dlopen \
           --enable-gdrcopy-dlopen --enable-efa \
        && make -j$(nproc) \
        && make install \
        && ldconfig \
        && cd .. \
        && rm -rf libfabric
    ```

!!! todo
    In the above recipe `CUDA_PATH` is "calculated" for gdrcopy, and just hard coded to `/usr/loca/cuda` for libfabric.
    How about just hard-coding it everywhere, to simplify the recipe?

!!! todo
    Should we include the EFA and UCX support here? It is not needed to run on Alps, and might confuse readers.

??? note "The full containerfile for GH200"

    The containerfile below is based on the NVIDIA CUDA image, which provides a complete CUDA installation.

    - Communication frameworks are built with explicit support for CUDA and GDRCopy.

    Some additional features are enabled to increase the portability of the container to non-Alps systems:

    - The libfabric [EFA](https://aws.amazon.com/hpc/efa/) provider is configured using the `--enable-efa` compatibility for derived images on AWS infrastructure.
    - this image also packages the UCX communication framework to allow building a broader set of software (e.g. some OpenSHMEM implementations) and supporting optimized Infiniband communication as well.

    ```
    ARG ubuntu_version=24.04
    ARG cuda_version=12.8.1
    FROM docker.io/nvidia/cuda:${cuda_version}-cudnn-devel-ubuntu${ubuntu_version}

    RUN apt-get update \
        && DEBIAN_FRONTEND=noninteractive \
           apt-get install -y \
            build-essential \
            ca-certificates \
            pkg-config \
            automake \
            autoconf \
            libtool \
            cmake \
            gdb \
            strace \
            wget \
            git \
            bzip2 \
            python3 \
            gfortran \
            rdma-core \
            numactl \
            libconfig-dev \
            libuv1-dev \
            libfuse-dev \
            libfuse3-dev \
            libyaml-dev \
            libnl-3-dev \
            libnuma-dev \
            libsensors-dev \
            libcurl4-openssl-dev \
            libjson-c-dev \
            libibverbs-dev \
            --no-install-recommends \
        && rm -rf /var/lib/apt/lists/*

    ARG gdrcopy_version=2.5.1
    RUN git clone --depth 1 --branch v${gdrcopy_version} https://github.com/NVIDIA/gdrcopy.git \
        && cd gdrcopy \
        && export CUDA_PATH=${CUDA_HOME:-$(echo $(which nvcc) | grep -o '.*cuda')} \
        && make CC=gcc CUDA=$CUDA_PATH lib \
        && make lib_install \
        && cd ../ && rm -rf gdrcopy

    # Install libfabric
    ARG libfabric_version=1.22.0
    RUN git clone --branch v${libfabric_version} --depth 1 https://github.com/ofiwg/libfabric.git \
        && cd libfabric \
        && ./autogen.sh \
        && ./configure --prefix=/usr --with-cuda=/usr/local/cuda --enable-cuda-dlopen --enable-gdrcopy-dlopen --enable-efa \
        && make -j$(nproc) \
        && make install \
        && ldconfig \
        && cd .. \
        && rm -rf libfabric

    # Install UCX
    ARG UCX_VERSION=1.19.0
    RUN wget https://github.com/openucx/ucx/releases/download/v${UCX_VERSION}/ucx-${UCX_VERSION}.tar.gz \
        && tar xzf ucx-${UCX_VERSION}.tar.gz \
        && cd ucx-${UCX_VERSION} \
        && mkdir build \
        && cd build \
        && ../configure --prefix=/usr --with-cuda=/usr/local/cuda --with-gdrcopy=/usr/local --enable-mt --enable-devel-headers \
        && make -j$(nproc) \
        && make install \
        && cd ../.. \
        && rm -rf ucx-${UCX_VERSION}.tar.gz ucx-${UCX_VERSION}
    ```

## Tuning libfabric

Tuning libfabric (particularly together with [Cray MPICH][ref-communication-cray-mpich], [OpenMPI][ref-communication-openmpi], [NCCL][ref-communication-nccl], and [RCCL][ref-communication-rccl]) depends on many factors, including the application, workload, and system.
For a comprehensive overview libfabric options for the CXI provider (the provider for the Slingshot network), see the [`fi_cxi` man pages](https://ofiwg.github.io/libfabric/v2.1.0/man/fi_cxi.7.html).
Note that the exact version deployed on Alps may differ, and not all options may be applicable on Alps.

See the [Cray MPICH known issues page][ref-communication-cray-mpich-known-issues] for issues when using Cray MPICH together with libfabric.

!!! todo
    - add environment variable tuning guide
