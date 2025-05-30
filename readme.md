# CSCS Documentation

The source CSCS documentation [docs.cscs.ch](httpa://docs.cscs.ch)

> [!NOTE]
> These docs are **work in progress**, and are not hosted at `docs.cscs.ch`.
> They can be viewed at [eth-cscs.github.io/cscs-docs](https://eth-cscs.github.io/cscs-docs)

## Getting Started

> [!IMPORTANT]
> to run the serve script, you need to first install [uv](https://docs.astral.sh/uv/getting-started/installation/).

Clone this repository on your PC/laptop, then view the documentation in a browser run `./serve`:
```bash
git clone git@github.com:${githubusername}/cscs-docs.git
cd cscs-docs
./serve
...
INFO    -  [08:33:34] Serving on http://127.0.0.1:8000/
```
This generates the documentation locally, which can be viewed using a local link, typically [http://127.0.0.1:8000/](http://127.0.0.1:8000/). The documentation will be rebuilt and the webpage reloaded when changed files are saved.

To build the docs in a `site` sub-directory:
```bash
./serve build
```
