"""Exercise navigation, new configured sections and derived categories through Hugo."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET

from check_site import Document

ROOT = Path(__file__).resolve().parents[1]


class SectionTest(unittest.TestCase):
    def build(self, root, metadata='', section='fieldwork'):
        content = root / 'content'
        (content / section).mkdir(parents=True)
        # Exercise the actual production generator when it exists.
        adapter = ROOT / 'content/_content.gotmpl'
        if adapter.is_file():
            shutil.copyfile(adapter, content / adapter.name)
        (content / 'archive.md').write_text('---\ntitle: Archive\nlayout: archive\n---\n')
        (content / 'updates.md').write_text('---\ntitle: Updates\nlayout: updates\n---\n')
        (content / section / 'entry.md').write_text('---\ntitle: Field journal\ndate: 2025-03-01\nlastmod: 2026-01-01\nstatus: note\ntags: [观察]\n' + metadata + '---\n\n## Observations\n\nOne entry.\n')
        data = root / 'data'
        shutil.copytree(ROOT / 'data', data)
        with (data / 'sections.yaml').open('a') as file:
            file.write('\n- slug: fieldwork\n  name: Fieldwork\n  chinese: 田野\n  description: New configured section.\n  kind: articles\n')
        override = root / 'override.toml'
        override.write_text(f'dataDir = "{data}"\n')
        output = root / 'public'
        result = subprocess.run([os.environ.get('HUGO_BIN', str(ROOT / '.tools/bin/hugo')),
                                 '--source', str(ROOT), '--config', f'{ROOT / "hugo.toml"},{override}',
                                 '--contentDir', str(content), '--destination', str(output),
                                 '--baseURL', 'https://example.com/sanctum/'],capture_output=True,text=True)
        return result, output

    def test_new_section_is_indexed_without_a_category_field(self):
        with TemporaryDirectory(prefix='sanctum-section-') as tmp:
            result, output = self.build(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in ('index.html', 'archive/index.html', 'updates/index.html'):
                self.assertTrue('Field journal' in (output / path).read_text(), path)
            article = Document((output / 'fieldwork/entry/index.html').read_text())
            self.assertTrue(any(s.get('@type') == 'BlogPosting' for s in article.schemas))
            self.assertIn('/sanctum/categories/fieldwork/', article.links)
            self.assertIn('Field journal', (output / 'categories/fieldwork/index.html').read_text())
            categories = Document((output / 'categories/index.html').read_text())
            self.assertIn('/sanctum/categories/fieldwork/', categories.links)
            self.assertNotIn('/sanctum/categories/now/', categories.links)
            section = (output / 'fieldwork/index.html').read_text()
            self.assertIn('田野', section)
            rss = ET.fromstring((output / 'index.xml').read_text())
            items = rss.findall('./channel/item')
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].findtext('category'), 'fieldwork')
            self.assertEqual(items[0].findtext('link'), 'https://example.com/sanctum/fieldwork/entry/')
            category_rss = ET.fromstring((output / 'categories/fieldwork/index.xml').read_text())
            self.assertEqual(category_rss.find('./channel/item/title').text, 'Field journal')

    def test_conflicting_legacy_category_blocks_build(self):
        with TemporaryDirectory(prefix='sanctum-category-conflict-') as tmp:
            result, _ = self.build(Path(tmp), 'categories: [notes]\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('categories must match section fieldwork', result.stdout + result.stderr)

    def test_matching_legacy_category_remains_compatible(self):
        with TemporaryDirectory(prefix='sanctum-category-legacy-') as tmp:
            result, output = self.build(Path(tmp), 'categories: [fieldwork]\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            rss = ET.fromstring((output / 'index.xml').read_text())
            self.assertEqual([item.text for item in rss.findall('./channel/item/category')], ['fieldwork'])

    def test_empty_legacy_category_cannot_disable_the_derived_category(self):
        with TemporaryDirectory(prefix='sanctum-empty-category-') as tmp:
            result, _ = self.build(Path(tmp), 'categories: []\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('categories must match section fieldwork', result.stdout + result.stderr)

    def test_unconfigured_section_cannot_disappear_silently(self):
        with TemporaryDirectory(prefix='sanctum-unconfigured-') as tmp:
            result, _ = self.build(Path(tmp), section='unregistered')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Register section unregistered in data/sections.yaml', result.stdout + result.stderr)

    def test_global_navigation_is_in_one_place(self):
        with TemporaryDirectory(prefix='sanctum-navigation-') as tmp:
            result, output = self.build(Path(tmp), section='notes')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in ('index.html', 'notes/entry/index.html', 'archive/index.html'):
                html = (output / path).read_text()
                header = Document(html.split('<header class="site-header">', 1)[1].split('</header>', 1)[0])
                for route in ('updates/', 'archive/', 'tags/', 'about/'):
                    self.assertIn('/sanctum/' + route, header.links, path)
                footer = Document(html.split('<footer class="site-footer">', 1)[1].split('</footer>', 1)[0])
                for route in ('updates/', 'archive/', 'tags/', 'about/'):
                    self.assertNotIn('/sanctum/' + route, footer.links, path)


if __name__ == '__main__':
    unittest.main()
