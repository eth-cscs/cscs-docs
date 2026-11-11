# Libfabric

[Libfabric](<https://ofiwg.github.io/libfabric/>), or Open Fabrics Interfaces (OFI), is a low-level networking library that provides an abstract interface for networks. Libfabric has backends for different network types, and is the interface chosen by HPE for the [Slingshot network on Alps](<https://docs.cscs.ch/alps/hardware/index.md#alps-high-speed-network> "Alps High Speed Network"), and by AWS for their [EFA network interface](<https://aws.amazon.com/hpc/efa/>).

To fully take advantage of the network on Alps:

- libfabric and its dependencies must be available in your environment (uenv or container);
- and, communication libraries in your environment like Cray MPICH, OpenMPI, NCCL, and NVSHMEM have to be built or configured to use libfabric.

> [!NOTE]
>
> **What about UCX?**
>
> [Unified Communication X (UCX)](<https://openucx.org/>) is a low level library that targets the same layer as libfabric. Specifically, it provides an open, standards-based, networking API. By targeting UCX and libfabric, MPI and NCCL do not need to implement low-level support for each network hardware.
>
> **There is no UCX back end for the Slingshot network on Alps**, and pre-built software (for example conda packages and containers) often provides versions of MPI built for UCX only. Running these images and packages on Alps will lead to very poor network performance or errors.

## Using libfabric

### uenv

If you are using a uenv provided by CSCS, such as [prgenv-gnu](<https://docs.cscs.ch/software/prgenv/prgenv-gnu/index.md#prgenv-gnu>), [Cray MPICH](<https://docs.cscs.ch/software/communication/cray-mpich/index.md#cray-mpich>) is linked to libfabric and the high speed network will be used. No changes are required in applications.

### Containers

The approach is to install libfabric inside the container, along with MPI and NCCL implementations linked against it. At runtime, the [container engine](<https://docs.cscs.ch/software/container-engine/index.md#container-engine> "Container Engine") [CXI hook](<https://docs.cscs.ch/software/container-engine/resource-hook/index.md#hpe-slingshot-interconnect> "HPE Slingshot interconnect") will replace the libfabric libraries inside the container with the corresponding libraries on the host system. This will ensure access to the Slingshot interconnect.

> [!NOTE]
>
> **Use NVIDIA containers for the gh200 nodes**
>
> Container images provided by NVIDIA, which come with CUDA, NCCL and other commonly used libraries are recommended as the base layer for building a container environment on the [gh200](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") and [a100](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-a100-gpu-nodes> "NVIDIA A100 GPU Nodes") nodes.
>
> The version of CUDA, NCCL and compilers in the container can be used once libfabric has been installed. Other communication libraries, like MPI and NVSHMEM, provided in the containers can’t be used directly. Instead, they have to be installed in the container and linked against libfabric.

> [!NOTE]
>
> **Installing libfabric in a container for NVIDIA nodes**
>
> The following lines demonstrate how to configure and install libfabric in a Containerfile. Communication frameworks are built with explicit support for CUDA and GDRCopy.
>
> Some additional features are enabled to increase the portability of the container to non-Alps systems:
>
> - The libfabric [EFA](<https://aws.amazon.com/hpc/efa/>) provider is configured with the `--enable-efa` flag, for compatibility with AWS infrastructure.
> - The UCX communication framework is added to facilitate building a broader set of software (e.g. some OpenSHMEM implementations) and for optimized infiniband network support.
>
> Note that it is assumed that CUDA has already been installed on the system.
>
> ```Dockerfile
> ARG gdrcopy_version=2.5.1
> RUN git clone --depth 1 --branch v${gdrcopy_version} https://github.com/NVIDIA/gdrcopy.git \
>     && cd gdrcopy \
>     && export CUDA_PATH=/usr/local/cuda \
>     && make CC=gcc CUDA=$CUDA_PATH lib \
>     && make lib_install \
>     && cd ../ && rm -rf gdrcopy
>
> # Install libfabric
> ARG libfabric_version=1.22.0
> RUN git clone --branch v${libfabric_version} --depth 1 https://github.com/ofiwg/libfabric.git \
>     && cd libfabric \
>     && ./autogen.sh \
>     && ./configure --prefix=/usr --with-cuda=/usr/local/cuda --enable-cuda-dlopen \
>        --enable-gdrcopy-dlopen --enable-efa \
>     && make -j$(nproc) \
>     && make install \
>     && ldconfig \
>     && cd .. \
>     && rm -rf libfabric
>
> # Install UCX
> ARG UCX_VERSION=1.19.0
> RUN wget https://github.com/openucx/ucx/releases/download/v${UCX_VERSION}/ucx-${UCX_VERSION}.tar.gz \
>     && tar xzf ucx-${UCX_VERSION}.tar.gz \
>     && cd ucx-${UCX_VERSION} \
>     && mkdir build \
>     && cd build \
>     && ../configure --prefix=/usr --with-cuda=/usr/local/cuda --with-gdrcopy=/usr/local \
>        --enable-mt --enable-devel-headers \
>     && make -j$(nproc) \
>     && make install \
>     && cd ../.. \
>     && rm -rf ucx-${UCX_VERSION}.tar.gz ucx-${UCX_VERSION}
> ```
>
> An example Containerfile that installs libfabric in an NVIDIA container can be expanded below:
>
> > **The full Containerfile for GH200**
> >
> > The Containerfile below is based on an NVIDIA CUDA image, which provides a complete CUDA installation and NCCL.
> >
> > ```text
> > ARG ubuntu_version=24.04
> > ARG cuda_version=12.8.1
> > FROM docker.io/nvidia/cuda:${cuda_version}-cudnn-devel-ubuntu${ubuntu_version}
> >
> > RUN apt-get update \
> >     && DEBIAN_FRONTEND=noninteractive \
> >        apt-get install -y \
> >         build-essential \
> >         ca-certificates \
> >         pkg-config \
> >         automake \
> >         autoconf \
> >         libtool \
> >         cmake \
> >         gdb \
> >         strace \
> >         wget \
> >         git \
> >         bzip2 \
> >         python3 \
> >         gfortran \
> >         rdma-core \
> >         numactl \
> >         libconfig-dev \
> >         libuv1-dev \
> >         libfuse-dev \
> >         libfuse3-dev \
> >         libyaml-dev \
> >         libnl-3-dev \
> >         libnuma-dev \
> >         libsensors-dev \
> >         libcurl4-openssl-dev \
> >         libjson-c-dev \
> >         libibverbs-dev \
> >         --no-install-recommends \
> >     && rm -rf /var/lib/apt/lists/*
> >
> > ARG gdrcopy_version=2.5.1
> > RUN git clone --depth 1 --branch v${gdrcopy_version} https://github.com/NVIDIA/gdrcopy.git \
> >     && cd gdrcopy \
> >     && export CUDA_PATH=/usr/local/cuda \
> >     && make CC=gcc CUDA=$CUDA_PATH lib \
> >     && make lib_install \
> >     && cd ../ && rm -rf gdrcopy
> >
> > # Install libfabric
> > ARG libfabric_version=1.22.0
> > RUN git clone --branch v${libfabric_version} --depth 1 https://github.com/ofiwg/libfabric.git \
> >     && cd libfabric \
> >     && ./autogen.sh \
> >     && ./configure --prefix=/usr --with-cuda=/usr/local/cuda --enable-cuda-dlopen \
> >        --enable-gdrcopy-dlopen --enable-efa \
> >     && make -j$(nproc) \
> >     && make install \
> >     && ldconfig \
> >     && cd .. \
> >     && rm -rf libfabric
> >
> > # Install UCX
> > ARG UCX_VERSION=1.19.0
> > RUN wget https://github.com/openucx/ucx/releases/download/v${UCX_VERSION}/ucx-${UCX_VERSION}.tar.gz \
> >     && tar xzf ucx-${UCX_VERSION}.tar.gz \
> >     && cd ucx-${UCX_VERSION} \
> >     && mkdir build \
> >     && cd build \
> >     && ../configure --prefix=/usr --with-cuda=/usr/local/cuda --with-gdrcopy=/usr/local \
> >        --enable-mt --enable-devel-headers \
> >     && make -j$(nproc) \
> >     && make install \
> >     && cd ../.. \
> >     && rm -rf ucx-${UCX_VERSION}.tar.gz ucx-${UCX_VERSION}
> > ```

## Tuning libfabric

Tuning libfabric (particularly together with [Cray MPICH](<https://docs.cscs.ch/software/communication/cray-mpich/index.md#cray-mpich>), [OpenMPI](<https://docs.cscs.ch/software/communication/openmpi/index.md#openmpi>), and [NCCL](<https://docs.cscs.ch/software/communication/nccl/index.md#nccl>)) depends on many factors, including the application, workload, and system. For a comprehensive overview libfabric options for the CXI provider (the provider for the Slingshot network), see the [`fi_cxi` man pages](<https://ofiwg.github.io/libfabric/v2.1.0/man/fi_cxi.7.html>). Note that the exact version deployed on Alps may differ, and not all options may be applicable on Alps.

See the [Cray MPICH known issues page](<https://docs.cscs.ch/software/communication/cray-mpich/index.md#known-issues> "Known issues") for issues when using Cray MPICH together with libfabric.
