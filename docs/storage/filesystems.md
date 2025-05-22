[](){#ref-storage-fs}
# File Systems

The file systems available on a [cluster][ref-alps-clusters] are determined by the cluster's [platform][ref-alps-platforms].


Low level information about `/capstor/store/cscs/<customer>/<group_id>` from [KB](https://confluence.cscs.ch/spaces/KB/pages/879142656/capstor+store) can be put into a folded admonition.

Broadly speaking, there are three types of file system, tabulated below

| file system                   |    backup  |  snapshot  |   cleanup   |    access |
| ---------                     | ---------- | ---------- | ----------- | --------- |
| [Home][ref-storage-home]      |    yes     |  yes       |    no       |   user    |
| [Scratch][ref-storage-scratch]|    no      |  no        |    yes      |   user    |
| [Store][ref-storage-store]    |    yes     |  no        |    no       |   project |

## Backup and Snapshots



[](){#ref-storage-home}
## Home

The home filesystem is mounted on every cluser, and is referenced by the environment variable `$HOME`.
Home is a relatively small storage for files such as source code or shell scripts and configuration files.

!!! example "Home on Daint"
    The home path for the user `$USER` is mounted at `/users/$USER`, for example the user `bcumming` on [Daint][ref-cluster-daint]:
    ```console
    $ ssh daint.alps.cscs.ch
    $ echo $HOME
    /users/bcumming
    ```

Home is provided by the [VAST][ref-alps-vast] filesystem.

!!! warning "Backup is not yet available"
    

* Vast
* everybody gets the same amount
* user-specific
* no cleanup policy
* quota?
* backup:
    * snapshots of the last 7 days are available in `HOME/.snapshot` (not visible to `ls`)
    * tape storage is not available yet: will follow the "last three copies policy on STORE"

[](){#ref-storage-scratch}
## Scratch

* LUSTRE
* everybody gets the same amount (50 GB)
* user-specific
* cleanup policy is applied (see [soft and hard quotas][ref-storage-quota-types])
* 4/6 meta data servers
* no backups

[](){#ref-storage-store}
## Store

A large, medium performance file system based on Lustre for sharing data within a project, and for medium term data storage.

### Backups

Data on store is backed up to tape every 24 hours, see 


* LUSTRE
* no clean up policy
* duration = lifetime of project + 3 months
* shared by users of a project
* quota is project-specific
* 2/6 Meta data servers - not so hot at many small files
* backups: every 24 hours check for modified files
    * each new or modified file is copied to tape
    * max three copies of a file are kept - the three most recent
    * to restore a backed up file create an SD ticket with
        * request to restor from backup
        * the full file or path to restore
        * the date to restore from: the most most recent backup older than the date will be provided

[](){#ref-storage-quota}
## Quota

Storage quota is a maximum limit on available storage, with different quotas applied to.

Quota can apply to:

* **capacity**: the total size of files.
* **inodes**: the total number of files and directories.

??? note "What is an inode?"
    inodes are data structures that describe Linux file system objects like files and directories - every file and directory has a corresponding inode.

    Large inode counts degrade file system performance in multiple ways.
    For example, Lustre filesystems have separate metadata and data management.
    Excessive inode usage can overwhelm the metadata services, causing degradation across the filesystem.

??? tip "Consider compressing paths to reduce inode usage"
    Consider archiving folders that you are not actively using with the tar command in order to keep low the number of files owned by users and groups.

    Consider compressing directories full of many small input files as SquashFS images (see the following example of generating [SquashFS images][ref-guides-storage-venv] for an example) - which pack many files into a single file that can be mounted to access the contents efficiently.


There are two types of quota:

[](){#ref-storage-quota-types}

* **Hard quotas** when exceeded no more files can be written.
* **Soft quota** when exceeded there is a grace period for transfering or deleting files, before it will become a hard quota.

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
| /capstor/scratch/cscs/user         | lustre | 243.0G |  0.2 |       - |      - |    - |      150.0T |   336479 | 33.6 |        - |         - |    - |     1000000 |
| /vast/users/cscs/user              | vast   |  11.7G | 23.3 | Unknown |      - |    - |       50.0G |    85014 | 17.0 |  Unknown |         - |    - |      500000 |
+------------------------------------+--------+--------+------+---------+--------+------+-------------+----------+------+----------+-----------+------+-------------+
```

## Backup

There are two methods for retaining backup copies of data on CSCS filesystems -- backup and snapshot -- documented below.

### Backups

Backups store copies of files on slow, high-capacity, tape storage.
The backup process checks for modified or new files every 24 hours, and makes a copy on tape of every new or modified file.

* up to three copies of a file are stored (the three most recent copies).

!!! question "How do I restore from a backup?"
    Open a [service desk](https://jira.cscs.ch/plugins/servlet/desk/site/global) ticket with "request type "Storage and Filesystems" to restore a file or directory.
    The ticket must provide the following information:

    * the **full path** to restore, e.g.:
        * a file: `/capstor/scratch/cscs/userbob/software/data/images.tar.gz`;
        * or a directory: `/capstor/scratch/cscs/userbob/software/data`.
    * the **date** to restore from:
        * the most recent backup older than the date will be used.

### Snapshots

A snapshot is a full copy of a filesystem at a certain point in time, that can be accessed via a special hidden directory.
Currently snapshots of the last 7 days are provided for the [Home][ref-storage-home] filesystem.

!!! example "Accessing snapshots on Home"
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

* snapshots of the last 7 days are available in `HOME/.snapshot` (not visible to `ls`)

[](){#ref-storage-cleanup}
## cleanup policies


## Common Questions

??? question "my files are gone, but the directories are still there"
    When the [cleanup policy][ref-storage-cleanup] is applied on LUSTRE file systems, the files are removed, but the directories remain to remind you of what was but no longer is.
