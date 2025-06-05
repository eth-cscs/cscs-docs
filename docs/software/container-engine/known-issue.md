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
