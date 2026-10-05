#!/usr/bin/env python3
"""Optional production browser tests (requires Playwright + Chromium).

Build and serve public/ first, then:
python3 tests/browser_smoke.py --url http://127.0.0.1:8001 --chromium /usr/bin/chromium
Pass --screenshots /tmp/sanctum-shots to save reference images.
This developer check exercises the current architecture and responsive layouts;
CI uses the content-independent standard-library check_site.py.
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
        page.goto(base + '/posts/', wait_until='networkidle')
        article_count = page.locator('.entry-list .entry-title').count()
        page.goto(base + '/', wait_until='networkidle')
        assert page.title() == 'Sanctum'
        assert page.locator('.utility-nav a').all_text_contents() == ['修行', '文字', '关于']
        assert page.locator('.home-now-summary').inner_text()
        assert page.locator('.home-links a').count() == 2
        assert page.locator('.home-sections').count() == 0
        assert page.locator('.recent-section .entry-title').count() == min(5, article_count)
        assert page.locator('#theme-toggle').inner_text() == '配色 · 系统'
        assert page.locator('.site-header #theme-toggle').count() == 0
        assert page.locator('.site-footer nav #theme-toggle').count() == 1
        if screenshots:
            page.screenshot(path=str(screenshots / 'home-light.png'), full_page=True)
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme') == 'light'
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme') == 'dark'
        assert page.evaluate('getComputedStyle(document.body).backgroundColor') == 'rgb(36, 36, 36)'
        page.reload()
        assert page.locator('html').get_attribute('data-theme') == 'dark'
        page.emulate_media(media='print', color_scheme='dark')
        assert page.evaluate('getComputedStyle(document.body).backgroundColor') == 'rgb(255, 255, 255)', 'Printing should use light paper even with explicit dark preference'
        page.emulate_media(media='screen', color_scheme='light')
        if screenshots:
            page.screenshot(path=str(screenshots / 'home-dark.png'), full_page=True)
        page.locator('#theme-toggle').click()
        assert page.locator('html').get_attribute('data-theme') is None
        page.emulate_media(color_scheme='dark')
        assert page.evaluate('getComputedStyle(document.body).backgroundColor') == 'rgb(36, 36, 36)'
        page.emulate_media(color_scheme='light')
        print('PASS theme cycle, persistence, system dark preference')

        page.goto(base + '/cultivation/')
        assert page.locator('.entry-list .entry-title').all_text_contents() == ['今朝', '道途', '境界', '灵根']
        assert page.locator('.entry-list time').count() == 4
        assert page.locator('.entry-list .entry-description, .entry-list .entry-meta').count() == 0
        assert page.locator('.cultivation-intro, .theory-links').count() == 0
        page.goto(base + '/path/')
        assert '功法' in page.locator('.article-heading .eyebrow').inner_text()
        page.goto(base + '/roots/')
        assert '此页尚待梳理' in page.locator('.prose').inner_text()
        assert page.locator('.theory-links a').count() == 1
        page.goto(base + '/realms/')
        assert '修为' in page.locator('.article-heading .eyebrow').inner_text()
        assert '当前修为尚待整理' in page.locator('.prose').inner_text()
        page.goto(base + '/archive/')
        assert page.locator('.archive-nav').count() == 0
        assert page.locator('.year-nav a').count() > 0
        page.goto(base + '/tags/')
        assert page.locator('.page-heading h1').inner_text().startswith('分类')
        page.goto(base + '/posts/cultivation-realms/')
        assert page.locator('.prose table').count() == 6
        page.locator('.article-toc > summary').click()
        page.locator('#TableOfContents a').first.click()
        assert urlsplit(page.url).fragment
        print('PASS cultivation overview, roles, templates, archive, classification, article tables and TOC')

        routes = ('/', '/cultivation/', '/now/', '/path/', '/realms/', '/roots/',
                  '/about/', '/posts/', '/posts/cultivation-realms/',
                  '/posts/cultivation-roots-and-methods/', '/archive/', '/tags/',
                  '/forms/', '/forms/reflection/', '/domains/', '/domains/mind/',
                  '/paths/', '/paths/明心/', '/updates/')
        for width in (320, 375, 768, 1440):
            page.set_viewport_size({'width': width, 'height': 900})
            for route in routes:
                response = page.goto(base + route)
                assert response.status == 200, route
                assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), (width, route)
                rss_box = page.locator('.site-footer nav a').first.bounding_box()
                theme_box = page.locator('#theme-toggle').bounding_box()
                assert abs(rss_box['y'] + rss_box['height'] / 2 - theme_box['y'] - theme_box['height'] / 2) < 2, (width, route, 'Footer controls must stay in one row')
                current = page.locator('.utility-nav a[aria-current]')
                if route == '/':
                    assert current.count() == 0
                elif route in ('/cultivation/', '/now/', '/path/', '/realms/', '/roots/'):
                    assert current.count() == 1 and current.get_attribute('href').endswith('/cultivation/'), route
                    assert page.locator('.section-nav').count() == 0
                elif route == '/about/':
                    assert current.count() == 1 and current.get_attribute('href').endswith('/about/')
                    assert page.locator('.section-nav').count() == 0
                else:
                    assert current.count() == 1 and current.get_attribute('href').endswith('/posts/'), route
                    assert page.locator('.section-nav a').all_text_contents() == ['全部文字', '存档', '分类', '最近更新']
            shared_styles = []
            for route in ('/cultivation/', '/posts/'):
                page.goto(base + route)
                shared_styles.append(page.evaluate('''() => {
                    const style = selector => {
                        const s = getComputedStyle(document.querySelector(selector));
                        return [s.fontSize, s.fontWeight, s.lineHeight, s.padding, s.margin, s.display, s.gridTemplateColumns];
                    };
                    return ['.page-heading', '.entry-list', '.entry-list > li', '.entry-title', '.entry-list time'].map(style);
                }'''))
            assert shared_styles[0] == shared_styles[1], (width, 'Cultivation and Posts must use the same heading and list styles')
            if width == 375 and screenshots:
                for name, route in (('home-mobile', '/'), ('cultivation-mobile', '/cultivation/'), ('article-mobile', '/posts/cultivation-realms/')):
                    page.goto(base + route)
                    page.screenshot(path=str(screenshots / (name + '.png')), full_page=True)
        print(f'PASS {len(routes) * 4} responsive route/viewport checks (320–1440px), region highlighting and contextual navigation')

        page.goto(base + '/posts/hello-world/')
        assert page.locator('.prose code').inner_text().strip() == 'console.log("hello");'
        print('PASS Hello World at its canonical post URL')
        context.close()

        offline = browser.new_context(java_script_enabled=False, color_scheme='dark')
        nojs = offline.new_page()
        nojs.goto(base + '/posts/cultivation-realms/')
        assert nojs.locator('.prose table').count() == 6
        assert nojs.locator('#theme-toggle').is_hidden()
        nojs.locator('.article-toc summary').click()
        assert nojs.locator('#TableOfContents').is_visible()
        assert nojs.locator('.post-navigation a').count() > 0
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
