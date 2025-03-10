# Contributing

This documentation is developed using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) framework, and the source code for the docs is publicly available on [GitHub](https://github.com/eth-cscs/cscs-docs).
This means that everybody, CSCS staff and the CSCS user community can contribute to the documentation.

## Getting Started

We use the GitHub fork and pull request model for development:

* First create a fork of the [main GitHub repository](https://github.com/eth-cscs/cscs-docs).
* Make all proposed changes in branches on your fork - don't make branches on the main repository (we reserve the right to block creating branches on the main repository).

Clone your fork repository on your PC/laptop:
```bash
# clone your fork of the repository
> git clone git@github.com:${githubusername}/cscs-docs.git
> cd cscs-docs
> git switch -c 'fix/ssh-alias'
# ... make your edits ...
# add and commit your changes
> git add <files>
> git commit -m 'update the ssh docs with alisases for all user lab vclusters'
> git push origin 'fix/ssh-alias'
```
Then navigate to GitHub, and create a pull request.

The `serve` script in the root path of the repository can be used to view the docs locally:`
```
> ./serve
...
INFO    -  [08:33:34] Serving on http://127.0.0.1:8000/
```
This generates the documentation locally, which can be viewed using a local link, which is `http://127.0.0.1:8000/` by default.
The documentation will be rebuilt and the webpage reloaded when changed files are saved.

!!! note
    To run the serve script, you need to first install [uv](https://docs.astral.sh/uv/getting-started/installation/).

To build the docs in a `site` sub-directory:
```bash
./serve build
```
## Review Process

Documentation is owned by everybody - so don't be afraid to jump in and make changes or fixes where you see that there is something missing or outdated.

If you plan to make large changes or contributions, please discuss them with the documentation owners beforehand, to make sure that the documentation will fit into the larger documentation structure.

If the documentation that you write or update might affect multiple stakeholders, ping them for a review.
If you don't get a timely reply, ask the documentation owners for a review or for permission to merge.

!!! note
    To minimise the overhead of the contributing to the documentation and speed up "time-to-published-docs" we do not have a formal review process.
    We will start simple, and add more formality as needed.

## Guidelines

### Frequently Asked Questions

The documentation does not have a FAQ section, because questions are best answered by the documentation, not in a separate section.
Integrating information into the main documentation requires some care to identify where the information needs to go, and edit the documentation around it.
Adding the information to a FAQ is easier, but the result is information about a topic distributed betwen the docs and FAQ questions, which ultimately makes the documentation harder to search.

FAQ content, such as lists of most frequently encountered error messages, is still very useful in many contexts.
If you want to add such content, create a section at the bottom of a topic page, for example this section on the [SSH documentation page][ref-ssh-faq].

### Images

Images are stored in the `docs/images` directory.

* there are sub-directories in the `docs/images` path - create a new sub-directory for your images if appropriate
* choose image and path names that make sense - `screenshot.png` is not a great file name. Neither is `PX-202502025-imgx.png`.

!!! tip
    When providing a screenshot, do you need to show the whole screen, or just part of one window?

    Cropping the image will decrease file size, and might also draw the readers attention to the most relevant information.

!!! tip
    Do you need a screenshot, or can a text description also work?

## Small Contributions

Small changes that only modify the contents of a single file, for example to fix some typos or add some clarifying detail to an example, it is possible to quickly create a pull request directly in the browser.

At the top of each page there is an "edit" icon :material-pencil:, which will open the markdown source for the page in the GitHub text editor.

Once your changes are ready, click on the "Commit changes..." button in the top right hand corner of the editor, and add at least a description commit message.

!!! note
    You will need to keep the default option **Create a new branch for this commit and start a pull request**.

    * if the change is small and you are CSCS staff, you can merge the PR immediately
    * all other changes can be
