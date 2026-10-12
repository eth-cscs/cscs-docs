#!/usr/bin/env bash
#
# Generate the cluster configuration artifacts that the documentation build
# includes. Run this on a login node of the cluster you want to refresh, then
# commit the result.
#
#   ./probes/probe.sh
#   git diff probes/generated/
#
# With --live, nothing is written: the same tables are printed for the system
# as it is running now, optionally only the named ones.
#
#   ./probes/probe.sh --live
#   ./probes/probe.sh --live partitions qos
#
# Three rules govern what this script emits:
#
#   1. Configuration, never state. Partition definitions and file system layout
#      change on a timescale of weeks, so an artifact stays correct between runs,
#      re-running produces an empty diff when nothing has changed, and a run
#      during a drain still captures the right thing. Live node and job counts
#      are deliberately excluded.
#
#   2. The intended configuration, for the documentation. The Slurm artifacts
#      are read from slurm.conf, so a partition or node that was changed on the
#      running system with `scontrol update` does not change the documentation.
#      The platform owners describe such a change in an admonition on the
#      cluster page. --live reads the running system instead.
#
#   3. Redaction at the source. Only whitelisted fields are emitted, with user
#      and project identifiers substituted. See probe_redact in lib/common.sh.
#
# The script is read-only with respect to the cluster and submits no jobs.

set -euo pipefail

# Describe the system as every user sees it, not the environment of whoever runs
# the probe: a tool installed in the user's own path (a development build of
# uenv, say) would otherwise be reported as the system version.
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

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

# intended (the default) or live: see lib/slurm.sh.
PROBE_SOURCE=intended

readonly OUTPUT_DIR="${PROBE_ROOT}/generated/${PROBE_CLUSTER}"
readonly MAX_AGE_DAYS=30

# artifact:emitter:source description, for the manifest
readonly ARTIFACTS=(
    "partitions.md:emit_partitions:slurm.conf and sacctmgr show qos"
    "qos.md:emit_qos:sacctmgr show qos and slurm.conf"
    "nodetypes.md:emit_nodetypes:slurm.conf"
    "filesystems.md:emit_filesystems:findmnt"
    "versions.md:emit_versions:tool version output"
)

usage() {
    echo "usage: probe.sh [--live [artifact...]]" >&2
    echo "artifacts: $(printf '%s\n' "${ARTIFACTS[@]}" | sed 's/\.md:.*//' | paste -sd' ')" >&2
}

# Print the artifacts for the system as it is running now. Nothing is written,
# so this can be run from a read-only checkout.
live() {
    local entry file name emitter found printed=""
    for name in "$@"; do
        found=""
        for entry in "${ARTIFACTS[@]}"; do
            [[ "${entry%%.md:*}" != "$name" ]] || found=1
        done
        if [[ -z "$found" ]]; then
            echo "probe.sh: unknown artifact '$name'" >&2
            usage
            return 1
        fi
    done
    for entry in "${ARTIFACTS[@]}"; do
        file="${entry%%:*}"
        name="${file%.md}"
        emitter="${entry#*:}"
        emitter="${emitter%%:*}"
        if [[ $# -gt 0 && " $* " != *" $name "* ]]; then
            continue
        fi
        [[ -z "$printed" ]] || echo
        "$emitter" || { echo "FAILED  ${emitter}" >&2; return 1; }
        printed=1
    done
}

main() {
    case "${1:-}" in
        --live)
            shift
            PROBE_SOURCE=live
            live "$@"
            return
            ;;
        "") ;;
        *)
            usage
            return 1
            ;;
    esac

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
    printf '*Cluster configuration on this page was generated from the configuration of the system on %s.*\n' \
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
