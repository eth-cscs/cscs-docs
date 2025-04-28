[](){#ref-storage-fs}
# File Systems

The file systems available on a [cluster][ref-alps-clusters] are determined by the cluster's [platform][ref-alps-platforms].

Broadly speaking, there are three types of file system:



* Home

Low level information about `/capstor/store/cscs/<customer>/<group_id>` from [KB](https://confluence.cscs.ch/spaces/KB/pages/879142656/capstor+store) can be put into a folded admonition.

## file systems



| file system|    backup  |  snapshot  |   cleanup   |    access |
| --------- | ---------- | ---------- | ----------- | --------- |
| store     |    yes     |  no        |    no       |   project |
| home      |    yes     |  yes       |    no       |   user    |
| scratch   |    no      |  no        |    yes      |   user    |


### home

* Vast
* everybody gets the same amount
* user-specific
* no cleanup policy
* quota?
* backup:
    * snapshots of the last 7 days are available in `HOME/.snapshot` (not visible to `ls`)
    * tape storage is not available yet: will follow the "last three copies policy on STORE"

### scratch

* LUSTRE
* everybody gets the same amount (50 GB)
* user-specific
* cleanup policy is applied (see [soft and hard quotas][ref-storage-quota-types])
* 4/6 meta data servers
* no backups

### store

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

## quota

Storage quota is a maximum limit on available storage, with different quotas applied to.

Quota can apply to:

* **capacity**: the total size of files.
* **inodes**: the total number of files and directories.

!!! note "what is an inode"
    inodes are data structures that describe Linux file system objects like files and directories - every file and directory has a corresponding inode.

    Large inode counts degrade file system performance in multiple ways.
    For example, Lustre filesystems have separate metadata and data management.
    Excessive inode usage can overwhelm the metadata services, causing degradation across the filesystem.

    !!! tip
        Consider archiving folders with the tar command in order to keep low the number of files owned by users and groups.

    !!! tip
        Consider compressing directories full of many small input files as squashfs images - which pack many files into a single file that can be mounted to access the contents efficiently.


There are two types of quota:

[](){#ref-storage-quota-types}

* **Hard quotas** when exceeded no more files can be written.
* **Soft quota** when exceeded there is a grace period for transfering or deleting files, before it will become a hard quota.

checking your quota

## backups

### backup

### snapshot

[](){#ref-storage-cleanup}
## cleanup policies


## Common Questions

??? question "my files are gone, but the directories are still there"
    When the [cleanup policy][ref-storage-cleanup] is applied on LUSTRE file systems, the files are removed, but the directories remain to remind you of what was but no longer is.
