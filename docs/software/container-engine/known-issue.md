## Slow or failing connection to Ubuntu package repositories
We are aware that the main repository for the Ubuntu package manager at http://ports.ubuntu.com/ubuntu-ports/ is slow or unresponsive towards CSCS.

A temporary solution is to use a CSCS local repo that works as a proxy for Ubuntu packages; it is much faster but needs a small workaround to the build process.
Basically, the `apt` package manager should be configured to use the CSCS local repository instead of the default one to resolve the packages.

This can be achieved by first creating specific configuration files. Below we provide examples for recent Ubuntu LTS releases:

- **For Ubuntu 22.04 Jammy:**
  ```console
  $ cat > ./workaround/ubuntu.sources << 'EOF'
  Types: deb
  URIs: https://jfrog.svc.cscs.ch/artifactory/ubuntu-ports/
  Suites: jammy jammy-updates jammy-backports
  Components: main universe restricted multiverse
  Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

  ## Ubuntu security updates. Aside from URIs and Suites,
  ## this should mirror your choices in the previous section.
  Types: deb
  URIs: https://jfrog.svc.cscs.ch/artifactory/ubuntu-ports/
  Suites: jammy-security
  Components: main universe restricted multiverse
  Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
  EOF

  $ cat > ./workaround/99-jfrog-proxy << 'EOF'
  Acquire::http::AllowRedirect "true";
  Acquire::http::Pipeline-Depth "0";
  EOF
  ```

- **For Ubuntu 24.04 Noble:**
  ```console
  $ cat ./workaround/ubuntu.sources << 'EOF'
  ## See the sources.list(5) manual page for further settings.
  Types: deb
  URIs: https://jfrog.svc.cscs.ch/artifactory/ubuntu-ports/
  Suites: noble noble-updates noble-backports
  Components: main universe restricted multiverse
  Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

  ## Ubuntu security updates. Aside from URIs and Suites,
  ## this should mirror your choices in the previous section.
  Types: deb
  URIs: https://jfrog.svc.cscs.ch/artifactory/ubuntu-ports/
  Suites: noble-security
  Components: main universe restricted multiverse
  Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
  EOF

  $ cat > ./workaround/99-jfrog-proxy  << 'EOF'
  Acquire::http::AllowRedirect "true";
  Acquire::http::Pipeline-Depth "0";
  EOF
  ```

These files can then be used in the `podman build` command through bind mounts, e.g.:

```console
$ podman build \
  -v "$PWD/workaround/ubuntu.sources:/etc/apt/sources.list.d/ubuntu.sources:ro,z" \
  -v "$PWD/workaround/99-jfrog-proxy:/etc/apt/apt.conf.d/99-jfrog-proxy:ro,z" \
  -t test-build .
```

What this approach is doing is setting up `apt` with:

**sources.list.d/ubuntu.sources**: Tells `apt` to use the internal CSCS JFrog mirror.
**99-jfrog-proxy**: Connection configurations.

Passing these configurations as bind mounts has the advantage that no modifications to the  Containerfile are needed.

We verified that the above workaround works for NGC images like PyTorch 24.01.

## Compatibility with Alpine Linux

Alpine Linux is incompatible with some hooks, causing errors when used with Slurm. For example,

```toml title="EDF: alpine.toml"
image = "alpine:3.19"
```

```console title="Command-line"
$ srun -lN1 --environment=alpine echo "abc"
0: slurmstepd: error: pyxis: container start failed with error code: 1
0: slurmstepd: error: pyxis: printing enroot log file:
0: slurmstepd: error: pyxis:     [ERROR] Failed to refresh the dynamic linker cache
0: slurmstepd: error: pyxis:     [ERROR] /etc/enroot/hooks.d/87-slurm.sh exited with return code 1
0: slurmstepd: error: pyxis: couldn't start container
0: slurmstepd: error: spank: required plugin spank_pyxis.so: task_init() failed with rc=-1
0: slurmstepd: error: Failed to invoke spank plugin stack
```

This is because some hooks (e.g., Slurm and CXI hooks) leverage `ldconfig` (from Glibc) when they bind-mount host libraries inside containers; since Alpine Linux provides an alternative `ldconfig` (from Musl Libc), it does not work as intended by hooks. As a workaround, users may disable problematic hooks. For example,

```toml title="EDF: alpine_workaround.toml"
image = "alpine:3.19"

[annotations]
com.hooks.cxi.enabled = "false"

[env]
ENROOT_SLURM_HOOK = "0"
```

```console title="Command-line"
$ srun -lN1 --environment=alpine_workaround echo "abc"
abc
```

Notice the section `[annotations]` disabling Slurm and CXI hooks.

## Using NCCL from remote SSH terminals

We are aware of an issue when enabling both [the AWS OFI NCCL hook][ref-ce-aws-ofi-hook] and [the SSH hook][ref-ce-ssh-hook], and launching programs using NCCL from Bash sessions connected via SSH.
The issue manifests with messages reporting `Error: network 'AWS Libfabric' not found`.

In addition to setting up a server for remote connections, the SSH hook also performs actions intended to improve the user experience. One of these is creating a script to be loaded by Bash in order to propagate the container job environment variables when connecting through SSH.
The script is translating the value of the `NCCL_NET` variable as `"'AWS Libfabric'"`, that is with additional quotes compared to the original value set by the AWS OFI NCCL hook. The quoted string induces NCCL to look for a network which is not defined, resulting in the unrecoverable error mentioned earlier.

As a workaround, resetting the NCCL_NET variable to the correct value is effective in allowing NCCL to use the AWS OFI plugin and access the Slingshot network, e.g. `export NCCL_NET="AWS Libfabric"`.

## Mounting home directories when using the SSH hook

Mounting individual home directories (usually located on the `/users` filesystem) overrides the files created by the SSH hook in `${HOME}/.ssh`, including the one which includes the authorized key entered in the EDF through the corresponding annotation. In other words, when using the SSH hook and bind mounting the user's own home folder or the whole `/users`, it is necessary to authorize manually the desired key.

It is generally NOT recommended to mount home folders inside containers, due to the risk of exposing personal data to programs inside the container.
Defining a mount related to `/users` in the EDF should only be done when there is a specific reason to do so, and the container image being deployed is trusted.

[](){#ref-ce-why-no-sbatch-env}
## Why `--environment` as `#SBATCH` is discouraged

The use of `--environment` as `#SBATCH` is known to cause **unexpected behaviors** and is exclusively reserved for highly customized workflows. This is because `--environment` as `#SBATCH` puts the entire SBATCH script in a container from the EDF file. The following are a few known associated issues.

 - **Slurm availability in a container**: Either Slurm components are not completely injected inside a container, or injected Slurm components do not function properly.

 - **Non-host execution context**: Since the SBATCH script runs inside a container, most host resources are inaccessible by default unless EDF explicitly exposes them. Affected resources include: filesystems, devices, system resources, container hooks, etc.

 - **Nested use of `--environment`**: running `srun --environment` in `#SBATCH --environment` results in double-entering EDF containers, causing unexpected errors in the underlying container runtime.

To avoid any unexpected confusion, users are advised **not** to use `--environment` as `#SBATCH`. If users encounter a problem while using this, it's recommended to move `--environment` from `#SBATCH` to each `srun` and see if the problem disappears.

[](){#ref-ce-no-user-id}
## Container start fails with `id: cannot find name for user ID`

If your slurm job using a container fails to start with an error message similar to:
```console
slurmstepd: error: pyxis: container start failed with error code: 1
slurmstepd: error: pyxis: container exited too soon
slurmstepd: error: pyxis: printing engine log file:
slurmstepd: error: pyxis:     id: cannot find name for user ID 42
slurmstepd: error: pyxis:     id: cannot find name for user ID 42
slurmstepd: error: pyxis:     id: cannot find name for user ID 42
slurmstepd: error: pyxis:     mkdir: cannot create directory ‘/iopsstor/scratch/cscs/42’: Permission denied
slurmstepd: error: pyxis: couldn't start container
slurmstepd: error: spank: required plugin spank_pyxis.so: task_init() failed with rc=-1
slurmstepd: error: Failed to invoke spank plugin stack
srun: error: nid001234: task 0: Exited with exit code 1
srun: Terminating StepId=12345.0
```
it does not indicate an issue with your container, but instead means that one or more of the compute nodes have user databases that are not fully synchronized.
If the problematic node is not automatically drained, please [let us know][ref-get-in-touch] so that we can ensure the node is in a good state.
You can check the state of a node using `sinfo --nodes=<node>`, e.g.:
```console
$ sinfo --nodes=nid006886
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
debug        up    1:30:00      0    n/a
normal*      up   12:00:00      1 drain$ nid006886
xfer         up 1-00:00:00      0    n/a
```

## Mismatching `PATH` between image build time and container runtime

With some container base images (e.g., [OpenSUSE Base Container Image](https://www.suse.com/products/base-container-images/)), the `PATH` environment variable at container runtime differs from its value at the end of image build time, usually resulting in missing software at runtime if they are built on top of the base image. This is because some base images overwrite `PATH` on container startup, regardless of whether it was updated during the container build. 

As a workaround, users may add a small entrypoint script at the end of their container build script (`Containerfile`) to update the runtime `PATH` to the build-time `PATH`. Notice that **the accompanying EDF file should enable the entrypoint** (`entrypoint = true`). 

```dockerfile
...
RUN { echo '#!/bin/bash' && \
      echo 'PATH='"$PATH"' exec "$@"'; } > /entry.sh && \
    chmod +x /entry.sh
ENTRYPOINT [ "/entry.sh" ]
CMD [ "/bin/bash" ]
```

Alternatively, users may also set an environment variable `ENROOT_LOGIN_SHELL` to `no` to work around this problem. Notice that the variable doesn't persist throughout different terminal sessions.

```console
$ export ENROOT_LOGIN_SHELL=no
```
