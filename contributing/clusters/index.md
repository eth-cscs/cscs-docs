# Updating cluster descriptions

The tables of partitions, nodes, file systems and tool versions on the cluster and platform pages are generated from the configuration of each cluster, by the script `probes/probe.sh`. This page is for platform owners and system administrators who update them after a change to a cluster.

## Quick start

On a login node of the cluster:

update the tables of a cluster

```bash
git clone git@github.com:<your-username>/cscs-docs.git
cd cscs-docs
git switch -c update-<cluster>
./probes/probe.sh --generate
git diff generated/clusters/
```

Check that every change in the diff is one that you expect, then commit, push, and open a pull request as described in the [contributing guide](<https://docs.cscs.ch/contributing/index.md#contributing> "Contributing").

Update the tables:

- after a maintenance, or any other change to `slurm.conf`, the QoS limits or the file systems;
- when the monthly check in CI reports the cluster as overdue (tables more than 30 days old) or stale (more than 60 days).

> [!WARNING]
>
> **Do not edit the generated files**
>
> The files in `generated/` are overwritten by the next update, and CI fails if a table does not match the `results.json` next to it. To change what a table shows, change the configuration of the cluster. To explain something, edit the cluster page in `docs/clusters/`.

## What the script does

The script works out which cluster it is on, and writes to `generated/clusters/<cluster>/`:

- one markdown table for each probe, such as `partitions.md` and `nodes.md`, which the pages include;
- `results.json`, which holds everything that the probes found, and is also published for agents.

It reads the configuration that was deployed: the partitions and nodes from `slurm.conf`, the QoS limits from `sacctmgr`, the file systems, and the versions of Slurm, uenv and the container engine. It changes nothing on the system, and submits no jobs.

If nothing changed on the cluster, the diff only changes the date in `results.json`. Any other difference is a change on the cluster, for example a new time limit, or nodes that moved to another cluster.

> [!NOTE]
>
> An unexpected difference may be a mistake in the configuration. Errors in Slurm configuration do happen, e.g. as the result of cut and paste, so it is important to follow up.

> [!NOTE]
>
> **Temporary changes are not shown**
>
> A change made on the running system with `scontrol update`, such as a shorter time limit during an incident, is not in `slurm.conf`, so the tables do not show it. If users need to know about such a change, describe it in an admonition on the cluster page.

## Clusters that share a platform page

The storage table of a platform page, such as [HPCP](<https://docs.cscs.ch/platforms/hpcp/index.md#hpc-platform> "HPC Platform"), is the `filesystems.md` of one reference cluster of the platform, for example Daint for HPCP. CI checks that the other clusters of the platform, such as Eiger, produce the same table. The reference cluster of each platform, and whether a difference fails the check or only warns, are set in `probes/platforms.json`.

- Updating a reference cluster also updates its platform page.
- If the storage of a whole platform changes, update all its clusters in the same pull request.
- If the check fails, either a cluster is configured by mistake, or its storage really differs from the rest of the platform. In the second case, [contact the documentation maintainers](<https://docs.cscs.ch/index.md#get-in-touch> "Get in Touch"): the table then belongs on the cluster pages instead.

To run the check before opening the pull request:

check that the clusters of each platform agree

```bash
./probes/check-platforms.sh
```

## Adding a cluster

Run the script on the new cluster as above, then include its tables in the cluster page, as the other cluster pages do:

include the node table of a cluster

```text
--8<-- "generated/clusters/<cluster>/nodes.md"
```

The tables that are available, and how they are made, are described in [`probes/README.md`](<https://github.com/eth-cscs/cscs-docs/blob/main/probes/README.md>).

## Known issues

The script stops, rather than guess, when it finds something that it does not recognise. If the cause is a mistake in the configuration, fix the configuration and run the script again. Otherwise, [contact the documentation maintainers](<https://docs.cscs.ch/index.md#get-in-touch> "Get in Touch"), who will add what is missing to the script.

> [!WARNING]
>
> **`is not a known Alps node type`**
>
> A node has a number of cores per socket and GPUs that matches none of the [Alps node types](<https://docs.cscs.ch/alps/hardware/index.md#alps-hardware> "Alps Hardware"). Either the node is configured with the wrong values, or it is new hardware that the script does not know yet.

> [!WARNING]
>
> **`more than any documented configuration of`**
>
> A node is configured with more memory than any documented memory configuration of its node type. This is usually a mistake in the `RealMemory` of the node in `slurm.conf`.

> [!WARNING]
>
> **`which sacctmgr does not report`**
>
> A partition in `slurm.conf` uses a QoS that is not defined in the Slurm database. Create the QoS, or remove it from the partition.

> [!WARNING]
>
> **`is on unrecognised mount`**
>
> A file system, such as `$SCRATCH`, is mounted from storage that the script does not know. This is expected when a cluster moves to new storage: contact the documentation maintainers.
