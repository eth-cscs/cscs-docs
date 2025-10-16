## Buffer overflow errors with long command strings

We are aware of an issue, as of the system update on 10th September 2025, which is causing a buffer overflow error and abrupt termination of jobs using the CE when entering very long strings as the command to execute in the Slurm job step.

The issue presents itself with a error message similar to the following:

```bash
srun: error: nid001309: task 0: Aborted
*** buffer overflow detected ***: terminated
```

We have identified the nature of the problem and are working towards deploying a fix.


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
