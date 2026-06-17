[](){#ref-ce-annotations}
## Annotations

Annotations define arbitrary metadata for containers in the form of key-value pairs.
Within the EDF, annotations are designed to be similar in appearance and behavior to those defined by the [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec/blob/main/config.md#annotations).
Annotation keys usually express a hierarchical namespace structure, with domains separated by "." (full stop) characters.

As annotations are often used to control hooks, they have a deep nesting level.
For example, to execute the [SSH hook][ref-ce-ssh-hook] described below, the annotation `com.hooks.ssh.enabled` must be set to the string `true`.

EDF files support setting annotations through the `annotations` table.
This can be done in multiple ways in TOML: for example, both of the following usages are equivalent:

!!! example "TOML nest levels"
    * In the TOML key
    ```toml
    [annotations]
    com.hooks.ssh.enabled = "true"
    ```

    * In the TOML table name
    ```toml
    [annotations.com.hooks.ssh]
    enabled = "true"
    ```

??? note "Relevant details of the TOML format"
     * All property assignments belong to the section immediately preceding them (the statement in square brackets), which defines the table they refer to.

     * Tables, on the other hand, do not automatically belong to the tables declared before them; to nest tables, their name has to list their parents using the dot notations (so the previous example defines the table `ssh` inside `hooks`, which in turn is inside `com`, which is inside `annotations`).

     * An assignment can implicitly define subtables if the key you assign is a dotted list. As a reference, see the examples made earlier in this section, where assigning a string to the `com.hooks.ssh.enabled` attribute within the `[annotations]` table is exactly equivalent to assigning to the `enabled` attribute within the `[annotations.com.hooks.ssh]` subtable.

     * Attributes can be added to a table only in one place in the TOML file. In other words, each table must be defined in a single square bracket section. For example, in the invalid example below, the `ssh` table was doubly defined both in the `[annotations]` and in the `[annotations.com.hooks.ssh]` sections. See the [TOML format](https://toml.io/en/) spec for more details.

        ```toml title="Valid"
        [annotations.com.hooks.ssh]
        authorize_ssh_key = "${SCRATCH}/tests/edf/authorized_keys"
        enabled = "true"
        ```

        ```toml title="Valid"
        [annotations]
        com.hooks.ssh.authorize_ssh_key = "${SCRATCH}/tests/edf/authorized_keys"
        com.hooks.ssh.enabled = "true"
        ```

        ```toml title="Invalid"
        [annotations]
        com.hooks.ssh.authorize_ssh_key = "${SCRATCH}/tests/edf/authorized_keys"

        [annotations.com.hooks.ssh]
        enabled = "true"
        ```

[](){#ref-ce-container-hooks}
## Container Hooks

Container hooks let you customize container behavior to fit system-specific needs, making them especially valuable for High-Performance Computing.

 * *What they do*: Hooks extend container runtime functionality by enabling custom actions during a container's life cycle.
 * *Use for HPC*: HPC systems rely on specialized hardware and fine-tuned software, unlike generic containers. Hooks bridge this gap by allowing containers to access these system-specific resources or enable custom features.

!!! info
    This section outlines all hooks supported in production by the Container Engine.
    However, specific Alps vClusters may support only a subset or use custom configurations.
    For details about available features in individual vClusters, consult platform documentation or contact CSCS support.

!!! note
    In the examples below, EDF files are assumed to be at `${EDF_PATH}`.

[](){#ref-ce-cxi-hook}
### HPE Slingshot interconnect 

```toml
com.hooks.cxi.enabled = "true"
```

The Container Engine provides a hook to allow containers relying on [libfabric](https://ofiwg.github.io/libfabric/) to leverage the HPE Slingshot 11 high-speed interconnect.
This component is commonly referred to as the "CXI hook", taking its name from the CXI libfabric provider required to interface with Slingshot 11.
The hook leverages bind-mounting the custom host libfabric library into the container (in addition to all the required dependency libraries and devices as well).

If a libfabric library is already present in the container filesystem (for example, it's provided by the image), it is replaced with its host counterpart, otherwise the host libfabric is just added to the container.

The hook is activated by setting the `com.hooks.cxi.enabled` annotation, which can be defined in the EDF.

!!! tip
    On most vClusters, the CXI hook for Slingshot connectivity is enabled implicitly by default or by other hooks.
    Therefore, entering the enabling annotation in the EDF is unnecessary in many cases.

!!! note
    * Due to the nature of Slingshot and the mechanism implemented by the CXI hook, container applications need to use a communication library which supports libfabric in order to benefit from usage of the hook.
    * Libfabric support might have to be defined at compilation time (as is the case for some MPI implementations, like MPICH and OpenMPI) or could be dynamically available at runtime (as is the case with NCCL - see also [this][ref-ce-aws-ofi-hook] section for more details).

??? example "Comparison between with and without the CXI hook"
    * Without the CXI hook

    ```toml title="EDF: osu-mb-wo-cxi.toml"
    image = "quay.io#madeeks/osu-mb:6.2-mpich4.1-ubuntu22.04-arm64"

    [annotations]
    com.hooks.cxi.enabled = "false"
    ```

    ```console title="Command-line"
    $ srun -N2 --mpi=pmi2 --environment=osu-mb-wo-cxi ./osu_bw
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

    ```toml title="EDF: osu-mb-cxi.toml"
    image = "quay.io#madeeks/osu-mb:6.2-mpich4.1-ubuntu22.04"

    [annotations]
    com.hooks.cxi.enabled = "true"
    ```

    ```console title="Command-line"
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

!!! tip "How to check the CXI provider works inside a container"

    You might want to check if the CXI provider works inside a container,
    i.e. that the CXI hook has been correctly applied.

    You can check if the CXI provider is working using `fi_info`,
    usually available alongside your `libfabric` installation,
    within the container:

    ```bash
    fi_info -p cxi
    ```

    ??? example "CXI provider is working"
        ```console
        $ fi_info -p cxi
        provider: cxi
            fabric: cxi
            domain: cxi0
            version: 0.1
            type: FI_EP_RDM
            protocol: FI_PROTO_CXI
        ```

    ??? example "CXI provider not working"
        ```console
        $ fi_info -p cxi
        fi_getinfo: -61 (No data available)
        ```

[](){#ref-ce-aws-ofi-hook}
### AWS OFI NCCL hook 

```toml
com.hooks.aws_ofi_nccl.enabled = "true"
com.hooks.aws_ofi_nccl.variant = "cuda-dl"   # (1)!
```

1. `com.hooks.aws_ofi_nccl.variant` may vary depending on vClusters. Details below.

The [AWS OFI NCCL plugin](https://github.com/aws/aws-ofi-nccl) is a software extension that allows the [NCCL](https://developer.nvidia.com/nccl) and [RCCL](https://rocm.docs.amd.com/projects/rccl/en/latest/) libraries to use libfabric as a network provider and, through libfabric, to access the Slingshot high-speed interconnect.
Also see [NCCL][ref-communication-nccl] and [libfabric][ref-communication-libfabric] for more information on using the libraries on Alps.

The Container Engine includes a hook program to inject the AWS OFI NCCL plugin in containers; since the plugin must also be compatible with the GPU programming software stack being used, the `com.hooks.aws_ofi_nccl.variant` annotation is used to specify a plugin variant suitable for a given container image.
At the moment of writing, the following plugin variants are configured:
* For NVIDIA GPU nodes: `cuda12`, `cuda13`, `cuda-dl`.
  The `cuda-dl` variant uses a plugin which is dynamically linked to CUDA, therefore being portable across versions, and is the generally recommended choice. Some issues may arise with old container images which don't provide generic symlinks to the CUDA Runtime (more details [here][ref-known-issue-dynamic-aws-nccl-plugin]).
  The numbered variants are statically linked against a specific CUDA version and must be matched exactly with containers providing a corresponding CUDA installation.
* For AMD GPU nodes, alongside RCCL: `rocm5`, and `rocm6`.
  Both these variants are statically linked to specific ROCm versions.


!!! tip
    The hook implicitly enables the [CXI hook][ref-ce-cxi-hook], therefore exposing the Slingshot interconnect to container applications. In other words, when enabling the AWS OFI NCCL hook, it's unnecessary to also enable the CXI hook separately in the EDF.

!!! note
    The hook sets environment variables to control the behavior of NCCL and the libfabric CXI provider for Slingshot, helping prevent application stalls and improving performance, especially when using GPUDirect for RDMA communication.

!!! example "EDF for the NGC PyTorch 25.11 image with CUDA 13.1"
    ```toml
    image = "nvcr.io/nvidia/pytorch:25.11-py3"
    mounts = ["/capstor/scratch/cscs/${USER}:/capstor/scratch/cscs/${USER}"]

    [annotations]
    com.hooks.aws_ofi_nccl.enabled = "true"
    com.hooks.aws_ofi_nccl.variant = "cuda-dl"
    ```

[](){#ref-ce-ssh-hook}
### SSH hook

```toml
com.hooks.ssh.enabled = "true"
com.hooks.ssh.authorize_ssh_key = "<public-key>"    # (1)!
```

1. Replace `<public-key>` with the path to your SSH public key file.

The SSH hook runs a lightweight, statically-linked SSH server (a build of [Dropbear](https://matt.ucc.asn.au/dropbear/dropbear.html)) inside the container.
While the container is running, it's possible to connect to it from a remote host using a private key matching the public one authorized in the EDF annotation.
It can be useful to add SSH connectivity to containers (for example, enabling remote debugging) without bundling an SSH server into the container image or creating ad-hoc image variants for such purposes.

The `com.hooks.ssh.authorize_ssh_key` annotation allows the authorization of a custom public SSH key for remote connections.
The annotation value must be the absolute path to a *text file* containing the public key (just the public key without any extra signature/certificate).
The annotation value should not be the public SSH key itself.
After the container starts, it is possible to get a remote shell inside the container by connecting with SSH to the listening port.

By default, the server started by the SSH hook listens to port 15263, but this setting can be controlled through the `com.hooks.ssh.port` annotation in the EDF.

!!! warning 
    The `srun` command launching an SSH-connectable container **should set the `--pty` option** in order for the hook to initialize properly.

!!! note
    The container must be **writable** (default) to use the SSH hook.

!!! info
    In order to establish connections through Visual Studio Code [Remote - SSH](https://code.visualstudio.com/docs/remote/ssh) extension, the `scp` program must be available inside the container.
    This is required to send and establish the VS Code Server into the remote container.

!!! example "Logging into a sleeping container via SSH"
    * On the cluster
    ```toml title="EDF: ubuntu-ssh.toml"
    image = "ubuntu:latest"

    [annotations]
    com.hooks.ssh.enabled = "true"
    com.hooks.ssh.authorize_ssh_key = "<public-key>"
    ```
    ```console title="Command-line"
    $ srun --environment=ubuntu-ssh --pty sleep 30
    ```

    * On the remote shell
    ```console
    $ ssh -p 15263 <host-of-container>
    ```

### NVIDIA CUDA MPS hook

```toml
com.hooks.nvidia_cuda_mps.enabled = "true"
```

On several Alps vClusters, NVIDIA GPUs by default operate in "Exclusive process" mode, that is, the CUDA driver is configured to allow only one process at a time to use a given GPU.
For example, on a node with 4 GPUs, a maximum of 4 CUDA processes can run at the same time.

In order to run multiple processes concurrently on the same GPU (one example could be running multiple MPI ranks on the same device), the [NVIDIA CUDA Multi-Process Service](https://docs.nvidia.com/deploy/mps/index.html) (or MPS, for short) must be started on the compute node.

The Container Engine provides a hook to automatically manage the setup and removal of the NVIDIA CUDA MPS components within containers.
The hook can be activated by setting the `com.hooks.nvidia_cuda_mps.enabled` to the string `true`.

!!! tip 
    When using the NVIDIA CUDA MPS hook it is not necessary to use other wrappers or scripts to manage the Multi-Process Service, as is documented for native jobs on some vClusters.

!!! note
    The container must be **writable** (default) to use the CUDA MPS hook.

!!! example "Using the CUDA MPS hook"
    ```toml title="EDF: vectoradd-cuda-mps.toml"
    image = "nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda12.5.0-ubuntu22.04"

    [annotations]
    com.hooks.nvidia_cuda_mps.enabled = "true"
    ```

    ```console title="Command-line"
    $ srun -t2 -N1 -n8 --environment=vectoradd-cuda-mps /cuda-samples/vectorAdd | grep "Test PASSED" | wc -l
    8
    ```

??? example "Available GPUs and oversubscription error *without* the CUDA MPS hook"
    ```toml title="EDF: vectoradd-cuda.toml"
    image = "nvcr.io/nvidia/k8s/cuda-sample:vectoradd-cuda12.5.0-ubuntu22.04"   # (1)!
    ```

    1. This EDF uses the CUDA vector addition sample from NVIDIA's NGC catalog.

    ```console title="Command-line"
    $ nvidia-smi -L
    GPU 0: GH200 120GB (UUID: GPU-...)
    GPU 1: GH200 120GB (UUID: GPU-...)
    GPU 2: GH200 120GB (UUID: GPU-...)
    GPU 3: GH200 120GB (UUID: GPU-...)

    $ srun -t2 -N1 -n4 --environment=vectoradd-cuda /cuda-samples/vectorAdd | grep "Test PASSED"    # (1)!
    Test PASSED
    Test PASSED
    Test PASSED
    Test PASSED

    $ srun -t2 -N1 -n5 --environment=vectoradd-cuda /cuda-samples/vectorAdd | grep "Test PASSED"    # (2)!
    Failed to allocate device vector A (error code CUDA-capable device(s) is/are busy or unavailable)!
    srun: error: ...
    ```

    1. 4 processes run successfully.
    2. More than 4 concurrent processes result in oversubscription errors.


[](){#ref-ce-netstack-source}
### Selecting the network stack source

The [CXI hook][ref-ce-cxi-hook] and [AWS OFI NCCL hook][ref-ce-aws-ofi-hook] inject a set of specialized network libraries, extensions, and dependencies (more details [here][ref-software-communication]). These components allow containers to use the Alps Slingshot interconnect transparently and efficiently.

For convenience, we refer to one such interdependent set of networking-related software as a **network stack**, or *netstack* for short.

Container Engine hooks can obtain the network stack from different sources. Use the `com.hooks.netstack.source` annotation to select the source, e.g.:

```toml
com.hooks.netstack.source = "artifact"
```

The following values are currently supported:

* `host`: use the native libraries installed on the host system.
* `artifact`: use a **network stack artifact**, a standalone netstack built specifically for mounting inside containers and minimizing compatibility issues.

Host libraries are provided by the system vendor and match a specific system configuration. Injecting them requires overriding all corresponding libraries inside the container, which can cause compatibility issues. Host libraries are also tied to vendor-defined settings, and their available versions and update frequency depend on several factors.

Network stack artifacts are built independently by CSCS staff for use with containers on Alps. They reduce compatibility issues by searching for their dependencies in a separate directory, configured through `rpath` at build time. This leaves most container libraries unchanged. Artifacts are available in multiple [versions and variants][ref-ce-netstack-artifacts], and they are not tied to operating-system changes, while remaining tuned for Slingshot performance.

!!! info

    Default network stack sources are already configured for all vClusters.
    The `com.hooks.netstack.source` annotation is optional and is only needed to override the vCluster default.

    At the time of writing, the Clariden and Daint vClusters use `artifact` as the default source.
    All other vClusters use `host`.

!!! note

    When using network stack artifacts, the `com.hooks.aws_ofi_nccl.variant` annotation is ignored because all artifacts use dynamically linked AWS OFI NCCL plugins.

!!! warning "Artifact availability"

    Network stack artifacts are currently fully tested and supported only on GH200 vClusters connected to the [Capstor Store][ref-alps-capstor-store] filesystem.
    Availability will be expanded progressively.


[](){#ref-ce-netstack-artifacts}
### Selecting network stack artifacts

Network stack artifacts are organized by **version** and **named variant**:

- A **version** identifies a release of the network stack. It determines the combination of versions used for key connectivity components, such as libfabric and the AWS OFI NCCL plugin.
- Within each version, a **named variant** identifies a build intended for a particular combination of underlying platform components, such as CUDA or the Slingshot user-space software.

The version selects a release of the network stack. The named variant makes it possible to choose a build compatible with the relevant container software and host drivers.

Specific artifacts can be selected by version and name using the following EDF annotations:

```toml
com.hooks.netstack.version = "latest"
com.hooks.netstack.name = "default"
```

!!! tip

    Default values for the network stack version and name are already configured for all vClusters.
    The corresponding annotations are optional and only needed to customize the artifact choice.


??? example "Network stack artifacts installations in more detail"

    At the time of writing, network stack artifacts are installed using the following directory structure: `<base path>/<architecture>/<version>/<name>`

    On Alps vClusters connected to Capstor, the base path is currently `/capstor/store/cscs/cscs/public/containers/netstack/`.

    Architecture directories use the values reported by `uname -m`, such as `aarch64` or `x86_64`.

    For example, on a GH200 vCluster, the installed versions can be listed as follows:

    ```console
    $ ls -l /capstor/store/cscs/cscs/public/containers/netstack/aarch64/
    total 8
    drwxrwsr-x+ 6 gwalee csstaff 4096 May  6 12:42 26.02.1
    drwxrwsr-x+ 5 gwalee csstaff 4096 May  5 17:01 26.05.1
    lrwxrwxrwx  1 gwalee csstaff    8 May  6 12:35 latest -> 26.05.1/
    ```

    The named variants available within a given version directory can be listed as follows:

    ```console
    $ ls -l /capstor/store/cscs/cscs/public/containers/netstack/aarch64/26.05.1
    total 12
    lrwxrwxrwx  1 gwalee csstaff   46 May  4 15:11 default -> gpu:cuda13,cxi:12.0.1,ofi:2.5.1,aws:1.18.0+dl/
    drwxr-sr-x+ 2 gwalee csstaff 4096 May  4 10:43 gpu:cuda13,cxi:12.0.1,ofi:2.5.1,aws:1.18.0+dl
    drwxr-sr-x+ 2 gwalee csstaff 4096 May  4 10:42 gpu:cuda13,cxi:13.1.0,ofi:2.5.1,aws:1.18.0+dl
    drwxr-sr-x+ 2 gwalee csstaff 4096 May  4 10:43 gpu:cuda13,cxi:14.0.0,ofi:2.5.1,aws:1.18.0+dl
    lrwxrwxrwx  1 gwalee csstaff   45 May  5 17:01 shs:12.0.1 -> gpu:cuda13,cxi:12.0.1,ofi:2.5.1,aws:1.18.0+dl
    lrwxrwxrwx  1 gwalee csstaff   45 May  5 17:01 shs:13.1.0 -> gpu:cuda13,cxi:13.1.0,ofi:2.5.1,aws:1.18.0+dl
    lrwxrwxrwx  1 gwalee csstaff   45 May  5 17:01 shs:14.0.0 -> gpu:cuda13,cxi:14.0.0,ofi:2.5.1,aws:1.18.0+dl
    ```

    ??? example "Listing the full contents of a netstack artifact"

        ```console
        $ ls -l /capstor/store/cscs/cscs/public/containers/netstack/aarch64/26.05.1/shs:13.1.0/
        total 25444
        -rwxr-xr-x+ 1 gwalee csstaff  197960 May  4 10:43 libbrotlicommon.so.1
        -rwxr-xr-x+ 1 gwalee csstaff   66984 May  4 10:43 libbrotlidec.so.1
        -rwxr-xr-x+ 1 gwalee csstaff   66992 May  4 10:43 libcom_err.so.2
        -rwxr-xr-x+ 1 gwalee csstaff 4283944 May  4 10:43 libcrypto.so.3
        -rwxr-xr-x+ 1 gwalee csstaff 1754432 May  4 10:43 libc.so.6
        -rwxr-xr-x+ 1 gwalee csstaff  666776 May  4 10:43 libcurl.so.4
        -rwxr-xr-x+ 1 gwalee csstaff  396656 May  4 10:43 libcxi.so.1
        -rwxr-xr-x+ 1 gwalee csstaff 2036112 May  4 10:43 libfabric.so.1
        -rwxr-xr-x+ 1 gwalee csstaff   67744 May  4 10:43 libffi.so.8
        -rwxr-xr-x+ 1 gwalee csstaff  135112 May  4 10:43 libgcc_s.so.1
        -rwxr-xr-x+ 1 gwalee csstaff  540712 May  4 10:43 libgmp.so.10
        -rwxr-xr-x+ 1 gwalee csstaff 2157896 May  4 10:43 libgnutls.so.30
        -rwxr-xr-x+ 1 gwalee csstaff  339400 May  4 10:43 libgssapi_krb5.so.2
        -rwxr-xr-x+ 1 gwalee csstaff  339832 May  4 10:43 libhogweed.so.6
        -rwxr-xr-x+ 1 gwalee csstaff  402304 May  4 10:43 libhwloc.so.15
        -rwxr-xr-x+ 1 gwalee csstaff  132856 May  4 10:43 libidn2.so.0
        -rwxr-xr-x+ 1 gwalee csstaff  136496 May  4 10:43 libjson-c.so.5
        -rwxr-xr-x+ 1 gwalee csstaff  201040 May  4 10:43 libk5crypto.so.3
        -rwxr-xr-x+ 1 gwalee csstaff   67880 May  4 10:43 libkeyutils.so.1
        -rwxr-xr-x+ 1 gwalee csstaff  876960 May  4 10:43 libkrb5.so.3
        -rwxr-xr-x+ 1 gwalee csstaff   69776 May  4 10:43 libkrb5support.so.0
        -rwxr-xr-x+ 1 gwalee csstaff   69784 May  4 10:43 liblber-2.5.so.0
        -rwxr-xr-x+ 1 gwalee csstaff  415240 May  4 10:43 libldap-2.5.so.0
        -rwxr-xr-x+ 1 gwalee csstaff  609784 May  4 10:43 libm.so.6
        -rwxr-xr-x+ 1 gwalee csstaff  530152 May  4 10:43 libnccl-net.so
        -rwxr-xr-x+ 1 gwalee csstaff  343760 May  4 10:43 libnettle.so.8
        -rwxr-xr-x+ 1 gwalee csstaff  204168 May  4 10:43 libnghttp2.so.14
        -rwxr-xr-x+ 1 gwalee csstaff  206136 May  4 10:43 libnl-3.so.200
        -rwxr-xr-x+ 1 gwalee csstaff 1316064 May  4 10:43 libp11-kit.so.0
        -rwxr-xr-x+ 1 gwalee csstaff  132792 May  4 10:43 libpsl.so.5
        -rwxr-xr-x+ 1 gwalee csstaff   68760 May  4 10:43 libresolv.so.2
        -rwxr-xr-x+ 1 gwalee csstaff  136232 May  4 10:43 librtmp.so.1
        -rwxr-xr-x+ 1 gwalee csstaff  134224 May  4 10:43 libsasl2.so.2
        -rwxr-xr-x+ 1 gwalee csstaff  477248 May  4 10:43 libssh.so.4
        -rwxr-xr-x+ 1 gwalee csstaff  680960 May  4 10:43 libssl.so.3
        -rwxr-xr-x+ 1 gwalee csstaff 2567464 May  4 10:43 libstdc++.so.6
        -rwxr-xr-x+ 1 gwalee csstaff  133344 May  4 10:43 libtasn1.so.6
        -rwxr-xr-x+ 1 gwalee csstaff  201968 May  4 10:43 libudev.so.1
        -rwxr-xr-x+ 1 gwalee csstaff 1790736 May  4 10:43 libunistring.so.2
        -rwxr-xr-x+ 1 gwalee csstaff   67048 May  4 10:43 libxpmem.so.0
        -rwxr-xr-x+ 1 gwalee csstaff  134016 May  4 10:43 libz.so.1
        -rwxr-xr-x+ 1 gwalee csstaff  805792 May  4 10:43 libzstd.so.1
        -rw-r--r--+ 1 gwalee csstaff    3435 May  4 10:42 ORIGIN
        ```

    Within installation trees, symlinks are provided for convenience in selecting the latest version or the most commonly recommended variant.

    Variant names and symbolic links may change in the future. When selecting a specific artifact, please refer to the versions and variants available in the installation tree.


## Accessing NVIDIA GPUs

The Container Engine leverages components from the NVIDIA Container Toolkit to expose NVIDIA GPU devices inside containers.
GPU device files are always mounted in containers, and the NVIDIA driver user space components are mounted if the `NVIDIA_VISIBLE_DEVICES` environment variable is not empty, unset or set to `void`.
`NVIDIA_VISIBLE_DEVICES` is already set in container images officially provided by NVIDIA to enable all GPUs available on the host system.
Such images are frequently used to containerize CUDA applications, either directly or as a base for custom images, thus in many cases no action is required to access GPUs.

!!! example "Cluster with 4 GH200 devices per node"
    ```toml title="EDF: cuda12.5.1.toml"
    image = "nvidia/cuda:12.5.1-devel-ubuntu24.04"
    ```

    ```console title="Command-line"
    $ srun --environment=cuda12.5.1 nvidia-smi
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

It is possible to use environment variables to control which capabilities of the NVIDIA driver are enabled inside containers.
Additionally, the NVIDIA Container Toolkit can enforce specific constraints for the container, for example, on versions of the CUDA runtime or driver, or on the architecture of the GPUs.
For the full details about using these features, please refer to the official documentation: [Driver Capabilities](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html#driver-capabilities), [Constraints](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html#constraints).
