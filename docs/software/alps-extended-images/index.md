# Alps Extended Images

The Alps infrastructure (specifically the networking stack) requires custom-built libraries and specific environment settings to fully leverage the high-speed network.
To reduce the burden on users and ensure best-in-class performance, we provide pre-built **Alps Extended Images** for popular base images (starting with those commonly used by the ML/AI community).

!!! note

    All extended images are thoroughly tested and validated to ensure correct behavior and optimal performance (see [contributing section](#contributing)).


## Images List

The images are hosted on the CSCS internal artifactory repository and can only be pulled from within the Alps environment.

!!! note "Repository URL"

    ```
    jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/<image:tag>
    ```

=== "alps3"

    | Base Image                       | Alps Extended Image              | URL                          |
    | :------------------------------- | :------------------------------- | :--------------------------- |
    | nvcr.io/nvidia/pytorch:26.01-py3 | ngc-pytorch:26.01-py3-alps3      | ```jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:26.01-py3-alps3``` |
    | nvcr.io/nvidia/pytorch:25.12-py3 | ngc-pytorch:25.12-py3-alps3      | ```jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:25.12-py3-alps3``` |
    | nvcr.io/nvidia/nemo:25.11.01     | ngc-nemo:25.11.01-alps3          | ```jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-nemo:25.11.01-alps3``` |

    Network Stack: libraries and versions

    | Library          | Version        | Notes                        |
    | :--------------- | :------------- | :--------------------------- |
    | `libfabric`      | `2.5.0a1`      | Built from commit `102872c0280ce290d9d663945dad8a36ceb53c50` + patch (removing dependency on `shs-14` API, which is not available on Alps) |
    | `NCCL`           | `2.29.3-1*`    | Patched by applying `https://github.com/NVIDIA/nccl/pull/1979` to the `2.29.3` release |
    | `aws-ofi-plugin` | `git-394ae7b*` | Built from commit `394ae7b20dd0e6b4e5f63652e15e9da100d5fe83` + patch by applying `https://github.com/aws/aws-ofi-nccl/pull/1056` |
    | `nvshmem`        | `3.4.5-0`      | |
    | `OpenMPI`        | `5.0.9`        | |


=== "alps2"

    ??? warning "The alps2 images are deprecated"

        | Base Image                       | Alps Extended Image              | URL                          |
        | :------------------------------- | :------------------------------- | :--------------------------- |
        | nvcr.io/nvidia/pytorch:26.01-py3 | ngc-pytorch:26.01-py3-alps2      | ```jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:26.01-py3-alps2``` |
        | nvcr.io/nvidia/pytorch:25.12-py3 | ngc-pytorch:25.12-py3-alps2      | ```jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:25.12-py3-alps2``` |
        | nvcr.io/nvidia/nemo:25.11.01     | ngc-nemo:25.11.01-alps2          | ```jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-nemo:25.11.01-alps2``` |

        Network Stack: libraries and versions

        | Library          | Version        | Notes                        |
        | :--------------- | :------------- | :--------------------------- |
        | `libfabric`      | `2.5.0a1`      | Built from commit `f8262817c337d615a1acceea6cd4ecb526ce548b` + patch by applying `https://github.com/ofiwg/libfabric/pull/11684` |
        | `NCCL`           | `2.29.2-1*`    | Patched by applying `https://github.com/NVIDIA/nccl/pull/1979` to the `2.29.2` release |
        | `aws-ofi-plugin` | `git-eb9877e*` | Built from commit `eb9877e9cfecf725dba0794a5e0fc06f8fdf7f3f` + patch by applying `https://github.com/aws/aws-ofi-nccl/pull/1056` |
        | `nvshmem`        | `3.4.5-0`      | |
        | `OpenMPI`        | `5.0.9`        | |

=== "alps1"

    ??? warning "The alps1 images are deprecated"

        | Base Image                       | Alps Extended Image              |
        | :------------------------------- | :------------------------------- |
        | nvcr.io/nvidia/pytorch:26.01-py3 | ngc-pytorch:26.01-py3-alps1      |
        | nvcr.io/nvidia/pytorch:25.12-py3 | ngc-pytorch:25.12-py3-alps1      |
        | nvcr.io/nvidia/nemo:25.11.01     | ngc-nemo:25.11.01-alps1          |


!!! tip

    Images are continuously updated to incorporate the latest improvements.
    We strongly recommend periodically checking whether a newer version of an Alps Extended Image is available.

## Direct Usage

To use an image directly on Alps via an EDF environment file, set the image to the repository URL followed by the image name and tag.

!!! danger

    - Do **not** use the `aws_ofi_nccl` hook annotation  
    - Explicitly **disable** the `cxi` hook
    - Use the `--environment` flag for `srun` instead of `sbatch` (i.e. `srun --environment=my_edf.toml ...`)
    - Use the `--network=disable_rdzv_get` flag for `srun` to disable the rendezvous mechanism for network initialization (i.e. `srun --network=disable_rdzv_get ...` or setting `SLURM_NETWORK=disable_rdzv_get`)
    - Launch MPI applications with `PMIx` (i.e. `srun --mpi=pmix` or setting `SLURM_MPI_TYPE=pmix`)

```toml title="Example EDF file"
# (1)!
image = "jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:26.01-py3-alps3"
mounts = [
    "/capstor/",
    "/iopsstor/",
]
writable = true
[env]
PMIX_MCA_psec = "native" # (2)!
[annotations]
com.hooks.cxi.enabled = "false" # (3)!
```

1. Images will be pulled directly from CSCS' `jfrog` artifactory
2. Pertinent environment variables for optimal network performance are already set in the container image. `PMIX_MCA_psec = "native"` is recommended here in order to avoid warnings at initialization.
3. The `CXI` hook **must** be disabled such that the container images network libraries have priority over the host system's libraries.

```bash title="Example sbatch file"
#!/usr/bin/env bash
#SBATCH --account=my_account
#SBATCH --job-name=example
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4

# (1)!
# (2)!
# (3)!
srun --mpi=pmix --network=disable_rdzv_get --environment=example.edf.toml python my_script.py
```

1. The `--mpi=pmix` flag is required to ensure that `PMIx` is used as the MPI launcher - without this flag you may encounter errors during initialization.
2. The `--network=disable_rdzv_get` flag is required to disable the rendezvous mechanism for network initialization. Alternatively, you can also set the environment variable `SLURM_NETWORK=disable_rdzv_get` to achieve the same effect.
3. The `--environment` must be used as a flag for `srun` - passing this flag to `sbatch` will lead to errors related to missing Slurm plugins.

!!! failure "`srun` errors related to missing Slurm plugins"

    If you are submitting a batch job with `sbatch` and using the `--environment` (i.e. `#SBATCH --environment=my_edf.toml`) option, this can lead to errors such as:
    ```
    srun: error: plugin_load_from_file: dlopen(/usr/lib64/slurm/switch_hpe_slingshot.so): libjson-c.so.3: cannot open shared object file: No such file or directory
    srun: error: Couldn't load specified plugin name for switch/hpe_slingshot: Dlopen of plugin file failed
    srun: fatal: Can't find plugin for switch/hpe_slingshot
    ```
    Make sure you use the option for `srun` instead of `sbatch`, i.e.:
    ```bash
    srun --environment=my_edf.toml ...
    ```

!!! failure "`PMIx`/`ucx` errors during initialization"

    If you see warnings related to `PMIx`, for example
    ```
    No PMIx server was reachable, but a PMI1/2 was detected
    ```
    or observe `ucx` logs indicating that
    ```
    Transport endpoint is not connected
    ```
    this likely indicates that Slurm is not configured to use `PMIx` for launching MPI applications.
    To resolve this, ensure that you are launching your application with the `--mpi=pmix` flag, for example:
    ```bash
    srun --mpi=pmix ...
    ```
    or set the environment variable `SLURM_MPI_TYPE=pmix` to make `PMIx` the default MPI launcher.

## Pulling Images with Podman

Extended images can also be pulled using Podman and used as a base image in your own Dockerfiles.

```bash title="Pulling with Podman"
podman pull docker://jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:26.01-py3-alps3
```

## Inspect image provenance labels

Alps Extended Images include OCI labels with provenance metadata (for example, source repository, commit SHA, and build time). You can inspect these labels with `podman`.

```bash title="Pull image and inspect labels"
IMAGE="jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:26.01-py3-alps3"

# Pull the image
podman pull "$IMAGE"

# Show all labels (JSON)
podman image inspect "$IMAGE" --format '{{ json .Labels }}'

# Show specific labels
podman image inspect "$IMAGE" --format 'Source Repository: {{ index .Labels "org.opencontainers.image.source" }}'
podman image inspect "$IMAGE" --format 'Source Revision: {{ index .Labels "org.opencontainers.image.revision" }}'
podman image inspect "$IMAGE" --format 'Build Time: {{ index .Labels "org.opencontainers.image.created" }}'
```

## Use in Dockerfile

```dockerfile title="Example Dockerfile"
FROM jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:26.01-py3-alps3

RUN echo "Hello world!"

```
For further information, please see the [guide to building container images on Alps][ref-build-containers].

## Contributing

The Alps extended images are automatically built via a dedicated CI/CD pipeline hosted on GitHub:

[github.com/eth-cscs/alps-swiss-ai](https://github.com/eth-cscs/alps-swiss-ai)

Additional tests can be added to the [build and test pipeline](https://github.com/eth-cscs/alps-swiss-ai/blob/main/ci-pipelines/build-alps-golden-images.yaml)

New images can be added to the [Alps-Images folder](https://github.com/eth-cscs/alps-swiss-ai/tree/main/Alps-Images)

!!! note

    The repository is currently private.
    Please open a [Service Desk](https://support.cscs.ch/) ticket to request access.
