[](){#ref-agents}
# Agent skills

CSCS publishes skills for [coding agents][ref-coding-agents] such as Claude Code, Codex and OpenCode.
A skill is a set of instructions, and sometimes tools, that an agent reads when a task needs it.
The CSCS skills help agents answer questions about Alps from facts read on the system, instead of from memory.

Skills are never installed or enabled for you: you choose which ones your agent uses.
They work in the same way whether the agent runs on Alps, or on your own computer and connects to Alps with [SSH][ref-ssh].

[](){#ref-agents-skills}
## Available skills

| Skill | What it does |
|-------|--------------|
| `cscs-cluster-probes` | Looks up how a cluster is configured and what it is doing now: partitions and their limits, QoS, node hardware and features, file systems, tool versions, idle nodes, pending jobs, and which partitions you can submit to. |

The skills are listed for agents in [`index.json`](https://docs.cscs.ch/.well-known/agent-skills/index.json), which follows the [Agent Skills Discovery](https://github.com/cloudflare/agent-skills-discovery-rfc) draft.
Each skill is one `.tar.gz` archive, and its `SKILL.md` can be read before it is installed, for example [`cscs-cluster-probes`](https://docs.cscs.ch/.well-known/agent-skills/cscs-cluster-probes/SKILL.md).

[](){#ref-agents-install}
## Installing skills

Skills are installed in your home directory.
On Alps, your home directory is shared by all clusters, so one installation is enough for all of them.

Each agent looks for skills in its own directory:

| Agent | Directory |
|-------|-----------|
| Codex, OpenCode | `~/.agents/skills/<skill>/` |
| Claude Code | `~/.claude/skills/<skill>/` |

The instructions below install each skill in `~/.agents/skills`, and link it from `~/.claude/skills` for Claude Code.

=== "Ask your agent"

    Start your agent and give it this request:

    ```text title="request to the agent"
    Install the CSCS agent skills, following https://docs.cscs.ch/agents/.
    Tell me what you will install and where, and ask me before you change anything.
    ```

    !!! info "Instructions for agents"
        * Read <https://docs.cscs.ch/.well-known/agent-skills/index.json>, and show the user the name and description of each skill.
        * Ask the user which skills to install, and install no others.
        * For each skill, download the archive named by `url`, relative to the index, and check that its SHA-256 matches `digest`.
          If it does not match, stop and tell the user.
        * Unpack the archive into `~/.agents/skills/<name>/`, replacing an earlier copy of the skill.
          The archive has `SKILL.md` at its root.
        * Write the digest to `~/.agents/skills/<name>/.digest`, so that an update can be detected later.
        * If the user uses Claude Code, link `~/.claude/skills/<name>` to `~/.agents/skills/<name>`.
        * Change nothing else: no configuration files, environment variables or shell startup files.
        * Tell the user what was installed, and how to remove it.

=== "Install by hand"

    ```bash title="install the cscs-cluster-probes skill"
    skill=cscs-cluster-probes
    curl -fsSLO https://docs.cscs.ch/.well-known/agent-skills/$skill.tar.gz
    sha256sum $skill.tar.gz   # compare with the digest of the skill in index.json
    rm -rf ~/.agents/skills/$skill
    mkdir -p ~/.agents/skills/$skill ~/.claude/skills
    tar -xzf $skill.tar.gz -C ~/.agents/skills/$skill
    ln -sfn ~/.agents/skills/$skill ~/.claude/skills/$skill   # for Claude Code
    rm $skill.tar.gz
    ```

=== "Link on Alps"

    !!! under-construction
        The skills will be available on all clusters in `/capstor/store/cscs/cscs/public/skills`, kept up to date by CSCS.
        Linking to that copy, instead of downloading one, keeps your skills up to date without further action.

!!! warning
    You are responsible for what an agent does with a skill, as with any [other action of a coding agent][ref-coding-agents].
    The `cscs-cluster-probes` skill only reads the configuration and state of a cluster, and submits no jobs.

[](){#ref-agents-update}
## Updating and removing skills

To update a skill, install it again.
The digest of a skill in `index.json` changes only when the skill changes.
An agent that installed the skill recorded the digest in the `.digest` file of the skill, so it can compare the two to tell whether an update is available.

To remove a skill, delete its directories:

```bash title="remove the cscs-cluster-probes skill"
rm -rf ~/.agents/skills/cscs-cluster-probes ~/.claude/skills/cscs-cluster-probes
```
