# Alps Extended Images

The Alps infrastructure (specifically the networking stack) requires custom-built libraries and specific environment settings to fully leverage the high-speed network.
To reduce the burden on users and ensure best-in-class performance, we provide pre-built **Alps Extended Images** for popular base images (starting with those commonly used by the ML/AI community).

!!! note

    All extended images are thoroughly tested and validated to ensure correct behavior and optimal performance (see [contributing section](#contributing)).

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

!!! note "Repository URL"

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
[env] # (2)!
PMIX_MCA_psec = "native"
[annotations]
com.hooks.cxi.enabled = "false" # (3)!
```

1. Images will be pulled directly from CSCS' `jfrog` artifactory
2. Pertinent environment variables for optimal network performance are already set in the container image. `PMIX_MCA_psec = "native"` is recommended here in order to avoid warnings at initialization.
3. Te `CXI` hook **must** be disabled such that the container images network libraries have priority over the host system's libraries.

```bash title="Example sbatch file"
#!/usr/bin/env bash
#SBATCH --account=my_account
#SBATCH --job-name=example
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4

# (1)!
# (2)!
srun --mpi=pmix --environment=example.edf.toml python my_script.py
```

1. The `--mpi=pmix` flag is required to ensure that `PMIx` is used as the MPI launcher - without this flag you may encounter errors during initialization.
2. The `--environment` must be used as a flag for `srun` - passing this flag to `sbatch` will lead to errors related to missing Slurm plugins.

### Pulling Images with Podman

Extended images can also be pulled using Podman and used as a base image in your own Dockerfiles.

```bash title="Pulling with Podman"
podman pull docker://jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:25.12-py3-alps2
```

### Use in Dockerfile

```dockerfile title="Example Dockerfile"
FROM jfrog.svc.cscs.ch/docker-group-csstaff/alps-images/ngc-pytorch:25.12-py3-alps2

RUN echo "Hello world!"

```
For further information, please see the [guide to building container images on Alps][ref-build-containers].

## Troubleshooting

!!! note MPI applications need to be launched with `--mpi=pmix`
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


!!! note The `--environment` option must not be used for `sbatch`
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

## Contributing

The Alps extended images are automatically built via a dedicated CI/CD pipeline hosted on GitHub:

[github.com/eth-cscs/alps-swiss-ai](https://github.com/eth-cscs/alps-swiss-ai)

Additional tests can be added to the [build and test pipeline](https://github.com/eth-cscs/alps-swiss-ai/blob/main/ci-pipelines/build-alps-golden-images.yaml)

New images can be added to the [Alps-Images folder](https://github.com/eth-cscs/alps-swiss-ai/tree/main/Alps-Images)

!!! note

    The repository is currently private.
    Please open a [Service Desk](https://support.cscs.ch/) ticket to request access.
