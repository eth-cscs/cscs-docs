# File systems visible on the cluster, and the environment variables that point
# into them.
#
# findmnt is used rather than `mount` because `mount` output contains NFS server
# addresses and Lustre MGS NIDs, which must not be committed to a public
# repository.
emit_filesystems() {
    probe_header '`findmnt`, and the environment set by `/etc/profile.d/cscs.sh`'

    echo "| Mount point | Type |"
    echo "|---|---|"
    findmnt --raw --noheadings --output TARGET,FSTYPE \
        | grep -E '^/(capstor|iopsstor|ritom|vast|users)' \
        | sort -u \
        | awk '{ printf "| `%s` | %s |\n", $1, $2 }'

    echo
    echo "| Variable | Path | Type |"
    echo "|---|---|---|"
    for var in HOME SCRATCH SCRATCH_OLD STORE PROJECT APPS; do
        local path="${!var:-}"
        [[ -n "$path" ]] || continue
        local fstype
        fstype="$(stat -f -c %T "$path" 2>/dev/null || echo unknown)"
        printf '| `$%s` | `%s` | %s |\n' "$var" "$(_display_path "$var" "$path")" "$fstype"
    done | probe_redact
}

# The Store path contains the tenant and customer for the project that generated
# it, which differ per project (userlab, swissai, 2go). Emit the documented
# pattern rather than one project's instance of it.
_display_path() {
    local var="$1" path="$2"
    if [[ "$var" == STORE || "$var" == PROJECT ]] && [[ "$path" == /capstor/store/* ]]; then
        echo '/capstor/store/<tenant>/<customer>/<group>'
    else
        echo "$path"
    fi
}
