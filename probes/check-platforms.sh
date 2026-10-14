#!/usr/bin/env bash
#
# Check that the clusters of a platform produce the same platform-level
# artifacts.
#
# A platform page includes the reference cluster's copy of an artifact (see
# probes/platforms.json), which is only correct while every cluster of the
# platform agrees. Like check-freshness.sh, this reads committed files and needs
# no cluster access, so it runs in CI.
#
# Each other cluster of a platform has a severity:
#
#   critical  a difference from the reference cluster fails the check
#   warn      a difference is reported, and the check still passes
#
#   ./probes/check-platforms.sh

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
exec python3 - <<'PY'
import difflib, json, os, pathlib, sys

SEVERITIES = ("critical", "warn")

# In GitHub Actions, also emit annotations, so that a warning is visible on the
# pull request even though the job passes.
GITHUB = os.environ.get("GITHUB_ACTIONS") == "true"

counts = {severity: 0 for severity in SEVERITIES}

def problem(severity, message, path, diff=()):
    counts[severity] += 1
    print("%s: %s" % ("ERROR" if severity == "critical" else "WARNING", message))
    sys.stdout.writelines(diff)
    if GITHUB:
        print("::%s file=%s::%s" % ("error" if severity == "critical" else "warning", path, message))

def body(path):
    # Drop the header comment, which names the cluster it was generated on.
    lines = path.read_text().splitlines(keepends=True)
    end = next(i for i, line in enumerate(lines) if line.rstrip().endswith("-->"))
    return lines[end + 1:]

def includes(page, path):
    return any(line.lstrip().startswith("--8<--") and '"%s"' % path in line
               for line in page.read_text().splitlines())

config = pathlib.Path("probes/platforms.json")
platforms = json.loads(config.read_text())
for platform, spec in sorted(platforms.items()):
    reference = spec["reference"]
    page = pathlib.Path(spec["page"])
    for cluster, severity in sorted(spec["clusters"].items()):
        if severity not in SEVERITIES:
            problem("critical", "%s: severity of %s is %r, expected one of %s"
                    % (platform, cluster, severity, ", ".join(SEVERITIES)), config)

    for artifact in spec["artifacts"]:
        ref_path = pathlib.Path("probes/generated", reference, artifact)
        if not includes(page, ref_path):
            problem("critical", "%s: %s does not include the reference copy %s"
                    % (platform, page, ref_path), page)
        if not ref_path.exists():
            problem("critical", "%s: %s not generated on %s" % (platform, artifact, reference), ref_path)
            continue
        for cluster, severity in sorted(spec["clusters"].items()):
            path = pathlib.Path("probes/generated", cluster, artifact)
            if not path.exists():
                # Not yet probed: reported by check-freshness.sh, not a conflict.
                print("%s: %s not generated on %s, skipped" % (platform, artifact, cluster))
                continue
            diff = list(difflib.unified_diff(body(ref_path), body(path), str(ref_path), str(path)))
            if diff:
                problem(severity if severity in SEVERITIES else "critical",
                        "%s: %s differs between %s and %s" % (platform, artifact, reference, cluster),
                        path, diff)
            else:
                print("%s: %s agrees on %s and %s" % (platform, artifact, reference, cluster))

if counts["warn"]:
    print("\n%d warning(s): a cluster differs from its platform's reference cluster, which the"
          " platform page documents. These do not fail the check." % counts["warn"], file=sys.stderr)
if counts["critical"]:
    print("\n%d error(s). Where the clusters of a platform no longer agree, either the difference"
          " is a mistake on a cluster, or the artifact is no longer a platform-level fact and"
          " belongs on the cluster pages." % counts["critical"], file=sys.stderr)
sys.exit(1 if counts["critical"] else 0)
PY
