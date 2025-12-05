[](){#ref-firecrest}
# FirecREST

FirecREST is a RESTful API for programmatically accessing High-Performance Computing resources, developed at CSCS.

Users can make use of FirecREST to automate access to HPC, enabling [CI/CD pipelines](https://eth-cscs.github.io/firecrest-v2/use_cases/CI-pipeline/), [workflow orchestrators](https://eth-cscs.github.io/firecrest-v2/use_cases/workflow-orchestrator/), and other tools against HPC resources.

Additionally, scientific platform developers can integrate FirecREST into [web-enabled portals](https://eth-cscs.github.io/firecrest-ui/home/) and [web UI applications](https://eth-cscs.github.io/firecrest-v2/use_cases/UI-client-credentials/), allowing them to securely access authenticated and authorized CSCS services such as job submission and data transfer on HPC systems.

Users can make HTTP requests to perform the following operations:

* basic system utilities like `ls`, `mkdir`, `mv`, `chmod`, `chown`, among others
* actions against the Slurm workload manager (submit, query, and cancel jobs of the user)
* internal (between CSCS systems) and external (to/from CSCS systems) data transfers

## FirecREST specification

Starting early 2025, CSCS has introduced a new version of the API: [FirecREST version 2](https://eth-cscs.github.io/firecrest-v2).

!!! warning "Deprecation notice"
    FirecREST version 1 has been decommissioned on December 5th, 2025. Since then, only version 2 is available at CSCS systems.

For a full feature set, have a look at the latest [FirecREST version 2 API specification](https://eth-cscs.github.io/firecrest-v2/openapi) deployed at CSCS.

Please refer to the [FirecREST-v2 documentation](https://eth-cscs.github.io/firecrest-v2/user_guide/) for detailed documentation.

## FirecREST Deployment on Alps

FirecREST is available for all three major [Alps platforms][ref-alps-platforms], with a dedicated API endpoint for each platform.


| Platform     |  API Endpoint | Clusters |
|----------    |--------------|----------|
| [HPC Platform][ref-platform-hpcp] | https://api.cscs.ch/hpc/firecrest/v2 | [Daint][ref-cluster-daint], [Eiger][ref-cluster-eiger] |
| [ML Platform][ref-platform-mlp] | https://api.cscs.ch/ml/firecrest/v2 | [Bristen][ref-cluster-bristen], [Clariden][ref-cluster-clariden] |
| [C&W Platform][ref-platform-cwp] | https://api.cscs.ch/cw/firecrest/v2 | [Santis][ref-cluster-santis] |

## Accessing FirecREST

### Clients and access tokens

For authenticating requests to FirecREST, [client applications][ref-devportal-application] use an **access token** instead of directly using the user's credentials.
The access token is a signed JSON Web Token ([JWT](https://jwt.io/introduction)) which contains user information and is only valid for a short time (5 minutes).
Behind the API, all commands launched by the client will use the account of the user that registered the client, inheriting their access rights.

Every client has a client ID (Consumer Key) and a secret (Consumer Secret) that are used to get a short-lived access token with an HTTP request.

??? example "`curl` call to fetch the access token"
    ```
    curl -s -X POST https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token \
         --data "grant_type=client_credentials" \
         --data "client_id=<client_id>" \
         --data "client_secret=<client_secret>"
    ```

You can manage your client application on the [CSCS Developer Portal][ref-devportal].


To use your client credentials to access FirecREST, follow the [API documentation](https://eth-cscs.github.io/firecrest-v2/openapi).

## Getting Started

### Using the Python Interface

One way to get started is by using [pyFirecREST](https://pyfirecrest.readthedocs.io/), a Python package with a collection of wrappers for the different functionalities of FirecREST.
This package simplifies the usage of FirecREST by making multiple requests in the background for more complex workflows as well as by refreshing the access token before it expires.

??? example "Try FirecREST using pyFirecREST v2"
    ```python
    import json
    import firecrest as f7t

    client_id = "<client_id>"
    client_secret = "<client_secret>"
    token_uri = "https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token"

    # Setup the client for the specific account
    # For instance, for the Alps HPC Platform system Daint:

    client = f7t.v2.Firecrest(
        firecrest_url="https://api.cscs.ch/hpc/firecrest/v2",
        authorization=f7t.ClientCredentialsAuth(client_id, client_secret, token_uri)
    )

    # Status of the systems, filesystems and schedulers:
    print(json.dumps(client.systems(), indent=2))

    # Output: information about systems and health status of the infrastructure
    # [
    #   {
    #     "name": "daint",
    #     "ssh": {                           # --> SSH settings
    #       "host": "daint.alps.cscs.ch",
    #       "port": 22,
    #       "maxClients": 100,
    #       "timeout": {
    #         "connection": 5,
    #         "login": 5,
    #         "commandExecution": 5,
    #         "idleTimeout": 60,
    #         "keepAlive": 5
    #       }
    #     },
    #     "scheduler": {                     # --> Scheduler settings
    #       "type": "slurm",
    #       "version": "24.05.4",
    #       "apiUrl": null,
    #       "apiVersion": null,
    #       "timeout": 10
    #     },
    #     "servicesHealth": [                # --> Health status of services
    #       {
    #         "serviceType": "scheduler",
    #         "lastChecked": "2025-03-18T23:34:51.167545Z",
    #         "latency": 0.4725925922393799,
    #         "healthy": true,
    #         "message": null,
    #         "nodes": {
    #           "available": 21,
    #           "total": 858
    #         }
    #       },
    #       {
    #         "serviceType": "ssh",
    #         "lastChecked": "2025-03-18T23:34:52.054056Z",
    #         "latency": 1.358715295791626,
    #         "healthy": true,
    #         "message": null
    #       },
    #       {
    #         "serviceType": "filesystem",
    #         "lastChecked": "2025-03-18T23:34:51.969350Z",
    #         "latency": 1.2738196849822998,
    #         "healthy": true,
    #         "message": null,
    #         "path": "/capstor/scratch/cscs"
    #       },
    #     (...)
    #     "fileSystems": [                   # --> Filesystem settings
    #       {
    #         "path": "/capstor/scratch/cscs",
    #         "dataType": "scratch",
    #         "defaultWorkDir": true
    #       },
    #       {
    #         "path": "/users",
    #         "dataType": "users",
    #         "defaultWorkDir": false
    #       },
    #       {
    #         "path": "/capstor/store/cscs",
    #         "dataType": "store",
    #         "defaultWorkDir": false
    #       }
    #     ]    
    #   }
    # ]

    # List content of directories
    print(json.dumps(client.list_files("daint", "/capstor/scratch/cscs/<username>"),
                                    indent=2))

    # [
    #   {
    #     "name": "directory",
    #     "type": "d",
    #     "linkTarget": null,
    #     "user": "<username>",
    #     "group": "<project>",
    #     "permissions": "rwxr-x---+",
    #     "lastModified": "2024-09-02T12:34:45",
    #     "size": "4096"
    #   },
    #   {
    #     "name": "file.txt",
    #     "type": "-",
    #     "linkTarget": null,
    #     "user": "<username>",
    #     "group": "<project>",
    #     "permissions": "rw-r-----+",
    #     "lastModified": "2024-09-02T08:26:04",
    #     "size": "131225"
    #   }
    # ]
    ```

The tutorial is written for a generic instance of FirecREST but if you have a valid user at CSCS you can test it directly with your resource allocation on the exposed systems.

### Data transfer with FirecREST

In addition to the [external transfer methods at CSCS][ref-data-xfer-external], FirecREST provides automated data transfer within the API.

A staging area is used for external transfers and downloading/uploading a file from/to a CSCS filesystem.

!!!Note
    pyFirecREST hides this complexity to the user. We strongly recommend to use this library for these tasks.

#### Examples of data transfer via pyFirecREST

!!! example "Upload a large file using FirecREST-v2"
    ```python

    import firecrest as f7t

    (...)

    system = "daint"
    source_path = "/path/to/local/file"
    target_dir = "/capstor/scratch/cscs/<username>"
    target_file = "file"
    account = "<project>"


    upload_task = client.upload(system,
                                local_file=source_path,
                                directory=target_dir,
                                filename=target_file,
                                account=account,
                                blocking=True)    
    ```

!!! example "Download a large file using FirecREST-v2"
    ```python

    import firecrest as f7t

    (...)

    system = "daint"
    source_path = "/capstor/scratch/cscs/<username>/file"
    target_path = "/path/to/local/file"
    account = "<project>"


    download_task = client.download(system,
                                    source_path=source_path,
                                    target_path=target_path,
                                    account=account,
                                    blocking=True)

    
    ```

!!! Note "Job submission through FirecREST"

    FirecREST provides an abstraction for job submission using in the backend the Slurm scheduler of the vCluster.

    When submitting a job via the different [endpoints](https://firecrest.readthedocs.io/en/latest/reference.html#compute), you should pass the `-l` option to the `/bin/bash` command on the batch file.

    ```bash
    #!/bin/bash -l

    #SBATCH --nodes=1
    ...
    ```

    This option ensures that the job submitted uses the same environment as your login shell to access the system-wide profile (`/etc/profile`) or to your profile (in files like `~/.bash_profile`, `~/.bash_login`, or `~/.profile`).

## Further Information

* [HPC Console](https://console.hpcp.cscs.ch)
* [ML Console](https://console.mlp.cscs.ch)
* [C&W Console](https://console.cwp.cscs.ch)
* [FirecREST OpenAPI Specification](https://eth-cscs.github.io/firecrest-v2/openapi)
* [FirecREST Official Docs](https://eth-cscs.github.io/firecrest-v2)
* [Documentation of pyFirecREST](https://pyfirecrest.readthedocs.io/)
* [FirecREST repository](https://github.com/eth-cscs/firecrest-v2)
* [What are JSON Web Tokens](https://jwt.io/introduction)
* [Python Requests](https://requests.readthedocs.io/en/master/user/quickstart)
* [Python Async API Calls](https://docs.aiohttp.org/en/stable/)
