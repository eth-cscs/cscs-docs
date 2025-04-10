[](){#ref-software-ml}
# Machine Learning Applications and Frameworks

## Containerized Machine Learning Applications

CSCS supports a variety of machine learning applications and frameworks on its
systems. Typically, machine learning applications are containerized to ensure
compatibility and ease of use across different environments.

CSCS does not provide any specific machine learning container images, but users
can create their own containers using popular base container registries, such
as [Nvidia's NGC Catalog](https://catalog.ngc.nvidia.com/containers). These
containers can be run on Alps, allowing users to leverage the
high-performance computing resources available for their machine learning
tasks.

* Jobs using containers can be easily set up and submitted using the [container
  engine][ref-container-engine].
* To build images, see the [guide to building container images on
  Alps][ref-build-containers].

## Uenv Software Stacks

CSCS provides a base [PyTorch uenv][ref-uenv-pytorch] that is available on the
[Clariden][ref-cluster-clariden] and [Daint][ref-cluster-daint] cluster.
