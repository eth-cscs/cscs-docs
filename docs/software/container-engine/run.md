## Running containerized environments

Specifying the `--environment` option to the Slurm command (e.g., `srun` or `salloc`) will make it run inside the EDF environment.
There are three ways to do so:

 1. **Through an absolute path**: an absolute path to EDF. 

    ```console
    $ srun --environment=${HOME}/.edf/ubuntu.toml echo "Hello"
    ```

 2. **Through a relative path**: a path relative from the current working directory (i.e., where the Slurm command is executed). Should be prepended by `./`.

    ```console
    $ srun --environment=./.edf/ubuntu.toml echo "Hello"    # from ${HOME}. 
    ```

 3. **From EDF search paths**: the name of EDF in the [EDF search path][ref-ce-edf-search-path]. `--environment` also accepts the EDF filename without the `.toml` extension:

    ```console 
    $ srun --environment=ubuntu echo "Hello" 
    ```

### Use from batch scripts

Use `--environment` with the Slurm command (e.g., `srun` or `salloc`):

!!! example "`srun` inside a batch script with EDF"
    ```bash
    #!/bin/bash
    #SBATCH --job-name=edf-example
    #SBATCH --time=00:01:00
    ...

    # Run job step
    srun --environment=ubuntu cat /etc/os-release
    ```

Specifying the `--environment` option with an `#SBATCH` option is **experimental**. 
Such usage is discouraged as it may result in unexpected behaviors.

!!! note
    Specifying `--environment` with `#SBATCH` will put the entire batch script inside the containerized environment, requiring the Slurm hook to use any Slurm commands within the batch script (e.g., `srun` or `scontrol`). 
    The hook is controlled by the `ENROOT_SLURM_HOOK` environment variable and activated by default on most vClusters.

[](){#ref-ce-edf-search-path}
### EDF search path

By default, the EDFs for each user are looked up in `${HOME}/.edf`.
The default EDF search path can be changed through the `EDF_PATH` environment variable.
`EDF_PATH` must be a colon-separated list of absolute paths to directories, where the CE searches each directory in order.
If an EDF is located in the search path, its name can be used in the `--environment` option without the `.toml` extension.

!!! example "Using `EDF_PATH` to control the default search path"
    ```console
    $ ls ~/.edf
    ubuntu.toml

    $ ls ~/example-project
    fedora-env.toml

    $ export EDF_PATH="$HOME/example-project"

    $ srun --environment=fedora-env cat /etc/os-release
    NAME="Fedora Linux"
    VERSION="40 (Container Image)"
    ID=fedora
    ...
    ```

## Using container images 

By default, images defined in the EDF as remote registry references (e.g. a Docker reference) are automatically pulled and locally cached.
A cached image would be preferred to pulling the image again in later usage.

An image cache is automatically created at `.edf_imagestore` in the user's scratch folder (i.e., `${SCRATCH}/.edf_imagestore`). Cached images are stored with the corresponding CPU architecture suffix (e.g., `x86` and `aarch64`). Remove the cached image to force re-pull.

An alternative image store path can be specify by defining the environment variable `EDF_IMAGESTORE`. `EDF_IMAGESTORE` must be an absolute path to an existing folder. Image caching may also be disable by setting `EDF_IMAGESTORE` to `void` (currently only available on Daint and Santis).

!!! note
    * If the CE cannot create a directory for the image cache, it operates in cache-free mode, meaning that it pulls an ephemeral image before every container launch and discards it upon termination.
    * Local container images are not cached. See the section below on how to use local images in EDF.

### Pulling images manually

To bypass any caching behavior, users can manually pull an image and directly plug it into their EDF.
To do so, users may execute `enroot import docker://[REGISTRY#]IMAGE[:TAG]` to pull container images from OCI registries to the current directory.

After the import is complete, images are available in Squashfs format in the current directory and can be used in EDFs:

!!! example "Manually pulling an `nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04` image"
    1. Pull the image.

        ```console
        $ cd ${SCRATCH}

        $ enroot import docker://nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04
        [INFO] Querying registry for permission grant
        [INFO] Authenticating with user: <anonymous>
        ...
        Number of gids 1
            root (0)

        $ ls *.sqsh
        nvidia+cuda+11.8.0-cudnn8-devel-ubuntu22.04.sqsh
        ```

    2. Create an EDF referencing the pulled image.

        ```toml
        image = "${SCRATCH}/nvidia+cuda+11.8.0-cudnn8-devel-ubuntu22.04.sqsh"
        ```

!!! note
    It is recommended to save images in `${SCRATCH}` or its subdirectories before using them.

[](){#ref-ce-third-party-private-registries}
### Third-party and private registries

[Docker Hub](https://hub.docker.com/) is the default registry from which remote images are imported.

!!! warning "Registry rate limits"
    Some registries will rate limit image pulls by IP address.
    Since [public IPs are a shared resource][ref-guides-internet-access] we recommend authenticating even for publicly available images.
    For example, [Docker Hub applies its rate limits per user when authenticated](https://docs.docker.com/docker-hub/usage/).

To use an image from a different registry, the corresponding registry URL has to be prepended to the image reference, using a hash character (#) as a separator:

!!! example "Using a third-party registry"
    * Within an EDF

    ```toml
    image = "nvcr.io#nvidia/nvhpc:23.7-runtime-cuda11.8-ubuntu22.04"
    ```

    * On the command line

    ```console
    $ enroot import docker://nvcr.io#nvidia/nvhpc:23.7-runtime-cuda11.8-ubuntu22.04
    ```

To import images from private repositories, access credentials should be configured by individual users in the `$HOME/.config/enroot/.credentials` file, following the [netrc file format](https://everything.curl.dev/usingcurl/netrc).
Using the `enroot import` documentation page as a reference:

??? example "`netrc` example"
    ```console
    # NVIDIA NGC catalog (both endpoints are required)
    machine nvcr.io login $oauthtoken password <token>
    machine authn.nvidia.com login $oauthtoken password <token>

    # DockerHub
    machine auth.docker.io login <login> password <password>

    # Google Container Registry with OAuth
    machine gcr.io login oauth2accesstoken password $(gcloud auth print-access-token)
    # Google Container Registry with JSON
    machine gcr.io login _json_key password $(jq -c '.' $GOOGLE_APPLICATION_CREDENTIALS | sed 's/ /\\u0020/g')

    # Amazon Elastic Container Registry
    machine 12345.dkr.ecr.eu-west-2.amazonaws.com login AWS password $(aws ecr get-login-password --region eu-west-2)

    # Azure Container Registry with ACR refresh token
    machine myregistry.azurecr.io login 00000000-0000-0000-0000-000000000000 password $(az acr login --name myregistry --expose-token --query accessToken  | tr -d '"')
    # Azure Container Registry with ACR admin user
    machine myregistry.azurecr.io login myregistry password $(az acr credential show --name myregistry --subscription mysub --query passwords[0].value | tr -d '"')

    # Github.com Container Registry (GITHUB_TOKEN needs read:packages scope)
    machine ghcr.io login <username> password <GITHUB_TOKEN>

    # GitLab Container Registry (GITLAB_TOKEN needs a scope with read access to the container registry)
    # GitLab instances often use different domains for the registry and the authentication service, respectively
    # Two separate credential entries are required in such cases, for example:
    # Gitlab.com
    machine registry.gitlab.com login <username> password <GITLAB TOKEN>
    machine gitlab.com login <username> password <GITLAB TOKEN>

    # ETH Zurich GitLab registry
    machine registry.ethz.ch login <username> password <GITLAB_TOKEN>
    machine gitlab.ethz.ch login <username> password <GITLAB_TOKEN>  
    ```

## Working with storage

Directories outside a container can be *mounted* inside a container so that the job inside the container can read/write on them. The directories to mount should be specified in EDF with `mounts`. 

!!! example "Specifying directories to mount in EDF"
    * Mount `${SCRATCH}` to `/scratch` inside the container

    ```toml
    mounts = ["${SCRATCH}:/scratch"]
    ```

    * Mount `${SCRATCH}` to `${SCRATCH}` inside the container

    ```toml
    mounts = ["${SCRATCH}:${SCRATCH}"]
    ```

    * Mount `${SCRATCH}` to `${SCRATCH}` and `${HOME}/data` to `${HOME}/data`

    ```toml
    mounts = ["${SCRATCH}:${SCRATCH}", "${HOME}/data:${HOME}/data"]
    ```

!!! note
    The source (before `:`) should be present on the cluster: the destination (after `:`) doesn't have to be inside the container.

See [the EDF reference][ref-ce-edf-reference] for the full specifiction of the `mounts` EDF entry.


[](){#ref-ce-run-mounting-squashfs}
### Mounting a SquashFS image

!!! warning
    This feature is only available on some vClusters (Daint and Santis, as of 17.06.2025).

A SquashFS image, essentially being a compressed data archive, can also be mounted _as a directory_ so that the image contents are readable inside the container. For this, `:sqsh` should be appended after the destination.

!!! example "Mounting a SquashFS image `${SCRATCH}/data.sqsh` to `/data`" 
    ```toml
    mounts = ["${SCRATCH}/data.sqsh:/data:sqsh"]
    ```

This is particularly useful if a job should read _multiple_ data files _frequently_, which may cause severe file access overheads. Instead, it is recommended to pack data files into one data SquashFS image and mount it inside a container. See the *"magic phrase"* in [this documentation](https://tldp.org/HOWTO/SquashFS-HOWTO/creatingandusing.html) for creating a SquashFS image.
