# Pipeline Station 1 — The Topic Engine

> **What this is:** A reusable prompt that generates a backlog of article ideas for
> Normaltown USA, each one mapped to a real search, a money-bucket, and an analogy
> hook. Run it whenever the backlog runs low. It's the front of the assembly line —
> it decides what the machine writes next.

---

## How to run it

Paste the **PROMPT** block below into Claude. Before you do, make sure Claude has
read `brand-voice-spec.md` (it carries the voice, the reader, and the money-buckets).
Tell it how many ideas you want and, optionally, which pillar to focus on.

Output lands in `pipeline/topic-backlog.md` — your runway of things to write.

---

## The thinking behind it (so you can tune it)

A good content engine isn't random blog posts — it's **clusters**. We pick a few
big "pillar" themes the reader cares about, then write many small articles that
each answer one specific question inside that pillar, all linking back to the
pillar. Google rewards this (it signals you're an authority on the whole topic),
and readers fall down a helpful rabbit hole that grows your email list.

Every idea the engine produces must carry six tags so you can prioritize at a glance:

1. **Working title** — written in the reader's words, not ours.
2. **The search** — the actual thing a 35–55 worried parent types into Google.
3. **Intent** — are they trying to *understand* something, *compare* options, or
   *do/buy* something? (Buy-intent topics earn money sooner; understand-intent
   topics build trust and rank easier.)
4. **Money-bucket** — `Trust` (pure value), `Health→CrowdHealth`, or `Money/Bitcoin`.
   (From the voice spec. Value first, pitch second, always.)
5. **Analogy hook** — the one Anil-Patel-style picture that makes it click (a leaky
   bucket, a rigged carnival game, a tire losing air). If we can't find an analogy,
   the topic isn't ready.
6. **Effort/competition** — `Easy win` (low competition, we can rank fast) vs.
   `Long game` (competitive, worth it eventually).

---

## PROMPT (paste this into Claude)

```
You are the topic engine for Normaltown USA. First, read and fully internalize
brand-voice-spec.md — the reader, the voice, the three core beliefs, and the
three money-buckets. Everything you produce must fit that spec: plain words,
simple analogies, never assume prior knowledge, no jargon, no "fiat," no hype.

INSPIRATION TO MATCH:
- Anil Patel (The Bitcoin Handbook / Visualizing Bitcoin): one idea explained
  with ONE memorable analogy and zero jargon. "No interest in sounding smart."
- Chris J. Koerner / @mhp_guy: plainspoken, practical, friend-across-the-table.
- The reader: married, 35–55, job + family, does everything right but still
  just getting by, still gets surprise medical bills. Gut feeling: "Why can't I get ahead when I'm doing it all right?"

YOUR JOB:
Generate {N} article ideas, organized under these PILLARS:

  PILLAR A — "Why am I still broke when I'm doing everything right?"
    (everyday money leaks, budgeting that respects busy people, the slow
     loss of the dollar's value explained simply)
  PILLAR B — "The health-bill trap" — anchored by the THESIS that the health
     industry profits from *managing* sickness, not from making people well
     (misaligned incentives; the mechanic paid by the visit). From there: why
     insured people still get crushed by bills, how self-pay/cash pricing works,
     and an honest look at health sharing like CrowdHealth (paid by a flat fee,
     not by denying claims) — including its real limits. Frame the system, not
     the people: most doctors want you well; it's the money plumbing that's
     pointed the wrong way.
  PILLAR C — "Saving in something that doesn't shrink" (preserving what you
     earn; bitcoin as savings-not-gambling, built up from first principles
     using Anil-style analogies)

For EACH idea, output a row with these six fields:
  1. Working title (in the reader's words)
  2. The search (exact phrase they'd Google)
  3. Intent (Understand / Compare / Do-or-Buy)
  4. Money-bucket (Trust / Health→CrowdHealth / Money-Bitcoin)
  5. Analogy hook (one plain-English picture — REQUIRED; if none, drop the idea)
  6. Effort (Easy win / Long game)

RULES:
- Spread ideas across all three pillars; mark which pillar each belongs to.
- At least 40% must be "Easy win" (specific, low-competition, long-tail searches
  like "why is my blood test bill so high if I have insurance").
- Health→CrowdHealth ideas must be honest: they earn the recommendation by
  genuinely helping, and they acknowledge CrowdHealth isn't insurance and has
  exclusions. Never bait-and-switch.
- Every analogy hook must pass the "huh, yeah" test from the voice spec.
- Avoid duplicate angles. Each idea = one distinct search a real person makes.

OUTPUT FORMAT:
A markdown table grouped by pillar, columns in the order above, plus a final
"Top 5 to write first" list with one sentence each on why (best mix of easy-win
+ money-bucket + reader urgency).
```

---

## Tuning notes (edit over time)

- If ideas feel too broad, tell it to go **more long-tail** ("only searches a
  real person types, 5+ words, low competition").
- To lean into a revenue push, ask for **more Health→CrowdHealth** ideas — but
  keep the value-first rule or you'll burn trust (and rankings).
- Reuse winners: when an article does well, run this engine again and ask for
  "10 follow-up ideas that link to [that article]" to build out the cluster.
