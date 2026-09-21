#!/usr/bin/env python3
"""Recolour the post hero art so it answers to the reader's light/dark setting.

Every hero was drawn with exactly three colours: #0F0F0F canvas, #FFFFFF line art,
#2DD4FF accent. This rewrites each one to carry semantic classes plus a small internal
stylesheet, so a single file renders warm on the light theme and keeps the original
identity on the dark one. Browsers honour a `prefers-color-scheme` query inside an SVG
even when it is loaded through <img>, so nothing needs a second file.

Idempotent: a file that already has the stylesheet is skipped. Standard library only.
Run from the repo root:  python3 brand/theme-hero-svgs.py
"""
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import build  # noqa: E402  (the builder owns the category rules)

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "Posts"

BG, INK, ACCENT = "#0F0F0F", "#FFFFFF", "#2DD4FF"

# light, dark
PALETTE = {
    "bg":  ("#F3EDE4", "#141210"),
    "ink": ("#1B1917", "#F7F3EC"),
    "ac":  ("#0E6F63", "#4FC7B4"),
}
# Bitcoin posts keep the cyan. It is the one place it still reads right, and on warm
# paper it has to darken to #0E7490 to clear 4.5:1.
PALETTE_BITCOIN = dict(PALETTE, ac=("#0E7490", "#2DD4FF"))

ROLE = {BG: "bg", INK: "ink", ACCENT: "ac"}
MARKER = "normaltown-theme"


def stylesheet(pal):
    light = "".join(f".f-{k}{{fill:{v[0]}}}.s-{k}{{stroke:{v[0]}}}" for k, v in pal.items())
    dark = "".join(f".f-{k}{{fill:{v[1]}}}.s-{k}{{stroke:{v[1]}}}" for k, v in pal.items())
    return (f'<style id="{MARKER}">{light}'
            f'@media (prefers-color-scheme:dark){{{dark}}}</style>')


def convert_tag(tag):
    """Swap a tag's hard-coded fill/stroke for the matching class."""
    classes = []

    def take(attr, prefix):
        nonlocal tag
        m = re.search(rf'\s{attr}="({BG}|{INK}|{ACCENT})"', tag, re.I)
        if not m:
            return
        classes.append(f"{prefix}-{ROLE[m.group(1).upper()]}")
        tag = tag.replace(m.group(0), "", 1)

    take("fill", "f")
    take("stroke", "s")
    if not classes:
        return tag
    existing = re.search(r'\sclass="([^"]*)"', tag)
    if existing:
        merged = existing.group(1) + " " + " ".join(classes)
        return tag.replace(existing.group(0), f' class="{merged}"', 1)
    return tag.replace("<", "<", 1).replace(
        tag.split(None, 1)[0], tag.split(None, 1)[0] + f' class="{" ".join(classes)}"', 1)


def convert(path, pal):
    src = path.read_text(encoding="utf-8")
    if MARKER in src:
        return False
    out = re.sub(r'<[a-zA-Z][^>]*?/?>', lambda m: convert_tag(m.group(0)), src)
    # Root <svg> keeps fill="none"; drop the stylesheet in right after it.
    out = re.sub(r'(<svg\b[^>]*>)', r'\1\n' + stylesheet(pal).replace('\\', '\\\\'), out, count=1)
    leftover = [c for c in (BG, INK, ACCENT) if c in out.replace(stylesheet(pal), "")]
    if leftover:
        print(f"  WARN {path}: unconverted {leftover}", file=sys.stderr)
    path.write_text(out, encoding="utf-8")
    return True


def is_bitcoin(folder):
    """Reuse the builder's own classifier rather than re-deriving it.

    No post declares `Category | Bitcoin`; the bitcoin hub is assembled from an explicit
    slug list plus a keyword sniff on the title. Guessing that again here would drift the
    moment build.py changes, so import the real thing.
    """
    pub = folder / "publish.md"
    article = folder / "article.md"
    if not pub.exists() or not article.exists():
        return False
    pub_text = pub.read_text(encoding="utf-8")
    slug = build._row_value(pub_text, "URL slug") or ""
    category = build._row_value(pub_text, "Category") or ""
    title = ""
    for line in article.read_text(encoding="utf-8").split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return build.classify(category, title, slug.strip("`")) == "bitcoin"


def main():
    done = skipped = 0
    for svg in sorted(POSTS.glob("*/*/*/*.svg")):
        pal = PALETTE_BITCOIN if is_bitcoin(svg.parent) else PALETTE
        if convert(svg, pal):
            done += 1
        else:
            skipped += 1
    print(f"themed {done} hero svgs, {skipped} already done")


if __name__ == "__main__":
    main()
