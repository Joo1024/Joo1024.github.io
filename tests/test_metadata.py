"""Exercise flat Markdown, native multidimensional indices and old feed URLs."""
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import shutil
import unittest
import xml.etree.ElementTree as ET

from check_site import Document, check
from hugo_helpers import ROOT, BASE, build_site, create_content


class MetadataTest(unittest.TestCase):
    def build(self, root, metadata='', directory='posts', articles=True):
        content = create_content(root)
        (content / 'now.md').write_text('---\ntitle: Now\nlastmod: 2025-01-01\n---\nLiving page.\n')
        if articles:
            section = content / directory
            section.mkdir(parents=True, exist_ok=True)
            (section / 'entry.md').write_text('---\ntitle: Field journal\ndate: 2025-03-01\n' + metadata + '---\n\n## Observations\n\nOne entry.\n')
        return build_site(root)

    def html(self, output, route):
        return (output / unquote(route).removeprefix('/sanctum/').strip('/') / 'index.html').read_text()

    def test_cross_domain_article_has_all_four_native_indices_and_feeds(self):
        with TemporaryDirectory(prefix='sanctum-dimensions-') as tmp:
            result, output = self.build(Path(tmp), 'type: practice\ndomains: [mind, body]\npaths: [明心, 精进]\ntags: [AI, 倒立]\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            article = Document((output / 'posts/entry/index.html').read_text())
            for route in ('/sanctum/types/practice/', '/sanctum/domains/mind/', '/sanctum/domains/body/'):
                self.assertIn(route, article.links)
                self.assertIn('Field journal', self.html(output, route))
            for key in ('paths', 'tags'):
                prefix = '/sanctum/' + key + '/'
                links = [link for link in article.links if link.startswith(prefix) and link != prefix]
                self.assertEqual(len(links), 2)
                for route in links:
                    self.assertIn('Field journal', self.html(output, route))
                    path = output / unquote(urlsplit(route).path).removeprefix('/sanctum/') / 'index.xml'
                    feed = ET.fromstring(path.read_text())
                    self.assertEqual([item.findtext('title') for item in feed.findall('./channel/item')], ['Field journal'])
            hub = Document((output / 'tags/index.html').read_text())
            for anchor in ('dimension-type', 'dimension-domains', 'dimension-paths', 'dimension-tags'):
                self.assertIn(anchor, hub.ids)
            for path in ('index.html', 'archive/index.html', 'updates/index.html'):
                self.assertIn('Field journal', (output / path).read_text())
            rss = ET.fromstring((output / 'index.xml').read_text())
            self.assertEqual(len(rss.findall('./channel/item')), 1)
            self.assertEqual(rss.findtext('./channel/item/link'), BASE + 'posts/entry/')
            self.assertEqual(len(rss.findall('./channel/item/category')), 7)
            self.assertNotIn('Living page', (output / 'index.xml').read_text())

    def test_only_title_and_date_are_required(self):
        with TemporaryDirectory(prefix='sanctum-minimum-') as tmp:
            result, output = self.build(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in ('index.html', 'archive/index.html', 'updates/index.html', 'index.xml'):
                self.assertIn('Field journal', (output / path).read_text())
            self.assertFalse((output / 'types/posts/index.html').exists(), 'The folder is not an automatic form')
            hub = Document((output / 'tags/index.html').read_text())
            self.assertNotIn('dimension-type', hub.ids)
            self.assertNotIn('dimension-domains', hub.ids)

    def test_unregistered_vocabulary_and_empty_arrays_are_supported(self):
        with TemporaryDirectory(prefix='sanctum-vocabulary-') as tmp:
            result, output = self.build(Path(tmp), 'type: letter\ndomains: [friendship]\npaths: [闲游]\ntags: []\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            article = Document((output / 'posts/entry/index.html').read_text())
            self.assertIn('/sanctum/types/letter/', article.links)
            self.assertIn('/sanctum/domains/friendship/', article.links)
            self.assertNotIn('dimension-tags', Document((output / 'tags/index.html').read_text()).ids)

    def test_array_fields_cannot_be_mistyped_as_scalar_strings(self):
        for field in ('domains', 'paths', 'tags'):
            with self.subTest(field=field), TemporaryDirectory(prefix='sanctum-invalid-metadata-') as tmp:
                result, _ = self.build(Path(tmp), field + ': mind\n')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field + ' must be a flat array of nonempty strings', result.stdout + result.stderr)

    def test_dates_and_optional_status_remain_validated(self):
        with TemporaryDirectory(prefix='sanctum-invalid-status-') as tmp:
            result, _ = self.build(Path(tmp), 'status: level-9\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Invalid status', result.stdout + result.stderr)
        with TemporaryDirectory(prefix='sanctum-invalid-lastmod-') as tmp:
            result, _ = self.build(Path(tmp), 'lastmod: 2024-01-01\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('lastmod predates date', result.stdout + result.stderr)

    def test_metadata_validation_cannot_be_bypassed_with_another_layout(self):
        cases = (
            ('layout: archive\nstatus: level-9\n', 'Invalid status'),
            ('layout: list\nlastmod: 2024-01-01\n', 'lastmod predates date'),
        )
        for metadata, message in cases:
            with self.subTest(metadata=metadata), TemporaryDirectory(prefix='sanctum-layout-validation-') as tmp:
                result, _ = self.build(Path(tmp), metadata)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stdout + result.stderr)

    def test_site_checker_reports_invalid_feed_without_crashing(self):
        with TemporaryDirectory(prefix='sanctum-invalid-feed-') as tmp:
            result, output = self.build(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            (output / 'index.xml').write_text('<rss><channel>')
            errors = StringIO()
            with redirect_stderr(errors), redirect_stdout(StringIO()):
                status = check(output, '/sanctum/')
            self.assertEqual(status, 1)
            self.assertIn('Invalid index.xml:', errors.getvalue())

    def test_original_date_and_title_cannot_be_omitted(self):
        for field in ('title', 'date'):
            with self.subTest(field=field), TemporaryDirectory(prefix='sanctum-missing-field-') as tmp:
                root = Path(tmp)
                result, output = self.build(root)
                article = root / 'content/posts/entry.md'
                lines = [line for line in article.read_text().splitlines() if not line.startswith(field + ':')]
                article.write_text('\n'.join(lines) + '\n')
                result, _ = build_site(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Missing original ' + field, result.stdout + result.stderr)

    def test_old_article_url_guid_and_old_section_feeds_remain_valid(self):
        with TemporaryDirectory(prefix='sanctum-old-url-') as tmp:
            result, output = self.build(Path(tmp), 'url: /practice/entry/\ntype: practice\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((output / 'practice/entry/index.html').is_file())
            for path in ('index.xml', 'practice/index.xml', 'categories/practice/index.xml', 'types/practice/index.xml'):
                rss = ET.fromstring((output / path).read_text())
                self.assertEqual(rss.findtext('./channel/item/guid'), BASE + 'practice/entry/', path)
                self.assertIn('2025', rss.findtext('./channel/item/pubDate'), path)
            for path in ('practice/index.html', 'categories/practice/index.html'):
                self.assertIn(BASE + 'types/practice/', (output / path).read_text())

    def test_empty_legacy_targets_fall_back_and_do_not_enter_sitemap(self):
        with TemporaryDirectory(prefix='sanctum-empty-') as tmp:
            result, output = self.build(Path(tmp), articles=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in ('practice/index.html', 'categories/practice/index.html'):
                self.assertIn(BASE + 'types/', (output / path).read_text())
            for path in ('index.xml', 'practice/index.xml', 'categories/practice/index.xml'):
                self.assertFalse(ET.fromstring((output / path).read_text()).findall('./channel/item'))
            sitemap = ET.fromstring((output / 'sitemap.xml').read_text())
            urls = [node.text for node in sitemap.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            self.assertNotIn(BASE + 'practice/', urls)
            self.assertNotIn(BASE + 'categories/practice/', urls)

    def test_fixed_pages_survive_deleting_all_sample_articles(self):
        with TemporaryDirectory(prefix='sanctum-delete-samples-') as tmp:
            root = Path(tmp)
            _, output = self.build(root, articles=False)
            for name in ('now.md', 'path.md', 'about.md'):
                shutil.copyfile(ROOT / 'content' / name, root / 'content' / name)
            result, _ = build_site(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for route in ('now', 'path', 'about', 'posts'):
                self.assertTrue((output / route / 'index.html').is_file())
            self.assertFalse(ET.fromstring((output / 'index.xml').read_text()).findall('./channel/item'))

    def test_drafts_and_future_articles_are_not_published(self):
        for metadata in ('draft: true\n', 'publishDate: 2999-01-01\n'):
            with self.subTest(metadata=metadata), TemporaryDirectory(prefix='sanctum-unpublished-') as tmp:
                result, output = self.build(Path(tmp), metadata)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse((output / 'posts/entry/index.html').exists())
                self.assertFalse(ET.fromstring((output / 'index.xml').read_text()).findall('./channel/item'))

    def test_articles_outside_the_flat_directory_fail_clearly(self):
        for directory in ('', 'unregistered', 'posts/nested'):
            with self.subTest(directory=directory), TemporaryDirectory(prefix='sanctum-flat-') as tmp:
                result, _ = self.build(Path(tmp), directory=directory)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Put articles directly in content/posts/', result.stdout + result.stderr)

    def test_global_navigation_stays_in_header(self):
        with TemporaryDirectory(prefix='sanctum-navigation-') as tmp:
            result, output = self.build(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for path in ('index.html', 'posts/entry/index.html', 'archive/index.html'):
                html = (output / path).read_text()
                header = Document(html.split('<header class="site-header">', 1)[1].split('</header>', 1)[0])
                footer = Document(html.split('<footer class="site-footer">', 1)[1].split('</footer>', 1)[0])
                for route in ('updates/', 'archive/', 'tags/', 'about/'):
                    self.assertIn('/sanctum/' + route, header.links)
                    self.assertNotIn('/sanctum/' + route, footer.links)


if __name__ == '__main__':
    unittest.main()
