"""Build real pages to verify the state/time navigation and publishing boundary."""
from html.parser import HTMLParser
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote
import shutil
import unittest
import xml.etree.ElementTree as ET

from check_site import Document, check
from hugo_helpers import ROOT, BASE, build_site, create_content


class Navigation(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.groups = {}
        self.group = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav':
            self.group = attrs.get('class')
            if self.group:
                self.groups[self.group] = []
        if tag == 'a' and self.group:
            self.groups[self.group].append(attrs)

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.group = None


class NavigationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = TemporaryDirectory(prefix='sanctum-navigation-')
        cls.root = Path(cls.tmp.name)
        content = create_content(cls.root)
        for name in ('now', 'path', 'about', 'cultivation', 'roots', 'realms'):
            source = ROOT / 'content' / (name + '.md')
            if source.exists():
                shutil.copyfile(source, content / source.name)
        cls.now_intro = 'A unique current practice from Now.'
        (content / 'now.md').write_text('---\ntitle: Now\nchinese: 今朝\nlastmod: 2025-04-02\n---\n' + cls.now_intro + '\n\n## SECTION_HEADING_NOT_SUMMARY\n\nA second current practice.\n')
        posts = content / 'posts'
        posts.mkdir()
        for n in range(1, 7):
            (posts / f'entry{n}.md').write_text(
                f'---\ntitle: Entry {n}\ndate: 2025-01-0{n}\n'
                'form: reflection\ndomains: [mind]\npaths: [明心]\ntags: [练习]\n'
                '---\nArticle body.\n')
        cls.result, cls.output = build_site(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def html(self, route):
        self.assertEqual(self.result.returncode, 0, self.result.stdout + self.result.stderr)
        file = self.output / unquote(route).strip('/') / 'index.html'
        self.assertTrue(file.is_file(), f'Missing page: {route}')
        return file.read_text()

    def test_primary_and_secondary_navigation_follow_the_current_region(self):
        cases = {
            'cultivation': ('cultivation', None),
            'now': ('cultivation', 'now'), 'path': ('cultivation', 'path'),
            'realms': ('cultivation', 'realms'), 'roots': ('cultivation', 'roots'),
            'posts': ('posts', 'posts'), 'posts/entry6': ('posts', 'posts'),
            'archive': ('posts', 'archive'), 'updates': ('posts', 'updates'),
            'tags': ('posts', 'tags'), 'forms/reflection': ('posts', 'tags'),
            'domains/mind': ('posts', 'tags'), 'paths/明心': ('posts', 'tags'),
            'tags/练习': ('posts', 'tags'), 'about': ('about', None),
            '': (None, None),
        }
        for route, (primary, secondary) in cases.items():
            with self.subTest(route=route):
                nav = Navigation(self.html(route)).groups
                self.assertEqual([a['href'] for a in nav['utility-nav']],
                                 ['/sanctum/cultivation/', '/sanctum/posts/', '/sanctum/about/'])
                active = [a['href'] for a in nav['utility-nav'] if a.get('aria-current')]
                self.assertEqual(active, [f'/sanctum/{primary}/'] if primary else [])
                if primary == 'cultivation':
                    expected = ['now', 'path', 'realms', 'roots']
                elif primary == 'posts':
                    expected = ['posts', 'archive', 'tags', 'updates']
                else:
                    self.assertNotIn('section-nav', nav)
                    continue
                self.assertEqual([a['href'] for a in nav['section-nav']],
                                 [f'/sanctum/{slug}/' for slug in expected])
                self.assertEqual([a['href'] for a in nav['section-nav'] if a.get('aria-current')],
                                 [f'/sanctum/{secondary}/'] if secondary else [])

    def test_home_reads_now_and_shows_only_the_five_latest_articles(self):
        html = self.html('')
        self.assertIn(self.now_intro, html)
        self.assertNotIn('home-sections', html)
        recent = html.split('id="recent-heading"', 1)[1].split('</section>', 1)[0]
        links = Document(recent).links
        self.assertEqual([link for link in links if '/posts/entry' in link],
                         [f'/sanctum/posts/entry{n}/' for n in (6, 5, 4, 3, 2)])
        self.assertIn('/sanctum/now/', Document(html).links)
        self.assertIn('/sanctum/cultivation/', Document(html).links)
        self.assertIn('/sanctum/posts/', Document(html).links)

    def test_home_summary_excerpts_paragraphs_without_section_headings(self):
        html = self.html('')
        summary = html.split('class="home-now-summary"', 1)[1].split('</p>', 1)[0]
        self.assertIn(self.now_intro, summary)
        self.assertIn('A second current practice.', summary)
        self.assertNotIn('SECTION_HEADING_NOT_SUMMARY', summary)

    def test_overview_describes_methods_and_attainment_with_actual_page_dates(self):
        html = self.html('cultivation')
        main = html.split('<main', 1)[1].split('</main>', 1)[0]
        self.assertIn('功法', main)
        self.assertIn('修为', main)
        self.assertIn('2025.04.02', main)
        for name in ('now', 'path', 'realms', 'roots'):
            self.assertIn(f'/sanctum/{name}/', Document(main).links)

    def test_archive_keeps_years_without_a_second_classification_menu(self):
        html = self.html('archive')
        self.assertNotIn('archive-nav', html)
        self.assertIn('year-2025', Document(html).ids)
        for n in range(1, 7):
            self.assertIn(f'/sanctum/posts/entry{n}/', Document(html).links)

    def test_fixed_pages_are_in_updates_and_sitemap_but_not_article_feeds(self):
        updates = Document(self.html('updates')).links
        sitemap = (self.output / 'sitemap.xml').read_text()
        for name in ('now', 'path', 'realms', 'roots'):
            self.assertIn(f'/sanctum/{name}/', updates)
            self.assertIn(BASE + name + '/', sitemap)
        for route in ('index.xml', 'posts/index.xml', 'forms/reflection/index.xml'):
            items = ET.parse(self.output / route).getroot().findall('./channel/item')
            self.assertEqual(len(items), 6)
            self.assertTrue(all('/posts/entry' in item.findtext('link') for item in items))

    def test_generated_site_has_no_broken_links_under_a_base_path(self):
        errors = StringIO()
        with redirect_stderr(errors), redirect_stdout(StringIO()):
            status = check(self.output, '/sanctum/')
        self.assertEqual(status, 0, errors.getvalue())


if __name__ == '__main__':
    unittest.main()
