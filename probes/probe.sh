#!/usr/bin/env bash
#
# Describe a cluster: for the documentation, and for agents that help users on
# the system.
#
# With no options, generate the cluster configuration artifacts that the
# documentation build includes. Run this on a login node of the cluster you want
# to refresh, then commit the result.
#
#   ./probes/probe.sh
#   git diff probes/generated/
#
# With --live or --intended nothing is written: the named probes are printed,
# as markdown tables or as JSON with everything that the probe knows.
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

# Describe the system as every user sees it, not the environment of whoever runs
# the probe: a tool installed in the user's own path (a development build of
# uenv, say) would otherwise be reported as the system version.
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# -B: the checkout is shared between clusters, so leave no bytecode in it.
exec python3 -B "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/cli.py" "$@"
