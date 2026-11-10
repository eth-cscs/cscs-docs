# Agent skills

CSCS publishes skills for coding agents such as Claude Code, Codex and OpenCode. A skill is a set of instructions, and sometimes tools, that an agent reads when a task needs it. The CSCS skills help agents answer questions about Alps from facts read on the system, instead of from memory.

Skills are never installed or enabled for you: you choose which ones your agent uses. They work in the same way whether the agent runs on Alps, or on your own computer and connects to Alps with SSH.

## Available skills

| Skill | What it does |
| --- | --- |
| `cscs-alps` | Orients an agent on Alps: which cluster and CPU architecture it is on, where files should go, and how to get software with uenv and the Container Engine instead of modules. |
| `cscs-cluster-probes` | Looks up how a cluster is configured and what it is doing now: partitions and their limits, QoS, node hardware and features, file systems, tool versions, idle nodes, pending jobs, and which partitions you can submit to. |
| `build-uenv-stackinator` | Builds a uenv with Stackinator and Spack: writing and editing recipes, configuring and running the build, fixing build and runtime problems, and testing the image. |
| `cscs-ci` | Works with CSCS CI/CD: checking the status of pipelines, fetching their logs, triggering them from pull requests, and writing their configuration. |

See publishing agent skills for how the skills are built and published. The skills are listed for agents in [`index.json`](<https://docs.cscs.ch/.well-known/agent-skills/index.json>), which follows the [Agent Skills Discovery](<https://github.com/cloudflare/agent-skills-discovery-rfc>) draft. Each skill is one `.tar.gz` archive, and its `SKILL.md` can be read before it is installed, at `.well-known/agent-skills/<name>/SKILL.md` on this site.

## Installing skills

Skills are installed in your home directory. On Alps, your home directory is shared by all clusters, so one installation is enough for all of them.

Each skill is installed in `$XDG_DATA_HOME/cscs/skills/<skill>/`, or in `~/.local/share/cscs/skills/<skill>/` if `XDG_DATA_HOME` is not set. It is linked from the directory where your agent looks for skills:

| Agent | Link |
| --- | --- |
| Codex, OpenCode | `~/.agents/skills/<skill>` |
| Claude Code | `~/.claude/skills/<skill>` |

So there is one copy of each skill, however many agents you use, and the directories of your agents contain only links.

Start your agent and give it this request:

request to the agent

```text
Install the CSCS agent skills, following https://docs.cscs.ch/agents/.
Tell me what you will install and where, and ask me before you change anything.
```

> [!NOTE]
>
> **Instructions for agents**
>
> - Read the index of skills at `../.well-known/agent-skills/index.json`, relative to the URL of this page. For this page at `https://docs.cscs.ch/agents/`, that is `https://docs.cscs.ch/.well-known/agent-skills/index.json`. Download everything from the same site as this page.
> - Show the user the name and description of each skill. Ask the user which skills to install, and install no others.
> - Ask the user which agents they use, to know which links to create: `~/.agents/skills/<name>` for Codex and OpenCode, `~/.claude/skills/<name>` for Claude Code.
> - Find the directory for the skills, `<skills>` below: `$XDG_DATA_HOME/cscs/skills` if `XDG_DATA_HOME` is set, otherwise `$HOME/.local/share/cscs/skills`. Expand it to an absolute path, such as `/home/alice/.local/share/cscs/skills`, and write that path in full in every command that follows.
> - If `<skills>/<name>` already exists, the skill is installed: follow the instructions for updating instead. If one of the links already exists, tell the user, and ask before you replace it.
> - For each skill, download the archive named by `url`, relative to the index, and check that its SHA-256 matches `digest`. If it does not match, stop and tell the user.
> - Unpack the archive into `<skills>/<name>/`. The archive has `SKILL.md` at its root.
> - Write the digest to `<skills>/<name>/.digest`, so that an update can be detected later.
> - Create the links to `<skills>/<name>`. Do not copy the skill into the directories of the agents.
> - Run each step as a separate command, so that the user can review it. Never build the path of a file to delete from shell variables, for example `rm "$dir/$name.tar.gz"`: write it in full, as in `rm /home/alice/.local/share/cscs/skills/cscs-cluster-probes.tar.gz`. Agents may refuse to run commands that delete paths built from variables.
> - Change nothing else: no configuration files, environment variables or shell startup files.
> - Tell the user what was installed, and how to remove it.

Download the skill, and check that the SHA-256 printed matches the `digest` of the skill in `index.json`:

download the cscs-cluster-probes skill

```bash
mkdir -p "${XDG_DATA_HOME:-$HOME/.local/share}/cscs/skills/cscs-cluster-probes"
cd "${XDG_DATA_HOME:-$HOME/.local/share}/cscs/skills"
curl -fsSLO https://docs.cscs.ch/.well-known/agent-skills/cscs-cluster-probes.tar.gz
sha256sum cscs-cluster-probes.tar.gz
```

If it matches, unpack it, and record its digest in the `.digest` file of the skill, so that you can check for updates later:

unpack the cscs-cluster-probes skill

```bash
tar -xzf cscs-cluster-probes.tar.gz -C cscs-cluster-probes
echo "sha256:$(sha256sum cscs-cluster-probes.tar.gz | cut -d' ' -f1)" > cscs-cluster-probes/.digest
rm cscs-cluster-probes.tar.gz
cd -
```

Then link the skill for the agents that you use:

link the skill for Codex and OpenCode

```bash
mkdir -p ~/.agents/skills
ln -s "${XDG_DATA_HOME:-$HOME/.local/share}/cscs/skills/cscs-cluster-probes" ~/.agents/skills/
```

link the skill for Claude Code

```bash
mkdir -p ~/.claude/skills
ln -s "${XDG_DATA_HOME:-$HOME/.local/share}/cscs/skills/cscs-cluster-probes" ~/.claude/skills/
```

If the skill is already installed, update it instead.

> [!NOTE]
>
> **Under-construction**
>
> The skills will be available on all clusters in `/capstor/store/cscs/cscs/public/skills`, kept up to date by CSCS. Linking the directories of your agents to that copy, instead of to a copy in your home directory, will keep your skills up to date without further action.

> [!WARNING]
>
> You are responsible for what an agent does with a skill, as with any other action of a coding agent. Read the `SKILL.md` of a skill to see what it asks the agent to do. For example, `cscs-cluster-probes` only reads the configuration and state of a cluster, and submits no jobs, while `build-uenv-stackinator` runs builds that can occupy a node for hours.

## Updating and removing skills

The digest of a skill in `index.json` changes when the skill changes. The installation records the digest in the `.digest` file of the skill, so comparing the two tells whether an update is available. Updating a skill replaces its directory, and with it any changes that you made to the skill; the links to it do not change.

Start your agent and give it this request:

request to the agent

```text
Update the CSCS agent skills, following https://docs.cscs.ch/agents/.
Show me what has changed, and ask me before you change anything.
```

> [!NOTE]
>
> **Instructions for agents**
>
> - Read the index of skills, and find the directory of the skills, `<skills>`, as for installing them. The installed skills are the directories in `<skills>` that contain a `SKILL.md`.
> - For each installed skill, compare the content of its `.digest` file with the `digest` of the skill in the index:
>
>   - if they are the same, the skill is up to date;
>   - if they differ, an update is available;
>   - if there is no `.digest` file, the version of the skill is unknown: tell the user, and offer to update it;
>   - if the skill is not in the index, it has been removed or renamed: tell the user, and do not delete it unless they ask.
> - For each skill with an update, show the user what has changed: download its `SKILL.md`, at `<name>/SKILL.md` relative to the index, and compare it with the installed `SKILL.md`. Tell the user that only `SKILL.md` is compared, and that the other files of the skill may also have changed.
> - Tell the user that updating replaces the directory of the skill, with any changes that they made to it. Ask the user which skills to update, and update no others.
> - For each skill to update, download the archive named by `url`, relative to the index, and check that its SHA-256 matches `digest`. If it does not match, stop and tell the user.
> - Unpack the archive into `<skills>/<name>.new/`, and write the digest to `<skills>/<name>.new/.digest`. Then delete the archive and `<skills>/<name>/`, and rename `<skills>/<name>.new/` to `<skills>/<name>/`. The links to `<skills>/<name>` need no change.
> - As when installing, run each step as a separate command, write every path in full, and change nothing else.
> - Tell the user which skills were updated, and which were already up to date.

Compare the digest of the installed skill with the digests in `index.json`:

check whether the cscs-cluster-probes skill is up to date

```bash
cat "${XDG_DATA_HOME:-$HOME/.local/share}/cscs/skills/cscs-cluster-probes/.digest"
curl -fsSL https://docs.cscs.ch/.well-known/agent-skills/index.json \
  | python3 -c 'import json, sys; [print(s["name"], s["digest"]) for s in json.load(sys.stdin)["skills"]]'
```

If they differ, or the skill has no `.digest` file, download the skill and check that the SHA-256 printed matches the `digest` of the skill in `index.json`:

download the cscs-cluster-probes skill

```bash
cd "${XDG_DATA_HOME:-$HOME/.local/share}/cscs/skills"
curl -fsSLO https://docs.cscs.ch/.well-known/agent-skills/cscs-cluster-probes.tar.gz
sha256sum cscs-cluster-probes.tar.gz
```

If it matches, unpack it next to the installed skill, then replace the installed skill with it:

replace the cscs-cluster-probes skill

```bash
mkdir cscs-cluster-probes.new
tar -xzf cscs-cluster-probes.tar.gz -C cscs-cluster-probes.new
echo "sha256:$(sha256sum cscs-cluster-probes.tar.gz | cut -d' ' -f1)" > cscs-cluster-probes.new/.digest
rm cscs-cluster-probes.tar.gz
rm -rf cscs-cluster-probes
mv cscs-cluster-probes.new cscs-cluster-probes
cd -
```

To remove a skill, delete its links and its directory:

remove the cscs-cluster-probes skill

```bash
rm -f ~/.agents/skills/cscs-cluster-probes ~/.claude/skills/cscs-cluster-probes
rm -rf "${XDG_DATA_HOME:-$HOME/.local/share}/cscs/skills/cscs-cluster-probes"
```
