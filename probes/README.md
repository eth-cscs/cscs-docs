# Cluster configuration probes

Facts about a cluster that can be read from the cluster should not be maintained by hand.
This directory holds a script that reads them, and the artifacts it produces, which the documentation build includes.
The same script answers questions about a cluster for an agent that is helping a user on it, see [Use by agents](#use-by-agents).

The hand-written partition table for Daint claimed a maximum of 2 nodes per job on the `debug` partition; `scontrol` reports 10.
That class of defect is what this replaces.

## Refreshing a cluster

Log into a login node of the cluster, then:

```console
$ git pull
$ ./probes/probe.sh
writing probes/generated/daint/partitions.md
...
$ git diff probes/generated/
```

Commit the result and open a pull request.
The diff is the useful output: a pull request whose diff adds two partition rows is the notification that the cluster gained two partitions, in a form a reviewer can check.

The script determines the cluster itself, is read-only with respect to the system, and submits no jobs.

## What is generated

Each probe writes two files to `probes/generated/<cluster>/`: a markdown table that the documentation includes, and a JSON file with everything the probe knows.

| Probe | Source | Table | Also in the JSON |
|---|---|---|---|
| `partitions` | `slurm.conf`, `sacctmgr show qos` | Nodes that the jobs of a partition can use, job size and time limits | The node pool and the limit that reduces it, partition and allowed QoS, priority tier, preemption, and the limits of each QoS |
| `nodetypes` | `slurm.conf` | Nodes, CPUs, memory, GPUs and available features for each node configuration in each partition | |
| `filesystems` | `findmnt -T` on `$HOME`, `$SCRATCH`, `$SCRATCH_OLD`, `$STORE` | The file system each variable provides, and the Alps storage system that hosts it (platform-level, see below) | The file system type |
| `versions` | tool `--version` output | Slurm, uenv, container engine, enroot, podman, OS | |

Two more files are written for each cluster: `stamp.md`, the visible "generated on" line for a page, and `manifest.json`, the provenance that `check-freshness.sh` reads.

A value in a table is what a job is held to, which is not always the value of the partition.
On Clariden the `normal` partition is configured on 1343 nodes, and its QoS limits its jobs to 400 of them: the table shows 400, and the JSON has both numbers and the limit that explains the difference.

Not generated, because no probe returns them: quota limits, cleanup periods, occupancy thresholds, billing rules, and the intended purpose of a partition.
Those are policy and remain hand-written.

## How a probe is built

A probe has three parts, which are kept apart so that the documentation and agents can be given different views of the same facts.

| Part | Where | What it does |
|---|---|---|
| Collect | `lib/system.py`, `lib/slurm.py` | Runs commands and reads files, and returns what the system states |
| Model | `build_*` in `lib/probes.py` | Plain data: the collected facts, the values derived from them, and the reason for each derived value |
| View | `columns` in `lib/probes.py`, `lib/views.py` | The markdown table is a list of columns over the model; the JSON view is the model |

To remove a column from a table, delete its entry from `columns`.
The value stays in the model, so it is still in the JSON.
Platform owners asked for the allowed QoS and the priority of a partition to be left out of the tables, and that is how they were removed.

The tables can be made again from the committed JSON, without access to a cluster:

```console
$ ./probes/probe.sh --render
```

A change to the columns of a table is therefore one commit for all clusters.
CI runs `./probes/probe.sh --render --check`, which fails if a table does not match its JSON, so the two cannot drift apart and a table cannot be edited by hand.
A change to what a probe collects still needs the probe to be run on each cluster.

The JSON has a `schema` number.
Adding a field does not change it; renaming or removing a field, or changing what one means, does.

### Scopes

Every probe has a scope, which decides where its output may go.

| Scope | What | Probes | Written to `generated/` |
|---|---|---|---|
| `config` | How the system is set up | `partitions`, `nodetypes`, `filesystems`, `versions` | yes |
| `state` | What the system is doing now | `usage` | never |
| `user` | What the person running the probe can use | `access` | never |

Only `config` probes are written and included in the documentation.
The others can only be printed, with `--live`.
Within a `config` probe, fields that identify users or projects (the accounts and groups allowed in a partition, the real path of `$STORE`) are printed on the system and left out of the files that are committed.

## Intended and live configuration

The probe has two uses, which need different sources.

| | Documentation | On the system |
|---|---|---|
| Command | `./probes/probe.sh` | `./probes/probe.sh --live [probe...]` |
| Slurm source | `slurm.conf`, as deployed by the platform owners | `scontrol show partition` and `sinfo` |
| Shows | The intended configuration | What the scheduler is using now |
| Output | Writes `probes/generated/<cluster>/` | Prints to the terminal, writes nothing |

The documentation shows the intended configuration.
A partition or node can be changed on the running system with `scontrol update`, for example to shorten a time limit during an incident.
Such a change is not in `slurm.conf`, so it does not appear in the generated tables, and regenerating the documentation while it is in place produces no diff.
If users need to know about the change, the platform owners describe it in an admonition on the cluster page.

An agent that helps a user on the system needs what the scheduler is doing now, including such changes, so it uses `--live`.
`--intended` prints the intended configuration without writing it, so the two can be compared to see what has been changed on the running system:

```console
$ diff <(./probes/probe.sh --live partitions) <(./probes/probe.sh --intended partitions)
```

QoS limits are the exception.
They are stored in the Slurm accounting database and are not in `slurm.conf`, so both modes read them with `sacctmgr`, and a change to a QoS limit does change the generated tables.

The probe fails if it cannot read `slurm.conf`, rather than falling back to the live configuration.

## Use by agents

An agent on a login node runs the probes from a checkout of this repository, which can be read-only.

```console
$ ./probes/probe.sh --list
$ ./probes/probe.sh --list --format json
$ ./probes/probe.sh --live --format json partitions usage access
```

`--list` names the probes, and with `--format json` describes every field of their output, so an agent does not need this page.
The JSON output of several probes is one object:

```json
{
  "schema": 1,
  "cluster": "clariden",
  "source": "live",
  "probes": {
    "partitions": {"partitions": [...], "qos": {...}},
    "usage": {"partitions": [...], "qos": {...}}
  }
}
```

The probes report facts and the reasons for derived values, and leave the diagnosis to the agent.
For example, a user asks why a job in `normal` on Clariden is pending while nodes are idle:

* `partitions` gives `nodes.pool` 1343, `nodes.usable` 400, and `nodes.limited_by` the QoS `normalp` with `GrpTRES node=400`;
* `usage` gives 399 of those 400 nodes in use, and `QOSGrpNodeLimit` as the most common reason for pending jobs;
* `access` gives the partitions and QoS that the user could submit to instead.

`probes/skill/SKILL.md` tells an agent which probe answers which kind of question.

Off the system, an agent reads the committed `probes/generated/<cluster>/*.json`, which is the intended configuration in the same format.

## Four rules

These govern what is written for the documentation.

**Configuration, never state.** Partition definitions and file system layout change on a timescale of weeks, so an artifact stays correct between runs, and re-running produces an empty diff when nothing has changed.
This also means a run during a drain still captures the right thing, so the cluster does not need to be in any particular state when the script is run.
Live node and job counts are excluded for the same reason.

**The intended configuration, not the running one.** See the section above.

**Redaction at the source.** The artifacts are committed to a public repository.
A model is built for publication without the fields that identify users and projects, and with placeholders in paths.
`findmnt` is used rather than `mount` because `mount` output contains NFS server addresses and Lustre MGS NIDs.
A reviewer cannot be relied on to spot a leak in a large diff, so the script must not produce one.

**Use the documentation's concepts, not the system's.** Generated content replaces hand-written content, and must not lose the care that went into it.
Emit the names and links the docs use, rather than raw command output: `$SCRATCH` is Scratch on Ritom, linked to their pages, not an `nfs` mount at `/ritom/scratch`.
Start from what users reach (the environment variables), not from everything the system exposes (every mount, including other tenants' Store).
When the system reports something that has no documented concept, fail rather than emit it, so that the docs or the mapping are updated deliberately.
The probe also runs with a fixed system `PATH`, so that it reports what every user sees rather than the environment of whoever ran it.

## Platforms and clusters

A platform can have more than one cluster, and its clusters are configured to serve the same community: Daint and Eiger are both HPC Platform (HPCP) clusters.
Facts that are a property of the platform, such as which storage `$HOME`, `$SCRATCH` and `$STORE` point to, should be documented once on the platform page, and the cluster pages should link to it.

The platforms, their clusters, and the artifacts that are documented once per platform are listed in `probes/platforms.json`.
The platform page includes the first cluster's copy of each such artifact; at present the HPCP page includes `probes/generated/daint/filesystems.md`.

That is only correct while every cluster of the platform agrees, so `probes/check-platforms.sh` compares the artifacts, ignoring the header that names the cluster.
Like the freshness check, it reads committed files and runs in CI.
A difference fails the check: either a cluster has been misconfigured, or the artifact is no longer a platform-level fact and belongs on the cluster pages.

Before adding an artifact to `platforms.json`, run the probe on every cluster of the platform and confirm that `check-platforms.sh` passes.

Facts that differ between the clusters of a platform, such as partitions and node types, stay on the cluster pages.

## Including an artifact in a page

```markdown
### Partitions

--8<-- "probes/generated/daint/partitions.md"
```

Snippet paths resolve from the repository root.
`pymdownx.snippets` is configured with `check_paths = true` and the site builds with `--strict`, so a renamed or deleted artifact fails the build rather than rendering an empty section.

Include `stamp.md` once per page, so that a reader can see how old the generated content is.
It is the only artifact carrying a date, which is what keeps the content fragments diff-stable.

## Freshness

```console
$ ./probes/check-freshness.sh
cluster         age  threshold  status
daint        0 days    30 days  ok
eiger             -          -  not generated
```

Artifacts older than 30 days are reported overdue, matching the monthly maintenance cadence; twice that fails, so one missed month warns without blocking.
This check reads the committed manifests and needs no cluster access, so it runs in CI on a schedule.
CI cannot refresh the artifacts, but it can say which cluster someone needs to log into.

A cluster with a documentation page but no artifacts is reported for information and does not fail.

## Tests

The collectors read the system through `lib/system.py`, which can read saved command output from a directory instead.
`probes/tests/fixtures/alpha` is a small invented cluster in that form, and the tests run the probes against it:

```console
$ python3 -m unittest discover -s probes/tests
```

The tests need no cluster and run in CI.
When a cluster is found to use a feature of `slurm.conf` that the probes get wrong, add it to the fixture with a test.
Do not copy the `slurm.conf` of a cluster into the repository: it contains account names and addresses.

## Compatibility

The probes must run on a login node with no set-up step.
Login nodes currently provide Python 3.6, so the code uses only the standard library, and avoids f-strings and `date.fromisoformat`.
`probe.sh` is a wrapper that sets a fixed system `PATH` and runs `lib/cli.py`.

`SINFO_FORMAT`, `SQUEUE_FORMAT` and `SLURM_TIME_FORMAT` are preset site-wide in `/etc/profile.d/cscs.sh`, so every `sinfo` call passes an explicit `-o`.
