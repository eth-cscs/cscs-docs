[](){#ref-software-ml}
# Machine learning applications and frameworks

CSCS supports a wide range of machine learning (ML) applications and frameworks on its systems.
Most ML workloads are containerized to ensure portability, reproducibility, and ease of use across environments.

Users can choose between running containers, using provided uenv software stacks, or building custom Python environments tailored to their needs.

## Running machine learning applications with containers

Containerization is the recommended approach for ML workloads on Alps, as it simplifies software management and maximizes compatibility with other systems.

* Users are encouraged to build their own containers, starting from popular sources such as the [Nvidia NGC Catalog](https://catalog.ngc.nvidia.com/containers), which offers a variety of pre-built images optimized for HPC and ML workloads.
Examples include:
    * [PyTorch NGC container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch)
    * [TensorFlow NGC container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorflow)
* For frequently changing dependencies, consider creating a virtual environment (venv) mounted into the container.

Helpful references:

* Running containers on Alps: [Container Engine Guide][ref-container-engine]
* Building custom container images: [Container Build Guide][ref-build-containers]

## Using provided uenv software stacks

Alternatively, CSCS provides pre-configured software stacks ([uenvs][ref-uenv]) that can serve as a starting point for machine learning projects.
These environments provide optimized compilers, libraries, and selected ML frameworks.

Available ML-related uenvs:

* [PyTorch][ref-uenv-pytorch] — available on [Clariden][ref-cluster-clariden] and [Daint][ref-cluster-daint]

To extend these environments with additional Python packages, it is recommended to create a Python Virtual Environment (venv).
See this [PyTorch venv example][ref-uenv-pytorch-venv] for details.

!!! note
    While many Python packages provide pre-built binaries for common architectures, some may require building from source.

## Building custom Python environments

Users may also choose to build entirely custom software stacks using Python package managers such as `uv` or `conda`.
Most ML libraries are available via the [Python Package Index (PyPI)](https://pypi.org/).

To ensure optimal performance on CSCS systems, we recommend starting from an environment that already includes:

* CUDA, cuDNN
* MPI, NCCL
* C/C++ compilers

This can be achieved either by:

* building a [custom container image][ref-build-containers] based on a suitable ML-ready base image,
* or starting from a provided uenv (e.g., [PrgEnv GNU][ref-uenv-prgenv-gnu] or [PyTorch uenv][ref-uenv-pytorch]),

and extending it with a virtual environment.

