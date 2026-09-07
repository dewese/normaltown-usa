#!/usr/bin/env python3
"""
Normaltown USA - static site generator (zero dependencies, Python 3 stdlib only).

The "machine": reads finished posts from Posts/<YYYY>/<MM>/<DD>/ and the site
copy in site/, then writes a complete static website to dist/.

Publishing a new post = drop its folder in Posts/ (article.md + publish.md
+ one .png), run `python3 build.py`, commit, push. Cloudflare Pages serves dist/.

SEO / GEO features (all automatic, driven by the post files):
  * JSON-LD on every page: WebSite + Organization, BlogPosting + BreadcrumbList
    on posts, FAQPage wherever a post (or the FAQ page) has question headings,
    Person on the About page, CollectionPage on topic hubs.
  * "In short" answer box: a `> ` blockquote right after the title in article.md.
  * FAQ: a `## Questions ...` section in article.md whose `### ` headings are the
    questions; each becomes visible content AND FAQPage schema.
  * Topic hubs (/money/, /health/, /bitcoin/), related posts, prev/next links,
    author box, visible published + updated dates, reading time, heading anchors.
  * llms.txt + llms-full.txt, RSS with full text, sitemap with lastmod,
    Cloudflare `_headers`, 404 page, absolute internal links normalised.

Brand (locked): canvas #0F0F0F (never #000), text #FFFFFF, accent cyan #2DD4FF,
Manrope for body/UI type. Logo = the SVG lockup in brand/logo/ (Montserrat ExtraBold,
outlined to paths, so no logo font is loaded). Visualize-Value aesthetic: one idea,
lots of negative space.
"""

import hashlib
import html
import json
import re
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "Posts"
SITE_DIR = ROOT / "site"
LOGO_DIR = ROOT / "brand" / "logo"   # SVG logo lockup + icon; copied to dist/assets/
DIST = ROOT / "dist"

SITE_NAME = "Normaltown USA"
SITE_TAGLINE = "Money & Healthcare Made Simple"
SITE_URL = "https://www.normaltownusa.com"
HOME_TITLE = "Normaltown USA: Plain-English Money and Health Help for Regular People"
HOME_DESC = ("Plain-English help with money, medical bills, health insurance, health "
             "sharing, and saving in bitcoin. Written by a regular guy with a family "
             "of four, for regular people. No jargon, no hype.")
AUTHOR = "David Dewese"
AUTHOR_FIRST = "David"
AUTHOR_URL = f"{SITE_URL}/about/"
AUTHOR_BIO = ("Normal guy with a full-time job, wife, and kids. Spent twenty years pursuing "
              "music and creative ventures before starting a family. Sharing tips and tricks "
              "on how to thrive while living on an artist's income. Not a financial advisor.")
AFFILIATE_URL = "https://www.joincrowdhealth.com/?referral_code=NORMAL"
CONTACT_EMAIL = "normaltownusa@gmail.com"
GA_ID = "G-8MJ82YYL8M"   # Google Analytics 4 measurement ID; set to "" to drop the tag

# Footer newsletter signup, on every page: beehiiv's inline embed (Subscribers > Subscribe
# forms > the form > Get embed code). The loader script renders the form in an iframe and
# already handles UTM/referrer attribution, so beehiiv's separate attribution.js is not
# needed. The label and fine print around it are ours, so only the field and button need
# styling inside beehiiv's builder. Set this to "" to fall back to a plain FormSubmit form
# that emails each signup to CONTACT_EMAIL.
NEWSLETTER_EMBED = ('<script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" '
                    'data-beehiiv-form="27669cbb-d776-41db-adde-6dad6f4d127a"></script>')

# "Updated" dates: a commit that touches more than this many articles at once is a
# site-wide edit (a template or wording pass), not a content update, and is ignored.
MASS_EDIT_FILES = 3

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# Date-gated publishing: a post whose folder date is in the future is written
# but NOT published until that day. Rebuild (or the daily cron) to release it.
# Use Eastern time so posts release on the brand's clock, not the CI server's UTC.
try:
    from zoneinfo import ZoneInfo
    TODAY = datetime.now(ZoneInfo("America/New_York")).date()
except Exception:
    TODAY = date.today()

# Topic hubs. Key = category slug; "name" is the pill label on cards.
CATEGORIES = {
    "money": {
        "name": "Money",
        "title": "Money for Normal People",
        "blurb": "Why you feel broke on a decent income, where it leaks out, and small moves that actually help.",
        "page_title": "Money for Normal People: Budgets, Raises, Debt, and Leaks Explained Plainly",
        "description": ("Plain-English money help for working families: why you feel broke on a "
                        "good income, where money leaks out, credit card interest, budgets that "
                        "survive a busy week, and what to do with a raise."),
        "intro": ("You work hard, you pay your bills, and the account still looks the same at the "
                  "end of the month. These posts explain why, in normal words, and give you one "
                  "small move at a time. No spreadsheets, no shame."),
    },
    "health": {
        "name": "Health",
        "title": "Health Insurance, Medical Bills, and Health Sharing",
        "blurb": "Why medical bills surprise you, how to pay less for care, and an honest look at health sharing.",
        "page_title": "Medical Bills, Health Insurance, and Health Sharing Explained in Plain English",
        "description": ("Why you get big bills with insurance, how deductibles and HSAs really work, "
                        "how to ask for the cash price, how to negotiate a hospital bill, and an "
                        "honest look at health sharing from a family that uses it."),
        "intro": ("A medical bill is the biggest money leak most families have. It's a money problem "
                  "wearing a lab coat. These posts explain how the system actually works, how to pay "
                  "less for care, and what health sharing is (my family of four uses CrowdHealth, "
                  "and I'll always tell you its honest limits)."),
    },
    "bitcoin": {
        "name": "Bitcoin",
        "title": "Bitcoin and the Dollar, Explained Calmly",
        "blurb": "Why the dollar loses value and where bitcoin fits as savings, not gambling.",
        "page_title": "Bitcoin for Normal People: Saving, Not Gambling, Explained Calmly",
        "description": ("A calm, plain-English look at why the dollar loses value over time and where "
                        "bitcoin fits as savings, not gambling: how to buy a first $20, how much is too "
                        "much, wallets, keys, and price swings."),
        "intro": ("This is the quiet corner of the internet on bitcoin. No hype, no price predictions. "
                  "Just why money loses value over time, why something hard to make holds its value, "
                  "and how a normal family can save a small amount in bitcoin without losing sleep."),
    },
}

# Slugs that belong in the Bitcoin hub even if publish.md still says "Money".
BITCOIN_SLUGS = {
    "is-bitcoin-saving-or-gambling", "what-scarce-means-for-your-money",
    "your-first-20-in-bitcoin", "the-dollars-slow-leak",
    "why-hard-to-make-money-holds-its-value", "a-little-each-week-beats-betting-it-all",
    "why-i-dont-try-to-time-the-price", "bitcoins-wild-price-swings-explained-calmly",
    "who-gets-the-new-money-first", "not-your-keys-what-it-means",
    "what-is-a-bitcoin-wallet", "how-much-is-too-much-sizing-a-small-bet",
}

# ----------------------------------------------------------------------------
# Minimal, controlled Markdown -> HTML (only the subset our articles use).
# ----------------------------------------------------------------------------

INTERNAL_ABS = re.compile(r'https?://(?:www\.)?normaltownusa\.com(/[^\s)"]*)?')

# Slugs of posts that exist but aren't published yet (future-dated). Links to
# them are rendered as plain text until the post goes live, so nothing 404s.
UNPUBLISHED = set()


def normalise_url(url):
    """Absolute links to our own site become root-relative, with a trailing slash
    on directory URLs (avoids a redirect hop on Cloudflare)."""
    m = INTERNAL_ABS.fullmatch(url.strip())
    if m:
        path = m.group(1) or "/"
        if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1] and "#" not in path:
            path += "/"
        return path
    return url


NEW_TAB = '<span class="sr-only"> (opens in a new tab)</span>'


def _inline(text):
    """Escape HTML, then apply inline markdown: links, bold, italic, code."""
    text = html.escape(text, quote=False)

    def link(m):
        label, url = m.group(1), normalise_url(m.group(2))
        um = re.match(r'^/p/([^/#?]+)/?', url)
        if um and um.group(1) in UNPUBLISHED:
            return label
        safe_url = html.escape(url, quote=True)
        attrs = ""
        if url.startswith("http"):
            rel = "noopener nofollow sponsored" if "joincrowdhealth.com" in url else "noopener"
            attrs = f' target="_blank" rel="{rel}"'
        if attrs:
            label += NEW_TAB
        return f'<a href="{safe_url}"{attrs}>{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![*\w])\*([^*\n]+)\*(?![*\w])', r'<em>\1</em>', text)
    return text


def plain_text(md):
    """Markdown -> plain text (for schema answers, descriptions, llms-full)."""
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', md)
    t = re.sub(r'[*`_]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


def slugify(title):
    s = title.lower()
    s = re.sub(r'&', ' and ', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def heading_id(text, used):
    base = slugify(plain_text(text))[:60].strip('-') or "section"
    hid, n = base, 2
    while hid in used:
        hid, n = f"{base}-{n}", n + 1
    used.add(hid)
    return hid


def strip_email_cta(md):
    """Drop a trailing email-style CTA block: a final '---' followed by inbox/list copy."""
    lines = md.split("\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "---":
            tail = "\n".join(lines[i + 1:]).lower()
            if any(k in tail for k in ("inbox", "normaltown usa list", "join the")):
                lines = lines[:i]
            break
    return "\n".join(lines)


def md_to_html(md, drop_email_cta=True, ids=None):
    """Convert an article body (title line already removed) to HTML blocks."""
    if drop_email_cta:
        md = strip_email_cta(md)
    lines = md.split("\n")
    used = ids if ids is not None else set()

    blocks = []
    buf = []

    def flush_para():
        if buf:
            joined = " ".join(l.strip() for l in buf).strip()
            if joined:
                blocks.append(f"<p>{_inline(joined)}</p>")
            buf.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush_para()
        elif stripped == "---":
            flush_para()
            blocks.append('<hr class="rule">')
        elif stripped.startswith("### "):
            flush_para()
            t = stripped[4:].strip()
            blocks.append(f'<h3 id="{heading_id(t, used)}">{_inline(t)}</h3>')
        elif stripped.startswith("## ") or stripped.startswith("# "):
            flush_para()
            t = stripped.split(" ", 1)[1].strip()
            blocks.append(f'<h2 id="{heading_id(t, used)}">{_inline(t)}</h2>')
        elif stripped.startswith("> "):
            flush_para()
            q = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q.append(lines[i].strip().lstrip(">").strip())
                i += 1
            blocks.append(f"<blockquote><p>{_inline(' '.join(q))}</p></blockquote>")
            continue
        elif re.match(r'^[-*] ', stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i].strip()):
                items.append(f"<li>{_inline(lines[i].strip()[2:].strip())}</li>")
                i += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        elif re.match(r'^\d+\. ', stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i].strip()):
                item_text = re.sub(r'^\d+\. ', '', lines[i].strip())
                items.append(f"<li>{_inline(item_text)}</li>")
                i += 1
            blocks.append("<ol>" + "".join(items) + "</ol>")
            continue
        else:
            buf.append(line)
        i += 1
    flush_para()
    return "\n".join(blocks)


def extract_short_answer(body_md):
    """A `> ` blockquote right after the title (before any heading) is the
    'In short' answer. Returns (answer_markdown or None, body_without_it)."""
    lines = body_md.split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].strip().startswith("> "):
        q = []
        j = i
        while j < len(lines) and lines[j].strip().startswith(">"):
            q.append(lines[j].strip().lstrip(">").strip())
            j += 1
        rest = lines[:i] + lines[j:]
        return " ".join(q).strip(), "\n".join(rest)
    return None, body_md


SOURCES_HEADING = re.compile(r'^##\s+(sources|where i checked|references|further reading)\b', re.IGNORECASE)
SOURCE_ITEM = re.compile(r'^[-*]\s+(?:\[([^\]]+)\]\((https?://[^)\s]+)\)|<?(https?://\S+?)>?)\s*[:.,\u2014-]*\s*(.*)$')


def extract_sources(md):
    """A `## Sources` section whose items are `- [Label](url): note` is pulled out of
    the body and rendered as its own Sources box (and as `citation` in the schema).
    Returns ([(label, url, note)], body_without_the_section)."""
    sources, out, in_section = [], [], False
    for line in md.split("\n"):
        s = line.strip()
        if s.startswith("## ") or s.startswith("# "):
            in_section = bool(SOURCES_HEADING.match(s))
            if in_section:
                continue
        if in_section:
            if s == "---":          # the trailing disclaimer rule ends the section
                in_section = False
                out.append(line)
                continue
            m = SOURCE_ITEM.match(s)
            if m:
                url = m.group(2) or m.group(3)
                label = (m.group(1) or re.sub(r'^https?://(www\.)?', '', url).rstrip('/')).strip()
                sources.append((label, url.strip(), m.group(4).strip().rstrip('.')))
            continue                # intro sentences inside the section are not rendered
        out.append(line)
    return sources, "\n".join(out)


FAQ_HEADING = re.compile(r'^##\s+.*(question|faq|people ask)', re.IGNORECASE)


def extract_faqs(md, every_h3=False):
    """Return [(question, answer_plain_text)] from `### ` headings.
    By default only inside a `## Questions ...` style section; with every_h3
    the whole document's ### headings count (used for the FAQ page)."""
    faqs = []
    in_section = every_h3
    q, ans = None, []

    def close():
        nonlocal q, ans
        if q and ans:
            faqs.append((plain_text(q), plain_text(" ".join(ans))))
        q, ans = None, []

    for line in md.split("\n"):
        s = line.strip()
        if s.startswith("## ") or s.startswith("# "):
            close()
            in_section = every_h3 or bool(FAQ_HEADING.match(s))
        elif s.startswith("### "):
            close()
            if in_section:
                q = s[4:].strip()
        elif q is not None:
            if s == "---":
                close()
            elif s:
                ans.append(s)
    close()
    return faqs


# ----------------------------------------------------------------------------
# Parsing posts
# ----------------------------------------------------------------------------

def _row_value(text, label):
    """Pull a value cell from a markdown table row whose first cell matches label."""
    pat = re.compile(r'^\|[^|]*' + re.escape(label) + r'[^|]*\|\s*(.+?)\s*\|',
                     re.IGNORECASE | re.MULTILINE)
    m = pat.search(text)
    if not m:
        return None
    val = m.group(1).strip()
    bt = re.search(r'`([^`]+)`', val)
    val = bt.group(1) if bt else val.strip("`")
    val = re.sub(r'\*?\(\s*\d+\s*chars?\s*\)\*?', '', val)
    val = re.sub(r'\*\*(.+?)\*\*', r'\1', val)
    val = val.strip().strip("`").strip()
    return val or None


def classify(pub_category, title, slug):
    if slug in BITCOIN_SLUGS:
        return "bitcoin"
    c = (pub_category or "").strip().lower()
    if c in CATEGORIES:
        return c
    text = (title + " " + slug).lower()
    if "bitcoin" in text:
        return "bitcoin"
    health = ("health", "insur", "deductible", "hsa", "sharing", "medical",
              "blood test", "crowd", "bill", "hospital", "advocate", "cobra", "er")
    if any(k in text for k in health):
        return "health"
    return "money"


def git_modified(path):
    """Date of the last commit touching path, or None (no git / shallow clone)."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                             capture_output=True, text=True, cwd=ROOT, timeout=10).stdout.strip()
        return date.fromisoformat(out) if out else None
    except Exception:
        return None


_ARTICLE_HISTORY = None


def article_history():
    """{repo-relative article path: [(commit date, was_created_here, n_articles_in_commit), ...]}
    newest first, from a single git call. Empty when git/history is unavailable."""
    global _ARTICLE_HISTORY
    if _ARTICLE_HISTORY is not None:
        return _ARTICLE_HISTORY
    _ARTICLE_HISTORY = {}
    try:
        out = subprocess.run(["git", "log", "--format=%x00%cs", "--name-status", "--", "Posts/*/article.md"],
                             capture_output=True, text=True, cwd=ROOT, timeout=20).stdout
    except Exception:
        return _ARTICLE_HISTORY
    for chunk in out.split("\x00")[1:]:
        lines = [l for l in chunk.split("\n") if l.strip()]
        if not lines:
            continue
        try:
            d = date.fromisoformat(lines[0].strip())
        except ValueError:
            continue
        files = []
        for l in lines[1:]:
            cells = l.split("\t")
            if len(cells) >= 2:
                files.append((cells[-1], cells[0].startswith("A")))
        for path, added in files:
            _ARTICLE_HISTORY.setdefault(path, []).append((d, added, len(files)))
    return _ARTICLE_HISTORY


def article_modified(article, pub, pub_date):
    """When a post was last substantively updated. An explicit `| Updated | YYYY-MM-DD |`
    row in publish.md wins. Otherwise: the newest commit that edited this article on its
    own, skipping the commit that created it and any commit touching many articles at
    once (a site-wide wording or template pass). Falls back to the publish date."""
    explicit = _row_value(pub, "Updated")
    if explicit:
        try:
            return max(date.fromisoformat(explicit.strip()[:10]), pub_date)
        except ValueError:
            pass
    rel = article.relative_to(ROOT).as_posix()
    for d, added, n in article_history().get(rel, []):
        if added or n > MASS_EDIT_FILES:
            continue
        return max(d, pub_date)
    return pub_date


def load_posts(include_future=False):
    posts = []
    # First pass: which slugs are written ahead but not yet live?
    UNPUBLISHED.clear()
    for article in POSTS_DIR.glob("*/*/*/article.md"):
        parts = article.parent.parts
        if date(int(parts[-3]), int(parts[-2]), int(parts[-1])) > TODAY and not include_future:
            pub_file = article.parent / "publish.md"
            pub = pub_file.read_text(encoding="utf-8") if pub_file.exists() else ""
            UNPUBLISHED.add(_row_value(pub, "slug") or "")
    for article in sorted(POSTS_DIR.glob("*/*/*/article.md")):
        folder = article.parent
        parts = folder.parts
        y, m, d = int(parts[-3]), int(parts[-2]), int(parts[-1])
        pub_date = date(y, m, d)
        if pub_date > TODAY and not include_future:
            continue  # future-dated: written ahead, not published yet
        raw = article.read_text(encoding="utf-8")

        title = folder.name
        body_md = raw
        for idx, line in enumerate(raw.split("\n")):
            if line.startswith("# "):
                title = line[2:].strip()
                body_md = "\n".join(raw.split("\n")[idx + 1:])
                break
        body_md = strip_email_cta(body_md)

        pub_file = folder / "publish.md"
        pub = pub_file.read_text(encoding="utf-8") if pub_file.exists() else ""

        slug = _row_value(pub, "slug") or slugify(title)
        subtitle = _row_value(pub, "Subtitle")
        meta = _row_value(pub, "Meta description")
        title_tag = _row_value(pub, "Title tag")
        if title_tag and title_tag.strip().lower() == title.strip().lower():
            title_tag = None

        short, body_md = extract_short_answer(body_md)
        sources, body_md = extract_sources(body_md)

        first_para = ""
        for para in body_md.split("\n\n"):
            p = para.strip()
            if p and not p.startswith("#") and p != "---" and not p.startswith(">"):
                first_para = re.sub(r'\s+', ' ', p)
                break
        if not meta:
            src = plain_text(short or first_para)
            meta = (src[:157] + "...") if len(src) > 160 else src

        alt = None
        am = re.search(r'[Aa]lt text[:*\s]+`?([^`\n|]+)`?', pub)
        if am:
            alt = am.group(1).strip().strip("`").strip()
        if not alt:
            alt = title

        png = next(iter(sorted(folder.glob("*.png"))), None)
        ids = set()
        body_html = md_to_html(body_md, drop_email_cta=False, ids=ids)
        words = len(plain_text(body_md).split())
        modified = article_modified(article, pub, pub_date)
        # dict.fromkeys, not set: dedupes but keeps the order the links appear in
        # the article, so related_posts() is stable across builds (set iteration
        # order varies per process with Python's hash randomisation).
        links = list(dict.fromkeys(
            re.findall(r'\]\((?:https?://(?:www\.)?normaltownusa\.com)?/p/([^/)#]+)', body_md)))

        posts.append({
            "date": pub_date,
            "modified": modified,
            "title": title,
            "title_tag": title_tag,
            "slug": slug,
            "url": f"{SITE_URL}/p/{slug}/",
            "subtitle": subtitle,
            "meta": meta,
            "short": short,
            "sources": sources,
            "preview": first_para,
            "alt": alt,
            "png": png,
            "png_name": png.name if png else None,
            "body_md": body_md,
            "body_html": body_html,
            "faqs": extract_faqs(body_md),
            "words": words,
            "minutes": max(1, round(words / 220)),
            "links": links,
            "category": classify(_row_value(pub, "Category"), title, slug),
            "affiliate": "joincrowdhealth.com" in body_md,
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


# ----------------------------------------------------------------------------
# Templates
# ----------------------------------------------------------------------------

CSS = """
:root{
  --canvas:#0F0F0F; --ink:#FFFFFF; --accent:#2DD4FF;
  --muted:rgba(255,255,255,.60); --faint:rgba(255,255,255,.12);
  --panel:#161616; --measure:40rem;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
@media (prefers-reduced-motion:reduce){*{transition:none !important}}
body{
  margin:0; background:var(--canvas); color:var(--ink);
  font-family:Manrope,'Helvetica Neue',Arial,sans-serif;
  font-size:18px; line-height:1.7; font-weight:400;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline}
/* links inside running text get an underline so color is not the only cue (WCAG 1.4.1) */
.body a,.short-answer a,.hero p a,.lede a,.post-cta a,.tile p a,.author-box a,.sources a,.toc a,
.contact-form .fine a,.foot-sub .fine a,.site-foot .disclaimer a{text-decoration:underline; text-underline-offset:.15em}
:focus-visible{outline:2px solid var(--accent); outline-offset:2px}
.sr-only{position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0}
img{max-width:100%; height:auto; display:block}
.wrap{width:100%; max-width:64rem; margin:0 auto; padding:0 1.5rem}
.skip{position:absolute; left:-999px; top:0; background:var(--accent); color:#000; padding:.5rem 1rem}
.skip:focus{left:1rem; z-index:10}

/* header */
.site-head{border-bottom:1px solid var(--faint)}
.site-head .wrap{display:flex; align-items:center; justify-content:space-between;
  gap:1rem; padding-top:1.1rem; padding-bottom:1.1rem; flex-wrap:wrap}
.brand{display:flex; align-items:center; flex:none}
.brand:hover{text-decoration:none}
.brand img{height:34px; width:auto; display:block}
nav.main{display:flex; gap:1.3rem; font-size:.95rem; font-weight:600; flex-wrap:wrap}
nav.main a{color:var(--muted)}
nav.main a:hover,nav.main a[aria-current]{color:var(--ink); text-decoration:none}
.menu-btn{display:none; background:none; border:1px solid var(--faint); border-radius:10px;
  color:var(--ink); padding:.45rem .6rem; cursor:pointer; line-height:0}
.menu-btn svg{width:22px; height:22px; display:block}
.menu-btn .x{display:none}
.site-head.open .menu-btn .bars{display:none}
.site-head.open .menu-btn .x{display:block}
@media (max-width:720px){
  .site-head .wrap{flex-wrap:nowrap}
  .menu-btn{display:block}
  nav.main{display:none; flex-basis:100%; flex-direction:column; gap:0; padding:.4rem 0 .6rem}
  nav.main a{padding:.7rem 0; border-top:1px solid var(--faint); font-size:1.05rem}
  .site-head.open .wrap{flex-wrap:wrap}
  .site-head.open nav.main{display:flex}
  .menu-btn[hidden]{display:none}
  .menu-btn[hidden]~nav.main{display:flex}
}

/* hero */
.hero{padding:4.5rem 0 2.5rem; border-bottom:1px solid var(--faint)}
.hero h1{font-size:clamp(2rem,5vw,3.1rem); line-height:1.08; letter-spacing:-.03em;
  font-weight:800; margin:0 0 1rem; max-width:22ch}
.hero p{font-size:1.2rem; color:var(--muted); margin:0 0 .8rem; max-width:52ch}
.hero p.promise{color:var(--ink); font-size:1.05rem; max-width:60ch}
.hero .accent{color:var(--accent)}
.hero.has-photo .wrap{display:grid; grid-template-columns:minmax(0,1fr) 16rem; gap:3rem; align-items:center}
.hero-photo{margin:0; width:16rem; justify-self:end; isolation:isolate}
.hero-photo img{display:block; width:100%; height:auto; border-radius:14px; background:var(--panel);
  border:1px solid var(--faint);
  box-shadow:12px 12px 0 -1px var(--canvas), 12px 12px 0 0 var(--accent)}
.hero-photo figcaption{margin:1.6rem 0 0; color:var(--muted); font-size:.9rem;
  line-height:1.5; display:flex; gap:.6rem; align-items:baseline}
.hero-photo figcaption::before{content:""; flex:none; width:.5rem; height:.5rem;
  border-radius:50%; background:var(--accent); transform:translateY(-.05rem)}
@media (max-width:820px){
  .hero.has-photo .wrap{grid-template-columns:1fr; gap:1.6rem}
  .hero-photo{width:11rem; justify-self:start; order:-1}
  .hero-photo img{box-shadow:9px 9px 0 -1px var(--canvas), 9px 9px 0 0 var(--accent)}
  .hero-photo figcaption{margin-top:1.2rem}
}

/* section headings + topic tiles */
.section-title{font-size:.82rem; color:var(--muted); font-weight:700; text-transform:uppercase;
  letter-spacing:.1em; margin:0 0 1rem}
.featured{padding:2.5rem 0 1rem}
.tiles{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; margin:0 0 1rem}
.tile{display:block; padding:1.2rem 1.3rem; border:1px solid var(--faint); border-radius:14px;
  background:var(--panel); color:var(--ink)}
.tile:hover{text-decoration:none; border-color:var(--accent)}
.tile h2,.tile h3{margin:0 0 .3rem; font-size:1.15rem; font-weight:800; letter-spacing:-.01em}
.tile p{margin:0; color:var(--muted); font-size:.95rem}
.tile .count{color:var(--accent); font-size:.8rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em}
.tile h2 a,.tile h3 a{color:var(--ink)}
.tile h2 a:hover,.tile h3 a:hover{color:var(--accent); text-decoration:none}
.tile .start{margin:.9rem 0 0; padding-top:.8rem; border-top:1px solid var(--faint); font-size:.92rem}
.tile .start span{display:block; color:var(--muted); font-size:.72rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.08em; margin-bottom:.15rem}
.tile .start a{color:var(--ink); font-weight:700}
.tile .start a:hover{color:var(--accent); text-decoration:none}
@media (max-width:720px){.tiles{grid-template-columns:1fr}}

/* post list */
.list{padding:2rem 0 4rem}
.post-card{display:block; padding:1.6rem 0; border-bottom:1px solid var(--faint);
  color:var(--ink)}
.post-card:hover{text-decoration:none}
.post-card:hover h2,.post-card:hover h3{color:var(--accent)}
.post-card .meta{font-size:.82rem; color:var(--muted); font-weight:600;
  text-transform:uppercase; letter-spacing:.08em; margin-bottom:.5rem;
  display:flex; gap:.7rem; align-items:center; flex-wrap:wrap}
.tag{color:var(--accent); border:1px solid var(--faint); border-radius:999px;
  padding:.05rem .55rem; font-size:.72rem}
a.tag:hover{border-color:var(--accent); text-decoration:none}
.post-card h2,.post-card h3{font-size:1.5rem; line-height:1.2; letter-spacing:-.02em;
  font-weight:800; margin:0 0 .35rem; transition:color .15s}
.post-card p{margin:0; color:var(--muted); font-size:1rem; max-width:60ch}

.more{margin:1.5rem 0 0; font-weight:700}
.page .tiles{margin-top:.2rem}

/* article */
.article{padding:2.5rem 0 4rem}
.crumbs{margin:0 0 1.4rem; font-size:.82rem; color:var(--muted)}
.crumbs ol{list-style:none; margin:0; padding:0; display:flex; gap:.5rem; flex-wrap:wrap}
.crumbs li+li::before{content:"\\203A"; content:"\\203A" / ""; margin-right:.5rem; color:var(--muted)}
.crumbs a{color:var(--muted)}
.crumbs a:hover{color:var(--ink)}
.article-head{max-width:var(--measure); margin:0 auto 2rem}
.article-head .meta{font-size:.82rem; color:var(--muted); font-weight:600;
  text-transform:uppercase; letter-spacing:.08em; margin-bottom:.9rem;
  display:flex; gap:.7rem; align-items:center; flex-wrap:wrap}
.article-head .meta a{color:var(--muted)}
.article-head .meta a:hover{color:var(--ink)}
.article-head h1{font-size:clamp(1.9rem,4.5vw,2.7rem); line-height:1.12;
  letter-spacing:-.03em; font-weight:800; margin:0 0 .6rem}
.article-head .subtitle{font-size:1.25rem; color:var(--muted); margin:0}
.short-answer{max-width:var(--measure); margin:0 auto 2rem; padding:1.2rem 1.4rem;
  border-left:3px solid var(--accent); background:var(--panel); border-radius:0 14px 14px 0}
.short-answer .label{display:flex; align-items:center; gap:.6rem; font-size:.78rem; font-weight:800;
  letter-spacing:.1em; text-transform:uppercase; color:var(--accent); margin-bottom:.5rem}
.short-answer .avatar{width:36px; height:36px; border-radius:50%; border:2px solid var(--accent); flex:none}
.short-answer p{margin:0; font-size:1.05rem}
.hero-img{max-width:var(--measure); margin:0 auto 2.5rem; border-radius:14px;
  overflow:hidden; background:var(--panel); border:1px solid var(--faint)}
.body{max-width:var(--measure); margin:0 auto}
.body h2{font-size:1.45rem; letter-spacing:-.02em; font-weight:800;
  margin:2.4rem 0 .6rem; line-height:1.25}
.body h3{font-size:1.15rem; font-weight:700; margin:1.8rem 0 .4rem}
.body p{margin:0 0 1.15rem}
.body ul,.body ol{margin:0 0 1.15rem; padding-left:1.2rem}
.body li{margin:.3rem 0}
.body strong{font-weight:700}
.body code{background:var(--panel); padding:.1rem .35rem; border-radius:5px;
  font-size:.9em}
.body blockquote{margin:0 0 1.15rem; padding:.2rem 0 .2rem 1.1rem; border-left:3px solid var(--accent);
  color:var(--muted)}
.body blockquote p{margin:0}
.body hr.rule{border:none; height:1px; background:var(--faint); margin:2.2rem 0}
.body h2:target,.body h3:target{color:var(--accent)}

/* table of contents (FAQ page) */
.toc{max-width:var(--measure); margin:0 0 2rem; padding:1rem 1.3rem; border:1px solid var(--faint); border-radius:14px;
  background:var(--panel); font-size:.95rem}
.toc strong{display:block; margin-bottom:.4rem; font-size:.78rem; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted)}
.toc ol{margin:0; padding-left:1.2rem}
.toc li{margin:.15rem 0}

/* author box, related, pager, CTA */
.author-box{max-width:var(--measure); margin:2.5rem auto 0; padding:1.4rem 1.6rem;
  border:1px solid var(--faint); border-radius:14px; display:flex; gap:1.2rem; align-items:flex-start}
.author-box img{width:72px; height:72px; border-radius:50%; object-fit:cover; object-position:center 35%;
  flex:none; background:var(--faint); border:1px solid var(--faint)}
.author-box .name{font-weight:800; margin:0 0 .2rem; font-size:1rem}
.author-box p{margin:0; color:var(--muted); font-size:.95rem}
.related{max-width:var(--measure); margin:2.5rem auto 0}
.related h2{font-size:.82rem; color:var(--muted); font-weight:700; text-transform:uppercase;
  letter-spacing:.1em; margin:0 0 .6rem}
.related ul{list-style:none; margin:0; padding:0}
.related li{padding:.7rem 0; border-top:1px solid var(--faint)}
.related li:last-child{border-bottom:1px solid var(--faint)}
.related a{font-weight:700; color:var(--ink)}
.related a:hover{color:var(--accent); text-decoration:none}
.related span{display:block; color:var(--muted); font-size:.92rem}
.sources{max-width:var(--measure); margin:2.5rem auto 0}
.sources h2{font-size:.82rem; color:var(--muted); font-weight:700; text-transform:uppercase;
  letter-spacing:.1em; margin:0 0 .4rem}
.sources > p{margin:0 0 .6rem; color:var(--muted); font-size:.92rem}
.sources ol{margin:0; padding-left:1.25rem; font-size:.95rem}
.sources li{padding:.3rem 0; color:var(--muted)}
.sources a{font-weight:700; color:var(--ink)}
.sources a:hover{color:var(--accent)}
.pager{max-width:var(--measure); margin:2rem auto 0; display:flex; justify-content:space-between;
  gap:1rem; font-size:.95rem}
.pager a{color:var(--muted); max-width:48%}
.pager a:hover{color:var(--ink)}
.pager small{display:block; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em}
.post-cta{max-width:var(--measure); margin:2.5rem auto 0; padding:1.8rem;
  border:1px solid var(--faint); border-radius:14px; background:var(--panel)}
.post-cta h2{margin:0 0 .4rem; font-size:1.2rem; font-weight:800; letter-spacing:-.01em}
.post-cta p{margin:0; color:var(--muted); font-size:1rem}

/* generic page */
.page{padding:3rem 0 4rem}
.page .body{max-width:var(--measure); margin-left:0; margin-right:0}
.page h1{font-size:clamp(1.9rem,4.5vw,2.6rem); letter-spacing:-.03em; font-weight:800;
  margin:0 0 1.4rem}
.page .lede{font-size:1.2rem; color:var(--muted); max-width:var(--measure); margin:-.6rem 0 1.8rem}

/* contact form */
.contact-form{max-width:var(--measure); margin:2rem 0 0; padding:1.6rem; border:1px solid var(--faint);
  border-radius:14px; background:var(--panel)}
.contact-form h2{margin:0 0 1rem; font-size:1.2rem; font-weight:800; letter-spacing:-.01em}
.contact-form label{display:block; font-size:.85rem; font-weight:700; color:var(--muted);
  text-transform:uppercase; letter-spacing:.08em; margin:1rem 0 .35rem}
.contact-form label:first-of-type{margin-top:0}
.contact-form input,.contact-form select,.contact-form textarea{width:100%; font:inherit; color:var(--ink);
  background:var(--canvas); border:1px solid var(--faint); border-radius:10px; padding:.7rem .85rem}
.contact-form input:focus,.contact-form select:focus,.contact-form textarea:focus{outline:2px solid var(--accent); outline-offset:2px; border-color:var(--accent)}
.contact-form .required-note{margin:0 0 .4rem; font-size:.85rem; color:var(--muted)}
.contact-form textarea{min-height:9rem; resize:vertical}
.contact-form select{appearance:none; -webkit-appearance:none; background-image:linear-gradient(45deg,transparent 50%,var(--muted) 50%),linear-gradient(135deg,var(--muted) 50%,transparent 50%);
  background-position:calc(100% - 20px) 50%,calc(100% - 14px) 50%; background-size:6px 6px; background-repeat:no-repeat; padding-right:2.4rem}
.contact-form .hp{position:absolute; left:-9999px; width:1px; height:1px; overflow:hidden}
.contact-form button{margin-top:1.3rem; font:inherit; font-weight:800; color:#0F0F0F; background:var(--accent);
  border:none; border-radius:999px; padding:.8rem 1.6rem; cursor:pointer}
.contact-form button:hover{filter:brightness(1.08)}
.contact-form .fine{margin:.9rem 0 0; font-size:.85rem; color:var(--muted)}

/* about page: text + family photo */
.about .wrap{display:grid; grid-template-columns:minmax(0,1fr) 21rem; gap:3.5rem;
  align-items:start}
.about .body{max-width:var(--measure)}
.about-photo{margin:.4rem 0 0; isolation:isolate}
.about-photo img{width:100%; border-radius:14px; background:var(--panel);
  border:1px solid var(--faint);
  box-shadow:16px 16px 0 -1px var(--canvas), 16px 16px 0 0 var(--accent)}
.about-photo figcaption{margin:2rem 0 0; color:var(--muted); font-size:.9rem;
  line-height:1.5; display:flex; gap:.6rem; align-items:baseline}
.about-photo figcaption::before{content:""; flex:none; width:.5rem; height:.5rem;
  border-radius:50%; background:var(--accent); transform:translateY(-.05rem)}
@media (max-width:820px){
  .about .wrap{grid-template-columns:1fr; gap:2.2rem}
  .about-photo{order:-1; max-width:20rem}
  .about-photo figcaption{margin-top:1.6rem}
}

/* footer */
.site-foot{border-top:1px solid var(--faint); padding:2.5rem 0; color:var(--muted);
  font-size:.9rem}
.site-foot .wrap{display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap}
.site-foot a{color:var(--muted)}
.site-foot a:hover{color:var(--ink)}
.site-foot .disclaimer{width:100%; font-size:.82rem}
.foot-sub{width:100%; margin:0 0 1.4rem; padding:0 0 1.6rem; border-bottom:1px solid var(--faint)}
.foot-sub .label{display:block; font-weight:800; color:var(--ink); font-size:1rem; margin:0 0 .6rem}
.foot-sub .row{display:flex; gap:.5rem; max-width:26rem}
.foot-sub .embed{max-width:26rem; min-height:3rem}
.foot-sub .embed iframe{display:block; width:100%; border:0}
.foot-sub input[type=email]{flex:1; min-width:0; font:inherit; color:var(--ink); background:var(--canvas);
  border:1px solid var(--faint); border-radius:999px; padding:.6rem 1rem}
.foot-sub input[type=email]:focus{outline:2px solid var(--accent); outline-offset:2px; border-color:var(--accent)}
.foot-sub button{font:inherit; font-weight:800; color:#0F0F0F; background:var(--accent); border:none;
  border-radius:999px; padding:.6rem 1.1rem; cursor:pointer; white-space:nowrap}
.foot-sub button:hover{filter:brightness(1.08)}
.foot-sub .fine{margin:.5rem 0 0; font-size:.8rem}
.foot-sub .hp{position:absolute; left:-9999px; width:1px; height:1px; overflow:hidden}

@media (max-width:640px){
  body{font-size:17px}
  .hero{padding:3rem 0 1.6rem}
  nav.main{gap:.9rem; font-size:.9rem}
  .brand img{height:28px}
  .author-box{flex-direction:column}
}
"""

MENU_SCRIPT = """<script>
(function(){var h=document.querySelector('.site-head'),b=h.querySelector('.menu-btn');if(!b)return;b.hidden=false;
function set(o){h.classList.toggle('open',o);b.setAttribute('aria-expanded',o);b.setAttribute('aria-label',o?'Close menu':'Open menu');}
b.addEventListener('click',function(){set(!h.classList.contains('open'));});
h.addEventListener('keydown',function(e){if(e.key==='Escape'&&h.classList.contains('open')){set(false);b.focus();}});})();
</script>"""

CSS_VERSION = hashlib.md5(CSS.encode("utf-8")).hexdigest()[:8]

NAV = [("/start-here/", "Start Here"), ("/blog/", "Blog"), ("/faq/", "FAQ"),
       ("/about/", "About"), ("/contact/", "Contact")]


def fmt_date(d):
    return f'{MONTHS[d.month]} {d.day}, {d.year}'


def json_ld(data):
    txt = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/ld+json">{txt}</script>'


def org_schema():
    return {
        "@type": "Organization",
        "@id": f"{SITE_URL}/#organization",
        "name": SITE_NAME,
        "url": SITE_URL + "/",
        "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/assets/og-default.png",
                 "width": 1200, "height": 630},
        "founder": {"@id": f"{SITE_URL}/#david"},
        "description": HOME_DESC,
        "contactPoint": {"@type": "ContactPoint", "contactType": "customer support",
                         "url": f"{SITE_URL}/contact/", "availableLanguage": "English"},
    }


def person_schema(full=False):
    p = {
        "@type": "Person",
        "@id": f"{SITE_URL}/#david",
        "name": AUTHOR,
        "url": AUTHOR_URL,
        "jobTitle": "Writer and founder, Normaltown USA",
        "description": AUTHOR_BIO,
        "image": f"{SITE_URL}/about/david-dewese-round.png",
        "worksFor": {"@id": f"{SITE_URL}/#organization"},
        "knowsAbout": ["personal finance for families", "medical bills", "health insurance",
                       "health sharing", "CrowdHealth", "cash prices for medical care",
                       "bitcoin as savings", "inflation"],
    }
    if full:
        p["mainEntityOfPage"] = AUTHOR_URL
    return p


def website_schema():
    return {
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": SITE_URL + "/",
        "name": SITE_NAME,
        "description": HOME_DESC,
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "inLanguage": "en-US",
    }


def ga_tag():
    """Google Analytics 4. Loads on every page; only reports from the real hostname so
    local previews don't show up as visits."""
    if not GA_ID:
        return ""
    return ('<script async src="https://www.googletagmanager.com/gtag/js?id=' + GA_ID + '"></script>\n'
            "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            "gtag('js',new Date());if(!/^(localhost|127\\.0\\.0\\.1)$/.test(location.hostname))"
            "gtag('config','" + GA_ID + "');</script>\n")


def footer_signup():
    """Minimal email signup for the site footer. Uses the beehiiv embed when
    NEWSLETTER_EMBED is set; otherwise a FormSubmit form that emails each signup to
    CONTACT_EMAIL (same free endpoint as the contact form) and lands on /subscribed/."""
    if NEWSLETTER_EMBED.strip():
        return f"""<div class="foot-sub">
    <span class="label" id="s-label">New posts by email</span>
    <div class="embed" role="group" aria-labelledby="s-label" aria-describedby="s-hint">{NEWSLETTER_EMBED}</div>
    <p class="fine" id="s-hint">Enter your email address above. No spam, no selling your address. Leave anytime.</p>
  </div>
  <script>(function(){{var e=document.querySelector('.foot-sub .embed');if(!e)return;function t(){{var f=e.querySelector('iframe');if(f&&!f.title)f.title='Email signup form';}}t();new MutationObserver(t).observe(e,{{childList:true,subtree:true}});}})();</script>"""
    import base64
    target = base64.b64encode(f"https://formsubmit.co/{CONTACT_EMAIL}".encode()).decode()
    return f"""<form class="foot-sub" method="POST" data-t="{target}">
    <input type="hidden" name="_subject" value="Normaltown USA: new email signup">
    <input type="hidden" name="_template" value="table">
    <input type="hidden" name="_captcha" value="false">
    <input type="hidden" name="_next" value="{SITE_URL}/subscribed/">
    <div class="hp" aria-hidden="true"><label for="s-honey">Leave this empty</label><input type="text" id="s-honey" name="_honey" tabindex="-1" autocomplete="off"></div>
    <label class="label" for="s-email">New posts by email</label>
    <div class="row"><input type="email" id="s-email" name="email" required autocomplete="email" placeholder="you@example.com"><button type="submit">Sign up</button></div>
    <p class="fine">No spam, no selling your address. Leave anytime.</p>
  </form>
  <script>(function(){{var f=document.querySelector('form.foot-sub');if(f)f.action=atob(f.getAttribute('data-t'));}})();</script>"""


def layout(title, description, body, canonical, og_image=None, og_type="article",
           schema=None, current=None, extra_head="", og_size=None, page_title=None,
           section=None):
    desc = html.escape(description or SITE_TAGLINE, quote=True)
    ga, signup = ga_tag(), footer_signup()
    if page_title is None:
        page_title = title if title == SITE_NAME else f"{title} | {SITE_NAME}"
    og_image = og_image or f"{SITE_URL}/assets/og-default.png"
    w, h = og_size or ((1200, 630) if og_image.endswith("og-default.png") else (1200, 1200))
    og_img = html.escape(og_image, quote=True)
    nav_items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else (' aria-current="true"' if href == section else "")
        nav_items.append(f'    <a href="{href}"{cur}>{label}</a>')
    nav = "\n".join(nav_items)
    graph = {"@context": "https://schema.org", "@graph": schema} if schema else None
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>if(/\.(workers|pages)\.dev$/.test(location.hostname)||location.hostname==="normaltownusa.com")location.replace("{SITE_URL}"+location.pathname+location.search+location.hash);</script>
{ga}<title>{html.escape(page_title)}</title>
<meta name="description" content="{desc}">
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#0F0F0F">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="{w}">
<meta property="og:image:height" content="{h}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title, quote=True)}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
{extra_head}<link rel="icon" type="image/svg+xml" href="/assets/normaltown-icon.svg">
<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css?v={CSS_VERSION}">
{json_ld(graph) if graph else ""}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap">
  <a class="brand" href="/" aria-label="{SITE_NAME} home"><img src="/assets/normaltown-logo-reverse.svg" alt="{SITE_NAME}" width="1132" height="156"></a>
  <button class="menu-btn" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="main-nav" hidden>
    <svg class="bars" aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
    <svg class="x" aria-hidden="true" focusable="false" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
  </button>
  <nav class="main" id="main-nav" aria-label="Main">
{nav}
  </nav>
</div></header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="site-foot"><div class="wrap">
  {signup}
  <span>&copy; {TODAY.year} {SITE_NAME}. {SITE_TAGLINE}.</span>
  <span><a href="/blog/">All posts</a> &middot; <a href="/money/">Money</a> &middot; <a href="/health/">Health</a> &middot; <a href="/bitcoin/">Bitcoin</a> &middot; <a href="/start-here/">Start Here</a> &middot; <a href="/faq/">FAQ</a> &middot; <a href="/about/">About</a> &middot; <a href="/contact/">Contact</a> &middot; <a href="/accessibility/">Accessibility</a> &middot; <a href="/rss.xml">RSS</a></span>
  <p class="disclaimer">Written by {AUTHOR}, a regular guy who does the homework, not a financial advisor, doctor, tax pro, or lawyer. Nothing here is financial, medical, tax, or legal advice. Some links (CrowdHealth, code NORMAL) pay a referral bonus at no extra cost to you. Health sharing is not insurance.</p>
</div></footer>
{MENU_SCRIPT}
</body>
</html>"""


POST_CTA = """<div class="post-cta">
  <h2>New here?</h2>
  <p>Normaltown USA is plain-English money and healthcare help for normal people, written by a regular guy with a family of four. No jargon, no hype. <a href="/start-here/">Start here</a>, or read the <a href="/faq/">FAQ</a>.</p>
</div>"""


def post_card(p, heading="h2"):
    cat = CATEGORIES[p["category"]]
    return f"""<a class="post-card" href="/p/{p['slug']}/">
          <div class="meta"><span class="tag">{cat['name']}</span><span>{fmt_date(p['date'])}</span><span>{p['minutes']} min read</span></div>
          <{heading}>{html.escape(p['title'])}</{heading}>
          <p>{html.escape(p['meta'] or '')}</p>
        </a>"""


def by_slug(posts):
    return {p["slug"]: p for p in posts}


START_HERE_SLUGS = ["nobody-gets-paid-to-make-you-well", "why-you-feel-broke-on-a-good-income",
                    "is-bitcoin-saving-or-gambling"]


def render_home(posts):
    lookup = by_slug(posts)
    photo = ""
    if HOME_HERO.exists():
        srcset = "/about/david-dewese-hero.jpg 659w"
        if HOME_HERO_SM.exists():
            srcset = "/about/david-dewese-hero-400.jpg 400w, " + srcset
        photo = f"""<figure class="hero-photo"><img src="/about/david-dewese-hero-400.jpg" srcset="{srcset}"
        sizes="(max-width:820px) 11rem, 16rem" alt="{html.escape(HOME_HEADSHOT_ALT, quote=True)}" width="659" height="850" fetchpriority="high">
        <figcaption>{html.escape(HOME_HEADSHOT_CAPTION)}</figcaption></figure>"""
    hero = f"""<section class="hero{' has-photo' if photo else ''}"><div class="wrap">
      <div class="hero-copy">
      <h1>Money &amp; health insurance, <span class="accent">explained in plain English</span>.</h1>
      <p>Why you feel broke on a good income, how to beat the rising cost of health insurance, and how to save in something that holds its value. Written by a normal family guy with a regular job, for normal people with regular jobs. One idea per post, short enough to read with your coffee.</p>
      <p class="promise">Read for a month and you'll know how to ask for the cash price on a medical bill, plug the leaks in your paycheck, and build your first $1,000 cushion. Almost nobody teaches this, because almost nobody gets paid to.</p>
      </div>
      {photo}
    </div></section>"""
    # One topic tile per category, each with a "Start with" link to that topic's
    # cornerstone post (the START_HERE_SLUGS, one per category).
    start_with = {lookup[s]["category"]: lookup[s] for s in START_HERE_SLUGS if s in lookup}
    counts = {k: sum(1 for p in posts if p["category"] == k) for k in CATEGORIES}
    tile_html = []
    for k, c in CATEGORIES.items():
        desc = c.get("blurb") or c["description"]
        first = start_with.get(k)
        start = (f'<p class="start"><span>Start with</span> <a href="/p/{first["slug"]}/">{html.escape(first["title"])}</a></p>'
                 if first else "")
        tile_html.append(f'<div class="tile"><span class="count">{c["name"]} &middot; {counts[k]} posts</span>'
                         f'<h3><a href="/{k}/">{html.escape(c["title"])}</a></h3><p>{html.escape(desc)}</p>{start}</div>')
    feat_html = ""
    tiles = ('<section class="featured"><div class="wrap"><h2 class="section-title">New here? Pick a topic</h2>'
             '<div class="tiles">' + "".join(tile_html) + '</div></div></section>')
    cards = "\n".join(post_card(p, heading="h3") for p in posts[:10])
    more = f'<p class="more"><a href="/blog/">See all {len(posts)} posts</a></p>' if len(posts) > 10 else ""
    body = hero + feat_html + tiles + f'<section class="list"><div class="wrap"><h2 class="section-title">Latest posts</h2>{cards}{more}</div></section>'
    schema = [website_schema(), org_schema(), person_schema(),
              {"@type": "CollectionPage", "@id": f"{SITE_URL}/#home", "url": SITE_URL + "/",
               "name": HOME_TITLE, "description": HOME_DESC,
               "isPartOf": {"@id": f"{SITE_URL}/#website"},
               "hasPart": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"],
                            "datePublished": p["date"].isoformat()} for p in posts[:20]]}]
    return layout(SITE_NAME, HOME_DESC, body, SITE_URL + "/", og_type="website",
                  schema=schema, current="/", page_title=HOME_TITLE)


BLOG_TITLE = "All Posts: Plain-English Money, Medical Bills, Health Sharing, and Bitcoin"
BLOG_DESC = ("Every Normaltown USA post, newest first: money for normal people, medical bills and "
             "health sharing, and bitcoin as savings. Short, first-person, one idea each.")


def render_blog(posts):
    counts = {k: sum(1 for p in posts if p["category"] == k) for k in CATEGORIES}
    tiles = '<h2 class="section-title">Pick a topic</h2><div class="tiles">' + "".join(
        f'<a class="tile" href="/{k}/"><span class="count">{counts[k]} posts</span><h3>{html.escape(c["title"])}</h3><p>{html.escape(c["description"].split(":")[0] if ":" in c["description"] else c["description"])}</p></a>'
        for k, c in CATEGORIES.items()) + '</div>'
    cards = "\n".join(post_card(p, heading="h3") for p in posts)
    body = f"""<section class="page"><div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">Blog</li></ol></nav>
      <h1>All posts</h1>
      <p class="lede">One idea per post, short enough to read with your coffee. Newest first, or pick a topic.</p>
      {tiles}
      <h2 class="section-title" style="margin-top:2rem">{len(posts)} posts, newest first</h2>
      {cards}
    </div></section>"""
    schema = [website_schema(), org_schema(),
              {"@type": "CollectionPage", "@id": f"{SITE_URL}/blog/#page", "url": f"{SITE_URL}/blog/",
               "name": BLOG_TITLE, "description": BLOG_DESC,
               "isPartOf": {"@id": f"{SITE_URL}/#website"},
               "hasPart": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"],
                            "datePublished": p["date"].isoformat()} for p in posts]}]
    return layout("Blog", BLOG_DESC, body, f"{SITE_URL}/blog/", og_type="website",
                  schema=schema, current="/blog/", page_title=f"{BLOG_TITLE} | {SITE_NAME}")


def render_hub(key, posts):
    c = CATEGORIES[key]
    mine = [p for p in posts if p["category"] == key]
    cards = "\n".join(post_card(p, heading="h3") for p in mine)
    body = f"""<section class="page"><div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">{c['name']}</li></ol></nav>
      <h1>{html.escape(c['title'])}</h1>
      <p class="lede">{html.escape(c['intro'])}</p>
      <h2 class="section-title">{len(mine)} posts, newest first</h2>
      {cards}
    </div></section>"""
    schema = [website_schema(), org_schema(),
              {"@type": "CollectionPage", "@id": f"{SITE_URL}/{key}/#page", "url": f"{SITE_URL}/{key}/",
               "name": c["page_title"], "description": c["description"],
               "isPartOf": {"@id": f"{SITE_URL}/#website"},
               "breadcrumb": {"@id": f"{SITE_URL}/{key}/#crumbs"},
               "hasPart": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"],
                            "datePublished": p["date"].isoformat()} for p in mine]},
              {"@type": "BreadcrumbList", "@id": f"{SITE_URL}/{key}/#crumbs", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
                  {"@type": "ListItem", "position": 2, "name": c["name"], "item": f"{SITE_URL}/{key}/"}]}]
    return layout(c["title"], c["description"], body, f"{SITE_URL}/{key}/", og_type="website",
                  schema=schema, section="/blog/", page_title=f"{c['page_title']} | {SITE_NAME}")


def related_posts(p, posts, n=3):
    lookup = by_slug(posts)
    picks = []
    for s in p["links"]:
        if s in lookup and s != p["slug"] and lookup[s] not in picks:
            picks.append(lookup[s])
    same = [q for q in posts if q["category"] == p["category"] and q["slug"] != p["slug"] and q not in picks]
    same.sort(key=lambda q: abs((q["date"] - p["date"]).days))
    picks += same
    if len(picks) < n:
        picks += [q for q in posts if q["slug"] != p["slug"] and q not in picks]
    return picks[:n]


def render_post(p, posts):
    canonical = p["url"]
    cat = CATEGORIES[p["category"]]
    subtitle = f'<p class="subtitle">{html.escape(p["subtitle"])}</p>' if p["subtitle"] else ""
    hero_img, og_image = "", None
    if p["png_name"]:
        hero_img = f'<figure class="hero-img"><img src="{p["png_name"]}" alt="{html.escape(p["alt"], quote=True)}" width="1200" height="1200" fetchpriority="high"></figure>'
        og_image = f"{canonical}{p['png_name']}"
    short = ""
    if p["short"]:
        avatar = ('<img class="avatar" src="/about/david-dewese-round-96.png" alt="" width="36" height="36">'
                  if HOME_HEADSHOT_XS.exists() else "")
        short = f'<div class="short-answer"><span class="label">{avatar}In short</span><p>{_inline(p["short"])}</p></div>'
    updated = ""
    if p["modified"] > p["date"]:
        updated = f'<span>Updated <time datetime="{p["modified"].isoformat()}">{fmt_date(p["modified"])}</time></span>'

    sources_html = ""
    if p["sources"]:
        items = "".join(
            f'<li><a href="{html.escape(u, quote=True)}" target="_blank" rel="noopener">{html.escape(l)}{NEW_TAB}</a>'
            + (f' <span>{html.escape(n)}.</span>' if n else "") + "</li>"
            for l, u, n in p["sources"])
        sources_html = (f'<section class="sources" id="sources"><h2>Sources</h2>'
                        f'<p>Where I checked the numbers and claims in this post.</p><ol>{items}</ol></section>')

    rel = related_posts(p, posts)
    related = ""
    if rel:
        related = '<section class="related"><h2>Read next</h2><ul>' + "".join(
            f'<li><a href="/p/{q["slug"]}/">{html.escape(q["title"])}</a><span>{html.escape(q["meta"] or "")}</span></li>'
            for q in rel) + '</ul></section>'

    # prev = older, next = newer (posts is newest-first)
    idx = next(i for i, q in enumerate(posts) if q["slug"] == p["slug"])
    older = posts[idx + 1] if idx + 1 < len(posts) else None
    newer = posts[idx - 1] if idx > 0 else None
    pager = ""
    if older or newer:
        o = f'<a href="/p/{older["slug"]}/" rel="prev"><small>Older</small>{html.escape(older["title"])}</a>' if older else "<span></span>"
        nw = f'<a href="/p/{newer["slug"]}/" rel="next" style="text-align:right"><small>Newer</small>{html.escape(newer["title"])}</a>' if newer else "<span></span>"
        pager = f'<nav class="pager" aria-label="Older and newer posts">{o}{nw}</nav>'

    author_box = f"""<div class="author-box">
        <img src="/about/david-dewese-240.png" alt="" width="72" height="72" loading="lazy">
        <div><p class="name">Written by <a href="/about/">{AUTHOR}</a></p>
        <p>{html.escape(AUTHOR_BIO)} <a href="/about/">More about me</a>.</p></div>
      </div>"""

    body = f"""<article class="article"><div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li><a href="/{p['category']}/">{cat['name']}</a></li><li aria-current="page">{html.escape(p['title'])}</li></ol></nav>
      <div class="article-head">
        <div class="meta"><a class="tag" href="/{p['category']}/">{cat['name']}</a><span><time datetime="{p['date'].isoformat()}">{fmt_date(p['date'])}</time></span>{updated}<span>by <a href="/about/" rel="author">{AUTHOR}</a></span><span>{p['minutes']} min read</span></div>
        <h1>{html.escape(p['title'])}</h1>
        {subtitle}
      </div>
      {short}
      {hero_img}
      <div class="body">{p['body_html']}</div>
      {sources_html}
      {author_box}
      {related}
      {pager}
      {POST_CTA}
    </div></article>"""

    article = {
        "@type": "BlogPosting",
        "@id": f"{canonical}#article",
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "url": canonical,
        "headline": p["title"],
        "description": p["meta"],
        "datePublished": f"{p['date'].isoformat()}T09:00:00-04:00",
        "dateModified": f"{p['modified'].isoformat()}T09:00:00-04:00",
        "author": {"@id": f"{SITE_URL}/#david"},
        "publisher": {"@id": f"{SITE_URL}/#organization"},
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "articleSection": cat["name"],
        "inLanguage": "en-US",
        "wordCount": p["words"],
        "isAccessibleForFree": True,
    }
    if p["short"]:
        article["abstract"] = plain_text(p["short"])
    if og_image:
        article["image"] = {"@type": "ImageObject", "url": og_image, "width": 1200, "height": 1200}
    if p["subtitle"]:
        article["alternativeHeadline"] = p["subtitle"]
    if p["affiliate"]:
        article["mentions"] = {"@type": "Organization", "name": "CrowdHealth", "url": "https://www.joincrowdhealth.com/"}
    if p["sources"]:
        article["citation"] = [{"@type": "CreativeWork", "name": l, "url": u} for l, u, _ in p["sources"]]
    schema = [article, person_schema(), org_schema(), website_schema(),
              {"@type": "BreadcrumbList", "@id": f"{canonical}#crumbs", "itemListElement": [
                  {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
                  {"@type": "ListItem", "position": 2, "name": cat["name"], "item": f"{SITE_URL}/{p['category']}/"},
                  {"@type": "ListItem", "position": 3, "name": p["title"], "item": canonical}]}]
    if p["faqs"]:
        schema.append({"@type": "FAQPage", "@id": f"{canonical}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in p["faqs"]]})
    extra = (f'<meta property="article:published_time" content="{p["date"].isoformat()}">\n'
             f'<meta property="article:modified_time" content="{p["modified"].isoformat()}">\n'
             f'<meta property="article:author" content="{AUTHOR_URL}">\n'
             f'<meta property="article:section" content="{cat["name"]}">\n')
    if older:
        extra += f'<link rel="prev" href="{older["url"]}">\n'
    if newer:
        extra += f'<link rel="next" href="{newer["url"]}">\n'
    page_title = f"{p['title_tag'] or p['title']} | {SITE_NAME}"
    return layout(p["title"], p["meta"], body, canonical, og_image=og_image, schema=schema,
                  section="/blog/", extra_head=extra, page_title=page_title)


def contact_form():
    """Static form posted to FormSubmit (free, no account): the first submission
    triggers a one-time activation email to CONTACT_EMAIL; after that, messages
    land in that inbox with the sender's address as reply-to."""
    import base64
    target = base64.b64encode(f"https://formsubmit.co/{CONTACT_EMAIL}".encode()).decode()
    return f"""<form class="contact-form" method="POST" data-t="{target}">
        <h2>Send a message</h2>
        <p class="required-note">Every field is required except the topic.</p>
        <noscript><p class="fine">Turn on JavaScript to send this form.</p></noscript>
        <input type="hidden" name="_subject" value="Normaltown USA contact form">
        <input type="hidden" name="_template" value="table">
        <input type="hidden" name="_captcha" value="false">
        <input type="hidden" name="_next" value="{SITE_URL}/contact/thanks/">
        <div class="hp" aria-hidden="true"><label for="_honey">Leave this empty</label><input type="text" id="_honey" name="_honey" tabindex="-1" autocomplete="off"></div>
        <label for="c-name">Your name</label>
        <input type="text" id="c-name" name="name" required autocomplete="name">
        <label for="c-email">Your email</label>
        <input type="email" id="c-email" name="email" required autocomplete="email">
        <label for="c-topic">What's this about?</label>
        <select id="c-topic" name="topic">
          <option>A question</option>
          <option>A medical bill or health sharing question</option>
          <option>One-on-one help</option>
          <option>Something I got wrong</option>
          <option>Something else</option>
        </select>
        <label for="c-message">Your message</label>
        <textarea id="c-message" name="message" required></textarea>
        <button type="submit">Send it</button>
        <p class="fine">Goes straight to my inbox. I never share your email with anyone, and I don't have a list to add you to.</p>
      </form>
      <script>(function(){{var f=document.querySelector('.contact-form');if(f)f.action=atob(f.getAttribute('data-t'));}})();</script>"""


def toc_html(md):
    """Jump links for a long page: one entry per ## heading."""
    used = set()
    items = []
    for line in md.split("\n"):
        s = line.strip()
        if s.startswith("### "):
            heading_id(s[4:].strip(), used)
        elif s.startswith("## "):
            t = s[3:].strip()
            items.append(f'<li><a href="#{heading_id(t, used)}">{_inline(t)}</a></li>')
    if not items:
        return ""
    return '<nav class="toc" aria-label="On this page"><strong>On this page</strong><ol>' + "".join(items) + '</ol></nav>'


def render_page(title, md_body, slug, description, figure="", page_class="", og_image=None,
                schema=None, toc=False, page_title=None, lede=None, after="", extra_head=""):
    body_html = md_to_html(md_body, drop_email_cta=False)
    cls = f"page {page_class}".strip()
    lede_html = f'<p class="lede">{_inline(lede)}</p>' if lede else ""
    body = f"""<section class="{cls}"><div class="wrap">
      <div>
        <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">Home</a></li><li aria-current="page">{html.escape(title)}</li></ol></nav>
        <h1>{html.escape(title)}</h1>
        {lede_html}
        {toc_html(md_body) if toc else ""}
        <div class="body">{body_html}</div>
        {after}
      </div>
      {figure}
    </div></section>"""
    og_size = (1400, 1750) if og_image and og_image.endswith("family.jpg") else None
    current = "/contact/" if slug.startswith("contact") else f"/{slug}/"
    return layout(title, description, body, f"{SITE_URL}/{slug}/", og_image=og_image,
                  og_type="website", schema=schema, current=current, og_size=og_size,
                  page_title=page_title, extra_head=extra_head)


# About page photo: black-and-white family portrait, 4:5, two sizes for srcset.
ABOUT_PHOTO = SITE_DIR / "about-family.jpg"          # 1400x1750
ABOUT_PHOTO_SM = SITE_DIR / "about-family-700.jpg"   # 700x875
AUTHOR_HEADSHOT = SITE_DIR / "author-headshot.png"        # transparent B&W cutout, 595x793 (Person schema image)
AUTHOR_HEADSHOT_SM = SITE_DIR / "author-headshot-240.png"  # 180x240 copy for the round author-box avatar
HOME_HEADSHOT = SITE_DIR / "home-headshot.png"            # 850x850 round B&W headshot, Person schema image
HOME_HEADSHOT_XS = SITE_DIR / "home-headshot-96.png"      # 96x96 copy for the tiny avatar beside "In short"
HOME_HERO = SITE_DIR / "home-hero.jpg"                    # 659x850 B&W portrait, homepage hero
HOME_HERO_SM = SITE_DIR / "home-hero-400.jpg"             # 400x516 copy for the hero at 1x/2x
HOME_HEADSHOT_ALT = "David Dewese, smiling, in a black and white headshot."
HOME_HEADSHOT_CAPTION = "Hi, I'm David!"
ABOUT_PHOTO_ALT = ("Black and white photo of David Dewese kneeling with his wife and two "
                   "daughters, everyone laughing, in front of giant paper letters.")
ABOUT_PHOTO_CAPTION = "The whole reason I do the homework."


def about_figure():
    """Return the <figure> for the About page, or '' if the photo isn't there."""
    if not ABOUT_PHOTO.exists():
        return ""
    srcset = "family.jpg 1400w"
    if ABOUT_PHOTO_SM.exists():
        srcset = "family-700.jpg 700w, " + srcset
    return f"""<figure class="about-photo">
        <img src="family.jpg" srcset="{srcset}" sizes="(max-width:820px) 20rem, 21rem"
             alt="{html.escape(ABOUT_PHOTO_ALT, quote=True)}" width="1400" height="1750" loading="eager">
        <figcaption>{html.escape(ABOUT_PHOTO_CAPTION)}</figcaption>
      </figure>"""


def load_page_md(filename):
    """Read a site/*.md file; return (title, body_without_title)."""
    path = SITE_DIR / filename
    if not path.exists():
        return None, None
    raw = path.read_text(encoding="utf-8")
    title = filename.replace(".md", "").replace("-", " ").title()
    body = raw
    for idx, line in enumerate(raw.split("\n")):
        if line.startswith("# "):
            title = line[2:].strip()
            body = "\n".join(raw.split("\n")[idx + 1:])
            break
    return title, body


# ----------------------------------------------------------------------------
# Feeds, llms.txt, sitemap, static extras
# ----------------------------------------------------------------------------

def render_rss(posts):
    items = []
    for p in posts[:30]:
        pub = p["date"].strftime("%a, %d %b %Y 09:00:00 -0400")
        content = p["body_html"]
        if p["short"]:
            content = f"<p><strong>In short:</strong> {_inline(p['short'])}</p>" + content
        content = content.replace('src="' + (p["png_name"] or "\x00"), f'src="{p["url"]}{p["png_name"]}"')
        content = re.sub(r'href="/', f'href="{SITE_URL}/', content)
        items.append(f"""<item>
      <title>{html.escape(p['title'])}</title>
      <link>{p['url']}</link>
      <guid isPermaLink="true">{p['url']}</guid>
      <pubDate>{pub}</pubDate>
      <dc:creator>{AUTHOR}</dc:creator>
      <category>{CATEGORIES[p['category']]['name']}</category>
      <description>{html.escape(p['meta'] or '')}</description>
      <content:encoded><![CDATA[{content}]]></content:encoded>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}/</link>
    <atom:link href="{SITE_URL}/rss.xml" rel="self" type="application/rss+xml"/>
    <description>{html.escape(HOME_DESC)}</description>
    <language>en-us</language>
    <lastBuildDate>{TODAY.strftime("%a, %d %b %Y 09:00:00 -0400")}</lastBuildDate>
    {"".join(items)}
</channel></rss>"""


def render_sitemap(posts, pages):
    """pages = [(url, lastmod_date)]"""
    entries = []
    for url, mod in pages:
        entries.append(f"<url><loc>{url}</loc><lastmod>{mod.isoformat()}</lastmod></url>")
    for p in posts:
        entries.append(f"<url><loc>{p['url']}</loc><lastmod>{p['modified'].isoformat()}</lastmod></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(entries) + '</urlset>')


def render_llms(posts):
    lookup = by_slug(posts)
    out = [f"# {SITE_NAME}", "",
           f"> Plain-English help with money, medical bills, health insurance, health sharing, and "
           f"saving in bitcoin, written by {AUTHOR}: a regular guy with a full-time job and a family of "
           f"four who uses these things himself (his family left health insurance for CrowdHealth, a "
           f"health sharing service). Not a financial advisor. Every post is short, first-person, and "
           f"explains one idea with a plain analogy. No jargon, no hype.", "",
           "Site: " + SITE_URL + "/. Every page is free and has no paywall. Posts live at /p/<slug>/. "
           "Full text of every post is in /llms-full.txt. Categories: Money, Health (medical bills, "
           "insurance, health sharing), Bitcoin (saving, not gambling).", "",
           "## Start here", "",
           f"- [Start Here]({SITE_URL}/start-here/): the reading paths and the three posts to read first.",
           f"- [FAQ]({SITE_URL}/faq/): short answers to the most common money, medical bill, health sharing, and bitcoin questions.",
           f"- [About David Dewese]({SITE_URL}/about/): who writes this, how he researches, how the site makes money.",
           f"- [Blog]({SITE_URL}/blog/): every post, newest first, grouped by topic.",
           f"- [Contact]({SITE_URL}/contact/): send a question or ask about one-on-one help.", ""]
    for s in START_HERE_SLUGS:
        if s in lookup:
            p = lookup[s]
            out.append(f"- [{p['title']}]({p['url']}): {p['meta']}")
    for key, c in CATEGORIES.items():
        out += ["", f"## {c['title']}", "", f"Hub: {SITE_URL}/{key}/", ""]
        for p in posts:
            if p["category"] == key:
                out.append(f"- [{p['title']}]({p['url']}): {p['meta']}")
    out += ["", "## Optional", "",
            f"- [Full text of every post]({SITE_URL}/llms-full.txt)",
            f"- [RSS feed]({SITE_URL}/rss.xml)",
            f"- [Sitemap]({SITE_URL}/sitemap.xml)", ""]
    return "\n".join(out)


def render_llms_full(posts):
    out = [f"# {SITE_NAME}: full text of every post", "",
           f"> {HOME_DESC}", "",
           f"Author: {AUTHOR} ({AUTHOR_URL}). Site: {SITE_URL}/. Each post below starts with its URL, "
           "publish date, and category.", ""]
    for p in posts:
        out += ["", "---", "", f"# {p['title']}", "",
                f"URL: {p['url']}", f"Published: {p['date'].isoformat()}",
                f"Updated: {p['modified'].isoformat()}", f"Category: {CATEGORIES[p['category']]['name']}",
                f"Author: {AUTHOR}", ""]
        if p["subtitle"]:
            out += [f"*{p['subtitle']}*", ""]
        if p["short"]:
            out += [f"**In short:** {p['short']}", ""]
        body = re.sub(r'\]\((/p/[^)]+)\)', lambda m: f"]({SITE_URL}{m.group(1)})",
                      re.sub(r'\]\(https?://(?:www\.)?normaltownusa\.com(/p/[^)]+?)/?\)',
                             lambda m: f"]({SITE_URL}{m.group(1)}/)", p["body_md"]))
        out += [body.strip(), ""]
        if p["sources"]:
            out += ["Sources:"] + [f"- {l}: {u}" for l, u, _ in p["sources"]] + [""]
    return "\n".join(out)


HEADERS = """# Cloudflare Pages headers (https://developers.cloudflare.com/pages/configuration/headers/)
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/styles.css
  Cache-Control: public, max-age=31536000, immutable

/p/*.png
  Cache-Control: public, max-age=2592000

/about/*.jpg
  Cache-Control: public, max-age=2592000

/about/*.png
  Cache-Control: public, max-age=2592000

/llms.txt
  Content-Type: text/plain; charset=utf-8

/llms-full.txt
  Content-Type: text/plain; charset=utf-8
"""


def render_404():
    body = """<section class="page"><div class="wrap"><div>
      <h1>That page isn't here.</h1>
      <div class="body"><p>Maybe the link was old, or maybe I moved something. Either way, no harm done.</p>
      <p>Try the <a href="/">home page</a>, the <a href="/start-here/">Start Here</a> page, or the <a href="/faq/">FAQ</a>.</p></div>
    </div></div></section>"""
    return layout("Page not found", "That page isn't here. Try the home page or Start Here.",
                  body, SITE_URL + "/404.html", og_type="website",
                  extra_head='<meta name="robots" content="noindex">\n')


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def check_links(posts, page_slugs):
    """Warn about internal links that point nowhere."""
    valid = {f"/p/{p['slug']}/" for p in posts} | {f"/{s}/" for s in page_slugs} | {"/", "/rss.xml", "/llms.txt"}
    valid |= {f"/p/{s}/" for s in UNPUBLISHED}
    valid |= {f"/{k}/" for k in CATEGORIES}
    problems = []
    for p in posts:
        for m in re.finditer(r'\]\(([^)]+)\)', p["body_md"]):
            url = normalise_url(m.group(1)).split("#")[0]
            if url.startswith("/") and url not in valid:
                problems.append((p["slug"], url))
    for m in re.finditer(r'\]\(([^)]+)\)', "\n".join((SITE_DIR / f).read_text(encoding="utf-8") for f in ("start-here.md", "faqs.md", "author-bio.md") if (SITE_DIR / f).exists())):
        url = normalise_url(m.group(1)).split("#")[0]
        if url.startswith("/") and url not in valid:
            problems.append(("site page", url))
    for slug, url in problems:
        print(f"  WARNING: /p/{slug}/ links to missing page {url}")
    return problems


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    posts = load_posts()

    write(DIST / "styles.css", CSS)
    shutil.copytree(LOGO_DIR, DIST / "assets")
    og_default = SITE_DIR / "og-default.png"
    if og_default.exists():
        shutil.copy(og_default, DIST / "assets" / "og-default.png")

    write(DIST / "index.html", render_home(posts))
    write(DIST / "blog" / "index.html", render_blog(posts))
    for key in CATEGORIES:
        write(DIST / key / "index.html", render_hub(key, posts))

    for p in posts:
        write(DIST / "p" / p["slug"] / "index.html", render_post(p, posts))
        if p["png"]:
            shutil.copy(p["png"], DIST / "p" / p["slug"] / p["png_name"])

    # static pages from site/*.md
    page_map = {
        "start-here.md": {
            "slug": "start-here",
            "desc": ("New to Normaltown USA? Here's who it's for, what I write about, the three posts "
                     "to read first, and where my family actually landed on health insurance."),
            "page_title": "Start Here: Plain-English Money and Health Help, and Where to Begin",
        },
        "faqs.md": {
            "slug": "faq",
            "desc": ("Short, plain-English answers to the questions I get most: why you feel broke on a "
                     "good income, why you got a big bill with insurance, what health sharing costs and "
                     "who it's wrong for, and how to start with bitcoin."),
            "page_title": "FAQ: Money, Medical Bills, Health Sharing, and Bitcoin Questions Answered Plainly",
            "toc": True,
        },
        "author-bio.md": {
            "slug": "about",
            "desc": (f"About {AUTHOR}: a regular guy with a full-time job and a family of four who "
                     "explains money, medical bills, health sharing, and bitcoin in plain English. "
                     "How I research, how this site makes money, and what I'm not."),
            "page_title": f"About {AUTHOR} and Normaltown USA",
        },
        "contact.md": {
            "slug": "contact",
            "desc": ("Ask a question, send a medical bill that doesn't make sense, or ask about "
                     f"one-on-one help. Messages go straight to {AUTHOR}'s inbox."),
            "page_title": "Contact David Dewese",
        },
        "accessibility.md": {
            "slug": "accessibility",
            "desc": ("Normaltown USA aims to meet WCAG 2.1 AA. What that means, what's been done, "
                     "the one known gap, and how to tell me if something doesn't work for you."),
            "page_title": "Accessibility Statement",
        },
        "contact-thanks.md": {
            "slug": "contact/thanks",
            "desc": "Your message is in my inbox. I'll write back as soon as I can.",
            "page_title": "Got it, thanks",
            "noindex": True,
        },
        "subscribed.md": {
            "slug": "subscribed",
            "desc": "You're on the list. New posts will show up in your inbox.",
            "page_title": "You're in",
            "noindex": True,
        },
    }
    page_slugs, sitemap_pages = [], [(SITE_URL + "/", TODAY)]
    for fname, cfg in page_map.items():
        slug = cfg["slug"]
        title, body = load_page_md(fname)
        if title is None:
            continue
        figure, page_class, og_image = "", "", None
        schema = [website_schema(), org_schema()]
        page_url = f"{SITE_URL}/{slug}/"
        if slug == "about" and ABOUT_PHOTO.exists():
            figure, page_class = about_figure(), "about"
            og_image = f"{SITE_URL}/about/family.jpg"
            (DIST / slug).mkdir(parents=True, exist_ok=True)
            shutil.copy(ABOUT_PHOTO, DIST / slug / "family.jpg")
            if ABOUT_PHOTO_SM.exists():
                shutil.copy(ABOUT_PHOTO_SM, DIST / slug / "family-700.jpg")
            if AUTHOR_HEADSHOT.exists():
                shutil.copy(AUTHOR_HEADSHOT, DIST / slug / "david-dewese.png")
            if AUTHOR_HEADSHOT_SM.exists():
                shutil.copy(AUTHOR_HEADSHOT_SM, DIST / slug / "david-dewese-240.png")
            if HOME_HEADSHOT.exists():
                shutil.copy(HOME_HEADSHOT, DIST / slug / "david-dewese-round.png")
            if HOME_HEADSHOT_XS.exists():
                shutil.copy(HOME_HEADSHOT_XS, DIST / slug / "david-dewese-round-96.png")
            if HOME_HERO.exists():
                shutil.copy(HOME_HERO, DIST / slug / "david-dewese-hero.jpg")
            if HOME_HERO_SM.exists():
                shutil.copy(HOME_HERO_SM, DIST / slug / "david-dewese-hero-400.jpg")
            schema.append(person_schema(full=True))
            schema.append({"@type": "AboutPage", "@id": page_url + "#page", "url": page_url,
                           "name": cfg["page_title"], "description": cfg["desc"],
                           "mainEntity": {"@id": f"{SITE_URL}/#david"},
                           "isPartOf": {"@id": f"{SITE_URL}/#website"}})
        elif slug == "faq":
            faqs = extract_faqs(body, every_h3=True)
            schema.append({"@type": "FAQPage", "@id": page_url + "#faq", "url": page_url,
                           "name": cfg["page_title"], "description": cfg["desc"],
                           "isPartOf": {"@id": f"{SITE_URL}/#website"},
                           "author": {"@id": f"{SITE_URL}/#david"},
                           "mainEntity": [{"@type": "Question", "name": q,
                                           "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
        elif slug == "contact":
            schema.append({"@type": "ContactPage", "@id": page_url + "#page", "url": page_url,
                           "name": cfg["page_title"], "description": cfg["desc"],
                           "isPartOf": {"@id": f"{SITE_URL}/#website"},
                           "about": {"@id": f"{SITE_URL}/#organization"}})
        else:
            schema.append({"@type": "WebPage", "@id": page_url + "#page", "url": page_url,
                           "name": cfg["page_title"], "description": cfg["desc"],
                           "isPartOf": {"@id": f"{SITE_URL}/#website"},
                           "author": {"@id": f"{SITE_URL}/#david"}})
        write(DIST / slug / "index.html",
              render_page(title, body, slug, cfg["desc"], figure=figure, page_class=page_class,
                          og_image=og_image, schema=schema, toc=cfg.get("toc", False),
                          page_title=f"{cfg['page_title']} | {SITE_NAME}",
                          after=contact_form() if slug == "contact" else "",
                          extra_head='<meta name="robots" content="noindex">\n' if cfg.get("noindex") else ""))
        page_slugs.append(slug)
        if not cfg.get("noindex"):
            sitemap_pages.append((page_url, git_modified(SITE_DIR / fname) or TODAY))
    sitemap_pages.append((f"{SITE_URL}/blog/", max([p["modified"] for p in posts] or [TODAY])))
    for key in CATEGORIES:
        sitemap_pages.append((f"{SITE_URL}/{key}/", max([p["modified"] for p in posts if p["category"] == key] or [TODAY])))

    # feeds, llms.txt, robots, headers, 404
    write(DIST / "rss.xml", render_rss(posts))
    write(DIST / "sitemap.xml", render_sitemap(posts, sitemap_pages))
    write(DIST / "llms.txt", render_llms(posts))
    write(DIST / "llms-full.txt", render_llms_full(posts))
    write(DIST / "_headers", HEADERS)
    write(DIST / "404.html", render_404())
    indexnow_key = SITE_DIR / "indexnow-key.txt"
    if indexnow_key.exists():   # IndexNow ownership file, see indexnow.py
        k = indexnow_key.read_text(encoding="utf-8").strip()
        write(DIST / f"{k}.txt", k)
    bing_auth = SITE_DIR / "BingSiteAuth.xml"
    if bing_auth.exists():      # Bing Webmaster Tools ownership file, served at the site root
        write(DIST / "BingSiteAuth.xml", bing_auth.read_text(encoding="utf-8"))
    robots = SITE_DIR / "robots.txt"
    robots_txt = robots.read_text(encoding="utf-8") if robots.exists() else "User-agent: *\nAllow: /\n"
    if "Sitemap:" not in robots_txt:
        robots_txt = robots_txt.rstrip() + f"\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    write(DIST / "robots.txt", robots_txt)

    problems = check_links(posts, page_slugs)
    no_short = [p["slug"] for p in posts if not p["short"]]
    no_faq = [p["slug"] for p in posts if not p["faqs"]]
    print(f"Built {len(posts)} posts + {len(page_slugs)} pages + {len(CATEGORIES)} hubs -> {DIST}")
    print("Latest:", posts[0]["title"] if posts else "(none)")
    if no_short:
        print(f"  {len(no_short)} posts without an 'In short' blockquote: {', '.join(no_short[:5])}{'...' if len(no_short) > 5 else ''}")
    if no_faq:
        print(f"  {len(no_faq)} posts without a Questions section: {', '.join(no_faq[:5])}{'...' if len(no_faq) > 5 else ''}")
    if problems:
        print(f"  {len(problems)} broken internal links (see warnings above)")


if __name__ == "__main__":
    main()
