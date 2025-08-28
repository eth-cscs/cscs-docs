[](){#ref-software-ml}
# Machine learning applications and frameworks

CSCS supports a wide range of machine learning (ML) applications and frameworks on its systems.
Most ML workloads are containerized to ensure portability, reproducibility, and ease of use across systems.

Users can choose between running containers, using provided uenv software stacks, or building custom Python environments tailored to their needs.

First time users are recommended to consult the [LLM tutorials][ref-tutorials-ml] to get familiar with the concepts of the Machine Learning platform in a series of hands-on examples. 

## Running ML applications with containers (recommended)

Containerization is the recommended approach for ML workloads on Alps, as it simplifies software management and maximizes compatibility with other systems.

Users are encouraged to build their own containers, starting from popular sources such as the [Nvidia NGC Catalog](https://catalog.ngc.nvidia.com/containers), which offers a variety of pre-built images optimized for HPC and ML workloads.
Examples include:

* [PyTorch NGC container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch) ([Release Notes](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/index.html))
* [JAX NGC container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/jax) ([Release Notes](https://docs.nvidia.com/deeplearning/frameworks/jax-release-notes/index.html))
* [TensorFlow NGC container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorflow) (deprecated since 25.02, see [Release Notes](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/index.html))

Documented best practices are available for:

* [PyTorch][ref-ce-pytorch]

!!! note "Extending a container with a virtual environment"
    For frequently changing Python dependencies during development, consider creating a Virtual Environment (venv) on top of the packages in the container (see [this example][ref-ce-pytorch-venv]).

Helpful references:

* Introduction to concepts of the Machine Learning platform: [LLM tutorials][ref-tutorials-ml]
* Running containers on Alps: [Container Engine Guide][ref-container-engine]
* Building custom container images: [Container Build Guide][ref-build-containers]

## Using provided uenv software stacks

Alternatively, CSCS provides pre-configured software stacks ([uenvs][ref-uenv]) that can serve as a starting point for machine learning projects.
These environments provide optimized compilers, libraries, and selected ML frameworks.

Available ML-related uenvs:

* [PyTorch][ref-uenv-pytorch] — available on [Clariden][ref-cluster-clariden] and [Daint][ref-cluster-daint]

!!! note "Extending a uenv with a virtual environment"
    To extend these environments with additional Python packages, it is recommended to create a Python Virtual Environment (venv) layered on top of the packages in the uenv.
    See this [PyTorch venv example][ref-uenv-pytorch-venv] for details.

## Building custom Python environments

Users may also choose to build entirely custom software stacks using Python package managers such as `uv` or `conda`.
Most ML libraries are available via the [Python Package Index (PyPI)](https://pypi.org/).

!!! note
    While many Python packages provide pre-built binaries for common architectures, some may require building from source.

To ensure optimal performance on CSCS systems, we recommend starting from an environment that already includes:

* CUDA, cuDNN
* MPI, NCCL
* C/C++ compilers

This can be achieved either by:

* building a [custom container image][ref-build-containers] based on a suitable ML-ready base image,
* or starting from a provided uenv (e.g., [`prgenv-gnu`][ref-uenv-prgenv-gnu] or [PyTorch uenv][ref-uenv-pytorch]),

and extending it with a virtual environment.

