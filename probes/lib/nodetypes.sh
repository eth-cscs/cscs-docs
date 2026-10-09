# Hardware per partition. SINFO_FORMAT is preset site-wide in
# /etc/profile.d/cscs.sh, so an explicit -o is required for stable output.
#
# Without --exact, sinfo merges nodes whose CPUs or memory differ into one line
# and prints the minimum with a "+" suffix (e.g. "241746+"). With it, nodes are
# only grouped when their resources are identical, and the grouping below merges
# rows whose memory differs by less than the rounding to GB, so that small
# per-node differences in configured memory do not split a node type.
#
# Features are the available ones (%f), not the active ones (%b): a node's active
# features depend on the options it was last booted with, which is state.
emit_nodetypes() {
    probe_header '`sinfo -o "%R|%D|%c|%m|%G|%f"`'
    sinfo --noheader --exact -o '%R|%D|%c|%m|%G|%f' | python3 -c '
import re, sys
from collections import OrderedDict

def memory(mb):
    return "%d GB" % round(int(mb) / 1024)

groups = OrderedDict()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    partition, nodes, cpus, mem_mb, gres, features = line.split("|")
    key = (partition.rstrip("*"), cpus, memory(mem_mb), gres, features)
    groups[key] = groups.get(key, 0) + int(nodes)

def gpus(gres):
    if gres in ("(null)", ""):
        return "none"
    # Drop the socket binding, e.g. gpu:4(S:0-3) -> gpu:4.
    return "`" + re.sub(r"\(S:[^)]*\)", "", gres) + "`"

def features(value):
    if value in ("(null)", ""):
        return "none"
    return ", ".join("`%s`" % f for f in sorted(value.split(",")))

print("| Partition | Nodes | CPUs per node | Memory per node | GPUs | Features |")
print("|---|---|---|---|---|---|")
for (partition, cpus, mem, gres, feat), nodes in sorted(groups.items()):
    print("| `%s` | %d | %s | %s | %s | %s |"
          % (partition, nodes, cpus, mem, gpus(gres), features(feat)))
'
}
