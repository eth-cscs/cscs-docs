# Contributing to the Docs

This documentation is for use by LLM agents tasked with drafting and editing documentation.

Humans can refer to the [online contributing guide](https://docs.cscs.ch/contributing)

Agents should:

1. read the contributing guide in its raw form in the `docs/contributing/index.md` file — the spell checker section in particular is not duplicated here.
2. read the rest of this page.

To validate changes, run `./serve build` (requires [uv](https://docs.astral.sh/uv/getting-started/installation/) to be installed).
This will catch broken links and build errors before the CI pipeline does.

## Guidelines for agents

The documentation uses the Material for MkDocs framework.

The project configuration is in the `mkdocs.yml` file.

The docs are in the `docs` directory.

### What are we documenting?

These is the public facing documentation for the Swiss National Supercomputing Center (CSCS).
They are mostly technical documentation for all users that aim to guide users through their first steps getting an account and logging in, through to advanced usage of the different systems and services.

### Documentation structure

CSCS has a large HPE Cray EX system called Alps.
Alps is not deployed as a monolithic cluster, instead it is partitioned into clusters, and these clusters are assigned to use-case specific Platforms.
Most users come to CSCS through one of the platforms, each of which has its own clusters, storage configuration, and user software.
The docs are structured to provide an on-ramp through a platform page, which links out to more general purpose documentation about services/storage/software etc that apply to all platforms.

NOTE:

* the layout of pages in the table of contents does not match directory structure in `docs`.
    * This is partly due to history: a page might move to a new area in the ToC but not move inside the repo
    * The url is determined by the location in the `docs` path: if we don't move files urls point to our docs are less likely to break.
* we use autorefs. This allows us to move pages and files without having to update internal links to the pages.
* each section of the docs has an `index.md` file that introduces the section, with a table of cards on the index page that link to the child pages, and maybe a quickstart guide if appropriate.
    * see the docs in `docs/software/uenv` for a good example

Here is a quick overview of the top level ToC entries:

* `alps`:
    * general documentation about the system, with information about the hardware, network and storage
    * also has an overview page for the platforms, and overview pages for each platform that summarise the specific clusters used by that platform, details about storage and software provided to users of the platform.
* `connecting to alps`:
    * guides for all methods provided for users to connect to Alps.
    * MFA and SSH key management
    * using SSH, using VS Code, FirecREST, JupyterLab, etc
* `running jobs`:
    * guide to running batch and interactive jobs with the Slurm job scheduler
    * HyperQueue for high-throughput scheduling of many small tasks
    * tools for profiling job performance: job reports and GPU reports
* `environments`:
    * how to set up the shell environment after logging in to a cluster
    * uenv: the CSCS tool for delivering scientific software stacks on Alps
    * container engine: recommended for machine learning workflows and Python environments
* `building and installing software`:
    * programming environments (prgenv-gnu, prgenv-nvfortran, linalg, julia, CPE) and Alps Extended Images
    * guides for building software using uenv or Python
    * packaging and deployment: creating containers with podman, or building uenv with the build service
* `applications and frameworks`:
    * scientific applications: CP2K, GROMACS, LAMMPS, NAMD, Quantum ESPRESSO, VASP
    * machine learning: PyTorch, and tutorials for LLM inference, fine-tuning and pre-training
    * climate and weather: ICON, netcdf-tools
    * communication libraries: libfabric, Cray MPICH, MPICH, OpenMPI, NCCL, NVSHMEM
    * user applications: ESMF/CESM, ORCA, WRF
    * scientific visualisation: ParaView
    * commercial software: Matlab
* `debugging and performance analysis`:
    * parallel debugging tools: Linaro Forge DDT
    * performance analysis tools: NVIDIA Nsight, Linaro Forge MAP, Score-P/Scalasca
    * job report and GPU report tools
* `data management and storage`:
    * file systems available on Alps
    * data transfer: moving data into and out of CSCS and between CSCS systems
    * long term storage (LTS): preserving scientific data with persistent identifiers
    * object storage: Ceph-based public cloud object storage
* `services`:
    * CI/CD: integrating GitHub, GitLab and Bitbucket projects with Alps
    * developer portal: creating and managing API subscriptions
    * Kubernetes: platform for deploying and managing containerised applications
* `accounts and projects`:
    * how to get a CSCS account (requires an invitation from the PI of an active project)
    * the project and resources management tool at portal.cscs.ch
    * linking external institutional accounts to a CSCS account
* `guides`:
    * best practices, practical tips, known issues and background information on a range of topics
* `policies`:
    * code of conduct, user regulations, and support policies
    * resource allocation: quarterly compute budgets measured in node hours
    * data retention: backup policy, scratch cleanup, and long term storage lifecycle

### we use autorefs

We use autorefs for generating links, e.g.:

```
[](){#ref-wombats}
# Wombats

This page describes wombat care at CSCS.
To get started, checkout out our [Quickstart guide][ref-wombats-quickstart].

[](){#ref-wombats-quickstart}
## Quickstart
```

They always start with `ref-`, followed by the name of the section/topic, then page (if appropriate), then a final sub-section.
For example, for the following structure:

```
docs
└── services
    ├── index.md
    └── inference
        ├── index.md
        └── api.md
```

* `/docs/services/index.md` would have the top level ref `ref-services`
* `/docs/services/inference/index.md` would have the top level ref `ref-inference`
* `/docs/services/inference/api.md` would have the top level ref `ref-inference-api`
* `/docs/services/inference/api.md#quickstart` a section header inside might have the ref `ref-inference-api-quickstart`

Note that for brevity we use `ref-inference` instead of `ref-services-inference`, and to make the link less bound to its location in the directory tree/table of contents.

* see the `docs/software/uenv` docs for guidance on how to structure links.

You can add references not only to sections/headers, but also to examples, images, etc.

When adding a link, always ask "how portable is this? How likely is this naming scheme and layout to break if we restructure the docs?"

### Link, don't replicate

Review the documentation to see whether a particular piece of information has been covered in another more appropriate section, and link to it (always using auto-refs).

If information is being documented in more than one place, propose centralising it (within reason).

### Ensure that plumbing is in place

IMPORTANT: When asked to write a new page, don't forget the following (where appropriate):

- add it to the table of contents in `mkdocs.yml`
- add a card at the appropriate `index.md` page
- do we need to update platform specific docs in `docs/alps/platform`?
- are we contradicting or replacing something that is documented elsewhere? If it looks like we are, ask the user how to proceed.

### Do not use emoji in titles and bullet lists

Never use emoji in bullet lists and section titles.
It is not professional, and adds no additional meaning.

It is okay to select appropriate emoji from fontawesome (the free version) in card titles, but aim for subtlety.

### Prefer flat content over headings

When creating, e.g., a list of steps, don't create numbered headers.
think about how this could be achieved using bullet lists, admonitions, or plain text formatting.

This isn't a hard and fast rule, but if you end up with many small sections and headers that start with numbers like the following, you know that something has gone wrong:

```
### 1. Get an account

### 2. Get a token

### 3. Use the token
```

### Headings use sentence case

Use [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case) for all headings: only the first word and proper names are capitalised.

### One sentence per line

In paragraphs of prose, write one sentence per line and disable automatic line-wrapping in your editor.
This makes diffs easier to read because a change to one sentence does not reflow the surrounding lines.
There is one and only one canonical representation of a paragraph, which reduces merge conflicts.

### No FAQ sections

The documentation does not have FAQ sections.
Questions are best answered by integrating the information into the relevant part of the main documentation.
A FAQ scatters information about a topic across two places, making it harder to search.
If you want to add a list of common error messages or similar, create a dedicated subsection (e.g. `## Known issues`) at the bottom of the relevant page.

### Use tabs when there is more than one way to do something

The mkdocs tabs feature is very useful for side by side examples, and applying vertical compression.

For example:

```
!!! example "querying the available models"
    Access the `vi/models` API end point to get a list of available models in JSON format.

    === "curl"
        ```console
        $ curl -X GET "https://ai-gateway.svc.cscs.ch/v1/models" \
          -H "Authorization: Bearer <AUTHENTICATION_TOKEN>" \
          -H "Content-Type: application/json"
        ```

    === "python"
        ```python
        import requests
        url = "https://ai-gateway.svc.cscs.ch/v1/models"
        headers = {
            "Authorization": "Bearer <AUTHENTICATION_TOKEN>",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        ```
```

### Try to preempt user questions

Use admonitions of the type `question` or `info` to provide additional context, and fold them if the information is for advanced users or for curious readers.

For example, the following in the documentation that explains file system quotas:

??? question "what is an inode"
    inodes are data structures that describe Linux file system objects like files and directories - every file and directory has a corresponding inode.

    Large inode counts degrade file system performance in multiple ways. For example, Lustre file systems have separate metadata and data management. Excessive inode usage can overwhelm the metadata services, causing degradation across the file system.

### Don't be afraid to share technical details

The documentation is also a good reference for CSCS staff and advanced users who want to understand how things work "under the hood".
You can use admonitions that provide insight (whether the admonition is hidden or not is a judgement call).

### Known issues

Known issues are kept in a section titled `## Known issues` at the bottom of their respective page.
There is some flexibility in how these are formatted, with the default style being "folded warning admonitions".

??? warning "ls: `No such file or directory`"
    This message is printed by the `ls` command when you search for an explicit pattern for which there are no matches.

If there is an error message, try to have it in the title of the folded admonition.
Verbatim reproduction of error/warning messages is important, to help users find documentation when searching with error messages.

You can also add a folded warning admonition inline 

### todo and under-construction

We have two custom admonitions for "todo" and "under-construction".

* "todo" is used to mark documentation that needs to be completed.
* "under-construction" is used to indicate a service/tool/etc that is still being built by CSCS.

When writing docs, we prefer to structure the docs as though they were "complete" or documenting a "complete service", and mark the parts that are missing. This ensures that the structure of pages does not change as much over time, and to ensure that missing documentation is clearly marked and less likely to be forgotten or brushed under the carpet.

### change admonitions

Use the `change` admonition to log updates to clusters or services, at the top of the relevant section.
Recent entries are expanded, older ones are folded:

```
!!! change "2025-04-17"
    * Slurm was upgraded to version 25.1.
    * uenv was upgraded to v0.8

??? change "2025-02-04"
    * The new scratch cleanup policy was implemented.
```

### Code blocks

Use `console` for interactive shell sessions that show a prompt and output:

```
```console title="check the queue"
$ squeue --me
```
```

Use `bash` for command-only blocks that should be easy to copy (no prompt, no output):

```
```bash title="load a uenv"
uenv start prgenv-gnu/24.11:v1
```
```

`terminal` is **not** a valid lexer — MkDocs will silently render it without highlighting.
Always use `$` as the prompt character in `console` blocks; `>` is not highlighted correctly.
Add a `title=` to every code block to describe what it does.

### Reusing content with snippets

If the same content needs to appear on multiple pages (e.g. a set of required environment variables), store it once as a plain text file and include it with the snippets syntax rather than copying it:

```
--8<-- "docs/path/to/snippet_file"
```

This keeps the content in sync across pages automatically.

### Spell checker

The CI pipeline runs a spell checker on all pull requests.
New technical terms, hostnames, software names, and HPC jargon will often be flagged.
Add unfamiliar-but-correct words (one per line) to `.github/actions/spelling/allow.txt`.
Words with unusual capitalisation that confuse the checker (e.g. `FirecREST`) should instead be added as a regex pattern to `.github/actions/spelling/patterns.txt`.
