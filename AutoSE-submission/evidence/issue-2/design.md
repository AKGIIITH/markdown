## Source evidence
Relevant application file: `markdown/extensions/toc.py` (lines 39‑48 show slugify forcing hyphen when separator is "~"; lines 409‑426 show heading ID generation using `self.slugify(..., self.sep)`). Public test example: `tests/test_syntax/extensions/test_toc.py` (lines 1037‑1061 demonstrate that a heading ID and its TOC link are generated consistently for the default separator). The test confirms that the slugified ID used on the heading element matches the href in the generated TOC entry.

## Implementation plan
1. **Edit slugify** in `markdown/extensions/toc.py` (function starting at line 39). Remove the special‑case that rewrites a "~" separator to "-". Instead, use the separator value directly. Updated logic:
```python
def slugify(value: str, separator: str, unicode: bool = False) -> str:
    if not unicode:
        value = unicodedata.normalize('NFKD', value)
        value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    # Collapse runs of the separator or whitespace into a single separator
    return re.sub(r'[{}\s]+'.format(re.escape(separator)), separator, value)
```
2. **Ensure TocExtension passes the configured separator** to the treeprocessor. In `TocExtension.__init__` add a config entry `'separator'` with default `'-'` (mirroring existing behavior). Update `extendMarkdown` (or the TreeProcessorClass init) to store `self.sep = self.getConfig('separator')` and pass it to `TocTreeprocessor`.
3. **Update TocTreeprocessor** (class `TocTreeprocessor` in the same file) to use the stored `self.sep` when calling `self.slugify`. The existing call at line 409 already uses `self.sep`; after step 2 it will reflect the user‑provided separator.
4. **Preserve explicit IDs** – the existing logic already skips slugification when an `id` attribute is present (lines 407‑410). No change needed.
5. **Add unit tests** for the new separator ("~") and existing underscore case. Tests can reuse the helper `assertMarkdownRenders` from the test suite.
6. **Documentation** – update the TocExtension docstring to mention the new `separator` option and its effect on generated IDs and TOC links.

No new files are required; only modifications to existing `toc.py` and addition of a config entry. All changes respect the current API: the `separator` option is a string, default `'-'`, and is read via `Extension.getConfig`, which already handles type conversion.

**Inspected path and function**: `markdown/extensions/toc.py` → `slugify` and `TocTreeprocessor` (ID generation at line 409).

## Public tests
- AC 1: input `markdown.markdown("# Exam Notes", extensions=[TocExtension(separator="~")])`; assert heading `<h1 id="exam~notes">Exam Notes</h1>`.
- AC 2: same input; assert TOC link contains `href="#exam~notes"`.
- AC 3: input with default extension (`TocExtension()`); assert heading id `exam-notes` and TOC href `#exam-notes`.
- AC 4: input with `separator="_"`; assert heading id `exam_notes` and TOC href `#exam_notes`.
- AC 5: input `# Exam Notes {#custom-id}` with `separator="~"`; assert heading id `custom-id` and TOC href `#custom-id`.