---
name: cscs-alps
description: Orientation for the Alps clusters of CSCS, the Swiss National Supercomputing Centre (Daint, Eiger, Clariden, Santis, Bristen, Beverin). Read before running, building, installing or storing anything on them, where CPU architecture, file systems and software environments differ from a generic Linux or HPC system. Use when the host name is like daint-ln001 or nid001234, when paths start with /users, /capstor, /iopsstor or /ritom, or when the user mentions CSCS or Alps.
---

# Alps at CSCS

Alps is the HPC infrastructure of CSCS; each cluster on it is a shared HPC system with Slurm.
Your knowledge of Linux, Slurm, MPI and containers applies.
This file lists only where Alps differs from what you would expect.

Details are in the documentation at <https://docs.cscs.ch/>.
Read the HTML pages, not the `.md` copies listed in `llms.txt`: the copies lose many of their links.

## Where you are

* `cat /etc/xthostname` gives the cluster name.
* A host name like `daint-ln001` is a login node; one like `nid001234` is a compute node.
* Login nodes are shared, with limits on CPU time and memory.
  Builds, tests and anything compute or memory intensive go to a compute node with `srun` or `sbatch`: the [fair use policy](https://docs.cscs.ch/policies/shared/#ref-policies-fair-use-login-node) lets CSCS stop such processes on login nodes without warning.
* Jobs are billed to a project.
  If the `cscs-cluster-probes` skill is installed, use it for partitions, limits, accounts and why a job is pending.

| Cluster | Compute nodes | CPU architecture |
|---|---|---|
| Daint, Clariden, Santis | 4 NVIDIA GH200 per node | aarch64 (Grace) |
| Eiger | CPU only, AMD | x86-64 |
| Bristen | NVIDIA A100 | x86-64 |
| Beverin | AMD MI300A and MI250X | x86-64 |

Check `uname -m` where the code will run to determine the CPU architecture.

## File systems

All file systems are shared over the network and mounted on every node.
`$HOME` is the same on all clusters, so files installed there by one cluster are seen by clusters of a different architecture.

| Variable | Path | Type | Use |
|---|---|---|---|
| `$HOME` | `/users/$USER` | VAST, NFS | Source, scripts and configuration. Quota of 50 GB and **500,000 files**. |
| `$SCRATCH` | `/ritom/scratch/cscs/$USER` (Daint, Eiger), `/capstor/scratch/cscs/$USER` (Santis), `/iopsstor/scratch/cscs/$USER` (Clariden, Bristen) | VAST NFS on `/ritom`, Lustre on the others | Builds, environments and job input and output. No backup. |
| `$STORE` or `$PROJECT` | `/capstor/store/cscs/<customer>/<project>` | Lustre | Results and data shared by a project, with backup. Not for the I/O of jobs. |

* **Do not build software, or create Python virtual environments, conda environments or package caches, in `$HOME`.**
  They hold many files and use up the file quota of `$HOME`.
  Put them in `$SCRATCH`.
* Files in Scratch that are not accessed for 30 days (14 days on `/iopsstor`) are deleted.
  Do not touch files to keep them: move what must be kept to `$STORE`.
* Operations on metadata are slow on all of them: many small files, `pip install`, `import` from a large environment, compiling, and `find` or `ls -R` on large trees.
  Many processes doing them at once slow the file system down for every user.
  The memory file systems `/dev/shm` and `/tmp` on a node are much faster for many small files in a job.
* `quota` shows the use of each file system.

Read [File systems](https://docs.cscs.ch/storage/filesystems/) before deciding where data goes, and the [storage guide](https://docs.cscs.ch/guides/storage/) for Lustre striping, VAST settings for MPI-IO, and [Python environments as SquashFS images](https://docs.cscs.ch/guides/storage/#ref-guides-storage-venv).

## Software

There is no module tree on the system (`module avail` find nothing useful)
There is no use software installed on the system.
Software comes from one of:

* **uenv**, a CSCS tool that mounts a SquashFS image of software built with Spack, usually at `/user-environment`.
  * `uenv image find` lists the images available on the cluster; `uenv image pull <image>` downloads one.
  * `uenv run --view=default prgenv-gnu/25.6:v2 -- <command>` runs a command in it.
  * In jobs, use `srun --uenv=<image> --view=<view>`, or the same as `#SBATCH` options.
  * `uenv start` opens an interactive shell: do not use it in scripts or `~/.bashrc`.
  * The software is not visible until a view is loaded; `--view=modules` provides `module` commands.
  * Programming environments such as `prgenv-gnu` provide compilers, MPI and common libraries; applications such as GROMACS have their own images.
  * [Using uenv](https://docs.cscs.ch/software/uenv/using/), [programming environments](https://docs.cscs.ch/software/prgenv/).
  * To build a uenv, use the `build-uenv-stackinator` skill if it is installed.
* **The Container Engine**, a CSCS container runtime integrated with Slurm.
  * There is no Docker daemon, and podman is provided for buildig containers, not for running containers.
  * A container is described by an environment definition file (EDF), a TOML file in `~/.edf/`.
  * `srun --environment=<name> <command>` runs a command in it, on compute nodes.
  * Images are built with Podman and imported as SquashFS files.
  * Containers are recommended for PyTorch and most machine learning, starting from NVIDIA NGC images.
  * [Container Engine](https://docs.cscs.ch/software/container-engine/), [PyTorch](https://docs.cscs.ch/software/ml/pytorch/).

The [software catalogue](https://docs.cscs.ch/software/) lists the applications and tools that CSCS provides, and how to get each.

## Network

Login nodes reach the internet directly; compute nodes reach it through NAT.
The public addresses are shared by all users, so services like Docker Hub apply rate limits to all of them together: [internet access](https://docs.cscs.ch/guides/internet-access/).
