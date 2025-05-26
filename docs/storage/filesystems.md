[](){#ref-storage-fs}
# File Systems

!!! todo
    Spellcheck

!!! note
    The different file systems provided on the Alps platforms and policies like quotas and backups are documented here.
    The file systems available on a [cluster][ref-alps-clusters] and the some policy details are determined by the [cluster][ref-alps-clusters]'s [platform][ref-alps-platforms].
    Please read the documentation for the clusters that you are working on after reviewing this documentation.

<div class="grid cards" markdown>

-   :fontawesome-solid-hard-drive: __File Systems__

    There are three *types* of file system that provided on Alps clusters:

    [:octicons-arrow-right-24: Home][ref-storage-home]

    [:octicons-arrow-right-24: Scratch][ref-storage-scratch]

    [:octicons-arrow-right-24: Store][ref-storage-store]

-   :fontawesome-solid-floppy-disk: __Backups__

    There are two forms of data [backup][ref-storage-backup] that are provided on some file systems.

    [:octicons-arrow-right-24: Backups][ref-storage-backups]

    [:octicons-arrow-right-24: Snapshots][ref-storage-snapshots]

-   :fontawesome-solid-broom: __Cleanup__

    Data retention policies and automatic cleanup of Scratch.

    [:octicons-arrow-right-24: Cleanup policies][ref-storage-cleanup]

-   :fontawesome-solid-layer-group: __Quota__

    Find out about limits to capacity and file counts, and how to your quota limits.

    [:octicons-arrow-right-24: Quota][ref-storage-quota]

-   :fontawesome-solid-circle-question: __Troubleshooting__

    Answers to common issues and questions.

    [:octicons-arrow-right-24: common questions][ref-storage-troubleshooting]

</div>

!!! todo
    Low level information about `/capstor/store/cscs/<customer>/<group_id>` from [KB](https://confluence.cscs.ch/spaces/KB/pages/879142656/capstor+store) can be put into a folded admonition.

!!! under-construction
    Broadly speaking, there are three types of file system, tabulated below

| file system                   |    backup  |  snapshot  |   cleanup   |    access |
| ---------                     | ---------- | ---------- | ----------- | --------- |
| [Home][ref-storage-home]      |    yes     |  yes       |    no       |   user    |
| [Scratch][ref-storage-scratch]|    no      |  no        |    yes      |   user    |
| [Store][ref-storage-store]    |    yes     |  no        |    no       |   project |


[](){#ref-storage-home}
## Home

The home file system is mounted on every cluser, and is referenced by the environment variable `$HOME`.
It is a relatively small storage for files such as source code or shell scripts and configuration files, provided on the [VAST][ref-alps-vast] file system.

!!! example "Home on Daint"
    The home path for the user `$USER` is mounted at `/users/$USER`, for example the user `bcumming` on [Daint][ref-cluster-daint]:
    ```console
    $ ssh daint.alps.cscs.ch
    $ echo $HOME
    /users/bcumming
    ```

### Cleanup and Expiration

There is no [cleanup policy][ref-storage-cleanup] on home, and the contents of are retained for three months after your last project finishes.

### Quota

All users get a [quota][ref-storage-quota] of 50 GB and 500,000 inodes.

### Backups

Daily [snapshots][ref-storage-snapshots] for the last seven days are provided in the hidden directory `$HOME/.snapshot`.

!!! under-construction "Backup is not yet available on home"
    [Backups][ref-storage-backups] to tape storage are currently being implemented for home directories.

[](){#ref-storage-scratch}
## Scratch

!!! todo
    The Scratch filesystem is designed for...

    Add some context about performance tuning of this FS for it to meet the requirements

    * 4/6 meta data servers

All users on Alps get `/capstor/scratch/cscs/$USER` path, which is pointed to by the variable `$SCRATCH`.

!!! info "`$SCRATCH` on MLP points to Iopsstore"
    On the MLP systems [clariden][ref-cluster-clariden] and [bristen][ref-cluster-bristen] the `$SCRATCH` variable points to storage on [Iopstore][ref-alps-iopsstor].
    See the [MLP docs][ref-mlp-storage] for more information.

### Cleanup and Expiration

There is no [cleanup policy][ref-storage-cleanup] on home, and the contents of your are retained for three months after your last project finishes.

### Quota

A [soft quota][ref-storage-quota-types] on is enforced on the Scratch file system, with a grace period to allow data transfer.

* 150 TB of disk space
* 1 million inodes
* grace period of two weeks

!!! important
    In order to prevent a degradation of the file system performance, please check your disk space and inode usage with the command [`quota`][ref-storage-quota-cli].
    Even if you are not close to the quota, please endevour to reduce usage wherever possible to improve user experience for everybody on the system.

### Backups

There are no backups on Scratch.
Please ensure that you move important data to a file system with backups, for example [Store][ref-storage-store].

[](){#ref-storage-store}
## Store

A large, medium performance file system based on Lustre for sharing data within a project, and for medium term data storage.

!!! under-construction
    * LUSTRE
    * 2/6 Meta data servers - not so hot at many small files
    * path and quota is project-specific
    * duration = lifetime of project + 3 months
    * shared by users of a project
    * no clean up policy
    * backups: every 24 hours check for modified files

### Backups

!!! under-construction
    Data on store is backed up to tape every 24 hours, see 


[](){#ref-storage-quota}
## Quota

Storage quota is a limit on available storage, that is applied to:

* **capacity**: the total size of files;
* and **inodes**: the total number of files and directories.

??? note "What is an inode?"
    inodes are data structures that describe Linux file system objects like files and directories - every file and directory has a corresponding inode.

    Large inode counts degrade file system performance in multiple ways.
    For example, Lustre file systems have separate metadata and data management.
    Excessive inode usage can overwhelm the metadata services, causing degradation across the file system.

??? tip "Consider compressing paths to reduce inode usage"
    Consider archiving folders that you are not actively using with the tar command in order to keep low the number of files owned by users and groups.

    Consider compressing directories full of many small input files as SquashFS images (see the following example of generating [SquashFS images][ref-guides-storage-venv] for an example) - which pack many files into a single file that can be mounted to access the contents efficiently.

There are two types of quota:

[](){#ref-storage-quota-types}

* **Soft quota** when exceeded there is a grace period for transfering or deleting files, before it will become a hard quota.
* **Hard quota** when exceeded no more files can be written.

!!! todo
    Storage team: can you please provide better/more complete definitions of the hard and soft quotas.

[](){#ref-storage-quota-cli}
### Checking quota

You can check your storage quotas with the command quota on the front-end system ela (`ela.cscs.ch`) and the login nodes of [daint][ref-cluster-daint], [santis][ref-cluster-santis], [clariden][ref-cluster-clariden] and [eiger][ref-cluster-eiger].

```console
$ ssh user@ela.cscs.ch
$ quota
checking your quota

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

The available capacity and used capacity is show for each filesystem that you have access to.
If you are in multiple projects, information for the [store][ref-storage-store] path for each project that you are a member of will be shown.
In the example above, the user is in two projects, namely `g33` and `csstaff`.

[](){#ref-storage-backup}
## Backup

There are two methods for retaining backup copies of data on CSCS file systems -- [backups][ref-storage-backups] and [snapshots][ref-storage-backups] -- documented below.

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
    Currently, only the [home][ref-storage-home] filesystem provides snapshots, with snapshots of the last 7 days available in the path `$HOME/.snapshot`.

??? example "Accessing snapshots on home"
    The snapshots for [Home][ref-storage-home] are in the hidden `.snapshot` path in home (the path is not visible even to `ls -a`)
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
Ideally occupancy should not exceed 60%, with severe performance degradation for all users when occupancy exceeds 80% or there are too many small files.

File cleanup removes files that are not being used to ensure that occupancy and file counts do not affect file system performance.

A daily process removes files that have not been **accessed (either read or written)** in the last 30 days.

??? example "How can I tell when a file was last accessed?"
    The access time of a file can be found using the `stat` command.
    For example, to get the access time of the file `./src/affinity.h`:

    ```console
    $ stat -c %x ./src/affinity.h
    2025-05-23 16:27:40.580767016 +0200
    ```

In addition to the automatic deletion of old files, if occupancy exceeds 60% the following steps are taken to maintain performance of the filesystem:

* **Occupancy ≥ 60%**: CSCS will ask users to take immediate action to remove uneccesary data.
* **Occupancy ≥ 80%**: CSCS will start manually removing files and folders without further notice.

!!! info "How do I ensure that important data is not purged?"
    File systems with cleanup, namely [Scratch][ref-storage-scratch], are not intended for long term storage.
    Copy the data to a file system designed for file storage that does not have a cleanup policy, for example [Store][ref-storage-store].

[](){#ref-storage-troubleshooting}
## Common Questions

??? question "My files are gone, but the directories are still there"
    When the [cleanup policy][ref-storage-cleanup] is applied on LUSTRE file systems, the files are removed, but the directories remain.

!!! todo
    review KB FAQ for storage questions
