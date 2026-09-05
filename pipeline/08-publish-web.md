# Pipeline Station 8 — Publish (self-hosted web) — REPLACES beehiiv (2026-09)

> The brand left beehiiv (~$50/mo, and its API can't publish anyway). The site is
> now a zero-cost, self-hosted static blog that Claude writes AND publishes.
> Live at https://www.normaltownusa.com (Cloudflare, GitHub repo `dewese/normaltown-usa`).

## Where a post lives
`Posts/<YYYY>/<MM>/<DD>/` — the folder date IS the publish date. Files:
- `article.md` — the post. **First `# ` line = the title.** Body follows. No email CTA.
- `publish.md` — metadata table the builder reads (see template below).
  (Legacy posts use `publish-beehiiv.md`; the builder still reads that as a fallback.)
- one `<name>.png` — the hero image (1200×1200, VV style, PNG not SVG). Keep the .svg too.

## `publish.md` template (builder parses these rows)
```
# Publish — <Title>

| Field | Value |
|---|---|
| **URL slug** | `kebab-case-slug` |
| **Subtitle** | `One-line subtitle shown under the title.` |
| **Meta description** | `~150-char search/social description.` |
| **Category** | Money  (or Health) |

- **Image:** `<name>.png` — Alt text: `plain description of the graphic`.
- **Internal links:** list the /p/<slug>/ posts linked in the body.
- **Affiliate:** CrowdHealth referral present? yes/no (if yes: disclosure + limits in body).
```
The builder auto-derives the slug/description if a row is missing, but always set them.

## Date-gated publishing (write ahead safely)
`build.py` **only publishes posts dated today or earlier.** Future-dated folders are
written but held until their day. So you can draft a whole month now; each post goes
live on its date the next time the site is built.

## Publish flow (what "publish" means now)
1. Add/finish the post folder under `Posts/…`.
2. `python3 build.py`   (regenerates `dist/`)
3. `python3 serve.py` → http://127.0.0.1:8787 to preview (optional).
4. `git add -A && git commit -m "Add post: <title>" && git push`
   → Cloudflare redeploys in ~1 min. Done.

## Releasing a future-dated post on its day
Because a static site only changes when rebuilt, a scheduled post needs a rebuild on
its date. Two options:
- **Manual:** run steps 2 + 4 that morning.
- **Machine (recommended, TODO):** a daily GitHub Action cron that runs `build.py`,
  commits `dist/` if it changed, and pushes — auto-releasing that day's post.

## Voice + rules still apply
Stations 1–5 (topic → outline → draft → fact-check → repurpose) are unchanged. Keep
the voice spec (plain English, one analogy, no em dashes, no ellipses) and Station 6
(value-first, disclose affiliate, state the honest limits). Graphics = Station 7 (VV
style: soft-black, white line art, one cyan accent, Manrope, labels, no baked-in title).
