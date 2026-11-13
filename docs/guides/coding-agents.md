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
The level of restrictions that you apply must be considered in relation to the risk that you consider acceptable for your work and project.

!!! warning "Sandbox restrictions do not apply to Slurm jobs submitted by agents"

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

OpenCode does not have a built-in sandbox.
The permission system described in the previous section provides basic checks for e.g. writes outside the working directory, but provides no guarantees.
An agent can still write outside the working directory through indirection in scripts etc.

[](){#ref-coding-agents-sandboxing-containers}
#### Running an agent in a container

An alternative to sandboxing an agent directly on the system is to run the agent inside a container and expose only the directories from the host system needed for the agent to do its work.
This can be done with the [Container Engine][ref-container-engine] on Alps.
An [Environment Definition File][ref-ce-edf-reference] lets you define the image and mounts to expose from the host system.
Additionally, the agent can run on a compute node with no Slurm available so it will not be able to spawn new jobs.

The example below uses the official OpenCode image to start a job on a compute node using the Container Engine.
For building a custom image with the tools you need, see [building container images on Alps][ref-build-containers].

!!! todo "Try this example!"

```toml title="~/.edf/opencode.toml"
image = "ghcr.io#anomalyco/opencode:latest"  # (1)!
mounts = [
    "${PROJECT}/myproject:${PROJECT}/myproject:ro",  # (2)!
    "${SCRATCH}/output:${SCRATCH}/output",  # (3)!
]
workdir = "${PROJECT}/myproject"  # (4)!

[annotations]
com.hooks.cxi.enabled = "false"  # (5)!

[env]
ENROOT_SLURM_HOOK = "0"  # (6)!
```

1. The container image with the agent and tools that you or the agent needs for development.
2. A project directory, mounted read-only.
3. A writable directory for e.g. outputs.
4. The directory that the agent starts in.
5. Disables the CXI hook, which does not work with the OpenCode image, which is based on Alpine. Without this the container does not start.
6. Disables the Slurm inside the container, so an agent can't submit jobs.

Once you've saved the file as `~/.edf/opencode.toml`, start an interactive shell on a compute node using the environment file:

```console title="running an agent in the container"
srun --environment=opencode --pty opencode
```

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


[](){#ref-coding-agents-support}
## Getting help

For issues with coding agent tools (Claude Code, OpenCode, etc.), consult their respective documentation.
If you have concerns about whether a particular agentic workflow is acceptable to run on Alps, [contact us for more information](https://support.cscs.ch).
