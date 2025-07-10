# Contributing

This documentation is developed using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) framework, and the source code for the docs is publicly available on [GitHub](https://github.com/eth-cscs/cscs-docs).
This means that everybody, CSCS staff and the CSCS user community can contribute to the documentation.

## Getting started

We use the GitHub fork and pull request model for development:

* First create a [fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) of the [main GitHub repository](https://github.com/eth-cscs/cscs-docs).
* Make all proposed changes in branches on your fork - don't make branches on the main repository (we reserve the right to block creating branches on the main repository).

Clone your fork repository on your PC/laptop:
```bash
# clone your fork of the repository
git clone git@github.com:${githubusername}/cscs-docs.git
cd cscs-docs
# create a branch for your changes (here we are fixing the ssh docs)
git switch -c 'fix/ssh-alias'
# ... make your edits ...
```

Review your edits checking the [Guidelines](#guidelines) section below.

!!! note
    Note that a simple editor markdown preview may not render all the features of the documentation.

To properly review the docs locally, the `serve` script in the root path of the repository can be used as shown below:
```bash
./serve
...
INFO    -  [08:33:34] Serving on http://127.0.0.1:8000/
```

!!! note
    To run the serve script, you need to first install [uv](https://docs.astral.sh/uv/getting-started/installation/).

You can now open your browser at the address shown above (`http://127.0.0.1:8000/`). The documentation will be automatically rebuilt and the webpage reloaded on each file change you save.

Alternatively, you can build the docs in a `site` sub-directory and open `site/index.html` with your browser too.

```bash
./serve build
```

After your first review, commit and push your changes
```bash
git add <files>
git commit -m 'update the ssh docs with aliases for all user lab vclusters'
git push origin 'fix/ssh-alias'
```

Then navigate to GitHub, and create a pull request.

!!! tip
    If you've already created a fork repository, make sure to [keep it synced](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork) to the main CSCS repository before making further change.

## Review process

Documentation is maintained by everybody - so don't be afraid to jump in and make changes or fixes where you see the need or the potential.

If you plan to make significantly large changes, please discuss them with an [issue](https://github.com/eth-cscs/cscs-docs/issues) beforehand, to ensure the changes will fit into the larger documentation structure.

If you think your documentation update could affect specific stakeholders, ping them for a review. The same applies if you are not getting get a timely reply for your pull request. You can get some hints of whom to contact by looking at [CODEOWNERS](https://github.com/eth-cscs/cscs-docs/blob/main/.github/CODEOWNERS).

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

> A picture is worth a thousand words

We encourage the usage of images to improve clarity and understanding. You can use **screenshots** or **diagrams**.

Images are stored in the `docs/images` directory.

* create a new sub-directory for your images if appropriate
* choose a path and file name that hint what the image is about - neither `screenshot.png` nor `PX-202502025-imgx.png` are great names.

!!! warning
    Keep the size of your images to a minimum because we want to keep an overall lightweight repository.


#### Screenshots

Screenshots can help readers follow steps on guides. Think if you need to show the whole screen or just part of one window. Cropping the image will decrease file size, and might also draw the readers attention to the most relevant information.

Often, screenshots can quickly become obsolete, so you may want to complement (or maybe even replace) some with text descriptions.

#### Diagrams

Diagrams can help readers understand more abstract concepts like processes or architectures. We suggest you use [mermaid](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams#creating-mermaid-diagrams). Such format makes diagrams easy to maintain and removes the need to commit image files in the repository.

??? "Example"

    === "Source"

        ````text
        ```mermaid
        graph TD;
            Image(Will image add value?);
            Image--NO-->T(keep text only);
            Image--YES-->SD(What image is needed?)
            SD--Screenshot-->S(keep it lean)
            SD--Diagram-->D(keep it maintainable)
            D--Default-->M(Mermaid)
            D--Custom-->DR(Draw.io)
        ```
        ````

    === "Rendered"

        ```mermaid
        graph TD;
            Image(Will image add value?);
            Image--NO-->T(keep text only);
            Image--YES-->SD(What image is needed?)
            SD--Screenshot-->S(keep it lean)
            SD--Diagram-->D(keep it maintainable)
            D--Default-->M(Mermaid)
            D--Custom-->DR(Draw.io)
        ```

If you need more hand-crafted diagrams, we suggest you use [draw.io](https://www.drawio.com/). Make sure you export the png with the [source inside](https://www.drawio.com/doc/faq/export-to-png), typically a `file.drawio.png`, so it can be extended in the future as needed.

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
    Use the default option **Create a new branch for this commit and start a pull request**.
    This allows others to review the change.
    Even for trivial changes, opening a PR creates visibility that a small fix or change has been made.

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
        * Slurm was upgraded to version 25.1.
        * uenv was upgraded to v0.8

    Old changes can be folded:

    ??? change "2025-02-04"
        * The new Scratch cleanup policy was implemented
        * NVIDIA driver was updated

=== "Markdown"
    ```
    !!! change "2025-04-17"
        * Slurm was upgraded to version 25.1.
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
