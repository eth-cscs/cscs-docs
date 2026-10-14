"""Collectors for Slurm: partitions, node types, QoS, and the state of the queue.

Partitions and node types can be read from two sources:

  intended  slurm.conf, the configuration that the platform owners deployed.
            This is what the documentation shows: it does not change when a
            partition or node is modified on the running system with
            `scontrol update`, so regenerating the docs is not affected by
            temporary changes.
  live      `scontrol show partition` and `sinfo`, what the scheduler is using
            at the moment. This is what an agent helping a user on the system
            needs.

QoS limits are stored in the accounting database, not in slurm.conf, so both
sources read them from `sacctmgr show qos`.

The collectors return the facts as Slurm states them. What they mean together
(for example, how many nodes the jobs of a partition can use) is worked out in
probes.py.

Runs on the login nodes, which provide Python 3.6: no f-strings.
"""
import os
import re
from collections import OrderedDict

from system import ProbeError


# -- slurm.conf ---------------------------------------------------------------

def split_top(expr):
    """Split a host list on the commas that are outside brackets."""
    items, depth, start = [], 0, 0
    for i, char in enumerate(expr):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
        elif char == "," and depth == 0:
            items.append(expr[start:i])
            start = i + 1
    items.append(expr[start:])
    return [item for item in items if item]


def expand(expr):
    """Expand a Slurm host list, e.g. nid[001-003,007] -> four names."""
    names = []
    for item in split_top(expr):
        match = re.match(r"^([^\[]*)\[([^\]]*)\](.*)$", item)
        if not match:
            names.append(item)
            continue
        head, ranges, tail = match.groups()
        for part in ranges.split(","):
            low, _, high = part.partition("-")
            high = high or low
            for i in range(int(low), int(high) + 1):
                names.extend(expand(head + str(i).zfill(len(low)) + tail))
    return names


def conf_lines(path):
    """Logical lines of slurm.conf: comments removed, continuations joined,
    Include directives followed."""
    pending = ""
    with open(path) as handle:
        for raw in handle:
            line = pending + raw.split("#", 1)[0].rstrip()
            if line.endswith("\\"):
                pending = line[:-1]
                continue
            pending = ""
            line = line.strip()
            if not line:
                continue
            match = re.match(r"(?i)^include\s+(\S+)$", line)
            if match:
                included = os.path.join(os.path.dirname(path), match.group(1))
                for inner in conf_lines(included):
                    yield inner
            else:
                yield line


def fields(line):
    """The key=value pairs of a line, with lower case keys, in order."""
    pairs = re.findall(r"(\w+)\s*=\s*(\"[^\"]*\"|\S*)", line)
    return OrderedDict((key.lower(), value.strip('"')) for key, value in pairs)


def node_cpus(attrs):
    if "cpus" in attrs:
        return attrs["cpus"]
    if "procs" in attrs:
        return attrs["procs"]
    total = 1
    for key in ("boards", "sockets", "corespersocket", "threadspercore"):
        total *= int(attrs.get(key, 1))
    if "sockets" not in attrs and "socketsperboard" in attrs:
        total *= int(attrs["socketsperboard"])
    return str(total)


def name_list(value):
    """A list of names, or None where Slurm applies no restriction (ALL)."""
    if value is None or value.upper() in ("ALL", "N/A", "(NULL)", ""):
        return None
    return [name for name in value.split(",") if name]


def partition(attrs, nodes, nodetypes):
    """One partition, from the fields of a slurm.conf line or of
    `scontrol show partition`, which use the same names."""
    def yes(key):
        return attrs.get(key, "NO").upper() == "YES"

    def upper(key):
        return attrs[key].upper() if attrs.get(key) else None

    qos = attrs.get("qos", "")
    return {
        "name": attrs["partitionname"],
        "default": yes("default"),
        "hidden": yes("hidden"),
        "nodes": nodes,
        "maxnodes": attrs.get("maxnodes", "UNLIMITED"),
        "defaulttime": attrs.get("defaulttime", "NONE"),
        "maxtime": attrs.get("maxtime", "UNLIMITED"),
        "allowqos": name_list(attrs.get("allowqos")),
        "qos": None if qos in ("", "N/A") else qos,
        "priority": int(attrs.get("prioritytier", 1)),
        "allowaccounts": name_list(attrs.get("allowaccounts")),
        "allowgroups": name_list(attrs.get("allowgroups")),
        "preemptmode": upper("preemptmode"),
        "oversubscribe": upper("oversubscribe") or upper("shared"),
        "nodetypes": nodetypes,
    }


def node_sockets(attrs):
    if "sockets" in attrs:
        return int(attrs["sockets"])
    return int(attrs.get("boards", 1)) * int(attrs.get("socketsperboard", 1))


def gpu_count(gres):
    """GPUs in a Gres value such as gpu:4, gpu:a100:4 or gpu:4(S:0-3)."""
    total = 0
    for item in split_top(re.sub(r"\([^)]*\)", "", gres or "")):
        parts = item.split(":")
        if parts[0] == "gpu" and len(parts) > 1 and parts[-1].isdigit():
            total += int(parts[-1])
    return total


def node_entry(name, attrs):
    """One node, from the fields of a slurm.conf line or of
    `scontrol show node`, which use the same names."""
    gres = attrs.get("gres", "")
    return {
        "name": name,
        "sockets": node_sockets(attrs),
        "cores_per_socket": int(attrs.get("corespersocket", 1)),
        "memory_mib": int(attrs.get("realmemory", 1)),
        "gres": "" if gres == "(null)" else gres,
    }


def read_conf(path):
    """The nodes, node sets and partition lines of slurm.conf, with the
    DEFAULT lines applied."""
    nodes = OrderedDict()       # name -> attributes
    nodesets = {}               # name -> fields
    partition_lines = []
    node_default, partition_default = {}, {}

    for line in conf_lines(path):
        attrs = fields(line)
        if not attrs:
            continue
        kind = next(iter(attrs))
        if kind == "nodename":
            if attrs["nodename"].upper() == "DEFAULT":
                node_default.update(attrs)
                continue
            merged = dict(node_default)
            merged.update(attrs)
            for name in expand(attrs["nodename"]):
                nodes[name] = merged
        elif kind == "nodeset":
            nodesets[attrs["nodeset"]] = attrs
        elif kind == "partitionname":
            if attrs["partitionname"].upper() == "DEFAULT":
                partition_default.update(attrs)
                continue
            merged = dict(partition_default)
            merged.update(attrs)
            partition_lines.append(merged)
    return nodes, nodesets, partition_lines


def load_conf_nodes(path):
    """Every node that slurm.conf defines, whether or not it is in a partition."""
    nodes, _, _ = read_conf(path)
    return [node_entry(name, attrs) for name, attrs in nodes.items()]


def load_conf(path):
    """Partitions and their node types as slurm.conf defines them."""
    nodes, nodesets, partition_lines = read_conf(path)

    def features(attrs):
        return attrs.get("feature", attrs.get("features", ""))

    def resolve(expr):
        members = OrderedDict()
        for item in split_top(expr):
            if item.upper() == "ALL":
                found = list(nodes)
            elif item in nodesets:
                nodeset = nodesets[item]
                if "nodes" in nodeset:
                    found = resolve(nodeset["nodes"])
                else:
                    wanted = nodeset.get("feature", "")
                    found = [n for n, a in nodes.items() if wanted in features(a).split(",")]
            else:
                found = expand(item)
            for name in found:
                members[name] = True
        return list(members)

    partitions = []
    for attrs in partition_lines:
        members = resolve(attrs.get("nodes", ""))
        nodetypes = OrderedDict()
        for member in members:
            if member not in nodes:
                raise ProbeError("partition %s uses node %s, which has no NodeName definition"
                                 % (attrs["partitionname"], member))
            node = nodes[member]
            key = (node_cpus(node), node.get("realmemory", "1"),
                   node.get("gres", ""), features(node), node.get("corespersocket", "1"))
            nodetypes[key] = nodetypes.get(key, 0) + 1
        partitions.append(partition(attrs, len(members), nodetypes))
    # Where more than one partition sets Default=YES, slurmctld uses the last.
    defaults = [p for p in partitions if p["default"]]
    for extra in defaults[:-1]:
        extra["default"] = False
    return partitions


# -- the running system -------------------------------------------------------

SCONTROL_PARTITIONS = ["scontrol", "show", "partition", "--oneliner"]

# SINFO_FORMAT is preset site-wide in /etc/profile.d/cscs.sh, so an explicit -o
# is required. Without --exact, sinfo merges nodes whose CPUs or memory differ
# and prints the minimum with a "+" suffix. Features are the available ones
# (%f), not the active ones (%b), which depend on the options a node was last
# booted with. The cores per socket (%Y) identify the Alps node type.
SINFO_NODETYPES = ["sinfo", "--noheader", "--exact", "-o", "%R|%D|%c|%m|%G|%f|%Y"]


def load_live(scontrol, sinfo=""):
    """Partitions as the scheduler reports them, with their node types if the
    output of SINFO_NODETYPES is given."""
    partitions = OrderedDict()
    for line in scontrol.splitlines():
        attrs = fields(line)
        if "partitionname" in attrs:
            partitions[attrs["partitionname"]] = partition(
                attrs, int(attrs.get("totalnodes", 0)), OrderedDict())
    for line in sinfo.splitlines():
        line = line.strip()
        if not line:
            continue
        name, count, cpus, memory, gres, features, cores = line.split("|")
        if name not in partitions:
            continue
        gres = "" if gres == "(null)" else re.sub(r"\(S:[^)]*\)", "", gres)
        features = "" if features == "(null)" else features
        nodetypes = partitions[name]["nodetypes"]
        key = (cpus, memory, gres, features, cores)
        nodetypes[key] = nodetypes.get(key, 0) + int(count)
    return list(partitions.values())


SCONTROL_NODES = ["scontrol", "show", "node", "--oneliner"]


def load_live_nodes(text):
    """Every node that the scheduler knows, from the output of SCONTROL_NODES."""
    nodes = []
    for line in text.splitlines():
        attrs = fields(line)
        if "nodename" in attrs:
            nodes.append(node_entry(attrs["nodename"], attrs))
    return nodes


def load_nodes(system, source):
    if source == "intended":
        nodes = load_conf_nodes(system.slurm_conf())
    else:
        nodes = load_live_nodes(system.run("scontrol-nodes", SCONTROL_NODES))
    if not nodes:
        raise ProbeError("no nodes found")
    return nodes


def load_partitions(system, source, nodetypes=False):
    if source == "intended":
        partitions = load_conf(system.slurm_conf())
    else:
        sinfo = system.run("sinfo-nodetypes", SINFO_NODETYPES) if nodetypes else ""
        partitions = load_live(system.run("scontrol-partition", SCONTROL_PARTITIONS), sinfo)
    if not partitions:
        raise ProbeError("no partitions found")
    return partitions


# -- QoS ----------------------------------------------------------------------

QOS_FORMAT = ("name", "grptres", "maxtres", "maxtrespu", "maxjobspu", "maxsubmitpu",
              "maxjobspa", "maxsubmitpa", "maxwall", "priority", "preempt")
SACCTMGR_QOS = ["sacctmgr", "-nP", "show", "qos", "format=" + ",".join(QOS_FORMAT)]


def tres_nodes(tres):
    match = re.search(r"(?:^|,)node=(\d+)", tres)
    return int(match.group(1)) if match else None


def load_qos(text):
    """The limits of every QoS, from the output of SACCTMGR_QOS."""
    def number(value):
        return int(value) if value else None

    qos = OrderedDict()
    for line in text.splitlines():
        if not line:
            continue
        values = dict(zip(QOS_FORMAT, line.split("|")))
        qos[values["name"]] = {
            "name": values["name"],
            "grp_nodes": tres_nodes(values["grptres"]),
            "job_nodes": tres_nodes(values["maxtres"]),
            "user_nodes": tres_nodes(values["maxtrespu"]),
            "user_jobs": number(values["maxjobspu"]),
            "user_submit": number(values["maxsubmitpu"]),
            "account_jobs": number(values["maxjobspa"]),
            "account_submit": number(values["maxsubmitpa"]),
            "maxwall": values["maxwall"] or None,
            "priority": number(values["priority"]),
            "preempt": name_list(values["preempt"]) or [],
        }
    return qos


def qos_blocked(qos):
    """A QoS that lets no job run, such as the one used to stop a project."""
    return 0 in (qos["user_jobs"], qos["user_submit"], qos["account_jobs"], qos["account_submit"])


SCONTROL_QOS_USAGE = ["scontrol", "show", "assoc_mgr", "flags=qos"]


def load_qos_usage(text):
    """Nodes held by the running jobs of each QoS that has a group limit on
    nodes, from the output of SCONTROL_QOS_USAGE: name -> (limit, in use)."""
    usage, name = OrderedDict(), None
    for line in text.splitlines():
        match = re.match(r"^QOS=(.+)\(\d+\)\s*$", line)
        if match:
            name = match.group(1)
            continue
        match = re.match(r"^\s+GrpTRES=.*?\bnode=(\d+)\((\d+)\)", line)
        if match and name:
            usage[name] = (int(match.group(1)), int(match.group(2)))
    return usage


# -- state --------------------------------------------------------------------

SINFO_STATES = ["sinfo", "--noheader", "-o", "%R|%T|%D"]
SQUEUE_JOBS = ["squeue", "--noheader", "-o", "%P|%T|%r"]


def load_node_states(text):
    """Nodes in each state for each partition: partition -> state -> count.
    The flags that sinfo appends to a state (such as * for not responding) are
    dropped."""
    states = OrderedDict()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        name, state, count = line.split("|")
        state = state.rstrip("*~#!%$@^-+")
        counts = states.setdefault(name, OrderedDict())
        counts[state] = counts.get(state, 0) + int(count)
    return states


def load_jobs(text):
    """Running and pending jobs of each partition. A pending job that was
    submitted to several partitions is counted in each of them."""
    jobs = OrderedDict()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        partitions, state, reason = line.split("|", 2)
        for name in partitions.split(","):
            entry = jobs.setdefault(name, {"running": 0, "pending": 0, "pending_reasons": {}})
            if state == "RUNNING":
                entry["running"] += 1
            elif state == "PENDING":
                entry["pending"] += 1
                entry["pending_reasons"][reason] = entry["pending_reasons"].get(reason, 0) + 1
    return jobs


# -- user ---------------------------------------------------------------------

def sacctmgr_assoc(user, cluster):
    return ["sacctmgr", "-nP", "show", "assoc", "where", "user=" + user, "cluster=" + cluster,
            "format=account,partition,qos,defaultqos"]


def load_assoc(text):
    """The accounts of a user, and the QoS that each can use."""
    accounts = []
    for line in text.splitlines():
        if not line:
            continue
        account, part, qos, default = line.split("|")
        accounts.append({
            "account": account,
            "partition": part or None,
            "qos": name_list(qos) or [],
            "default_qos": default or None,
        })
    return accounts
