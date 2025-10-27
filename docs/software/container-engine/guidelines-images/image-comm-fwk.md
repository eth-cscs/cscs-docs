[](){#ref-ce-guidelines-images-commfwk}
# Communication frameworks image

This page describes a container image providing foundational software components for achieving efficient execution on Alps nodes with NVIDIA GPUs.

The most important aspect to consider for performance of containerized applications is related to use of high-speed networks,
therefore this image mainly installs communication frameworks and libraries, besides general utility tools.
In particular, the [libfabric](https://ofiwg.github.io/libfabric/) framework (also known as Open Fabrics Interfaces - OFI) is required to interface applications with the Slingshot high-speed network.

At runtime, the container engine [CXI hook][ref-ce-cxi-hook] will replace the libfabric libraries inside the container with the corresponding libraries on the host system.
This will ensure access to the Slingshot interconnect.

This image is not intended to be used on its own, but to serve as a base to build higher-level software (e.g. MPI implementations) and application stacks.
For this reason, no performance results are provided in this page.

A build of this image is currently hosted on the [Quay.io](https://quay.io/) registry at the following reference:
`quay.io/ethcscs/comm-fwk:ofi1.22-ucx1.19-cuda12.8`.
The image name `comm-fwk` is a shortened form of "communication frameworks".

## Contents

- Ubuntu 24.04
- CUDA 12.8.1
- GDRCopy 2.5.1
- Libfabric 1.22.0
- UCX 1.19.0

## Containerfile
```Dockerfile
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

## Notes
- The image is based on an official NVIDIA CUDA image, and therefore already provides the NCCL library, alongside a complete CUDA installation.
- Communication frameworks are built with explicit support for CUDA and GDRCopy.
- The libfabric [EFA](https://aws.amazon.com/hpc/efa/) provider is included to leave open the possibility to experiment with derived images on AWS infrastructure as well.
- Although only the libfabric framework is required to support Alps' Slingshot network, this image also packages the UCX communication framework to allow building a broader set of software (e.g. some OpenSHMEM implementations) and supporting optimized Infiniband communication as well.
