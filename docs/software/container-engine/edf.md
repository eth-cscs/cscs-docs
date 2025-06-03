[](){#ref-ce-edf-reference}
# EDF Reference

EDF files use the [TOML format](https://toml.io/en/). For details about the data types used by the different parameters, please refer to the [TOML spec webpage](https://toml.io/en/v1.0.0).

## EDF fields

In the following, the default value is none (i.e., the empty value of the corresponding type) if not specified.

### (ARRAY or STRING) base_environment

Ordered list of EDFs that this file inherits from. Parameters from listed environments are evaluated sequentially. Supports up to 10 levels of recursion.

??? note
     * Parameters from the listed environments are evaluated sequentially, adding new entries or overwriting previous ones, before evaluating the parameters from the current EDF. In other words, the current EDF inherits the parameters from the EDFs listed in `base_environment`. When evaluating `mounts` or `env` parameters, values from downstream EDFs are appended to inherited values.
     * The individual EDF entries in the array follow the same search rules as the arguments of the `--environment` CLI option for Slurm; they can be either file paths or filenames without extension if the file is located in the [EDF search path][ref-ce-edf-search-path].
     * This parameter can be a string if there is only one base environment.

??? example
     * Single environment inheritance:
        ```bash
        base_environment = "common_env"
        ```

     * Multiple environment inheritance:
        ```bash
        base_environment = ["common_env", "ml_pytorch_env1"]
        ```

### (STRING) image

The container image to use. Can reference a remote Docker/OCI registry or a local Squashfs file as a filesystem path.

??? note
     * The full format for remote references is `[USER@][REGISTRY#]IMAGE[:TAG]`.
         * `[REGISTRY#]`: (optional) registry URL, followed by #. Default: Docker Hub.
         * `IMAGE`: image name.
         * `[:TAG]`: (optional) image tag name, preceded by :.
     * The registry user can also be specified in the `$HOME/.config/enroot/.credentials` file.

??? example
     * Reference of Ubuntu image in the Docker Hub registry (default registry)
        ```bash
        image = "library/ubuntu:24.04"
        ```

     * Explicit reference of Ubuntu image in the Docker Hub registry
        ```bash
        image = "docker.io#library/ubuntu:24.04"
        ```

     * Reference to PyTorch image from NVIDIA Container Registry (nvcr.io)
        ```bash
        image = "nvcr.io#nvidia/pytorch:22.12-py3"
        ```

     * Image from third-party quay.io registry
        ```bash
        image = "quay.io#madeeks/osu-mb:6.2-mpich4.1-ubuntu22.04-arm64"
        ```

     * Reference to a manually pulled image stored in parallel FS
        ```bash
        image = "/path/to/image.squashfs"
        ```

### (STRING) workdir

Initial working directory when the container starts. Default: inherited from image.

??? example
     * Workdir pointing to a user defined project path 
        ```bash
        workdir = "/home/user/projects"
        ```
     * Workdir pointing to the `/tmp` directory
        ```bash
        workdir = "/tmp"
        ```

### (BOOL) entrypoint

If true, run the entrypoint from the container image. Default: true.

??? example
    ```bash
    entrypoint = false
    ```

### (BOOL) writable

If false, the container filesystem is read-only. Default: true.

??? example
    ```bash
    writable = true
    ```

### (ARRAY) mounts

List of bind mounts in the format `SOURCE:DESTINATION[:FLAGS]`. Flags are optional and can include `ro`, `private`, etc.

??? note
    * Mount flags are separated with a plus symbol, for example: `ro+private`.
    * Optional flags from docker format or OCI (need reference)

??? example

     * Literal fixed mount map
        ```bash
        mounts = ["/capstor/scratch/cscs/amadonna:/capstor/scratch/cscs/amadonna"]
        ```

     * Mapping path with `env` variable expansion
        ```bash
        mounts = ["/capstor/scratch/cscs/${USER}:/capstor/scratch/cscs/${USER}"]
        ```

     * Mounting the scratch filesystem using a host environment variable
        ```bash
        mounts = ["${SCRATCH}:/scratch"]
        ```


### (TABLE) env

Environment variables to set in the container. Null-string values will unset the variable. Default: inherited from the host and the image.

??? note
    * By default, containers inherit environment variables from the container image and the host environment, with variables from the image taking precedence.
    * The env table can be used to further customize the container environment by setting, modifying, or unsetting variables.
    * Values of the table entries must be strings. If an entry has a null value, the variable corresponding to the entry key is unset in the container.


??? example

     * Basic `env` block
        ```bash
        [env]
        MY_RUN = "production",
        DEBUG = "false"
        ```

     * Use of environment variable expansion
        ```bash
        [env]
        MY_NODE = "${VAR_FROM_HOST}",
        PATH = "${PATH}:/custom/bin", 
        DEBUG = "true"
        ```


### (TABLE) annotations

OCI-like annotations for the container. For more details, refer to the [Annotations][ref-ce-annotations] section.

??? example

     * Disabling the CXI hook
        ```bash
        [annotations]
        com.hooks.cxi.enabled = "false"
        ```

     * Control of SSH hook parameters via annotation and variable expansion
        ```bash
        [annotations.com.hooks.ssh]
        authorize_ssh_key = "/capstor/scratch/cscs/${USER}/tests/edf/authorized_keys"
        enabled = "true"
        ```

     * Alternative example for usage of annotation with fixed path
        ```bash
        [annotations]
        com.hooks.ssh.authorize_ssh_key = "/path/to/authorized_keys"
        com.hooks.ssh.enabled = "true"
        ```

!!! note
    Environment variable expansion and relative paths expansion are only available on the Bristen vCluster as technical preview.

## Environment variable expansion

Environment variable expansion allows for dynamic substitution of environment variable values within the EDF (Environment Definition File). This capability applies across all configuration parameters in the EDF, providing flexibility in defining container environments.

 * *Syntax*. Use `${VAR}` to reference an environment variable `VAR`. The variable's value is resolved from the combined environment, which includes variables defined in the host and the container image, the later taking precedence.
 * *Scope*. Variable expansion is supported across all EDF parameters. This includes EDF’s parameters like mounts, workdir, image, etc. For example, `${SCRATCH}` can be used in mounts to reference a directory path.
 * *Undefined Variables*. Referencing an undefined variable results in an error. To safely handle undefined variables, you can use the syntax ${VAR:-}, which evaluates to an empty string if VAR is undefined.
 * *Preventing Expansion*. To prevent expansion, use double dollar signs $$. For example, `$${VAR}` will render as the literal string `${VAR}`.
 * *Limitations*
    * Variables defined within the `[env]` EDF table cannot reference other entries from `[env]` tables in the same or other EDF files (e.g. the ones entered as base environments). Therefore, only environment variables from the host can be referenced.  
 * *Environment Variable Resolution Order*. The environment variables in containers are set based on the following order: 
    * EDF env: Variable values as defined in EDF’s `[env]` table.
    * Container Image: Variables defined in the container image's environment take precedence.
    * Host Environment: Environment variables defined in the host system.

## Relative paths expansion

Relative filesystem paths can be used within EDF parameters, and will be expanded by the CE at runtime. The paths are interpreted as relative to the working directory of the process calling the CE, not to the location of the EDF file.
