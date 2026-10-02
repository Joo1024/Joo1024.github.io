#!/usr/bin/env python3
"""Regression tests build isolated Markdown fixtures through the real Hugo templates.

Run: python3 -m unittest discover -s tests -p 'test_*.py' -v
HUGO_BIN can override the default .tools/bin/hugo.
"""
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import subprocess
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class Anchors(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for attribute in ('href', 'src'):
            if attribute in attrs:
                self.links.append(attrs[attribute])


class ContentTest(unittest.TestCase):
    def test_empty_later_notes_do_not_create_a_homepage_link(self):
        with TemporaryDirectory(prefix='sanctum-empty-note-') as tmp:
            root = Path(tmp)
            section = root / 'content' / 'notes'
            section.mkdir(parents=True)
            (section / 'empty.md').write_text('---\ntitle: Empty\ndate: 2026-01-01\nstatus: note\nlater_notes: []\n---\nContent.\n')
            output = root / 'public'
            result = subprocess.run([os.environ.get('HUGO_BIN', str(ROOT / '.tools/bin/hugo')),
                                     '--source', str(ROOT), '--contentDir', str(root / 'content'),
                                     '--destination', str(output)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            home = Anchors((output / 'index.html').read_text())
            self.assertFalse(any(link.endswith('#later-notes') for link in home.links), 'An empty list must not advertise a nonexistent later-note anchor')

    def test_relative_feed_urls_and_independent_later_note_footnotes(self):
        """A reader can open media/links; each note points to its own footnote."""
        with TemporaryDirectory(prefix='sanctum-regression-') as tmp:
            root = Path(tmp)
            section = root / 'content' / 'reflection'
            section.mkdir(parents=True)
            (section / '_index.md').write_text('---\ntitle: Reflection\n---\n')
            (section / 'entry.md').write_text('''---
title: Fixture
date: 2025-01-01
lastmod: 2026-01-03
status: reflection
later_notes:
  - date: 2026-01-02
    text: |
      ## Revisited
      First note.[^1]

      [^1]: Footnote belonging to first note.
  - date: 2026-01-03
    text: |
      ## Revisited
      Second note.[^1]

      [^1]: Footnote belonging to second note.
---

## Revisited

Original body.[^1]

[^1]: Footnote belonging to original body.

![Ridge](../../images/ridge.svg)

[Other](../other/)
''')
            (section / 'other.md').write_text('---\ntitle: Other\ndate: 2025-01-02\nstatus: note\n---\nOther article.\n')
            output = root / 'public'
            command = [os.environ.get('HUGO_BIN', str(ROOT / '.tools/bin/hugo')),
                       '--source', str(ROOT), '--contentDir', str(root / 'content'),
                       '--baseURL', 'https://example.com/sanctum/', '--destination', str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            article = Anchors((output / 'reflection/entry/index.html').read_text())
            self.assertEqual(len(article.ids), len(set(article.ids)), 'Body and later notes must have unique heading/footnote IDs')
            refs = [link for link in article.links if link.startswith('#') and 'fn:' in link]
            self.assertEqual(len(refs), 3)
            self.assertEqual(len(set(refs)), 3, 'Each citation must target a separate footnote')
            for ref in refs:
                self.assertIn(ref[1:], article.ids)
            rss = ET.fromstring((output / 'index.xml').read_text())
            entry = next(item for item in rss.findall('./channel/item') if item.findtext('title') == 'Fixture')
            feed = Anchors(entry.findtext('description'))
            self.assertIn('https://example.com/sanctum/images/ridge.svg', feed.links)
            self.assertIn('https://example.com/sanctum/reflection/other/', feed.links)
            for link in feed.links:
                self.assertTrue(link.startswith('https://example.com/sanctum/'), link)
            self.assertIn('2025', entry.findtext('pubDate'), 'Later notes must retain original RSS publication date')


if __name__ == '__main__':
    unittest.main()
