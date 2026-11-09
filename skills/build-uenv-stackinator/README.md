# build-uenv-stackinator

An agent skill for building [uenv][https://docs.cscs.ch/software/uenv] software-stack images on CSCS Alps HPC systems using [stackinator][https://github.com/eth-cscs/stackinator]

## What it covers

- **Setting up from scratch** — the working directory, the three repos to clone, cribbing a recipe from `alps-uenv`, and writing `mirrors.yaml`.
- **The image format** — a uenv is an ordinary SquashFS file; what is inside one, and why the mount point is baked into its contents.
- **The build workflow** — configure with `stack-config`, build with `make store.squashfs`, and the fast iteration loop for prototyping changes.
- **Build notes convention** — read a recipe's `README.md` for prior gotchas before building, and record hard-won findings there after a successful build.
- **Debugging** — where sandbox log files really live, how to get a debug shell (`stack-debug.sh`), and how to inspect the store before repackaging.
- **Common issues** — concretization failures, missing externals, build-path restrictions, image-size reduction, and idempotency traps in custom packages.
- **Runtime fixes** — the escalation ladder from adding explicit specs → view env vars → post-install hooks → custom packages.
- **Testing** — exercising an image's headline feature end-to-end, not just checking that the build finished.

## Contents

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill definition and main instructions the agent follows. |
| `references/recipe-files.md` | Field-by-field reference for every recipe YAML file, with annotated examples. |
| `references/runtime-fixes.md` | Detailed remediation for images that build but fail at runtime. |
| `references/vnc-example.md` | Worked example: design decisions for a VNC/remote-visualization uenv on GH200. |

