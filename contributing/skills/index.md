# Publishing agent skills

CSCS publishes agent skills with the documentation. This page explains how they are built, published and installed, for contributors and for users who want to know what they are installing.

The details needed to add or change a skill are in [`skills/README.md`](<https://github.com/eth-cscs/cscs-docs/blob/main/skills/README.md>), next to the code.

## Why the skills are in this repository

The skills and the documentation describe the same systems. For example, the partition tables on the cluster pages and the answers of the `cscs-cluster-probes` skill both come from the probes in `probes/`. Keeping the skills in this repository means that a change to the documentation and the matching change to a skill are made, reviewed and published together, so the two do not drift apart.

## The skill format

Each skill is a directory in `skills/` in the [Agent Skills](<https://agentskills.io/specification>) format: a `SKILL.md` file with a name and a description in its frontmatter, followed by instructions for the agent. A skill can also contain scripts and other files. The format is read by Claude Code, Codex, OpenCode and other agents.

A skill can use files from elsewhere in the repository, which are copied into it when it is published. The `cscs-cluster-probes` skill, for example, carries a copy of `probes/probe.sh`, so that users do not need a copy of this repository to run it.

## How skills are published

The site is built by the `build` script in the root of the repository, which CI runs for every pull request and every change to `main`:

build the complete site

```bash
./build
```

It builds the documentation with Zensical, then runs `skills/build.py`, which adds the skills to the site:

| Path on the site | Contents |
| --- | --- |
| `/.well-known/agent-skills/index.json` | the list of skills, with the URL and digest of each archive |
| `/.well-known/agent-skills/<skill>.tar.gz` | one archive per skill, with `SKILL.md` at its root |
| `/.well-known/agent-skills/<skill>/SKILL.md` | the instructions of each skill, to read before installing it |
| `/generated/clusters/index.json` | the clusters whose configuration is published |
| `/generated/clusters/<cluster>/results.json` | the configuration of a cluster, for agents that cannot run the probes on it |

The `/.well-known/` path prefix is reserved for files that describe a site, so that clients can find them without being told where they are (see [RFC 8615](<https://www.rfc-editor.org/rfc/rfc8615>)). The layout of `/.well-known/agent-skills/` follows the [Agent Skills Discovery RFC](<https://github.com/cloudflare/agent-skills-discovery-rfc>) proposed by Cloudflare, which is still a draft. Few agents read it yet, and the installation instructions do not depend on it, but it lets tools that do support it find the skills given only the address of the site.

Before a skill is published, the build checks it, and stops if:

- the frontmatter of `SKILL.md` is invalid, or the name of the skill is not the name of its directory;
- a file that the skill needs from elsewhere in the repository does not exist;
- the skill fails its own test, which runs the assembled skill as a user would;
- the skill is not listed on the agent skills page, where users choose what to install.

The archives are reproducible: building the same files gives the same bytes. So the digest of a skill, the SHA-256 of its archive, changes only when the skill changes, and serves as its version: an installed skill is up to date if its digest matches the one in `index.json`.

## How users install skills

Skills are never installed or enabled automatically: CSCS does not set environment variables or change configuration files that would make an agent load them. Users choose which skills to install, by following the agent skills page, or by asking their agent to follow it. The page contains instructions for agents, which tell them to show the user what they will install and where, and to ask before changing anything.

Each agent looks for skills in its own directory:

| Agent | Directory | Documentation |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | [Skills](<https://code.claude.com/docs/en/skills>) |
| Codex | `~/.agents/skills/` | [Build skills](<https://learn.chatgpt.com/docs/build-skills>) |
| OpenCode | `~/.config/opencode/skills/`, `~/.agents/skills/` or `~/.claude/skills/` | [Agent skills](<https://opencode.ai/docs/skills/>) |

Rather than copying a skill into each of these directories, it is installed once in the data directory defined by the [XDG Base Directory Specification](<https://specifications.freedesktop.org/basedir-spec/latest/>), `$XDG_DATA_HOME/cscs/skills/<skill>/` (by default `~/.local/share/cscs/skills/<skill>/`), and linked from the directories of the agents that the user uses. All three agents follow such links. On Alps, the home directory is shared by all clusters, so one installation serves all of them.

The digest of the installed archive is kept in the `.digest` file of the skill, so that an agent can tell whether an update is available.

> [!NOTE]
>
> **Skills on Alps**
>
> The skills will be published on every cluster in `/capstor/store/cscs/cscs/public/skills`, kept up to date with the documentation. Users on Alps will then be able to link to that copy instead of downloading their own, and receive updates without further action. The message of the day on the clusters will point users of coding agents to the agent skills page.
