# Pipeline Station 5 — The Repurpose Engine

> **What this is:** One article in, a week of distribution out. Turns the finished
> piece into a newsletter and social posts — the "spokes" that point back to the hub.
> This is the leverage: write once, show up everywhere.

## How to run it
Feed it the FINAL `article.md` (post fact-check). Paste the PROMPT.
Output → `articles/<slug>/repurpose.md`.

## PROMPT (paste into Claude)
```
You are the repurpose engine for Normaltown USA. Read brand-voice-spec.md and the
final article. Keep the same voice and the same analogy. Produce:

1. NEWSLETTER (email):
   - 3 subject-line options (curiosity + clarity, no clickbait, no "fiat")
   - A short email (200–350 words) that delivers the ONE big idea and links to the
     full article. Friend-to-friend, not a press release. One clear CTA to read on.

2. SOCIAL POSTS (text only — no on-camera, ever):
   - X/Twitter: a 5–8 line post or short thread opener built on the analogy.
   - LinkedIn: a slightly more reflective version, same idea, professional-warm.
   - Facebook/Instagram caption: conversational, ends with a soft question to spark replies.

RULES: each piece must stand alone and give value even if nobody clicks. No hype,
no fear, no jargon. Lead with the analogy or the reader's feeling. One link max each.
No em dashes (—) or ellipses (… / ...) — use periods and commas, short sentences.
```

## Tuning notes
- Save winning subject lines; reuse the pattern.
- Ask for "3 more social variants" to fill a week without rewriting the article.
