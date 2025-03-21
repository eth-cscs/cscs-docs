# Style Guide

This guide contains general guidelines for how to format and present documentation in this repository.
They should be followed for most cases, but as a guideline it can be broken, _with good reason_.

The documentation is written using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## General Formatting

- Format paragraphs with one sentence per line for easier diffs.
- Leave a space before and after headings.

## Headings are Written in Title Case

Use [title case](https://en.wikipedia.org/wiki/Letter_case#Title_case) for headings, meaning all words are capitalized except for minor words.

## Avoid Nesting Headings too Deep

Nesting headings up to three levels is generally ok.

## Unordered and Ordered Lists

Write lists as proper sentences.
Separate the items simply with commas if each item is simple, or make each item a full sentence if the items are longer and contain multiple sentences.

1. The first item can look like this,
2. The second like this, and
3. The third item like this.

## Using Admonitions

Aim to include examples, notes, warnings using [admonitions](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) whenever appropriate.
They stand out better from the main text, and can be collapsed by default if needed.

!!! example "Example one"
    This is an example.
    The title of the example uses [sentence case](https://en.wikipedia.org/wiki/Letter_case#Sentence_case).
    
??? note "Collapsed note"
    This note is collapsed, because it uses `???`.

[](){#ref-style-references}
## References

Add references to headings to allow easier cross-referencing from other sections.
Prefix the reference name with `ref-`, followed by at least one level of identifier for the page itself.
Finally, add an identifier for the heading itself.
[This section][ref-style-references] uses the identifier `ref-style-references`.
