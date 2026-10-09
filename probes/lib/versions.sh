# Versions of the tools a job script or environment definition depends on.
emit_versions() {
    probe_header 'the version output of each tool'

    echo "| Tool | Version |"
    echo "|---|---|"
    _version_row "Slurm"            "$(sinfo --version 2>/dev/null | awk '{print $2}')"
    _version_row "uenv"             "$(uenv --version 2>/dev/null)"
    _version_row "Container engine" "$(sarusctl --version 2>/dev/null | awk '{print $NF}')"
    _version_row "enroot"           "$(enroot version 2>/dev/null)"
    _version_row "podman"           "$(podman --version 2>/dev/null | awk '{print $3}')"
    _version_row "Operating system" "$(sed -n 's/^PRETTY_NAME="\(.*\)"/\1/p' /etc/os-release)"
    _version_row "Kernel"           "$(uname -r)"
    _version_row "Architecture"     "$(uname -m)"
}

_version_row() {
    local name="$1" version="$2"
    [[ -n "$version" ]] || version="not available"
    printf '| %s | `%s` |\n' "$name" "$version"
}
