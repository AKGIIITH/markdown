import unittest
import xml.etree.ElementTree as etree

import markdown
from markdown.extensions.toc import TocExtension


class TestTocSeparator(unittest.TestCase):
    def heading_id(self, extension):
        output = markdown.markdown('# Exam Notes', extensions=[extension])
        heading = etree.fromstring(output)
        self.assertEqual(heading.tag, 'h1')
        self.assertEqual(heading.text, 'Exam Notes')
        return heading.get('id')

    def test_tilde_separator_is_used(self):
        self.assertEqual(self.heading_id(TocExtension(separator='~')), 'exam~notes')

    def test_default_separator_is_preserved(self):
        self.assertEqual(self.heading_id(TocExtension()), 'exam-notes')

    def test_underscore_separator_is_preserved(self):
        self.assertEqual(self.heading_id(TocExtension(separator='_')), 'exam_notes')

    def assert_link_resolves(self, extension, expected):
        output = markdown.markdown('[TOC]\n\n# Exam Notes', extensions=[extension])
        root = etree.fromstring(f'<root>{output}</root>')
        link = root.find('.//a')
        self.assertIsNotNone(link)
        self.assertEqual(link.get('href'), '#' + expected)
        self.assertEqual(link.text, 'Exam Notes')
        matching = [heading for heading in root.findall('h1') if heading.get('id') == expected]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0].text, 'Exam Notes')

    def test_tilde_toc_link_resolves_to_heading(self):
        self.assert_link_resolves(TocExtension(separator='~'), 'exam~notes')

    def test_default_toc_link_resolves_to_heading(self):
        self.assert_link_resolves(TocExtension(), 'exam-notes')
