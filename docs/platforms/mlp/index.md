[](){#ref-platform-mlp}
# Machine learning platform

The Machine Learning Platform (MLP) provides compute, storage and expertise to the machine learning communities accessing the Alps Research Infrastructure.

## Getting started

<div class="grid cards" markdown>
-   :fontawesome-solid-mountain: __ML Guides__

    For an overview of how to use common machine learning software, tools and workflows, read our [machine learning documentation][ref-software-ml].

    Tutorials on how to set up and configure a machine learning environment in order to run LLM workloads such as inference, fine-tuning and multi-node training can be found in the [tutorials section][ref-tutorials-ml].

    Check out the [PyTorch documentation][ref-software-pytorch] for information about how to run PyTorch.

</div>

### Getting access

Project administrators (PIs and deputy PIs) of projects on the MLP can to invite users to join their project, before they can use the project's resources on Alps.
This is performed using the [project management tool][ref-account-waldur].

Once invited to a project, you will receive an email, which you need to create an account and configure [multi-factor authentication][ref-mfa] (MFA).

<div class="grid cards" markdown>
-   :fontawesome-solid-scale-balanced: [__Project policies__][ref-mlp-policies]

    How MLP projects are allocated and managed: the small and large project types, the usage-based credit model, and the rules that apply while a project runs and after it ends.
</div>

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

The following file systems are mounted on the MLP clusters Clariden and Bristen:

| type |mount | filesystem |
| -- | -- | -- |
| Home | `/users/$USER` | [Vadret][ref-alps-vadret] |
| Scratch | `/iopsstor/scratch/cscs/$USER` | [Iopsstor][ref-alps-iopsstor] |
|         | `/capstor/scratch/cscs/$USER` | [Capstor][ref-alps-capstor] |
|         | `/ritom/scratch/cscs/$USER` | [Ritom][ref-alps-ritom] |
| Store | `/capstor/store/cscs/<organization>/<project>` | [Capstor][ref-alps-capstor] |
| Datacache | `/iopsstor/datacache/cscs/<organization>/<project>` | [Iopsstor][ref-alps-iopsstor] |

In the paths above, `<organization>` is the organization your project belongs to (for example `swissai`) and `<project>` is your project's name.

[](){#ref-mlp-storage-model}
### How storage works on the MLP

The file systems are tuned for different roles, and a typical job moves data between them rather than keeping everything in one place:

* **Home** (`/users/$USER`) holds your code, scripts, small configuration files and software. It is small, and not meant for datasets or job output.
* **Scratch** (`$SCRATCH`) is a large, fast workspace for *running jobs*: you stage input data in, the job reads and writes here, and you copy results out when it finishes. Scratch is temporary --- a [cleanup policy][ref-storage-cleanup] removes files that have not been accessed recently, and there are no backups.
* **Project store** (`/capstor/store`) is persistent, backed-up storage for the datasets and results you want to keep. It has no cleanup policy.
* **Project data cache** (`/iopsstor/datacache`) is a fast, project-level working area on Iopsstor for datasets shared across the whole project. Like scratch it is not backed up, but unlike scratch it has no cleanup policy --- the project owns its data lifecycle. See [project data cache][ref-mlp-storage-datacache].

The golden rule is to **use scratch only while jobs are running, and move anything you want to keep to the [project store][ref-storage-store] afterwards** --- see [transferring data between scratch and store][ref-data-xfer-internal] for how to do this efficiently.

The same principle applies to `datacache`, only without a deadline: there is no cleanup policy forcing you to act, but because it is not backed up, the durable copy of anything you want to keep still belongs on the project store.

Scratch is available on more than one file system, on hardware tuned for different access patterns; choosing the right one matters for performance, as explained under [file system suitability][ref-mlp-storage-suitability].

### Home

Every user has a home path (`$HOME`) mounted at `/users/$USER` on the [Vadret][ref-alps-vadret] filesystem.
The home directory has 50 GB of capacity, and is intended for configuration, small software packages and scripts.

### Scratch

Scratch filesystems provide temporary storage for high-performance I/O for executing jobs.
Use scratch to store datasets that will be accessed by jobs, and for job output.
Scratch is per user - each user gets separate scratch path and quota.

* The environment variable `SCRATCH=/iopsstor/scratch/cscs/$USER` is set automatically when you log into a system of the ML platform, and can be used as a shortcut to access scratch.
* There is an additional scratch path mounted on [Capstor][ref-alps-capstor] at `/capstor/scratch/cscs/$USER`.
* There is a further scratch path on [Ritom][ref-alps-ritom] (a VAST file system) at `/ritom/scratch/cscs/$USER`.

!!! warning "scratch cleanup policy"
    - Files on `/iopsstor/scratch/cscs/$USER` that have not been accessed in **14 days** are automatically deleted.
    - Files on `/capstor/scratch/cscs/$USER` that have not been accessed in **30 days** are automatically deleted.
    - The cleanup policy for `/ritom/scratch/cscs/$USER` is being finalised.

    **Scratch is not intended for permanent storage**: transfer files back to the capstor project storage after job runs.

[](){#ref-mlp-storage-suitability}
!!! note "file system suitability"
    The Capstor scratch filesystem is based on HDDs and is optimized for large, sequential read and write operations.
    We recommend using Capstor for storing **checkpoint files** and other **large, contiguous outputs** generated by your training runs.
    In contrast, Iopsstor uses high-performance NVMe drives, which excel at handling **IOPS-intensive workloads** involving frequent, random access. This makes it a better choice for storing **training datasets**, especially when accessed randomly during machine learning training.
    Iopsstor is also a smaller and more expensive resource than Capstor, so prefer Capstor unless random-access IOPS is genuinely limiting your workload. Keeping data that does not need fast random access on Capstor leaves Iopsstor capacity available for the jobs that need it.
    See the [Lustre guide][ref-guides-storage-lustre] for some hints on how to get the best performance out of the filesystem.

### Scratch Usage Recommendations

Use Iopsstor scratch (`$SCRATCH`) for:

* Training and validation datasets that are read frequently and non-sequentially.
* Workloads that perform many small, random I/O operations.

Use Capstor scratch (`/capstor/scratch/cscs/$USER`) for:

* Storing model checkpoints.
* Outputs from simulations or training jobs that involve large, contiguous I/O.

After your job completes, remember to transfer any important results to your [project store][ref-storage-store], for example with [`rclone` on the `xfer` queue][ref-data-xfer-internal].

### Project store

The [project store][ref-storage-store] (`/capstor/store/cscs/<organization>/<project>`) is persistent, backed-up storage for datasets, shared code and configuration scripts that need to be accessed from different vClusters.
It has no cleanup policy, and is per project: each project gets a folder with a project [quota][ref-storage-quota] on capacity and inodes.
Hard limits prevent writing once the quota is reached; you can check usage with the [`quota`][ref-storage-quota] command on a login node or ela.

Writing to the project store directly from jobs is not recommended: stage data to scratch or the project data cache for a run, and keep the durable copy here.

!!! note "requesting more project storage"
    Ask your PI to open a [CSCS Service Desk](https://jira.cscs.ch/plugins/servlet/desk) ticket describing the use case and the additional space and inodes required.
    CSCS then reviews the request before increasing the quota.

[](){#ref-mlp-storage-datacache}
### Project data cache

`datacache` is a project-level working area on the fast [Iopsstor][ref-alps-iopsstor] file system, mounted at `/iopsstor/datacache/cscs/<organization>/<project>`.
It gives the whole project one shared, high-performance copy of the datasets its members actively work on, so users no longer stage a private copy of the same data on their own scratch.

Like scratch, it is fast NVMe storage and is **not backed up**.
Unlike scratch, it has **no cleanup policy**: files are never deleted automatically, and the project owns its data lifecycle and space hygiene within a project [quota][ref-storage-quota] on capacity and inodes, as for the project store.

Because nothing here is backed up, `datacache` is a *manual* cache: CSCS never copies its contents anywhere else, so the durable copy of anything you keep must live on the [project store][ref-storage-store] (`/capstor/store`, which is backed up).
A typical workflow keeps the authoritative dataset on the project store, stages it once into `datacache` where the whole project reads it at NVMe speed during training, and moves anything worth preserving back to the project store afterwards.

!!! note "requesting a project data cache"
    A `datacache` area is **not provisioned by default**, unlike the project store.
    Ask your PI to open a [CSCS Service Desk](https://jira.cscs.ch/plugins/servlet/desk) ticket describing the use case and the space and inodes required.
    CSCS then reviews the request before creating the area.
    Without justification, a small project can request up to 100GB and 1M inodes, and a large project can request up to 1TB and 5M inodes, for the whole duration of the project.

    Requesting more resources than the default limits above must be properly justified, and a contact person that will be responsible for the data management should be provided.
    The extra storage capacity will be typically provided only for a specific amount of time, and not for the whole project duration.
