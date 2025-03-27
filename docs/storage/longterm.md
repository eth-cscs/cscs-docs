# Long Term Storage (LTS)

The Long Term Storage (LTS) service enables CSCS users to preserve their scientific data and ensures that it can be publicly accessed through a persistent identifier.
The current implementation of the LTS service addresses the first two principles of the FAIR quadrant: __findable__ and __accessible__.

<div class="grid cards" markdown>

- :fontawesome-solid-magnifying-glass: __Findable__ Data and supplementary materials have sufficiently rich metadata anda  unique and persistent identifier.
- :fontawesome-solid-universal-access: __Accessible__ Metadata and data are understandable to humans and machines. Data is deposited in a trusted repository.
- :fontawesome-solid-arrow-right-arrow-left: __Interoperable__ Metadata use a formal, accessible, shared, and broadly applicable language for knowledge representation.
- :fontawesome-solid-recycle: __Reusable__ Data and collections have a clear usage license and provide accurate information on provenance.

</div>

These are the main features of the service:

* Storage repository with long term retention capabilities (10 years);
* Provide persistent identifiers;
* Ability to set public access to data when needed;
* Data stored in LTS easily accessible from a web browser (HTTP protocol);
* RESTful API to integrate with third party applications/portals;
* Scalable service that can cope with large volumes of data;
* Resiliency due to data protection measures against hardware/software failures;
* Clear licensing of the data.

## Service Description

The main unit of the LTS workflow is the data collection. A data collection is a group of data files enriched with a set of metadata attributes and a persistent ID referencing the entire collection. In other contexts such an entity might be called dataset, data aggregate or data block.

The data files are store in the CSCS Object Store thus the data collection and its associated [PID handle](https://www.pidconsortium.net/) (the specific type of persistent ID used by LTS) will contain a list of URLs. There is no need to have special clients to access the data URLs or the PID handle, standard HTTP client like a browser or the `curl` command are sufficient.

The PID handles use for the LTS service are the one provided by the [CSCS PID service](https://pid.cscs.ch/). This enables the LTS service to guarantee the consistency between data collection, object store data and PID handle.

## Pricing

As of 2021:

* Users from the free User Lab program are entitled to use 2 TB of LTS storage quota (for 10 years) free of charge per project
* Currently additional space can be purchased for CHF 600.- for each Terabyte (for 10 years)

## Prerequisites

In order to create collections and upload files into the LTS service, a user needs the following prerequisites:

* CSCS project with a quota on the LTS (and/or LTS-TDS) facility
* HTTP client: for example `curl` or Python requests.
* Keycloak registered client (only to access the service via RESTful API, not needed when using the web portal)
* Outgoing connectivity to the following services:

    | Service | URL | Description |
    | --- | --- | --- |
    | LTS Prod | [https://lts.cscs.ch](https://lts.cscs.ch) | Production LTS service |
    | LTS TDS | [https://lts-tds.cscs.ch](https://lts-tds.cscs.ch) | Test LTS service |
    | Keycloak | [https://auth.cscs.ch](https://auth.cscs.ch) | Authentication service |
    | Object Store | [https://object.cscs.ch](https://object.cscs.ch) | Object Store service |
    | PID | [https://hdl.handle.net](https://hdl.handle.net) | PID service |

In order to download files from the LTS service, a user needs a web browser or any other HTTP client like `curl`.

## Creating collections and uploading files

LTS can be accessed in two ways:

* the web portal available at [lts.cscs.ch](https://lts.cscs.ch);
* the LTS RESTful API, whose endpoints are described by the online documentation at [lts.cscs.ch/api](https://lts.cscs.ch/api)

### Authentication

The LTS authenticates users based on the CSCS authentication service, therefore a user needs a valid CSCS account in order to access the service. The LTS web portal will guide the user through the authentication process; in order to access LTS through the RESTful API, the user will need to create a Keycloak token first.

### Authorization

LTS data collections belong to a CSCS project: data can be stored in the LTS service after the principal investigator of the project has granted a project member the permissions to store data on behalf of the project. This is done by enabling the LTS facility for the user on the [CSCS Account and Resources Management Tool](https://account.cscs.ch).

## Data collection creation Workflow

The typical LTS workflow will involve several steps, as described below. During the process, the data collection will go through the following states:

``` mermaid
graph LR
  A[NEW] --> B[COMMITTED]
  B --> C[VALIDATED]
  C --> D[HANDLE ASSIGNED]
  D --> E[COMPLETED]
```


### Data collection definition

The workflow begins with the creation of a data collection.
A minimum set of attributes is necessary to create the data collection; the most important ones are the following:

* name of the collection
* brief description
* project owning the data
* list of metadata attributes
* list of data files
* data files license

The initial state of a data collection is `NEW`: the list of attributes and data files can be specified both at creation time or also added afterwards. The list of data files must contain the filename and the corresponding md5 checksum.

Currently all the LTS data collections are considered containing public data: in future, the user will be able to specify whether the data collection is going to be public or private.

If the data files are covered by copyright the user have to select an appropriate license.
The default LTS license is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

### Data collection inspection

The collection can be inspected immediately after its creation. This is useful to check the attributes/objects already included in its definition, the object checksums, the overall state and the state of the single objects and their temporary URLs.

### Data collection update and data upload

After the collection has been created, it can be modified during a transient phase: meanwhile, the collection state is `NEW` and the user can do the following:

* add additional data files
* add additional metadata attributes
* update already defined data files/attributes
* delete already defined data files/attributes
* upload the data files

The LTS service generates a set of object store temporary URLs, one for each data file, which will be used to upload them to the object store. LTS is not involved in the upload operation, the data path comes from the user machine to the CSCS Object Store servers.

### Licensing

When you prepare a data collection you must specify the license under which you publish your data. The default is the Creative Commons CC BY 4.0 license, but you can choose other ones.
This Licensing guide provides information about the data licenses available in LTS.

!!! todo
    the link to the licensing guide on Confluence KB was broken.

### Commit

At the end of the creation/update/upload phase, the user has to declare that the definition of the collection is complete.
This is done by the user, who sends a collection commit request: after the commit request, the collection state changes from `NEW` to `COMMITTED` and from that point on the data collection definition cannot be modified anymore.

### Validation

Once the LTS service has received the commit request, it starts performing the validation operations needed to assess whether the files uploaded are consistent with the the checksums defined in the collection.
If a mismatch is found, then the collection gets a `FAILED` status and the issue is reported back to the user.
If all files are found in the object store and they have the correct checksum, the collection state is set to `VALIDATED`.
At the end of the validation process, LTS sets the Object Store container ACLs in order to make the container world readable.

### Handle assignment

When the collection has entered the `VALIDATED` state, it's time for the LTS service to talk with the PID service and ask for a handle.
The handle is attached to the collection and at that point the creation workflow of the collection is complete and the collection enter in the state `HANDLE_ASSIGNED` and the state COMPLETED shortly after that.

## Dealing with Failures

After the collection is committed by the user, LTS performs a series of checks on the uploaded data and requests an handle to the ePIC handle service. If any error occurs during this phase the collection state will be `FAILED`. Possible reasons for this state are:

* a failure in one of the LTS microservices
* a failure in one of the underneath services (object store, handle server, database server etc ..)
* one or more data files were not uploaded
* one or more data file checksums are wrong

When in state FAILED the collection is still editable. The user will have to review the content of the collection, fix the checksum or re-upload files if he/she spots anything wrong or missing. Then the collection needs to be saved and the validation retried. The validation process can be retried clicking on "Retry Data Collection" from the web portal or through the `commit` endpoint if using the RESTful API.

## Downloading data from LTS

The data is publicly accessible via the HTTP protocol once the status of the collection has entered the `COMPLETED` step.
Its URL can be found under the "Handle" attribute of the data collection.

## Further Documentation

!!! todo
    All of the links in this section (except the video) on the Confluence KB were broken.

The Long Term Storage webinar, held in June 2021, provides an description of the Long Term Storage service use case, its architecture and workflow, and a demonstration of the Web Portal.

<iframe width="100%" height="315" src="https://www.youtube.com/embed/ODqoSMW_1ik?si=wsWnHCVoUlGJVyh1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

The RESTful API HowTo provides some usage examples for the LTS API with curl and Python.

The Web portal: create a data collection page provides usage examples for the creation of a data collection in the LTS web portal.

The Web portal: define and upload objects page provides usage examples for definition and the upload of data collection objects in the LTS web portal.

The Licensing guide provides information about the data licenses available in LTS.

The Landing page page provides information about the LTS landing page.
