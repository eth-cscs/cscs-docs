# Cluster configuration probes

If a fact about a cluster can be read directly from the cluster, we shouldn't have to maintain it by hand.
This directory contains a script that collects those facts, along with the files it generates, which are included in the documentation when it is built.

Here's the kind of mistake this is meant to prevent.
The hand-written partition table for Daint said that jobs on the `debug` partition could use at most 2 nodes, but `scontrol` reports a limit of 10.
Nobody noticed, because nothing checked the table against the system.

The same script is also useful to an agent that is helping a user on a cluster: see [Use by agents](#use-by-agents).

## Refreshing a cluster

Log in to one of the cluster's login nodes and run:

```console
$ git pull
$ ./probes/probe.sh
writing generated/clusters/daint/partitions.md
...
$ git diff generated/clusters/
```

Then commit the result and open a pull request.

The diff is the most useful part.
If a cluster gains two partitions, the pull request will add two rows to the partition table, and a reviewer can see exactly what changed.

You don't need to tell the script which cluster you are on, because it works that out itself.
It only reads from the system: it doesn't change anything and it doesn't submit any jobs.

## What gets generated

The probes write their output to `generated/clusters/<cluster>/`, outside `docs/`, because every markdown file under `docs/` is built as a page of its own.
Each probe writes a markdown table that the documentation includes, named after the probe, such as `partitions.md`.
The models of all the probes are written to one JSON file, `results.json`, which contains everything the probes know, which is usually more than the tables show.

| Probe | Reads from | The table shows | The JSON also has |
|---|---|---|---|
| `partitions` | `slurm.conf` and `sacctmgr show qos` | How many nodes a job in each partition can use, plus job size and time limits | The full node pool and whatever limit reduces it, allowed QoS, priority tier, preemption, and the limits of each QoS |
| `nodetypes` | `slurm.conf` | How many nodes of each Alps node type are in each partition (linked to the hardware docs), and the documented feature sets you can select with `--constraint` (vboost, thp, amdgpu) | The CPUs, memory and GPUs that Slurm schedules, and every feature |
| `nodes` | `slurm.conf` | How many nodes of each node type and memory configuration the cluster has, with their CPU sockets and GPUs | The memory and number of sockets that Slurm is configured with for each node |
| `filesystems` | `findmnt -T` on `$HOME`, `$SCRATCH`, `$SCRATCH_OLD` and `$STORE` | Which file system each variable points to, and which Alps storage system hosts it (this is documented per platform, see below) | The file system type |
| `versions` | The `--version` output of each tool | Versions of Slurm, uenv, the container engine, enroot, podman and the OS | |

`results.json` also records when the files were generated, which is what `check-freshness.sh` reads, and `emitters`, a hash of the probe code that produced them.
The tables carry neither, so a table changes only when what it shows changes.
Lists whose order means nothing to Slurm, such as `AllowQos`, are sorted, so reordering them in `slurm.conf` doesn't change any file either.
Re-running the probes on an unchanged cluster changes only `results.json`: its date, and `emitters` if the probe code has changed since the last run.

The numbers in the tables are the limits that a job actually runs into, which aren't always the same as the partition's own settings.
For example, Clariden's `normal` partition is configured with 1343 nodes, but its QoS limits each job to 400 of them.
The table shows 400, and the JSON records both numbers along with the QoS limit that explains the difference.

Some things can't be generated, because no command on the system reports them.
These include quota limits, cleanup periods, occupancy thresholds, billing rules, and what a partition is intended to be used for.
They are policy decisions, so they stay hand-written.

## How a probe is built

Each probe is split into three parts.
We keep them separate so that the documentation and agents can each get a different view of the same facts.

| Part | Where it lives | What it does |
|---|---|---|
| Collect | `lib/system.py`, `lib/slurm.py` | Runs commands and reads files, and returns what the system reports |
| Model | the `build_*` functions in `lib/probes.py` | Holds the collected facts as plain data, along with any values derived from them and the reason for each one |
| View | `columns` in `lib/probes.py`, and `lib/views.py` | Turns the model into output: the markdown table is a list of columns, and the JSON is just the model itself |

To remove a column from a table, delete its entry from `columns`.
The value stays in the model, so it still appears in the JSON.
This is how we dropped the allowed QoS and partition priority from the tables when the platform owners asked us to.

Because `results.json` is committed, you can regenerate the tables without logging in to any cluster:

```console
$ ./probes/probe.sh --render
```

This means that changing the columns of a table takes a single commit that covers every cluster.
In CI we run `./probes/probe.sh --render --check`, which fails if any table doesn't match `results.json`.
That keeps the two in sync, and it also means nobody can edit a table by hand.
If you change what a probe collects, though, you still need to run it on each cluster.

The JSON includes a `schema` number.
Adding a new field doesn't change it, but renaming or removing a field, or changing what a field means, does.

### Scopes

Every probe has a scope, which controls where its output is allowed to go.

| Scope | Describes | Probes | Written to `generated/clusters/`? |
|---|---|---|---|
| `config` | How the system is set up | `partitions`, `nodetypes`, `nodes`, `filesystems`, `versions` | yes |
| `state` | What the system is doing right now | `usage` | never |
| `user` | What the person running the probe has access to | `access` | never |

Only `config` probes are written to files and included in the documentation.
The other probes can only print their results, using `--live`.

Even `config` probes can see some details that identify users or projects, such as the accounts and groups allowed in a partition, or the real path behind `$STORE`.
These are printed when you run the probe on the system, but they are left out of the committed files.

## Intended versus live configuration

The probes are used in two different ways, and each needs a different source of information.

| | For the documentation | On the system |
|---|---|---|
| Command | `./probes/probe.sh` | `./probes/probe.sh --live [probe...]` |
| Slurm source | `slurm.conf`, as deployed by the platform owners | `scontrol show partition` and `sinfo` |
| Shows | The intended configuration | What the scheduler is actually doing now |
| Output | Writes to `generated/clusters/<cluster>/` | Prints to the terminal and writes nothing |

The documentation describes the intended configuration.
Admins can change a partition or node on the running system with `scontrol update`, for example to shorten a time limit during an incident.
That change isn't in `slurm.conf`, so it doesn't show up in the generated tables, and regenerating the docs while it is in effect won't produce a diff.
If users need to know about a temporary change like this, the platform owners should add an admonition to the cluster page.

An agent helping a user on the system, on the other hand, needs to know what the scheduler is doing right now, including any temporary changes.
That's what `--live` is for.
There's also `--intended`, which prints the intended configuration without writing any files.
Comparing the two shows you what has been changed on the running system:

```console
$ diff <(./probes/probe.sh --live partitions) <(./probes/probe.sh --intended partitions)
```

QoS limits are the one exception.
They live in the Slurm accounting database rather than in `slurm.conf`, so both modes read them with `sacctmgr`.
As a result, changing a QoS limit does change the generated tables.

If the probe can't read `slurm.conf`, it fails instead of quietly falling back to the live configuration.

## Use by agents

An agent on a login node can run the probes from a checkout of this repository, and the checkout can be read-only.

```console
$ ./probes/probe.sh --list
$ ./probes/probe.sh --list --format json
$ ./probes/probe.sh --live --format json partitions usage access
```

`--list` shows the available probes.
With `--format json` it also describes every field in their output, so an agent doesn't need to read this page to use them.
When you run several probes at once, the JSON output is combined into a single object:

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

The probes report facts, and explain how they arrived at any derived values, but they leave the diagnosis to the agent.
Say a user on Clariden asks why their job in `normal` is pending even though some nodes are idle.
The agent could piece together the answer like this:

* `partitions` shows that the pool has 1343 nodes (`nodes.pool`), but only 400 are usable (`nodes.usable`), because the `normalp` QoS sets `GrpTRES node=400` (`nodes.limited_by`);
* `usage` shows that 399 of those 400 nodes are already in use, and that the most common reason for pending jobs is `QOSGrpNodeLimit`;
* `access` lists the other partitions and QoS that the user could submit to instead.

The file `probes/skill/SKILL.md` tells an agent which probe to use for which kind of question.

When an agent isn't on the system, it can read the committed `generated/clusters/<cluster>/results.json` instead.
It contains the intended configuration in the same format as the combined output of the published probes.

## Four rules

These rules apply to everything the probes write for the documentation.

**Record configuration, not state.**
Partition definitions and file system layouts change over weeks, not minutes, so the generated files stay correct between runs, and re-running on an unchanged cluster gives an empty diff.
It also means the cluster doesn't need to be in any particular state when you run the script: a run during a drain still records the right thing.
For the same reason, live node and job counts are left out.

**Record the intended configuration, not the running one.**
See [Intended versus live configuration](#intended-versus-live-configuration) above.

**Redact at the source.**
The generated files are committed to a public repository.
So the model used for publication is built without any fields that identify users or projects, and paths are replaced with placeholders.
We use `findmnt` rather than `mount` for the same reason, because `mount` output includes NFS server addresses and Lustre MGS NIDs.
A reviewer can't be expected to spot a leak buried in a large diff, so the script must never produce one in the first place.

**Use the documentation's concepts, not the system's.**
Generated content replaces content that people wrote carefully, and it shouldn't be worse.
So the probes output the names and links the docs already use, rather than raw command output.
For example, `$SCRATCH` is described as Scratch on Ritom, with links to the relevant pages, rather than as an `nfs` mount at `/ritom/scratch`.
The probes start from what users actually use (the environment variables), not from everything the system exposes (every mount, including other tenants' Store).
If the system reports something that the docs have no concept for, the probe fails instead of printing it, so that someone has to update the docs or the mapping on purpose.
The probe also runs with a fixed system `PATH`, so it reports what every user sees, not whatever happens to be in the environment of the person running it.

## Platforms and clusters

A platform can have several clusters, all set up to serve the same community.
For example, Daint and Eiger are both clusters on the HPC Platform (HPCP).
Some facts belong to the platform as a whole, such as which storage `$HOME`, `$SCRATCH` and `$STORE` point to.
Those should be documented once, on the platform page, and the cluster pages should link to it.

The file `probes/platforms.json` lists the platforms, their clusters, and which generated files are documented once per platform:

```json
"mlp": {
  "reference": "clariden",
  "clusters": {"bristen": "warn"},
  "artifacts": ["filesystems.md"],
  "page": "docs/platforms/mlp/index.md"
}
```

The platform page includes the copy generated on the platform's reference cluster.
In this example, the MLP page includes `generated/clusters/clariden/filesystems.md`.

Of course, that only works as long as every cluster on the platform really is the same.
To check this, `probes/check-platforms.sh` compares each cluster's files with the reference cluster's, ignoring the header line that names the cluster.
Like the freshness check, it only reads committed files, so it runs in CI.
What happens when it finds a difference depends on the severity set for that cluster:

| Severity | What happens when the cluster differs from the reference |
|---|---|
| `critical` | The check fails. Either the cluster has been misconfigured, or the fact is no longer platform-wide and should move to the cluster pages. |
| `warn` | The difference is printed and shown as a warning on the pull request, but the check passes. |

Use `warn` for a cluster that is expected to differ from the rest of its platform, such as Bristen on MLP.
The check also fails if a platform page doesn't include the reference cluster's copy of a file it is supposed to include.

Before you add a file to `platforms.json`, run the probe on every cluster in the platform and make sure `check-platforms.sh` passes.

Facts that differ between clusters on the same platform, such as partitions and node types, stay on the individual cluster pages.

## Including a generated file in a page

```markdown
### Partitions

--8<-- "generated/clusters/daint/partitions.md"
```

Snippet paths are relative to the root of the repository.
Because `pymdownx.snippets` is configured with `check_paths = true` and the site is built with `--strict`, renaming or deleting a generated file breaks the build, rather than silently leaving an empty section.

## Freshness

```console
$ ./probes/check-freshness.sh
cluster         age  threshold  status
daint        0 days    30 days  ok
eiger             -          -  not generated
```

Files older than 30 days are reported as overdue, to match the monthly maintenance schedule.
Files older than 60 days make the check fail, so missing a single month gives you a warning but doesn't block anything.

The check only reads the committed `results.json` files and doesn't need access to any cluster, so it runs in CI on a schedule.
CI can't refresh the files itself, but it can tell you which cluster someone needs to log in to.

If a cluster has a documentation page but no generated files yet, the check mentions it but doesn't fail.

## Tests

The collectors access the system through `lib/system.py`, which can also read saved command output from a directory instead of running the real commands.
`probes/tests/fixtures/alpha` is a small, made-up cluster stored in that form, and the tests run the probes against it:

```console
$ python3 -m unittest discover -s probes/tests
```

The tests don't need a cluster, so they run in CI.
If you find a cluster that uses a `slurm.conf` feature the probes handle incorrectly, add an example of it to the fixture, along with a test.
Don't copy a real cluster's `slurm.conf` into the repository, because it contains account names and addresses.

## Compatibility

The probes have to run on a login node without any setup.
Login nodes currently have Python 3.6, so the code only uses the standard library, and avoids newer features such as f-strings and `date.fromisoformat`.
`probe.sh` is a small wrapper that sets a fixed system `PATH` and then runs `lib/cli.py`.

`SINFO_FORMAT`, `SQUEUE_FORMAT` and `SLURM_TIME_FORMAT` are set for everyone in `/etc/profile.d/cscs.sh`, so every call to `sinfo` passes its own `-o` format explicitly.
