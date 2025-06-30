[](){#ref-alps-storage}
# Alps Storage

!!! under-construction

The Alps infrastructure offers multiple storage solutions, each with characteristics suited to different workloads and use cases.
HPC storage is provided by independent clusters, composed of servers and physical storage drives.

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

Capstor and Iopsstor are on the same Slingshot network as Alps, while VAST is on the CSCS Ethernet network.

See the [Lustre guide][ref-guides-storage-lustre] for some hints on how to get the best performance out of the filesystem.

The mounts, and how they are used for Scratch, Store, and Home file systems that are mounted on clusters are documented in the [file system docs][ref-storage-fs].

[](){#ref-alps-capstor}
## Capstor

Capstor is the largest file system, and it is meant for storing large amounts of input and output data.
It is used to provide [scratch][ref-storage-scratch] and [store][ref-storage-store].

Capstor has 80 Object Storage Servers ([OSS](https://wiki.lustre.org/Lustre_Object_Storage_Service_(OSS))), and 6 Metadata Servers ([MDS](https://wiki.lustre.org/Lustre_Metadata_Service_(MDS))). 
Two of of these Metadata servers are dedicated for Store, and the remaining four are dedicated for Scratch.

[](){#ref-alps-capstor-scratch}
### Scratch

All users on Alps get their own scratch path on Alps, `/capstor/scratch/cscs/$USER`.
Since Capstor OSSs are made of HDDs, Capstor is a storage well suited for jobs which perform large sequential and parallel read/write operations.
See the [Scratch documentation][ref-storage-scratch] for more information.

[](){#ref-alps-capstor-store}
### Store

The [Store][ref-storage-store] mount point on Capstor provides stable storage with [backups][ref-storage-backups] and no [cleaning policy][ref-storage-cleanup].
It is mounted on clusters at the `/capstor/store` mount point, with folders created for each project.

[](){#ref-alps-iopsstor}
## Iopsstor

Iopsstor is a smaller filesystem compared to Capstor, but it leverages high-performance NVMe drives, which offer significantly better speed and responsiveness than traditional HDDs.
It is primarily used as a scratch space, and it is optimized for IOPS-intensive workloads. 
This makes it particularly well-suited for applications that involve frequent, random read and write operations within files.

Iopsstor has has 20 OSSs, and 2 MDSs. 

[](){#ref-alps-vast}
## VAST

The VAST storage is smaller capacity system that is designed for use as [Home][ref-storage-home] folders.

!!! todo
    small text explaining what VAST is designed to be used for.


