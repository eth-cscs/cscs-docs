#!/usr/bin/env bash
#
# Check that the clusters of a platform produce the same platform-level
# artifacts.
#
# A platform page includes one cluster's copy of an artifact (see
# probes/platforms.json), which is only correct while every cluster of the
# platform agrees. Like check-freshness.sh, this reads committed files and needs
# no cluster access, so it runs in CI.
#
#   ./probes/check-platforms.sh

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python3 - <<'PY'
import difflib, json, pathlib, sys

def body(path):
    # Drop the header comment, which names the cluster it was generated on.
    lines = path.read_text().splitlines(keepends=True)
    end = next(i for i, line in enumerate(lines) if line.rstrip().endswith("-->"))
    return lines[end + 1:]

platforms = json.loads(pathlib.Path("probes/platforms.json").read_text())
failed = False
for platform, spec in sorted(platforms.items()):
    reference, *others = spec["clusters"]
    for artifact in spec["artifacts"]:
        ref_path = pathlib.Path("probes/generated", reference, artifact)
        if not ref_path.exists():
            print("%s: %s not generated on %s" % (platform, artifact, reference))
            failed = True
            continue
        for cluster in others:
            path = pathlib.Path("probes/generated", cluster, artifact)
            if not path.exists():
                # Not yet probed: reported by check-freshness.sh, not a conflict.
                print("%s: %s not generated on %s, skipped" % (platform, artifact, cluster))
                continue
            diff = list(difflib.unified_diff(body(ref_path), body(path), str(ref_path), str(path)))
            if diff:
                print("%s: %s differs between %s and %s" % (platform, artifact, reference, cluster))
                sys.stdout.writelines(diff)
                failed = True
            else:
                print("%s: %s agrees on %s and %s" % (platform, artifact, reference, cluster))

if failed:
    print("\nThe clusters of a platform no longer agree. Either the difference is a"
          " mistake on a cluster, or the artifact is no longer a platform-level fact"
          " and belongs on the cluster pages.", file=sys.stderr)
sys.exit(1 if failed else 0)
PY
