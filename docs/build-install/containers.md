[](){#ref-build-containers}
# Building container images on Alps

Building OCI container images on Alps vClusters is supported through [Podman](https://podman.io/), an open-source container engine that adheres to OCI standards and supports rootless containers by leveraging Linux [user namespaces](https://www.man7.org/linux/man-pages/man7/user_namespaces.7.html).
Its command-line interface (CLI) closely mirrors Docker’s, providing a consistent and familiar experience for users of established container tools.

## Preliminary step: configuring Podman's storage

The first step in order to use Podman on Alps is to create a valid Container Storage configuration file at `$HOME/.config/containers/storage.conf` (or `$XDG_CONFIG_HOME/containers/storage.conf`, if you have `$XDG_CONFIG_HOME` set), according to the following minimal template:

```toml
[storage]
driver = "overlay"
runroot = "/dev/shm/$USER/runroot"
graphroot = "/dev/shm/$USER/root"
```

!!! warning
    In the above configuration, `/dev/shm` is used to store the container images.
    `/dev/shm` is the mount point of a [tmpfs filesystem](https://www.kernel.org/doc/html/latest/filesystems/tmpfs.html#tmpfs) and is compatible with the user namespaces used by Podman.
    The limitation of this approach  is that container images created during a job allocation are deleted when the job ends.
    Therefore, the image needs to either be pushed to a container registry or imported by the Container Engine before the job allocation finishes.

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

## Importing images in the Container Engine

An image built using Podman can be easily imported as a squashfs archive in order to be used with our Container Engine solution.
It is important to keep in mind that the import has to take place in the same job allocation where the image creation took place, otherwise the image is lost due to the temporary nature of `/dev/shm`.

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
