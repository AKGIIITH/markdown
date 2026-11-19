# Let me leave selected headings out of the table of contents

I use headings for short reminders in my lecture notes. I want those reminders
to stay visible and linkable on the page, but including each one in the table
of contents makes the outline harder to scan.

With the `attr_list` and `toc` extensions enabled, I'd like to choose a CSS
class through a TOC option such as `exclude_class="no-toc"`. For example:

```markdown
# Course
## Quick reminder {.aside .no-toc}
### Worked example
## Practice
```

With that setting, the page should still contain "Quick reminder" with its
heading ID and CSS classes. In the TOC, "Course" should have two entries
under it, "Worked example" followed by "Practice". I want to skip only
the marked heading, while keeping its unmarked children in the outline.

With no exclusion option configured, all four headings should appear in
the TOC as usual.

Baseline: 2c96e36ba4750cf18583d62e2fcecff49e077419
