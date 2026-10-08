"""Exercise flat Markdown, native multidimensional indices and post URLs."""
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
    def build(self, root, metadata='', directory='posts', articles=True, layout_dir=None):
        content = create_content(root)
        (content / 'now.md').write_text('---\ntitle: Now\nlastmod: 2025-01-01\n---\nLiving page.\n')
        if articles:
            section = content / directory
            section.mkdir(parents=True, exist_ok=True)
            (section / 'entry.md').write_text('---\ntitle: Field journal\ndate: 2025-03-01\n' + metadata + '---\n\n## Observations\n\nOne entry.\n')
        return build_site(root, layout_dir=layout_dir)

    def html(self, output, route):
        return (output / unquote(route).removeprefix('/sanctum/').strip('/') / 'index.html').read_text()

    def test_cross_domain_article_has_all_four_native_indices_and_feeds(self):
        with TemporaryDirectory(prefix='sanctum-dimensions-') as tmp:
            result, output = self.build(Path(tmp), 'form: practice\ndomains: [mind, body]\npaths: [明心, 精进]\ntags: [AI, 倒立]\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            article = Document((output / 'posts/entry/index.html').read_text())
            for route in ('/sanctum/forms/practice/', '/sanctum/domains/mind/', '/sanctum/domains/body/'):
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
            for anchor in ('dimension-form', 'dimension-domains', 'dimension-paths', 'dimension-tags'):
                self.assertIn(anchor, hub.ids)
            for path in ('index.html', 'archive/index.html'):
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
            for path in ('index.html', 'archive/index.html', 'index.xml'):
                self.assertIn('Field journal', (output / path).read_text())
            self.assertFalse((output / 'forms/posts/index.html').exists(), 'The folder is not an automatic form')
            hub = Document((output / 'tags/index.html').read_text())
            self.assertNotIn('dimension-form', hub.ids)
            self.assertNotIn('dimension-domains', hub.ids)

    def test_unregistered_vocabulary_and_empty_arrays_are_supported(self):
        with TemporaryDirectory(prefix='sanctum-vocabulary-') as tmp:
            result, output = self.build(Path(tmp), 'form: letter\ndomains: [friendship]\npaths: [闲游]\ntags: []\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            article = Document((output / 'posts/entry/index.html').read_text())
            self.assertIn('/sanctum/forms/letter/', article.links)
            self.assertIn('/sanctum/domains/friendship/', article.links)
            self.assertNotIn('dimension-tags', Document((output / 'tags/index.html').read_text()).ids)

    def test_array_fields_cannot_be_mistyped_as_scalar_strings(self):
        for field in ('domains', 'paths', 'tags'):
            with self.subTest(field=field), TemporaryDirectory(prefix='sanctum-invalid-metadata-') as tmp:
                result, _ = self.build(Path(tmp), field + ': mind\n')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(field + ' must be a flat array of nonempty strings', result.stdout + result.stderr)

    def test_form_must_be_one_nonempty_string(self):
        for value in ('[reflection]', '42', '" "'):
            with self.subTest(value=value), TemporaryDirectory(prefix='sanctum-invalid-form-') as tmp:
                result, _ = self.build(Path(tmp), 'form: ' + value + '\n')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('form must be a single nonempty string', result.stdout + result.stderr)

    def test_old_type_field_requires_explicit_migration(self):
        with TemporaryDirectory(prefix='sanctum-old-type-') as tmp:
            result, _ = self.build(Path(tmp), 'type: reflection\n')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('type is reserved by Hugo; use form for article format', result.stdout + result.stderr)

    def test_status_describes_state_instead_of_form(self):
        for status in ('note', 'reflection', 'false', '0', '[ongoing]'):
            with self.subTest(status=status), TemporaryDirectory(prefix='sanctum-old-status-') as tmp:
                result, _ = self.build(Path(tmp), 'form: reflection\nstatus: ' + status + '\n')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Invalid status', result.stdout + result.stderr)
        for status, label in (('ongoing', '持续中'), ('archived', '已归档')):
            with self.subTest(status=status), TemporaryDirectory(prefix='sanctum-valid-status-') as tmp:
                result, output = self.build(Path(tmp), 'form: reflection\nstatus: ' + status + '\n')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(label, (output / 'posts/entry/index.html').read_text())

    def test_form_does_not_select_hugo_content_templates(self):
        with TemporaryDirectory(prefix='sanctum-form-template-') as tmp:
            root = Path(tmp)
            layouts = root / 'layouts'
            shutil.copytree(ROOT / 'layouts', layouts)
            (layouts / 'reflection').mkdir()
            (layouts / 'reflection/single.html').write_text('{{ define "main" }}Wrong content type template{{ end }}')
            result, output = self.build(root, 'form: reflection\n', layout_dir=layouts)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            article = (output / 'posts/entry/index.html').read_text()
            self.assertIn('One entry.', article)
            self.assertNotIn('Wrong content type template', article)
            self.assertIn('/sanctum/forms/reflection/', Document(article).links)

    def test_obsolete_column_pages_and_feeds_are_not_generated(self):
        with TemporaryDirectory(prefix='sanctum-no-legacy-') as tmp:
            result, output = self.build(Path(tmp), 'form: practice\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((output / 'posts/entry/index.html').is_file())
            old_routes = ('reflection', 'practice', 'making', 'notes', 'reading', 'journey',
                          'yearly', 'categories', 'categories/practice', 'types', 'types/practice', 'updates')
            for route in old_routes:
                for filename in ('index.html', 'index.xml'):
                    self.assertFalse((output / route / filename).exists(), route + '/' + filename)

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

    def test_post_filename_defines_url_and_feed_guid(self):
        with TemporaryDirectory(prefix='sanctum-post-url-') as tmp:
            result, output = self.build(Path(tmp), 'form: practice\n')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((output / 'posts/entry/index.html').is_file())
            for path in ('index.xml', 'posts/index.xml', 'forms/practice/index.xml'):
                rss = ET.fromstring((output / path).read_text())
                self.assertEqual(rss.findtext('./channel/item/link'), BASE + 'posts/entry/', path)
                self.assertEqual(rss.findtext('./channel/item/guid'), BASE + 'posts/entry/', path)
                self.assertIn('2025', rss.findtext('./channel/item/pubDate'), path)

    def test_empty_site_has_valid_empty_indices_and_feeds(self):
        with TemporaryDirectory(prefix='sanctum-empty-') as tmp:
            result, output = self.build(Path(tmp), articles=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for route in ('posts', 'forms', 'domains', 'paths', 'tags', 'archive'):
                self.assertTrue((output / route / 'index.html').is_file(), route)
            for path in ('index.xml', 'posts/index.xml', 'forms/index.xml', 'domains/index.xml',
                         'paths/index.xml', 'tags/index.xml'):
                self.assertFalse(ET.fromstring((output / path).read_text()).findall('./channel/item'))

    def test_fixed_pages_are_independent_of_articles(self):
        with TemporaryDirectory(prefix='sanctum-fixed-pages-') as tmp:
            root = Path(tmp)
            _, output = self.build(root, articles=False)
            for name in ('now.md', 'path.md', 'realms.md', 'roots.md', 'about.md'):
                shutil.copyfile(ROOT / 'content' / name, root / 'content' / name)
            result, _ = build_site(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for route in ('now', 'path', 'realms', 'roots', 'about', 'cultivation', 'posts'):
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
                for route in ('cultivation/', 'posts/', 'about/'):
                    self.assertIn('/sanctum/' + route, header.links)
                    self.assertNotIn('/sanctum/' + route, footer.links)


if __name__ == '__main__':
    unittest.main()
