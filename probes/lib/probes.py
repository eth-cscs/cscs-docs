"""The probes: what each one reports, and how its table is laid out.

A probe has three parts, which are kept apart:

  collect   read the system (system.py, slurm.py)
  model     build() returns the facts as plain data: everything that was
            collected, the values derived from it, and why a derived value is
            what it is. Nothing in the model is about presentation.
  view      the markdown table is a list of columns over the model (views.py);
            the JSON view is the model itself.

The documentation shows a few columns. An agent reads the JSON, which has the
rest: removing a column from a table does not remove it from the model.

Each probe has a scope, which decides where its output may go:

  config    how the system is set up. The only scope that the documentation
            includes, and the only one that is written to probes/generated/.
  state     what the system is doing now, such as idle nodes and pending jobs.
  user      what the person running the probe can use.

Runs on the login nodes, which provide Python 3.6: no f-strings.
"""
import re
from collections import OrderedDict

import slurm
from system import ProbeError

# Version of the JSON that the probes emit. Increase it when a field is renamed,
# removed, or changes meaning; adding a field does not need a new version.
SCHEMA = 1


class Probe(object):
    def __init__(self, name, scope, description, sources, build, rows, columns, fields):
        self.name = name
        self.scope = scope
        self.description = description
        self.sources = sources      # source ("intended", "live") -> where the facts come from
        self.build = build          # (system, source, publish) -> model
        self.rows = rows            # model -> the rows of the markdown table
        self.columns = columns      # [(header, row -> cell)]
        self.fields = fields        # field of the model -> what it means


# -- formatting helpers for table cells ---------------------------------------

def code(value):
    return "`%s`" % value


def number(value):
    return "unlimited" if value is None else str(value)


# -- partitions ---------------------------------------------------------------

def slurm_time(value):
    """A time limit in the form Slurm prints, [days-]hh:mm:ss, or None where
    there is no limit."""
    upper = value.upper()
    if upper in ("UNLIMITED", "INFINITE", "NONE", ""):
        return None
    days, _, rest = value.rpartition("-")
    parts = [int(p) for p in rest.split(":")]
    if days:
        hours, minutes, seconds = (parts + [0, 0])[:3]
    elif len(parts) == 1:
        hours, minutes, seconds = 0, parts[0], 0
    elif len(parts) == 2:
        hours, minutes, seconds = 0, parts[0], parts[1]
    else:
        hours, minutes, seconds = parts
    total = ((int(days or 0) * 24 + hours) * 60 + minutes) * 60 + seconds
    days, total = divmod(total, 86400)
    hours, total = divmod(total, 3600)
    minutes, seconds = divmod(total, 60)
    text = "%02d:%02d:%02d" % (hours, minutes, seconds)
    return "%d-%s" % (days, text) if days else text


def partition_qos(partition, qos):
    name = partition["qos"]
    if name is None:
        return None
    if name not in qos:
        raise ProbeError("partition %s uses QoS %s, which sacctmgr does not report"
                         % (partition["name"], name))
    return qos[name]


def usable_nodes(partition, qos):
    """The most nodes that the jobs of a partition can hold at the same time,
    and the limit that sets it if that is not the size of the partition.

    A partition can list far more nodes than its jobs may use together: the
    limit is then a group limit (GrpTRES) on the partition QoS, or on the QoS
    that jobs in the partition are allowed to use.
    """
    usable, limited_by = partition["nodes"], None
    own = partition_qos(partition, qos)
    if own and own["grp_nodes"] is not None and own["grp_nodes"] < usable:
        usable = own["grp_nodes"]
        limited_by = {"source": "partition QoS", "qos": [own["name"]],
                      "limit": "GrpTRES node=%d" % usable}
    if partition["allowqos"] is not None:
        allowed = [qos[n] for n in partition["allowqos"] if n in qos]
        open_qos = [q for q in allowed if not slurm.qos_blocked(q)]
        if open_qos and all(q["grp_nodes"] is not None for q in open_qos):
            total = sum(q["grp_nodes"] for q in open_qos)
            if total < usable:
                usable = total
                limited_by = {"source": "allowed QoS", "qos": [q["name"] for q in open_qos],
                              "limit": "GrpTRES node=" + "+".join(str(q["grp_nodes"]) for q in open_qos)}
    return usable, limited_by


def job_nodes(partition, qos):
    """The most nodes that one job in a partition can use, and what sets it."""
    limit, limited_by = None, None
    if partition["maxnodes"].upper() not in ("UNLIMITED", "INFINITE"):
        limit = int(partition["maxnodes"])
        limited_by = {"source": "partition", "limit": "MaxNodes=%d" % limit}
    own = partition_qos(partition, qos)
    if own and own["job_nodes"] is not None and (limit is None or own["job_nodes"] < limit):
        limit = own["job_nodes"]
        limited_by = {"source": "partition QoS", "qos": [own["name"]],
                      "limit": "MaxTRES node=%d" % limit}
    return limit, limited_by


def qos_model(entry):
    return OrderedDict([
        ("max_nodes_in_use", entry["grp_nodes"]),
        ("max_nodes_per_job", entry["job_nodes"]),
        ("max_nodes_per_user", entry["user_nodes"]),
        ("max_running_jobs_per_user", entry["user_jobs"]),
        ("max_submitted_jobs_per_user", entry["user_submit"]),
        ("max_running_jobs_per_account", entry["account_jobs"]),
        ("max_submitted_jobs_per_account", entry["account_submit"]),
        ("max_time", slurm_time(entry["maxwall"]) if entry["maxwall"] else None),
        ("priority", entry["priority"]),
        ("preempts", entry["preempt"]),
        ("blocks_jobs", slurm.qos_blocked(entry)),
    ])


def build_partitions(system, source, publish):
    partitions = slurm.load_partitions(system, source)
    qos = slurm.load_qos(system.run("sacctmgr-qos", slurm.SACCTMGR_QOS))

    items, used_qos = [], set()
    for partition in sorted(partitions, key=lambda p: p["name"]):
        # Hidden partitions are for staff and services. They are not published,
        # but are reported on the system, where `scontrol` shows them anyway.
        if publish and partition["hidden"]:
            continue
        usable, usable_limit = usable_nodes(partition, qos)
        per_job, per_job_limit = job_nodes(partition, qos)
        item = OrderedDict([
            ("name", partition["name"]),
            ("default", partition["default"]),
            ("hidden", partition["hidden"]),
            ("nodes", OrderedDict([
                ("pool", partition["nodes"]),
                ("usable", usable),
                ("limited_by", usable_limit),
            ])),
            ("job_nodes", OrderedDict([
                ("max", per_job),
                ("limited_by", per_job_limit),
            ])),
            ("time", OrderedDict([
                ("default", slurm_time(partition["defaulttime"])),
                ("max", slurm_time(partition["maxtime"])),
            ])),
            ("partition_qos", partition["qos"]),
            ("allowed_qos", partition["allowqos"]),
            ("priority_tier", partition["priority"]),
            ("preempt_mode", partition["preemptmode"]),
            ("oversubscribe", partition["oversubscribe"]),
        ])
        # Account and group names identify projects, so they are reported on
        # the system and left out of what is committed to a public repository.
        if not publish:
            item["allowed_accounts"] = partition["allowaccounts"]
            item["allowed_groups"] = partition["allowgroups"]
        items.append(item)
        used_qos.update(partition["allowqos"] or [])
        if partition["qos"]:
            used_qos.add(partition["qos"])

    return OrderedDict([
        ("partitions", items),
        ("qos", OrderedDict((name, qos_model(qos[name])) for name in sorted(used_qos) if name in qos)),
    ])


def partition_name(row):
    return code(row["name"]) + (" (default)" if row["default"] else "")


PARTITIONS = Probe(
    name="partitions",
    scope="config",
    description="Slurm partitions: how many nodes their jobs can use, job size and time limits, "
                "and the QoS that apply to them.",
    sources={
        "intended": "`slurm.conf` and `sacctmgr show qos`",
        "live": "`scontrol show partition` and `sacctmgr show qos`",
    },
    build=build_partitions,
    rows=lambda model: [p for p in model["partitions"] if not p["hidden"]],
    columns=[
        ("Partition", partition_name),
        ("Nodes", lambda row: str(row["nodes"]["usable"])),
        ("Max nodes/job", lambda row: number(row["job_nodes"]["max"])),
        ("Default time", lambda row: row["time"]["default"] or "none"),
        ("Max time", lambda row: row["time"]["max"] or "unlimited"),
    ],
    fields=OrderedDict([
        ("partitions[].name", "Name, as passed to --partition."),
        ("partitions[].default", "True for the partition that a job gets when it names none."),
        ("partitions[].hidden", "True for partitions that sinfo does not list; they are for staff and services."),
        ("partitions[].nodes.pool", "Number of nodes that the partition is configured on. Partitions can share nodes."),
        ("partitions[].nodes.usable", "Most nodes that all the jobs of the partition can hold at the same time."),
        ("partitions[].nodes.limited_by", "The limit that makes usable smaller than pool, or null. "
                                          "Jobs waiting on it are pending with reason QOSGrpNodeLimit."),
        ("partitions[].job_nodes.max", "Most nodes that one job can request, or null for no limit."),
        ("partitions[].job_nodes.limited_by", "The partition or QoS limit that sets job_nodes.max, or null."),
        ("partitions[].time.default", "Time limit of a job that sets none, as [days-]hh:mm:ss, or null."),
        ("partitions[].time.max", "Longest time limit that a job can request, or null for no limit."),
        ("partitions[].partition_qos", "QoS whose limits apply to every job in the partition, or null. "
                                       "It is not one that a job requests."),
        ("partitions[].allowed_qos", "QoS that a job in the partition can run under (--qos), or null for any."),
        ("partitions[].priority_tier", "Jobs in a partition with a higher tier are scheduled first, "
                                       "and can preempt jobs in a lower tier if preemption is enabled."),
        ("partitions[].preempt_mode", "What happens to a job of this partition that is preempted; "
                                      "OFF if its jobs are never preempted, null for the cluster default."),
        ("partitions[].oversubscribe", "EXCLUSIVE if a job gets whole nodes; otherwise jobs can share a node."),
        ("partitions[].allowed_accounts", "Accounts that can submit to the partition, or null for any. "
                                          "Not published."),
        ("partitions[].allowed_groups", "Unix groups that can submit to the partition, or null for any. "
                                        "Not published."),
        ("qos.<name>", "Limits of each QoS named by a partition; null where there is no limit. "
                       "Read from the accounting database in both the intended and live modes."),
        ("qos.<name>.max_nodes_in_use", "Most nodes that all the jobs running under the QoS can hold (GrpTRES)."),
        ("qos.<name>.blocks_jobs", "True for a QoS that lets no job run, used to stop a project."),
    ]),
)


# -- node types ---------------------------------------------------------------

def build_nodetypes(system, source, publish):
    partitions = slurm.load_partitions(system, source, nodetypes=True)
    # Nodes whose configured memory differs by less than the rounding to GB are
    # one node type, so small per-node differences do not split a row.
    groups = {}
    for partition in partitions:
        if partition["hidden"]:
            continue
        for (cpus, memory, gres, features), nodes in partition["nodetypes"].items():
            key = (partition["name"], int(cpus), int(round(int(memory) / 1024.0)), gres,
                   tuple(sorted(f for f in features.split(",") if f)))
            groups[key] = groups.get(key, 0) + nodes
    # Within a partition, the configuration with the most nodes comes first.
    items = []
    for (name, cpus, memory, gres, features), nodes in sorted(
            groups.items(), key=lambda group: (group[0][0], -group[1], group[0])):
        items.append(OrderedDict([
            ("partition", name),
            ("nodes", nodes),
            ("cpus", cpus),
            ("memory_gb", memory),
            ("gres", gres or None),
            ("features", list(features)),
        ]))
    return OrderedDict([("nodetypes", items)])


NODETYPES = Probe(
    name="nodetypes",
    scope="config",
    description="Hardware of the nodes in each partition, and the features that --constraint can select.",
    sources={
        "intended": "`slurm.conf`",
        "live": "`sinfo -o \"%R|%D|%c|%m|%G|%f\"`",
    },
    build=build_nodetypes,
    rows=lambda model: model["nodetypes"],
    columns=[
        ("Partition", lambda row: code(row["partition"])),
        ("Nodes", lambda row: str(row["nodes"])),
        ("CPUs per node", lambda row: str(row["cpus"])),
        ("Memory per node", lambda row: "%d GB" % row["memory_gb"]),
        ("GPUs", lambda row: code(row["gres"]) if row["gres"] else "none"),
        ("Features", lambda row: ", ".join(code(f) for f in row["features"]) or "none"),
    ],
    fields=OrderedDict([
        ("nodetypes[]", "One entry for each configuration of node in each partition."),
        ("nodetypes[].nodes", "Number of nodes of the partition with this configuration."),
        ("nodetypes[].cpus", "CPUs that Slurm schedules on the node (cores, or hardware threads)."),
        ("nodetypes[].memory_gb", "Memory that Slurm schedules on the node, rounded to GB."),
        ("nodetypes[].gres", "Generic resources, e.g. gpu:4 for four GPUs, or null."),
        ("nodetypes[].features", "Features that can be requested with --constraint."),
    ]),
)


# -- file systems -------------------------------------------------------------

# The storage that the standard environment variables point to, described with
# the names used in the storage documentation.
#
# The variables are the starting point, rather than the list of mounts: users
# and their tools reach storage through $SCRATCH, $STORE and $HOME, and many
# mounts (other tenants' Store, application areas) are not for general use.
# Variables that point to the same path ($STORE and $PROJECT) share an entry, so
# that every name the docs use appears without repeating the storage.
FILESYSTEM_VARIABLES = OrderedDict([
    # variable -> (documented file system, is its previous location)
    ("HOME", ("home", False)),
    ("SCRATCH", ("scratch", False)),
    ("SCRATCH_OLD", ("scratch", True)),
    ("STORE", ("store", False)),
    ("PROJECT", ("store", False)),
])

# The Alps storage system that serves a mount point: (test, name, technology,
# expected fstype). The expected fstype guards the mapping: a path that is
# mounted differently than documented fails the probe instead of being described
# wrongly.
STORAGE_SYSTEMS = [
    (lambda mount: mount.startswith("/capstor/"), "capstor", "Lustre", "lustre"),
    (lambda mount: mount.startswith("/iopsstor/"), "iopsstor", "Lustre", "lustre"),
    (lambda mount: mount.startswith("/ritom/"), "ritom", "VAST", "nfs"),
    (lambda mount: mount == "/users", "vadret", "VAST", "nfs"),
]


def path_template(system, variable, path):
    """The path with the parts that belong to whoever runs the probe replaced
    by placeholders, so that it can be published and applies to every user."""
    # The Store path is /capstor/store/<tenant>/<customer>/<group_id>, the names
    # defined in the Store documentation. The tenant is a property of the
    # platform (cscs on HPCP), the customer and group are not.
    match = re.match(r"^(/capstor/store/[^/]+)/", path)
    if FILESYSTEM_VARIABLES[variable][0] == "store" and match:
        return match.group(1) + "/<customer>/<group_id>"
    path = re.sub(r"/%s\b" % re.escape(system.user()), "/$USER", path)
    return re.sub(r"/%s\b" % re.escape(system.group()), "/$GROUP", path)


def build_filesystems(system, source, publish):
    # Group the variables by the path they point to, in the order listed.
    paths = OrderedDict()
    for variable in FILESYSTEM_VARIABLES:
        path = system.env(variable)
        if path:
            paths.setdefault(path, []).append(variable)

    items = []
    for path, variables in paths.items():
        variable = variables[0]
        if not system.exists(path):
            raise ProbeError("$%s points to %s, which does not exist" % (variable, path))
        # findmnt is used rather than `mount` because `mount` output contains
        # NFS server addresses and Lustre MGS NIDs, which must not be committed
        # to a public repository.
        found = system.run("findmnt-" + variable, ["findmnt", "--noheadings", "--output",
                                                   "TARGET,FSTYPE", "--target", path]).split()
        if len(found) != 2:
            raise ProbeError("findmnt does not report a mount for $%s (%s)" % (variable, path))
        mount, fstype = found
        for matches, storage, technology, expected in STORAGE_SYSTEMS:
            if matches(mount):
                break
        else:
            raise ProbeError("$%s is on unrecognised mount %s; add it to STORAGE_SYSTEMS in probes.py"
                             % (variable, mount))
        if fstype != expected:
            raise ProbeError("$%s is on %s with type %s, expected %s for %s"
                             % (variable, mount, fstype, expected, storage))
        filesystem, previous = FILESYSTEM_VARIABLES[variable]
        item = OrderedDict([
            ("variables", variables),
            ("filesystem", filesystem),
            ("previous_location", previous),
            ("path_template", path_template(system, variable, path)),
            ("storage", storage),
            ("technology", technology),
            ("fstype", fstype),
        ])
        if not publish:
            item["path"] = path
        items.append(item)
    return OrderedDict([("filesystems", items)])


# The names and links that the documentation uses for the file systems and the
# storage systems: (name, anchor), and the guide for the technology if any.
FILESYSTEM_DOCS = {
    "home": "[Home][ref-storage-home]",
    "scratch": "[Scratch][ref-storage-scratch]",
    "store": "[Store][ref-storage-store]",
}
STORAGE_DOCS = {
    "capstor": ("[Capstor][ref-alps-capstor]", "ref-guides-storage-lustre"),
    "iopsstor": ("[Iopsstor][ref-alps-iopsstor]", "ref-guides-storage-lustre"),
    "ritom": ("[Ritom][ref-alps-ritom]", "ref-guides-storage-vast-ritom"),
    "vadret": ("[Vadret][ref-alps-vadret]", None),
}


def filesystem_type(row):
    guide = STORAGE_DOCS[row["storage"]][1]
    return "[%s][%s]" % (row["technology"], guide) if guide else row["technology"]


FILESYSTEMS = Probe(
    name="filesystems",
    scope="config",
    description="The storage that $HOME, $SCRATCH and $STORE point to.",
    sources={
        "intended": "`findmnt -T` on the paths in `$HOME`, `$SCRATCH`, `$SCRATCH_OLD`, `$STORE` and `$PROJECT`",
        "live": "`findmnt -T` on the paths in `$HOME`, `$SCRATCH`, `$SCRATCH_OLD`, `$STORE` and `$PROJECT`",
    },
    build=build_filesystems,
    rows=lambda model: model["filesystems"],
    columns=[
        ("Variable", lambda row: ", ".join(code("$" + v) for v in row["variables"])),
        ("File system", lambda row: FILESYSTEM_DOCS[row["filesystem"]]
            + (" (previous location)" if row["previous_location"] else "")),
        ("Path", lambda row: code(row["path_template"])),
        ("Storage", lambda row: STORAGE_DOCS[row["storage"]][0]),
        ("Type", filesystem_type),
    ],
    fields=OrderedDict([
        ("filesystems[].variables", "Environment variables that point to the path."),
        ("filesystems[].filesystem", "The documented file system: home, scratch or store. "
                                     "Its quota, cleanup and backup policies are in the storage documentation."),
        ("filesystems[].previous_location", "True for a file system that has moved and is kept for migration."),
        ("filesystems[].path_template", "The path, with placeholders for the user, group and customer."),
        ("filesystems[].path", "The path for the person running the probe. Not published."),
        ("filesystems[].storage", "Alps storage system that hosts it: capstor, iopsstor, ritom or vadret."),
        ("filesystems[].technology", "Lustre or VAST."),
    ]),
)


# -- versions -----------------------------------------------------------------

def build_versions(system, source, publish):
    def output(name, argv):
        return system.run("version-" + name, argv, required=False).split()

    def word(words, index):
        return words[index] if words and -len(words) <= index < len(words) else None

    os_release = re.search(r'(?m)^PRETTY_NAME="(.*)"', system.read("os-release", "/etc/os-release"))
    tools = [
        ("slurm", "Slurm", word(output("slurm", ["sinfo", "--version"]), 1)),
        ("uenv", "uenv", word(output("uenv", ["uenv", "--version"]), 0)),
        ("container-engine", "Container engine", word(output("container-engine", ["sarusctl", "--version"]), -1)),
        ("enroot", "enroot", word(output("enroot", ["enroot", "version"]), 0)),
        ("podman", "podman", word(output("podman", ["podman", "--version"]), 2)),
        ("os", "Operating system", os_release.group(1) if os_release else None),
        ("kernel", "Kernel", word(output("kernel", ["uname", "-r"]), 0)),
        ("architecture", "Architecture", word(output("architecture", ["uname", "-m"]), 0)),
    ]
    return OrderedDict([("tools", [
        OrderedDict([("id", key), ("name", name), ("version", version)]) for key, name, version in tools
    ])])


VERSIONS = Probe(
    name="versions",
    scope="config",
    description="Versions of the tools that a job script or environment definition depends on.",
    sources={
        "intended": "the version output of each tool",
        "live": "the version output of each tool",
    },
    build=build_versions,
    rows=lambda model: model["tools"],
    columns=[
        ("Tool", lambda row: row["name"]),
        ("Version", lambda row: code(row["version"] or "not available")),
    ],
    fields=OrderedDict([
        ("tools[].id", "Stable identifier of the tool."),
        ("tools[].version", "Version installed for every user, or null if the tool is not available."),
    ]),
)


# -- usage (state) ------------------------------------------------------------

def build_usage(system, source, publish):
    partitions = slurm.load_partitions(system, "live")
    states = slurm.load_node_states(system.run("sinfo-states", slurm.SINFO_STATES))
    jobs = slurm.load_jobs(system.run("squeue-jobs", slurm.SQUEUE_JOBS))
    qos_usage = slurm.load_qos_usage(system.run("scontrol-qos-usage", slurm.SCONTROL_QOS_USAGE,
                                                required=False))

    items = []
    for partition in sorted(partitions, key=lambda p: p["name"]):
        name = partition["name"]
        if name not in states:
            continue
        counts = states[name]
        queue = jobs.get(name, {"running": 0, "pending": 0, "pending_reasons": {}})
        # The nodes that the QoS of the partition still allows its jobs to take.
        headroom = None
        if partition["qos"] in qos_usage:
            limit, used = qos_usage[partition["qos"]]
            headroom = OrderedDict([("qos", partition["qos"]), ("limit", limit), ("in_use", used),
                                    ("free", max(limit - used, 0))])
        items.append(OrderedDict([
            ("name", name),
            ("nodes", OrderedDict([
                ("total", sum(counts.values())),
                ("idle", counts.get("idle", 0)),
                ("by_state", OrderedDict(sorted(counts.items()))),
            ])),
            ("qos_nodes", headroom),
            ("jobs", OrderedDict([
                ("running", queue["running"]),
                ("pending", queue["pending"]),
                ("pending_reasons", OrderedDict(sorted(queue["pending_reasons"].items(),
                                                       key=lambda item: (-item[1], item[0])))),
            ])),
        ]))
    return OrderedDict([
        ("partitions", items),
        ("qos", OrderedDict(
            (name, OrderedDict([("limit", limit), ("in_use", used), ("free", max(limit - used, 0))]))
            for name, (limit, used) in sorted(qos_usage.items()))),
    ])


def usage_qos_cell(row):
    if not row["qos_nodes"]:
        return ""
    return "%d of %d" % (row["qos_nodes"]["in_use"], row["qos_nodes"]["limit"])


USAGE = Probe(
    name="usage",
    scope="state",
    description="What the cluster is doing now: idle nodes, how much of each QoS node limit is in use, "
                "and the running and pending jobs of each partition.",
    sources={"live": "`sinfo`, `squeue` and `scontrol show assoc_mgr flags=qos`"},
    build=build_usage,
    rows=lambda model: model["partitions"],
    columns=[
        ("Partition", lambda row: code(row["name"])),
        ("Nodes", lambda row: str(row["nodes"]["total"])),
        ("Idle nodes", lambda row: str(row["nodes"]["idle"])),
        ("QoS nodes in use", usage_qos_cell),
        ("Running jobs", lambda row: str(row["jobs"]["running"])),
        ("Pending jobs", lambda row: str(row["jobs"]["pending"])),
    ],
    fields=OrderedDict([
        ("partitions[].nodes.idle", "Nodes that are free now. Partitions can share nodes, so the same idle node "
                                    "can be counted in several partitions."),
        ("partitions[].nodes.by_state", "Number of nodes in each Slurm node state."),
        ("partitions[].qos_nodes", "Use of the node limit of the partition QoS, or null if it has none. "
                                   "When free is 0, new jobs wait with reason QOSGrpNodeLimit even if nodes are idle."),
        ("partitions[].jobs.pending_reasons", "Number of pending jobs for each reason that squeue gives, "
                                              "most common first. A job submitted to several partitions is "
                                              "counted in each."),
        ("qos.<name>", "Nodes in use against the group node limit of every QoS that has one."),
    ]),
)


# -- access (user) ------------------------------------------------------------

def build_access(system, source, publish):
    user = system.user()
    cluster = system.slurm_config().get("ClusterName") or system.cluster()
    accounts = slurm.load_assoc(system.run("sacctmgr-assoc", slurm.sacctmgr_assoc(user, cluster)))
    groups = set(system.groups())
    partitions = slurm.load_partitions(system, "live")
    qos = slurm.load_qos(system.run("sacctmgr-qos", slurm.SACCTMGR_QOS))

    items = []
    for partition in sorted(partitions, key=lambda p: p["name"]):
        name = partition["name"]
        allowed = [a for a in accounts
                   if a["partition"] in (None, name)
                   and (partition["allowaccounts"] is None or a["account"] in partition["allowaccounts"])]
        usable_qos = sorted(set(
            q for a in allowed for q in a["qos"]
            if partition["allowqos"] is None or q in partition["allowqos"]))
        open_qos = [q for q in usable_qos if q not in qos or not slurm.qos_blocked(qos[q])]

        reason = None
        if partition["allowgroups"] is not None and not groups & set(partition["allowgroups"]):
            reason = "the partition is restricted to Unix groups that the user is not in"
        elif not accounts:
            reason = "the user has no account on this cluster"
        elif not allowed:
            reason = "none of the user's accounts is allowed in the partition"
        elif not usable_qos:
            reason = "the user's accounts have none of the QoS that the partition allows: " \
                     + ", ".join(partition["allowqos"])
        elif not open_qos:
            reason = "the only QoS that the user can use here lets no job run: " + ", ".join(usable_qos)
        items.append(OrderedDict([
            ("name", name),
            ("can_submit", reason is None),
            ("reason", reason),
            ("accounts", [a["account"] for a in allowed] if reason is None else []),
            ("qos", open_qos if reason is None else []),
        ]))
    return OrderedDict([
        ("user", user),
        ("accounts", [OrderedDict([("account", a["account"]), ("partition", a["partition"]),
                                   ("qos", a["qos"]), ("default_qos", a["default_qos"])])
                      for a in accounts]),
        ("partitions", items),
    ])


ACCESS = Probe(
    name="access",
    scope="user",
    description="What the person running the probe can use: their accounts, and the partitions and QoS "
                "that they can submit to.",
    sources={"live": "`sacctmgr show assoc`, `scontrol show partition` and `id`"},
    build=build_access,
    rows=lambda model: model["partitions"],
    columns=[
        ("Partition", lambda row: code(row["name"])),
        ("Can submit", lambda row: "yes" if row["can_submit"] else "no"),
        ("Accounts", lambda row: ", ".join(code(a) for a in row["accounts"])),
        ("QoS", lambda row: ", ".join(code(q) for q in row["qos"])),
        ("Reason", lambda row: row["reason"] or ""),
    ],
    fields=OrderedDict([
        ("accounts[]", "The user's Slurm associations: an account (--account), and the QoS it can use."),
        ("accounts[].partition", "Partition that the association is restricted to, or null for all."),
        ("partitions[].can_submit", "Whether the user has an account and a QoS with which a job in the "
                                    "partition can run. It does not check the budget of the account."),
        ("partitions[].reason", "Why the user cannot submit, or null."),
        ("partitions[].accounts", "The user's accounts that the partition accepts."),
        ("partitions[].qos", "QoS that the user can pass to --qos in the partition."),
    ]),
)


PROBES = OrderedDict((probe.name, probe) for probe in
                     (PARTITIONS, NODETYPES, FILESYSTEMS, VERSIONS, USAGE, ACCESS))


def published():
    """The probes whose output is written to probes/generated/ and included in
    the documentation: configuration only, never state or anything about a
    user."""
    return [probe for probe in PROBES.values() if probe.scope == "config"]
