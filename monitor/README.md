# Site monitor

Scripts that check how the live site is doing. Standard library only (plus the `openssl`
command for Google sign-in). Everything they write goes to `monitor/private/`, which is
git-ignored: this repo is public, and traffic numbers, roadmaps and keys stay on this Mac.

| Script | What it checks | Needs |
|---|---|---|
| `techcheck.py` | Every sitemap page: status, title, meta, canonical, JSON-LD, alt text, broken links, referral codes, robots.txt, redirects, 404, headers | nothing |
| `pagespeed.py` | Lighthouse scores + Core Web Vitals (lab and real-user) for key pages, mobile and desktop | PageSpeed API key |
| `google_data.py` | Search Console (clicks, queries, positions, striking distance, gaps, index status) and GA4 (sessions, channels, landing pages, key events, AI referrals) | service account |

```
monitor/private/
  config.json                       {"psi_api_key": "...", optional "gsc_site", "ga4_property"}
  google-service-account.json       key file from Google Cloud
  reports/YYYY-MM-DD-*.md / .json   one set per run; each run compares with the previous one
  weekly/YYYY-MM-DD.md              the weekly summary written by the scheduled task
  roadmap-development.md            technical roadmap, updated weekly
  roadmap-content.md                content roadmap, updated weekly
```

## Schedule (Claude desktop app → scheduled tasks)

- **Daily, 7:30am:** `techcheck.py`. A notification only when something is broken.
- **Weekly, Monday 8am:** all three scripts with `--inspect` + beehiiv stats → `weekly/<date>.md`,
  both roadmaps updated, notification with the top 3 actions.

These run only while the Mac is awake and the Claude app is open. A missed run starts the next
time the app opens.

## One-time Google setup (about 15 minutes)

1. Go to https://console.cloud.google.com and create a project (any name, e.g. `normaltown-monitor`).
2. **APIs & Services → Library**: enable *Google Search Console API*, *Google Analytics Data API*,
   *Google Analytics Admin API* and *PageSpeed Insights API*.
3. **APIs & Services → Credentials → Create credentials → API key.** Restrict it to the PageSpeed
   Insights API. Paste it into `monitor/private/config.json` as `psi_api_key`.
4. **IAM & Admin → Service Accounts → Create service account** (e.g. `normaltown-reader`, no roles).
   Open it → **Keys → Add key → JSON**. Save the downloaded file as
   `monitor/private/google-service-account.json`. Copy the account's email (…@….iam.gserviceaccount.com).
5. **Search Console** → Settings → Users and permissions → Add user → that email → *Restricted*.
6. **GA4** → Admin → Property access management → + → that email → *Viewer*.

Then test: `python3 monitor/google_data.py` and `python3 monitor/pagespeed.py --quick`.

The service account can only read. To revoke it, delete the key in Google Cloud or remove the
user in Search Console / GA4.
