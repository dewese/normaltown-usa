#!/usr/bin/env python3
"""Technical health check of the LIVE site (www.normaltownusa.com). Standard library only.

Crawls every URL in the live sitemap and checks:
  - each page returns 200, has one <h1>, a <title>, a meta description, a canonical that
    matches its own URL, valid JSON-LD, and alt text on every image
  - every internal link resolves, and every external link (sampled politely) still works
  - every CrowdHealth link carries referral_code=NORMAL, every River link carries r=EYL3QNCO
  - robots.txt has no Cloudflare-managed block and no Disallow lines
  - apex -> www and http -> https redirects are 301s that keep the path
  - the 404 page returns a real 404, and sitemap/rss/llms files are reachable
  - security headers are present

Writes monitor/private/reports/<date>-tech.json and .md, and compares with the last run so
the report lists NEW problems separately from old ones.

Usage: python3 monitor/techcheck.py [--no-external]
Exit code 1 if any error-level issue is found (warnings do not fail).
"""
import concurrent.futures as cf
import datetime as dt
import html.parser
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://www.normaltownusa.com"
HOST = "www.normaltownusa.com"
UA = "Mozilla/5.0 (compatible; NormaltownSiteCheck/1.0)"
ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "private" / "reports"
SECURITY_HEADERS = ("x-content-type-options", "x-frame-options", "referrer-policy")
CTX = ssl.create_default_context()


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


_noredir = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=CTX))
_redir = urllib.request.build_opener(urllib.request.HTTPSHandler(context=CTX))


def fetch(url, method="GET", follow=True, timeout=20):
    """Return (status, headers dict, body text, final url, seconds). status 0 = network error."""
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
    t = time.time()
    try:
        r = (_redir if follow else _noredir).open(req, timeout=timeout)
        body = r.read().decode("utf-8", "replace") if method == "GET" else ""
        return r.status, {k.lower(): v for k, v in r.headers.items()}, body, r.geturl(), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, "", url, time.time() - t
    except Exception as e:  # DNS, timeout, TLS
        return 0, {"error": str(e)}, "", url, time.time() - t


class PageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.in_title, self.h1 = "", False, 0
        self.meta_desc = self.canonical = None
        self.links, self.imgs_no_alt, self.jsonld = [], [], []
        self._in_ld, self._ld = False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta" and (a.get("name") or "").lower() == "description":
            self.meta_desc = a.get("content") or ""
        elif tag == "link" and "canonical" in (a.get("rel") or "").lower().split():
            self.canonical = a.get("href")
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "img" and a.get("alt") is None:
            self.imgs_no_alt.append(a.get("src", "?"))
        elif tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_ld, self._ld = True, []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "script" and self._in_ld:
            self._in_ld = False
            self.jsonld.append("".join(self._ld))

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self._in_ld:
            self._ld.append(data)


def norm(url):
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path or "/", p.query, ""))


def main():
    check_external = "--no-external" not in sys.argv
    issues = []  # dicts: level (error|warn), check, url, detail

    def add(level, check, url, detail=""):
        issues.append({"level": level, "check": check, "url": url, "detail": detail})

    # --- site-wide checks -------------------------------------------------------------
    st, hd, robots, _, _ = fetch(SITE + "/robots.txt")
    if st != 200:
        add("error", "robots.txt reachable", SITE + "/robots.txt", f"status {st}")
    else:
        if "BEGIN Cloudflare Managed" in robots:
            add("error", "robots.txt: Cloudflare managed block is back", SITE + "/robots.txt",
                "Security > Settings > Bot traffic > Manage your robots.txt -> Disable")
        if re.search(r"(?im)^\s*disallow:\s*\S", robots):
            add("warn", "robots.txt has Disallow lines", SITE + "/robots.txt")
        if "sitemap:" not in robots.lower():
            add("warn", "robots.txt missing Sitemap line", SITE + "/robots.txt")

    for src, want in (("https://normaltownusa.com/faq/?x=1", SITE + "/faq/?x=1"),
                      ("http://www.normaltownusa.com/faq/", SITE + "/faq/"),
                      ("http://normaltownusa.com/faq/", None)):
        st, hd, _, _, _ = fetch(src, follow=False)
        loc = hd.get("location", "")
        if st not in (301, 308):
            add("error", "redirect to https://www", src, f"status {st}, location {loc or '-'}")
        elif want and loc != want:
            add("warn", "redirect target", src, f"goes to {loc}, expected {want}")

    st, _, _, _, _ = fetch(SITE + "/this-page-does-not-exist-check/")
    if st != 404:
        add("error", "404 page returns real 404", SITE + "/this-page-does-not-exist-check/", f"status {st}")

    for path in ("/rss.xml", "/llms.txt", "/llms-full.txt"):
        st, _, _, _, _ = fetch(SITE + path, method="HEAD")
        if st != 200:
            add("error", "feed/LLM file reachable", SITE + path, f"status {st}")

    st, _, sitemap, _, _ = fetch(SITE + "/sitemap.xml")
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap) if st == 200 else []
    if not urls:
        add("error", "sitemap.xml readable", SITE + "/sitemap.xml", f"status {st}")

    # --- page checks ------------------------------------------------------------------
    pages = {}

    def check_page(url):
        return url, fetch(url)

    with cf.ThreadPoolExecutor(8) as ex:
        for url, (st, hd, body, final, secs) in ex.map(check_page, urls):
            pages[url] = {"status": st, "seconds": round(secs, 2)}
            if st != 200:
                add("error", "sitemap page returns 200", url, f"status {st}")
                continue
            if norm(final) != norm(url):
                add("warn", "sitemap URL redirects", url, f"ends at {final}")
            missing = [h for h in SECURITY_HEADERS if h not in hd]
            if missing:
                add("warn", "security headers", url, ", ".join(missing))
            p = PageParser()
            p.feed(body)
            pages[url].update(title=p.title.strip(), links=p.links)
            if not p.title.strip():
                add("error", "has <title>", url)
            else:
                bare = p.title.strip().removesuffix(" | Normaltown USA") if hasattr(str, "removesuffix") \
                    else re.sub(r" \| Normaltown USA$", "", p.title.strip())
                if len(bare) > 65:  # Google shows ~60 chars; the brand suffix is expected to be cut
                    add("warn", "title (before ' | Normaltown USA') over 65 chars", url, f"{len(bare)} chars")
            if not p.meta_desc:
                add("error", "has meta description", url)
            elif len(p.meta_desc) > 160:
                add("warn", "meta description over 160 chars", url, f"{len(p.meta_desc)} chars")
            if p.canonical is None:
                add("error", "has canonical", url)
            elif norm(p.canonical) != norm(url):
                add("error", "canonical matches URL", url, f"canonical is {p.canonical}")
            if p.h1 != 1:
                add("warn", "exactly one <h1>", url, f"{p.h1} found")
            for src in p.imgs_no_alt:
                add("error", "image has alt attribute", url, src)
            for block in p.jsonld:
                try:
                    json.loads(block)
                except ValueError as e:
                    add("error", "JSON-LD parses", url, str(e)[:120])
            if "/p/" in url and not p.jsonld:
                add("warn", "post has JSON-LD", url)

    # --- link checks ------------------------------------------------------------------
    internal, external = {}, {}
    for url, info in pages.items():
        for href in info.get("links", []):
            if href.startswith(("mailto:", "tel:", "#", "javascript:")):
                continue
            absu = urllib.parse.urljoin(url, href)
            host = urllib.parse.urlsplit(absu).netloc.lower()
            if "joincrowdhealth.com" in host and "referral_code=NORMAL" not in absu:
                add("error", "CrowdHealth link has referral_code=NORMAL", url, absu)
            if host.endswith("river.com") and "/signup" in absu and "r=EYL3QNCO" not in absu:
                add("error", "River signup link has r=EYL3QNCO", url, absu)
            target = internal if host in (HOST, "normaltownusa.com", "") else external
            target.setdefault(urllib.parse.urldefrag(absu)[0], set()).add(url)

    def head_or_get(u):
        st, hd, _, final, _ = fetch(u, method="HEAD", timeout=15)
        if st in (0, 403, 405, 429, 400, 501) or st >= 500:
            st, hd, _, final, _ = fetch(u, method="GET", timeout=20)
        return u, st, hd.get("error", "")

    with cf.ThreadPoolExecutor(8) as ex:
        for u, st, err in ex.map(head_or_get, sorted(internal)):
            if st != 200:
                for page in sorted(internal[u])[:3]:
                    add("error", "internal link works", page, f"{u} -> {st or err}")
    ext_checked = 0
    if check_external:
        with cf.ThreadPoolExecutor(6) as ex:
            for u, st, err in ex.map(head_or_get, sorted(external)):
                ext_checked += 1
                if st == 404 or st == 410 or (st == 0 and "Name or service" in err):
                    add("error", "external link works", sorted(external[u])[0],
                        f"{u} -> {st or err} (on {len(external[u])} page(s))")
                elif st != 200 and not (300 <= st < 400):
                    add("warn", "external link works (may block bots)", sorted(external[u])[0],
                        f"{u} -> {st or err[:80]} (on {len(external[u])} page(s))")

    slow = sorted(((v["seconds"], u) for u, v in pages.items() if v.get("seconds", 0) > 2.5), reverse=True)
    for secs, u in slow[:10]:
        add("warn", "server response over 2.5s", u, f"{secs}s")

    # --- compare with last run --------------------------------------------------------
    REPORTS.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    key = lambda i: (i["check"], i["url"], i["detail"])
    prev = sorted(p for p in REPORTS.glob("*-tech.json") if not p.name.startswith(today))
    old = set()
    if prev:
        try:
            old = {key(i) for i in json.loads(prev[-1].read_text())["issues"]}
        except Exception:
            pass
    for i in issues:
        i["new"] = bool(prev) and key(i) not in old
    resolved = sorted(old - {key(i) for i in issues})

    errors = [i for i in issues if i["level"] == "error"]
    warns = [i for i in issues if i["level"] == "warn"]
    result = {"date": today, "pages": len(pages), "internal_links": len(internal),
              "external_links_checked": ext_checked, "errors": len(errors), "warnings": len(warns),
              "issues": issues, "resolved_since_last_run": [list(r) for r in resolved],
              "compared_with": prev[-1].name if prev else None}
    (REPORTS / f"{today}-tech.json").write_text(json.dumps(result, indent=1))

    lines = [f"# Technical check {today}", "",
             f"{len(pages)} pages, {len(internal)} internal links, {ext_checked} external links checked.",
             f"**{len(errors)} errors, {len(warns)} warnings.** "
             f"New since last run: {sum(i['new'] for i in issues)}. Resolved: {len(resolved)}.", ""]
    for title, group in (("Errors", errors), ("Warnings", warns)):
        if group:
            lines += [f"## {title}", ""]
            by_check = {}
            for i in group:
                by_check.setdefault(i["check"], []).append(i)
            for check, items in sorted(by_check.items(), key=lambda kv: (not any(i["new"] for i in kv[1]), kv[0])):
                n_new = sum(i["new"] for i in items)
                tag = f"**NEW x{n_new}** " if n_new else ""
                if len(items) > 5:  # collapse long lists; full detail stays in the JSON
                    sample = ", ".join(urllib.parse.urlsplit(i["url"]).path for i in items[:5])
                    lines.append(f"- {tag}{check}: {len(items)} pages (e.g. {sample})")
                else:
                    for i in items:
                        lines.append(f"- {'**NEW** ' if i['new'] else ''}{check}: {i['url']}"
                                     + (f" ({i['detail']})" if i["detail"] else ""))
            lines.append("")
    if resolved:
        lines += ["## Resolved since last run", ""] + [f"- {c}: {u}" for c, u, _ in resolved] + [""]
    (REPORTS / f"{today}-tech.md").write_text("\n".join(lines))
    print("\n".join(lines))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
