---
name: cscs-cluster-probes
description: Look up how a CSCS Alps cluster is configured and what it is doing now (Slurm partitions and their limits, QoS, node hardware and features, file systems, tool versions, idle nodes, pending jobs, and what the current user can submit to). Use when helping a user on a CSCS cluster choose a partition, write a job script, or understand why a job is pending or was rejected.
---

# CSCS cluster probes

`scripts/probe.sh`, in the directory that contains this file, reports facts about the cluster that it is run on.
It is read-only, submits no jobs, and takes about a second.
Prefer it to parsing `scontrol`, `sinfo` and `sacctmgr` yourself: it combines them, and states why a limit is what it is.

Always pass `--live --format json` on a cluster, and name the probes that you need.
In the examples, `$SKILL` is the directory that contains this file.

```console
$ $SKILL/scripts/probe.sh --live --format json partitions usage access
```

Run `$SKILL/scripts/probe.sh --list --format json` once for the meaning of every field.

If you are not on a cluster but can connect to one with ssh, copy the `scripts` directory there and run it in the same way.
The probe needs only Python 3.6 and the Slurm commands of the cluster.

## Which probe

| Question | Probe | Look at |
|---|---|---|
| Which partition should a job use, and what are its limits? | `partitions` | `nodes.usable`, `job_nodes.max`, `job_node_minutes.max`, `time` |
| Can this user submit to a partition, and with which account and QoS? | `access` | `partitions[].can_submit`, `reason`, `accounts`, `qos` |
| Why was a job rejected at submission? | `access`, `partitions` | `reason`; `job_nodes.max`, `job_node_minutes.max` and `time.max` against the request; `qos.<name>.deny_on_limit` |
| Why is a job pending? | `usage`, `partitions` | `jobs.pending_reasons`, `qos_nodes`, `nodes.limited_by` |
| Will a job start soon? | `usage` | `nodes.idle`, `qos_nodes.free`, `jobs.pending` |
| What hardware does a partition have, and which `--constraint` values exist? | `nodetypes` | `type`, `cpus`, `memory_gb`, `gres`, `features` |
| How many nodes of each type, and with how much memory, does the cluster have? | `nodes` | `type`, `installed_memory_gb`, `nodes`, `memory_gb` |
| Where should data go? | `filesystems` | `path`, `filesystem`, `storage` |
| Which version of Slurm, uenv or the container engine is installed? | `versions` | `tools[].version` |

## Reading the output

* `null` means no limit or not set, never zero.
* `partitions[].nodes.pool` is the number of nodes that a partition is configured on.
  Partitions share nodes, so it is not what the jobs of the partition can use: that is `nodes.usable`, and `nodes.limited_by` names the QoS limit that sets it.
* `partitions[].job_nodes.max` is the largest job that can run in the partition: the tightest of the partition `MaxNodes`, and the per-job (`MaxTRES`) and group (`GrpTRES`) node limits of its QoS.
  A job larger than that is rejected at submission only if the QoS that sets the limit has `deny_on_limit`; otherwise it is accepted and stays pending without end, for example with reason `QOSGrpNodeLimit`.
  The QoS that a job requests can lower the limit further: compare `qos.<name>.max_nodes_per_job`.
  `job_nodes.size_max` is the limit on job size alone, without the group limits; it is what the documentation tables show as *Max nodes/job*, next to the group limit as *Max nodes in use*.
* `partitions[].job_node_minutes.max` limits nodes times the time limit of one job (e.g. 90: 1 node for 90 minutes, or 2 nodes for 45).
* A partition has two kinds of QoS.
  `partition_qos` applies to every job in the partition and is not requested.
  `allowed_qos` lists the ones that a job can request with `--qos`; the limits of each are under `qos`.
* A pending job with reason `QOSGrpNodeLimit` is waiting for a QoS node limit, not for idle nodes.
  Compare `usage` `qos_nodes.in_use` with `limit`.
* `access` checks accounts, groups and QoS.
  It does not check whether the project has budget left.
* `usage` is a snapshot.
  Run it again rather than reusing an earlier answer.

## Intended and live

`--live` reports what the scheduler is using now.
`--intended` reports the configuration that the platform owners deployed, which is what the documentation at <https://docs.cscs.ch> shows.
If the two differ for a partition, the running system was changed temporarily: tell the user what applies now, and that it differs from the documentation.

```console
$ diff <($SKILL/scripts/probe.sh --live partitions) <($SKILL/scripts/probe.sh --intended partitions)
```

Without access to a cluster, read <https://docs.cscs.ch/generated/clusters/index.json> for the list of clusters, then <https://docs.cscs.ch/generated/clusters/CLUSTER/results.json>, with `CLUSTER` replaced by the cluster name.
It is the intended configuration of the published probes, in the same format, from the last time that the documentation was updated.
The `usage` and `access` probes are only available on a cluster.

## Not covered

Quota and how full a file system is, the remaining budget of a project, scratch cleanup and backup policies, and the intended purpose of each partition.
For policies, read the cluster and storage pages of the documentation.

## Updates

This skill is published by CSCS at <https://docs.cscs.ch/agents/>.
When the user asks to install or update the CSCS agent skills, follow the instructions on that page.
