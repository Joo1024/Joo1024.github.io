#!/usr/bin/env python3
"""Check the actual generated site, local URLs/anchors and publishing features."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import json
import sys
import xml.etree.ElementTree as ET


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.links = []
        self.ids = set()
        self.duplicate_ids = []
        self.images = []
        self.meta = {}
        self.schemas = []
        self.json_script = False
        self.json_text = ''
        self.section_links = []
        self.in_sections = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'nav' and 'home-sections' in attrs.get('class', '').split():
            self.in_sections = True
        if tag == 'a' and self.in_sections and 'href' in attrs:
            self.section_links.append(attrs['href'])
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.duplicate_ids.append(attrs['id'])
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'meta' and 'name' in attrs:
            self.meta[attrs['name']] = attrs.get('content')
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.json_script = True
            self.json_text = ''

    def handle_data(self, data):
        if self.json_script:
            self.json_text += data

    def handle_endtag(self, tag):
        if tag == 'nav':
            self.in_sections = False
        if tag == 'script' and self.json_script:
            self.schemas.append(json.loads(self.json_text))
            self.json_script = False


def check(root, base, examples=False):
    problems = []
    def require(condition, message):
        if not condition:
            problems.append(message)
    def read(route):
        path = root / route
        require(path.is_file(), f'Missing generated page: {route}')
        return path.read_text() if path.is_file() else ''
    def parse_xml(route, text):
        if text:
            try:
                return ET.fromstring(text)
            except ET.ParseError as exc:
                problems.append(f'Invalid {route}: {exc}')
    home = read('index.html')
    home_document = Document(home)
    require('Sanctum' in home, 'Home must identify Sanctum')
    section_links = home_document.section_links
    require(bool(section_links), 'Home must expose the configured sections')
    for link in section_links:
        route = unquote(urlsplit(link).path)
        require(route.startswith(base), f'Section escapes base path: {link}')
        if route.startswith(base):
            read(route[len(base):].rstrip('/') + '/index.html')
    for route in ('archive/index.html', 'updates/index.html', 'tags/index.html', 'categories/index.html', '404.html'):
        read(route)
    archive = read('archive/index.html')
    if examples:
        require('year-2025' in archive and 'year-2026' in archive, 'Archive must group original years')
        article = read('reflection/on-keeping-a-place/index.html')
        for marker in ('TableOfContents', 'footnotes', 'later-notes', 'datePublished', 'dateModified', 'post-navigation', 'reflection', '2025-11-16', '2026-09-20'):
            require(marker in article, f'Article must provide {marker}')
        require('2026-09-20' in read('updates/index.html'), 'Updates must show last modification date')
        practice = read('practice/small-repetitions/index.html')
        require('highlight' in practice and '<pre' in practice and '<blockquote' in practice, 'Markdown code and quote must render')
        journey = read('journey/before-the-ridge/index.html')
        require(any(i.get('loading') == 'lazy' for i in Document(journey).images), 'Journey images must be lazy loaded')
    require('canonical' in home and bool(home_document.meta.get('description')), 'SEO metadata must be present')
    rss = read('index.xml')
    rss_xml = parse_xml('index.xml', rss)
    parse_xml('sitemap.xml', read('sitemap.xml'))
    if examples:
        require('后记' in rss and 'on-keeping-a-place' in rss, 'RSS must include article content and later notes')
    documents = {p: Document(p.read_text()) for p in root.rglob('*.html')}
    articles = [s for d in documents.values() for s in d.schemas if s.get('@type') == 'BlogPosting']
    if rss_xml is not None:
        feed_items = rss_xml.findall('./channel/item')
        require(len(feed_items) == len(articles), 'RSS must include every published article exactly once')
        for schema in articles:
            require(schema.get('datePublished') <= schema.get('dateModified'), 'Article modification must not predate publication')
            year = schema.get('datePublished', '')[:4]
            require(f'year-{year}' in archive, f'Archive must retain original publication year {year}')
            require(any(item.findtext('link') == schema.get('mainEntityOfPage') for item in feed_items), 'Article missing from RSS')
    for path, document in documents.items():
        require(not document.duplicate_ids, f'Duplicate anchors: {path.relative_to(root)} {document.duplicate_ids}')
        require('cdn.jsdelivr.net' not in document.text, f'Runtime CDN dependency in {path.relative_to(root)}')
        for img in document.images:
            require(bool(img.get('alt')), f'Missing image alt text: {path.relative_to(root)}')
            require(img.get('loading') == 'lazy', f'Image missing lazy loading: {path.relative_to(root)}')
        for link in document.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path and not url.fragment:
                continue
            raw = unquote(url.path)
            if raw.startswith('/'):
                require(raw.startswith(base), f'Link escapes base path: {link}')
                if not raw.startswith(base):
                    continue
                target = root / raw[len(base):]
            else:
                target = path.parent / raw if raw else path
            if target.is_dir():
                target /= 'index.html'
            target = target.resolve()
            require(target.is_file(), f'Broken local link: {path.relative_to(root)} → {link}')
            if url.fragment and target.suffix == '.html' and target.is_file():
                linked = documents.get(target) or Document(target.read_text())
                require(unquote(url.fragment) in linked.ids, f'Broken anchor: {path.relative_to(root)} → {link}')
    if problems:
        print('\n'.join(f'FAIL {p}' for p in problems), file=sys.stderr)
        return 1
    print(f'PASS {len(documents)} HTML pages, {len(articles)} articles, {len(section_links)} configured sections; local links/anchors, dates/archive, RSS, sitemap, lazy images, SEO' + ('; example Markdown/TOC/footnotes/later notes' if examples else ''))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default='public')
    parser.add_argument('--base-path', default='/')
    parser.add_argument('--examples', action='store_true', help='Also validate the removable example articles')
    args = parser.parse_args()
    sys.exit(check(Path(args.root).resolve(), args.base_path, args.examples))
