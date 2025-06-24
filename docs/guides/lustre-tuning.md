# Lustre Tuning
`/capstor/` and `/iopsstor` are both [lustre](https://lustre.org) filesystem.
Lustre is an open-source, parallel file system used in HPC systems.
As shown in ![Lustre architecture](/images/storage/lustre.png) uses *metadata* servers to store and query metadata which is basically what is shown by `ls`: directory structure, file permission, modification dates,..
This data is globally synchronized, which means that handling many small files is not especially suited for lustre, and the perfomrance of that part is similar on both capstor and iopsstor.
With many small files, a local filesystems like `/dev/shmem/$USER` or "/tmp", if enough memory can be spared for it, can be *much* faster, and offset the packing/unpacking work. Alternatively using a squashed filesystems can be a good option.

The data itself is subdivided in blocks of size `<blocksize>` and is stored by Object Storage Servers (OSS) in one or more Object Storage Targets (OST).
The blocksize and number of OSTs to use is defined by the striping settings. A new file or directory ihnerits them from its parent directory. The `lfs getstripe <path>` command can be used to get information on the actual stripe settings. For directories and empty files `lfs setstripe --stripe-count <count> --stripe-size <size> <directory/file>` can be used to set the layout. The simplest way to have the correct layout is to copy to a directory with the correct layout

A blocksize of 4MB gives good throughput, without being overly big, so it is a good choice when reading a file sequentially or in large chuncks, but if one reads shorter chuncks in random order it might be better to reduce the size, the performance will be smaller, but the performance of your application might actually increase.
https://doc.lustre.org/lustre_manual.xhtml#managingstripingfreespace

!!! example "Good large files settings"
    ```console
    lfs setstripe --stripe-count -1 --stripe-size 4M <big_files_dir>`
    ```

Lustre also supports composite layouts, switching from one layout to another at a given size `--component-end` (`-E`).
With it it is possible to create a Progressive file layout switching `--stripe-count` (`-c`), `--stripe-size` (`-S`), so that fewer locks are required for smaller files, but load is distributed for larger files.

!!! example "Good default settings"
    ```console
    lfs setstripe -E 4M -c 1 -E 64M -c 4 -E -1 -c -1 -S 4M <base_dir>
    ```
