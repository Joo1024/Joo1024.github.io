"""Public sources remain compatible with the private notebook's metadata."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from hugo_helpers import create_content, build_site


class SourcesTest(unittest.TestCase):
    def build(self, root, metadata=''):
        content = create_content(root)
        (content / 'posts').mkdir()
        (content / 'posts/2025-03-02-01.md').write_text(
            '---\ntitle: Post\ndate: 2025-03-02\nform: brief\n' + metadata + '---\nPost.\n')
        return build_site(root)

    def test_public_sources_support_shared_kinds_without_private_paths(self):
        for sources in ('[]', '[{kind: note, title: Public reference, url: "https://example.com/note"}, {kind: book, title: Reading}, {kind: article, url: "https://example.com"}, {kind: video}, {kind: ai}, {kind: other}]'):
            with self.subTest(sources=sources), TemporaryDirectory() as tmp:
                result, _ = self.build(Path(tmp), 'sources: ' + sources + '\n')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_sources_fail(self):
        for value in ('book', '{}', '[book]', '[{}]', '[{kind: unknown}]', '[{kind: book, title: 42}]', '[{kind: ai, url: []}]', '[{kind: note, title: ""}]'):
            with self.subTest(value=value), TemporaryDirectory() as tmp:
                result, _ = self.build(Path(tmp), 'sources: ' + value + '\n')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('sources', result.stdout + result.stderr)

    def test_private_source_paths_are_rejected(self):
        for kind in ('note', 'other'):
            with self.subTest(kind=kind), TemporaryDirectory() as tmp:
                result, _ = self.build(Path(tmp),
                    'sources: [{kind: ' + kind + ', path: notes/2025-03-01-01.md}]\n')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('sources.path belongs in the private sanctum-notebook', result.stdout + result.stderr)

    def test_private_notes_are_rejected_even_when_unpublished(self):
        for metadata in ('', 'draft: true\n', 'publishDate: 2999-01-01\n'):
            with self.subTest(metadata=metadata), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.build(root)
                notes = root / 'content/notes'
                notes.mkdir()
                (notes / '2025-03-01-01.md').write_text(
                    '---\ntitle: Private thought\ndate: 2025-03-01\n' + metadata + '---\nPrivate body.\n')
                result, _ = build_site(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Keep private notes in sanctum-notebook/notes/', result.stdout + result.stderr)

    def test_no_note_pages_feeds_or_navigation_are_generated(self):
        with TemporaryDirectory() as tmp:
            result, output = self.build(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((output / 'notes').exists())
            for path in output.rglob('*'):
                if path.suffix in ('.html', '.xml'):
                    self.assertNotIn('/notes/', path.read_text(), str(path.relative_to(output)))
