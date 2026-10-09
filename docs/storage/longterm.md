# Long Term Storage (LTS)

!!! warning "LTS is in read-only mode"
    The LTS service no longer accepts new customers, and is in read-only mode for existing data.
    New data collections can no longer be created, and data can no longer be uploaded.
    Existing data collections remain accessible, see [downloading data from LTS][ref-storage-lts-download].

The Long Term Storage (LTS) service enables CSCS users to preserve their scientific data and ensures that it can be publicly accessed through a persistent identifier.
The current implementation of the LTS service addresses the first two principles of the FAIR quadrant: __findable__ and __accessible__.

<div class="grid cards" markdown>

- :fontawesome-solid-magnifying-glass: __Findable__ Data and supplementary materials have sufficiently rich metadata and a unique and persistent identifier.
- :fontawesome-solid-universal-access: __Accessible__ Metadata and data are understandable to humans and machines.
  Data is deposited in a trusted repository.
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

The main unit of the LTS workflow is the data collection.
A data collection is a group of data files enriched with a set of metadata attributes and a persistent ID referencing the entire collection.
In other contexts such an entity might be called dataset, data aggregate or data block.

The data files are stored in the CSCS Object Store thus the data collection and its associated [PID handle](https://www.pidconsortium.net/) (the specific type of persistent ID used by LTS) will contain a list of URLs.
There is no need to have special clients to access the data URLs or the PID handle, standard HTTP client like a browser or the `curl` command are sufficient.

The PID handles used for the LTS service are the ones provided by the [CSCS PID service](https://pid.cscs.ch/).
This enables the LTS service to guarantee the consistency between data collection, object store data and PID handle.

[](){#ref-storage-lts-download}
## Accessing data in LTS

Data collections stored in LTS remain available for the full retention period, and all of the interfaces for finding, inspecting and downloading them are still provided.

Every data collection is public: anybody can download its data files with a web browser or any other HTTP client, like `curl`, without a CSCS account.
The client needs outgoing connectivity to the following services:

| Service | URL | Description |
| --- | --- | --- |
| LTS | [https://lts.cscs.ch](https://lts.cscs.ch) | LTS web portal and RESTful API |
| Keycloak | [https://auth.cscs.ch](https://auth.cscs.ch) | Authentication service (only needed to log in to LTS) |
| Object Store | [https://object.cscs.ch](https://object.cscs.ch) | Object Store service, where the data files are stored |
| PID | [https://hdl.handle.net](https://hdl.handle.net) | PID service, which resolves handles |

[](){#ref-storage-lts-handle}
### Persistent identifiers

Each completed data collection was assigned a [PID handle](https://www.pidconsortium.net/) by the [CSCS PID service](https://pid.cscs.ch/).
The handle is stored in the "Handle" attribute of the data collection, and is the persistent identifier that should be used to reference and cite the data.

The handle can be resolved with any web browser through the global handle resolver at `https://hdl.handle.net/<handle>`.
The handle record contains the list of URLs of the data files in the collection, which point to the CSCS Object Store.

[](){#ref-storage-lts-inspect}
### Inspecting data collections

Members of the project that owns a data collection can find and inspect their collections in two ways:

* the web portal available at [lts.cscs.ch](https://lts.cscs.ch);
* the LTS RESTful API, whose endpoints are described by the online documentation at [lts.cscs.ch/api](https://lts.cscs.ch/api).

LTS authenticates users with the CSCS authentication service, so a valid CSCS account is required.
The web portal guides the user through the authentication process; to access LTS through the RESTful API, the user first needs to create a Keycloak token.

Inspecting a data collection shows:

* its name, description and the project that owns it;
* its metadata attributes;
* its handle;
* its license;
* the list of data files, with the md5 checksum and URL of each file.

[](){#ref-storage-lts-download-files}
### Downloading data files

The data files are stored in the CSCS Object Store, with world readable access.
Download them with a web browser, or with any HTTP client using the URLs listed in the handle record or the data collection:

```bash title="download a data file and verify its checksum"
curl -O <data-file-url>
md5sum <data-file>
```

Compare the output of `md5sum` with the checksum recorded in the data collection to verify that the file was downloaded correctly.

### Licensing

Every data collection was published under a license, which is stored with the collection.
The default LTS license is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Check the license of a data collection before reusing its data.
