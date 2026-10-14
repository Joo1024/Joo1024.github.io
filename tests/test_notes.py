"""Notes and unified sources use the real Hugo validation templates."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from hugo_helpers import create_content, build_site


class NotesTest(unittest.TestCase):
    def build(self, root, metadata='', filename='2025-03-01-01.md'):
        content = create_content(root)
        (content / 'notes').mkdir()
        note = content / 'notes' / filename
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text('---\ntitle: Unique note title\ndate: 2025-03-01\n' + metadata + '---\nNote body.\n')
        return build_site(root)

    def test_notes_render_without_entering_post_timelines(self):
        with TemporaryDirectory() as tmp:
            result, output = self.build(Path(tmp), 'domains: [mind]\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = (output / 'notes/2025-03-01-01/index.html').read_text()
            self.assertIn('href="/sanctum/notes/" aria-current="location"', html)
            self.assertIn('Note body.', (output / 'notes/2025-03-01-01/index.html').read_text())
            self.assertIn('Unique note title', (output / 'notes/index.html').read_text())
            for path in ('index.html', 'archive/index.html', 'posts/index.html', 'index.xml'):
                self.assertNotIn('Unique note title', (output / path).read_text(), path)

    def test_sources_are_supported_in_both_collections(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result, _ = self.build(root, 'sources: [{kind: book, title: Reading}, {kind: article, url: "https://example.com"}, {kind: video}, {kind: ai}, {kind: other}]\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (root / 'content/posts').mkdir()
            (root / 'content/posts/entry.md').write_text('---\ntitle: Post\ndate: 2025-03-02\nform: brief\nsources: [{kind: note, path: notes/2025-03-01-01.md}]\n---\nPost.\n')
            result, _ = build_site(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_sources_fail(self):
        for value in ('book', '{}', '[book]', '[{}]', '[{kind: unknown}]', '[{kind: book, title: 42}]', '[{kind: ai, url: []}]', '[{kind: note}]', '[{kind: note, path: notes/2025-03-01-02.md}]', '[{kind: note, path: "../notes/2025-03-01-01.md"}]'):
            with self.subTest(value=value), TemporaryDirectory() as tmp:
                result, _ = self.build(Path(tmp), 'sources: ' + value + '\n')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('sources', result.stdout + result.stderr)

    def test_note_sources_can_reference_other_notes(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build(root)
            (root / 'content/notes/2025-03-01-02.md').write_text('---\ntitle: Followup\ndate: 2025-03-01\nsources: [{kind: note, path: notes/2025-03-01-01.md}]\n---\nBody.\n')
            result, _ = build_site(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unpublished_notes_are_valid_source_files(self):
        for metadata in ('draft: true', 'publishDate: 2999-01-01'):
            with self.subTest(metadata=metadata), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.build(root, metadata + '\n')
                (root / 'content/posts').mkdir()
                (root / 'content/posts/entry.md').write_text('---\ntitle: Post\ndate: 2025-03-02\nsources: [{kind: note, path: notes/2025-03-01-01.md}]\n---\nPost.\n')
                result, _ = build_site(root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_notes_do_not_use_post_form(self):
        with TemporaryDirectory() as tmp:
            result, _ = self.build(Path(tmp), 'form: reflection\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Notes do not use form', result.stdout + result.stderr)

    def test_invalid_note_names_and_required_fields(self):
        for filename in ('entry.md', '2025-03-01-00.md', 'nested/2025-03-01-01.md', '2025-99-99-01.md', '2025-02-30-01.md'):
            with self.subTest(filename=filename), TemporaryDirectory() as tmp:
                result, _ = self.build(Path(tmp), filename=filename)
                self.assertNotEqual(result.returncode, 0)
        for field in ('title', 'date'):
            with self.subTest(field=field), TemporaryDirectory() as tmp:
                root = Path(tmp)
                self.build(root)
                note = root / 'content/notes/2025-03-01-01.md'
                note.write_text('\n'.join(line for line in note.read_text().splitlines() if not line.startswith(field + ':')))
                result, _ = build_site(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Missing original ' + field, result.stdout + result.stderr)
