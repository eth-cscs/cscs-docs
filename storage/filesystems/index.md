# File Systems

> [!NOTE]
>
> The different file systems provided on the Alps platforms and policies like quotas and backups are documented here. The file systems available on a [cluster](<https://docs.cscs.ch/clusters/index.md#alps-clusters> "Alps Clusters") and policy details are determined by the [cluster](<https://docs.cscs.ch/clusters/index.md#alps-clusters> "Alps Clusters")’s [platform](<https://docs.cscs.ch/alps/platforms/index.md#platforms-on-alps> "Platforms on Alps"). Please read the documentation for the clusters that you are working on after reviewing this documentation.

- **File Systems**

  There are three *types* of file system that are provided on Alps clusters:

  |  | [backups](<https://docs.cscs.ch/storage/filesystems/index.md#backups_3> "Backups") | [snapshot](<https://docs.cscs.ch/storage/filesystems/index.md#snapshots> "Snapshots") | [cleanup](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies") | access |
  | --- | --- | --- | --- | --- |
  | [Home](<https://docs.cscs.ch/storage/filesystems/index.md#home>) | yes | yes | no | user |
  | [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>) | no | no | yes | user |
  | [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) | yes | no | no | project |

- **Backups**

  There are two forms of data [backup](<https://docs.cscs.ch/storage/filesystems/index.md#backup> "Backup") that are provided on some file systems.

  [Backups](<https://docs.cscs.ch/storage/filesystems/index.md#backups_3>)

  [Snapshots](<https://docs.cscs.ch/storage/filesystems/index.md#snapshots>)
- **Cleanup**

  Data retention policies and automatic cleanup of Scratch.

  [Cleanup policies](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies>)
- **Quota**

  Find out about quota on capacity and file counts, and how to check your quota limits.

  [Quota](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3>)
- **Troubleshooting**

  Answers to common issues and questions.

  [common questions](<https://docs.cscs.ch/storage/filesystems/index.md#frequently-asked-questions> "Frequently asked questions")

## Home

The Home file system is mounted on every cluster, and is referenced by the environment variable `$HOME`. It is a relatively small storage for files such as source code or shell scripts and configuration files, provided on the [Vadret](<https://docs.cscs.ch/alps/storage/index.md#vadret>) file system.

> [!NOTE]
>
> **Home on Daint**
>
> The Home path for the user `$USER` is mounted at `/users/$USER`. For example, the user `bcumming` on [Daint](<https://docs.cscs.ch/clusters/daint/index.md#daint>):
>
> ```console
> $ ssh daint.alps.cscs.ch
> $ echo $HOME
> /users/bcumming
> ```

### Cleanup and expiration

There is no [cleanup policy](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies") on Home, and the contents are retained for three months after your last project finishes.

### Quota

All users get a [quota](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3> "Quota") of 50 GB and 500,000 inodes in Home.

### Backups

Daily [snapshots](<https://docs.cscs.ch/storage/filesystems/index.md#snapshots> "Snapshots") for the last seven days are provided in the hidden directory `$HOME/.snapshot`.

> [!NOTE]
>
> **Backup is not yet available on Home**
>
> [Backups](<https://docs.cscs.ch/storage/filesystems/index.md#backups_3>) to tape storage are currently being implemented for Home directories.

## Scratch

The Scratch file system is a fast workspace tuned for use by parallel jobs, with an emphasis on performance over reliability, hosted on the [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) Lustre filesystem or the [Ritom](<https://docs.cscs.ch/alps/storage/index.md#ritom>) VAST NFS filesystem. See the [Lustre guide](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") and [VAST guide](<https://docs.cscs.ch/guides/storage/index.md#vast-tuning-on-ritom> "VAST tuning on Ritom") for some hints on how to get the best performance out of each filesystem.

All users on Alps get their own Scratch path. On the [HPC Platform](<https://docs.cscs.ch/platforms/hpcp/index.md#hpc-platform>) clusters Eiger, Daint it points to `/ritom/scratch/cscs/$USER`, on the [Climate and Weather Platform](<https://docs.cscs.ch/platforms/cwp/index.md#climate-and-weather-platform>) cluster Santis it points to `/capstor/scratch/cscs/$USER`.

> [!NOTE]
>
> **`$SCRATCH` on MLP points to Iopsstor**
>
> On the machine learning platform (MLP) systems [clariden](<https://docs.cscs.ch/clusters/clariden/index.md#clariden> "Clariden") and [bristen](<https://docs.cscs.ch/clusters/bristen/index.md#bristen> "Bristen") the `$SCRATCH` variable points to storage on [Iopsstor](<https://docs.cscs.ch/alps/storage/index.md#iopsstor>). See the [MLP docs](<https://docs.cscs.ch/platforms/mlp/index.md#file-systems-and-storage> "File Systems and Storage") for more information.

### Cleanup and expiration

The [cleanup policy](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies") is enforced on Scratch, to ensure continued performance of the file system.

- Files on `/capstor/scratch/cscs/$USER` and `/ritom/scratch/cscs/$USER` that have not been accessed in **30 days** are automatically deleted.
- Files on `/iopsstor/scratch/cscs/$USER` that have not been accessed in **14 days** are automatically deleted.
- When capacity grows above:

  - 60%: users are asked to start removing or archiving unneeded files
  - 80%: CSCS will start removing files and paths without further notice.

> [!WARNING]
>
> **Hidden directories are excluded from the cleaning policy**
>
> The following directories are automatically created by the system and are **not** subject to the cleaning policy. They will never be automatically deleted:
>
> - `.uenv-images`: used by [uenv](<https://docs.cscs.ch/software/uenv/index.md#uenv>) as the default repository for [managing uenv images](<https://docs.cscs.ch/software/uenv/management/index.md#managing-uenvs> "Managing uenvs").
>
> Using this directory to store general data in order to circumvent the cleaning policy is a violation of CSCS usage policies.
>
> This directory can consume significant disk space and inodes over time. If you no longer need the environments stored there, you can safely remove them manually to free up space.
>
> Note that the following directories **are** subject to the cleaning policy and their contents will be removed if not accessed within the retention period:
>
> - `.enroot`: container images downloaded by the user
> - `.edf_imagestore`: container images used by the [Container Engine](<https://docs.cscs.ch/software/container-engine/index.md#container-engine>)

### Quota

A [soft quota](<https://docs.cscs.ch/storage/filesystems/index.md#ref-storage-quota-types> "Quota") is enforced on the Scratch file system, with a grace period to allow data transfer.

Every user gets the following [quota](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3> "Quota"):

- 150 TB of disk space;
- 1 million inodes;
- and a soft quota grace period of two weeks.

> [!IMPORTANT]
>
> In order to prevent a degradation of the file system performance, please check your disk space and inode usage with the command [`quota`](<https://docs.cscs.ch/storage/filesystems/index.md#checking-quota> "Checking quota"). Even if you are not close to the quota, please endeavor to reduce usage wherever possible to improve user experience for everybody on the system.

### Backups

There are no backups on Scratch. Please ensure that you move important data to a file system with backups, for example [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>).

## Store

Store is a large, medium-performance, storage on the [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) Lustre file system for sharing data within a project, and for medium term data storage. See the [Lustre guide](<https://docs.cscs.ch/guides/storage/index.md#lustre-tuning> "Lustre tuning") for some hints on how to get the best performance out of the filesystem.

Space on Store is allocated per-project, with a path created for each project. To accomodate the different customers and projects on Alps, the project paths are organised as follows:

```text
/capstor/store/<tenant>/<customer>/<group_id>
```

- **`tenant`**: there are currently two tenants, `cscs` and `mch`:

  - the vast majority of projects are hosted by the `cscs` tenant.
- **`customer`**: refers to the contractual partner responsible for the project. Examples of customers include:

  - `userlab`: projects allocated in the CSCS User Lab through open calls. The majority of projects are hosted here, particularly on the [HPC platform](<https://docs.cscs.ch/platforms/hpcp/index.md#hpc-platform> "HPC Platform").
  - `swissai`: most projects allocated on the [Machine Learning Platform](<https://docs.cscs.ch/platforms/mlp/index.md#machine-learning-platform> "Machine learning platform").
  - `2go`: projects allocated under the [CSCS2GO](<https://2go.cscs.ch>) scheme.
- **`group_id`**: refers to the linux group created for the project.

> [!NOTE]
>
> **Which groups and projects am I a member of?**
>
> Users often are part of multiple projects, and by extension their associated `groupd_id` groups. You can get a list of your groups using the `id` command in the terminal:
>
> ```console
> $ id $USER
> uid=12345(bobsmith) gid=32819(g152) groups=32819(g152),33119(g174),32336(vasp6)
> ```
>
> Here the user `bobsmith` is in three projects (`g152`, `g174` and `vasp6`), with the project `g152` being their **primary project**. In the terminal, use the following command to find your **primary group**:
>
> ```console
> $ id -gn $USER
> g152
> ```

> [!NOTE]
>
> **The `$STORE` environment variable**
>
> On some clusters, for example, [Eiger](<https://docs.cscs.ch/clusters/eiger/index.md#eiger>) and [Daint](<https://docs.cscs.ch/clusters/daint/index.md#daint>), the project folder for your primary project can be accessed using the `$STORE` environment variable.

> [!WARNING]
>
> **Avoid using Store for jobs**
>
> Store is tuned for storing results and shared datasets, specifically it has fewer meta data servers assigned to it.
>
> Use the Scratch file systems, which are tuned for fast parallel I/O, for storing input and output for jobs.

### Cleanup and expiration

There is no [cleanup policy](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies") on Store, and the contents are retained for three months after the project ends.

### Quota

Paths on Store is allocated per-project: a path is created for each project with a [quota](<https://docs.cscs.ch/storage/filesystems/index.md#quota_3> "Quota") based on the initial resource request. Users have read and write access to the Store paths for each project that they are a member of, and you can check the quota on Store for all of your projects using the [`quota`](<https://docs.cscs.ch/storage/filesystems/index.md#checking-quota> "Checking quota") tool.

### Backups

[Backups](<https://docs.cscs.ch/storage/filesystems/index.md#backups_3>) are performed on Store, with the three most recent copies of every file backed up to tape every 24 hours.

## Quota

Storage quota is a limit on available storage applied to:

- **capacity**: the total size of files;
- and **inodes**: the total number of files and directories.

> [!NOTE]
>
> **What is an inode?**
>
> inodes are data structures that describe Linux file system objects like files and directories - every file and directory has a corresponding inode.
>
> Large inode counts degrade file system performance in multiple ways. For example, Lustre file systems have separate metadata and data management. Excessive inode usage can overwhelm the metadata services, causing degradation across the file system.

> [!TIP]
>
> **Consider compressing paths to reduce inode usage**
>
> Consider archiving folders that you are not actively using with the tar command to reduce used capacity and the number of inodes.
>
> Consider compressing directories full of many small input files as SquashFS images (see the following example of generating [SquashFS images](<https://docs.cscs.ch/guides/storage/index.md#squash-python-virtual-environments-with-uenv> "Squash Python virtual environments with uenv") for an example) - which pack many files into a single file that can be mounted to access the contents efficiently.

> [!TIP]
>
> **Update file timestamps when unpacking tar files**
>
> The default behavior of the `tar` command is to retain the access date of the original file when unpacking tar balls. When unpacking on a file system with [cleanup policy](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies"), use the `--touch` flag with `tar` to ensure that the files won’t be cleaned up prematurely. For example:
>
> ```console
> $ tar --touch -xvf data_archive.tgz
> ```

There are two types of quota:

- **Soft quota** when exceeded there is a grace period for transferring or deleting files, before it will become a hard quota.
- **Hard quota** when exceeded no more files can be written.

### Checking quota

You can check your storage quotas with the command `quota` on the front-end system Ela (`ela.cscs.ch`) and the login nodes of [Daint](<https://docs.cscs.ch/clusters/daint/index.md#daint>), [Santis](<https://docs.cscs.ch/clusters/santis/index.md#santis>), [Clariden](<https://docs.cscs.ch/clusters/clariden/index.md#clariden>) and [Eiger](<https://docs.cscs.ch/clusters/eiger/index.md#eiger>).

The tool shows available capacity and used capacity for each file system that you have access to. If you are in multiple projects, information for the [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) path for each project that you are a member of will be shown.

> [!NOTE]
>
> **Checking your quota on Ela**
>
> ```console
> $ ssh user@ela.cscs.ch
> $ quota
> Retrieving data ...
>
> User: user
> Usage data updated on: 2025-05-21 11:10:02
> +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
> |                                             |        User quota       |          Proj quota         |         User files         |    Proj files    |             |
> +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
> | Directory                          | FS     |   Used |    % |   Grace |   Used |    % | Quota limit |     Used |    % |    Grace |      Used |    % | Files limit |
> +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
> | /iopsstor/scratch/cscs/user        | lustre |  32.0G |    - |       - |      - |    - |           - |     7746 |    - |        - |         - |    - |           - |
> | /capstor/users/cscs/user           | lustre |   3.2G |  6.4 |       - |      - |    - |       50.0G |    14471 |  2.9 |        - |         - |    - |      500000 |
> | /capstor/store/cscs/director2/g33  | lustre |   1.9T |  1.3 |       - |      - |    - |      150.0T |   146254 | 14.6 |        - |         - |    - |     1000000 |
> | /capstor/store/cscs/cscs/csstaff   | 263.9T | 88.0 |      - |    - |      300.0T | 18216778 | 91.1 |         - |    - |    20000000 |
> | /capstor/scratch/cscs/user         | lustre | 243.0G |  0.2 |       - |      - |    - |      150.0T |   336479 | 33.6 |        - |         - |    - |     1000000 |
> | /vast/users/cscs/user              | vast   |  11.7G | 23.3 | Unknown |      - |    - |       50.0G |    85014 | 17.0 |  Unknown |         - |    - |      500000 |
> +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
> ```
>
> Here the user is in two projects, namely `g33` and `csstaff`, for which the quota for their respective paths in `/capstor/store` are reported. Note that the path `/vast/users/cscs/user` is mounted at `/users/user` (i.e. `$HOME`) on Alps.

## Backup

There are two methods for retaining backup copies of data on CSCS file systems, namely [backups](<https://docs.cscs.ch/storage/filesystems/index.md#backups_3> "Backups") and [snapshots](<https://docs.cscs.ch/storage/filesystems/index.md#backups_3> "Backups").

### Backups

Backups store copies of files on slow, high-capacity, tape storage. The backup process checks for modified or new files every 24 hours, and makes a copy on tape of every new or modified file.

- up to three copies of a file are stored (the three most recent copies).

> [!NOTE]
>
> **How do I restore from a backup?**
>
> Open a [service desk](<https://jira.cscs.ch/plugins/servlet/desk/site/global>) ticket with *request type* “Storage and File systems” to restore a file or directory.
>
> Please provide the following information in the request:
>
> - the **full path** to restore, e.g.:
>
>   - a file: `/capstor/store/cscs/your_project/software/data/results.tar.gz`
>   - or a directory: `/capstor/store/cscs/your_project/software/data`.
> - the **date** to restore from:
>
>   - the most recent backup older than the date will be used.

### Snapshots

A snapshot is a full copy of a file system at a certain point in time, that can be accessed via a special hidden directory.

> [!NOTE]
>
> **Where are snapshots available?**
>
> Currently, only the [Home](<https://docs.cscs.ch/storage/filesystems/index.md#home>) file system provides snapshots, with snapshots of the last 7 days available in the path `$HOME/.snapshot`.

> [!NOTE]
>
> **Accessing snapshots on Home**
>
> The snapshots for [Home](<https://docs.cscs.ch/storage/filesystems/index.md#home>) are in the hidden `.snapshot` path in Home (the path is not visible even to `ls -a`)
>
> ```console
> $ ls $HOME/.snapshot
> big_catalog_2025-05-21_08_49_34_UTC
> big_catalog_2025-05-21_09_19_34_UTC
> users_2025-05-14_22_59_00_UTC
> users_2025-05-15_22_59_00_UTC
> users_2025-05-16_22_59_00_UTC
> users_2025-05-17_22_59_00_UTC
> users_2025-05-18_22_59_00_UTC
> users_2025-05-19_22_59_00_UTC
> users_2025-05-20_22_59_00_UTC
> ```

## Cleanup policies

The performance of Lustre file systems is affected by file system occupancy and the number of files. Ideally occupancy should not exceed 60%, with severe performance degradation for all users when occupancy exceeds 80% and when there are too many small files.

File cleanup removes files that are not being used to ensure that occupancy and file counts do not affect file system performance.

A daily process removes files that have not been **accessed (either read or written)** within the retention period:

- **30 days** on [Capstor](<https://docs.cscs.ch/alps/storage/index.md#capstor>) (`/capstor/scratch/cscs/$USER`)
- **14 days** on [Iopsstor](<https://docs.cscs.ch/alps/storage/index.md#iopsstor>) (`/iopsstor/scratch/cscs/$USER`)

> [!NOTE]
>
> **How can I tell when a file was last accessed?**
>
> The access time of a file can be found using the `stat` command. For example, to get the access time of the file `./src/affinity.h`:
>
> ```console
> $ stat -c %x ./src/affinity.h
> 2025-05-23 16:27:40.580767016 +0200
> ```

> [!WARNING]
>
> **Do not artificially update the access time of files**
>
> It is not allowed to automatically or artificially update the access time of files to avoid the cleanup policy, and CSCS scans for these activities.
>
> Please move data to a file system that is suitable for persistent storage instead.

In addition to the automatic deletion of old files, if occupancy exceeds 60% the following steps are taken to maintain performance of the file system:

- **Occupancy ≥ 60%**: CSCS will ask users to take immediate action to remove unnecessary data.
- **Occupancy ≥ 80%**: CSCS will start manually removing files and folders without further notice.

> [!NOTE]
>
> **How do I ensure that important data is not cleaned up?**
>
> File systems with cleanup, namely [Scratch](<https://docs.cscs.ch/storage/filesystems/index.md#scratch>), are not intended for long term storage. Copy the data to a file system designed for file storage that does not have a cleanup policy, for example [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>).

## Frequently asked questions

> [!NOTE]
>
> **My files are gone, but the directories are still there**
>
> When the [cleanup policy](<https://docs.cscs.ch/storage/filesystems/index.md#cleanup-policies> "Cleanup policies") is applied on Lustre file systems, the files are removed, but the directories remain.

> [!NOTE]
>
> **What do messages like `mkdir: cannot create directory 'test': Disk quota exceeded` mean?**
>
> You have run out of quota on the target file system. Consider deleting unneeded files, or moving data to a different file system. Specifically, if you see this message when using [Home](<https://docs.cscs.ch/storage/filesystems/index.md#home>), which has a relatively small 50 GB limit, consider moving the data to your project’s [Store](<https://docs.cscs.ch/storage/filesystems/index.md#store>) path.

> [!NOTE]
>
> **Todo**
>
> FAQ question: [writing with specific group access](<https://confluence.cscs.ch/spaces/KB/pages/276955350/Writing+on+project+if+you+belong+to+more+than+one+group>)
