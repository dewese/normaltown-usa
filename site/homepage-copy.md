# Homepage Copy v2 (messaging-score fixes)

Created 2026-07-21 in response to a third-party clarity/messaging audit of
normaltownusa.com. Scores: Clarity 82, Audience 78, Value 76, Action 71.

Root cause across all four: every line describes HOW we talk (plain English,
from a friend, no jargon, no scare tactics) and none describes WHAT the reader
gets. Tone is the packaging, not the product. All fixes below add outcomes.

Style guardrails hold: no em dashes, no ellipses, plain English, polite, no cursing.

---

## 1. TAGLINE (SITE_TAGLINE in build.py)

CURRENT: Money and health, from a friend

NEW: Keep more of the money you already make

Why: "from a friend" is a tone promise. "Keep more of the money you already
make" is an outcome promise, and it is the single frame that makes money AND
health one topic instead of two. Warmth is not lost, it is carried by the
subhead and by the writing itself.

Runner-up if a shorter slot is needed: More of your money stays yours


## 2. SUBHEAD (the line directly under the tagline)

NEW: Written by a regular guy with a full-time job, for regular people with
full-time jobs. Every post is one specific thing you can do to spend less,
owe less, or bring in a little more.

Why: this is the AUDIENCE fix. It names exactly who the reader is and puts the
"from a friend" warmth in a place where it earns its keep.


## 3. THE SPLIT-FOCUS FIX (money vs health)

The audit dinged the money/health split as ambiguous. One sentence resolves it.
Place it under the subhead or as the first line of the About/Start Here box.

NEW: Health is in here because a medical bill is the biggest money leak most
families have. It is a money problem wearing a lab coat.

Why: this converts an apparent two-topic site into a one-topic site with two
beats. Nothing about the content has to change.


## 4. ABOVE THE SUBSCRIBE FORM (the audit's "FIX FIRST" item)

This is the exact thing the audit asked for: what the reader will know or be
able to do after reading that they cannot do now.

NEW: Read for one month and you will know how to ask for the cash price on a
medical bill, name the leaks quietly draining your paycheck, and build a first
$1,000 cushion so a surprise bill is not a crisis. Almost nobody teaches this,
because almost nobody gets paid to.

Why: three concrete, verifiable capabilities and a time frame. The last line
echoes the cornerstone post's thesis, which ties the promise to proof already
on the page.


## 5. OPT-IN PROMISE (replaces current subscribe blurb)

CURRENT: The plain-English money newsletter for normal people. No jargon, no
scare tactics. One short email. Unsubscribe anytime.

NEW: One short email each morning with one thing you can actually do that day.
Five minutes to read, and the first one arrives tomorrow. No jargon, no scare
tactics, unsubscribe anytime.

Why: VALUE fix. The old version led with what we will NOT do. The new one leads
with cadence, effort, and payoff, then keeps the guardrail phrases as a closer
where they belong. "The first one arrives tomorrow" is the ACTION fix: it gives
a reason to subscribe today rather than browsing the free archive.

NOTE: only claim "each morning" while the daily cadence actually holds. If the
schedule loosens, change this line to "Two or three mornings a week."


## 6. STRUCTURAL FIXES (not copy, but they move Clarity and Action)

a) Publish site/start-here.md and pin it. Slug `start-here`. A new reader
   currently lands on a reverse-chronological list with no entry point.
   Verify the three featured posts are live first.

b) Add a real headshot to the About page (site/author-bio.md). Right now the author page is empty, so "from a friend" has no
   friend attached to it. This is the largest single trust lever available.

c) Homepage title tag: change "Home | Normaltown USA" to
   "Normaltown USA: Plain-English Money and Health for Regular People"

d) Fill the empty og:description and twitter:description with the canonical
   meta description.

e) Fix the post #2 slug to `what-is-health-sharing` so the four internal links
   pointing at it stop 404ing.


## 7. THE MISSING OFFER (consulting / coaching)

Stated business goal includes private consulting and coaching, and there is
currently zero surface area for it on the site. Nobody can hire someone whose
site does not say they are hireable. Minimum viable version, as one line in the
footer or at the bottom of the Start Here page:

NEW: Stuck on a specific bill or a money decision and want a second set of
eyes? Reply to any email. I read every one, and I take on a few people a month
for one-on-one help.

Why: "reply to any email" costs nothing to offer, needs no booking page, and
turns the newsletter into the top of the coaching funnel. It also raises reply
rate, which helps deliverability.

Build the real version later: a /work-with-me page with scope, price, and a
booking link, once there is enough inbound to justify it.


## PASTE ORDER (highest impact first)

1. Item 4 (above the subscribe form) - the audit's explicit fix-first
2. Item 5 (opt-in promise)
3. Item 1 + 2 (tagline + subhead)
4. Item 6b (author bio + headshot)
5. Item 6a (publish and pin Start Here)
6. Item 3 (money/health bridge line)
7. Item 7 (coaching line)
8. Item 6c/d/e (SEO cleanup)
