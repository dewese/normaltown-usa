# Pipeline Station 8 — Publish (self-hosted web)

> The site is a zero-cost, self-hosted static blog that Claude writes AND publishes.
> Live at https://www.normaltownusa.com (Cloudflare, GitHub repo `dewese/normaltown-usa`).

## Where a post lives
`Posts/<YYYY>/<MM>/<DD>/` — the folder date IS the publish date. Files:
- `article.md` — the post. **First `# ` line = the title.** Body follows. No email CTA.
- `publish.md` — metadata table the builder reads (see template below).
- one `<name>.png` — the hero image (1200×1200, VV style, PNG not SVG). Keep the .svg too.

## `publish.md` template (builder parses these rows)
```
# Publish — <Title>

| Field | Value |
|---|---|
| **URL slug** | `kebab-case-slug` |
| **Title tag** | `Optional keyword-first SEO title, ≤70 chars (H1 stays the hooky one)` |
| **Subtitle** | `One-line subtitle shown under the title.` |
| **Meta description** | `~150-char search/social description (hard max 160).` |
| **Category** | Money  (or Health, or Bitcoin) |

- **Image:** `<name>.png` — Alt text: `plain description of the graphic`.
- **Internal links:** list the /p/<slug>/ posts linked in the body.
- **Affiliate:** CrowdHealth referral present? yes/no (if yes: disclosure + limits in body).
```
The builder auto-derives the slug/description if a row is missing, but always set them.

## `article.md` SEO/GEO structure (added 2026-09-06, every post has it)
```
# Title

> In short: a 40-70 word self-contained answer with a specific number in it. This is
> the box AI answer engines lift, so it must stand alone. One blockquote, right here.

...body, with ## question-shaped headings, one analogy, "## The takeaway"...

## Questions I get about this

### A real question someone would type?

40-70 word answer in David's voice. Link the related post with a root-relative
link like [text](/p/slug/). 3-4 questions per post.

*standard disclaimer if CrowdHealth is mentioned*
```
Rules: root-relative links (`/p/slug/`, trailing slash), no em dashes/ellipses, numbers
where possible (GEO rewards fact density), first person. Linking to a post that isn't
live yet is fine: the builder shows plain text until the day it publishes.

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
its date. This is now automated:
- **Machine (live):** `.github/workflows/daily-publish.yml` runs every day at ~9am
  Eastern (13:00 UTC), rebuilds, and commits/pushes `dist/` if it changed, so that
  day's post auto-releases. You can also trigger it by hand: repo → Actions →
  "Daily publish" → Run workflow. `build.py` uses Eastern time for the date gate.
- **Manual fallback:** run steps 2 + 4 yourself any morning.

## Voice + rules still apply
Stations 1–5 (topic → outline → draft → fact-check → repurpose) are unchanged. Keep
the voice spec (plain English, one analogy, no em dashes, no ellipses) and Station 6
(value-first, disclose affiliate, state the honest limits). Graphics = Station 7 (VV
style: soft-black, white line art, one cyan accent, Manrope, labels, no baked-in title).
