[](){#ref-communication-rccl}
# RCCL

[RCCL](https://rocmdocs.amd.com/projects/rccl/en/latest/) is an optimized inter-GPU communication library for AMD GPUs.
It provides equivalent functionality to [NCCL][ref-communication-nccl] for AMD GPUs.

!!! todo
    - high level description
    - libfabric/aws-ofi-rccl plugin
    - configuration options

!!! info
    RCCL uses many of the same [configuration options as NCCL](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html), with the `NCCL` prefix, not `RCCL`.
    Refer to NCCL documentation to tune RCCL.
