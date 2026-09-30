# Hardware per partition. SINFO_FORMAT is preset site-wide in
# /etc/profile.d/cscs.sh, so an explicit -o is required for stable output.
emit_nodetypes() {
    probe_header '`sinfo -o "%R|%D|%c|%m|%G|%b"`'
    sinfo --noheader -o '%R|%D|%c|%m|%G|%b' | python3 -c '
import sys
from collections import OrderedDict

groups = OrderedDict()
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    partition, nodes, cpus, mem_mb, gres, features = line.split("|")
    key = (partition.rstrip("*"), cpus, mem_mb, gres, features)
    groups[key] = groups.get(key, 0) + int(nodes)

def memory(mb):
    return "%d GB" % round(int(mb) / 1024)

def gpus(gres):
    if gres in ("(null)", ""):
        return "none"
    return "`" + gres + "`"

def features(value):
    if value in ("(null)", ""):
        return "none"
    return ", ".join("`%s`" % f for f in sorted(value.split(",")))

print("| Partition | CPUs per node | Memory per node | GPUs | Active features |")
print("|---|---|---|---|---|")
for (partition, cpus, mem_mb, gres, feat), nodes in sorted(groups.items()):
    print("| `%s` | %s | %s | %s | %s |"
          % (partition, cpus, memory(mem_mb), gpus(gres), features(feat)))
'
}
