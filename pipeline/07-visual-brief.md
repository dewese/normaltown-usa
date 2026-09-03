# Pipeline Station 7 — Visual Brief

> **What this is:** For every article, this station designs the graphic(s) in the
> Normaltown visual system (see `brand/visual-identity.md`). The system is pure
> geometry, so **most graphics are built natively as SVG by Claude** — exact hex,
> Manrope type, editable, free. Gemini is only for the rare organic illustration.

## How to run it
Claude reads `brand/visual-identity.md` + the finished article. Paste the PROMPT.
Output → `articles/<slug>/<name>.svg` (+ PNG preview) and notes in `visual-brief.md`.

## PROMPT (paste into Claude)
```
You are the visual brief engine for Normaltown USA. Read brand/visual-identity.md
and the article. Find the article's ONE core idea (and its analogy). Then design:

1. A SQUARE 1:1 graphic (default; add a 16:9 only if a blog hero needs it) that
   reduces the idea to GEOMETRY (circles, arrows, triangles, bars, math symbols).
   - Canvas #0F0F0F (soft black, NEVER #000). White line art. CYAN #2DD4FF on
     exactly ONE element — the point. Manrope for any type.
   - DO NOT embed the article title/headline. The title is delivered in the article
     or social caption. Only include short FUNCTIONAL labels if the diagram needs
     them (e.g., "YOUR CARE · 80¢"). No wordmark, no logo, no footer, no branding.
2. Build path:
   - DEFAULT: write a precise SVG build-spec (shapes, coordinates, exact hex,
     font-family Manrope) so Claude renders it directly. Prefer this almost always.
   - ONLY IF it truly needs organic illustration: a Gemini prompt that still obeys
     the system (soft-black, white line art, one cyan accent, no title, no branding).
3. ALT TEXT: one plain sentence, topic worked in naturally (SEO + a11y).
4. Filename: descriptive kebab-case, no brand name, no "vv".

RULES: one idea; contrast carries meaning; cyan marks ONE thing; three colors only
(#0F0F0F / #FFFFFF / #2DD4FF); no gray, no orange, no second accent; no embedded
title; no branding; no gradients/shadows/3D/clip-art.
```

## After the brief
Claude builds the SVG, renders a PNG preview (`qlmanage`), and saves both in the
article folder. The headline goes in the article body or the post caption — never on
the art. Tweaks are one-line edits to the SVG.

## Tuning notes
- If a graphic feels busy, remove elements until only the contrast remains.
- Reuse a motif across a cluster (e.g., the same bar or circle-pair) for a family look.
- For portable hand-off, outline Manrope text to paths so the font always holds.
