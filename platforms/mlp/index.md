# Machine learning platform

The Machine Learning Platform (MLP) provides compute, storage and expertise to the machine learning communities accessing the Alps Research Infrastructure.

## Getting started

- **ML Guides**

  For an overview of how to use common machine learning software, tools and workflows, read our [machine learning documentation](<https://docs.cscs.ch/software/ml/index.md#machine-learning-applications-and-frameworks> "Machine learning applications and frameworks").

  Tutorials on how to set up and configure a machine learning environment in order to run LLM workloads such as inference, fine-tuning and multi-node training can be found in the [tutorials section](<https://docs.cscs.ch/tutorials/ml/index.md#machine-learning-platform-tutorials> "Machine Learning Platform Tutorials").

  Check out the [PyTorch documentation](<https://docs.cscs.ch/software/ml/pytorch/index.md#pytorch>) for information about how to run PyTorch.

### Getting access

Project administrators (PIs and deputy PIs) of projects on the MLP can to invite users to join their project, before they can use the project’s resources on Alps. This is performed using the [project management tool](<https://docs.cscs.ch/accounts/waldur/index.md#the-project-and-resources-management-tool> "The Project and Resources Management Tool").

Once invited to a project, you will receive an email, which you need to create an account and configure [multi-factor authentication](<https://docs.cscs.ch/access/mfa/index.md#multi-factor-authentication> "Multi Factor Authentication") (MFA).

- [**Project policies**](<https://docs.cscs.ch/platforms/mlp/policies/index.md#machine-learning-platform-project-policies> "Machine Learning Platform project policies")

  How MLP projects are allocated and managed: the small and large project types, the usage-based credit model, and the rules that apply while a project runs and after it ends.

## Systems

The main cluster provided by the MLP is Clariden, a large Grace-Hopper GPU system on Alps.

- [**Clariden**](<https://docs.cscs.ch/clusters/clariden/index.md#clariden>)

  Clariden is the main [Grace-Hopper](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-gh200-gpu-nodes> "NVIDIA GH200 GPU Nodes") cluster.

- [**Bristen**](<https://docs.cscs.ch/clusters/bristen/index.md#bristen>)

  Bristen is a smaller system with [A100 GPU nodes](<https://docs.cscs.ch/alps/hardware/index.md#nvidia-a100-gpu-nodes> "NVIDIA A100 GPU Nodes") for data processing, development, x86 workloads and inference services.

## File Systems and Storage

The file systems provided on the MLP cluster [Clariden](<https://docs.cscs.ch/clusters/clariden/index.md#clariden>), the environment variables that point to them, and the [Alps storage system](<https://docs.cscs.ch/alps/storage/index.md#alps-storage> "Alps Storage") that hosts each one:

| Variable | File system | Path | Storage | Type |
| --- | --- | --- | --- | --- |
| `$HOME` | [Home](<https://docs.cscs.ch/storage/filesystems/index.md#home>) | `/users/$USER` | [Vadret](<https://docs.cscs.ch/alps/storage/index.md#vadret>) | VAST |
| `$SCRATCH` | [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) | `/iopsstor/scratch/cscs/$USER` | [Iopsstor](<https://docs.cscs.ch/alps/storage/index.md#iopsstor>) | [Lustre](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") |
| `$STORE`, `$PROJECT` | [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) | `/capstor/store/cscs/<customer>/<group_id>` | [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) | [Lustre](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") |

The following are also provided, but no environment variable points to them:

| file system | path | storage |
| --- | --- | --- |
| [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) | `/capstor/scratch/cscs/$USER` | [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) |
| [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) | `/ritom/scratch/cscs/$USER` | [Ritom](<https://docs.cscs.ch/alps/storage/index.md#ritom>) |
| [Datacache](<https://docs.cscs.ch/platforms/mlp/index.md#project-data-cache> "Project data cache") | `/iopsstor/datacache/cscs/<customer>/<group_id>` | [Iopsstor](<https://docs.cscs.ch/alps/storage/index.md#iopsstor>) |

In the Store and Datacache paths, `<customer>` is the organization your project belongs to (`swissai` for most MLP projects), and `<group_id>` is your project’s Linux group; the rest of this page calls them `<organization>` and `<project>`.

### How storage works on the MLP

The file systems are tuned for different roles, and a typical job moves data between them rather than keeping everything in one place:

- **Home** (`/users/$USER`) holds your code, scripts, small configuration files and software. It is small, and not meant for datasets or job output.
- **Scratch** (`$SCRATCH`) is a large, fast workspace for *running jobs*: you stage input data in, the job reads and writes here, and you copy results out when it finishes. Scratch is temporary — a [cleanup policy](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies") removes files that have not been accessed recently, and there are no backups.
- **Project store** (`/capstor/store`) is persistent, backed-up storage for the datasets and results you want to keep. It has no cleanup policy.
- **Project data cache** (`/iopsstor/datacache`) is a fast, project-level working area on Iopsstor for datasets shared across the whole project. Like scratch it is not backed up, but unlike scratch it has no cleanup policy — the project owns its data lifecycle. See [project data cache](<https://docs.cscs.ch/platforms/mlp/index.md#project-data-cache> "Project data cache").

The golden rule is to **use scratch only while jobs are running, and move anything you want to keep to the [project store](<https://docs.cscs.ch/storage/filesystems/index.md#store> "Store") afterwards** — see [transferring data between scratch and store](<https://docs.cscs.ch/storage/transfer/index.md#internal-transfer> "Internal Transfer") for how to do this efficiently.

The same principle applies to `datacache`, only without a deadline: there is no cleanup policy forcing you to act, but because it is not backed up, the durable copy of anything you want to keep still belongs on the project store.

Scratch is available on more than one file system, on hardware tuned for different access patterns; choosing the right one matters for performance, as explained under [file system suitability](<https://docs.cscs.ch/platforms/mlp/index.md#ref-mlp-storage-suitability> "Scratch").

### Home

Every user has a home path (`$HOME`) mounted at `/users/$USER` on the [Vadret](<https://docs.cscs.ch/alps/storage/index.md#vadret>) filesystem. The home directory has 50 GB of capacity, and is intended for configuration, small software packages and scripts.

### Scratch

Scratch filesystems provide temporary storage for high-performance I/O for executing jobs. Use scratch to store datasets that will be accessed by jobs, and for job output. Scratch is per user - each user gets separate scratch path and quota.

- The environment variable `SCRATCH=/iopsstor/scratch/cscs/$USER` is set automatically when you log into a system of the ML platform, and can be used as a shortcut to access scratch.
- There is an additional scratch path mounted on [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) at `/capstor/scratch/cscs/$USER`.
- There is a further scratch path on [Ritom](<https://docs.cscs.ch/alps/storage/index.md#ritom>) (a VAST file system) at `/ritom/scratch/cscs/$USER`.

> [!WARNING]
>
> **scratch cleanup policy**
>
> - Files on `/iopsstor/scratch/cscs/$USER` that have not been accessed in **14 days** are automatically deleted.
> - Files on `/capstor/scratch/cscs/$USER` that have not been accessed in **30 days** are automatically deleted.
> - The cleanup policy for `/ritom/scratch/cscs/$USER` is being finalised.
>
> **Scratch is not intended for permanent storage**: transfer files back to the capstor project storage after job runs.

> [!NOTE]
>
> **file system suitability**
>
> The Capstor scratch filesystem is based on HDDs and is optimized for large, sequential read and write operations. We recommend using Capstor for storing **checkpoint files** and other **large, contiguous outputs** generated by your training runs. In contrast, Iopsstor uses high-performance NVMe drives, which excel at handling **IOPS-intensive workloads** involving frequent, random access. This makes it a better choice for storing **training datasets**, especially when accessed randomly during machine learning training. Iopsstor is also a smaller and more expensive resource than Capstor, so prefer Capstor unless random-access IOPS is genuinely limiting your workload. Keeping data that does not need fast random access on Capstor leaves Iopsstor capacity available for the jobs that need it. See the [Lustre guide](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") for some hints on how to get the best performance out of the filesystem.

### Scratch Usage Recommendations

Use Iopsstor scratch (`$SCRATCH`) for:

- Training and validation datasets that are read frequently and non-sequentially.
- Workloads that perform many small, random I/O operations.

Use Capstor scratch (`/capstor/scratch/cscs/$USER`) for:

- Storing model checkpoints.
- Outputs from simulations or training jobs that involve large, contiguous I/O.

After your job completes, remember to transfer any important results to your [project store](<https://docs.cscs.ch/storage/filesystems/index.md#store> "Store"), for example with [`rclone` on the `xfer` queue](<https://docs.cscs.ch/storage/transfer/index.md#internal-transfer> "Internal Transfer").

### Project store

The [project store](<https://docs.cscs.ch/storage/filesystems/index.md#store> "Store") (`/capstor/store/cscs/<organization>/<project>`) is persistent, backed-up storage for datasets, shared code and configuration scripts that need to be accessed from different vClusters. It has no cleanup policy, and is per project: each project gets a folder with a project [quota](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3> "Quota") on capacity and inodes. Hard limits prevent writing once the quota is reached; you can check usage with the [`quota`](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3> "Quota") command on a login node or ela.

Writing to the project store directly from jobs is not recommended: stage data to scratch or the project data cache for a run, and keep the durable copy here.

> [!NOTE]
>
> **requesting more project storage**
>
> Ask your PI to open a [CSCS Service Desk](<https://jira.cscs.ch/plugins/servlet/desk>) ticket describing the use case and the additional space and inodes required. CSCS then reviews the request before increasing the quota.

### Project data cache

`datacache` is a project-level working area on the fast [Iopsstor](<https://docs.cscs.ch/alps/storage/index.md#iopsstor>) file system, mounted at `/iopsstor/datacache/cscs/<organization>/<project>`. It gives the whole project one shared, high-performance copy of the datasets its members actively work on, so users no longer stage a private copy of the same data on their own scratch.

Like scratch, it is fast NVMe storage and is **not backed up**. Unlike scratch, it has **no cleanup policy**: files are never deleted automatically, and the project owns its data lifecycle and space hygiene within a project [quota](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3> "Quota") on capacity and inodes, as for the project store.

Because nothing here is backed up, `datacache` is a *manual* cache: CSCS never copies its contents anywhere else, so the durable copy of anything you keep must live on the [project store](<https://docs.cscs.ch/storage/filesystems/index.md#store> "Store") (`/capstor/store`, which is backed up). A typical workflow keeps the authoritative dataset on the project store, stages it once into `datacache` where the whole project reads it at NVMe speed during training, and moves anything worth preserving back to the project store afterwards.

> [!NOTE]
>
> **requesting a project data cache**
>
> A `datacache` area is **not provisioned by default**, unlike the project store. Ask your PI to open a [CSCS Service Desk](<https://jira.cscs.ch/plugins/servlet/desk>) ticket describing the use case and the space and inodes required. CSCS then reviews the request before creating the area. Without justification, a small project can request up to 100GB and 1M inodes, and a large project can request up to 1TB and 5M inodes, for the whole duration of the project.
>
> Requesting more resources than the default limits above must be properly justified, and a contact person that will be responsible for the data management should be provided. The extra storage capacity will be typically provided only for a specific amount of time, and not for the whole project duration.
