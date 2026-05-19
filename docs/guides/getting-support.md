[](){#ref-guide-support}
# Getting support

Requests for support must be submitted to the [CSCS Service Desk](https://support.cscs.ch)

## Before submitting a ticket

It is worth ruling out some common causes before submitting a ticket.

* Check the [status page](https://status.cscs.ch) for the latest updates and ongoing incidents.
* Check your [available disk quotas][ref-storage-quota] using the [`quota`][ref-storage-quota-cli] command.
* Check whether scheduled maintenance is in progress (see the [Scheduled Events](https://status.cscs.ch/scheduled-events) tab on the status page).

## Writing a good support ticket

The goal of a support ticket is to give the engineer enough information to reproduce or understand your problem without having to ask follow-up questions.

!!! example "Example of a good support ticket"
    My MPI application hangs during initialization when running on 2 or more nodes on Daint.

    Job ID: 123456

    The issue occurs consistently when using 2 or more nodes but works correctly on a single node.

    Stdout:
    ```
    /capstor/scratch/cscs/alice/run_123456.out
    ```

    Stderr:
    ```
    /capstor/scratch/cscs/alice/run_123456.err
    ```

    Batch file:
    ```
    /capstor/scratch/cscs/alice/mpi_gpu.slurm
    ```

    Steps to reproduce:

    ```
    uenv start --view=default prgenv-gnu/25.6:v1
    sbatch mpi_gpu.slurm
    ```

    This workflow ran fine last month and no changes were made to the application code
    (the last time I successfully ran was January 23rd). The issue started on Monday 4th.

### Clear description of the problem

Describe exactly what you observed and what you expected to happen.
Avoid vague descriptions like "my job failed" or "the cluster is broken".
Instead support engineers need concrete, observable details to start investigating.

Good examples:

* "My Slurm job exits immediately with an out-of-memory error."
* "MPI jobs hang during startup on more than two nodes."
* "My application compiled successfully but crashes at runtime."
* "My application was running successfully, but since Monday it is crashing with I/O errors."

!!! tip "Describe symptoms, not diagnoses"
    It is fine to include theories about the cause, but always state the observable symptoms first.
    "The job printed `Error: out of memory` and exited with code 1" is a symptom.
    "There is a memory leak in the runtime" is a diagnosis.

### Slurm job information

If the issue involves a batch or interactive Slurm job, include the job ID(s), the submission script, and the number of nodes, tasks, and other resources requested.

It helps to state explicitly how you intend the job to run. For example, "I want to run 16 MPI ranks on 4 nodes, with one GPU per MPI rank".

If the problem is intermittent, include job IDs for both successful and unsuccessful runs.

### Job output and logs

Always provide the paths to the standard output and standard error logs, and ensure they are readable by support staff.

!!! info "CSCS staff can't read your paths by default"
    Support staff at CSCS do not have access to your files and folders by default.
    If you would like to share logs, scripts and other artifacts, ensure that you [give access to the `csstaff` group][ref-guides-storage-sharing].

Include any relevant error messages, stack traces, and the last few lines of output before the failure.
Paste error messages verbatim, even if the numbers and codes seem meaningless to you, they are often the fastest path to a diagnosis.

!!! tip
    Our support desk uses Jira, which has its own [Jira formatting](https://cheatography.com/rhorber/cheat-sheets/jira-text-formatting-notation) markup language.
    A little bit of text formatting makes your request much easier to read for support engineers.

    === "Markup"

        ```
        The stderr and stdout output are in {{/capstor/scratch/cscs/jsmith/output/log123.txt}}.
        The specific error message is:

        {code}
        starting time step 23
        updated particle positions
        Error: out of memory allocating ring buffer (rank 15)
        {code}
        ```

    === "Result"

        The stderr and stdout output are in `/capstor/scratch/cscs/jsmith/output/log123.txt`.
        The error message in the logs is:

        ```
        starting time step 23
        updated particle positions
        Error: out of memory allocating ring buffer (rank 15)
        ```

!!! tip "Only use screenshots of the terminal when necessary"
    Sometimes a screenshot is more useful than raw text, however 90% of the time it is better to paste terminal output directly into the ticket or attach a text file.
    This makes it much easier for support engineers to copy job IDs, hashes, and error messages when trying to help.

### Steps to reproduce

Support staff must be able to reproduce the issue wherever possible.
Include the commands you executed, the software environment (uenv, container description, etc.), and the exact sequence of actions leading to the failure.
If the issue depends on specific input data or configuration files, provide their location.

!!! tip "Preserve the failing run before retrying"
    Before rerunning or modifying anything, note the Slurm job ID and the locations of the stdout/stderr files.
    Each rerun can overwrite output files and makes it harder to reconstruct exactly what happened.
    The failing run is evidence — preserve it first.

### Has this worked before?

Tell us whether this workflow has ever run successfully, when it last worked, and what changed since then.
For example: "This job ran successfully last Friday but started failing after I updated my virtual environment" or "This issue began after the maintenance last Wednesday."
If the workflow has never run successfully, say so — that changes how the engineer approaches the problem.

### Scope and impact

Let us know how widely the issue affects you: does it affect one job or all jobs, and is it reproducible by other users?
If there is an urgent deadline, please mention it.
