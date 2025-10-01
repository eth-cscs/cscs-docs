[](){#ref-ce-guidelines-images}
# Guidelines for images on Alps

This section offers some guidelines about creating and using container images that achieve good performance on the Alps research infrastructure.
The section focuses on foundational components (such as communication libraries) which are essential to enabling performant effective usage of Alps' capabilities, rather than full application use cases.
Synthetic benchmarks are also used to showcase quantitative performance.

!!! important
    The Containerfiles and examples provided in this section are intended to serve as general reference and starting point.
    They are not meant to represent all possible combinations and versions of software capable of running efficiently on Alps.

    In the same vein, please note that the content presented here is not intended to represent images officially supported by CSCS staff.

Below is a summary of the software suggested and demonstrated throughout this section:

- Base components:
    - CUDA 12.8.1
    - GDRCopy 2.5.1
    - Libfabric 1.22.0
    - UCX 1.19.0
- MPI implementations
    - MPICH 4.3.1
    - OpenMPI 5.0.8
- Other programming libraries
    - NVSHMEM 3.4.5
- Synthetic benchmarks
    - OSU Micro-benchmarks 7.5.1
    - NCCL Tests 2.17.1

The content is organized in pages which detail container images building incrementally upon each other:

- a base image installing baseline libraries and frameworks (e.g. CUDA, libfabric)
- MPI implementations (MPICH, OpenMPI)
- NVSHMEM
- NCCL tests
