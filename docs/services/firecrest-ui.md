[](){#ref-firecrest}
# FirecREST UI

FirecREST UI is a web application designed to provide essential functionalities for interacting with [FirecREST API v2 backend](https://docs.cscs.ch/services/firecrest/).

## Features

- A modern web interface built on FirecREST API functionalities.
- A dashboard offering an overview of configured clusters and their statuses.
- A dedicated view for creating and monitoring jobs.
- A file navigator with basic file management functionalities, including upload and download features.

A description of the views and functionalities can be found [here](https://eth-cscs.github.io/firecrest-ui/documentation/).

## FirecREST supported version

Starting early 2025, CSCS has introduced a new version of the API: [FirecREST version 2](https://eth-cscs.github.io/firecrest-v2).

The FirecREST UI is available and runs on the FirecREST API v2 backend (v1 not supported).

## FirecREST UI Deployment on Alps

FirecREST UI is currently available on two [Alps platforms][ref-alps-platforms].

<table>
  <tr>
    <th>Platform</th>
    <th>UI URL</th>
    <th>Clusters</th>
  </tr>
  <tr>
    <td>HPC Platform</td>
    <td>https://my.hpcp.cscs.ch/</td>
    <td><a href="../../clusters/daint">Daint</a>, <a href="../../clusters/eiger">Eiger</a></td>
  </tr>
  <tr>
    <td>ML Platform</td>
    <td>https://my.mlp.cscs.ch/</td>
    <td><a href="../../clusters/bristen">Bristen</a>, <a href="../../clusters/clariden">Clariden</a></td>
  </tr>
</table>


## Further Information

* [FirecREST Official Docs](https://eth-cscs.github.io/firecrest-ui/)
* [FirecREST UI for HPC Platform](https://my.hpcp.cscs.ch)
* [FirecREST UI for ML Platform](https://my.mlp.cscs.ch)
* [FirecREST OpenAPI Specification](https://eth-cscs.github.io/firecrest-v2/openapi)
* [FirecREST Official Docs](https://eth-cscs.github.io/firecrest-v2)
* [Documentation of pyFirecREST](https://pyfirecrest.readthedocs.io/)
* [FirecREST repository](https://github.com/eth-cscs/firecrest-v2)
* [What are JSON Web Tokens](https://jwt.io/introduction)
* [Python Requests](https://requests.readthedocs.io/en/master/user/quickstart)
* [Python Async API Calls](https://docs.aiohttp.org/en/stable/)
