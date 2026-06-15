[](){#ref-build-containers}
# Building container images on Alps

Building OCI container images on Alps vClusters is supported through [Podman](https://podman.io/), an open-source container engine that adheres to OCI standards and supports rootless containers by leveraging Linux [user namespaces](https://www.man7.org/linux/man-pages/man7/user_namespaces.7.html).
Its command-line interface (CLI) closely mirrors Docker’s, providing a consistent and familiar experience for users of established container tools.

[](){#ref-build-containers-configure-podman}
## Preliminary step: configuring Podman's storage

The first step in order to use Podman on Alps is to create a valid Container Storage configuration file in your home directory, according to the following minimal template:

```toml title="$HOME/.config/containers/storage.conf"
[storage]
driver = "overlay"
runroot = "/dev/shm/$USER/runroot"
graphroot = "/dev/shm/$USER/root"
```

!!! warning
    If `$XDG_CONFIG_HOME` is set, place this file at `$XDG_CONFIG_HOME/containers/storage.conf` instead.
    See the [terminal user guide][ref-guides-terminal-arch] for further information about XDG variables.

!!! warning
    In the above configuration, `/dev/shm` is used to store the container images.
    `/dev/shm` is the mount point of a [tmpfs filesystem](https://www.kernel.org/doc/html/latest/filesystems/tmpfs.html#tmpfs) and is compatible with the user namespaces used by Podman.
    The limitation of this approach  is that container images created during a job allocation are deleted when the job ends.
    Therefore, the image needs to either be pushed to a container registry or imported by the Container Engine before the job allocation finishes.<br/>
    [Local-registry][ref-local-registry] can be used to enable caching on a filesystem other than `/dev/shm`, and speed up subsequent build processes.

You can use

```bash
podman info | grep -A 2 "store:"
```

to check that the correct `storage.conf` file is used by Podman (`store:configFile` field).

## Building images with Podman

The easiest way to build a container image is to rely on a Containerfile (a more generic name for a container image recipe, but essentially equivalent to Dockerfile):

```bash
# Allocate a compute node and open an interactive terminal on it
srun --pty --partition=<partition> bash
 
# Change to the directory containing the Containerfile/Dockerfile and build the image
podman build -t <image:tag> .
```

In general, [`podman build`](https://docs.podman.io/en/stable/markdown/podman-build.1.html) follows the Docker options convention.

!!! info "Debugging the container build"
    If the container build fails, you can run an interactive shell using the image from the last successfully built layer with

    ```bash
    podman run -it --rm -e NVIDIA_VISIBLE_DEVICES=void <last-layer-hash> bash # (1)!
    ```

    1. Setting `NVIDIA_VISIBLE_DEVICES` in the environment is required specifically to run NGC containers with podman

    replacing `<last-layer-hash>` with the actual hash output in the build job and interactively test the failing command.


## Importing images in the Container Engine

An image built using Podman can be easily imported as a squashfs archive in order to be used with our Container Engine solution.
It is important to keep in mind that the import has to take place in the same job allocation where the image creation took place, otherwise the image is lost due to the temporary nature of `/dev/shm`.

!!! info "Preliminary configuration: Lustre settings for container images"
    Container images are stored in a single [SquashFS]() file, that is typically between 1-20 GB in size (particularly for large ML containers).
    To ensure good performance for jobs on multiple nodes, take the time to configure the target directory using `lfs setstripe` according to [best practices for Lustre][ref-guides-storage-lustre] before importing the container image, or using `lfs migrate` to fix files that are already imported.

To import the image:

```
enroot import -x mount -o <image_name.sqsh> podman://<image:tag>
```

The resulting `<image_name.sqsh>` can used directly as an explicitly pulled container image, as documented in Container Engine.
An example Environment Definition File (EDF) using the imported image looks as follows:

```toml
image = "/<path to image directory>/<image_name.sqsh>"
mounts = ["/capstor/scratch/cscs/<username>:/capstor/scratch/cscs/<username>"]
workdir = "/capstor/scratch/cscs/<username>"
```
## Pushing Images to a Container Registry

In order to push an image to a container registry, you first need to follow three steps:

1. Use your credential to login to the container registry with podman login.
2. Tag the image according to the name of your container registry and the corresponding repository, using podman tag. This step can be skipped if you already provided the appropriate tag when building the image.
3. Push the image using podman push.

```bash
# Login to a container registry using username/password interactively
podman login <registry_url>

# Tag the image accordingly
podman tag <image:tag> <registry url>/<image:tag>

# Push the image (for docker type registries use the docker:// prefix)
podman push docker://<registry url>/<image:tag>
```

For example, to push an image to the DockerHub container registry, the following steps have to be performed:

```bash
# Login to DockerHub (Podman will ask for your credentials)
podman login docker.io

# Tag the image based on your username
podman tag <image:tag> docker.io/<username>/myimage:latest

# Push the image to the repository of your choice
podman push docker://docker.io/<username>/myimage:latest
```

[](){#ref-local-registry}
## Caching image layers on a local registry

The Podman image building process can be enhanced by caching intermediate layers and using the cache in subsequent runs.

When building inside a Slurm job, [`local-registry`](https://github.com/eth-cscs/local-registry) can be used as container registry for caching purposes.

   ```console title="Download"
   $ git clone https://github.com/eth-cscs/local-registry.git
   Cloning into 'local-registry'...
   ...
   Receiving objects: 100% (6/6), done.
   $ cd local-registry
   ```
!!! warning
    local registry can work only on compute nodes inside a slurm job

   ```console title="Launch interactive slurm job"
   $ srun ... --pty bash
   ```

   ```console title="Ensure filesystem folder exists"
   $ mkdir <CHOSEN_REGISTRY_DIRPATH>
   ```

   ```console title="Setup and start registry"
   $ . env-registry && registry up <CHOSEN_REGISTRY_DIRPATH>
   Local registry started on folder <CHOSEN_REGISTRY_DIRPATH>
   The address is:
   <REGISTRY_HOST>:<REGISTRY_PORT>
   ```
!!! info
    `<CHOSEN_REGISTRY_DIRPATH>` can be omitted if unchanged


   ```console title="Build container image using local registry as cache"
   $ cat <CONTAINERFILE>
   FROM ubuntu:latest
   RUN apt update
   RUN apt upgrade -y

   $ podman-cached -f <CONTAINERFILE> -t <IMAGE_NAME>:<IMAGE_TAG>
   Executing: podman build --layers --tls-verify=false --cache-from=<REGISTRY_HOST>:<REGISTRY_PORT>/cache --cache-to=<REGISTRY_HOST>:<REGISTRY_PORT>/cache  -f <CONTAINERFILE> -t <IMAGE_NAME>:<IMAGE_TAG>
   STEP 1/3: FROM ubuntu:latest
   STEP 2/3: RUN apt update
   --> Using cache 7e878891345baea142da9dca42bf131488a317178a162b1388f449f40328eb45
   --> Pushing cache [localhost:5000/cache]:3e03c073728436d9337daacb491169e6cb3868d4f0f9385058d8333dc62eb903
   --> 7e878891345b
   STEP 3/3: RUN apt upgrade -y
   --> Using cache 2c8781e264b03ce41c571b6a4d24c8d8472a413ee50073ad662e517f92a0ff2a
   COMMIT <IMAGE_NAME>:<IMAGE_TAG>
   --> Pushing cache [localhost:5000/cache]:3e44a53a47cd2318f910222fec5ae4f68853c471410d73f52e6b01c4eaec5555
   --> 2c8781e264b0
   Successfully tagged localhost/<IMAGE_NAME>:<IMAGE_TAG>
   Successfully tagged localhost/<IMAGE_NAME>:latest
   2c8781e264b03ce41c571b6a4d24c8d8472a413ee50073ad662e517f92a0ff2a
   ```

   ```console title="Stop registry"
   $ registry down
   local registry is stopped.
   ```

Additional commands can be used to manage the local registry:

   ```console title="Check registry status (UP)"
   $ registry status
   local registry is running at:
   <REGISTRY_HOST>:<REGISTRY_PORT>
   ```

   ```console title="Check registry status (DOWN)"
   $ registry status
   local registry is stopped.
   ```

   ```console title="Delete registry (when data is not needed anymore)"
   $ registry delete
   Removing directory <CHOSEN_REGISTRY_DIRPATH> content ... [DONE]
   Removing configuration file <HOME>/.local_registry/registry.conf ... [DONE]

   local registry is DELETED.
   ```
