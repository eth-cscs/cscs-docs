# Slurm configuration: partitions, QoS limits and node types.
#
# There are two sources, selected by PROBE_SOURCE (see lib/slurm.py):
#
#   intended  slurm.conf, as deployed by the platform owners. The default, and
#             what the documentation includes: a partition or node that was
#             changed on the running system with `scontrol update` does not
#             change the generated tables.
#   live      `scontrol` and `sinfo`, what the scheduler is using now. Selected
#             with `probe.sh --live`, for use on the system itself.
#
# QoS limits are only stored in the accounting database, so both sources read
# them with sacctmgr.

# The slurm.conf that the Slurm commands on this node use.
probe_slurm_conf() {
    local conf
    conf="$(scontrol show config | awk '$1 == "SLURM_CONF" { print $3 }')" || return 1
    if [[ ! -r "$conf" ]]; then
        echo "probe_slurm_conf: cannot read slurm.conf (got '$conf')" >&2
        return 1
    fi
    echo "$conf"
}

# Emit one of the tables of lib/slurm.py: partitions, qos or nodetypes.
probe_slurm_table() {
    local table="$1" work conf status=0
    work="$(mktemp -d)" || return 1
    {
        sacctmgr -nP show qos format=name,grptres,maxtres,maxtrespu,maxjobspu,maxsubmitpu,maxwall > "$work/qos" &&
        if [[ "$PROBE_SOURCE" == live ]]; then
            # SINFO_FORMAT is preset site-wide in /etc/profile.d/cscs.sh, so an
            # explicit -o is required. Without --exact, sinfo merges nodes whose
            # CPUs or memory differ and prints the minimum with a "+" suffix.
            # Features are the available ones (%f), not the active ones (%b),
            # which depend on the options a node was last booted with.
            scontrol show partition --oneliner > "$work/scontrol" &&
            sinfo --noheader --exact -o '%R|%D|%c|%m|%G|%f' > "$work/sinfo" &&
            python3 "${PROBE_ROOT}/lib/slurm.py" "$table" --qos "$work/qos" \
                --scontrol "$work/scontrol" --sinfo "$work/sinfo"
        else
            conf="$(probe_slurm_conf)" &&
            python3 "${PROBE_ROOT}/lib/slurm.py" "$table" --qos "$work/qos" --conf "$conf"
        fi
    } || status=1
    rm -rf "$work"
    return "$status"
}

# The header names the source: $1 for the live system, $2 for the intended
# configuration.
probe_slurm_source() {
    if [[ "$PROBE_SOURCE" == live ]]; then
        echo "$1"
    else
        echo "$2"
    fi
}

# Scheduling limits of each partition. The node count is the pool of nodes that
# the partition can use; the QoS limits decide how many its jobs can hold.
emit_partitions() {
    probe_header "$(probe_slurm_source \
        '`scontrol show partition` and `sacctmgr show qos`' \
        '`slurm.conf` and `sacctmgr show qos`')"
    probe_slurm_table partitions
}

# Limits of each QoS that jobs in the partitions above can run under.
emit_qos() {
    probe_header "$(probe_slurm_source \
        '`sacctmgr show qos` and `scontrol show partition`' \
        '`sacctmgr show qos` and `slurm.conf`')"
    probe_slurm_table qos
}

# Hardware per partition.
emit_nodetypes() {
    probe_header "$(probe_slurm_source '`sinfo -o "%R|%D|%c|%m|%G|%f"`' '`slurm.conf`')"
    probe_slurm_table nodetypes
}
