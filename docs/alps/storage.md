[](){#ref-alps-storage}
# Alps Storage

!!! under-construction

Alps has different storage attached, each with characteristics suited to different workloads and use cases.
HPC storage is managed in a separate cluster of nodes that host servers that manage the storage and the physical storage drives.
These separate clusters are on the same Slingshot 11 network as Alps.

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


!!! todo
    Information about Lustre. Meta data servers, etc.

    * how many meta data servcers on capstor and iopstor
    * how these are distributed between store/scratch

    Also discuss how capstor and iopstor are used to provide both scratch / store / other file systems

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

The Store mount point on Capstor provides stable storage with [backups][ref-storage-backups] and no [cleaning policy][ref-storage-cleanup].
It is mounted on clusters at the `/capstor/store` mount point, with folders created for each project.

To accomodate the different customers and projects on Alps, the directory structure is more complicated than the per-user paths on Scratch.
Project paths are organised as follows:

```
/capstor/store/<tenant>/<customer>/<group_id>
```

!!! question "What are `tenant`, `customer` and `group_id` in this context?"

    * **`tenant`**: there are currently two tenants, `cscs` and `mch`:
        * the vast majority of projects are hosted by the `cscs` tenant.
    * **`customer`**: refers to the contractual partner responsible for the project.
       Examples of customers include:
        * `userlab`: projects allocated in the CSCS User Lab through open calls. The majority of projects are hosted here, particularly on the [HPC platform][ref-platform-hpcp].
        * `swissai`: most projects allocated on the [Machine Learning Platform][ref-platform-mlp].
        * `2go`: projects allocated under the [CSCS2GO](https://2go.cscs.ch) scheme.
    * **`group_id`**: refers to the linux group created for the project.

    Users often are part of multiple projects, and by extension their associated `groupd_id` groups.
    You can get a list of your groups using the `id` command in the terminal:
    ```console
    $ id $USER
    uid=22008(bobsmith) gid=32819(g152) groups=32819(g152),33119(g174),32336(vasp6)
    ```
    Here the user `bobsmith` is in three projects, with the project `g152` being their **primary project** (which can also be determined using the `id -gn $USER`).

    * They are also in the `vasp6` group, which users who have been granted access to the [VASP][ref-uenv-vasp] application.

!!! info "The `$PROJECT` environment variable"
    On some clusters, for example [Eiger][ref-cluster-eiger] and [Eiger][ref-cluster-daint], the project folder for your primary project can be accessed using the `$PROJECT` environment variable.

[](){#ref-alps-iopsstor}
## Iopsstor

!!! todo
    small text explaining what iopsstor is designed to be used for.

[](){#ref-alps-vast}
## Vast

The Vast storage is smaller capacity system that is designed for use as home folders.

!!! todo
    small text explaining what iopsstor is designed to be used for.

The mounts, and how they are used for SCRATCH, STORE, PROJECT, HOME would be in the [storage docs][ref-storage-fs]

