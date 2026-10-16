#!/usr/bin/env bash
#
# Describe a cluster: for the documentation, and for agents that help users on
# the system.
#
# With no options, generate the cluster configuration artifacts used to generate
# the docs.
# Run on a login node of a cluster, then commit the result:
#
#   ./probes/probe.sh
#   git diff probes/generated/
#
# The --live or --intended write generate output to stdout. output is printed
# as markdown tables or as JSON:
#
#   ./probes/probe.sh --list
#   ./probes/probe.sh --live --format json partitions usage access
#   ./probes/probe.sh --intended partitions
#
# Three rules govern what is written for the documentation:
#
#   1. Configuration, never state. Partition definitions and file system layout
#      change on a timescale of weeks, so an artifact stays correct between runs,
#      re-running produces an empty diff when nothing has changed, and a run
#      during a drain still captures the right thing. Probes of the state of the
#      system, and of what a user can do, are only ever printed.
#
#   2. The intended configuration. The Slurm artifacts are read from slurm.conf,
#      so a partition or node that was changed on the running system with
#      `scontrol update` does not change the documentation. The platform owners
#      describe such a change in an admonition on the cluster page. --live reads
#      the running system instead.
#
#   3. Redaction at the source. Fields that identify users and projects are not
#      written, and paths are written with placeholders. See `publish` in
#      lib/probes.py.
#
# The script is read-only with respect to the cluster and submits no jobs. The
# probes are in lib/probes.py.

set -euo pipefail

# Use the default search paths to avoid poluting results with user-specific
# customizations (e.g. custom uenv build in $HOME/.local/bin)
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# -B: generate no bytecode in case the checkout is shared between clusters
exec python3 -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/cli.py" "$@"
