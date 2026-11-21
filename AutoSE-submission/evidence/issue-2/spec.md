# Requirements

When the TOC extension is configured with a custom separator (e.g., "~"), automatically generated heading IDs and the corresponding TOC links must use that separator, while the default hyphen and underscore separators continue to work and any explicitly supplied heading IDs must be preserved unchanged.

## Acceptance criteria

1. Given Markdown input "# Exam Notes" and the TOC extension instantiated with separator="~", when the markdown is rendered to HTML, then the generated heading element has id="exam~notes".
2. Given Markdown input "# Exam Notes" and the TOC extension instantiated with separator="~", when the markdown is rendered to HTML, then the generated TOC link href attribute is "#exam~notes".
3. Given Markdown input "# Exam Notes" with the TOC extension using the default separator (no separator argument), when the markdown is rendered to HTML, then the generated heading element has id="exam-notes" and the TOC link href is "#exam-notes".
4. Given Markdown input "# Exam Notes" and the TOC extension instantiated with separator="_", when the markdown is rendered to HTML, then the generated heading element has id="exam_notes" and the TOC link href is "#exam_notes".
5. Given Markdown input "# Exam Notes {#custom-id}" (explicit heading ID) and the TOC extension instantiated with separator="~", when the markdown is rendered to HTML, then the heading element retains id="custom-id" and the TOC link href is "#custom-id".

## Unresolved questions

