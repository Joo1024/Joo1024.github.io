#!/usr/bin/env python3
"""Optional first-edition browser tests (requires Playwright + Chromium).

Build and serve public/ first, then:
python3 tests/browser_smoke.py --url http://127.0.0.1:8001 --chromium /usr/bin/chromium
Pass --screenshots /tmp/sanctum-shots to save reference images.
This developer check exercises the initial example content; CI uses the
content-independent standard-library check_site.py instead.
"""
import argparse
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright


def run(base, chromium, screenshots):
    base = base.rstrip('/')
    failures = []
    external = []
    with sync_playwright() as p:
        options = {'headless': True, 'args': ['--no-sandbox']}
        if chromium:
            options['executable_path'] = chromium
        browser = p.chromium.launch(**options)
        context = browser.new_context(viewport={'width': 1440, 'height': 1100}, color_scheme='light')
        context.on('page', lambda page: page.on('pageerror', lambda error: failures.append(str(error))))
        page = context.new_page()
        page.on('request', lambda request: external.append(request.url)
                if urlsplit(request.url).netloc != urlsplit(base).netloc else None)
        page.goto(base + '/', wait_until='networkidle')
        assert page.title() == 'Sanctum'
        assert page.locator('.home-sections > a').count() == 9
        assert page.locator('.recent-section .entry-list > li').count() == 4
        assert page.locator('#theme-toggle').inner_text() == '配色 · 系统'
        if screenshots:
            page.screenshot(path=str(screenshots / 'home-light.png'), full_page=True)
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme') == 'light'
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme') == 'dark'
        assert page.evaluate('getComputedStyle(document.body).backgroundColor') == 'rgb(32, 37, 35)'
        page.reload()
        assert page.locator('html').get_attribute('data-theme') == 'dark'
        if screenshots:
            page.screenshot(path=str(screenshots / 'home-dark.png'), full_page=True)
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme') is None
        page.emulate_media(color_scheme='dark')
        assert page.evaluate('getComputedStyle(document.body).backgroundColor') == 'rgb(32, 37, 35)'
        page.emulate_media(color_scheme='light')
        print('PASS theme cycle, persistence, system dark preference')

        page.goto(base + '/reflection/on-keeping-a-place/')
        assert page.locator('h1').inner_text() == '给未完成的自己，留一处地方'
        assert '发布于 2025.11.16' in page.locator('.article-meta').inner_text()
        assert '更新于 2026.09.20' in page.locator('.article-meta').inner_text()
        assert page.locator('#later-notes').count() == 1
        page.locator('.article-toc > summary').click()
        page.locator('#TableOfContents a').first.click()
        assert urlsplit(page.url).fragment
        page.locator('.footnote-ref').click()
        assert page.locator('.footnotes').count() == 1
        page.locator('.post-navigation a').click()
        assert page.url.endswith('/reflection/enough-for-a-day/')
        page.locator('.article-taxonomy a', has_text='#生活').click()
        assert page.locator('.entry-list a', has_text='怎样算是好好度过了一天').count() == 1
        page.goto(base + '/practice/small-repetitions/')
        assert page.locator('.highlight pre').count() == 1
        assert page.locator('blockquote').count() == 1
        print('PASS article dates, later notes, TOC, footnotes, adjacent article, Chinese tag, code')

        for width in (320, 375, 768, 1440):
            page.set_viewport_size({'width': width, 'height': 900})
            for route in ('/', '/now/', '/path/', '/reflection/on-keeping-a-place/',
                          '/practice/small-repetitions/', '/journey/before-the-ridge/',
                          '/archive/', '/tags/', '/categories/', '/updates/'):
                response = page.goto(base + route)
                assert response.status == 200, route
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), (width, route)
            if width == 375 and screenshots:
                page.goto(base + '/')
                page.screenshot(path=str(screenshots / 'home-mobile.png'), full_page=True)
                page.goto(base + '/reflection/on-keeping-a-place/')
                page.screenshot(path=str(screenshots / 'article-mobile.png'), full_page=True)
        print('PASS 40 responsive route/viewport checks (320–1440px)')

        page.goto(base + '/?p=posts/hello.md')
        page.wait_for_url('**/notes/hello-world/')
        assert page.locator('.prose code').inner_text().strip() == 'console.log("hello");'
        print('PASS legacy Hello World direct link')
        context.close()

        offline = browser.new_context(java_script_enabled=False, color_scheme='dark')
        nojs = offline.new_page()
        nojs.goto(base + '/reflection/on-keeping-a-place/')
        assert nojs.locator('#later-notes').is_visible()
        assert nojs.locator('#theme-toggle').is_hidden()
        nojs.locator('.article-toc summary').click()
        assert nojs.locator('#TableOfContents').is_visible()
        assert nojs.locator('.post-navigation a').count() == 1
        print('PASS no-JS reading, TOC and navigation')
        offline.close()

        restricted = browser.new_context()
        restricted.add_init_script("Object.defineProperty(window, 'localStorage', { get() { throw new Error('Storage blocked'); } });")
        storage_page = restricted.new_page()
        storage_page.on('pageerror', lambda error: failures.append(str(error)))
        storage_page.goto(base + '/')
        storage_page.locator('#theme-toggle').click()
        assert storage_page.locator('html').get_attribute('data-theme') == 'light'
        print('PASS blocked localStorage fallback')
        restricted.close()
        browser.close()
    assert not failures, failures
    assert not external, external
    print('PASS no JavaScript errors or third-party requests')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8001')
    parser.add_argument('--chromium')
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)
    run(args.url, args.chromium, args.screenshots)
