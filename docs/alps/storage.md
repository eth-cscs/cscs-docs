[](){#ref-alps-storage}
# Alps Storage

Alps has different storage attached, each with characteristics suited to different workloads and use cases.
HPC storage is managed in a separate cluster of nodes that host servers that manage the storage and the physical storage drives.
These separate clusters are on the same Slingshot 11 network as the Alps.

|              | Capstor                | Iopsstor               | Vast                |
|--------------|------------------------|------------------------|---------------------|
| Model        | HPE ClusterStor E1000D | HPE ClusterStor E1000F | Vast                |
| Type         | Lustre                 | Lustre                 | NFS                 |
| Capacity     | 129 PB raw GridRAID    | 7.2 PB raw RAID 10     | 1 PB                |
| Number of Drives | 8,480 16 TB HDD    | 240 * 30 TB NVMe SSD   | N/A                 |
| Read Speed   | 1.19 TB/s              | 782 GB/s               | 38 GB/s             |
| Write Speed  | 1.09 TB/s              | 393 GB/s               | 11 GB/s             |
| IOPs         | 1.5M                   | 8.6M read, 24M write   | 200k read, 768k write |
| file create/s| 374k                   | 214k                   | 97k                 |

[](){#ref-alps-capstor}
## capstor

Capstor is the largest file system, for storing large amounts of input and output data.
It is used to provide SCRATCH and STORE for different clusters - the precise details are platform-specific.

[](){#ref-alps-iopsstor}
## iopsstor

!!! todo
    small text explaining what iopsstor is designed to be used for.

[](){#ref-alps-vast}
## vast

The Vast storage is smaller capacity system that is designed for use as home folders.

!!! todo
    small text explaining what iopsstor is designed to be used for.

The mounts, and how they are used for SCRATCH, STORE, PROJECT, HOME would be in the [storage docs][ref-storage-fs]

