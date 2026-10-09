# Slurm partition configuration: scheduling limits only, no live node state.
emit_partitions() {
    probe_header '`scontrol show partition`'
    scontrol show partition --oneliner | python3 -c '
import re, sys

COLUMNS = [
    ("PartitionName", "Partition",     "code"),
    ("TotalNodes",    "Nodes",         "plain"),
    ("MaxNodes",      "Max nodes/job", "plain"),
    ("DefaultTime",   "Default time",  "plain"),
    ("MaxTime",       "Max time",      "plain"),
    ("AllowQos",      "Allowed QoS",   "code"),
    ("PriorityTier",  "Priority",      "plain"),
]

def cell(key, value):
    if value in ("", "UNLIMITED", "NONE"):
        return {"": "", "UNLIMITED": "unlimited", "NONE": "none"}[value]
    return value

rows = []
for line in sys.stdin:
    if line.strip():
        rows.append(dict(re.findall(r"([A-Za-z]+)=(\S*)", line)))

print("| " + " | ".join(h for _, h, _ in COLUMNS) + " |")
print("|" + "---|" * len(COLUMNS))
for row in sorted(rows, key=lambda r: r.get("PartitionName", "")):
    cells = []
    for key, _, style in COLUMNS:
        value = cell(key, row.get(key, ""))
        if style == "code" and value:
            value = "`" + value + "`"
        if key == "PartitionName" and row.get("Default") == "YES":
            value += " (default)"
        cells.append(value)
    print("| " + " | ".join(cells) + " |")
'
}
