#!/usr/bin/env bash
#
# Report the age of each generated cluster configuration artifact set.
#
# This runs anywhere: it reads the committed manifests and needs no access to a
# cluster. It is the counterpart to probe.sh, which can only be run on a cluster
# by a person. CI cannot refresh the artifacts, but it can say which cluster is
# overdue.
#
#   ./probes/check-freshness.sh

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python3 - <<'PY'
import datetime, glob, json, os, pathlib, sys

# Artifacts older than max_age_days (declared per cluster in the manifest, 30 by
# default, matching the monthly maintenance cadence) are reported stale. Twice
# that is treated as a failure, so that a single missed month warns without
# blocking work.
FAILURE_MULTIPLIER = 2

today = datetime.date.today()
rows, failed = [], False

generated = sorted(glob.glob("probes/generated/*/manifest.json"))
for path in generated:
    manifest = json.loads(pathlib.Path(path).read_text())
    cluster = manifest["cluster"]
    max_age = manifest.get("max_age_days", 30)
    age = (today - datetime.datetime.strptime(manifest["generated"], "%Y-%m-%d").date()).days

    if age > max_age * FAILURE_MULTIPLIER:
        status, failed = "STALE", True
    elif age > max_age:
        status = "overdue"
    else:
        status = "ok"
    rows.append((cluster, "%d days" % age, "%d days" % max_age, status))

# A cluster with a documentation page but no artifacts has never had the probes
# run on it. Reported for information only: it must not fail the build, or the
# check would be red until every cluster has been visited.
documented = {pathlib.Path(p).stem for p in glob.glob("docs/clusters/*.md")} - {"index"}
for cluster in sorted(documented - {json.loads(pathlib.Path(p).read_text())["cluster"]
                                   for p in generated}):
    rows.append((cluster, "-", "-", "not generated"))

width = max(len(r[0]) for r in rows) if rows else 8
print("%-*s  %9s  %9s  %s" % (width, "cluster", "age", "threshold", "status"))
for cluster, age, threshold, status in rows:
    print("%-*s  %9s  %9s  %s" % (width, cluster, age, threshold, status))

if failed:
    print("\nRun ./probes/probe.sh on the cluster(s) marked STALE and commit the result.",
          file=sys.stderr)
sys.exit(1 if failed else 0)
PY
