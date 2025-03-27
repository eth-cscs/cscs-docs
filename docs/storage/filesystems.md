[](){#ref-storage-fs}
# File Systems

!!! todo
    these are already out of date and need significant refactoring to be coherently linked to cluster definitions.

CSCS supports different file systems, whose specifications are summarized in the table below:


Please build big software projects not fitting `$HOME` on `$PROJECT` instead.
Since you should not run jobs from `$HOME` or `$PROJECT`, please copy the executables, libraries and data sets needed to run your simulations to `$SCRATCH` with the Slurm transfer queue.

Users can also write temporary builds on `/dev/shm`, a filesystem using virtual memory rather than a persistent storage device: please note that files older than 24 hours will be deleted automatically.

[](){#ref-storage-quota}
## Quota

You can check your storage quotas with the command quota on the front-end system ela (ela.cscs.ch) and the login nodes of [eiger][ref-cluster-eiger], [daint][ref-cluster-daint], [santis][ref-cluster-santis], and [clariden][ref-cluster-clariden].

```bash
$ quota
Retrieving data ...

User: testuser
Usage data updated on: 2025-02-21 16:01:27
+------------------------------------+--------+-----+-------+----+-------------+----------+-----+---------+------+-------------+
|                                    |  User quota  | Proj quota |             |   User files   |   Proj files   |             |
+------------------------------------+--------+-----+-------+----+-------------+----------+-----+---------+------+-------------+
| Directory                          |   Used |   % |  Used |  % | Quota limit |     Used |   % |    Used |    % | Files limit |
+------------------------------------+--------+-----+-------+----+-------------+----------+-----+---------+------+-------------+
| /iopsstor/scratch/cscs/testuser    |   4.0K |   - |     - |  - |           - |        1 |   - |       - |    - |           - |
| /capstor/scratch/cscs/testuser     |   8.0K | 0.0 |     - |  - |      150.0T |        2 | 0.0 |       - |    - |     1000000 |
| /users/testuser                    |  32.0K | 0.0 |     - |  - |       50.0G |       42 | 0.0 |       - |    - |      500000 |
+------------------------------------+--------+-----+-------+----+-------------+----------+-----+---------+------+-------------+
```

Quotas apply to the total size of stored data, and in some cases to the number of [inodes](https://en.wikipedia.org/wiki/Inode), to the filesystems on Alps.
The command reports both disk space and the number of files for each filesystem/directory.

??? note "what is an inode"
    inodes are data structures that describe Linux file system objects like files and directories - every file and directory has a corresponding inode.

    Large inode counts degrade file system performance in multiple ways.
    For example, Lustre filesystems have separate metadata and data management.
    Excessive inode usage can overwhelm the metadata services, causing degradation across the filesystem.

    !!! tip
        Consider archiving folders with the tar command in order to keep low the number of files owned by users and groups.

    !!! tip
        Consider compressing directories full of many small input files as squashfs images - which pack many files into a single file that can be mounted to access the contents efficiently.

!!! note
    The size of the quota depends on the file system, platform and project.

[](){#ref-storage-cleaning}

## Cleaning Policy and Data Retention


## Scratch

The scratch file system is designed for performance rather than reliability, as a fast workspace for temporary storage.
All CSCS systems provide a scratch personal folder for users that can be accessed through the environment variable `$SCRATCH`.

Alps provides a Lustre scratch file system mounted on `/capstor/scratch/cscs`, while other clusters share the GPFS scratch file system under `/scratch/shared`.

### Soft Quota

No strict quotas are enforced on scratch, but the scratch file system on Alps (`/capstor/scratch/cscs`) has a soft quota on both disk occupancy and inodes (files and folders), with a grace period to allow data transfer.
Note that when the grace time expires, the soft quotas will become hard limits if you are over quota, therefore you won’t be able to write any longer on your personal scratch folder.

Alps (Eiger) users need to check their disk space and inodes usage with the command quota, that is available on the front end Ela and on Eiger User Access Nodes (UANs) as well. Currently the soft quotas are 150 TB disk space and 1 million inodes on Alps scratch file system, with a grace time of two weeks.

### Cleaning Policy

Please note that a cleaning policy is in place on scratch: all files older than 30 days will be deleted by a script that runs daily, so please ensure that you do not target this filesystem as a long term storage.
Furthermore, kindly note that in order to avoid performance and stability issues on the scratch filesystem, if the occupancy grows above the critical limit of 60% we will be forced to ask you immediate action to remove unnecessary data: if the occupancy continues to grow and we reach 80%, we will then need to free up disk space manually removing files and folders without further notice.

As a matter of fact, when the occupancy goes above 80% the Lustre filesystem shows a performance degradation that affects all users.
The same applies with large numbers of small files, since the Lustre filesystem is not behaving ideally when dealing with high volumes of small files.

Keep also in mind that data on scratch are not backed up, therefore users are advised to move valuable data to the /project filesystem or alternative storage facilities as soon as batch jobs are completed.

!!! note
    Do not use the `touch` command to prevent the cleaning policy from removing files, because this behaviour would deprive the community of a shared resource.

## Users

Users are not supposed to run jobs from this filesystem because of the low performance. In fact the emphasis on the `/users` filesystem is reliability over performance: all home directories are backed up with GPFS snapshots and no cleaning policy is applied.

### Quota

The $HOME environment variable points to the personal folder /users/<username>: please, keep in mind that you cannot exceed the 50 GB - 500 K files quota enforced on $HOME.
Expiration

!!! warning
    All data will be deleted 3 months after the closure of the user account without further warning.

## Store on Capstore

The `/capstor/store` mount point of the Lustre file system `capstor` is intended for high-performance per-project storage on Alps. The mount point is accessible from the User Access Nodes (UANs) of Alps vClusters.

!!! note
    Capstore store is not yet mounted on Eiger.

!!! info
    `/capstor/store` is equivalent to the  `/project` and `/store` GPFS mounts on the old Daint system.

The mount point features subfolders named after tenants and customers: on `daint.alps`, the only tenant currently available is CSCS, therefore all customer folders are located under the folder `/capstor/store/cscs` 

* UserLab customers can access their project folder on daint.alps  with the `$PROJECT` environment variable, that targets the personal folder `/capstor/store/cscs/userlab/group_id/$USER`.
* Please note that users need to create their own sub-folders under the project folder, as they are not created automatically.
* Contractual partners will find their project folder under the corresponding contractual name listed in `/capstor/store/cscs`. For instance, EMPA users will have their projects listed under the `/capstor/store/cscs/empa` folder, and so on 

Data on `/capstor/store` is backed up with no cleaning policy: it provides intermediate storage space for datasets, shared code or configuration scripts that need to be accessed from different vClusters.
The performance of the Lustre file system (read and write) increases using larger files, therefore you should consider to archive small files with the tar utility.
Quota

### Quota

Access to `/capstor/store` is granted to all users with a production or large development project upon request at the time of proposal submission: please note that applicants should justify the requested storage as well as they do for compute resources. Each group folder has a quota space allocated that allows maximum 1 M files and 150 TB of disk space at present.
Expiration 

!!! warning
    All data will be deleted 3 months after the end of the project without further warning!

## Project

This is a shared - parallel file system based on the IBM GPFS software.
It is accessible from the login nodes of all CSCS platforms using the native GPFS client through Infiniband or ethernet, however it is mounted read-only on the compute nodes of the Cray computing systems.

!!! warning
    Users are not allowed to run jobs from this file system because of the low performance. 

The `$PROJECT` environment variable targets the personal folder `/project/<group_id>/$USER` on the GPFS: please note that users need to create their own sub-folders under the project folder, as they are not created automatically.
Data is backed up with GPFS snapshots and no cleaning policy is applied: it provides intermediate storage space for datasets, shared code or configuration scripts that need to be accessed from different platforms.
Read and write performance increase using larger files, therefore you should consider to archive small files with the tar utility.

### Quota

Access to `/project` is granted to all users with a production or large development project upon request at the time of proposal submission: please note that applicants should justify the requested storage as well as they do for compute resources.
Each group folder has a quota space allocated that allows maximum 50 K files per TB of disk space.
Expiration

!!! warning
    All data will be deleted 3 months after the end of the project without further warning.

## Store

Users are NOT supposed to run jobs from this filesystem because of the low performance.
This is a shared - parallel filesystem based on the IBM GPFS software.
It is accessible from the login nodes of all CSCS platforms using the native GPFS client through Infiniband or ethernet, however it is mounted read-only on the compute nodes of the Cray computing systems.

Data is backed up with GPFS snapshots and no cleaning policy is applied: it provides long term storage for large amount of datasets, code or scripts that need to be accessed from different platforms.
It is also intended for large files: performance increases when using larger files, therefore you should consider archiving small files with the tar utility.

### Quota

Access to /store can only be bought signing a contract with CSCS. Data and inode quotas are group based: the quota is enforced according to the signed contract, with maximum 50 K files per TB of disk space.
Expiration

!!! warning
    All data will be deleted 3 months after the end of the contract.
