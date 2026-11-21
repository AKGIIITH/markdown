# Heading links use hyphens when I configure a tilde separator

My site links to headings using URLs such as `#exam~notes`. When I render
`# Exam Notes` with the `toc` extension configured to use `~` between
words, the heading gets the ID `exam-notes`. As a result, the existing
link does not point to the heading.

## How to reproduce

```python
import markdown
from markdown.extensions.toc import TocExtension

print(markdown.markdown("# Exam Notes", extensions=[TocExtension(separator="~")]))
```

Expected heading ID: exam~notes
Actual heading ID: exam-notes

The default separator produces exam-notes, and configuring _ produces
exam_notes, both as expected.

Affected branch: a3/bug02-seed
Affected commit: 1e2b7f27aeefe70057025a1da0d10006dd11ad48

## Acceptance scope

With the TOC extension enabled, a heading whose ID is generated automatically
uses the configured separator in the actual heading `id`. Its generated TOC
link must point to that same ID. For `# Exam Notes` and `separator="~"`, the
heading has `id="exam~notes"` and the TOC link has `href="#exam~notes"`.
The default hyphen and configured underscore still work. Preserve explicit
heading IDs.
