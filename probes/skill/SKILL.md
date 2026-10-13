---
name: cscs-cluster-probes
description: Look up how a CSCS Alps cluster is configured and what it is doing now (Slurm partitions and their limits, QoS, node hardware and features, file systems, tool versions, idle nodes, pending jobs, and what the current user can submit to). Use when helping a user on a CSCS cluster choose a partition, write a job script, or understand why a job is pending or was rejected.
---

# CSCS cluster probes

`probes/probe.sh` in a checkout of the CSCS documentation repository reports facts about the cluster that it is run on.
It is read-only, submits no jobs, and takes about a second.
Prefer it to parsing `scontrol`, `sinfo` and `sacctmgr` yourself: it combines them, and states why a limit is what it is.

Always pass `--live --format json` on a cluster, and name the probes that you need.

```console
$ ./probes/probe.sh --live --format json partitions usage access
```

Run `./probes/probe.sh --list --format json` once for the meaning of every field.

## Which probe

| Question | Probe | Look at |
|---|---|---|
| Which partition should a job use, and what are its limits? | `partitions` | `nodes.usable`, `job_nodes.max`, `time` |
| Can this user submit to a partition, and with which account and QoS? | `access` | `partitions[].can_submit`, `reason`, `accounts`, `qos` |
| Why was a job rejected at submission? | `access`, `partitions` | `reason`; `job_nodes.max` and `time.max` against the request |
| Why is a job pending? | `usage`, `partitions` | `jobs.pending_reasons`, `qos_nodes`, `nodes.limited_by` |
| Will a job start soon? | `usage` | `nodes.idle`, `qos_nodes.free`, `jobs.pending` |
| What hardware does a partition have, and which `--constraint` values exist? | `nodetypes` | `cpus`, `memory_gb`, `gres`, `features` |
| Where should data go? | `filesystems` | `path`, `filesystem`, `storage` |
| Which version of Slurm, uenv or the container engine is installed? | `versions` | `tools[].version` |

## Reading the output

* `null` means no limit or not set, never zero.
* `partitions[].nodes.pool` is the number of nodes that a partition is configured on.
  Partitions share nodes, so it is not what the jobs of the partition can use: that is `nodes.usable`, and `nodes.limited_by` names the QoS limit that sets it.
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
$ diff <(./probes/probe.sh --live partitions) <(./probes/probe.sh --intended partitions)
```

Off a cluster, read `probes/generated/<cluster>/<probe>.json`: the intended configuration in the same format.
The `usage` and `access` probes are only available on a cluster.

## Not covered

Quota and how full a file system is, the remaining budget of a project, scratch cleanup and backup policies, and the intended purpose of each partition.
For policies, read the cluster and storage pages of the documentation.
