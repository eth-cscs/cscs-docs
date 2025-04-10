[](){#ref-platform-mlp}
# Machine learning platform

The Machine Learning Platform (MLP) provides compute, storage and expertise to the machine learning and AI community in Switzerland, with the main user being the [Swiss AI Initiative](https://www.swiss-ai.org/).

## Getting started

### Getting access

Project administrators (PIs and deputy PIs) of projects on the MLP can to invite users to join their project, before they can use the project's resources on Alps.
This is performed using the [project management tool][ref-account-waldur]

Once invited to a project, you will receive an email, which you can need to create an account and configure [multi-factor authentication][ref-mfa] (MFA).

## Systems

The main cluster provided by the MLP is Clariden, a large Grace-Hopper GPU system on Alps.

<div class="grid cards" markdown>
-   :fontawesome-solid-mountain: [__Clariden__][ref-cluster-clariden]

    Clariden is the main [Grace-Hopper][ref-alps-gh200-node] cluster.
</div>

<div class="grid cards" markdown>
-   :fontawesome-solid-mountain: [__Bristen__][ref-cluster-bristen]

    Bristen is a smaller system with [A100 GPU nodes][ref-alps-a100-node] for data processing, development, x86 workloads and inference services.
</div>

[](){#ref-mlp-storage}
## File Systems and Storage

There are three main file systems mounted on the MLP clusters Clariden and Bristen.

| type |mount | filesystem |
| -- | -- | -- |
| Home | /users/$USER | [VAST][ref-alps-vast] |
| Scratch | `/iopstor/scratch/cscs/$USER` | [Iopstor][ref-alps-iopstor] |
| Project | `/capstor/store/cscs/swissai/<project>` | [Capstor][ref-alps-capstor] |

### Home

Every user has a home path (`$HOME`) mounted at `/users/$USER` on the [VAST][ref-alps-vast] filesystem.
The home directory has 50 GB of capacity, and is intended for configuration, small software packages and scripts.

### Scratch

Scratch filesystems provide temporary storage for high-performance I/O for executing jobs.
Use scratch to store datasets that will be accessed by jobs, and for job output.
Scratch is per user - each user gets separate scratch path and quota.

* The environment variable `SCRATCH=/iopstor/scratch/cscs/$USER` is set automatically when you log into the system, and can be used as a shortcut to access scratch.

!!! warning "scratch cleanup policy"
    Files that have not been accessed in 30 days are automatically deleted.

    **Scratch is not intended for permanant storage**: transfer files back to the capstor project storage after job runs.

!!! note
    There is an additional scratch path mounted on [Capstor][ref-alps-capstor] at `/capstor/scratch/cscs/$USER`, however this is not reccomended for ML workloads for performance reasons.

### Project

Project storage is backed up, with no cleaning policy: it provides intermediate storage space for datasets, shared code or configuration scripts that need to be accessed from different vClusters.
Project is per project - each project gets a project folder with project-specific quota.

* if you need additional storage, ask your PI to contact the CSCS service managers Fawzi or Nicholas.
* hard limits on capacity and inodes prevent users from writing to project if the quota is reached - you can check quota and available space by running the [`quota`][ref-storage-quota] command on a login node or ela 
* it is not recommended to write directly to the project path from jobs.

## Guides and tutorials

Tutorials for finetuning and running inference of LLMs as well as training an LLM with Nanotron can be found in the [MLP Tutorials][ref-guides-mlp-tutorials] page.
