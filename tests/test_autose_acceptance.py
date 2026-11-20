import unittest
import xml.etree.ElementTree as ET

import markdown
from markdown.test_tools import TestCase


class TestTableClass(TestCase):
    """Tests for the table_class configuration option of the tables extension."""

    def _render(self, text, config=None):
        """Render Markdown text with the tables extension and optional config."""
        return markdown.markdown(
            text,
            extensions=["tables"],
            extension_configs={"tables": config or {}},
        )

    def _parse_tables(self, html):
        """Parse the rendered HTML and return a list of <table> elements."""
        # Wrap the output in a root element to parse multiple top-level tables.
        root = ET.fromstring(f"<div>{html}</div>")
        return root.findall(".//table")

    def _check_table(self, table, expected_headers, expected_body_rows):
        """Check that a table has the expected headers and body rows."""
        headers = [th.text for th in table.findall(".//thead/tr/th")]
        self.assertEqual(headers, expected_headers)

        body_rows = table.findall(".//tbody/tr")
        self.assertEqual(len(body_rows), len(expected_body_rows))
        for row, expected_row in zip(body_rows, expected_body_rows):
            cells = [td.text for td in row.findall("td")]
            self.assertEqual(cells, expected_row)

    def test_table_class_single(self):
        """When table_class is set to a single class, all tables receive that class."""
        markdown_text = """\
| Header1 | Header2 |
|---------|---------|
| Cell1   | Cell2   |

| A | B |
|---|---|
| X | Y |
"""
        rendered = self._render(markdown_text, {"table_class": "report-table"})
        tables = self._parse_tables(rendered)
        self.assertEqual(len(tables), 2)

        for index, table in enumerate(tables):
            self.assertEqual(table.get("class"), "report-table")
            if index == 0:
                self._check_table(table, ["Header1", "Header2"], [["Cell1", "Cell2"]])
            else:
                self._check_table(table, ["A", "B"], [["X", "Y"]])

    def test_table_class_multiple(self):
        """When table_class contains multiple space-separated classes, all tables receive them."""
        markdown_text = """\
| Header1 | Header2 |
|---------|---------|
| Cell1   | Cell2   |

| A | B |
|---|---|
| X | Y |
"""
        rendered = self._render(markdown_text, {"table_class": "report-table compact"})
        tables = self._parse_tables(rendered)
        self.assertEqual(len(tables), 2)

        for index, table in enumerate(tables):
            class_attr = table.get("class")
            self.assertIsNotNone(class_attr)
            # Order of classes is not significant
            class_tokens = set(class_attr.split())
            self.assertEqual(class_tokens, {"report-table", "compact"})
            if index == 0:
                self._check_table(table, ["Header1", "Header2"], [["Cell1", "Cell2"]])
            else:
                self._check_table(table, ["A", "B"], [["X", "Y"]])

    def test_table_class_default(self):
        """When table_class is omitted, tables should have no class attribute."""
        markdown_text = """\
| Header1 | Header2 |
|---------|---------|
| Cell1   | Cell2   |

| A | B |
|---|---|
| X | Y |
"""
        rendered = self._render(markdown_text)  # No config passed
        tables = self._parse_tables(rendered)
        self.assertEqual(len(tables), 2)

        for index, table in enumerate(tables):
            self.assertIsNone(table.get("class"))
            if index == 0:
                self._check_table(table, ["Header1", "Header2"], [["Cell1", "Cell2"]])
            else:
                self._check_table(table, ["A", "B"], [["X", "Y"]])


if __name__ == "__main__":
    unittest.main()
