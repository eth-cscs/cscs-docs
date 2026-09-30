#!/usr/bin/env bash
#
# Generate the cluster configuration artifacts that the documentation build
# includes. Run this on a login node of the cluster you want to refresh, then
# commit the result.
#
#   ./probes/probe.sh
#   git diff probes/generated/
#
# Two rules govern what this script emits:
#
#   1. Configuration, never state. Partition definitions and file system layout
#      change on a timescale of weeks, so an artifact stays correct between runs,
#      re-running produces an empty diff when nothing has changed, and a run
#      during a drain still captures the right thing. Live node and job counts
#      are deliberately excluded.
#
#   2. Redaction at the source. Only whitelisted fields are emitted, with user
#      and project identifiers substituted. See probe_redact in lib/common.sh.
#
# The script is read-only with respect to the cluster and submits no jobs.

set -euo pipefail

PROBE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROBE_ROOT

# shellcheck source=lib/common.sh
source "${PROBE_ROOT}/lib/common.sh"
for lib in "${PROBE_ROOT}"/lib/*.sh; do
    [[ "$lib" == */common.sh ]] || source "$lib"
done

PROBE_CLUSTER="$(probe_cluster)"
PROBE_EMITTERS_SHA="$(probe_emitters_sha)"
readonly PROBE_CLUSTER PROBE_EMITTERS_SHA

readonly OUTPUT_DIR="${PROBE_ROOT}/generated/${PROBE_CLUSTER}"
readonly MAX_AGE_DAYS=30

# artifact:emitter:source description, for the manifest
readonly ARTIFACTS=(
    "partitions.md:emit_partitions:scontrol show partition"
    "nodetypes.md:emit_nodetypes:sinfo"
    "filesystems.md:emit_filesystems:findmnt"
    "versions.md:emit_versions:tool version output"
)

main() {
    mkdir -p "$OUTPUT_DIR"

    for entry in "${ARTIFACTS[@]}"; do
        local file="${entry%%:*}"
        local rest="${entry#*:}"
        local emitter="${rest%%:*}"

        # Emit to a temporary file so that a failing probe leaves the committed
        # artifact untouched rather than truncated.
        local tmp
        tmp="$(mktemp "${OUTPUT_DIR}/.${file}.XXXXXX")"
        if "$emitter" > "$tmp"; then
            mv "$tmp" "${OUTPUT_DIR}/${file}"
            echo "writing probes/generated/${PROBE_CLUSTER}/${file}"
        else
            rm -f "$tmp"
            echo "FAILED  ${emitter}" >&2
            return 1
        fi
    done

    emit_stamp    > "${OUTPUT_DIR}/stamp.md"
    echo "writing probes/generated/${PROBE_CLUSTER}/stamp.md"
    emit_manifest > "${OUTPUT_DIR}/manifest.json"
    echo "writing probes/generated/${PROBE_CLUSTER}/manifest.json"
}

# The visible provenance line. This is the only artifact that carries a date, so
# that the content fragments produce empty diffs when nothing has changed, while
# a reader of the rendered page can still see how old the facts are.
emit_stamp() {
    printf '*Cluster configuration on this page was generated from the live system on %s.*\n' \
        "$(date -u +%F)"
}

emit_manifest() {
    local artifact_json=""
    for entry in "${ARTIFACTS[@]}"; do
        local file="${entry%%:*}"
        local source="${entry##*:}"
        [[ -z "$artifact_json" ]] || artifact_json+=","
        artifact_json+=$(printf '\n    "%s": { "source": "%s" }' "$file" "$source")
    done

    cat <<EOF
{
  "cluster": "${PROBE_CLUSTER}",
  "generated": "$(date -u +%F)",
  "host": "$(hostname)",
  "emitters_sha": "${PROBE_EMITTERS_SHA}",
  "max_age_days": ${MAX_AGE_DAYS},
  "artifacts": {${artifact_json}
  }
}
EOF
}

main "$@"
