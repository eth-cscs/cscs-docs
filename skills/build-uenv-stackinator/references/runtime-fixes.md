# Fixing runtime issues

When a uenv builds successfully but packages fail at runtime, escalate through these approaches by root cause.

## 1. Missing files in the view

Only packages listed as explicit specs in `environments.yaml` (and their runtime dependencies) get linked into the view. If a transitive dependency's files are needed at runtime but missing, add it as an explicit spec.

Example: `shared-mime-info` is a runtime dependency of `gdk-pixbuf`, but GTK only finds its MIME database if it appears in `XDG_DATA_DIRS` — which requires it to be in the view. Adding it as an explicit spec fixes this.

## 2. Environment variables

Views can set environment variables via the view definition:

```yaml
  views:
    vnc:
      link: roots
      env:
        set:
          GDK_PIXBUF_MODULE_FILE: "{prefix}/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache"
        prepend_path:
          XDG_DATA_DIRS: "{prefix}/share"
```

These land in the view's `activate.sh` and are set when the uenv is loaded. `{prefix}` expands to the view prefix.

## 3. Post-install hook for deeper fixes

When environment variables aren't enough, use a `post-install` script for arbitrary modifications:
- Edit `meta/env.json` to modify view definitions or add environment variables.
- Delete or patch files in installed package prefixes.
- Add wrapper scripts or config files.

If the script modifies an installed package (not just adds files), you may need a clean rebuild rather than an incremental one.

The hook runs inside the sandbox after `env-meta` (so `meta/env.json` exists) and before the squashfs is built. It is Jinja-templated with `env.mount` (the store mount point), `env.build`, `env.config`, and `env.spack`. `spack` and `jq` are both available.

**Injecting a package's real prefix into a view.** The view symlink farm doesn't always surface everything a tool needs at run time — e.g. a compiler's offload sub-tools that get spawned via `PATH`, or a plugin `.so` loaded via `LD_LIBRARY_PATH`, both of which live in the package's own hash-prefixed prefix. Resolve that concrete prefix from the store DB and patch it into `meta/env.json`. Each view's variables live under `.views.<name>.env.values.list.<VAR>` as an array of `{"op": "prepend", "value": [ ... ]}` entries:

```bash
PREFIX=$(spack find --format "{prefix}" "<spec>")   # concrete store path (no env needed)
jq --arg bin "$PREFIX/bin" --arg lib "$PREFIX/lib64" '
  .views |= map_values(
    (if (.env.values.list.PATH?) and ((.env.values.list.PATH[0].value | index($bin)) | not)
       then .env.values.list.PATH[0].value += [$bin] else . end)
    | (if (.env.values.list.LD_LIBRARY_PATH?) and ((.env.values.list.LD_LIBRARY_PATH[0].value | index($lib)) | not)
       then .env.values.list.LD_LIBRARY_PATH[0].value += [$lib] else . end))
' "{{ env.mount }}/meta/env.json" > tmp && mv tmp "{{ env.mount }}/meta/env.json"
```

The `index(...) | not` guards make the edit idempotent — important because a hook may run more than once, and because it keeps re-runs during iteration clean. Write to a temp file and `mv` so a `jq` error can't truncate `env.json`.

## 4. Custom packages (last resort)

If the fault is in a Spack package's build logic (wrong configure flags, missing dependencies, broken install layout), a custom package in `repo/packages/` is appropriate. But first try the simpler, more maintainable options — a variant flag, an additional spec, or an external declaration.
