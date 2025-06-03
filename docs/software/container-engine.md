[](){#ref-container-engine}
# Container Engine

The Container Engine (CE) toolset is designed to enable computing jobs to seamlessly run inside Linux application containers, thus providing support for containerized user environments.

## Concept

Containers effectively encapsulate a software stack; however, to be useful in HPC computing environments, they often require the customization of bind mounts, environment variables, working directories, hooks, plugins, etc. 
To simplify this process, the Container Engine (CE) toolset supports the specification of user environments through Environment Definition Files.

An Environment Definition File (EDF) is a text file in the [TOML format](https://toml.io/en/) that declaratively and prescriptively represents the creation of a computing environment based on a container image.
Users can create their own custom environments and share, edit, or build upon already existing environments.

The Container Engine (CE) toolset leverages its tight integration with the Slurm workload manager to parse EDFs directly from the command line or batch script and instantiate containerized user environments seamlessly and transparently.

Through the EDF, container use cases can be abstracted to the point where end users perform their workflows as if they were operating natively on the computing system.

**Key Benefits**

 * *Freedom*: Container gives users full control of the user space. The user can decide what to install without involving a sysadmin.
 * *Reproducibility*: Workloads consistently run in the same environment, ensuring uniformity across job experimental runs.
 * *Portability*: The self-contained nature of containers simplifies the deployment across architecture-compatible HPC systems.
 * *Seamless Access to HPC Resources*: CE facilitates native access to specialized HPC resources like GPUs, interconnects, and other system-specific tools crucial for performance.

## Quick Start

Let's set up a containerized Ubuntu 24.04 environment on the scratch folder (`${SCRATCH}`).
Save this file below as `ubuntu.toml` in `${HOME}/.edf` directory (the default location of EDF files).
A more detailed explanation of each entry for the EDF can be seen in the [EDF reference][ref-ce-edf-reference].

```bash
image = "library/ubuntu:24.04"
mounts = ["/capstor/scratch/cscs/${USER}:/capstor/scratch/cscs/${USER}"]
workdir = "/capstor/scratch/cscs/${USER}"
```


!!! note
    Create `${HOME}/.edf` if the folder doesn't exist.

Use Slurm in the cluster login node to start the environment above:

```bash
$ srun --environment=ubuntu --pty bash
```

The terminal snippet below demonstrates how to launch a containerized environment using Slurm with the `--environment` option.
Click on the :fontawesome-solid-circle-plus: icon for information on each command.

```console
[daint-ln002]$ srun --environment=ubuntu --pty bash   # (1)

[nid005333]$ pwd                                      # (2)
/capstor/scratch/cscs/<username>

[nid005333]$ cat /etc/os-release                      # (3)
PRETTY_NAME="Ubuntu 24.04 LTS"
NAME="Ubuntu"
VERSION_ID="24.04"
...

[nid005333]$ exit                                     # (4)
[daint-ln002]$
```

1.  Starting an interactive shell session within the Ubuntu 24.04 container deployed on a compute node using `srun --environment=ubuntu --pty bash`.
2.  Check the current folder (dubbed _the working directory_) is set to the user's scratch folder, as per EDF.
3.  Show the OS version of your container (using `cat /etc/os-release`) based on Ubuntu 24.04 LTS.
4.  Exiting the container (`exit`), returning to the login node.

!!! note
    CE pulls the image automatically when the container starts.

## Running containerized environments

Specifying the `--environment` option to the Slurm command (e.g., `srun` or `salloc`) will make it run inside the EDF environment: 

!!! example "Specifying EDF with an absolute path"
    ```bash
    $ srun --environment=$SCRATCH/edf/debian.toml cat /etc/os-release
    PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
    NAME="Debian GNU/Linux"
    VERSION_ID="12"
    ...
    ```

`--environment` can be a relative path from the current working directory (i.e., where the Slurm command is executed). 
A relative path should be prepended by `./`:

!!! example "Specifying EDF with a relative path"
    ```bash
    $ ls
    debian.toml

    $ srun --environment=./debian.toml cat /etc/os-release
    PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
    NAME="Debian GNU/Linux"
    VERSION_ID="12"
    ...
    ```

If an EDF is located in the [EDF search path][ref-ce-edf-search-path], `--environment` also accepts the EDF filename without the `.toml` extension:

!!! example "Specifying EDF in the default search path"
    ```bash
    $ srun --environment=debian cat /etc/os-release
    PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
    NAME="Debian GNU/Linux"
    VERSION_ID="12"
    ...
    ```

### Use from batch scripts

The recommended approach is to use `--environment` as part of the Slurm command (e.g., `srun` or `salloc`):

!!! example "Adding `--environment` to `srun`"
    ```bash
    #!/bin/bash
    #SBATCH --job-name=edf-example
    ...

    # Run job step
    srun --environment=debian cat /etc/os-release
    ```

Alternatively, the `--environment` option can also be specified with an `#SBATCH` option.
However, the support status is still **experimental** and may result in unexpected behaviors.

!!! note
    Specifying `--environment` with `#SBATCH` will put the entire batch script inside the containerized environment, requiring the Slurm hook to use any Slurm commands within the batch script (e.g., `srun` or `scontrol`). 
    The hook is controlled by the `ENROOT_SLURM_HOOK` environment variable and activated by default on most vClusters.

[](){#ref-ce-edf-search-path}
### EDF search path

By default, the EDFs for each user are looked up in `$HOME/.edf`.
The default EDF search path can be changed through the `EDF_PATH` environment variable.
`EDF_PATH` must be a colon-separated list of absolute paths to directories, where the CE searches each directory in order.
If an EDF is located in the search path, its name can be used in the `--environment` option without the `.toml` extension.

!!! example "Using `EDF_PATH` to control the default search path"
    ```bash
    $ ls ~/.edf
    debian.toml

    $ ls ~/example-project
    fedora-env.toml

    $ export EDF_PATH="$HOME/example-project"

    $ srun --environment=fedora-env cat /etc/os-release
    NAME="Fedora Linux"
    VERSION="40 (Container Image)"
    ID=fedora
    ...
    ```

## Image Management

### Image cache

By default, images defined in the EDF as remote registry references (e.g. a Docker reference) are automatically pulled and locally cached.
A cached image would be preferred to pulling the image again in later usage.

An image cache is automatically created at `.edf_imagestore` in the user's scratch folder (i.e., `${SCRATCH}/.edf_imagestore`), under which cached images are stored with the corresponding CPU architecture suffix (e.g., `x86` and `aarch64`).
Cached images may be subject to the automatic cleaning policy of the scratch folder.
 
Should users want to re-pull a cached image, they have to remove the corresponding image in the cache.

To choose an alternative image store path (e.g., to use a directory owned by a group and not to an individual user), users can specify an image cache path explicitly by defining the environment variable `EDF_IMAGESTORE`.
 `EDF_IMAGESTORE` must be an absolute path to an existing folder.

!!! note
    If the CE cannot create a directory for the image cache, it operates in cache-free mode, meaning that it pulls an ephemeral image before every container launch and discards it upon termination.

### Pulling images manually

To work with images stored from the NGC Catalog, please refer also to the next section "Using images from third party registries and private repositories".

To bypass any caching behavior, users can manually pull an image and directly plug it into their EDF.
To do so, users may execute `enroot import docker://[REGISTRY#]IMAGE[:TAG]` to pull container images from OCI registries to the current directory.

After the import is complete, images are available in Squashfs format in the current directory and can be used in EDFs:

!!! example "Manually pulling an `nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04` image"
    ```console
    $ cd ${SCRATCH}
    $ enroot import docker://nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
    [INFO] Querying registry for permission grant
    [INFO] Authenticating with user: <anonymous>
    ...
    Number of gids 1
        root (0)

    $ ls *.sqsh
    nvidia+cuda+11.8.0-cudnn8-devel-ubuntu22.04.sqsh

    $ cat ${HOME}/.edf/example.toml      # (1)
    image = "/capstor/scratch/cscs/${USER}/nvidia+cuda+11.8.0-cudnn8-devel-ubuntu22.04.sqsh"
    ```

    1. Assuming `example.toml` is already written at `${HOME}/.edf`. 

!!! note
    It is recommended to save images in `/capstor/scratch/cscs/${USER}` or its subdirectories before using them with the CE.

[](){#ref-ce-third-party-private-registries}
### Third-party and private registries

[Docker Hub](https://hub.docker.com/) is the default registry from which remote images are imported.

!!! warning "Registry rate limits"
    Some registries will rate limit image pulls by IP address.
    Since [public IPs are a shared resource][ref-guides-internet-access] we recommend authenticating even for publicly available images.
    For example, [Docker Hub applies its rate limits per user when authenticated](https://docs.docker.com/docker-hub/usage/).

To use an image from a different registry, the corresponding registry URL has to be prepended to the image reference, using a hash character (#) as a separator:

!!! example "Using a third-party registry within an EDF"
    ```bash
    $ cat ${HOME}/.edf/example.toml    # (1)
    image = "nvcr.io#nvidia/nvhpc:23.7-runtime-cuda11.8-ubuntu22.04"
    ```
    
    1. Assuming `example.toml` is already written at `${HOME}/.edf`. 

!!! example "Using a third-party registry on the command line"
    ```bash
    $ enroot import docker://nvcr.io#nvidia/nvhpc:23.7-runtime-cuda11.8-ubuntu22.04
    ```

To import images from private repositories, access credentials should be configured by individual users in the `$HOME/.config/enroot/.credentials` file, following the [netrc file format](https://everything.curl.dev/usingcurl/netrc).
Using the `enroot import` documentation page as a reference:

??? example "`netrc` example"
    ```bash
    # NVIDIA NGC catalog (both endpoints are required)
    machine nvcr.io login $oauthtoken password <token>
    machine authn.nvidia.com login $oauthtoken password <token>

    # DockerHub
    machine auth.docker.io login <login> password <password>

    # Google Container Registry with OAuth
    machine gcr.io login oauth2accesstoken password $(gcloud auth print-access-token)
    # Google Container Registry with JSON
    machine gcr.io login _json_key password $(jq -c '.' $GOOGLE_APPLICATION_CREDENTIALS | sed 's/ /\\u0020/g')

    # Amazon Elastic Container Registry
    machine 12345.dkr.ecr.eu-west-2.amazonaws.com login AWS password $(aws ecr get-login-password --region eu-west-2)

    # Azure Container Registry with ACR refresh token
    machine myregistry.azurecr.io login 00000000-0000-0000-0000-000000000000 password $(az acr login --name myregistry --expose-token --query accessToken  | tr -d '"')
    # Azure Container Registry with ACR admin user
    machine myregistry.azurecr.io login myregistry password $(az acr credential show --name myregistry --subscription mysub --query passwords[0].value | tr -d '"')

    # Github.com Container Registry (GITHUB_TOKEN needs read:packages scope)
    machine ghcr.io login <username> password <GITHUB_TOKEN>

    # GitLab Container Registry (GITLAB_TOKEN needs a scope with read access to the container registry)
    # GitLab instances often use different domains for the registry and the authentication service, respectively
    # Two separate credential entries are required in such cases, for example:
    # Gitlab.com
    machine registry.gitlab.com login <username> password <GITLAB TOKEN>
    machine gitlab.com login <username> password <GITLAB TOKEN>

    # ETH Zurich GitLab registry
    machine registry.ethz.ch login <username> password <GITLAB_TOKEN>
    machine gitlab.ethz.ch login <username> password <GITLAB_TOKEN>  
    ```

[](){#ref-ce-annotations}
## Annotations

Annotations define arbitrary metadata for containers in the form of key-value pairs.
Within the EDF, annotations are designed to be similar in appearance and behavior to those defined by the [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec/blob/main/config.md#annotations).
Annotation keys usually express a hierarchical namespace structure, with domains separated by "." (full stop) characters.

As annotations are often used to control hooks, they have a deep nesting level.
For example, to execute the [SSH hook][ref-ce-ssh-hook] described below, the annotation `com.hooks.ssh.enabled` must be set to the string `true`.

EDF files support setting annotations through the `annotations` table.
This can be done in multiple ways in TOML: for example, both of the following usages are equivalent:

!!! example "Nest levels in the TOML key"
    ```bash
    [annotations]
    com.hooks.ssh.enabled = "true"
    ```

!!! example "Nest levels in the TOML table name"
    ```bash
    [annotations.com.hooks.ssh]
    enabled = "true"
    ```

??? note "Relevant details of the TOML format"
     * All property assignments belong to the section immediately preceding them (the statement in square brackets), which defines the table they refer to.

     * Tables, on the other hand, do not automatically belong to the tables declared before them; to nest tables, their name has to list their parents using the dot notations (so the previous example defines the table `ssh` inside `hooks`, which in turn is inside `com`, which is inside `annotations`).

     * An assignment can implicitly define subtables if the key you assign is a dotted list. As a reference, see the examples made earlier in this section, where assigning a string to the `com.hooks.ssh.enabled` attribute within the `[annotations]` table is exactly equivalent to assigning to the `enabled` attribute within the `[annotations.com.hooks.ssh]` subtable.

     * Attributes can be added to a table only in one place in the TOML file. In other words, each table must be defined in a single square bracket section. For example, Case 3 in the example below is invalid because the `ssh` table was doubly defined both in the `[annotations]` and in the `[annotations.com.hooks.ssh]` sections. See the [TOML format](https://toml.io/en/) spec for more details.

    !!! example ":white_check_mark: Valid usage"
        ```bash
        [annotations.com.hooks.ssh]
        authorize_ssh_key = "/capstor/scratch/cscs/<username>/tests/edf/authorized_keys"
        enabled = "true"
        ```

    !!! example ":white_check_mark: Valid usage"
        ```bash
        [annotations]
        com.hooks.ssh.authorize_ssh_key = "/capstor/scratch/cscs/<username>/tests/edf/authorized_keys"
        com.hooks.ssh.enabled = "true"
        ```

    !!! example ":x: Invalid usage"
        ```bash
        [annotations]
        com.hooks.ssh.authorize_ssh_key = "/capstor/scratch/cscs/<username>/tests/edf/authorized_keys"

        [annotations.com.hooks.ssh]
        enabled = "true"
        ```

## Accessing native resources

### NVIDIA GPUs

The Container Engine leverages components from the NVIDIA Container Toolkit to expose NVIDIA GPU devices inside containers.
GPU device files are always mounted in containers, and the NVIDIA driver user space components are  mounted if the `NVIDIA_VISIBLE_DEVICES` environment variable is not empty, unset or set to `void`.
`NVIDIA_VISIBLE_DEVICES` is already set in container images officially provided by NVIDIA to enable all GPUs available on the host system.
Such images are frequently used to containerize CUDA applications, either directly or as a base for custom images, thus in many cases no action is required to access GPUs.

!!! example "Cluster with 4 GH200 devices per node"
    ```bash
    $ cat cuda12.5.1.toml       # (1)
    image = "nvidia/cuda:12.5.1-devel-ubuntu24.04"

    $ srun --environment=./cuda12.5.1.toml nvidia-smi
    Thu Oct 26 17:59:36 2023       
    +------------------------------------------------------------------------------------+
    | NVIDIA-SMI 535.129.03          Driver Version: 535.129.03   CUDA Version: 12.5     |
    |--------------------------------------+----------------------+----------------------+
    | GPU  Name              Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
    | Fan  Temp   Perf       Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
    |                                      |                      |               MIG M. |
    |======================================+======================+======================|
    |   0  GH200 120GB                 On  | 00000009:01:00.0 Off |                    0 |
    | N/A   24C    P0           89W / 900W |     37MiB / 97871MiB |      0%   E. Process |
    |                                      |                      |             Disabled |
    +--------------------------------------+----------------------+----------------------+
    |   1  GH200 120GB                 On  | 00000019:01:00.0 Off |                    0 |
    | N/A   24C    P0           87W / 900W |     37MiB / 97871MiB |      0%   E. Process |
    |                                      |                      |             Disabled |
    +--------------------------------------+----------------------+----------------------+
    |   2  GH200 120GB                 On  | 00000029:01:00.0 Off |                    0 |
    | N/A   24C    P0           83W / 900W |     37MiB / 97871MiB |      0%   E. Process |
    |                                      |                      |             Disabled |
    +--------------------------------------+----------------------+----------------------+
    |   3  GH200 120GB                 On  | 00000039:01:00.0 Off |                    0 |
    | N/A   24C    P0           85W / 900W |     37MiB / 97871MiB |      0%   E. Process |
    |                                      |                      |             Disabled |
    +--------------------------------------+----------------------+----------------------+
                                                                                             
    +------------------------------------------------------------------------------------+
    | Processes:                                                                         |
    |  GPU   GI   CI        PID   Type   Process name                         GPU Memory |
    |        ID   ID                                                          Usage      |
    |====================================================================================|
    |  No running processes found                                                        |
    +------------------------------------------------------------------------------------+
    ```

    1. Assuming `cuda12.5.1.toml` is present the current folder. 

It is possible to use environment variables to control which capabilities of the NVIDIA driver are enabled inside containers.
Additionally, the NVIDIA Container Toolkit can enforce specific constraints for the container, for example, on versions of the CUDA runtime or driver, or on the architecture of the GPUs.
For the full details about using these features, please refer to the official documentation: [Driver Capabilities](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html#driver-capabilities), [Constraints](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html#constraints).

[](){#ref-ce-container-hooks}
## Container Hooks

Container hooks let you customize container behavior to fit system-specific needs, making them especially valuable for High-Performance Computing.

 * *What they do*: Hooks extend container runtime functionality by enabling custom actions during a container's lifecycle.
 * *Use for HPC*: HPC systems rely on specialized hardware and fine-tuned software, unlike generic containers. Hooks bridge this gap by allowing containers to access these system-specific resources or enable custom features.

!!! info
    This section outlines all hooks supported in production by the Container Engine.
    However, specific Alps vClusters may support only a subset or use custom configurations.
    For details about available features in individual vClusters, consult platform documentation or contact CSCS support.

[](){#ref-ce-cxi-hook}
### HPE Slingshot interconnect 

!!! tip
    On most vClusters, the CXI hook for Slingshot connectivity is enabled implicitly by default or by other hooks.
    Therefore, entering the enabling annotation in the EDF is unnecessary in many cases.

!!! note "Required annotation"
    ```bash
    com.hooks.cxi.enabled = "true"
    ```

The Container Engine provides a hook to allow containers relying on [libfabric](https://ofiwg.github.io/libfabric/) to leverage the HPE Slingshot 11 high-speed interconnect.
This component is commonly referred to as the "CXI hook", taking its name from the CXI libfabric provider required to interface with Slingshot 11.
The hook leverages bind-mounting the custom host libfabric library into the container (in addition to all the required dependency libraries and devices as well).

If a libfabric library is already present in the container filesystem (for example, it's provided by the image), it is replaced with its host counterpart, otherwise the host libfabric is just added to the container.

!!! note
    Due to the nature of Slingshot and the mechanism implemented by the CXI hook, container applications need to use a communication library which supports libfabric in order to benefit from usage of the hook.

!!! note
    Libfabric support might have to be defined at compilation time (as is the case for some MPI implementations, like MPICH and OpenMPI) or could be dynamically available at runtime (as is the case with NCCL - see also [this][ref-ce-aws-ofi-hook] section for more details).

The hook is activated by setting the `com.hooks.cxi.enabled` annotation, which can be defined in the EDF.

??? example "Comparison between with and without the CXI hook"
    * Without the CXI hook

    ```bash
    $ cat ${HOME}/.edf/osu-mb.toml 
    image = "quay.io#madeeks/osu-mb:6.2-mpich4.1-ubuntu22.04-arm64"

    [annotations]
    com.hooks.cxi.enabled = "false"

    $ srun -N2 --mpi=pmi2 --environment=osu-mb ./osu_bw
    # OSU MPI Bandwidth Test v6.2
    # Size      Bandwidth (MB/s)
    1                       0.22
    2                       0.40
    4                       0.90
    8                       1.82
    16                      3.41
    32                      6.81
    64                     13.18
    128                    26.74
    256                    11.95
    512                    38.06
    1024                   39.65
    2048                   83.22
    4096                  156.14
    8192                  143.08
    16384                  53.78
    32768                 106.77
    65536                  49.88
    131072                871.86
    262144                780.97
    524288                694.58
    1048576               831.02
    2097152              1363.30
    4194304              1279.54
    ```

    * With the CXI hook enabling access to the Slingshot high-speed network

    ```bash
    $ cat ${HOME}/.edf/osu-mb-cxi.toml 
    image = "quay.io#madeeks/osu-mb:6.2-mpich4.1-ubuntu22.04"

    [annotations]
    com.hooks.cxi.enabled = "true"

    $ srun -N2 --mpi=pmi2 --environment=osu-mb-cxi ./osu_bw
    # OSU MPI Bandwidth Test v6.2
    # Size      Bandwidth (MB/s)
    1                       1.21
    2                       2.32
    4                       4.85
    8                       8.38
    16                     19.36
    32                     38.47
    64                     76.28
    128                   151.76
    256                   301.25
    512                   604.17
    1024                 1145.03
    2048                 2367.25
    4096                 4817.16
    8192                 8633.36
    16384               16971.18
    32768               18740.55
    65536               21978.65
    131072              22962.31
    262144              23436.78
    524288              23672.92
    1048576             23827.78
    2097152             23890.95
    4194304             23925.61
    ```

[](){#ref-ce-aws-ofi-hook}
### AWS OFI NCCL Hook 

!!! note "Required annotation"
    ```bash
    com.hooks.aws_ofi_nccl.enabled = "true"
    com.hooks.aws_ofi_nccl.variant = "cuda12"   # (1)
    ```

    1. `com.hooks.aws_ofi_nccl.variant` may vary depending on vClusters. Details below.

The [AWS OFI NCCL plugin](https://github.com/aws/aws-ofi-nccl) is a software extension that allows the [NCCL](https://developer.nvidia.com/nccl) and [RCCL](https://rocm.docs.amd.com/projects/rccl/en/latest/) libraries to use libfabric as a network provider and, through libfabric, to access the Slingshot high-speed interconnect.
Also see [NCCL][ref-communication-nccl] and [libfabric][ref-communication-libfabric] for more information on using the libraries on Alps.

The Container Engine includes a hook program to inject the AWS OFI NCCL plugin in containers; since the plugin must also be compatible with the GPU programming software stack being used, the `com.hooks.aws_ofi_nccl.variant` annotation is used to specify a plugin variant suitable for a given container image.
At the moment of writing, 4 plugin variants are configured: `cuda11`, `cuda12` (to be used on NVIDIA GPU nodes), `rocm5`, and `rocm6` (to be used on AMD GPU nodes alongside RCCL).

!!! example "EDF for the NGC PyTorch 22.12 image with Cuda 11"
    ```bash
    image = "nvcr.io#nvidia/pytorch:22.12-py3"
    mounts = ["/capstor/scratch/cscs/${USER}:/capstor/scratch/cscs/${USER}"]

    [annotations]
    com.hooks.aws_ofi_nccl.enabled = "true"
    com.hooks.aws_ofi_nccl.variant = "cuda11"
    ```

!!! tip
    It implicitly enables the [CXI hook][ref-ce-cxi-hook], therefore exposing the Slingshot interconnect to container applications. In other words, when enabling the AWS OFI NCCL hook, it's unnecessary to also enable the CXI hook separately in the EDF.

!!! note
    It sets environment variables to control the behavior of NCCL and the libfabric CXI provider for Slingshot. In particular, the `NCCL_NET_PLUGIN` variable ([link](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html#nccl-net-plugin)) is set to force NCCL to load the specific network plugin mounted by the hook. This is useful because certain container images (for example, those from NGC repositories) might already ship with a default NCCL plugin. Other environment variables help prevent application stalls and improve performance when using GPUDirect for RDMA communication.

[](){#ref-ce-ssh-hook}
### SSH Hook

!!! note "Required annotation"
    ```bash
    com.hooks.ssh.enabled = "true"
    com.hooks.ssh.authorize_ssh_key = "<public-key>"    # (1)
    ```

    1. Replace `<public-key>` with your SSH public key.

!!! warning 
    The `srun` command launching an SSH-connectable container **should set the `--pty` option** in order for the hook to initialize properly.

The SSH hook runs a lightweight, statically-linked SSH server (a build of [Dropbear](https://matt.ucc.asn.au/dropbear/dropbear.html)) inside the container.
While the container is running, it's possible to connect to it from a remote host using a private key matching the public one authorized in the EDF annotation.
It can be useful to add SSH connectivity to containers (for example, enabling remote debugging) without bundling an SSH server into the container image or creating ad-hoc image variants for such purposes.

The `com.hooks.ssh.authorize_ssh_key` annotation allows the authorization of a custom public SSH key for remote connections.
The annotation value must be the absolute path to a text file containing the public key (just the public key without any extra signature/certificate).
After the container starts, it is possible to get a remote shell inside the container by connecting with SSH to the listening port.

By default, the server started by the SSH hook listens to port 15263, but this setting can be controlled through the `com.hooks.ssh.port` annotation in the EDF.

!!! example "Logging into a sleeping container via SSH"
    * On the cluster
    ```bash
    $ cat ubuntu-ssh.toml
    image = "ubuntu:latest"

    [annotations]
    com.hooks.ssh.enabled = "true"
    com.hooks.ssh.authorize_ssh_key = "<public-key>"

    $ srun --environment=./ubuntu-ssh.toml --pty sleep 30
    ```

    * On the remote shell
    ```bash
    ssh -p 15263 <host-of-container>
    ```

!!! note
    The container must be **writable** (default) to use the SSH hook.

!!! info
    In order to establish connections through Visual Studio Code [Remote - SSH](https://code.visualstudio.com/docs/remote/ssh) extension, the `scp` program must be available inside the container.
    This is required to send and establish the VS Code Server into the remote container.

### NVIDIA CUDA MPS Hook

!!! note "Require annotation"
    ```bash
    com.hooks.nvidia_cuda_mps.enabled = "true"
    ```

On several Alps vClusters, NVIDIA GPUs by default operate in "Exclusive process" mode, that is, the CUDA driver is configured to allow only one process at a time to use a given GPU.
For example, on a node with 4 GPUs, a maximum of 4 CUDA processes can run at the same time.

!!! example "Available GPUs and oversubscription error"
    ```bash
    $ nvidia-smi -L
    GPU 0: GH200 120GB (UUID: GPU-...)
    GPU 1: GH200 120GB (UUID: GPU-...)
    GPU 2: GH200 120GB (UUID: GPU-...)
    GPU 3: GH200 120GB (UUID: GPU-...)

    $ cat ${HOME}/.edf/vectoradd-cuda.toml        # (1)
    image = "nvcr.io#nvidia/k8s/cuda-sample:vectoradd-cuda12.5.0-ubuntu22.04"

    $ srun -t2 -N1 -n4 --environment=vectoradd-cuda /cuda-samples/vectorAdd | grep "Test PASSED"    # (2)
    Test PASSED
    Test PASSED
    Test PASSED
    Test PASSED

    $ srun -t2 -N1 -n5 --environment=vectoradd-cuda /cuda-samples/vectorAdd | grep "Test PASSED"    # (3)
    Failed to allocate device vector A (error code CUDA-capable device(s) is/are busy or unavailable)!
    srun: error: ...
    ```

    1. This EDF uses the CUDA vector addition sample from NVIDIA's NGC catalog.
    2. 4 processes run successfully.
    3. More than 4 concurrent processes result in oversubscription errors.

In order to run multiple processes concurrently on the same GPU (one example could be running multiple MPI ranks on the same device), the [NVIDIA CUDA Multi-Process Service](https://docs.nvidia.com/deploy/mps/index.html) (or MPS, for short) must be started on the compute node.

The Container Engine provides a hook to automatically manage the setup and removal of the NVIDIA CUDA MPS components within containers.
The hook can be activated by setting the `com.hooks.nvidia_cuda_mps.enabled` to the string `true`.

!!! example "Using the CUDA MPS hook"
    ```bash
    $ cat vectoradd-cuda-mps.toml
    image = "nvcr.io#nvidia/k8s/cuda-sample:vectoradd-cuda12.5.0-ubuntu22.04"

    [annotations]
    com.hooks.nvidia_cuda_mps.enabled = "true"

    $ srun -t2 -N1 -n8 --environment=./vectoradd-cuda-mps.toml /cuda-samples/vectorAdd | grep "Test PASSED" | wc -l
    8
    ```

!!! note
    The container must be **writable** (default) to use the CUDA MPS hook.

!!! info
    When using the NVIDIA CUDA MPS hook it is not necessary to use other wrappers or scripts to manage the Multi-Process Service, as is documented for native jobs on some vClusters.

[](){#ref-ce-edf-reference}
## EDF Reference

EDF files use the [TOML format](https://toml.io/en/). For details about the data types used by the different parameters, please refer to the [TOML spec webpage](https://toml.io/en/v1.0.0).

In the following, the default value is none (i.e., the empty value of the corresponding type) if not specified.

### (ARRAY or STRING) base_environment

Ordered list of EDFs that this file inherits from. Parameters from listed environments are evaluated sequentially. Supports up to 10 levels of recursion.

??? note
     * Parameters from the listed environments are evaluated sequentially, adding new entries or overwriting previous ones, before evaluating the parameters from the current EDF. In other words, the current EDF inherits the parameters from the EDFs listed in `base_environment`. When evaluating `mounts` or `env` parameters, values from downstream EDFs are appended to inherited values.
     * The individual EDF entries in the array follow the same search rules as the arguments of the `--environment` CLI option for Slurm; they can be either file paths or filenames without extension if the file is located in the [EDF search path][ref-ce-edf-search-path].
     * This parameter can be a string if there is only one base environment.

??? example
     * Single environment inheritance:
        ```bash
        base_environment = "common_env"
        ```

     * Multiple environment inheritance:
        ```bash
        base_environment = ["common_env", "ml_pytorch_env1"]
        ```

### (STRING) image

The container image to use. Can reference a remote Docker/OCI registry or a local Squashfs file as a filesystem path.

??? note
     * The full format for remote references is `[USER@][REGISTRY#]IMAGE[:TAG]`.
         * `[REGISTRY#]`: (optional) registry URL, followed by #. Default: Docker Hub.
         * `IMAGE`: image name.
         * `[:TAG]`: (optional) image tag name, preceded by :.
     * The registry user can also be specified in the `$HOME/.config/enroot/.credentials` file.

??? example
     * Reference of Ubuntu image in the Docker Hub registry (default registry)
        ```bash
        image = "library/ubuntu:24.04"
        ```

     * Explicit reference of Ubuntu image in the Docker Hub registry
        ```bash
        image = "docker.io#library/ubuntu:24.04"
        ```

     * Reference to PyTorch image from NVIDIA Container Registry (nvcr.io)
        ```bash
        image = "nvcr.io#nvidia/pytorch:22.12-py3"
        ```

     * Image from third-party quay.io registry
        ```bash
        image = "quay.io#madeeks/osu-mb:6.2-mpich4.1-ubuntu22.04-arm64"
        ```

     * Reference to a manually pulled image stored in parallel FS
        ```bash
        image = "/path/to/image.squashfs"
        ```

### (STRING) workdir

Initial working directory when the container starts. Default: inherited from image.

??? example
     * Workdir pointing to a user defined project path 
        ```bash
        workdir = "/home/user/projects"
        ```
     * Workdir pointing to the `/tmp` directory
        ```bash
        workdir = "/tmp"
        ```

### (BOOL) entrypoint

If true, run the entrypoint from the container image. Default: true.

??? example
    ```bash
    entrypoint = false
    ```

### (BOOL) writable

If false, the container filesystem is read-only. Default: false.

??? example
    ```bash
    writable = true
    ```

### (ARRAY) mounts

List of bind mounts in the format `SOURCE:DESTINATION[:FLAGS]`. Flags are optional and can include `ro`, `private`, etc.

??? note
    * Mount flags are separated with a plus symbol, for example: `ro+private`.
    * Optional flags from docker format or OCI (need reference)

??? example

     * Literal fixed mount map
        ```bash
        mounts = ["/capstor/scratch/cscs/amadonna:/capstor/scratch/cscs/amadonna"]
        ```

     * Mapping path with `env` variable expansion
        ```bash
        mounts = ["/capstor/scratch/cscs/${USER}:/capstor/scratch/cscs/${USER}"]
        ```

     * Mounting the scratch filesystem using a host environment variable
        ```bash
        mounts = ["${SCRATCH}:/scratch"]
        ```


### (TABLE) env

Environment variables to set in the container. Null-string values will unset the variable. Default: inherited from the host and the image.

??? note
    * By default, containers inherit environment variables from the container image and the host environment, with variables from the image taking precedence.
    * The env table can be used to further customize the container environment by setting, modifying, or unsetting variables.
    * Values of the table entries must be strings. If an entry has a null value, the variable corresponding to the entry key is unset in the container.


??? example

     * Basic `env` block
        ```bash
        [env]
        MY_RUN = "production",
        DEBUG = "false"
        ```

     * Use of environment variable expansion
        ```bash
        [env]
        MY_NODE = "${VAR_FROM_HOST}",
        PATH = "${PATH}:/custom/bin", 
        DEBUG = "true"
        ```


### (TABLE) annotations

OCI-like annotations for the container. For more details, refer to the [Annotations][ref-ce-annotations] section.

??? example

     * Disabling the CXI hook
        ```bash
        [annotations]
        com.hooks.cxi.enabled = "false"
        ```

     * Control of SSH hook parameters via annotation and variable expansion
        ```bash
        [annotations.com.hooks.ssh]
        authorize_ssh_key = "/capstor/scratch/cscs/${USER}/tests/edf/authorized_keys"
        enabled = "true"
        ```

     * Alternative example for usage of annotation with fixed path
        ```bash
        [annotations]
        com.hooks.ssh.authorize_ssh_key = "/path/to/authorized_keys"
        com.hooks.ssh.enabled = "true"
        ```

!!! note
    Environment variable expansion and relative paths expansion are only available on the Bristen vCluster as technical preview.

### Environment Variable Expansion

Environment variable expansion allows for dynamic substitution of environment variable values within the EDF (Environment Definition File). This capability applies across all configuration parameters in the EDF, providing flexibility in defining container environments.

 * *Syntax*. Use ${VAR} to reference an environment variable VAR. The variable's value is resolved from the combined environment, which includes variables defined in the host and the container image, the later taking precedence.
 * *Scope*. Variable expansion is supported across all EDF parameters. This includes EDF’s parameters like mounts, workdir, image, etc. For example, ${SCRATCH} can be used in mounts to reference a directory path.
 * *Undefined Variables*. Referencing an undefined variable results in an error. To safely handle undefined variables, you can use the syntax ${VAR:-}, which evaluates to an empty string if VAR is undefined.
 * *Preventing Expansion*. To prevent expansion, use double dollar signs $$. For example, $$${VAR} will render as the literal string ${VAR}.
 * *Limitations*
    * Variables defined within the [env] EDF table cannot reference other entries from [env] tables in the same or other EDF files (e.g. the ones entered as base environments) . Therefore, only environment variables from the host or image can be referenced.
 * *Environment Variable Resolution Order*. The environment variables are resolved based on the following order:
     * TOML env: Variable values as defined in EDF’s env.
     * Container Image: Variables defined in the container image's environment take precedence.
     * Host Environment: Environment variables defined in the host system.

### Relative paths expansion

Relative filesystem paths can be used within EDF parameters, and will be expanded by the CE at runtime. The paths are interpreted as relative to the working directory of the process calling the CE, not to the location of the EDF file.

## Known Issues

### Compatibility with Alpine Linux

Alpine Linux is incompatible with some hooks, causing errors when used with Slurm. For example,

```bash
> cat alpine.toml
image = "alpine: *19"
> srun -lN1 --environment=alpine.toml echo "abc"
0: slurmstepd: error: pyxis: container start failed with error code: 1
0: slurmstepd: error: pyxis: printing enroot log file:
0: slurmstepd: error: pyxis:     [ERROR] Failed to refresh the dynamic linker cache
0: slurmstepd: error: pyxis:     [ERROR] /etc/enroot/hooks.d/87-slurm.sh exited with return code 1
0: slurmstepd: error: pyxis: couldn't start container
0: slurmstepd: error: spank: required plugin spank_pyxis.so: task_init() failed with rc=-1
0: slurmstepd: error: Failed to invoke spank plugin stack
```

This is because some hooks (e.g., Slurm and CXI hooks) leverage `ldconfig` (from Glibc) when they bind-mount host libraries inside containers; since Alpine Linux provides an alternative `ldconfig` (from Musl Libc), it does not work as intended by hooks. As a workaround, users may disable problematic hooks. For example,

```bash
$ cat alpine_workaround.toml
image = "alpine: *19"

[annotations]
com.hooks.slurm.enabled = "false"
com.hooks.cxi.enabled = "false"

$ srun -lN1 --environment=alpine_workaround.toml echo "abc"
abc
```

Notice the section `[annotations]` disabling Slurm and CXI hooks.

### Using NCCL from remote SSH terminals

We are aware of an issue when enabling both [the AWS OFI NCCL hook][ref-ce-aws-ofi-hook] and [the SSH hook][ref-ce-ssh-hook], and launching programs using NCCL from Bash sessions connected via SSH.
The issue manifests with messages reporting `Error: network 'AWS Libfabric' not found`.

In addition to setting up a server for remote connections, the SSH hook also performs actions intended to improve the user experience. One of these is creating a script to be loaded by Bash in order to propagate the container job environment variables when connecting through SSH.
The script is translating the value of the `NCCL_NET` variable as `"'AWS Libfabric'"`, that is with additional quotes compared to the original value set by the AWS OFI NCCL hook. The quoted string induces NCCL to look for a network which is not defined, resulting in the unrecoverable error mentioned earlier.

As a workaround, resetting the NCCL_NET variable to the correct value is effective in allowing NCCL to use the AWS OFI plugin and access the Slingshot network, e.g. `export NCCL_NET="AWS Libfabric"`.

### Mounting home directories when using the SSH hook

Mounting individual home directories (usually located on the `/users` filesystem) overrides the files created by the SSH hook in `${HOME}/.ssh`, including the one which includes the authorized key entered in the EDF through the corresponding annotation. In other words, when using the SSH hook and bind mounting the user's own home folder or the whole `/users`, it is necessary to authorize manually the desired key.

It is generally NOT recommended to mount home folders inside containers, due to the risk of exposing personal data to programs inside the container.
Defining a mount related to `/users` in the EDF should only be done when there is a specific reason to do so, and the container image being deployed is trusted.
