#!/usr/bin/env python3
"""Render the Slurm tables for probe.sh.

The tables can be built from two sources:

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

Runs on the login nodes, which provide Python 3.6: no f-strings.
"""
import argparse
import os
import re
import sys
from collections import OrderedDict

UNLIMITED = "unlimited"


def fail(message):
    sys.stderr.write("slurm.py: %s\n" % message)
    sys.exit(1)


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


def load_conf(path):
    """Partitions and node types as slurm.conf defines them."""
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

    def features(attrs):
        return attrs.get("feature", attrs.get("features", ""))

    def resolve(expr):
        names = OrderedDict()
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
                names[name] = True
        return list(names)

    partitions = []
    for attrs in partition_lines:
        name = attrs["partitionname"]
        members = resolve(attrs.get("nodes", ""))
        nodetypes = OrderedDict()
        for member in members:
            if member not in nodes:
                fail("partition %s uses node %s, which has no NodeName definition" % (name, member))
            node = nodes[member]
            key = (node_cpus(node), node.get("realmemory", "1"),
                   node.get("gres", ""), features(node))
            nodetypes[key] = nodetypes.get(key, 0) + 1
        partitions.append({
            "name": name,
            "default": attrs.get("default", "NO").upper() == "YES",
            "hidden": attrs.get("hidden", "NO").upper() == "YES",
            "nodes": len(members),
            "maxnodes": attrs.get("maxnodes", "UNLIMITED"),
            "defaulttime": attrs.get("defaulttime", "NONE"),
            "maxtime": attrs.get("maxtime", "UNLIMITED"),
            "allowqos": attrs.get("allowqos", "ALL"),
            "qos": attrs.get("qos", ""),
            "priority": attrs.get("prioritytier", "1"),
            "nodetypes": nodetypes,
        })
    return partitions


# -- the running system -------------------------------------------------------

def load_live(scontrol_path, sinfo_path):
    """Partitions and node types as the scheduler reports them."""
    partitions = OrderedDict()
    with open(scontrol_path) as handle:
        for line in handle:
            attrs = fields(line)
            if "partitionname" not in attrs:
                continue
            qos = attrs.get("qos", "")
            partitions[attrs["partitionname"]] = {
                "name": attrs["partitionname"],
                "default": attrs.get("default") == "YES",
                "hidden": attrs.get("hidden") == "YES",
                "nodes": int(attrs.get("totalnodes", 0)),
                "maxnodes": attrs.get("maxnodes", "UNLIMITED"),
                "defaulttime": attrs.get("defaulttime", "NONE"),
                "maxtime": attrs.get("maxtime", "UNLIMITED"),
                "allowqos": attrs.get("allowqos", "ALL"),
                "qos": "" if qos == "N/A" else qos,
                "priority": attrs.get("prioritytier", "1"),
                "nodetypes": OrderedDict(),
            }
    if sinfo_path:
        # sinfo -o "%R|%D|%c|%m|%G|%f"
        with open(sinfo_path) as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                name, count, cpus, memory, gres, features = line.split("|")
                if name not in partitions:
                    continue
                gres = "" if gres == "(null)" else re.sub(r"\(S:[^)]*\)", "", gres)
                features = "" if features == "(null)" else features
                nodetypes = partitions[name]["nodetypes"]
                key = (cpus, memory, gres, features)
                nodetypes[key] = nodetypes.get(key, 0) + int(count)
    return list(partitions.values())


# -- QoS ----------------------------------------------------------------------

QOS_FORMAT = ("name", "grptres", "maxtres", "maxtrespu", "maxjobspu", "maxsubmitpu", "maxwall")


def tres_nodes(tres):
    match = re.search(r"(?:^|,)node=(\d+)", tres)
    return int(match.group(1)) if match else None


def load_qos(path):
    """sacctmgr -nP show qos format=<QOS_FORMAT>"""
    qos = OrderedDict()
    with open(path) as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line:
                continue
            values = dict(zip(QOS_FORMAT, line.split("|")))
            qos[values["name"]] = {
                "name": values["name"],
                "grp_nodes": tres_nodes(values["grptres"]),
                "job_nodes": tres_nodes(values["maxtres"]),
                "user_nodes": tres_nodes(values["maxtrespu"]),
                "user_jobs": int(values["maxjobspu"]) if values["maxjobspu"] else None,
                "user_submit": int(values["maxsubmitpu"]) if values["maxsubmitpu"] else None,
                "maxwall": values["maxwall"],
            }
    return qos


def blocked(qos):
    """A QoS that lets no job run, such as the one used to stop a project."""
    return qos["user_jobs"] == 0 or qos["user_submit"] == 0


def partition_qos(partition, qos):
    name = partition["qos"]
    if not name:
        return None
    if name not in qos:
        fail("partition %s uses QoS %s, which sacctmgr does not report" % (partition["name"], name))
    return qos[name]


def nodes_in_use(partition, qos):
    """The most nodes that the jobs of a partition can hold at the same time.

    A partition can list far more nodes than its jobs may use together: the
    limit is then a group limit (GrpTRES) on the partition QoS, or on the only
    QoS that jobs in the partition are allowed to use.
    """
    limit = partition["nodes"]
    own = partition_qos(partition, qos)
    if own and own["grp_nodes"] is not None:
        limit = min(limit, own["grp_nodes"])
    if partition["allowqos"].upper() != "ALL":
        allowed = [qos[n] for n in partition["allowqos"].split(",") if n in qos]
        usable = [q for q in allowed if not blocked(q)]
        if usable and all(q["grp_nodes"] is not None for q in usable):
            limit = min(limit, sum(q["grp_nodes"] for q in usable))
    return limit


def nodes_per_job(partition, qos):
    limit = partition["maxnodes"]
    own = partition_qos(partition, qos)
    if own and own["job_nodes"] is not None:
        if limit.upper() in ("UNLIMITED", "INFINITE") or own["job_nodes"] < int(limit):
            limit = str(own["job_nodes"])
    return limit


# -- rendering ----------------------------------------------------------------

def slurm_time(value):
    """Normalise a time limit to the form Slurm prints, [days-]hh:mm:ss."""
    upper = value.upper()
    if upper in ("UNLIMITED", "INFINITE"):
        return UNLIMITED
    if upper in ("NONE", ""):
        return "none"
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


def count(value):
    if value is None:
        return ""
    if str(value).upper() in ("UNLIMITED", "INFINITE"):
        return UNLIMITED
    return str(value)


def table(header, rows):
    print("| " + " | ".join(header) + " |")
    print("|" + "---|" * len(header))
    for row in rows:
        print("| " + " | ".join(row) + " |")


def visible(partitions):
    return sorted((p for p in partitions if not p["hidden"]), key=lambda p: p["name"])


def render_partitions(partitions, qos):
    rows = []
    for partition in visible(partitions):
        name = "`%s`" % partition["name"]
        if partition["default"]:
            name += " (default)"
        rows.append([
            name,
            str(partition["nodes"]),
            str(nodes_in_use(partition, qos)),
            count(nodes_per_job(partition, qos)),
            slurm_time(partition["defaulttime"]),
            slurm_time(partition["maxtime"]),
            "`%s`" % partition["allowqos"],
            partition["priority"],
        ])
    table(["Partition", "Nodes", "Max nodes in use", "Max nodes/job", "Default time",
           "Max time", "Allowed QoS", "Priority"], rows)


def render_qos(partitions, qos):
    """The limits of each QoS that a job in a visible partition can run under."""
    rows = []
    for name, entry in sorted(qos.items()):
        every_job, on_request = [], []
        for partition in visible(partitions):
            if partition["qos"] == name:
                every_job.append(partition["name"])
            allowed = partition["allowqos"].split(",")
            if name in allowed:
                on_request.append(partition["name"])
        if not every_job and not on_request:
            continue
        limits = [entry["grp_nodes"], entry["job_nodes"], entry["user_nodes"],
                  entry["user_jobs"], entry["user_submit"]]
        if all(limit is None for limit in limits) and not entry["maxwall"]:
            continue
        applies = []
        if every_job:
            applies.append("every job in " + ", ".join("`%s`" % p for p in every_job))
        if on_request:
            applies.append("jobs that use it in " + ", ".join("`%s`" % p for p in on_request))
        rows.append(["`%s`" % name, "; ".join(applies)]
                    + [count(limit) for limit in limits]
                    + [slurm_time(entry["maxwall"]) if entry["maxwall"] else ""])
    table(["QoS", "Applies to", "Max nodes in use", "Max nodes/job", "Max nodes/user",
           "Running jobs/user", "Submitted jobs/user", "Max time"], rows)


def render_nodetypes(partitions):
    # Nodes whose configured memory differs by less than the rounding to GB are
    # one node type, so small per-node differences do not split a row.
    groups = {}
    for partition in visible(partitions):
        for (cpus, memory, gres, features), nodes in partition["nodetypes"].items():
            key = (partition["name"], cpus, "%d GB" % round(int(memory) / 1024.0), gres, features)
            groups[key] = groups.get(key, 0) + nodes
    rows = []
    for (name, cpus, memory, gres, features), nodes in sorted(groups.items()):
        rows.append([
            "`%s`" % name,
            str(nodes),
            cpus,
            memory,
            "`%s`" % gres if gres else "none",
            ", ".join("`%s`" % f for f in sorted(features.split(","))) if features else "none",
        ])
    table(["Partition", "Nodes", "CPUs per node", "Memory per node", "GPUs", "Features"], rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("table", choices=["partitions", "qos", "nodetypes"])
    parser.add_argument("--conf", help="slurm.conf (intended configuration)")
    parser.add_argument("--scontrol", help="output of scontrol show partition --oneliner (live)")
    parser.add_argument("--sinfo", help="output of sinfo -o '%%R|%%D|%%c|%%m|%%G|%%f' (live)")
    parser.add_argument("--qos", help="output of sacctmgr -nP show qos format=" + ",".join(QOS_FORMAT))
    args = parser.parse_args()

    if args.conf:
        partitions = load_conf(args.conf)
    elif args.scontrol:
        partitions = load_live(args.scontrol, args.sinfo)
    else:
        parser.error("one of --conf and --scontrol is required")
    if not partitions:
        fail("no partitions found")

    if args.table == "nodetypes":
        render_nodetypes(partitions)
        return
    if not args.qos:
        parser.error("--qos is required for the %s table" % args.table)
    qos = load_qos(args.qos)
    if args.table == "partitions":
        render_partitions(partitions, qos)
    else:
        render_qos(partitions, qos)


if __name__ == "__main__":
    main()
