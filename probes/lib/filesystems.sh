# The storage that the standard environment variables point to, described with
# the names used in the storage documentation.
#
# The variables are the starting point, rather than the list of mounts: users
# and their tools reach storage through $SCRATCH, $STORE and $HOME, and many
# mounts (other tenants' Store, application areas) are not for general use.
# Variables that point to the same path ($STORE and $PROJECT) share a row, so
# that every name the docs use appears without repeating the storage.
#
# findmnt is used rather than `mount` because `mount` output contains NFS server
# addresses and Lustre MGS NIDs, which must not be committed to a public
# repository.
emit_filesystems() {
    probe_header '`findmnt -T` on the paths in `$HOME`, `$SCRATCH`, `$SCRATCH_OLD`, `$STORE` and `$PROJECT`'

    echo "| Variable | File system | Path | Storage | Type |"
    echo "|---|---|---|---|---|"

    # Group the variables by the path they point to, in the order listed.
    local var path i
    local -a paths=() groups=()
    for var in HOME SCRATCH SCRATCH_OLD STORE PROJECT; do
        path="${!var:-}"
        [[ -n "$path" ]] || continue
        for i in "${!paths[@]}"; do
            if [[ "${paths[$i]}" == "$path" ]]; then
                groups[$i]+=" $var"
                continue 2
            fi
        done
        paths+=("$path")
        groups+=("$var")
    done

    for i in "${!paths[@]}"; do
        _filesystem_row "${paths[$i]}" ${groups[$i]} || return 1
    done | probe_redact
}

# The documented file system that each variable provides.
_filesystem_concept() {
    case "$1" in
        HOME)        echo '[Home][ref-storage-home]' ;;
        SCRATCH)     echo '[Scratch][ref-storage-scratch]' ;;
        SCRATCH_OLD) echo '[Scratch][ref-storage-scratch] (previous location)' ;;
        STORE|PROJECT) echo '[Store][ref-storage-store]' ;;
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

# One row for a path, and the variables (one or more) that point to it.
_filesystem_row() {
    local path="$1"; shift
    local var="$1"
    local label
    label="$(printf '`$%s`, ' "$@")"
    label="${label%, }"

    if [[ ! -e "$path" ]]; then
        echo "emit_filesystems: \$$var points to $path, which does not exist" >&2
        return 1
    fi

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

    printf '| %s | %s | `%s` | [%s][%s] | %s |\n' \
        "$label" "$(_filesystem_concept "$var")" "$(_display_path "$var" "$path")" \
        "$name" "$anchor" "$type"
}

# The Store path is /capstor/store/<tenant>/<customer>/<group_id>, the names
# defined in the Store documentation. The tenant is a property of the platform
# (cscs on HPCP), but the customer and group belong to whoever runs the probe,
# so emit those as placeholders.
_display_path() {
    local var="$1" path="$2"
    if [[ "$var" == STORE || "$var" == PROJECT ]] && [[ "$path" =~ ^(/capstor/store/[^/]+)/ ]]; then
        echo "${BASH_REMATCH[1]}/<customer>/<group_id>"
    else
        echo "$path"
    fi
}
