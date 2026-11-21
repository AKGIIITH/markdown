# Requirements

Add a configurable `table_class` option to the Markdown tables extension so that generated tables receive the specified CSS class(es) while preserving content, and ensure that raw HTML tables remain unchanged and that omission of the option leaves generated tables without a class attribute.

## Acceptance criteria

1. Given the tables extension is configured with `table_class="report-table"` and the Markdown input contains a standard Markdown table, when the document is converted to HTML, then the output contains a `<table>` element with `class="report-table"` and the table’s header and cell contents match the source.
2. Given the tables extension is configured with `table_class="report-table compact"` and the Markdown input contains a standard Markdown table, when the document is converted to HTML, then the output contains a `<table>` element with `class="report-table compact"` (preserving the space between class names) and the table’s header and cell contents match the source.
3. Given the tables extension is used without specifying the `table_class` option and the Markdown input contains a standard Markdown table, when the document is converted to HTML, then the output `<table>` element has no `class` attribute, matching current behavior.
4. Given the Markdown input contains a raw HTML `<table class="custom">` element and the tables extension is configured with any `table_class` value or none, when the document is converted to HTML, then the raw HTML `<table>` is emitted unchanged, preserving its existing `class` attribute and contents.

## Unresolved questions

