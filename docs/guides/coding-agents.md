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
      Not following the [Fair Usage of Shared Resources][ref-policies-fair-use] may result in access being revoked.
    - CSCS takes no responsibility for files deleted, quotas being exhausted, or other unintended behaviour by agents.
    - CSCS takes no responsibility for data inadvertently shared by your agent with third party LLM providers.

The [LLM inference service hosted by CSCS][ref-inference-api] can be used as a provider in most coding agents.
See the [inference API documentation][ref-inference-api-coding-agents-setup] for instructions on how to set up the most common agents to use the CSCS-hosted inference service.

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

We recommend _not_ running agents on login nodes because of the potential for unintended high resource usage on a shared resource.
However, even when not running on login nodes other resources are limited and care should be taken for example to not:

- overload the [filesystems][ref-storage-fs],
- overload the Slurm scheduler with many small jobs, or
- submit excessive network requests from Alps.

We recommend running agents either on compute nodes or on your local computer with limited Slurm or FirecREST jobs allowed.
When running on a compute node, [run the agent inside a container][ref-container-engine] with [only necessary directories mounted][ref-ce-edf-reference-mounts] or inside a [uenv][ref-uenv] to give the agent access to build tools and dependencies for your project.
See the [sandboxing section][ref-coding-agents-sandboxing] below for more pointers on restricting coding agents.

!!! note "uenvs do not restrict access to the host system"
    While containers provide some isolation from the host system, uenvs provide no isolation.
    uenvs only provide additional software on top of the host system.

[](){#ref-coding-agents-sandboxing}
### Sandboxing

Most agents will by default give access only to files within the working directory in which the agent is launched.
This provides a basic level of protection against unwanted and irreversible actions taken by agents.
Sandboxing can provide stronger protection.

We highly recommend consulting your coding agent's documentation for instructions on how to restrict commands and filesystem access. See for example:

- Claude Code documentation on [sandboxing](https://code.claude.com/docs/en/sandbox-environments) or [permissions](https://code.claude.com/docs/en/permissions)
- OpenCode documentation on [permissions](https://opencode.ai/docs/permissions)

We recommend starting with restrictive permissions and progressively whitelisting or approving commands manually as you get to know the behaviour of your particular coding agent and model on Alps.
This is particularly important if you are new to coding agents, but is important even if you have used them in the past and are moving workflows to Alps.

!!! info "Anthropic srt uenv"
    On the [daint cluster][ref-cluster-daint] a preview [uenv][ref-uenv] containing the [Anthropic Sandbox Runtime (srt)](https://github.com/anthropic-experimental/sandbox-runtime) is available in the `build::` namespace:
    
    ```console title="Pulling and using the srt uenv"
    $ uenv image find build::srt
    uenv                 arch   system  id                size(MB)  date
    srt/26.4:2590682466  gh200  daint   ae6b951e8de7276f     969    2026-06-10
    $ uenv image pull build::srt
    $ uenv start srt/26.4 --view=srt
    $ srt curl "anthropic.com"
    Connection blocked by network allowlist
    ```
    
    See the [srt documentation](https://github.com/anthropic-experimental/sandbox-runtime) for more information on configuring the sandbox.
    
!!! warning "Slurm does not propagate sandbox restrictions"
    Sandboxing agents is effective for the agent process and its tool calls on the particular node where the agent is running.
    When an agent submits a Slurm job, the restrictions of the sandbox are typically not propagated to the compute nodes of the Slurm job, resulting in the agent having broader access than the sandbox would indicate.
    
    We are investigating alternatives for improving the integration with Slurm.

!!! todo "Provide more concrete examples of sandboxing and useful permissions configurations on Alps"

[](){#ref-coding-agents-support}
## Getting help

For issues with coding agent tools (Claude Code, OpenCode, etc.), consult their respective documentation.
If you have concerns about whether a particular agentic workflow is acceptable to run on Alps, [contact us for more information](https://support.cscs.ch).
