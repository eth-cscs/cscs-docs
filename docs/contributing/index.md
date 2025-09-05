[](){#ref-contributing}
# Contributing

This documentation is developed using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) framework, and the source code for the docs is publicly available on [GitHub](https://github.com/eth-cscs/cscs-docs).
This means that everybody, CSCS staff and the CSCS user community can contribute to the documentation.

## Making suggestions or small changes

If you have a suggestion, comment or small change to make when reading the documentation, there are three ways to reach out.

1.  **Edit the page inline**: click on the :material-pencil: icon on the top right hand corner of each page, and make the change inline. When you click "commit", and create a pull request, which will then be reviewed by the CSCS docs team.
1.  **Create a GitHub issue**: create an issue on the [issue page](https://github.com/eth-cscs/cscs-docs/issues) on the GitHub repository.
1.  **Create a CSCS service desk ticket**: create a ticket on the CSCS service desk.
    This is useful if you don't have a GitHub account, or would prefer not to use Github.

## Before starting

The CSCS documentation takes contributions from all CSCS staff, with a _core team_ of maintainers responsible for ensuring that the overall documentation is well organised, that pages are well written and up to date, and that contributions are reviewed and merged as quickly as possible.

??? question "Who are the core team?"
    The docs core team are:

    * Ben Cumming (@bcumming);
    * Mikael Simberg (@msimberg);
    * and Rocco Meli (@RMeli).

    We are volunteers for this role, who care about the quality of CSCS documentation!

!!! tip "Before contributing"
    Please read the [guidelines][] and [style guide][] before making any contribution.
    Consistency and common practices make it easier for users to read and navigate the documentation, make it easier for regular contributors to write, and avoid style debates.
    We try to strike a balance between following the guidelines and letting authors write in a style that is comfortable for them.

    To speed up the merge process and avoid lengthy style discussions, we reserve the right to make changes to pull requests to bring it into line with the guidelines.
    The core team will also update pages when they are out of date or when the style guidelines change.
!!! tip "Before making large contributions"
    If you plan to make large changes, like adding documentation for a new tool/service or refactoring existing documentation, __reach out to the core team__ before starting.

    This will mean that the changes are consistent with other parts of the documentation, streamline the review process, and to avoid misunderstandings.

### Code owners

Many sections have individual staff that follow them.
This is codified in the [CODEOWNERS](https://github.com/eth-cscs/cscs-docs/blob/main/.github/CODEOWNERS) file in the repository.
The code owners are notified when there is a change to their pages, and can review the changes.

If you want to follow changes to a page or section, add your name to the CODEOWNERS.

!!! note
    Review from code owners is not required to merge, however the core team will try to get a timely review from code owners whenever possible.

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

Review your edits checking the [Guidelines][ref-contributing-guidelines] section below.

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

After you have made a pull request, a CI/CD pipeline will run the [spell checker][ref-contributing-spelling] and build a copy of the docs with the PR changes.
A temporary "TDS" copy of the docs is deployed, to allow reviewers to see the finished documentation, at the address `https://docs.tds.cscs.ch/$PR`, where `PR` is the number of the pull request.

To make changes based on reviewer feedback, make a new commit on your branch, and push it to your fork.
The PR will automatically be updated, the spell checker will run again, and the TDS documentation site will be rebuilt.

!!! tip
    If you think your documentation update could affect specific stakeholders, ping them for a review.
    You can get some hints of whom to contact by looking at [CODEOWNERS](https://github.com/eth-cscs/cscs-docs/blob/main/.github/CODEOWNERS).
    If they don't reply in a timely manner, reach out to the core docs team to expedite the process.

!!! note
    To minimise the overhead of the contributing to the documentation and speed up "time-to-published-docs" we do not have a formal review process.
    We will start simple, and add more formality as needed.

[](){#ref-contributing-spelling}
### Spell checker

A spell checker workflow runs on all PRs to help catch simple typos.
If the spell checker finds words that it considers misspelled, it will add a comment like [this](https://github.com/eth-cscs/cscs-docs/pull/193#issuecomment-3056795496) to the PR, listing the words that it finds misspelled.

The spell checker isn't always right and can be configured to ignore words.
Most frequently technical terms, project names, etc. will not be in the dictionaries.
There are three files used to configure words that get ignored:

- `.github/actions/spelling/allow.txt`:
  This is the main file for whitelisting words.
  Each line of the file contains a word that is ignored by the spell checker.
  All lowercase words are matched with any capitalization, while words containing at least one uppercase letter are matched with the given capitalization.
  Using the capitalized word is useful if you always want to ensure the same spelling, e.g. for names.
<!--begin no spell check-->
- `.github/actions/spelling/patterns.txt`:
  This file is used to ignore words that match a given regular expression.
  This file is useful to ignore e.g. URLs or markdown references.
  Words that have unusual capitalization may also need to be added to this file to make sure they are ignored.
  For example, "FirecREST" is normally recognized as two words: "Firec" and "REST", and adding "FirecREST" to `allow.txt` will not ignore the word.
  In this case it can be ignored by adding it to `patterns.txt`
<!--end no spell check-->
- `.github/actions/spelling/block-delimiters.txt`:
  This file can be used to ignore words between begin- and end markers.
  For example, code blocks starting and ending with `` ``` `` are ignored from spell checking as they often contain unusual words not in dictionaries.
  If adding words to `allow.txt` or `patterns.txt`, or ignoring blocks with `block-delimiters.list`, is not sufficient, you can as a last resort use the HTML comments `<!--begin no spell check-->` and `<!--end no spell check-->` to ignore spell checking for a larger block of text.
  The comments will not be rendered in the final documentation.

Additionally, the file `.github/actions/spelling/only.txt` contains a list of regular expressions used to match which files to check.
Only markdown files under the `docs` directory are checked.

[](){#ref-contributing-guidelines}
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

    Add a reference above the item, in this case we want to link to the section with the title `## The fast server`:

    ```
    [](){#ref-fast-server}
    ## Fast server
    ```

    Use the `[](){#}` syntax to define the reference/anchor.

    !!! note
        Always place the anchor above the item you are linking to.

=== "linking to a reference"

    In any other file in the project, use the `[][]` syntax to refer to the link (note that this link type uses square braces, instead of the usual parenthesis):

    ```
    [the fast server][ref-fast-server]
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

!!! tip
    Screen shots take up space in the git repository.

    It might be "only a few hundred kilobytes" for a picture, but over the lifetime of the git repository this adds up to slow down source code cloning and CI/CD pipelines.

!!! tip
    Avoid using screen shots that do not directly contribute to the documentation.

    For example, showing a screen shot with markers that are used to explain non-trivial steps that a user should follow is good documentation.
    On the other hand, a screenshot that says "this is a screenshot of the tool" adds no value, and draws the readers attention away from documentation.

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
    See [the GitHub official guide on editing files](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files) for a step-by-step walkthrough.

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

### Avoiding repetition using snippets

It can be useful to repeat information on different pages to increase visibility for users.
If possible, prefer linking to a primary section describing a topic instead of fully repeating text on different pages.
However, if you believe it's beneficial to actually repeat the content, consider using [snippets](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/) to avoid repeated information getting out of sync on different pages.
Snippets allow including the contents of a text file in multiple places of the documentation.

For example, the recommended NCCL environment variables are defined in a text file [`docs/software/commuinication/nccl_env_vars`](https://github.com/eth-cscs/cscs-docs/blob/main/docs/software/communication/nccl_env_vars) and included on multiple pages because it's essential that users of NCCL notice and use the environment variables.

Snippets are included with `--8<-- path/to/snippet`.
For example, to include the recommended NCCL environment variables, do the following:

=== "Markdown"

    ````markdown
    ```bash
    ;--8<-- "docs/software/communication/nccl_env_vars"
    ```
    ````

=== "Rendered"

    ```bash title="Recommended NCCL environment variables"
    --8<-- "docs/software/communication/nccl_env_vars"
    ```

## Documentation structure

Here we describe a high-level overview of the documentation layout and organisation.

!!! under-construction
    This section is mostly incomplete, and will be expanded over time.

Note that the directory layout, where markdown files are stored in the repository, does not strictly reflect the section of the documentation where the content is displayed because:

* the URL of a page is decided by its location in the directory tree, not in the table of contents.
  If a page is moved in the ToC, we are conservative about moving the file, so that urls don't break.
* pages can be included in multiple locations in the ToC (not a feature that we use very often).

### Tutorials

All tutorials are stored in the `/docs/tutorials` directory.
Currently we only have ML tutorials in `/docs/tutorials/ml`.

There is no top level "Tutorials" section, instead tutorial content can be include directly in the docs where most appropriate.
The ML tutorials, for example, are alongside the PyTorch documentation in the Applications and Frameworks material.

!!! note "rationale"
    Group all tutorial content together in the directory structure so that the url of specific tutorials won't change when they are moved around.
