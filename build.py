#!/usr/bin/env python3
"""
Normaltown USA - static site generator (zero dependencies, Python 3 stdlib only).

The "machine": reads finished posts from Posts/<YYYY>/<MM>/<DD>/ and the site
copy in site/, then writes a complete static website to dist/.

Publishing a new post = drop its folder in Posts/ (article.md + publish-beehiiv.md
+ one .png), run `python3 build.py`, commit, push. Cloudflare Pages serves dist/.

Brand (locked): canvas #0F0F0F (never #000), text #FFFFFF, accent cyan #2DD4FF,
Manrope. Visualize-Value aesthetic: one idea, lots of negative space.
"""

import html
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "Posts"
SITE_DIR = ROOT / "site"
DIST = ROOT / "dist"

SITE_NAME = "Normaltown USA"
SITE_TAGLINE = "Money & Healthcare Made Simple"
SITE_URL = "https://www.normaltownusa.com"
AUTHOR = "David Dewese"

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# ----------------------------------------------------------------------------
# Minimal, controlled Markdown -> HTML (only the subset our articles use).
# ----------------------------------------------------------------------------

def _inline(text):
    """Escape HTML, then apply inline markdown: links, bold, italic, code."""
    text = html.escape(text, quote=False)
    # links [text](url)  -- process before emphasis
    def link(m):
        label, url = m.group(1), m.group(2)
        safe_url = html.escape(url, quote=True)
        return f'<a href="{safe_url}">{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    return text


def md_to_html(md, drop_email_cta=True):
    """Convert an article body (title line already removed) to HTML blocks."""
    lines = md.split("\n")

    # Drop a trailing email-style CTA block: a final '---' followed by inbox/list copy.
    if drop_email_cta:
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "---":
                tail = "\n".join(lines[i + 1:]).lower()
                if any(k in tail for k in ("inbox", "normaltown usa list", "join the")):
                    lines = lines[:i]
                break

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
            blocks.append(f"<h3>{_inline(stripped[4:].strip())}</h3>")
        elif stripped.startswith("## "):
            flush_para()
            blocks.append(f"<h2>{_inline(stripped[3:].strip())}</h2>")
        elif stripped.startswith("# "):
            flush_para()
            blocks.append(f"<h2>{_inline(stripped[2:].strip())}</h2>")
        elif re.match(r'^[-*] ', stripped):
            flush_para()
            items = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i].strip()):
                items.append(f"<li>{_inline(lines[i].strip()[2:].strip())}</li>")
                i += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        else:
            buf.append(line)
        i += 1
    flush_para()
    return "\n".join(blocks)


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
    val = val.strip("`").strip()          # drop code ticks
    val = re.sub(r'\*\*(.+?)\*\*', r'\1', val)  # drop bold
    return val or None


def slugify(title):
    s = title.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def classify(title, slug):
    text = (title + " " + slug).lower()
    health = ("health", "insur", "deductible", "hsa", "sharing", "medical",
              "blood test", "crowd", "bill")
    if any(k in text for k in health):
        return "Health"
    return "Money"


def load_posts():
    posts = []
    for article in sorted(POSTS_DIR.glob("*/*/*/article.md")):
        folder = article.parent
        parts = folder.parts
        y, m, d = int(parts[-3]), int(parts[-2]), int(parts[-1])
        raw = article.read_text(encoding="utf-8")

        # title = first "# " line; body = everything after it
        title = folder.name
        body_md = raw
        for idx, line in enumerate(raw.split("\n")):
            if line.startswith("# "):
                title = line[2:].strip()
                body_md = "\n".join(raw.split("\n")[idx + 1:])
                break

        pub_file = folder / "publish-beehiiv.md"
        pub = pub_file.read_text(encoding="utf-8") if pub_file.exists() else ""

        slug = _row_value(pub, "slug") or slugify(title)
        subtitle = _row_value(pub, "Subtitle")
        meta = _row_value(pub, "Meta description")

        # first paragraph as fallback description / preview
        first_para = ""
        for para in body_md.split("\n\n"):
            p = para.strip()
            if p and not p.startswith("#") and p != "---":
                first_para = re.sub(r'\s+', ' ', p)
                break
        if not meta:
            meta = (first_para[:157] + "...") if len(first_para) > 160 else first_para

        # alt text (from "Alt text:" line) fallback to title
        alt = None
        am = re.search(r'[Aa]lt text[:*\s]+`?([^`\n|]+)`?', pub)
        if am:
            alt = am.group(1).strip().strip("`").strip()
        if not alt:
            alt = title

        png = next(iter(sorted(folder.glob("*.png"))), None)

        posts.append({
            "date": date(y, m, d),
            "title": title,
            "slug": slug,
            "subtitle": subtitle,
            "meta": meta,
            "preview": first_para,
            "alt": alt,
            "png": png,
            "png_name": png.name if png else None,
            "body_html": md_to_html(body_md),
            "category": classify(title, slug),
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
body{
  margin:0; background:var(--canvas); color:var(--ink);
  font-family:Manrope,'Helvetica Neue',Arial,sans-serif;
  font-size:18px; line-height:1.7; font-weight:400;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--accent); text-decoration:none}
a:hover{text-decoration:underline}
img{max-width:100%; height:auto; display:block}
.wrap{width:100%; max-width:64rem; margin:0 auto; padding:0 1.5rem}

/* header */
.site-head{border-bottom:1px solid var(--faint)}
.site-head .wrap{display:flex; align-items:center; justify-content:space-between;
  gap:1rem; padding-top:1.1rem; padding-bottom:1.1rem; flex-wrap:wrap}
.brand{display:flex; align-items:center; gap:.6rem; font-weight:800;
  letter-spacing:-.02em; color:var(--ink); font-size:1.15rem}
.brand:hover{text-decoration:none}
.dot{width:.7rem; height:.7rem; border-radius:50%; background:var(--accent);
  display:inline-block; flex:none}
nav.main{display:flex; gap:1.4rem; font-size:.95rem; font-weight:600}
nav.main a{color:var(--muted)}
nav.main a:hover{color:var(--ink); text-decoration:none}

/* hero */
.hero{padding:4.5rem 0 2rem; border-bottom:1px solid var(--faint)}
.hero h1{font-size:clamp(2rem,5vw,3.1rem); line-height:1.08; letter-spacing:-.03em;
  font-weight:800; margin:0 0 1rem; max-width:20ch}
.hero p{font-size:1.2rem; color:var(--muted); margin:0; max-width:46ch}
.hero .accent{color:var(--accent)}

/* post list */
.list{padding:2.5rem 0 4rem}
.post-card{display:block; padding:1.6rem 0; border-bottom:1px solid var(--faint);
  color:var(--ink)}
.post-card:hover{text-decoration:none}
.post-card:hover h2{color:var(--accent)}
.post-card .meta{font-size:.82rem; color:var(--muted); font-weight:600;
  text-transform:uppercase; letter-spacing:.08em; margin-bottom:.5rem;
  display:flex; gap:.7rem; align-items:center}
.tag{color:var(--accent); border:1px solid var(--faint); border-radius:999px;
  padding:.05rem .55rem; font-size:.72rem}
.post-card h2{font-size:1.5rem; line-height:1.2; letter-spacing:-.02em;
  font-weight:800; margin:0 0 .35rem; transition:color .15s}
.post-card p{margin:0; color:var(--muted); font-size:1rem; max-width:60ch}

/* article */
.article{padding:3rem 0 4rem}
.article-head{max-width:var(--measure); margin:0 auto 2rem}
.article-head .meta{font-size:.82rem; color:var(--muted); font-weight:600;
  text-transform:uppercase; letter-spacing:.08em; margin-bottom:.9rem;
  display:flex; gap:.7rem; align-items:center}
.article-head h1{font-size:clamp(1.9rem,4.5vw,2.7rem); line-height:1.12;
  letter-spacing:-.03em; font-weight:800; margin:0 0 .6rem}
.article-head .subtitle{font-size:1.25rem; color:var(--muted); margin:0}
.hero-img{max-width:var(--measure); margin:0 auto 2.5rem; border-radius:14px;
  overflow:hidden; background:var(--panel); border:1px solid var(--faint)}
.body{max-width:var(--measure); margin:0 auto}
.body h2{font-size:1.45rem; letter-spacing:-.02em; font-weight:800;
  margin:2.4rem 0 .6rem; line-height:1.25}
.body h3{font-size:1.15rem; font-weight:700; margin:1.8rem 0 .4rem}
.body p{margin:0 0 1.15rem}
.body ul{margin:0 0 1.15rem; padding-left:1.2rem}
.body li{margin:.3rem 0}
.body strong{font-weight:700}
.body code{background:var(--panel); padding:.1rem .35rem; border-radius:5px;
  font-size:.9em}
.body hr.rule{border:none; height:1px; background:var(--faint); margin:2.2rem 0}

/* post footer CTA */
.post-cta{max-width:var(--measure); margin:3rem auto 0; padding:1.8rem;
  border:1px solid var(--faint); border-radius:14px; background:var(--panel)}
.post-cta h3{margin:0 0 .4rem; font-size:1.2rem; font-weight:800; letter-spacing:-.01em}
.post-cta p{margin:0; color:var(--muted); font-size:1rem}

/* generic page */
.page{padding:3rem 0 4rem}
.page .body{max-width:var(--measure)}
.page h1{font-size:clamp(1.9rem,4.5vw,2.6rem); letter-spacing:-.03em; font-weight:800;
  margin:0 0 1.4rem}

/* footer */
.site-foot{border-top:1px solid var(--faint); padding:2.5rem 0; color:var(--muted);
  font-size:.9rem}
.site-foot .wrap{display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap}
.site-foot a{color:var(--muted)}
.site-foot a:hover{color:var(--ink)}

@media (max-width:640px){
  body{font-size:17px}
  .hero{padding:3rem 0 1.6rem}
  nav.main{gap:1rem; font-size:.9rem}
}
"""


def layout(title, description, body, canonical, og_image=None, is_home=False):
    desc = html.escape(description or SITE_TAGLINE, quote=True)
    page_title = title if title == SITE_NAME else f"{title} | {SITE_NAME}"
    og = f'<meta property="og:image" content="{html.escape(og_image, quote=True)}">' if og_image else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{'website' if is_home else 'article'}">
<meta property="og:url" content="{canonical}">
{og}
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body>
<header class="site-head"><div class="wrap">
  <a class="brand" href="/"><span class="dot"></span>{SITE_NAME}</a>
  <nav class="main">
    <a href="/">Home</a>
    <a href="/start-here/">Start Here</a>
    <a href="/faq/">FAQ</a>
    <a href="/about/">About</a>
  </nav>
</div></header>
{body}
<footer class="site-foot"><div class="wrap">
  <span>&copy; {date.today().year} {SITE_NAME}. {SITE_TAGLINE}.</span>
  <span><a href="/rss.xml">RSS</a> &middot; <a href="/start-here/">Start Here</a></span>
</div></footer>
</body>
</html>"""


POST_CTA = """<div class="post-cta">
  <h3>New here?</h3>
  <p>Normaltown USA is plain-English money and healthcare help for normal people. No jargon, no hype. <a href="/start-here/">Start here</a>.</p>
</div>"""


def render_home(posts):
    hero = f"""<section class="hero"><div class="wrap">
      <h1>Money help for normal people, <span class="accent">explained plainly</span>.</h1>
      <p>{SITE_TAGLINE}. No jargon, no being talked down to. One clear idea at a time.</p>
    </div></section>"""
    cards = []
    for p in posts:
        d = f'{MONTHS[p["date"].month]} {p["date"].day}, {p["date"].year}'
        cards.append(f"""<a class="post-card" href="/p/{p['slug']}/">
          <div class="meta"><span class="tag">{p['category']}</span><span>{d}</span></div>
          <h2>{html.escape(p['title'])}</h2>
          <p>{html.escape(p['meta'] or '')}</p>
        </a>""")
    body = hero + '<section class="list"><div class="wrap">' + "\n".join(cards) + "</div></section>"
    return layout(SITE_NAME, SITE_TAGLINE, body, SITE_URL + "/", is_home=True)


def render_post(p):
    d = f'{MONTHS[p["date"].month]} {p["date"].day}, {p["date"].year}'
    canonical = f"{SITE_URL}/p/{p['slug']}/"
    subtitle = f'<p class="subtitle">{html.escape(p["subtitle"])}</p>' if p["subtitle"] else ""
    hero_img = ""
    og_image = None
    if p["png_name"]:
        hero_img = f'<figure class="hero-img"><img src="{p["png_name"]}" alt="{html.escape(p["alt"], quote=True)}" width="1200" height="1200"></figure>'
        og_image = f"{canonical}{p['png_name']}"
    body = f"""<article class="article"><div class="wrap">
      <div class="article-head">
        <div class="meta"><span class="tag">{p['category']}</span><span>{d}</span><span>by {AUTHOR}</span></div>
        <h1>{html.escape(p['title'])}</h1>
        {subtitle}
      </div>
      {hero_img}
      <div class="body">{p['body_html']}</div>
      {POST_CTA}
    </div></article>"""
    return layout(p["title"], p["meta"], body, canonical, og_image=og_image)


def render_page(title, md_body, slug, description):
    body_html = md_to_html(md_body, drop_email_cta=False)
    body = f"""<section class="page"><div class="wrap">
      <h1>{html.escape(title)}</h1>
      <div class="body">{body_html}</div>
    </div></section>"""
    return layout(title, description, body, f"{SITE_URL}/{slug}/")


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
# Feeds
# ----------------------------------------------------------------------------

def render_rss(posts):
    items = []
    for p in posts[:20]:
        link = f"{SITE_URL}/p/{p['slug']}/"
        pub = p["date"].strftime("%a, %d %b %Y 09:00:00 +0000")
        items.append(f"""<item>
      <title>{html.escape(p['title'])}</title>
      <link>{link}</link>
      <guid>{link}</guid>
      <pubDate>{pub}</pubDate>
      <description>{html.escape(p['meta'] or '')}</description>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
    <title>{SITE_NAME}</title>
    <link>{SITE_URL}/</link>
    <description>{SITE_TAGLINE}</description>
    <language>en-us</language>
    {"".join(items)}
</channel></rss>"""


def render_sitemap(posts, page_slugs):
    urls = [SITE_URL + "/"]
    urls += [f"{SITE_URL}/{s}/" for s in page_slugs]
    urls += [f"{SITE_URL}/p/{p['slug']}/" for p in posts]
    body = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemap.org/schemas/sitemap/0.9">{body}</urlset>'


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    posts = load_posts()

    # styles
    write(DIST / "styles.css", CSS)

    # home
    write(DIST / "index.html", render_home(posts))

    # posts + their images
    for p in posts:
        write(DIST / "p" / p["slug"] / "index.html", render_post(p))
        if p["png"]:
            shutil.copy(p["png"], DIST / "p" / p["slug"] / p["png_name"])

    # static pages from site/*.md
    page_map = {
        "start-here.md": ("start-here", "Where to begin with Normaltown USA."),
        "faqs.md": ("faq", "Common questions about money, healthcare, and Normaltown USA."),
        "author-bio.md": ("about", f"About {AUTHOR} and Normaltown USA."),
    }
    page_slugs = []
    for fname, (slug, desc) in page_map.items():
        title, body = load_page_md(fname)
        if title is None:
            continue
        write(DIST / slug / "index.html", render_page(title, body, slug, desc))
        page_slugs.append(slug)

    # feeds + robots
    write(DIST / "rss.xml", render_rss(posts))
    write(DIST / "sitemap.xml", render_sitemap(posts, page_slugs))
    robots = SITE_DIR / "robots.txt"
    robots_txt = robots.read_text(encoding="utf-8") if robots.exists() else "User-agent: *\nAllow: /\n"
    if "Sitemap:" not in robots_txt:
        robots_txt = robots_txt.rstrip() + f"\n\nSitemap: {SITE_URL}/sitemap.xml\n"
    write(DIST / "robots.txt", robots_txt)

    print(f"Built {len(posts)} posts + {len(page_slugs)} pages -> {DIST}")
    print("Latest:", posts[0]["title"] if posts else "(none)")


if __name__ == "__main__":
    main()
