# October 2026 — "CrowdHealth Fanboy" Member Stories

**Goal:** show how CrowdHealth works in real health situations, one kind per day, so a
reader can find the story closest to their own worry. Referral code **NORMAL**.

**Written and scheduled 2026-09-30.** Oct 1 to 3 were already taken by the three branded
posts (`crowdhealth-cost`, `crowdhealth-pre-existing-conditions`, `is-crowdhealth-legit`),
so the series runs **Oct 4 to 31** (28 posts). Three finished posts that did not fit are
parked in `pipeline/drafts/october-2026/`.

## Rules this series follows (set by David, 2026-09-30)

- **Real member situations only.** Sources: public Trustpilot reviews, members' own blogs,
  news coverage (TIME, Forbes, Bangor Daily News), and material CrowdHealth published
  (member stories, case study, monthly Transparency Files, webinar).
- **No names, no towns, no employer or other identifying detail.** Situations are retold in
  general terms. Where a public story had a rare combination of details, some were dropped.
- **Own words.** At most one short quoted phrase per post. No copied passages.
- **No dollar figure unless the source states it.** Where sources disagree (the accidental
  gunshot story has three different totals), the post says so.
- **Sourcing is in text, not links.** Each post ends with an italic "About this story" line
  naming the kind of source. **No links to the original stories.**
- **Every outbound link is a CrowdHealth page carrying `?referral_code=NORMAL`.** The code
  works on any joincrowdhealth.com URL (all returned HTTP 200 on 2026-09-30), so each post's
  CTA goes to the page that fits the topic: `/how-it-works`, `/pricing`, `/pregnancy`,
  `/crowdfunding-results`, `/member-tools-and-services`, `/monthly-cost-insights`,
  `/member-guides`, `/resources/faq`. The Sources box links CrowdHealth's own pages the
  same way. `/pregnancy` exists but is not in their navigation.
- **Honest ratio.** About one post in four is a story where it went badly or a limit bit:
  10/12, 10/14 (half), 10/20, 10/23, 10/27, 10/28, 10/29, 10/30.
- **Nothing is invented about David's own family.** The posts say "my family of four has
  used it since 2022" and stop there. Real first-hand detail would make these stronger.

## Schedule

| Day | Slug | Situation | Main source type |
|---|---|---|---|
| 10/04 | `why-im-a-crowdhealth-fanboy` | Series intro and rules | CrowdHealth published numbers |
| 10/05 | `toddler-medevac-30000-in-bills` | Toddler medevac to pediatric ICU, $30k+, $500 paid | Trustpilot |
| 10/06 | `the-35000-appendix-that-cost-500` | Emergency appendectomy, $35,000 to $10,600 | CrowdHealth story + Trustpilot |
| 10/07 | `one-heart-procedure-three-prices` | Heart rhythm procedure, three hospital quotes | CrowdHealth story (2022) |
| 10/08 | `having-a-baby-on-crowdhealth` | Pregnancy, $3,000 commitment, 300-day rule | Trustpilot + member blogs |
| 10/09 | `the-240000-nicu-bill` | NICU stay, $240,000+ | CrowdHealth video/webinar |
| 10/10 | `kidney-stones-funded-in-under-two-weeks` | Kidney stone surgery, paid back in under two weeks | Trustpilot |
| 10/11 | `broken-bones-on-crowdhealth` | Broken ankle, elbow, arm | Trustpilot |
| 10/12 | `the-10000-bill-the-crowd-never-saw` | Pre-existing denial, $10,000 (negative) | Trustpilot 1-star |
| 10/13 | `cancer-a-few-months-after-joining` | Stage 4 melanoma, $100k+ per treatment | CrowdHealth video + Trustpilot |
| 10/14 | `two-hernia-surgeries-two-different-stories` | Hernia: one smooth, one fair-price gap | Trustpilot 5-star and 2-star |
| 10/15 | `his-heart-stopped-for-four-minutes` | Cardiac arrest, bypass; stroke | Trustpilot |
| 10/16 | `the-mri-that-took-two-weeks` | MRI and imaging | Trustpilot + CrowdHealth video |
| 10/17 | `blood-work-262-last-year-36-this-year` | Lab work, $262 to $36 | Trustpilot |
| 10/18 | `sick-on-a-sunday` | Virtual visit, $6 prescription | Trustpilot + member blogs |
| 10/19 | `the-er-bill-one-phone-call` | ER visits, $4,142 to $1,657 | Member blog + Trustpilot |
| 10/20 | `when-the-hospital-wont-negotiate` | Collections during negotiation (negative) | Trustpilot 3- and 4-star |
| 10/21 | `a-new-hip-for-500` | Hip and knee replacement | CrowdHealth story + independent review |
| 10/22 | `torn-knees-and-sprained-ankles` | ACL, ankle, physical therapy | Trustpilot + member blog |
| 10/23 | `six-routine-visits-one-covered` | Routine care limits (negative) | Trustpilot 2-star |
| 10/24 | `tonsils-ear-tubes-and-other-kid-surgeries` | Kids' surgeries, founder's ear tube bill | Trustpilot + CrowdHealth |
| 10/25 | `the-freak-accident` | Accidental gunshot, boating accident | CrowdHealth videos |
| 10/26 | `the-48000-quote-that-became-9190` | Hysterectomy quote negotiated | CrowdHealth case study + Trustpilot |
| 10/27 | `the-paperwork-is-real` | Paperwork burden (negative) | Trustpilot 3- and 4-star |
| 10/28 | `when-the-bill-is-under-500` | Bills under $500 | Member blog + Trustpilot 3-star |
| 10/29 | `the-fine-print-that-catches-new-members` | Ten rules that surprise people (negative) | Trustpilot 1- and 2-star, complaints log |
| 10/30 | `what-the-critics-say-about-crowdhealth` | The case against, fairly stated | TIME, Forbes, Bangor Daily News, Maryland advisory |
| 10/31 | `what-a-month-of-member-stories-taught-me` | Wrap-up and who it fits | All of the above |

## Parked, ready to publish (`pipeline/drafts/october-2026/`)

- `when-the-birth-plan-changes` (home birth to C-section, NICU as a separate $500 event)
- `gallbladder-surgery-funded-before-the-first-cut`
- `the-stories-about-loss` (miscarriage; sensitive, publish only if David wants it up)

Each has article.md, publish.md, and its hero svg/png. To publish: move the folder to
`Posts/<year>/<month>/<day>/`, run `python3 brand/theme-hero-svgs.py && python3 build.py`.

## Things to re-check before reusing any of this

- Research notes with source URLs are in `pipeline/research-private/` (git-ignored, local
  only, because they contain reviewer details). Trustpilot figures were re-read on
  2026-09-30 for the posts that lean on a number.
- The 2027 member guide changes (fee to $65, 15-visit therapy limit, flexible $300
  wellness, $129 virtual visits) are noted in 10/04, 10/18, 10/22, 10/23, 10/24, 10/29.
  After January 1, 2027 those "starting in 2027" lines need a tense pass.
