# Normaltown USA — Brand Guide

> The single entry point to the brand. Start here; the deep specs are linked below.
> Mantra (borrowed from Jack Butcher): **making complex ideas simple.**

---

## In one line
**Money help for normal people, explained in plain English. No jargon, no being
talked down to.**

## Who it's for
Married, 35–55, a job and a family. They do everything right, pay for health
insurance every month, and *still* come up short and still get surprise medical
bills. Their gut feeling: *"Why can't I get ahead when I'm doing it all right?"*

## What we believe (the spine)
1. The health industry is paid to **manage** sickness, not to make us well
   (misaligned incentives).
2. National money loses value over time, a slow leak that quietly shrinks savings.
3. Bitcoin is designed to preserve what you earn. Savings, not gambling.

---

## Voice (summary)
Plainspoken, warm, a friend across the table. Simple words, short sentences, one
clear analogy per idea, never assume prior knowledge. No jargon, no "fiat," no
cursing, **no em dashes, no ellipses**. Frame the system, not the people.
→ Full spec: [`brand-voice-spec.md`](../brand-voice-spec.md)

## Visual identity (summary)
Visualize-Value style: **one idea per graphic, reduced to geometry, with the point
marked in one color.**
- **Colors (exactly three):** soft-black `#0F0F0F` (never true black), white
  `#FFFFFF`, cyan `#2DD4FF` (the accent that marks "the point"). No gray, no orange.
- **Logo:** icon + wordmark lockup in `brand/logo/` (wordmark set in **Montserrat
  ExtraBold**, outlined to paths; "Normaltown" white, "USA" + icon cyan). Reverse
  (dark-canvas) versions only. The icon alone is the favicon.
- **Font:** Manrope (Google Font) for all body, headline, UI, and graphic type. The
  logo is the only place Montserrat appears.
- **Format:** 1:1 square (1200×1200) by default.
- **Rules:** no embedded title (titles go in the article/caption), no branding on the
  art, lots of negative space.
→ Full spec: [`visual-identity.md`](visual-identity.md)
→ Palette: [`palette.svg`](palette.svg) · Building blocks: [`visual-vocabulary.svg`](visual-vocabulary.svg)
→ Logo files: [`logo/`](logo/) (full lockup, wordmark only, icon only)

## How we make money (ethos)
**Value first, pitch second, always.** Three buckets: pure trust-builders, a health
angle that honestly leads to CrowdHealth's flat-fee model (disclosed, with its real
limits stated), and a money/bitcoin angle. Never bait-and-switch.
→ Rules: [`../pipeline/06-cta-affiliate.md`](../pipeline/06-cta-affiliate.md)

---

## The content machine (7 stations)
A repeatable assembly line of paste-in prompts in [`../pipeline/`](../pipeline/):
1. **Topic engine** — tagged article ideas across the three pillars.
2. **Outline** — search-smart, analogy-anchored, tight word targets.
3. **Draft** — writes in voice.
4. **Fact-check / EEAT** — verifies every claim, adds sources, checks guardrails.
5. **Repurpose** — newsletter + social posts from one article.
6. **CTA / affiliate** — value-first monetization rules.
7. **Visual brief** — designs the graphic; Claude builds most as SVG natively.

---

## File map
```
Normaltown-USA/
├─ brand-voice-spec.md         ← how we write (voice, reader, beliefs)
├─ brand/
│  ├─ brand-guide.md           ← you are here (master entry point)
│  ├─ visual-identity.md       ← how we look (full visual spec)
│  ├─ palette.svg              ← the locked 3-color palette
│  ├─ visual-vocabulary.svg    ← reusable geometric building blocks
│  └─ logo/                    ← SVG logo: full lockup, wordmark, icon (Montserrat ExtraBold, outlined)
├─ pipeline/                   ← the 7-station content machine (prompts)
└─ articles/<slug>/            ← each article + its assets (svg, alt text, repurpose)
```

## Quick facts (keep current)
- **Accent color decided:** cyan `#2DD4FF` (chosen over green/magenta/yellow).
- **Cornerstone article:** `articles/nobody-gets-paid-to-make-you-well/`.
- **Platform:** Ghost vs. beehiiv — not yet chosen.
- **CrowdHealth:** flat $60/mo fee (not a cut of claims); not insurance; has limits.
