# Cluster configuration probes

Facts about a cluster that can be read from the cluster should not be maintained by hand.
This directory holds a script that reads them, and the artifacts it produces, which the documentation build includes.

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

| Artifact | Source | Contents |
|---|---|---|
| `partitions.md` | `scontrol show partition` | Node counts, job size and time limits, QoS, priority |
| `nodetypes.md` | `sinfo` | CPUs, memory, GPUs and active features per partition |
| `filesystems.md` | `findmnt -T` on `$HOME`, `$SCRATCH`, `$SCRATCH_OLD`, `$STORE` | The file system each variable provides, and the Alps storage system that hosts it |
| `versions.md` | tool `--version` output | Slurm, uenv, container engine, enroot, podman, OS |
| `stamp.md` | — | The visible "generated on" line for the page |
| `manifest.json` | — | Provenance, for `check-freshness.sh` |

Not generated, because no probe returns them: quota limits, cleanup periods, occupancy thresholds, billing rules, and the intended purpose of a partition.
Those are policy and remain hand-written.

Also not generated: anything per-user or per-project, and live node or job counts.

## Three rules

**Configuration, never state.** Partition definitions and file system layout change on a timescale of weeks, so an artifact stays correct between runs, and re-running produces an empty diff when nothing has changed.
This also means a run during a drain still captures the right thing, so the cluster does not need to be in any particular state when the script is run.
Live node and job counts are excluded for the same reason.

**Redaction at the source.** The artifacts are committed to a public repository.
Only whitelisted fields are emitted, with user and project identifiers substituted.
`findmnt` is used rather than `mount` because `mount` output contains NFS server addresses and Lustre MGS NIDs.
A reviewer cannot be relied on to spot a leak in a large diff, so the script must not produce one.

**Use the documentation's concepts, not the system's.** Generated content replaces hand-written content, and must not lose the care that went into it.
Emit the names and links the docs use, rather than raw command output: `$SCRATCH` is Scratch on Ritom, linked to their pages, not an `nfs` mount at `/ritom/scratch`.
Start from what users reach (the environment variables), not from everything the system exposes (every mount, including other tenants' Store).
When the system reports something that has no documented concept, fail rather than emit it, so that the docs or the mapping are updated deliberately.
The probe also runs with a fixed system `PATH`, so that it reports what every user sees rather than the environment of whoever ran it.

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

## Compatibility

The emitters must run on a login node with no set-up step.
Login nodes currently provide Python 3.6, so the Python fragments avoid f-strings and `date.fromisoformat`.

`SINFO_FORMAT`, `SQUEUE_FORMAT` and `SLURM_TIME_FORMAT` are preset site-wide in `/etc/profile.d/cscs.sh`, so every `sinfo` call passes an explicit `-o`.
