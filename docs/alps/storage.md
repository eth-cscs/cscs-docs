[](){#ref-alps-storage}
# Alps Storage

!!! under-construction

Alps has different storage attached, each with characteristics suited to different workloads and use cases.
HPC storage is managed in a separate cluster of nodes that host servers that manage the storage and the physical storage drives.
These separate storage clusters are on the same Slingshot 11 network as Alps.

|              | Capstor                | Iopsstor               | VAST                |
|--------------|------------------------|------------------------|---------------------|
| Model        | HPE ClusterStor E1000D | HPE ClusterStor E1000F | VAST                |
| Type         | Lustre                 | Lustre                 | NFS                 |
| Capacity     | 129 PB raw GridRAID    | 7.2 PB raw RAID 10     | 1 PB                |
| Number of Drives | 8,480 16 TB HDD    | 240 * 30 TB NVMe SSD   | N/A                 |
| Read Speed   | 1.19 TB/s              | 782 GB/s               | 38 GB/s             |
| Write Speed  | 1.09 TB/s              | 393 GB/s               | 11 GB/s             |
| IOPs         | 1.5M                   | 8.6M read, 24M write   | 200k read, 768k write |
| file create/s| 374k                   | 214k                   | 97k                 |


!!! todo
    Information about Lustre. Meta data servers, etc.

    * how many meta data servers on Capstor and Iopsstor
    * how these are distributed between store/scratch

    Also discuss how Capstor and iopstor are used to provide both scratch / store / other file systems

The mounts, and how they are used for Scratch, Store, and Home file systems that are mounted on clusters are documented in the [file system docs][ref-storage-fs].

[](){#ref-alps-capstor}
## Capstor

Capstor is the largest file system, for storing large amounts of input and output data.
It is used to provide [scratch][ref-storage-scratch] and [store][ref-storage-store].

!!! todo "add information about meta data services, and their distribution over scratch and store"

[](){#ref-alps-capstor-scratch}
### Scratch

All users on Alps get their own scratch path on Alps, `/capstor/scratch/cscs/$USER`.

[](){#ref-alps-capstor-store}
### Store

The [Store][ref-storage-store] mount point on Capstor provides stable storage with [backups][ref-storage-backups] and no [cleaning policy][ref-storage-cleanup].
It is mounted on clusters at the `/capstor/store` mount point, with folders created for each project.

[](){#ref-alps-iopsstor}
## Iopsstor

!!! todo
    small text explaining what Iopsstor is designed to be used for.

[](){#ref-alps-vast}
## VAST

The VAST storage is smaller capacity system that is designed for use as [Home][ref-storage-home] folders.

!!! todo
    small text explaining what Iopsstor is designed to be used for.


