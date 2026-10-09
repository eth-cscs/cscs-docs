# The storage that the standard environment variables point to, described with
# the names used in the storage documentation.
#
# The variables are the starting point, rather than the list of mounts: users
# and their tools reach storage through $SCRATCH, $STORE and $HOME, and many
# mounts (other tenants' Store, application areas) are not for general use.
#
# findmnt is used rather than `mount` because `mount` output contains NFS server
# addresses and Lustre MGS NIDs, which must not be committed to a public
# repository.
emit_filesystems() {
    probe_header '`findmnt -T` on the paths in `$HOME`, `$SCRATCH`, `$SCRATCH_OLD` and `$STORE`'

    echo "| Variable | File system | Path | Storage | Type |"
    echo "|---|---|---|---|---|"

    local var
    for var in HOME SCRATCH SCRATCH_OLD STORE; do
        local path="${!var:-}"
        [[ -n "$path" ]] || continue
        _filesystem_row "$var" "$path" || return 1
    done | probe_redact
}

# The documented file system that each variable provides.
_filesystem_concept() {
    case "$1" in
        HOME)        echo '[Home][ref-storage-home]' ;;
        SCRATCH)     echo '[Scratch][ref-storage-scratch]' ;;
        SCRATCH_OLD) echo '[Scratch][ref-storage-scratch] (previous location)' ;;
        STORE)       echo '[Store][ref-storage-store]' ;;
    esac
}

# Map a mount point to the Alps storage system that serves it, as
# "name|anchor|technology|expected fstype|guide anchor". The expected fstype
# guards the mapping: a path that is mounted differently than documented fails
# the probe instead of being described wrongly.
_storage_system() {
    case "$1" in
        /capstor/*)  echo 'Capstor|ref-alps-capstor|Lustre|lustre|ref-guides-storage-lustre' ;;
        /iopsstor/*) echo 'Iopsstor|ref-alps-iopsstor|Lustre|lustre|ref-guides-storage-lustre' ;;
        /ritom/*)    echo 'Ritom|ref-alps-ritom|VAST|nfs|ref-guides-storage-vast-ritom' ;;
        /users)      echo 'Vadret|ref-alps-vadret|VAST|nfs|' ;;
        *)           return 1 ;;
    esac
}

_filesystem_row() {
    local var="$1" path="$2"

    local mount fstype
    read -r mount fstype < <(findmnt --noheadings --output TARGET,FSTYPE --target "$path")

    local system
    if ! system="$(_storage_system "$mount")"; then
        echo "emit_filesystems: \$$var is on unrecognised mount $mount; add it to _storage_system" >&2
        return 1
    fi

    local name anchor technology expected guide
    IFS='|' read -r name anchor technology expected guide <<< "$system"
    if [[ "$fstype" != "$expected" ]]; then
        echo "emit_filesystems: \$$var is on $mount with type $fstype, expected $expected for $name" >&2
        return 1
    fi

    local type="$technology"
    [[ -z "$guide" ]] || type="[$technology][$guide]"

    printf '| `$%s` | %s | `%s` | [%s][%s] | %s |\n' \
        "$var" "$(_filesystem_concept "$var")" "$(_display_path "$var" "$path")" \
        "$name" "$anchor" "$type"
}

# The Store path is /capstor/store/<tenant>/<customer>/<project>. The tenant is
# a property of the platform (cscs on HPCP), but the customer and project belong
# to whoever runs the probe, so emit the placeholders that the storage docs use.
_display_path() {
    local var="$1" path="$2"
    if [[ "$var" == STORE ]] && [[ "$path" =~ ^(/capstor/store/[^/]+)/ ]]; then
        echo "${BASH_REMATCH[1]}/<customer>/<project>"
    else
        echo "$path"
    fi
}
