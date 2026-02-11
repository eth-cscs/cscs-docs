# Alps Extended Images

The Alps infrastructure (specifically the networking stack) requires custom-built libraries and specific environment settings to fully leverage the high-speed network.
To reduce the burden on users and ensure best-in-class performance, we provide pre-built **Alps Extended Images** for popular base images (starting with those commonly used by the ML/AI community).

!!! note

    All extended images are thoroughly tested and validated to ensure correct behavior and optimal performance.
    Build and testing pipeline: https://github.com/eth-cscs/alps-swiss-ai/blob/main/ci-pipelines/build-alps-golden-images.yaml


---

## Images List

!!! tip

    Images are continuously updated to incorporate the latest improvements.
    We strongly recommend periodically checking whether a newer version of an Alps Extended Image is available.


| Base Image                       | Alps Extended Image              | Notes                       |
| :------------------------------- | :------------------------------- | ---------------------------:|
| nvcr.io/nvidia/pytorch:26.01-py3 | ngc-pytorch:26.01-py3-alps2      | Libfabric 2.4, RDMA enabled |
| nvcr.io/nvidia/pytorch:25.12-py3 | ngc-pytorch:25.12-py3-alps2      | Libfabric 2.4, RDMA enabled |
| nvcr.io/nvidia/nemo:25.11.01     | ngc-nemo:25.11.01-alps2          | Libfabric 2.4, RDMA enabled |

---

## Using the Images

The images are hosted on the CSCS internal artifactory repository and can only be pulled from within the Alps environment.

**Repository URL**
!!! note ""

    ```
    jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/<image:tag>
    ```

### Direct Usage

To use an image directly on Alps via an EDF environment file, set the image to the repository URL followed by the image name and tag.

!!! danger

    - Do **not** use the `aws_ofi_nccl` hook annotation  
    - Explicitly **disable** the `cxi` hook

```toml title="Example EDF file"
# (1)!
image = "jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:25.12-py3-alps2"
mounts = [
    "/capstor/",
    "/iopsstor/",
]
writable = true
[env]
# (2)!
PMIX_MCA_psec = "native"
[annotations]
# (3)!
com.hooks.cxi.enabled = "false"
```

1. Images will be pulled directly from CSCS' `jfrog` artifactory
2. Pertinent environment variables for optimal network performance are already set in the container image. `PMIX_MCA_psec = "native"` is recommended here in order to avoid warnings at initialization.
3. Te `CXI` hook **must** be disabled such that the container images network libraries have priority over the host system's libraries.

### Pulling Images with Podman

Extended images can also be pulled using Podman and used as a base image in your own Dockerfiles.

Example pull with Podman:

```bash
podman pull docker://jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:25.12-py3-alps2
```

### Use in Dockerfile

Example Dockerfile:
```dockerfile
FROM jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:25.12-py3-alps2

RUN echo "Hello world!"

```
For further information, please see the [guide to building container images on Alps][ref-build-containers].


# Contributing

The Alps extended images are automatically built via a dedicated CI/CD pipeline hosted on GitHub:

[github.com/eth-cscs/alps-swiss-ai](https://github.com/eth-cscs/alps-swiss-ai)


!!! note

    The repository is currently private.
    Please open a [Service Desk](https://support.cscs.ch/) ticket to request access.








