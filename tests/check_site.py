#!/usr/bin/env python3
"""Check the actual generated site, local URLs/anchors and publishing features."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import sys
import xml.etree.ElementTree as ET


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.ids = set()
        self.images = []
        self.meta = {}
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'meta' and 'name' in attrs:
            self.meta[attrs['name']] = attrs.get('content')


def check(root, base):
    problems = []
    def require(condition, message):
        if not condition:
            problems.append(message)
    def read(route):
        path = root / route
        require(path.is_file(), f'Missing generated page: {route}')
        return path.read_text() if path.is_file() else ''
    home = read('index.html')
    require('Sanctum' in home, 'Home must identify Sanctum')
    for section in ('now', 'path', 'reflection', 'practice', 'making', 'reading', 'journey', 'notes', 'yearly'):
        read(f'{section}/index.html')
        require(f'{base}{section}/' in home, f'Home must link {section}')
    for route in ('archive/index.html', 'updates/index.html', 'tags/index.html', 'categories/index.html', '404.html'):
        read(route)
    archive = read('archive/index.html')
    require('year-2025' in archive and 'year-2026' in archive, 'Archive must group original years')
    article = read('reflection/on-keeping-a-place/index.html')
    for marker in ('TableOfContents', 'footnotes', 'later-notes', 'datePublished', 'dateModified', 'post-navigation', 'reflection', '2025-11-16', '2026-09-20'):
        require(marker in article, f'Article must provide {marker}')
    require('2026-09-20' in read('updates/index.html'), 'Updates must show last modification date')
    practice = read('practice/small-repetitions/index.html')
    require('highlight' in practice and '<pre' in practice and '<blockquote' in practice, 'Markdown code and quote must render')
    journey = read('journey/before-the-ridge/index.html')
    require(any(i.get('loading') == 'lazy' for i in Document(journey).images), 'Journey images must be lazy loaded')
    require('canonical' in home and bool(Document(home).meta.get('description')), 'SEO metadata must be present')
    for file in ('index.xml', 'sitemap.xml'):
        text = read(file)
        if text:
            try:
                ET.fromstring(text)
            except ET.ParseError as exc:
                problems.append(f'Invalid {file}: {exc}')
    rss = read('index.xml')
    require('后记' in rss and 'on-keeping-a-place' in rss, 'RSS must include article content and later notes')
    documents = {p: Document(p.read_text()) for p in root.rglob('*.html')}
    for path, document in documents.items():
        text = path.read_text()
        require('cdn.jsdelivr.net' not in text, f'Runtime CDN dependency in {path.relative_to(root)}')
        for img in document.images:
            require(bool(img.get('alt')), f'Missing image alt text: {path.relative_to(root)}')
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
    print(f'PASS {len(documents)} HTML pages; local links/anchors, nine sections, metadata, Markdown, later notes, archive, RSS, sitemap, lazy images, SEO')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', nargs='?', default='public')
    parser.add_argument('--base-path', default='/')
    args = parser.parse_args()
    sys.exit(check(Path(args.root).resolve(), args.base_path))
