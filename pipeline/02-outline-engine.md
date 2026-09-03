# Pipeline Station 2 — The Outline Engine

> **What this is:** Turns one title from `topic-backlog.md` into a search-smart,
> analogy-anchored outline that's ready to draft. The blueprint before the build.

## How to run it
Make sure Claude has read `brand-voice-spec.md`. Paste the PROMPT, fill in the
title/search from the backlog. Output → `articles/<slug>/outline.md`.

## PROMPT (paste into Claude)
```
You are the outline engine for Normaltown USA. Read brand-voice-spec.md first.

INPUT:
- Working title: {title}
- Target search: {search}
- Money-bucket: {bucket}
- Analogy hook: {analogy}

Produce an outline with:
1. H1 (the headline — reader's words, curiosity + clarity)
2. Meta description (≤155 chars, plain, no hype)
3. The promise (one sentence: what the reader walks away with)
4. The ONE analogy carried start to finish (state it, then where it recurs)
5. Section beats as H2/H3 — each beat = one idea, in order, noting which fact
   needs a source and where the analogy reappears
6. The honest turn → money-bucket (how value leads naturally to the soft mention)
7. CTA (email list) + any affiliate mention, value-first
8. 2–3 internal links to other backlog articles (cluster building)
9. Target word count — keep it tight: easy-wins 500–900; cornerstones 1,000–1,300.
   Rule: "as long as it needs to be, and not one word longer." For easy-wins, lead
   with the answer in the first paragraph (don't make the reader scroll for it).

RULES: one idea per beat; every claim that needs proof gets a [VERIFY] tag for
Station 4; if a section has no analogy or example, it's too abstract — fix it.
```

## Tuning notes
- Cornerstones earn length; easy-wins stay tight.
- If the outline feels preachy, add a "name the reader's feeling first" opening beat.
