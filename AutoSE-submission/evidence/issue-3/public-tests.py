import unittest
import markdown
from xml.etree import ElementTree as ET


class TestTableClassOption(unittest.TestCase):
    """Tests for the ``table_class`` option of the tables extension."""

    def _render(self, text, table_class=None):
        """Render *text* to HTML using the tables extension.

        If *table_class* is provided it is passed via ``extension_configs``.
        """
        if table_class is not None:
            ext_cfg = {"tables": {"table_class": table_class}}
        else:
            ext_cfg = {}
        md = markdown.Markdown(extensions=["tables"], extension_configs=ext_cfg)
        return md.convert(text)

    def _find_table(self, html):
        """Return the first <table> element parsed from *html*."""
        # Wrap in a root element to ensure well‑formed XML.
        root = ET.fromstring(f"<root>{html}</root>")
        return root.find(".//table")

    def test_single_class_applied(self):
        """Generated tables receive the configured single CSS class."""
        md = (
            "| Header1 | Header2 |\n"
            "|--------|--------|\n"
            "| Cell1  | Cell2  |\n"
        )
        html = self._render(md, table_class="report-table")
        table = self._find_table(html)
        self.assertIsNotNone(table, "No <table> element found in output")
        self.assertEqual(table.get("class"), "report-table")
        # Verify header and cell contents are preserved.
        header_cells = [c.text for c in table.find("thead").findall("tr/th")]
        self.assertEqual(header_cells, ["Header1", "Header2"])
        body_cells = [c.text for c in table.find("tbody").findall("tr/td")]
        self.assertEqual(body_cells, ["Cell1", "Cell2"])

    def test_multiple_classes_preserved(self):
        """Generated tables receive multiple CSS classes preserving spaces."""
        md = (
            "| H1 | H2 |\n"
            "|----|----|\n"
            "| A  | B  |\n"
        )
        html = self._render(md, table_class="report-table compact")
        table = self._find_table(html)
        self.assertIsNotNone(table, "No <table> element found in output")
        self.assertEqual(table.get("class"), "report-table compact")
        # Verify content.
        header = [c.text for c in table.find("thead").findall("tr/th")]
        self.assertEqual(header, ["H1", "H2"])

    def test_no_class_when_option_omitted(self):
        """When ``table_class`` is omitted, generated tables have no class attribute."""
        md = (
            "| X | Y |\n"
            "|---|---|\n"
            "| 1 | 2 |\n"
        )
        html = self._render(md)
        table = self._find_table(html)
        self.assertIsNotNone(table, "No <table> element found in output")
        self.assertIsNone(table.get("class"))
        # Ensure the table still contains the expected cells.
        self.assertIn("<th>X</th>", html)
        self.assertIn("<td>1</td>", html)

    def test_raw_html_table_unchanged(self):
        """Raw HTML tables are emitted unchanged regardless of the option."""
        raw = '<table class="custom"><tr><td>Raw</td></tr></table>'
        md = f"{raw}\n\n| H | I |\n|---|---|\n| J | K |\n"
        html = self._render(md, table_class="report-table")
        # The raw table should appear exactly as provided.
        self.assertIn(raw, html)
        # Ensure the generated table has the class while the raw one does not gain it.
        generated_table = self._find_table(html.replace(raw, ""))
        self.assertIsNotNone(generated_table, "Generated <table> not found")
        self.assertEqual(generated_table.get("class"), "report-table")
        # Verify the raw table still has its original class attribute.
        self.assertIn('<table class="custom">', html)


if __name__ == "__main__":
    unittest.main()
