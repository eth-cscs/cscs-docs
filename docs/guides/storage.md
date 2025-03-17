[](){#ref-guides-storage}
# Storage

## Many small files vs. HPC File Systems

Workloads that read or create many small files are not well-suited to parallel file systems, which are designed for parallel and distributed I/O.

Workloads that do not play nicely with Lustre include:

* Configuration and compiling applications.
* Using Python virtual environments

At first it can seem strange that a "high-performance" file system is significantly slower than a laptop drive for a "simple" task like compilation or loading Python modules, however Lustre is designed for high-bandwidth parallel file access from many nodes at the same time, with the attendant trade offs this implies.

Meta data lookups on Lustre are expensive compared to your laptop, where the local file system is able to agressively cache meta data.

### Python virtual environments with uenv

Python virtual environments can be very slow on Lustre, for example a simple `import numpy` command run on Lustre might take seconds, compared to milliseconds on your laptop.

The main reasons for this include:

* Python virtual environments contain many small files, on which Python performs `stat()`, `open()` and `read()` commands when loading a module.
* Python pre-compiles `.pyc` files for each `.py` file in a project.
* All of these operations create a lot of meta-data lookups.

As a result, using virtual environments can be slow, and these problems are only exacerbated when the virtual environment is loaded simultaneously by many ranks in an MPI job.

One solution is to use the tool `mksquashfs` to compresses the contents of a directory - files, inodes and sub-directories - into a single file.
This file can be mounted as a read-only [Squashfs](https://en.wikipedia.org/wiki/SquashFS) file system, which is much faster because a single file is accessed instead of the many small files that were in the original environment.


#### Step 1: create the virtual environment

The first step is to create the virtual environment using the usual workflow.

=== "uv"

    The recommended way to create a new virtual environment is to use the [uv](https://docs.astral.sh/uv/) tool, which supports _relocatable_ virtual environments and asynchronous package downloads. The main benefit of a relocatable virtual environment is that it does not need to be created in the final path from where it will be used. This allows the use of shared memory to speed up the creation and initialization of the virtual environment and, since the virtual environment can be used from any location, the resulting squashfs image can be safely shared across projects.

    ```bash
    # start the uenv
    # in this case the "default" view of prgenv-gnu provides python, cray-mpich,
    # and other useful tools
    uenv start prgenv-gnu/24.11:v1 --view=default

    # create and activate a new relocatable venv using uv
    # in this case we explicitly select python 3.12
    uv venv -p 3.12 --relocatable --link-mode=copy /dev/shm/sqfs-demo/.venv
    cd /dev/shm/sqfs-demo
    source .venv/bin/activate

    # install software in the virtual environment using uv
    # in this case we install install pytorch
    uv pip install --link-mode=copy torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cu126

    # optionally, to reduce the import times, precompile all
    # python modules to bytecode before creating the squashfs image
    python -m compileall -j 8 -o 1 -o 2 .venv/lib/python3.12/site-packages
    ```

=== "venv"

    A new virtual environment can also be created using the standard `venv` module. However, virtual environments created by `venv` are not relocatable, and thus they need to be created and initialized in the path from where they will be used. This implies that the installation process can not be optimized for file system performance and will still be slow on Lustre filesystems.

    ```bash
    # start the uenv
    # in this case the "default" view of prgenv-gnu provides python, cray-mpich,
    # and other useful tools
    uenv start prgenv-gnu/24.11:v1 --view=default

    # for the example create a working path on SCRATCH
    mkdir $SCRATCH/sqfs-demo
    cd $SCRATCH/sqfs-demo

    # create and activate the empty venv
    python -m venv ./.venv
    source ./.venv/bin/activate

    # install software in the virtual environment
    # in this case we install install pytorch
    pip install torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cu126
    ```

??? example "how many files did that create?"
    An inode is created for every file, directory and symlink on a file system.
    In order to optimise performance, we want to reduce the number of inodes (i.e. the number of files and directories).

    The following command can be used to count the number of inodes:
    ```
    find $SCRATCH/sqfs-demo/.venv -exec stat --format="%i" {} + | sort -u | wc -l
    ```
    `find` is used to list every path and file, and `stat` is called on each of these to get the inode, and then `sort` and `wc` are used to count the number of unique inodes.

    In our "simple" pytorch example, I counted **22806 inodes**!


#### Step 2: make a squashfs image of the virtual environment

The next step is to create a single squashfs file that contains the whole virtual environment folder (i.e. `/dev/shm/sqfs-demo/.venv` or `$SCRATCH/sqfs-demo/.venv`).

This is performed using the `mksquashfs` command, that is installed on all Alps clusters.

=== "uv"

    ```bash
    mksquashfs /dev/shm/sqfs-demo/.venv py_venv.squashfs \
        -no-recovery -noappend -Xcompression-level 3
    ```

=== "venv"

    ```bash
    mksquashfs $SCRATCH/sqfs-demo/.venv py_venv.squashfs \
        -no-recovery -noappend -Xcompression-level 3
    ```

!!! hint
    The `-Xcompression-level` flag sets the compression level to a value between 1 and 9, with 9 being the most compressed.
    We find that level 3 provides a good trade off between the size of the compressed image and performance: both [uenv][ref-uenv] and the [container engine][ref-container-engine] use level 3.

??? warning "I am seeing errors of the form `Unrecognised xattr prefix...`"
    You can safely ignore the (possibly many) warning messages of the form:
    ```
    Unrecognised xattr prefix lustre.lov
    Unrecognised xattr prefix system.posix_acl_access
    Unrecognised xattr prefix lustre.lov
    Unrecognised xattr prefix system.posix_acl_default
    ```

!!! tip
    The default installed version of `mksquashfs` on Alps does not support the best `zstd` compression method.
    Every uenv contains a better version of `mksquashfs`, which is used by the uenv to compress itself when it is built.

    The exact location inside the uenv depends on the target architecture, and version, and will be of the form:
    ```
    /user-environment/linux-sles15-${arch}/gcc-7.5.0/squashfs-${version}-${hash}/bin/mksquashfs
    ```
    Use this version for the best results, though it is also perfectly fine to use the system version.

#### Step 3: use the squashfs

To use the optimised virtual environment, mount the squashfs image at the location of the original virtual environment when starting the uenv.

=== "uv"

    ```bash
    cd $SCRATCH/sqfs-demo
    uenv start --view=default \
        prgenv-gnu/24.11:v1,$PWD/py_venv.squashfs:$SCRATCH/sqfs-demo/.venv
    source .venv/bin/activate
    ```

    Remember that virtual environments created by `uv` are relocatable only if the `--relocatable` option flag is passed to the `uv venv` command as mentioned in step 1. In that case, the generated environment is relocatable and thus it is possible to mount it in multiple locations without problems.

=== "venv"

    ```bash
    cd $SCRATCH/sqfs-demo
    uenv start --view=default \
        prgenv-gnu/24.11:v1,$PWD/py_venv.squashfs:$SCRATCH/sqfs-demo/.venv
    source .venv/bin/activate
    ```

    Note that the original virtual environment is still installed in `$SCRATCH/sqfs-demo/.venv`, however the squashfs image has been mounted on top of it, so the single squashfs file is being accessed instead of the many files in the original version.

    A benefit of this approach is that the squashfs file can be copied to a location that is not subject to the Scratch cleaning policy.

    !!! warning
        Virtual environments created by `venv` are not relocatable as they contain symlinks to absolute locations inside the virtual environment. This means that the squashfs file must be mounted in the exact same location where the virtual environment was created.

#### Step 4: (optional) regenerate the virtual environment

The squashfs file is immutable - it is not possible to modify the contents of `.venv` while it is mounted.
This means that it is not possible to `pip install` more packages in the virtual environment.

If you need to modify the virtual environment, run the original uenv without the squashfs file mounted, make changes to the virtual environment, and run step 2 again to generate a new image.

!!! hint
    If you save the updated copy in a different file, you can now "roll back" to the old version of the environment by mounting the old image.
