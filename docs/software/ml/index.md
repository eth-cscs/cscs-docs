[](){#ref-software-ml}
# Machine learning applications and frameworks

## Overview

CSCS supports a wide range of machine learning (ML) applications and frameworks
on its systems. Most ML workloads are containerized to ensure portability,
reproducibility, and ease of use across environments.

Users can choose between running containers, using provided uenv software
stacks, or building custom Python environments tailored to their needs.

## Running Machine Learning Applications with Containers

Containerization is the recommended approach for ML workloads on Alps, as it
simplifies software management and maximizes compatibility with other systems.

* CSCS does not provide ready-to-use ML container images
* Users are encouraged to build their own containers, starting from popular
  sources such as the [Nvidia NGC
  Catalog](https://catalog.ngc.nvidia.com/containers)

Helpful references:

* Running containers on Alps: [Container Engine Guide][ref-container-engine]
* Building custom container images: [Container Build
  Guide][ref-build-containers]

## Using Provided uenv Software Stacks

Alternatively, CSCS provides pre-configured software stacks ([uenvs][ref-uenv])
that can serve as a starting point for machine learning projects. These
environments provide optimized compilers, libraries, and selected ML
frameworks.

Available ML-related uenvs:

* [PyTorch][ref-uenv-pytorch] — available on [Clariden][ref-cluster-clariden]
  and [Daint][ref-cluster-daint]

To extend these environments with additional Python packages, it is recommended
to create a Python Virtual Environment (venv). See this [PyTorch venv
example][ref-uenv-pytorch-venv] for details.

!!! note
    While many Python packages provide pre-built binaries for common
    architectures, some may require building from source.

## Building Custom Python Environments

Users may also choose to build entirely custom software stacks using Python
package managers such as `pip` or `conda`. Most ML libraries are available via
the [Python Package Index (PyPI)](https://pypi.org/).

To ensure optimal performance on CSCS systems, we recommend starting from an
environment that already includes:

* CUDA, cuDNN
* MPI, NCCL
* c/c++ compilers

This can be achieved either by:

* Building a [custom container image][ref-build-containers] based on a suitable
  ML-ready base image.
* Starting from a provided uenv (e.g., [PrgEnv GNU][ref-uenv-prgenv-gnu] or
  [PyTorch uenv][ref-uenv-pytorch]) and extending it with a virtual
  environment.

