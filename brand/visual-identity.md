# Normaltown USA — Visual Identity

> The master reference for every graphic, the visual twin of `brand-voice-spec.md`.
> Inspired by Jack Butcher / Visualize Value and his mantra **"Making complex ideas
> simple."** Same job as the writing: take something tangled and make a busy person
> get it in one glance.

---

## The one rule
**One idea per graphic. Reduce it to geometry. Mark the point in one color.**

If a graphic needs a sentence to explain itself, it's not done. If it has two ideas,
split it into two graphics.

---

## The system (what makes it ours)

1. **One idea, nothing else.** Brutal focus. Empty space is the feature.
2. **Geometry as metaphor.** No illustration, no clip-art. Primitives only: circles,
   arrows, triangles, lines, dots, bars, math symbols. The *contrast between shapes*
   carries the meaning.
3. **Soft-black canvas, white line art.** Thin white monoline shapes on `#0F0F0F`,
   huge negative space.
4. **One bright accent: cyan.** On exactly ONE element — the thing the eye should land
   on (the point, the answer, the aligned choice). White is default; cyan is spotlight.

---

## Palette — exactly three colors (never approximate, never add a fourth)

| Role | Hex | Use |
|---|---|---|
| Canvas (soft black) | `#0F0F0F` | the background. **Never true black `#000`.** |
| Line + labels (white) | `#FFFFFF` | all line art and functional labels |
| **Accent (cyan)** | **`#2DD4FF`** | the ONE element that is "the point" |

No gray, no second accent, **no orange** (CrowdHealth + bitcoin own it). The only
allowance: white at reduced opacity (e.g., 60%) for a quieter label — still white.

---

## Logo (updated 2026-09-05)
The logo is a **lockup: icon + wordmark**. Master files live in `brand/logo/`.

| File | What it is | Use |
|---|---|---|
| `normaltown-logo-reverse.svg` | Full lockup: cyan icon + "Normaltown" (white) + "USA" (cyan). 1132×156. | Site header, anything on the soft-black canvas |
| `normaltown-wordmark-reverse.svg` | Wordmark only, no icon. 977×99. | Tight horizontal spaces |
| `normaltown-icon.svg` | The icon alone (two cyan shapes, ~118×156, portrait). | Favicon, avatars, app-style tiles |

- **Wordmark font: Montserrat ExtraBold.** "Normaltown" is white, "USA" is cyan
  `#2DD4FF`. The text is **outlined to paths** in the SVGs, so nothing needs to load
  Montserrat to render the logo correctly. Never re-typeset the wordmark in Manrope.
- **Icon is always cyan** on the soft-black canvas. Do not recolor it, add a stroke, or
  put it on a light background (these are "reverse" files: built for dark canvas only).
  A light-canvas version does not exist yet; make one from the same paths if needed.
- Clear space: at least the icon's width on every side. Minimum header height 28px.
- On the website the logo is the only branding: it sits in the header (`build.py`),
  the icon is the favicon (`/assets/normaltown-icon.svg`), and both are copied to
  `dist/assets/` on every build. **Graphics still carry no logo** (see below).

---

## Typography
Two typefaces, each with one job:

- **Logo only: Montserrat ExtraBold.** Lives inside the logo SVGs as outlined paths.
  Not used for body copy, headlines, labels, or graphics.
- **Everything else: Manrope (Google Font).** Body, headlines, UI, and every graphic label.
  `font-family="Manrope, 'Helvetica Neue', Arial, sans-serif"`.
  Bold / ExtraBold for emphasis; Regular / Medium for labels. Tight tracking.
- Manrope is installed locally (`~/Library/Fonts/Manrope.ttf`) so SVG previews render
  true. For portable hand-off files, outline text to paths so the font always holds.

---

## Titles live OUTSIDE the graphic
- **Do not embed the article headline/title in the image.** The title is delivered in
  the article body or the social caption, not baked into the art.
- **Functional labels are fine** — short data labels that are part of the diagram
  itself (e.g., "YOUR CARE · 80¢", "THEIR CUT · 20¢", an axis, a comparison label).
  They explain the geometry; they are not the headline.

---

## No branding in the graphic
- No wordmark, no "Normaltown USA" footer, no logo, no kicker line. The art stands
  alone. Branding lives in the post/page around it, not on it. The logo files in
  `brand/logo/` are for the site chrome and social profiles, never for the graphics.

---

## Formats
- **Square 1:1 (1200×1200)** — the default and signature unit (matches social).
- **16:9 (1200×675)** — optional, for a blog hero when needed.
- Generous margins; let the mark breathe in the center/lower-middle.

---

## Filenames
- Descriptive **kebab-case**, no brand name, **no "vv"**, no style jargon.
  Good: `premium-dollar.svg`, `cash-vs-insured-price.svg`.
  Bad: `nbtown-vv-hero-final.svg`.

---

## Visual vocabulary (reach for these first)
- **Circle:** outline = ordinary/empty; filled = real/the point.
- **Arrows:** straight = direct; jagged = wasted motion; up = growth; cyan arrow = "this grows."
- **Triangle:** whole = the goal; subdivided = made of small parts.
- **Bar / split:** proportions, before/after, where-the-money-goes.
- **Two-up comparison:** the workhorse. Left = the common way; right (cyan) = the point.
- **Math symbols:** `=`, `≠`, `0 → 1`, `+`, `×` for crisp logical ideas.

---

## Production: who makes it
- **Default = Claude builds it natively as SVG** (`#0F0F0F`/white/cyan, Manrope,
  exact geometry), then renders a PNG preview via `qlmanage`. Edits are one-liners.
- **Gemini only for the rare organic illustration** geometry can't carry — and it must
  still obey this system: soft-black, white line art, one cyan accent, Manrope feel,
  no embedded title, no branding.

---

## Do / Don't
- ✅ One idea. Lots of soft-black. White lines. One cyan accent. Manrope. No title baked in.
- ✅ Functional data labels when they help. Reuse a motif across a cluster.
- ❌ No true black, no gray, no second accent, no orange.
- ❌ No embedded headline, no logo/wordmark/footer.
- ❌ No gradients, shadows, 3D, stock-photo realism, clip-art. No "vv" in filenames.
