[](){#ref-firecrest}
# FirecREST

FirecREST is a RESTful API for programmatically accessing High-Performance Computing resources, developed at CSCS.

Users can make use of FirecREST to automate access to HPC, enabling [CI/CD pipelines](https://github.com/eth-cscs/firecrest/tree/master/examples/CI-pipeline), [workflow managers](https://github.com/eth-cscs/firecrest/tree/master/examples/airflow-operators), and other tools against HPC resources.

Additionally, scientific platform developers can integrate FirecREST into [web-enabled portals](https://firecrest-ui-hpc.cscs.ch) and [applications](https://github.com/eth-cscs/firecrest/tree/master/examples/UI-client-credentials), allowing them to securely access authenticated and authorized CSCS services such as job submission and data transfer on HPC systems.

Users can make HTTP requests to perform the following operations:

* basic system utilities like `ls`, `mkdir`, `mv`, `chmod`, `chown`, among others
* actions against the Slurm workload manager (submit, query, and cancel jobs of the user)
* internal (between CSCS systems) and external (to/from CSCS systems) data transfers

## FirecREST versions

Starting early 2025, CSCS has introduced a new version of the API: [FirecREST version 2](https://eth-cscs.github.io/firecrest-v2).

Version 2 is faster, easier to use, and more efficient in resource management than its predecessor, therefore, if you are new to FirecREST start directly using **version 2** (if available for your platform).

If you're using **version 1**, we recommend you to port your applications to use the new version.

=== "Version 2"

    !!!Warning
        Documentation for version 2 is still work in progress

    For a full feature set, have a look at the latest [FirecREST version 2 API specification](https://eth-cscs.github.io/firecrest-v2/openapi) deployed at CSCS.

    Please refer to the [FirecREST-v2 documentation](https://eth-cscs.github.io/firecrest-v2/use) for detailed documentation.

=== "Version 1"

    For a full feature set, have a look at the latest [FirecREST version 1 API specification](https://firecrest-docs.v1.svc.cscs.ch/) deployed at CSCS.

    Please refer to the [FirecREST-v1 documentation](https://firecrest.readthedocs.io/en/latest/) for detailed documentation.


## FirecREST Deployment on Alps

FirecREST is available for all three major [Alps platforms][ref-alps-platforms], with a different API endpoint and versions for each platform.

<table>
<tr><th>Platform</th><th>Version</th><th>API Endpoint</th><th>Clusters</th></tr>
<tr><td style="vertical-align: middle;" rowspan="2">HPC Platform</td><td>v1</td><td>https://api.cscs.ch/hpc/firecrest/v1</td><td style="vertical-align: middle;" rowspan="2"><a href="../../clusters/daint">Daint</a>, <a href="../../clusters/eiger">Eiger</a></td></tr>
<tr>                                 <td>v2</td><td>https://api.cscs.ch/hpc/firecrest/v2</td></tr>
<tr><td>ML Platform</td><td>v1</td><td>https://api.cscs.ch/ml/firecrest/v1</td><td style="vertical-align: middle;"><a href="../../clusters/bristen">Bristen</a>, <a href="../../clusters/clariden">Clariden</a></td></tr>
<tr><td style="vertical-align: middle;" rowspan="2">CW Platform</td><td>v1</td><td>https://api.cscs.ch/cw/firecrest/v1</td><td style="vertical-align: middle;" rowspan="2"><a href="../../clusters/santis">Santis</a></td></tr>
<tr><td>v2</td><td>https://api.cscs.ch/cw/firecrest/v2</td></tr>
</table>


## Accessing FirecREST

### Clients and access tokens

For authenticating requests to FirecREST, **client applications** use an **access token** instead of directly using the user's credentials.
The access token is a signed JSON Web Token ([JWT](https://jwt.io/introduction)) which contains user information and is only valid for a short time (5 minutes).
Behind the API, all commands launched by the client will use the account of the user that registered the client, inheriting their access rights.

Every client has a client ID (Consumer Key) and a secret (Consumer Secret) that are used to get a short-lived access token with an HTTP request.

??? example "`curl` call to fetch the access token"
    ```
    curl -s -X POST https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token \
         --data "grant_type=client_credentials" \
         --data "client_id=<your_client>" \
         --data "client_secret=<your_secret>"
    ```

You can manage your client application on the [CSCS Developer Portal][ref-devportal].

[](){#ref-devportal}
### CSCS Developer Portal

The [Developer Portal](https://developer.cscs.ch) facilitates CSCS users to manage subscriptions to an API at CSCS (such as FirecREST v1/v2).

Start by browsing to [developer.cscs.ch](https://developer.cscs.ch), then sign in by clicking the "SIGN-IN" button on the top right hand corner of the page.

Once logged in, you will see a list of APIs that are available to your user.

!!! Warning
    You might not see version 1 or version 2 of some API. You will be able to see all the versions when you *subscribe* your Application to the API.

### Creating an Application

Click on the "Applications" button at the top of the screen to manage your Applications.

![FirecREST Main Page](../images/firecrest/f7t-apis.png)

To create a new application, click on the "ADD NEW APPLICATION" button at the top of the Applications page, and complete the mandatory fields (marked with `*`).
Make sure to give the application a unique name and select the number of requests per minute.
When finished, click on the "Save" button.

!!! note
    To subscribe to an API you need at least one application, for which it is possible to use the DefaultApplication.

!!! note
    The quota of requests per minute will be shared by all subscribers to the Application over all APIs.

### Configuring Production Keys

Once the Application is created, create the Production Keys (`Client ID` and `Client Secret`) by clicking on "Production Keys" 

![FirecREST production keys](../images/firecrest/f7t-keys.png)


Use this if this is your first FirecREST application, or if you wish to create new keys.

* click on the "Generate Keys" button at the bottom of the page

![FirecREST existing keys](../images/firecrest/f7t-generate-keys.png)

Once the keys are generated, you will see the pair "Consumer Key" and "Consumer Secret".

![FirecREST keys](../images/firecrest/f7t-keys-overview.png)

!!! warning
    Store this pair of credentials securely, these are the access keys to your resources at CSCS.

### Subscribe to an API

Once you have set up your Application, is time to subscribe it to an API.

To do so:

* (8a) click on the "Subscriptions" option on the left panel
* (8b) click the :fontawesome-solid-circle-plus: "Subscribe APIS" button
* (8c) choose the API you want to subscribe to by clicking the "Subscribe" button

![FirecREST subscriptions](../images/firecrest/f7t-api-subscriptions.png)

Back on the Subscription Management page, you can review your active subscriptions and APIs that your Application has access to.

![FirecREST subscription management](../images/firecrest/f7t-api-subscriptions-management.png)

To use your Application to access FirecREST, follow the [API documentation](https://firecrest-docs.v1.svc.cscs.ch/).

## Getting Started

### Using the Python Interface

One way to get started is by using [pyFirecREST](https://pyfirecrest.readthedocs.io/), a Python package with a collection of wrappers for the different functionalities of FirecREST.
This package simplifies the usage of FirecREST by making multiple requests in the background for more complex workflows as well as by refreshing the access token before it expires.

=== "Version 2"

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

=== "Version 1"

    ??? example "Try FirecREST using pyFirecREST v1"
        ```python
        import json
        import firecrest as f7t

        client_id = "<client_id>"
        client_secret = "<client_secret>"
        token_uri = "https://auth.cscs.ch/auth/realms/firecrest-clients/protocol/openid-connect/token"

        # Setup the client for the specific account
        # For instance, for the Alps HPC Platform system Daint:

        client = f7t.v1.Firecrest(
            firecrest_url="https://api.cscs.ch/hpc/firecrest/v1",
            authorization=f7t.ClientCredentialsAuth(client_id, client_secret, token_uri)
        )

        print(json.dumps(client.all_systems(), indent=2))
        # Output: (one dictionary per system)
        # [{
        #      'description': 'System ready',
        #      'status': 'available',
        #      'system': 'daint'      
        # }]

        print(json.dumps(client.list_files('daint', '/capstor/scratch/cscs/<username>'),
                                        indent=2))
        # Example output: (one dictionary per file)
        # [
        #   {
        #       'name': 'directory',
        #       'user': '<username>'
        #       'last_modified': '2024-04-20T11:22:41',
        #       'permissions': 'rwxr-xr-x',
        #       'size': '4096',
        #       'type': 'd',
        #       'group': '<project>',
        #       'link_target': '',
        #   }
        #   {
        #      'name': 'file.txt',
        #      'user': '<username>'
        #      'last_modified': '2024-09-02T08:26:04',
        #      'permissions': 'rw-r--r--',
        #      'size': '131225',
        #      'type': '-',
        #      'group': '<project>',
        #      'link_target': '',
        #   }
        # ]
        ```

The tutorial is written for a generic instance of FirecREST but if you have a valid user at CSCS you can test it directly with your resource allocation on the exposed systems.

### Data transfer with FirecREST

In addition to the [external transfer methods at CSCS][ref-data-xfer-external], FirecREST provides automated data transfer within the API.

A staging area is used for external transfers and downloading/uploading a file from/to a CSCS filesystem.

!!!Note
    pyFirecREST (both v1 and v2) hides this complexity to the user. We strongly recommend to use this library for these tasks.

=== "Version 2"

    #### Upload
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
    #### Download

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

=== "Version 1"

    Please follow the steps below to download a file:

    1. Request FirecREST to move the file to the staging area: a download link will be provided
    2. The file will remain in the staging area for 7 days or until the link gets invalidated with a request to the [`/storage/xfer-external/invalidate`](https://firecrest.readthedocs.io/en/latest/reference.html#post--storage-xfer-external-invalidate) endpoint or through the pyfirecrest method
    3. The staging area is common for all users, therefore users should invalidate the link as soon as the download has been completed

    You can see the full process in this [tutorial](https://firecrest.readthedocs.io/en/latest/tutorial.html#upload-with-non-blocking-call-something-bigger).

    We may be forced to delete older files sooner than 7 days whenever large files are moved to the staging area and the link is not invalidated after the download, to avoid issues for other users: we will contact the user in this case.

    When uploading files through the staging area, you don't need to invalidate the link. FirecREST will do it automatically as soon as it transfers the file to the filesystem of CSCS.

    There is also a constraint on the size of a single file to transfer externally to our systems via FirecREST: 5 GB.

    If you wish to transfer data bigger than the limit mentioned above, you can check the [compress](https://firecrest.readthedocs.io/en/latest/reference.html#post--storage-xfer-internal-compress) and [extract](https://firecrest.readthedocs.io/en/latest/reference.html#post--storage-xfer-internal-extract) endpoints or follow the following [example on how to split large files](https://github.com/eth-cscs/firecrest/blob/master/examples/download-large-files/README.md) and download/upload them using FirecREST.

    The limit on the time and size of files that can be download/uploaded via FirecREST might change if needed.

    !!! example "Checking the current values in the parameters endpoint"
        ```python
        >>> print(json.dumps(client.parameters(), indent = 2))
        {
        (...)

        "storage": [
            {
            "description": "Type of object storage, like `swift`, `s3v2` or `s3v4`.",
            "name": "OBJECT_STORAGE",
            "unit": "",
            "value": "s3v4"
            },
            {
            "description": "Expiration time for temp URLs.",
            "name": "STORAGE_TEMPURL_EXP_TIME",
            "unit": "seconds",
            "value": "604800"  ## <-------- 7 days
            },
            {
            "description": "Maximum file size for temp URLs.",
            "name": "STORAGE_MAX_FILE_SIZE",
            "unit": "MB",
            "value": "5120"   ## <--------- 5 GB
            }
        (...)
        }
        ```
!!! Note "Job submission through FirecREST"

    FirecREST provides an abstraction for job submission using in the backend the SLURM scheduler of the vCluster.

    When submitting a job via the different [endpoints](https://firecrest.readthedocs.io/en/latest/reference.html#compute), you should pass the `-l` option to the `/bin/bash` command on the batch file.

    ```bash
    #!/bin/bash -l

    #SBATCH --nodes=1
    ...
    ```

    This option ensures that the job submitted uses the same environment as your login shell to access the system-wide profile (`/etc/profile`) or to your profile (in files like `~/.bash_profile`, `~/.bash_login`, or `~/.profile`).

## Further Information

* [FirecREST UI for HPC Platform](https://firecrest-ui-hpc.cscs.ch)
* [FirecREST OpenAPI Specification Version 1](https://firecrest.readthedocs.io/en/latest/reference.html)
* [FirecREST OpenAPI Specification Version 2](https://eth-cscs.github.io/firecrest-v2/openapi)
* [FirecREST Docs Version 1](https://firecrest.readthedocs.io/)
* [FirecREST Docs Version 2](https://eth-cscs.github.io/firecrest-v2)
* [Documentation of pyFirecREST (v1/v2)](https://pyfirecrest.readthedocs.io/)
* [FirecREST repository Version 1](https://github.com/eth-cscs/firecrest)
* [FirecREST repository Version 2](https://github.com/eth-cscs/firecrest-v2)
* [What are JSON Web Tokens](https://jwt.io/introduction)
* [Python Requests](https://requests.readthedocs.io/en/master/user/quickstart)
* [Python Async API Calls](https://docs.aiohttp.org/en/stable/)
