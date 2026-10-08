#!/usr/bin/env python3
"""Download the public Hyperliquid GitBook, using only Python's standard library."""
import concurrent.futures
import datetime
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = 'https://hyperliquid.gitbook.io/hyperliquid-docs'
ROOT = Path(__file__).resolve().parents[1]
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(url):
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Hyperliquid-documentation-archive/1.0'})
            with OPENER.open(request, timeout=45) as response:
                return response.read(), response.headers.get_content_type()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def main():
    sources = ROOT / 'sources'
    sources.mkdir(parents=True, exist_ok=True)
    urls = {}
    pending = [BASE + '/sitemap.xml']
    seen = set()
    while pending:
        url = pending.pop(0)
        if url in seen:
            continue
        seen.add(url)
        raw, _ = fetch(url)
        relative = urllib.parse.urlsplit(url).path.removeprefix('/hyperliquid-docs/').replace('/', '__')
        (sources / relative).write_bytes(raw)
        tree = ET.fromstring(raw)
        for entry in tree:
            loc = entry.find('{*}loc').text
            if tree.tag.endswith('sitemapindex'):
                pending.append(loc)
            else:
                lastmod = entry.find('{*}lastmod')
                urls[loc.rstrip('/')] = lastmod.text if lastmod is not None else None

    indexed = {}
    for section in ('',):
        url = BASE + section + '/llms.txt'
        raw, _ = fetch(url)
        (sources / ('llms' + section.replace('/', '-') + '.txt')).write_bytes(raw)
        for title, md_url in re.findall(r'^- \[([^\n]+?)\]\((https://[^\s)]+\.md)\)', raw.decode(), re.M):
            if md_url.startswith(BASE + '/'):
                indexed[md_url[:-3]] = title
    # GitBook's root page has a canonical slug in llms.txt rather than root.md.
    aliases = {BASE: BASE + '/about-hyperliquid',
               BASE + '/support': BASE + '/support/read-me-support-guide',
               BASE + '/builder-tools': BASE + '/builder-tools/read-me-builder-tools'}
    for old, new in aliases.items():
        if old in urls and new in indexed:
            urls[new] = urls.pop(old)
    for url in indexed:
        urls.setdefault(url, None)
    pages = []
    failed = []

    def download_page(item):
        url, lastmod = item
        raw, content_type = fetch(url + '.md')
        text = raw.decode('utf-8')
        if '# Page Not Found' in text[:1000] or content_type == 'text/html' or not re.search(r'^# ', text, re.M):
            raise ValueError('Invalid Markdown export: ' + url)
        relative = urllib.parse.unquote(url.removeprefix(BASE + '/'))
        path = Path('docs') / (relative + '.md')
        if '..' in path.parts or path.is_absolute():
            raise ValueError('Unsafe page path')
        title_match = re.search(r'^# (.+)$', text, re.M)
        return {'source_url': url, 'markdown_url': url + '.md', 'path': path.as_posix(),
                'title': indexed.get(url, title_match.group(1)), 'source_lastmod': lastmod,
                'raw_sha256': hashlib.sha256(raw).hexdigest(), '_text': text}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(download_page, item): item[0] for item in urls.items()}
        for future in concurrent.futures.as_completed(futures):
            try:
                pages.append(future.result())
            except Exception as error:
                failed.append({'url': futures[future], 'error': str(error)})
            if (len(pages) + len(failed)) % 25 == 0:
                print(f'Downloaded {len(pages)}/{len(urls)} pages; failed {len(failed)}', flush=True)
    if failed:
        (ROOT / 'download-errors.json').write_text(json.dumps(failed, indent=2))
        raise RuntimeError(f'{len(failed)} pages failed; see download-errors.json')

    page_map = {page['source_url']: page['path'] for page in pages}
    page_map.update({old: page_map[new] for old, new in aliases.items() if new in page_map})
    asset_urls = set()
    attachment_aliases = {}
    for page in pages:
        placeholders = list(dict.fromkeys(re.findall(r'src=["\'](/files/[^"\']+)["\']', page['_text'])))
        if placeholders:
            attachment_urls = []
            class AttachmentParser(HTMLParser):
                def handle_starttag(self, tag, attrs):
                    href = dict(attrs).get('href', '')
                    if tag == 'a' and ('files.gitbook.io/' in href or 'files.gitbook.com/' in href):
                        if href not in attachment_urls:
                            attachment_urls.append(href)
            raw_html, _ = fetch(page['source_url'])
            AttachmentParser().feed(raw_html.decode('utf-8'))
            if len(placeholders) != len(attachment_urls):
                raise RuntimeError('Cannot resolve all file attachments: ' + page['source_url'])
            for placeholder, url in zip(placeholders, attachment_urls):
                attachment_aliases[placeholder] = url
                asset_urls.add(url)
        for asset in re.findall(r'(?:src|href)=["\'](https://[^"\']+)["\']', page['_text']):
            parsed = urllib.parse.urlsplit(html.unescape(asset))
            if parsed.hostname and (parsed.hostname.endswith('files.gitbook.io') or parsed.hostname == 'files.gitbook.com'):
                asset_urls.add(html.unescape(asset))
        for asset in re.findall(r'!?\[[^\]\n]*\]\((https://[^\s)]+)\)', page['_text']):
            parsed = urllib.parse.urlsplit(html.unescape(asset))
            if parsed.hostname and (parsed.hostname.endswith('files.gitbook.io') or parsed.hostname == 'files.gitbook.com'):
                asset_urls.add(html.unescape(asset))
    assets = []
    asset_failed = []

    def download_asset(url):
        raw, content_type = fetch(url)
        unquoted = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
        filename = unquoted.rsplit('/', 1)[-1]
        filename = re.sub(r'[^\w. -]', '_', filename) or 'asset'
        path = Path('assets') / (hashlib.sha256(url.encode()).hexdigest()[:12] + '-' + filename)
        (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / path).write_bytes(raw)
        return {'source_url': url, 'path': path.as_posix(), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'content_type': content_type}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(download_asset, url): url for url in asset_urls}
        for future in concurrent.futures.as_completed(futures):
            try:
                assets.append(future.result())
            except Exception as error:
                asset_failed.append({'url': futures[future], 'error': str(error)})
    asset_map = {asset['source_url']: asset['path'] for asset in assets}
    asset_map.update({placeholder: asset_map[url] for placeholder, url in attachment_aliases.items() if url in asset_map})
    for page in pages:
        text = page.pop('_text')
        # Rewrite known page and attachment links, leaving code examples intact.
        blocks = re.split(r'(```[^\n]*\n.*?```|~~~[^\n]*\n.*?~~~)', text, flags=re.S)
        def local_link(match):
            full_url = html.unescape(match.group(0))
            if full_url.startswith('/hyperliquid-docs/'):
                full_url = 'https://hyperliquid.gitbook.io' + full_url
            if full_url in asset_map:
                return urllib.parse.quote(os.path.relpath(ROOT / asset_map[full_url], (ROOT / page['path']).parent), safe='/.-_')
            if not full_url.startswith(BASE) and full_url not in asset_map:
                return match.group(0)
            parsed = urllib.parse.urlsplit(full_url)
            canonical = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path.removesuffix('.md').rstrip('/'), '', ''))
            target = asset_map.get(full_url) or page_map.get(canonical)
            if not target:
                return match.group(0)
            local = urllib.parse.quote(os.path.relpath(ROOT / target, (ROOT / page['path']).parent), safe='/.-_')
            if canonical in page_map and parsed.fragment:
                local += '#' + parsed.fragment
            return local
        for index in range(0, len(blocks), 2):
            blocks[index] = re.sub(r'https://[^\s<>"\')]+', local_link, blocks[index])
            blocks[index] = re.sub(r'(?<![A-Za-z0-9:/])/(?:hyperliquid-docs|files)/[^\s<>"\')]+', local_link, blocks[index])
            blocks[index] = re.sub(r'{% file src="([^"]+)" %}\s*(.*?)\s*{% endfile %}',
                                   lambda match: '[' + (match.group(2).strip() or urllib.parse.unquote(match.group(1)).rsplit('/', 1)[-1]) + '](' + match.group(1) + ')', blocks[index], flags=re.S)
            blocks[index] = re.sub(r'{% file src="([^"]+)" %}',
                                   lambda match: '[' + urllib.parse.unquote(match.group(1)).rsplit('/', 1)[-1] + '](' + match.group(1) + ')', blocks[index])
        text = ''.join(blocks)
        text = f'<!-- Source: {page["source_url"]} -->\n\n' + text
        destination = ROOT / page['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding='utf-8')
        page['sha256'] = hashlib.sha256(text.encode()).hexdigest()

    pages.sort(key=lambda page: page['path'])
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest = {'source': BASE, 'downloaded_at_utc': timestamp, 'page_count': len(pages),
                'asset_count': len(assets), 'pages': pages, 'assets': sorted(assets, key=lambda asset: asset['path']),
                'asset_failures': asset_failed}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = '# 文档目录 / Documentation index\n\n'
    for page in pages:
        depth = max(0, page['path'].count('/') - 1)
        summary += '  ' * depth + f'- [{page["title"]}]({urllib.parse.quote(page["path"], safe="/.-_")})\n'
    (ROOT / 'SUMMARY.md').write_text(summary, encoding='utf-8')
    print(json.dumps({'pages': len(pages), 'assets': len(assets), 'asset_failures': len(asset_failed), 'downloaded_at_utc': timestamp}), flush=True)


if __name__ == '__main__':
    main()
