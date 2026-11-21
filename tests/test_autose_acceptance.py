import unittest
import re
import markdown
from markdown.extensions.tables import TableExtension


class TestTableClassOption(unittest.TestCase):
    def _render(self, text, **ext_kwargs):
        """Render markdown text with the tables extension.
        ext_kwargs are passed to TableExtension.
        """
        extensions = [TableExtension(**ext_kwargs)]
        return markdown.markdown(text, extensions=extensions)

    def _extract_tables(self, html):
        """Return the opening tag and class attribute for each table.
        The class attribute is the raw string or None.
        """
        pattern = re.compile(r'<table(?P<attrs>[^>]*)>', re.IGNORECASE)
        tables = []
        for m in pattern.finditer(html):
            attrs = m.group('attrs')
            class_match = re.search(r'\bclass\s*=\s*"([^"]*)"', attrs)
            class_val = class_match.group(1) if class_match else None
            tables.append((m.group(0), class_val))
        return tables

    def test_table_class_single(self):
        md = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
        html = self._render(md, table_class='report-table')
        tables = self._extract_tables(html)
        self.assertEqual(len(tables), 1, "Expected exactly one <table> element")
        _, class_attr = tables[0]
        self.assertIsNotNone(class_attr, "Table should have a class attribute")
        tokens = set(class_attr.split())
        self.assertEqual(tokens, {'report-table'})
        # Ensure content is present
        self.assertIn('Header 1', html)
        self.assertIn('Cell 2', html)

    def test_table_class_multiple_tokens(self):
        md = """
| H1 | H2 |
|----|----|
| A  | B  |
"""
        html = self._render(md, table_class='report-table compact')
        tables = self._extract_tables(html)
        self.assertEqual(len(tables), 1)
        _, class_attr = tables[0]
        self.assertIsNotNone(class_attr)
        tokens = set(class_attr.split())
        self.assertEqual(tokens, {'report-table', 'compact'})
        # Content check
        self.assertIn('H1', html)
        self.assertIn('B', html)

    def test_table_class_default(self):
        md = """
| Col1 | Col2 |
|------|------|
| X    | Y    |
"""
        html = self._render(md)  # No table_class option
        tables = self._extract_tables(html)
        self.assertEqual(len(tables), 1)
        _, class_attr = tables[0]
        self.assertIsNone(class_attr, "Table should not have a class attribute when option is omitted")
        # Content check
        self.assertIn('Col1', html)
        self.assertIn('Y', html)

    def test_table_content_preserved_with_class(self):
        md = """
| A1 | A2 |
|----|----|
| a  | b  |

| B1 | B2 |
|----|----|
| c  | d  |
"""
        html = self._render(md, table_class='report-table')
        tables = self._extract_tables(html)
        self.assertEqual(len(tables), 2, "Expected two tables in the output")
        # Verify both tables have the class attribute
        for _, class_attr in tables:
            self.assertIsNotNone(class_attr)
            self.assertIn('report-table', class_attr.split())
        # Verify content of each table is preserved
        self.assertIn('A1', html)
        self.assertIn('b', html)
        self.assertIn('B1', html)
        self.assertIn('d', html)


if __name__ == '__main__':
    unittest.main()
