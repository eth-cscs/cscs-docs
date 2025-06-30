[](){#ref-storage-fs}
# File Systems

!!! note
    The different file systems provided on the Alps platforms and policies like quotas and backups are documented here.
    The file systems available on a [cluster][ref-alps-clusters] and policy details are determined by the [cluster][ref-alps-clusters]'s [platform][ref-alps-platforms].
    Please read the documentation for the clusters that you are working on after reviewing this documentation.

<div class="grid cards" markdown>

-   :fontawesome-solid-hard-drive: __File Systems__

    There are three *types* of file system that are provided on Alps clusters:

    |                               |    [backups][ref-storage-backups]  |  [snapshot][ref-storage-snapshots]  |   [cleanup][ref-storage-cleanup]   |    access |
    | ---------                     | ---------- | ---------- | ----------- | --------- |
    | [Home][ref-storage-home]      |    yes     |  yes       |    no       |   user    |
    | [Scratch][ref-storage-scratch]|    no      |  no        |    yes      |   user    |
    | [Store][ref-storage-store]    |    yes     |  no        |    no       |   project |

</div>

<div class="grid cards" markdown>

-   :fontawesome-solid-floppy-disk: __Backups__

    There are two forms of data [backup][ref-storage-backup] that are provided on some file systems.

    [:octicons-arrow-right-24: Backups][ref-storage-backups]

    [:octicons-arrow-right-24: Snapshots][ref-storage-snapshots]

-   :fontawesome-solid-broom: __Cleanup__

    Data retention policies and automatic cleanup of Scratch.

    [:octicons-arrow-right-24: Cleanup policies][ref-storage-cleanup]

-   :fontawesome-solid-layer-group: __Quota__

    Find out about quota on capacity and file counts, and how to check your quota limits.

    [:octicons-arrow-right-24: Quota][ref-storage-quota]

-   :fontawesome-solid-circle-question: __Troubleshooting__

    Answers to common issues and questions.

    [:octicons-arrow-right-24: common questions][ref-storage-troubleshooting]

</div>

[](){#ref-storage-home}
## Home

The Home file system is mounted on every cluster, and is referenced by the environment variable `$HOME`.
It is a relatively small storage for files such as source code or shell scripts and configuration files, provided on the [VAST][ref-alps-vast] file system.

!!! example "Home on Daint"
    The Home path for the user `$USER` is mounted at `/users/$USER`.
    For example, the user `bcumming` on [Daint][ref-cluster-daint]:
    ```console
    $ ssh daint.alps.cscs.ch
    $ echo $HOME
    /users/bcumming
    ```

### Cleanup and expiration

There is no [cleanup policy][ref-storage-cleanup] on Home, and the contents are retained for three months after your last project finishes.

### Quota

All users get a [quota][ref-storage-quota] of 50 GB and 500,000 inodes in Home.

### Backups

Daily [snapshots][ref-storage-snapshots] for the last seven days are provided in the hidden directory `$HOME/.snapshot`.

!!! under-construction "Backup is not yet available on Home"
    [Backups][ref-storage-backups] to tape storage are currently being implemented for Home directories.

[](){#ref-storage-scratch}
## Scratch

The Scratch file system is a fast workspace tuned for use by parallel jobs, with an emphasis on performance over reliability, hosted on the [Capstor][ref-alps-capstor] Lustre filesystem.
See the [Lustre guide][ref-guides-storage-lustre] for some hints on how to get the best performance out of the filesystem.

All users on Alps get their own Scratch path, `/capstor/scratch/cscs/$USER`, which is pointed to by the variable `$SCRATCH` on the [HPC Platform][ref-platform-hpcp] and [Climate and Weather Platform][ref-platform-cwp] clusters Eiger, Daint and Santis.

!!! info "`$SCRATCH` on MLP points to Iopsstor"
    On the machine learning platform (MLP) systems [clariden][ref-cluster-clariden] and [bristen][ref-cluster-bristen] the `$SCRATCH` variable points to storage on [Iopstore][ref-alps-iopsstor].
    See the [MLP docs][ref-mlp-storage] for more information.

### Cleanup and expiration

The [cleanup policy][ref-storage-cleanup] is enforced on Scratch, to ensure continued performance of the file system.

* Files not accessed in the last 30 days are automatically deleted.
* When capacity grows above:
    * 60%: users are asked to start removing or archiving unneeded files
    * 80%: CSCS will start removing files and paths without further notice.

### Quota

A [soft quota][ref-storage-quota-types] is enforced on the Scratch file system, with a grace period to allow data transfer.

Every user gets the following [quota][ref-storage-quota]:

* 150 TB of disk space;
* 1 million inodes;
* and a soft quota grace period of two weeks.

!!! important
    In order to prevent a degradation of the file system performance, please check your disk space and inode usage with the command [`quota`][ref-storage-quota-cli].
    Even if you are not close to the quota, please endeavor to reduce usage wherever possible to improve user experience for everybody on the system.

### Backups

There are no backups on Scratch.
Please ensure that you move important data to a file system with backups, for example [Store][ref-storage-store].

[](){#ref-storage-store}
## Store

Store is a large, medium-performance, storage on the [Capstor][ref-alps-capstor] Lustre file system for sharing data within a project, and for medium term data storage.
See the [Lustre guide][ref-guides-storage-lustre] for some hints on how to get the best preformance out of the filesystem.

Space on Store is allocated per-project, with a path created for each project.
To accomodate the different customers and projects on Alps, the project paths are organised as follows:

```
/capstor/store/<tenant>/<customer>/<group_id>
```

* **`tenant`**: there are currently two tenants, `cscs` and `mch`:
    * the vast majority of projects are hosted by the `cscs` tenant.
* **`customer`**: refers to the contractual partner responsible for the project.
   Examples of customers include:
    * `userlab`: projects allocated in the CSCS User Lab through open calls. The majority of projects are hosted here, particularly on the [HPC platform][ref-platform-hpcp].
    * `swissai`: most projects allocated on the [Machine Learning Platform][ref-platform-mlp].
    * `2go`: projects allocated under the [CSCS2GO](https://2go.cscs.ch) scheme.
* **`group_id`**: refers to the linux group created for the project.

??? example "Which groups and projects am I a member of?"
    Users often are part of multiple projects, and by extension their associated `groupd_id` groups.
    You can get a list of your groups using the `id` command in the terminal:
    ```console
    $ id $USER
    uid=12345(bobsmith) gid=32819(g152) groups=32819(g152),33119(g174),32336(vasp6)
    ```
    Here the user `bobsmith` is in three projects (`g152`, `g174` and `vasp6`), with the project `g152` being their **primary project**. 
    In the terminal, use the following command to find your **primary group**:
    ```console
    $ id -gn $USER
    g152
    ```

!!! info "The `$STORE` environment variable"
    On some clusters, for example, [Eiger][ref-cluster-eiger] and [Daint][ref-cluster-daint], the project folder for your primary project can be accessed using the `$STORE` environment variable.

!!! warning "Avoid using Store for jobs"
    Store is tuned for storing results and shared datasets, specifically it has fewer meta data servers assigned to it.

    Use the Scratch file systems, which are tuned for fast parallel I/O, for storing input and output for jobs.

### Cleanup and expiration

There is no [cleanup policy][ref-storage-cleanup] on Store, and the contents are retained for three months after the project ends.

### Quota

Paths on Store is allocated per-project: a path is created for each project with a [quota][ref-storage-quota] based on the initial resource request.
Users have read and write access to the Store paths for each project that they are a member of, and you can check the quota on Store for all of your projects using the [`quota`][ref-storage-quota-cli] tool.

### Backups

[Backups][ref-storage-backups] are performed on Store, with the three most recent copies of every file backed up to tape every 24 hours.

[](){#ref-storage-quota}
## Quota

Storage quota is a limit on available storage applied to:

* **capacity**: the total size of files;
* and **inodes**: the total number of files and directories.

??? note "What is an inode?"
    inodes are data structures that describe Linux file system objects like files and directories - every file and directory has a corresponding inode.

    Large inode counts degrade file system performance in multiple ways.
    For example, Lustre file systems have separate metadata and data management.
    Excessive inode usage can overwhelm the metadata services, causing degradation across the file system.

!!! tip "Consider compressing paths to reduce inode usage"
    Consider archiving folders that you are not actively using with the tar command to reduce used capacity and the number of inodes.

    Consider compressing directories full of many small input files as SquashFS images (see the following example of generating [SquashFS images][ref-guides-storage-venv] for an example) - which pack many files into a single file that can be mounted to access the contents efficiently.

!!! tip "Update file timestamps when unpacking tar files"
    The default behavior of the `tar` command is to retain the access date of the original file when unpacking tar balls.
    When unpacking on a file system with [cleanup policy][ref-storage-cleanup], use the `--touch` flag with `tar` to ensure that the files won't be cleaned up prematurely.
    For example:
    ```console
    $ tar --touch -xvf data_archive.tgz
    ```

There are two types of quota:

[](){#ref-storage-quota-types}

* **Soft quota** when exceeded there is a grace period for transferring or deleting files, before it will become a hard quota.
* **Hard quota** when exceeded no more files can be written.

!!! todo
    Storage team: can you please provide better/more complete definitions of the hard and soft quotas.

[](){#ref-storage-quota-cli}
### Checking quota

You can check your storage quotas with the command `quota` on the front-end system Ela (`ela.cscs.ch`) and the login nodes of [Daint][ref-cluster-daint], [Santis][ref-cluster-santis], [Clariden][ref-cluster-clariden] and [Eiger][ref-cluster-eiger].

The tool shows available capacity and used capacity for each file system that you have access to.
If you are in multiple projects, information for the [Store][ref-storage-store] path for each project that you are a member of will be shown.

??? example "Checking your quota on Ela"
    ```console
    $ ssh user@ela.cscs.ch
    $ quota
    Retrieving data ...

    User: user
    Usage data updated on: 2025-05-21 11:10:02
    +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
    |                                             |        User quota       |          Proj quota         |         User files         |    Proj files    |             |
    +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
    | Directory                          | FS     |   Used |    % |   Grace |   Used |    % | Quota limit |     Used |    % |    Grace |      Used |    % | Files limit |
    +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
    | /iopsstor/scratch/cscs/user        | lustre |  32.0G |    - |       - |      - |    - |           - |     7746 |    - |        - |         - |    - |           - |
    | /capstor/users/cscs/user           | lustre |   3.2G |  6.4 |       - |      - |    - |       50.0G |    14471 |  2.9 |        - |         - |    - |      500000 |
    | /capstor/store/cscs/director2/g33  | lustre |   1.9T |  1.3 |       - |      - |    - |      150.0T |   146254 | 14.6 |        - |         - |    - |     1000000 |
    | /capstor/store/cscs/cscs/csstaff   | 263.9T | 88.0 |      - |    - |      300.0T | 18216778 | 91.1 |         - |    - |    20000000 |
    | /capstor/scratch/cscs/user         | lustre | 243.0G |  0.2 |       - |      - |    - |      150.0T |   336479 | 33.6 |        - |         - |    - |     1000000 |
    | /vast/users/cscs/user              | vast   |  11.7G | 23.3 | Unknown |      - |    - |       50.0G |    85014 | 17.0 |  Unknown |         - |    - |      500000 |
    +------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
    ```


    Here the user is in two projects, namely `g33` and `csstaff`, for which the quota for their respective paths in `/capstor/store` are reported.

[](){#ref-storage-backup}
## Backup

There are two methods for retaining backup copies of data on CSCS file systems, namely [backups][ref-storage-backups] and [snapshots][ref-storage-backups].

[](){#ref-storage-backups}
### Backups

Backups store copies of files on slow, high-capacity, tape storage.
The backup process checks for modified or new files every 24 hours, and makes a copy on tape of every new or modified file.

* up to three copies of a file are stored (the three most recent copies).

!!! question "How do I restore from a backup?"
    Open a [service desk](https://jira.cscs.ch/plugins/servlet/desk/site/global) ticket with *request type* "Storage and File systems" to restore a file or directory.

    Please provide the following information in the request:

    * the **full path** to restore, e.g.:
        * a file: `/capstor/scratch/cscs/userbob/software/data/results.tar.gz`
        * or a directory: `/capstor/scratch/cscs/userbob/software/data`.
    * the **date** to restore from:
        * the most recent backup older than the date will be used.

[](){#ref-storage-snapshots}
### Snapshots

A snapshot is a full copy of a file system at a certain point in time, that can be accessed via a special hidden directory.

!!! note "Where are snapshots available?"
    Currently, only the [Home][ref-storage-home] file system provides snapshots, with snapshots of the last 7 days available in the path `$HOME/.snapshot`.

??? example "Accessing snapshots on Home"
    The snapshots for [Home][ref-storage-home] are in the hidden `.snapshot` path in Home (the path is not visible even to `ls -a`)
    ```console
    $ ls $HOME/.snapshot
    big_catalog_2025-05-21_08_49_34_UTC
    big_catalog_2025-05-21_09_19_34_UTC
    users_2025-05-14_22_59_00_UTC
    users_2025-05-15_22_59_00_UTC
    users_2025-05-16_22_59_00_UTC
    users_2025-05-17_22_59_00_UTC
    users_2025-05-18_22_59_00_UTC
    users_2025-05-19_22_59_00_UTC
    users_2025-05-20_22_59_00_UTC
    ```

[](){#ref-storage-cleanup}
## Cleanup policies

The performance of Lustre file systems is affected by file system occupancy and the number of files.
Ideally occupancy should not exceed 60%, with severe performance degradation for all users when occupancy exceeds 80% and when there are too many small files.

File cleanup removes files that are not being used to ensure that occupancy and file counts do not affect file system performance.

A daily process removes files that have not been **accessed (either read or written)** in the last 30 days.

??? example "How can I tell when a file was last accessed?"
    The access time of a file can be found using the `stat` command.
    For example, to get the access time of the file `./src/affinity.h`:

    ```console
    $ stat -c %x ./src/affinity.h
    2025-05-23 16:27:40.580767016 +0200
    ```

!!! warning "Do not artificially update the access time of files"
    It is not allowed to automatically or artificially update the access time of files to avoid the cleanup policy, and CSCS scans for these activities.

    Please move data to a file system that is suitable for persistant storage instead.

In addition to the automatic deletion of old files, if occupancy exceeds 60% the following steps are taken to maintain performance of the file system:

* **Occupancy ≥ 60%**: CSCS will ask users to take immediate action to remove unnecessary data.
* **Occupancy ≥ 80%**: CSCS will start manually removing files and folders without further notice.

!!! info "How do I ensure that important data is not cleaned up?"
    File systems with cleanup, namely [Scratch][ref-storage-scratch], are not intended for long term storage.
    Copy the data to a file system designed for file storage that does not have a cleanup policy, for example [Store][ref-storage-store].

[](){#ref-storage-troubleshooting}
## Frequently asked questions

??? question "My files are gone, but the directories are still there"
    When the [cleanup policy][ref-storage-cleanup] is applied on Lustre file systems, the files are removed, but the directories remain.

??? question "What do messages like `mkdir: cannot create directory 'test': Disk quota exceeded` mean?"
    You have run out of quota on the target file system.
    Consider deleting unneeded files, or moving data to a different file system.
    Specifcially, if you see this message when using [Home][ref-storage-home], which has a relatively small 50 GB limit, consider moving the data to your project's [Store][ref-storage-store] path.

!!! todo
    FAQ question: [writing with specific group access](https://confluence.cscs.ch/spaces/KB/pages/276955350/Writing+on+project+if+you+belong+to+more+than+one+group)


