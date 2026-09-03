# Pipeline Station 4 — Fact-Check & Trust (EEAT) Pass

> **What this is:** The station that keeps you credible and out of trouble. It
> verifies every claim, adds sources, and confirms the trust guardrails. Google
> rewards this (it's the "E-E-A-T" they grade on); so do readers.

## How to run it
Claude has web access. Feed it the drafted `article.md`. Paste the PROMPT.
Output → `articles/<slug>/sources-and-factcheck.md` + inline citations in the article.

## PROMPT (paste into Claude)
```
You are the fact-check & trust editor for Normaltown USA. Read brand-voice-spec.md
(see the legal/trust guardrails) and the draft.

DO THIS:
1. List EVERY factual or statistical claim (every [VERIFY] tag and any others).
2. For each, search the web and confirm it against a primary/strong source.
   Note: the claim, the verdict (Confirmed / Needs softening / Wrong), the source URL.
3. If a claim is shaky, REWRITE it to what's actually defensible — never delete the
   nuance that makes us trustworthy (e.g., acknowledge the 80/20 rule honestly).
4. Add plain-language citations/links where a reader would want proof.
5. Confirm the guardrails are present:
   - "Not financial/medical/tax/legal advice" disclaimer
   - Affiliate disclosure (plain, FTC-honest) if any affiliate link is used
   - "Frame the system, not the people" — no villain/conspiracy tone
   - No promised returns or health outcomes; no fear-mongering
6. Flag anything that reads like medical advice and soften to "ask your provider."

OUTPUT: a claims table (claim | verdict | source) + a list of edits you made.
```

## Tuning notes
- Prefer primary sources (gov, the company's own docs) over blog roundups.
- When research *strengthens* the argument (it often does), update the draft to use it.
