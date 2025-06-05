# Contributing

This documentation is developed using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) framework, and the source code for the docs is publicly available on [GitHub](https://github.com/eth-cscs/cscs-docs).
This means that everybody, CSCS staff and the CSCS user community can contribute to the documentation.

## Getting started

We use the GitHub fork and pull request model for development:

* First create a fork of the [main GitHub repository](https://github.com/eth-cscs/cscs-docs).
* Make all proposed changes in branches on your fork - don't make branches on the main repository (we reserve the right to block creating branches on the main repository).

Clone your fork repository on your PC/laptop:
```bash
# clone your fork of the repository
git clone git@github.com:${githubusername}/cscs-docs.git
cd cscs-docs
git switch -c 'fix/ssh-alias'
# ... make your edits ...
# add and commit your changes
git add <files>
git commit -m 'update the ssh docs with aliases for all user lab vclusters'
git push origin 'fix/ssh-alias'
```
Then navigate to GitHub, and create a pull request.

The `serve` script in the root path of the repository can be used to view the docs locally:
```bash
./serve
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
## Review process

Documentation is owned by everybody - so don't be afraid to jump in and make changes or fixes where you see that there is something missing or outdated.

If you plan to make large changes or contributions, please discuss them with the documentation owners beforehand, to make sure that the documentation will fit into the larger documentation structure.

If the documentation that you write or update might affect multiple stakeholders, ping them for a review.
If you don't get a timely reply, ask the documentation owners for a review or for permission to merge.

!!! note
    To minimise the overhead of the contributing to the documentation and speed up "time-to-published-docs" we do not have a formal review process.
    We will start simple, and add more formality as needed.

## Guidelines

### Links

#### External links

Links to external sites use the `[]()` syntax:

=== "external link syntax"

    ```
    [The Spack repository](https://github.com/spack/spack)
    ```

=== "result"

    [The Spack repository](https://github.com/spack/spack)

#### Internal links

!!! note
    The CI/CD pipeline will fail if it detects broken links in your draft documentation.
    It is not completely foolproof - to ensure that your changes do not create broken links you should merge the most recent version of the `main` branch of the docs into your branch branch.

Adding and maintaining links to internal pages and sections that don't break or conflict requires care.
It is possible to refer to links in other files using relative links, for example `[the fast server](../servers.md#fast-server)`, however if the target file is moved, or the section title "fast-server" is changed, the link will break.

Instead, we advocate adding unique references to sections.

=== "adding a reference"

    Add a reference above the item, in this case we want to link to the section with the title `## The Fast Server`:

    ```
    [](){#ref-servers-fast}
    ## Fast Server
    ```

    Use the `[](){#}` syntax to define the reference/anchor.

    !!! note
        Always place the anchor above the item you are linking to.

=== "linking to a reference"

    In any other file in the project, use the `[][]` syntax to refer to the link (note that this link type uses square braces, instead of the usual parenthesis):

    ```
    [the fast server][ref-servers-fast]
    ```

The benefits of this approach are that the link won't break if

* either the file containing the link or the file that refers to the link move,
* or if the title of the target sections changes.

### Images

Images are stored in the `docs/images` directory.

* there are sub-directories in the `docs/images` path - create a new sub-directory for your images if appropriate
* choose image and path names that make sense - `screenshot.png` is not a great file name. Neither is `PX-202502025-imgx.png`.

!!! tip
    When providing a screenshot, do you need to show the whole screen, or just part of one window?

    Cropping the image will decrease file size, and might also draw the readers attention to the most relevant information.

!!! tip
    Do you need a screenshot, or can a text description also work?

### Text formatting

Turn off automatic line breaks in your text editor, and stick to one sentence per line in paragraphs of text.

See the good and bad examples below for an example of of what happens when a change to a sentence forces a line rebalance:

=== "good"
    Before:
    ```
    There are many different versions of MPI that can be used for communication.
    The final choice of which to use is up to you.
    ```

    After:
    ```
    There are many different versions of the popular MPI communication library that can be used for communication.
    The final choice of which to use is up to you.
    ```

    The diff in this case affects only one line.

=== "bad"
    Before:
    ```
    There are many different versions of MPI that
    can be used for communication. The final choice
    of which to use is up to you.
    ```

    After:
    ```
    There are many different versions of the popular
    MPI communication library that can be used for
    communication. The final choice of which to use
    is up to you.
    ```

    The diff in this case affects the original 3 lines, and creates a new one.

This method defines a canonical representation of text, i.e. there is one and only one way to write a paragraph of text, which plays much better with git.

* changes to the text are less likely to create merge conflicts
* changing one line of text will not modify the surrounding lines (see example above)
* git diffs and git history are easier to read.

### Frequently asked questions

The documentation does not have a FAQ section, because questions are best answered by the documentation, not in a separate section.
Integrating information into the main documentation requires some care to identify where the information needs to go, and edit the documentation around it.
Adding the information to a FAQ is easier, but the result is information about a topic distributed between the docs and FAQ questions, which ultimately makes the documentation harder to search.

FAQ content, such as lists of most frequently encountered error messages, is still very useful in many contexts.
If you want to add such content, create a section at the bottom of a topic page, for example this section on the [SSH documentation page][ref-ssh-faq].


### Small contributions

Small changes that only modify the contents of a single file, for example to fix some typos or add some clarifying detail to an example, it is possible to quickly create a pull request directly in the browser.

At the top of each page there is an "edit" icon :material-pencil:, which will open the markdown source for the page in the GitHub text editor.

Once your changes are ready, click on the "Commit changes..." button in the top right hand corner of the editor, and add at least a description commit message.

!!! tip
    See [the GitLab official guide on editing files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files) for a step-by-step walkthrough.

!!! note
    You will need to keep the default option **Create a new branch for this commit and start a pull request**.

    * if the change is small and you are CSCS staff, you can merge the PR immediately
    * all other changes can be

## Style guide

This section contains general guidelines for how to format and present documentation in this repository.
They should be followed for most cases, but as a guideline it can be broken, _with good reason_.

### Headings are written in sentence case

Use [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case) for headings, meaning all words are capitalized except for minor words.

### Avoid nesting headings too deep

Nesting headings up to three levels is generally ok.

### Lists

Write lists as proper sentences.
Separate the items simply with commas if each item is simple, or make each item a full sentence if the items are longer and contain multiple sentences.

1. The first item can look like this,
2. the second like this, and
3. the third item like this.

### Using admonitions

Aim to include examples, notes, warnings using [admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) whenever appropriate.
They stand out better from the main text, and can be collapsed by default if needed.

!!! example "Example one"
    This is an example.
    The title of the example uses [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case).
    
??? note "Collapsed note"
    This note is collapsed, because it uses `???`.
    
If an admonition is collapsed by default, it should have a title.

We provide some custom admonitions.

#### Change

For adding information about a change, originally designed for recording updates to clusters.

=== "Rendered"
    !!! change "2025-04-17"
        * SLURM was upgraded to version 25.1.
        * uenv was upgraded to v0.8

    Old changes can be folded:

    ??? change "2025-02-04"
        * The new Scratch cleanup policy was implemented
        * NVIDIA driver was updated

=== "Markdown"
    ```
    !!! change "2025-04-17"
        * SLURM was upgraded to version 25.1.
        * uenv was upgraded to v0.8
    ```

    Old changes can be folded:

    ```
    ??? change "2025-02-04"
        * The new Scratch cleanup policy was implemented
        * NVIDIA driver was updated
    ```

#### Under construction

For marking incomplete sections.

=== "Rendered"
    !!! under-construction
        This is not finished yet!

=== "Markdown"
    ```
    !!! under-construction
        This is not finished yet!
    ```

#### Todo

As a placeholder for documentation that needs to be written.

=== "Rendered"
    !!! todo
        Add some common error messages and how to fix them.

=== "Markdown"
    ```
    !!! todo
        Add some common error messages and how to fix them.
    ```

### Code blocks

Use [code blocks](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/) when you want to display monospace text in a programming language, terminal output, configuration files etc.
The documentation uses [pygments](https://pygments.org) for highlighting.
See [list of available lexers](https://pygments.org/docs/lexers/#) for the languages that you can use for code blocks.

Use [`console`](https://pygments.org/docs/lexers/#pygments.lexers.shell.BashSessionLexer) for interactive sessions with prompt-output pairs:

=== "Markdown"

    ````markdown
    ```console title="Hello, world!"
    $ echo "Hello, world!"
    Hello, world!
    ```
    ````

=== "Rendered"

    ```console title="Hello, world!"
    $ echo "Hello, world!"
    Hello, world!
    ```

!!! warning
    `terminal` is not a valid lexer, but MkDocs or pygments will not warn about using it as a language.
    The text will be rendered without highlighting.

!!! warning
    Use `$` as the prompt character, optionally preceded by text.
    `>` as the prompt character will not be highlighted correctly.

Note the use of `title=...`, which will give the code block a heading.

!!! tip
    Include a title whenever possible to describe what the code block does or is.

If you want to display commands without output that can easily be copied, use `bash` as the language:

=== "Markdown"

    ````markdown
    ```bash title="Hello, world!"
    echo "Hello, world!"
    ```
    ````

=== "Rendered"

    ```bash title="Hello, world!"
    echo "Hello, world!"
    ```
