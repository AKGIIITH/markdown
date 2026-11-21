# Python-Markdown architecture

## Purpose and source revision

Python-Markdown converts Markdown source into HTML or XHTML. Use this guide
to trace a reported behavior through the application and produce a design
that another agent can implement and test.

The workflow supplies the public issue, accepted requirements, and application
commit. Issues 1, 3, 4, and 5 use application commit
`2c96e36ba4750cf18583d62e2fcecff49e077419`. Issue 2 uses the seeded commit
`1e2b7f27aeefe70057025a1da0d10006dd11ad48` on `a3/bug02-seed`.

The workflow branch can contain newer development tools and documents.
Inspect application source and tests at the commit selected for the issue.
Use `git show <commit>:<path>` to read a file at that revision.

## Conversion path

| Component | Responsibility | Starting point |
| --- | --- | --- |
| Public API and CLI | Accept text, files, options, and extension configuration. The CLI delegates conversion and exposes a process exit status. | `markdown/core.py`, `markdown/__main__.py` |
| Preprocessors | Transform lists of source lines before parsing. Extensions can recognize source syntax and stash content for later restoration. | `markdown/preprocessors.py` |
| Block parser | Dispatch blocks to processors that construct ElementTree nodes for paragraphs, headings, lists, tables, and other structures. Nested content can re-enter block parsing. | `markdown/blockparser.py`, `markdown/blockprocessors.py` |
| Tree and inline processors | Traverse and transform the intermediate tree. Inline recognition runs during tree processing. A tree processor can modify nodes in place or return a replacement root. | `markdown/treeprocessors.py`, `markdown/inlinepatterns.py` |
| Serialization | Convert the intermediate tree to the selected HTML or XHTML representation, including element text and attributes. | `markdown/serializers.py` |
| Postprocessing | Transform serialized output text and restore stashed fragments. Some HTML visible in the final output bypasses ordinary tree serialization. | `markdown/postprocessors.py`, `HtmlStash` in `markdown/util.py` |

Follow one representative input from its public entry point to its observable
output. A generated table and a fenced code block both appear as HTML, but
their producers can handle attributes at different stages. Locate the
producer before proposing a change to shared serialization code.

## Extension configuration, ordering, and state

`markdown/extensions/__init__.py` defines the `Extension` base class and its
configuration helpers. An extension attaches behavior through `extendMarkdown`.
For a configuration issue, trace where the option is declared, how its value
reaches the registered processor, and which operation consumes it. Inspect
the path taken when the caller omits the option.

`markdown/util.py` defines named, priority-ordered registries. Higher numeric
priorities run earlier. Reusing a registration name can replace a processor.
When proposing an ordering change, identify the producer and consumer whose
interaction depends on that order.

A `Markdown` instance owns its configured parser, registries, HTML stash,
and registered stateful extensions. `Markdown.reset` clears document-level
state and invokes reset hooks on registered extensions. For a change that
stores per-document data, identify who owns that data and how a caller
reusing a converter starts the next document.

## Where to investigate an issue

| Reported behavior | Starting point | Question for the pinned source |
| --- | --- | --- |
| Fenced code attributes | `markdown/extensions/fenced_code.py` | Which rendering path handles the enabled extensions, and what value reaches attribute rendering? |
| Heading links and table of contents | `markdown/extensions/toc.py` | Where are IDs assigned, entries selected, and parent-child relationships built? Inspect both the document and the navigation output. |
| Markdown tables | `markdown/extensions/tables.py` | How is the table processor registered, and which method constructs each table element? |
| File conversion errors | `markdown/__main__.py`, `markdown/core.py` | Where does the file operation fail, and which layer owns the user-facing diagnostic and exit status? |
| Extension interactions | Each extension's `extendMarkdown` and target registry | Which processor produces a value, which consumes it, and in what order do they run? |

Confirm exact files and symbols at the selected commit. Use ordinary repository
tests as evidence of expected behavior. The experiment's private acceptance
tests are held separately for evaluation.

## Design-stage handoff

Write `design.md` with enough detail for the Builder to make and verify the
change:

1. Record the issue, application commit, public entry point, requested
   behavior, and compatibility expectation.
2. Trace the existing behavior through specific files, classes, and methods.
   Distinguish observations from predictions based on reading the source.
3. Name each proposed edit location and explain why that component owns the
   change. Label proposed new symbols explicitly.
4. Map every accepted criterion to a test location, input, and observable
   assertion. Use semantic assertions where equivalent outputs satisfy the
   issue.
5. Identify any missing evidence or ambiguity that materially changes the
   design. Record discrepancies between this guide and the pinned source.

A usable plan explains how the proposed change reaches the user-visible
behavior and how each criterion will be checked. Record build, test, CI, and
review results when those stages run.
