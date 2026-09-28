# CrowdHealth Fact Verification Checklist

> **Why this exists:** `06-cta-affiliate.md` feeds every CrowdHealth post on the site, so
> one stale number there is a wrong number in fifty places. It was last verified
> 2026-09-03. Several figures in it now conflict with 2026 sources.
>
> **This cannot be done by an agent from the build environment.** `joincrowdhealth.com`
> and the major comparison sites are blocked by the network proxy (403 at the CONNECT
> tunnel). David has to open these pages himself.
>
> **Cadence:** monthly. Stamp the date at the bottom of `06-cta-affiliate.md` each time.

## Pages to open

1. https://www.joincrowdhealth.com/pricing
2. https://www.joincrowdhealth.com/how-it-works
3. https://www.joincrowdhealth.com/resources/member-guide
4. https://www.joincrowdhealth.com/resources/faq
5. https://www.joincrowdhealth.com/resources/referral-program  (log in, check YOUR code)
6. https://www.joincrowdhealth.com/monthly-cost-insights
7. https://www.joincrowdhealth.com/longevity-discount-program  (new, not on our site at all)
8. https://www.trustpilot.com/review/joincrowdhealth.com
9. https://insurance.maryland.gov/Consumer/Pages/ConsumerAdvisory-MIA-warns-of-risks-involved-in-crowd-funding-healthcare-payment-platform-CrowdHealth.aspx

## The rows that are in dispute

Fill in the right-hand column from the source, then correct `06-cta-affiliate.md`.

| # | What our file currently says | What 2026 search results suggest | Verified value | Source page |
|---|---|---|---|---|
| 1 | ~~37,000+ members~~ | ~15,000 to 17,000 | **VERIFIED 2026-09-28 by David.** Roughly 15,000 to 17,000. The old figure was wrong by more than 2x. Corrected everywhere. | member/company |
| 2 | ~~45,000+ bills funded~~ | 53,877 lifetime | **VERIFIED 2026-09-28 by David.** **53,877**. Corrected in 13 places. Pair it with row 11: 53,877 bills across ~16k members is 3+ funded bills per member. Do not cite the "32 unfunded" figure, that one is still unconfirmed. | member/company |
| 3 | ~~$60/mo flat + variable contributions, no cap mentioned~~ | $60 base, contributions capped ~$140/mo per adult under 55 | **VERIFIED 2026-09-21 by David from his member account.** $60/mo per person incl. children. Crowd ask hard-capped: $140 (0-54), $280 (55-64), $420 (family of 4+, household). Worst case all in: $200 / $340 / $660. Crowd historically rarely asks the full share. | member account |
| 4 | Pre-existing: ineligible yrs 1 to 2, then $25k/yr cap from yr 3 | ~~One source describes a 6-month waiting period~~ | **VERIFIED 2026-09-28 by David.** **Our copy was right, the 6-month claim was wrong.** Verbatim rules now in the fact sheet. New detail: **high cholesterol and high blood pressure are exempt.** | member guide |
| 5 | 4.9 Trustpilot, 1,000+ reviews | ~~4.6 in a 2026 roundup~~ | **VERIFIED 2026-09-28 by David.** **4.9 confirmed, our copy was right.** trustpilot.com/review/joincrowdhealth.com | Trustpilot |
| 6 | Referral NORMAL = 3 months at $99 | ~~Coupon sites advertise $99/mo for 6 months~~ | **VERIFIED 2026-09-21 by David: member referral discounts are 3 months only.** Site copy was already correct. The coupon-aggregator "6 months" claims are wrong or stale; do not repeat them. | member account |
| 7 | ~~$86.7M saved~~ | ~$100M | **VERIFIED 2026-09-28 by David.** ~$100 million total, CrowdHealth's own figure via their Instagram. Weak surface for a dollar claim, so always attribute to them. Never appeared in a post, only the fact sheet. | company Instagram |
| 8 | Largest bills: $643K / $437K / $333K | not re-confirmed | **STILL OPEN.** Currently published in several posts as "single bills over $600,000". Sourced 2026-09-03, so not wrong, just stale. | |
| 9 | ~7 days bill to funded, ~2 days to reimburse | not re-confirmed | **STILL OPEN.** Published as "about a week on average". Sourced 2026-09-03, stale not wrong. | |
| 10 | State notes: VT, CA, MA, NJ, RI, DC | MD advisory added March 2026 | **STILL OPEN, and the most consequential one left.** The list does not include Maryland. Needed before the state-by-state page. | |
| 11 | (was not in our file) 99.8% of bills funded | strong honest stat | **VERIFIED 2026-09-28 by David.** **True.** Now used alongside row 2. | member/company |
| 12 | (was not in our file) Longevity Discount Program | exists | **VERIFIED 2026-09-28 by David.** Real, and still mentioned nowhere on the site. joincrowdhealth.com/longevity-discount-program | company |

## Rows 3 and 6 matter most

**Row 3, the contribution cap.** If contributions really are capped per adult, that is a
selling point the site is not using, and right now our posts describe an open-ended
monthly cost. Readers comparing to a deductible need the cap to make the comparison.

**Row 6 is settled and the alarm was false.** Member referral discounts are three months,
full stop. The "$99 for six months" on the coupon aggregators is wrong or stale, so the
site's copy was right all along and no post needs changing. Never cite those aggregators
as a source.

Still worth doing, just not as a fix: ask CrowdHealth what a *partner* arrangement looks
like, as distinct from the standard member referral. They have a "Manager, Crowd and
Influencer Marketing" role posted, so there is a person whose job this is, and a site with
50+ posts and four years of member history is a different proposition from a member
passing a code to a friend.

## Where each number appears, so nothing gets missed

After correcting `06-cta-affiliate.md`, grep the posts. These numbers are hard-coded in
article bodies, not pulled from the pipeline file at build time:

```
grep -rn "37,000\|45,000\|4\.9\|86\.7\|643K\|\$25,000\|5 yrs\|five years" Posts/ site/
```

Every hit is a post that needs the same correction, and per
`/how-i-keep-this-accurate/` a real correction gets an `Updated` row in its
`publish.md`, not a silent edit.

## Also confirm before the redesign

- Does CrowdHealth still describe itself as "healthcare crowdfunding" rather than
  "health sharing"? Thirty September posts are titled with a phrase the company avoids.
  This decides how much of the September batch gets re-titled.
