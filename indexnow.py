#!/usr/bin/env python3
"""Tell Bing (which feeds ChatGPT search), DuckDuckGo, Yandex and friends that pages
changed, via IndexNow. Free, no account. Reads every URL in dist/sitemap.xml and posts
them in one request. The key lives in site/indexnow-key.txt and build.py publishes it
at /<key>.txt so the engines can verify we own the site.

Usage: python3 indexnow.py            (after a publish; the daily workflow runs it too)
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST = "www.normaltownusa.com"

key = (ROOT / "site" / "indexnow-key.txt").read_text().strip()
sitemap = (ROOT / "dist" / "sitemap.xml").read_text()
urls = re.findall(r"<loc>([^<]+)</loc>", sitemap)
if not urls:
    sys.exit("no URLs found in dist/sitemap.xml")

payload = json.dumps({
    "host": HOST,
    "key": key,
    "keyLocation": f"https://{HOST}/{key}.txt",
    "urlList": urls[:10000],
}).encode("utf-8")
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow: HTTP {r.status} for {len(urls)} URLs")
except urllib.error.HTTPError as e:
    print(f"IndexNow: HTTP {e.code} {e.reason} (200/202 = accepted)")
    sys.exit(0 if e.code in (200, 202) else 1)
