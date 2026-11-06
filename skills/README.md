# Agent skills

Skills for coding agents (Claude Code, Codex, OpenCode, …) that CSCS publishes with the documentation.
Users install them from <https://docs.cscs.ch/agents/> (`docs/agents/index.md`).
How they are published and installed is explained in `docs/contributing/skills.md` (<https://docs.cscs.ch/contributing/skills/>); this file has the details needed to add or change a skill.

Each directory that contains a `SKILL.md` is one skill, in the [Agent Skills](https://agentskills.io) format.
The skills are kept in this repository so that a change to the documentation and the matching change to a skill are made, reviewed and published together.

## How a skill is published

`./build`, which CI runs to build the site, runs `skills/build.py` after zensical.
For each skill, it:

* checks the frontmatter of `SKILL.md`: `name` is the name of the directory, and is 1-64 lowercase letters, digits and single hyphens; `description` is at most 1024 characters;
* checks that the skill is named, in backticks, on `docs/agents/index.md`, so that users know what they install;
* copies the skill, and the files that its `bundle.json` names, to a temporary directory;
* runs the smoke test of `bundle.json` in that copy;
* packs the copy as `.well-known/agent-skills/<name>.tar.gz` in the site, with `SKILL.md` at the root of the archive;
* lists it, with the SHA-256 of the archive, in `.well-known/agent-skills/index.json`, which follows the [Agent Skills Discovery](https://github.com/cloudflare/agent-skills-discovery-rfc) draft.

The archives are reproducible: the same files give the same bytes, so the digest of a skill changes only when the skill does.
Don't put dates, build numbers or commit hashes in a skill.

`build.py` also publishes the committed `generated/clusters/<cluster>/results.json`, and a list of them in `generated/clusters/index.json`, for agents that cannot run the probes on a cluster.

## bundle.json

Optional. It names the files from elsewhere in the repository that the skill needs, and a command that tests the assembled skill:

```json
{
  "files": {
    "scripts/probe.sh": "probes/probe.sh",
    "scripts/lib": "probes/lib"
  },
  "smoke_test": ["scripts/probe.sh", "--list"]
}
```

* `files` maps a path in the skill to a file or directory in the repository.
  `__pycache__`, `*.pyc` and dotfiles are left out.
* `smoke_test` is run from the root of the repository.
  Its first element is a path in the assembled skill.
  A failure stops the build.

## Adding a skill

* Create `skills/<name>/SKILL.md`, and `bundle.json` if the skill needs files from elsewhere in the repository.
* In `SKILL.md`, refer to bundled files relative to the directory of the skill: users install it in `$XDG_DATA_HOME/cscs/skills/<name>/` (by default `~/.local/share/cscs/skills/<name>/`), linked from the skills directory of their agent, not in a checkout of this repository.
* Add the skill to the table on `docs/agents/index.md`.
* Run `./build` and `python3 -m unittest discover -s skills/tests`.
