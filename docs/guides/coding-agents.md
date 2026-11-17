[](){#ref-coding-agents}
# Using coding agents on Alps

Coding agents are AI-powered tools that assist with software development tasks such as writing, editing, debugging, and refactoring code.
They can read and modify files, run build commands, and submit Slurm jobs on your behalf.

This page covers Alps-specific considerations for running coding agents, regardless of which agent or LLM provider you use.

!!! warning "You are responsible for actions taken by coding agents"
    Any action taken by a coding agent you launch is your responsibility.
    The [CSCS policies][ref-policies] apply.

    In particular:

    - Compute resources used by agent-launched Slurm jobs are billed to your project account.
    - Coding agents may inadvertently submit many jobs, consume node hours, or modify files in unintended ways.
      Not following the [Fair Usage of Shared Resources][ref-policies-fair-use-login-node] may result in access being revoked.
    - CSCS takes no responsibility for files deleted, quotas being exhausted, or other unintended behaviour by agents.
    - CSCS takes no responsibility for data inadvertently shared by your agent with third party LLM providers.

The [LLM inference service hosted by CSCS][ref-inference-api] can be used as a provider in most coding agents.
See the [inference API documentation][ref-inference-api-coding-agents-setup] for instructions on how to set up the most common agents to use the CSCS-hosted inference service.

CSCS also publishes [agent skills][ref-agents] that help agents answer questions about Alps, such as which partition a job should use, from facts read on the system.

!!! info "Discovering best practices"
    As agentic workflows change and improve rapidly, so do best practices.
    To help keep this page relevant, we encourage and welcome contributions from the CSCS user community on best practices on using coding agents.
    If you have suggestions, tips, or warnings that you'd like to share, please [get in touch with us][ref-get-in-touch], share your findings directly with other users on the [CSCS User Slack](https://cscs-users.slack.com/), or [contribute directly to the documentation][ref-contributing].

[](){#ref-coding-agents-methods}
## Running on Alps

Coding agents can be run on Alps in different ways:

- running the agent on a login node,
- running the agent on a compute node, or
- running the agent locally and submitting jobs over [SSH][ref-ssh] and [Slurm][ref-slurm] or via [FirecREST][ref-firecrest].

We ask _not_ running agents on login nodes because of the potential for unintended high resource usage on a shared resource.
However, even when not running on login nodes other resources are limited and care should be taken for example to not:

- overload the [filesystems][ref-storage-fs],
- overload the Slurm scheduler with many small jobs, or
- submit excessive network requests from Alps.

We recommend running agents either on compute nodes or on your local computer with limited Slurm or FirecREST jobs allowed.
When running on a compute node, [run the agent inside a container][ref-container-engine] with [only necessary directories mounted][ref-ce-edf-reference-mounts] or inside a [uenv][ref-uenv] to give the agent access to build tools and dependencies for your project.
See the section on [restricting agents][ref-coding-restricting-agents] below for more pointers on restricting coding agents.

!!! note "uenvs do not restrict access to the host system"
    While containers provide some isolation from the host system, uenvs provide no isolation.
    uenvs only provide additional software on top of the host system.

[](){#ref-coding-restricting-agents}
### Restricting agents

Most agents will by default give access only to files within the working directory in which the agent is launched.
This provides a basic level of protection against unwanted and irreversible actions taken by agents.
Sandboxing can provide stronger protection.
Below we describe multiple alternatives for restricting agent access on and outside of Alps.
Multiple options can and should often be combined.
We recommend at least setting up restrictions on permissions and one of the sandboxing options below for your agent.
If your workflow allows it, we recommend testing one of the sandboxing options that [take Slurm job submission into account][ref-coding-agents-sandboxing-slurm].

!!! danger "Sandbox restrictions do not apply to Slurm jobs submitted by agents"

    Most sandboxing and permissions restrict the agent on the node where it runs.
    Jobs that the agent submits to Slurm, directly or through [FirecREST][ref-firecrest], run without those restrictions.
    See [Sandboxing Slurm jobs][ref-coding-agents-sandboxing-slurm] for options for restricting permissions on compute nodes for agents submitting jobs to Slurm.

[](){#ref-coding-agents-permissions}
#### Restricting agent permissions

We highly recommend consulting your coding agent's documentation for instructions on how to restrict commands and filesystem access. See for example:

- Claude Code documentation on [sandboxing](https://code.claude.com/docs/en/sandbox-environments) or [permissions](https://code.claude.com/docs/en/permissions)
- OpenCode documentation on [permissions](https://opencode.ai/docs/permissions)

We recommend starting with restrictive permissions and progressively whitelisting or approving commands manually as you get to know the behaviour of your particular coding agent and model on Alps.
This is particularly important if you are new to coding agents, but is important even if you have used them in the past and are moving workflows to Alps.

[](){#ref-coding-agents-sandboxing-builtin}
#### Built-in sandboxing

Some coding agents come with a built-in sandbox that restricts the commands that they run:

- Claude Code wraps bash commands in a bubblewrap sandbox.
  It can be enabled with the `/sandbox` command.
  The file tools of Claude Code and MCP servers still run outside the sandbox.
  See the Claude Code documentation on [sandboxing](https://code.claude.com/docs/en/sandbox-environments) for more information.
- Codex CLI runs commands in a built-in OS sandbox, with network access off by default.
  See its documentation on [agent approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) for more details.
- OpenCode does not have a built-in sandbox.
  The permission system described in the previous section provides basic checks for e.g. writes outside the working directory, but provides no guarantees.
  An agent can still write outside the working directory through indirection in scripts etc.
  Use the sandboxing solutions described in the other sections instead together with restricted permissions.


[](){#ref-coding-agents-sandboxing-containers}
#### Running an agent in a container

An alternative to sandboxing an agent directly on the system is to run the agent inside a container and expose only the directories from the host system needed for the agent to do its work.
This can be done with the [Container Engine][ref-container-engine] on Alps.
An [Environment Definition File][ref-ce-edf-reference] lets you define the image and mounts to expose from the host system.
Additionally, the agent can run on a compute node with no Slurm available so it will not be able to spawn new jobs.

The example below runs the official OpenCode image through the early-access [Sarus Suite][ref-sarus-suite-user-guide] tooling.
For building a custom image with the tools you need, see [building container images on Alps][ref-build-containers].

```toml title="~/.edf/opencode.toml"
image = "ghcr.io#anomalyco/opencode:latest"  # (1)!
mounts = [
    "${PROJECT}/myproject:${PROJECT}/myproject:ro",  # (2)!
    "${SCRATCH}/output:${SCRATCH}/output",  # (3)!
    "${HOME}/.local/share/opencode:${HOME}/.local/share/opencode",  # (4)!
    "${HOME}/.local/state/opencode:${HOME}/.local/state/opencode",  # (5)!
    "${HOME}/.config/opencode:${HOME}/.config/opencode",  # (6)!
]
workdir = "${PROJECT}/myproject"  # (7)!
```

1. The container image with the agent and tools that you or the agent needs for development.
2. A project directory, mounted read-only.
3. A writable directory for e.g. outputs.
4. The data directory of OpenCode, with the credentials in `auth.json`; mounted read-write so that the agent can refresh tokens.
5. The state directory of OpenCode: prompt history, last model choice, and locks; mounted read-write so that they survive between runs.
6. Your custom OpenCode configuration, if you have one; remove this line if you do not.
7. The directory that the agent starts in.

Once you've saved the file as `~/.edf/opencode.toml`, and made sure that the directories in the `mounts` list exist, start an interactive shell on a compute node using the environment file:

```bash title="running an agent in the container"
srun --pty sarusctl run opencode
```

!!! warning "Slurm hooks do not currently work with Alpine-based images"

    The command above calls `sarusctl run` directly instead of using the Slurm plugin with `--edf`, because Alpine-based images, such as the `opencode` image, do not currently start correctly with Slurm hooks.

The agent sees only the container and the mounts that you listed.
Files outside them, including your home directory, are not visible to the agent.
The project directory is mounted read-only.
The agent is able to write freely inside the container, but the only way for the agent to persist work outside the container is in the `output` directory.
Containers do not restrict the network access of the agent.
Running an agent in a container can be combined with the sandboxing and permissions restrictions described on this page.

[](){#ref-coding-agents-sandboxing-bwrap}
#### Sandboxing with bubblewrap

[bubblewrap](https://github.com/containers/bubblewrap) is a simple but powerful sandboxing tool.
Compared to other solutions, it requires manual setup, but can be customized to many needs.
Similar to other sandboxing solutions, bubblewrap also does not move to compute nodes when submitting jobs to Slurm.
The example below shows a reasonable default: a read-only filesystem, a writable working directory with a private `/tmp`, private PID and IPC namespaces, and cleanup on exit:

```bash title="bwrap-sandbox.sh"
#!/usr/bin/env bash
bwrap --die-with-parent \ # (1)!
    --ro-bind / / \ # (2)!
    --dev /dev --proc /proc \ # (3)!
    --bind "$PWD" "$PWD" \ # (4)!
    --tmpfs /tmp \ # (5)!
    --chdir "$PWD" \ # (6)!
    --unshare-pid \ # (7)!
    --unshare-ipc \ # (8)!
    --bind "${SCRATCH}/output" "${SCRATCH}/output" \ # (9)!
    --tmpfs "$HOME/.ssh" \ # (10)!
    claude
```

1. Exits the sandbox when the process that started it dies, so no orphaned agent processes survive a closed terminal or a lost SSH connection.
2. Mounts the whole filesystem read-only.
3. Provides the device and process filesystems that programs expect.
4. Makes the working directory writable.
5. Gives the agent a private, writable `/tmp`.
6. Starts the agent in the working directory.
7. Gives the agent a private PID namespace: it cannot see or signal processes outside the sandbox.
8. Gives the agent a private IPC namespace, isolating System V shared memory, semaphores, and message queues.
9. A writable directory in scratch, for outputs.
10. Hides your SSH keys: the agent sees an empty directory instead of `$HOME/.ssh`.

The default read-only mount with `--ro-bind / /` still lets agents read files anywhere on the filesystem.
If you want to fully hide files, use a `--tmpfs` mount, as for `$HOME/.ssh` in the example.

As with other sandboxing solutions, compute nodes do not get the same sandbox when an agent submits Slurm jobs.

[](){#ref-coding-agents-sandboxing-tools}
#### Existing sandboxing tools

Many existing sandboxing tools do not run easily or at all on Alps clusters.
Below we list some alternatives, but we are continuously looking to improve support for established sandboxing tools to make it easier for you to use them on Alps.

The [Anthropic sandbox runtime (srt)](https://github.com/anthropics/sandbox-runtime) restricts the filesystem and network access of arbitrary processes, without a container.
The sandbox requires `npm` for installation, which is not available globally on Alps, but a preview [uenv][ref-uenv] is available on the [daint cluster][ref-cluster-daint] in the `build::` namespace:

```console title="Pulling and using the srt uenv"
$ uenv image find build::srt
uenv                 arch   system  id                size(MB)  date
srt/26.4:2590682466  gh200  daint   ae6b951e8de7276f     969    2026-06-10
$ uenv image pull build::srt
$ uenv start srt/26.4 --view=srt
$ srt curl "anthropic.com"
Connection blocked by network allowlist
```

[`nono`](https://nono.sh/) is another popular sandboxing solution.
However, `nono` currently does not run on Alps due to [Landlock](https://landlock.io) not being enabled.
We are investigating enabling Landlock to allow use of `nono` and other sandboxing solutions based on it.

[](){#ref-coding-agents-sandboxing-slurm}
#### Sandboxing Slurm jobs

All of the options above restrict the agent process and its tool calls on the node where the agent runs.
When an agent submits a Slurm job, the restrictions do not travel with the job and an agent has full access to your account on a compute node.
The same applies to jobs that an agent submits through [FirecREST][ref-firecrest].

Two early-stage projects aim to make the sandbox apply both on the login node and on a compute node.
Both options disallow agents from submitting Slurm jobs directly and intercept the submission to enforce that a sandbox is used also on compute nodes.
We recommend evaluating both for your use case:

- [`husk`](https://github.com/MeteoSwiss/husk) currently supports only Claude Code.
- [`agent_sandbox`](https://github.com/katosh/agent_sandbox) supports multiple agent harnesses.

!!! warning "FirecREST submissions are not handled by the above sandboxing tools"

    Neither `husk` nor `agent_sandbox` sandbox jobs submitted via FirecREST.

[](){#ref-coding-agents-support}
## Getting help

For issues with coding agent tools (Claude Code, OpenCode, etc.), consult their respective documentation.
If you have concerns about whether a particular agentic workflow is acceptable to run on Alps, [contact us for more information](https://support.cscs.ch).
