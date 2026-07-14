[](){#ref-sarus-suite-user-guide}
# Sarus Suite & Podman on Alps — Early Access User Guide

!!! under-construction

    Sarus Suite is **currently intended for early access testing and evaluation only**, with the goal of collecting feedback to guide further development and eventual production rollout.

    The tools described here are under active development and will be continuously updated over the coming months as progress is made towards supporting more features and production readiness.

    Accordingly, the contents of this page are not final and should be expected to change.

    Familiarity with the current [Container Engine (CE)][ref-container-engine] toolset is assumed.

!!! Danger "Current differences from the production CE and limitations"

    * [HPC features][ref-sarus-suite-hpc-features] are enabled primarily through [CDI specs](https://github.com/cncf-tags/container-device-interface) and the [device array][ref-sarus-suite-edf-device-array], not annotations. Work is ongoing to enable the CE vService to handle configuration of OCI hooks for Podman and align them with annotations.
    * CXI libfabric replacement is not enabled by default.
    * The CXI CDI relies on an old Sarus 1.7.0 hook for libfabric replacement. When activated, the hook requires a libfabric to be present inside the container. Enabling the CXI CDI with a container that does not have libfabric results in an error.
    * CXI and AWS OFI NCCL CDI specs cannot handle replacement of multiple libfabric or plugin libraries inside containers. This complicates the effective use of images with multiple NCCL plugins already installed, like NGC images. Work in preparing OCI hooks to handle these cases is ongoing. In the meantime, customized CDI specs are a possible workaround.
    * Mount destinations in EDFs must be explicit (e.g. `mounts=["${SCRATCH}"]` will result in an error).
    * SquashFS mounts from EDFs are not supported yet.
    * PMIx propagation is achieved by bind-mounting `/tmp` into containers, until a hook for proper PMIx support is rolled out.
    * No support yet for netstack artifacts, CUDA MPS, or direct SSH into containers.
    * Error propagation and reporting still need improvements.


## Similarities with the current Container Engine

One of the main goals of the transition from **Enroot & Pyxis** to **Sarus Suite & Podman** is to minimize changes to the end-user experience.

Sarus Suite:

*   supports the **EDF format** and the **EDF search path rules** already implemented in the current Container Engine;
*   integrates with **Slurm** in a similar way to launch containerized jobs on compute nodes.


## New General Concepts

### Podman Read-Only Image Store

!!! warning

    Due to the way Podman's image storage works, with Sarus Suite it's no longer possible to use direct filesystem paths to define images in EDFs. Images must be entered in the form of registry references.

Podman's native storage backends do not support networked filesystems and rely on plain directories, which would perform poorly on parallel filesystems such as Lustre.

To address these limitations, Sarus Suite provides an **image storage location** that Podman can access through its own interfaces, while storing images in **SquashFS format**.

This image storage is:

*   meant to be modified **exclusively** through Sarus Suite tools (not directly by Podman);
*   referred to as the **Podman read-only store** or, more technically, the **Parallax store** (after the low-level storage utility that manages it).

Key characteristics:

*   Located on a parallel filesystem (for example `/capstor/scratch/cscs/${USER}/.parallax_imagestore`).
*   Separate from Podman's default storage, which is currently recommended to be located on `/dev/shm` on Alps (node-local).
*   Images in the read-only store are **not visible** to regular Podman commands such as `podman images`.
*   Sarus Suite tools which execute containers (`sarusctl`, Skybox) exclusively use images from the read-only store, not from Podman's default store.

[](){#ref-sarus-suite-edf-device-array}
### Device Array in EDFs

With Podman, hooks are no longer the only mechanism to modify container contents and behavior. An increasingly adopted standard is the [Container Device Interface (CDI)](https://github.com/cncf-tags/container-device-interface), which describes in YAML or JSON how complex resources are exposed inside containers.
A prominent example is **NVIDIA**, which is transitioning to CDI as the preferred mechanism for GPU support in Podman.

In addition, Podman does **not** automatically mount all device files, unlike Enroot; devices must therefore be enabled individually.

To address both points, EDFs support a `devices` array. Each entry must be a valid value for Podman's `--device` option, for example:

```toml
devices = ["nvidia.com/gpu=all", "/dev/gdrdrv"]
```

!!! tip
    Some commonly used devices are enabled by default.
    See the related section below.

### Bash Expansion in EDFs

Sarus Suite tools support expansion of most Bash syntax within EDF files.
This is an upgrade from the current EDF implementation in Pyxis, where only environment variable expansion is supported, and with very limited syntax.

For security reasons, **subshell execution of arbitrary commands is not allowed**.


## Sarusctl: The Interactive Interface

The first Sarus Suite component most users will interact with is the command-line tool `sarusctl`:

```console
$ sarusctl

CLI tool for sarus-suite

Usage: sarusctl [OPTIONS]  <COMMAND>

Commands:
  validate   Validate EDF file
  render     Render EDF file
  images     List images including Parallax storage
  pull       Pull image with Podman and migrate to Parallax storage
  migrate    Migrate image to Parallax storage
  rmi        Remove image from Parallax storage
  run        Run container from EDF file
  help       Print this message or the help of the given subcommand(s)

Options:
  -v, --verbose
  -h, --help     Print help
  -V, --version  Print version
```

### What `sarusctl` Is

`sarusctl` is an interactive utility that supports:

*   preparation and validation of EDF files,
*   image management (pulling, migrating, removing),
*   pre-flight testing and exploration of containerized environments.

These features are described in the sections below about features and commands.

### What `sarusctl` Is NOT

*   A tool to run compute jobs, especially at scale.
    Important features to run efficiently at scale, such as grouping multiple ranks on the same node into a single container or automatically importing host environment variables, are provided only by the **Skybox SPANK plugin**, just as they are provided by **Pyxis** (not Enroot) in the current CE.

*   A full Podman wrapper.
    `sarusctl` intentionally exposes only a limited subset of Podman-like functionality. Sarus Suite aims for integration through well-defined, idiomatic interfaces - not ownership or re-implementation of Podman semantics.

In more general terms, `sarusctl` is a utility for "Sarus Suite operations", which includes:

*   EDF operations, including validation;
*   Parallax storage operations.


## Validating and Rendering EDFs

The `sarusctl validate` command performs a quick validity check without launching a container:

```console
$ sarusctl validate ~/.edf/ubuntu.toml
/users/amadonna/.edf/ubuntu.toml is a valid EDF file
```

The `sarusctl render` command prints the **fully expanded representation** of an EDF, including default values that are not explicitly specified:

```console
$ cat ~/.edf/pyfr.toml 
image="ghcr.io/sarus-suite/sarus-suite/containerfiles-ci/pyfr:2.1-ompi5.0.9-ofi1.22-cuda12.8.1"
mounts = ["${PWD}:/pyfr", "${SCRATCH}:${SCRATCH}"]
workdir = "/pyfr"

[env]
PMIX_MCA_psec = "^munge"
UCX_WARN_UNUSED_ENV_VARS = "n"

[annotations]
com.sarus.perfmon="true"


$ sarusctl render pyfr
{
  "annotations": {
    "com.sarus.perfmon": "true"
  },
  "devices": [],
  "entrypoint": true,
  "env": {
    "PMIX_MCA_psec": "^munge",
    "UCX_WARN_UNUSED_ENV_VARS": "n"
  },
  "image": "ghcr.io/sarus-suite/sarus-suite/containerfiles-ci/pyfr:2.1-ompi5.0.9-ofi1.22-cuda12.8.1",
  "mounts": [
    "/users/amadonna:/pyfr",
    "/capstor/scratch/cscs/amadonna:/capstor/scratch/cscs/amadonna"
  ],
  "workdir": "/pyfr",
  "writable": true
}
```

`sarusctl render` shows how the EDF will be interpreted by Sarus Suite at runtime. It acts as a **second-level validation**, helping ensure the container definition matches user intent.

!!! note
    *   `render` applies **EDF search-path rules**.
    *   `validate` requires a full path to the EDF file.


## Running Containers Interactively

Containers can be launched interactively using `sarusctl run`, providing an EDF and optional command arguments:

```console
$ sarusctl run --help
Run container from EDF file

Usage: sarusctl run <FILEPATH> [CONTAINER_CMD]...

Arguments:
  <FILEPATH>
  [CONTAINER_CMD]...

Options:
  -h, --help  Print help


$ sarusctl run ubuntu cat /etc/os-release 
PRETTY_NAME="Ubuntu 24.04.3 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
VERSION="24.04.3 LTS (Noble Numbat)"
VERSION_CODENAME=noble
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=noble
LOGO=ubuntu-logo

$ sarusctl run ubuntu bash
amadonna@starlex-ln001:/$ ls -l
total 0
lrwxrwxrwx    1 amadonna ubuntu     7 Apr 22  2024 bin -> usr/bin
drwxr-xr-x    2 amadonna ubuntu     0 Apr 22  2024 boot
drwxr-xr-x    5 root     root     360 Apr 21 19:55 dev
drwxr-xr-x   33 amadonna ubuntu   120 Apr 21 19:55 etc
drwxr-xr-x    3 amadonna ubuntu     0 Jan 13 03:19 home
lrwxrwxrwx    1 amadonna ubuntu     7 Apr 22  2024 lib -> usr/lib
drwxr-xr-x    2 amadonna ubuntu     0 Jan 13 03:10 media
drwxr-xr-x    2 amadonna ubuntu     0 Jan 13 03:10 mnt
drwxr-xr-x    2 amadonna ubuntu     0 Jan 13 03:10 opt
dr-xr-xr-x 3820 nobody   nogroup    0 Apr  8 11:34 proc
drwx------    2 amadonna ubuntu     0 Jan 13 03:18 root
drwxr-xr-x    4 amadonna ubuntu    60 Apr 21 19:55 run
lrwxrwxrwx    1 amadonna ubuntu     8 Apr 22  2024 sbin -> usr/sbin
drwxr-xr-x    2 amadonna ubuntu     0 Jan 13 03:10 srv
dr-xr-xr-x   13 nobody   nogroup    0 Apr 13 23:20 sys
drwxrwxrwt   18 nobody   nogroup 3160 Apr 21 19:55 tmp
drwxr-xr-x   11 amadonna ubuntu     0 Jan 13 03:10 usr
drwxr-xr-x   11 amadonna ubuntu     0 Jan 13 03:18 var
amadonna@starlex-ln001:/$ exit
```

Key behavior:

*   Command-line arguments provided after the EDF are executed as commands inside the container, similarly to what happens with most container tools.
*   If no command is provided, the image entrypoint is executed.
*   The container runs **in the foreground** on the same host where `sarusctl` is invoked: `sarusctl run` is intended for interactive exploration, debugging, and pre-flight testing, either on login or compute nodes.
*   The container is removed automatically once the user command terminates.

`sarusctl run` is designed to behave consistently with EDF usage through Slurm: if the referenced image is not present in the read-only store, `sarusctl run` will automatically pull and migrate it:

```console
$ cat ~/.edf/debian13.toml 
image="debian:trixie"

$ sarusctl run debian13 cat /etc/os-release 
Pulling debian:trixie with Podman...
Migrating debian:trixie with Parallax...
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
VERSION="13 (trixie)"
VERSION_CODENAME=trixie
DEBIAN_VERSION_FULL=13.4
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
```


## Querying Available Images

The `sarusctl images` command lists images from both Podman's default storage and the read-only store used by Sarus Suite:

```console
$ sarusctl images
REPOSITORY                                                         TAG                                       IMAGE ID      CREATED        SIZE        R/O
docker.io/library/debian                                           trixie                                    94d8be26824c  2 weeks ago    146 MB      false
debian                                                             trixie                                    24fa35cacf16  2 weeks ago    3.49 kB     true
docker.io/library/debian                                           trixie                                    24fa35cacf16  2 weeks ago    3.49 kB     true
jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/pyfr          2.1-ompi5.0.9-ofi1.22-cuda12.8.1          e45475209a1d  8 weeks ago    66.3 kB     true
jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/sphexa        0.95-mpich4.3.2-ofi1.22-cuda12.8.1        2f74ba917abb  8 weeks ago    58.7 kB     true
jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/megatron-lm   0.15.2-pt25.11                            e5b9e1e7a18e  8 weeks ago    136 kB      true
jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/nccl-tests    2.17.9-ompi5.0.9-ofi1.22-cuda12.8.1       20b961f4e77f  2 months ago   55.5 kB     true
jfrog.svc.cscs.ch/ghcr/sarus-suite/containerfiles-ci/omb           7.5.2-ompi5.0.9-ofi1.22-cuda12.8.1        de1530cfce4b  2 months ago   56.8 kB     true
ubuntu                                                             24.04                                     917b79865e78  3 months ago   6.11 kB     true
docker.io/library/ubuntu                                           24.04                                     917b79865e78  3 months ago   6.11 kB     true
```

The `R/O` column indicates whether an image belongs to the read-only store.

!!! note
    Image sizes reported for read-only images are misleadingly small. Podman cannot track the underlying SquashFS files, so actual filesystem usage is not reflected.


## Migrating Images to the Read-Only Store

`sarusctl migrate` converts an image from Podman's default store into SquashFS format and transfers it to the read-only store.

This is the functional counterpart of:

```console
enroot import -x mount podman://<image>
```

Migration:

*   works on any image from the Podman default store, including locally built ones;
*   does **not** remove the source image from Podman's default storage.


## Pulling Images Directly

`sarusctl pull` pulls an image from an OCI registry and automatically migrates it to the read-only storage:

```console
$ sarusctl pull alpine:3.22
Pulling alpine:3.22 with Podman...
Migrating alpine:3.22 with Parallax...
```

While this functionality is also triggered automatically by `sarusctl run` and Skybox, pulling images explicitly without defining an EDF or allocating a Slurm job can be useful for debugging or tighter control.

Using the `sarusctl --verbose` global option propagates the output of the underlying Podman and Parallax commands:

```console
$ sarusctl --verbose pull alpine:3.22
Pulling alpine:3.22 with Podman...
Resolved "alpine" as an alias (/etc/containers/registries.conf.d/000-shortnames.conf)
Trying to pull docker.io/library/alpine:3.22...
Getting image source signatures
Copying blob 58e777220c39 done   | 
Copying config 6a2735c23f done   | 
Writing manifest to image destination
6a2735c23ff3a1a7c2afe285f58e1ef43d3c7d21886ec231aa16dba29be71826
Migrating alpine:3.22 with Parallax...
INFO[2026-04-22T07:55:37+02:00] Starting migration for image: alpine:3.22     component=cmd sub=migration
INFO[2026-04-22T07:55:37+02:00] Resolving full name                           component=cmd fn=resolveImageNames sub=migration
INFO[2026-04-22T07:55:37+02:00] Setting up SRC Store                          component=cmd fn=setupSrcStore sub=migration
INFO[2026-04-22T07:55:37+02:00] Mirror: creating temp dir for "/capstor/scratch/cscs/amadonna/.parallax_imagestore" 
INFO[2026-04-22T07:55:37+02:00] Mirror: rsync from /capstor/scratch/cscs/amadonna/.parallax_imagestore/ to /tmp/rsync-mirror-1745517656/ (no squash/) 
INFO[2026-04-22T07:55:37+02:00] Mirror setup: rsync from /capstor/scratch/cscs/amadonna/.parallax_imagestore/ to /tmp/rsync-mirror-1745517656/ 
INFO[2026-04-22T07:55:37+02:00]   rsync args [-a --include=overlay/ --include=overlay-containers/ --include=overlay-images/ --include=overlay-layers/ --include=storage.lock --include=userns.lock --exclude=* --delete /capstor/scratch/cscs/amadonna/.parallax_imagestore/ /tmp/rsync-mirror-1745517656/] 
INFO[2026-04-22T07:55:37+02:00] Mirror: creating squash symlink /tmp/rsync-mirror-1745517656/squash to /capstor/scratch/cscs/amadonna/.parallax_imagestore/squash 
INFO[2026-04-22T07:55:37+02:00] Copy mirror of /capstor/scratch/cscs/amadonna/.parallax_imagestore at /tmp/rsync-mirror-1745517656  component=cmd fn=setupScratchStore sub=migration
INFO[2026-04-22T07:55:37+02:00] Setting up scratch Store                      component=cmd fn=setupScratchStore sub=migration
INFO[2026-04-22T07:55:37+02:00] Mounting source image                         component=cmd fn="prep&mount" sub=migration
INFO[2026-04-22T07:55:37+02:00] Creating a dummy layer diff dir               component=cmd fn=createDummyFlatLayer sub=migration
INFO[2026-04-22T07:55:37+02:00] Put single dummy layer                        component=cmd fn=putFlattenedLayer sub=migration
INFO[2026-04-22T07:55:38+02:00] Reading overlay link from /tmp/rsync-mirror-1745517656  component=cmd fn=readOverlayLink sub=migration
INFO[2026-04-22T07:55:38+02:00] Building squash file                          component=cmd fn=createSquash sub=migration
INFO[2026-04-22T07:55:38+02:00] Symlinking squash                             component=cmd fn=createSquash sub=migration
INFO[2026-04-22T07:55:38+02:00] Migration successfully completed for image: edea7c8203a9430a1feb5cd5cc26f0303112e4689c6c8b99ad3a822b2c11bf08  component=cmd sub=migration
INFO[2026-04-22T07:55:38+02:00] Mirror-cleanup: remove mirror's squash symlink 
INFO[2026-04-22T07:55:38+02:00] Mirror-cleanup: rsync back from /tmp/rsync-mirror-1745517656/ to /capstor/scratch/cscs/amadonna/.parallax_imagestore/ 
```


## Removing Images from the Read-Only Store

`sarusctl rmi` removes an image - and its SquashFS backing file - from the read-only store.

It does **not** remove the corresponding image from Podman's default storage:

```console
$ sarusctl images | grep alpine
docker.io/library/alpine                                           3.22                                      6a2735c23ff3  4 days ago     8.87 MB     false
docker.io/library/alpine                                           3.22                                      edea7c8203a9  4 days ago     4.32 kB     true
alpine                                                             3.22                                      edea7c8203a9  4 days ago     4.32 kB     true

$ sarusctl rmi alpine:3.22

$ sarusctl images | grep alpine
docker.io/library/alpine                                           3.22                                      6a2735c23ff3  4 days ago     8.87 MB     false
```


## Skybox: the Slurm Integration

**Skybox** is a SPANK plugin that integrates EDF-defined Podman containers into the Slurm job life cycle. It fulfills the same role as **Pyxis** in the current CE production setup.

Skybox:

*   parses EDFs,
*   automatically pulls and migrates images,
*   creates containers optimized for HPC workloads (e.g. relaxed namespace isolation, SquashFS images),
*   runs **one container per compute node**, joining all ranks on that node,
*   imports the host environment,
*   cleans up containers at job termination.

The key user-visible difference is the use of the `--edf` option, instead of `--environment` used for Pyxis:

```console
$ srun -A csstaff --ntasks-per-node=4 --edf=ubuntu cat /etc/os-release | grep PRETTY
PRETTY_NAME="Ubuntu 24.04.3 LTS"
PRETTY_NAME="Ubuntu 24.04.3 LTS"
PRETTY_NAME="Ubuntu 24.04.3 LTS"
PRETTY_NAME="Ubuntu 24.04.3 LTS"
```

The `com.sarus.perfmon="true"` annotation enables performance timing output, which is useful for evaluating startup overhead. For example:

```console
$ cat .edf/ubuntu.toml 
image = "ubuntu:24.04"

[annotations]
com.sarus.perfmon = "true"

$ srun -A csstaff --edf ubuntu cat /etc/os-release | grep PRETTY
skybox-perf: Podman run elapsed time: 0.278427 sec
PRETTY_NAME="Ubuntu 24.04.3 LTS"
```


[](){#ref-sarus-suite-hpc-features}
## Enabling HPC Features

In current deployments of Sarus Suite, HPC features are enabled primarily through **CDI specs**, not annotations.
Work is ongoing to enable the CE vService to handle configuration of OCI hooks for Podman and align them with annotations.

!!! info "Default devices"
    The following devices are enabled automatically in Sarus Suite by the CE vService, if they are detected in a compute node when the vService is deployed:

    *   NVIDIA GPUs
    *   CXI device nodes (e.g. `/dev/cxi0`)
    *   `/dev/xpmem`
    *   `/dev/gdrdrv`

### NVIDIA GPUs

All GPUs available on a node are enabled in containers through the device specification `nvidia.com/gpu=all`.
Individual GPUs can be specified by passing the GPU ordinal id or the UUID of a given device, although these are more niche use cases.

The GDR driver device file must also be added to leverage GPUDirect RDMA:

```toml
devices = ["nvidia.com/gpu=all", "/dev/gdrdrv"]
```

### CXI Devices and libfabric for Slingshot

CXI device nodes are enabled via the `hpe.com/cxi=all` CDI spec (tentative name, potentially subject to change).

The `alps.cscs/cxi=all` CDI mounts Slingshot library dependencies and replaces the container's libfabric via an OCI hook, similarly to the Enroot CXI hook.

```toml
devices = ["hpe.com/cxi=all", "alps.cscs/cxi=all"]
```

### AWS OFI NCCL Plugin

The device specification `alps.cscs/aws-ofi-nccl` provides similar functionality to the Enroot AWS OFI NCCL hook: it mounts the AWS OFI NCCL plugin and sets related NCCL and libfabric environment variables.
For example:

```toml
devices = ["alps.cscs/aws-ofi-nccl=cuda-dl"]
```

Supported values map to the `com.hooks.aws_ofi_nccl.variant` annotation, e.g. `cuda-dl`, `cuda13`, `cuda12`, `rocm5`, `rocm6`.

### Example: CXI libfabric replacement and AWS OFI NCCL plugin mounting, assuming defaults from vService

```toml
devices = [
  "alps.cscs/cxi=all",
  "alps.cscs/aws-ofi-nccl=cuda-dl"
]
```

### Example: What actually happens with all defaults included

```toml
devices = [
  "alps.cscs/cxi=all",
  "alps.cscs/aws-ofi-nccl=cuda-dl",
  "hpe.com/cxi=all",
  "/dev/xpmem",
  "nvidia.com/gpu=all",
  "/dev/gdrdrv"
]
```


## Advanced Topics

### Sarus Suite Configuration

All Sarus Suite tools use the same configuration files (located under `/etc/sarus-suite`), which establish the admin-defined defaults on a given machine (e.g. the location of the read-only store, the path to specific utilities, etc).

Individual parameters from the system-wide configuration can be overridden at the EDF level using the annotations `com.sarus.<parameter>=<value>`.

### Custom CDI Specs

CDI specs are normally set by system administrators and/or automated provisioning mechanisms. As stated by the CDI standard, the default locations of CDI files are `/etc/cdi/` and `/var/run/cdi/`.

Given the current limitations in the CXI and AWS plugin CDI specs (as mentioned in the related section), in some use cases it is useful to have Podman access custom CDI files.

The locations where Podman looks for CDI files can be controlled by redefining the `cdi_spec_dirs` parameter in the user-specific `containers.conf` file (`$HOME/.config/containers/containers.conf`), for example:

```console
$ cat $HOME/.config/containers/containers.conf

[engine]
cdi_spec_dirs=["/etc/cdi", "/users/amadonna/.config/cdi/"]
```

The first entry preserves the default search directory, the following ones are arbitrary. Once a new location has been added, custom CDI files can be copied into that directory, and their device definitions can be used in EDFs or directly with Podman `--device` options.
