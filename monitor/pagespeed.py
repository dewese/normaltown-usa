#!/usr/bin/env python3
"""PageSpeed Insights (Lighthouse lab data + Chrome real-user field data) for key pages.

Needs a free Google API key with the "PageSpeed Insights API" enabled, saved as
  monitor/private/config.json  ->  {"psi_api_key": "..."}
(or the PSI_API_KEY environment variable). Google set the keyless quota to zero.

Pages tested: home, hubs, the top posts in PAGES below, plus the 3 newest posts in the
live sitemap. Mobile and desktop. Writes monitor/private/reports/<date>-pagespeed.json/.md
and flags any score that dropped 10+ points or any metric that crossed into "poor".

Usage: python3 monitor/pagespeed.py [--quick]   (--quick = home + 2 pages, mobile only)
Exit 2 = no API key; 1 = a page failed a Core Web Vitals threshold; 0 = fine.
"""
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://www.normaltownusa.com"
ROOT = Path(__file__).resolve().parent
PRIVATE = ROOT / "private"
REPORTS = PRIVATE / "reports"
PAGES = ["/", "/crowdhealth/", "/health/", "/bitcoin/",
         "/p/crowdhealth-pre-existing-conditions/", "/p/cancer-a-few-months-after-joining/",
         "/p/crowdhealth-cost/", "/p/is-crowdhealth-legit/"]
# Google's "good" / "poor" thresholds (lab LCP/CLS/TBT; field LCP/CLS/INP)
LAB = {"largest-contentful-paint": ("LCP", 2500, 4000, "ms"),
       "cumulative-layout-shift": ("CLS", 0.1, 0.25, ""),
       "total-blocking-time": ("TBT", 200, 600, "ms"),
       "first-contentful-paint": ("FCP", 1800, 3000, "ms")}
FIELD = {"LARGEST_CONTENTFUL_PAINT_MS": "LCP", "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
         "INTERACTION_TO_NEXT_PAINT": "INP"}


def api_key():
    if os.environ.get("PSI_API_KEY"):
        return os.environ["PSI_API_KEY"]
    cfg = PRIVATE / "config.json"
    if cfg.exists():
        return json.loads(cfg.read_text()).get("psi_api_key")
    return None


def run(url, strategy, key):
    q = urllib.parse.urlencode([("url", url), ("strategy", strategy), ("key", key),
                                ("category", "performance"), ("category", "accessibility"),
                                ("category", "best-practices"), ("category", "seo")])
    try:
        with urllib.request.urlopen(f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?{q}",
                                    timeout=120) as r:
            d = json.load(r)
    except urllib.error.HTTPError as e:
        return {"url": url, "strategy": strategy, "error": f"{e.code} {e.read()[:200]!r}"}
    except Exception as e:
        return {"url": url, "strategy": strategy, "error": str(e)}
    lr = d.get("lighthouseResult", {})
    out = {"url": url, "strategy": strategy,
           "scores": {k: round((v.get("score") or 0) * 100) for k, v in lr.get("categories", {}).items()},
           "lab": {}, "field": {}, "opportunities": []}
    for audit, (name, good, poor, unit) in LAB.items():
        v = lr.get("audits", {}).get(audit, {}).get("numericValue")
        if v is not None:
            out["lab"][name] = {"value": round(v, 3 if not unit else 0),
                                "rating": "good" if v <= good else "poor" if v > poor else "needs work"}
    for m, name in FIELD.items():
        f = d.get("loadingExperience", {}).get("metrics", {}).get(m)
        if f:
            out["field"][name] = {"p75": f.get("percentile"), "rating": f.get("category")}
    for a in lr.get("audits", {}).values():
        sav = (a.get("details") or {}).get("overallSavingsMs") or 0
        if a.get("score") is not None and a["score"] < 0.9 and sav >= 150:
            out["opportunities"].append({"title": a.get("title"), "savings_ms": round(sav)})
    out["opportunities"].sort(key=lambda o: -o["savings_ms"])
    out["failed_audits"] = sorted(a.get("title") for k, a in lr.get("audits", {}).items()
                                  if a.get("score") == 0 and a.get("scoreDisplayMode") == "binary")
    return out


def main():
    key = api_key()
    REPORTS.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    if not key:
        msg = "PageSpeed skipped: no API key in monitor/private/config.json (psi_api_key)."
        (REPORTS / f"{today}-pagespeed.md").write_text(f"# PageSpeed {today}\n\n{msg}\n")
        print(msg)
        sys.exit(2)
    quick = "--quick" in sys.argv
    pages = PAGES[:3] if quick else list(PAGES)
    if not quick:
        with urllib.request.urlopen(SITE + "/sitemap.xml", timeout=30) as r:
            sm = r.read().decode()
        posts = sorted(re.findall(r"<loc>([^<]+/p/[^<]+)</loc><lastmod>([^<]+)</lastmod>", sm),
                       key=lambda x: x[1], reverse=True)
        for u, _ in posts[:3]:
            path = urllib.parse.urlsplit(u).path
            if path not in pages:
                pages.append(path)
    jobs = [(SITE + p, s) for p in pages for s in (("mobile",) if quick else ("mobile", "desktop"))]
    with cf.ThreadPoolExecutor(4) as ex:
        results = list(ex.map(lambda j: run(j[0], j[1], key), jobs))

    prev = sorted(p for p in REPORTS.glob("*-pagespeed.json") if not p.name.startswith(today))
    old = {}
    if prev:
        for r in json.loads(prev[-1].read_text()).get("results", []):
            old[(r["url"], r["strategy"])] = r
    alerts = []
    for r in results:
        if "error" in r:
            alerts.append(f"{r['strategy']} {r['url']}: API error {r['error'][:120]}")
            continue
        for name, m in {**r["lab"], **r["field"]}.items():
            if m["rating"] in ("poor", "SLOW"):
                alerts.append(f"{r['strategy']} {r['url']}: {name} is poor ({m.get('value', m.get('p75'))})")
        o = old.get((r["url"], r["strategy"]))
        if o and "scores" in o:
            for cat, sc in r["scores"].items():
                if cat in o["scores"] and o["scores"][cat] - sc >= 10:
                    alerts.append(f"{r['strategy']} {r['url']}: {cat} score fell {o['scores'][cat]} -> {sc}")
    (REPORTS / f"{today}-pagespeed.json").write_text(json.dumps(
        {"date": today, "results": results, "alerts": alerts,
         "compared_with": prev[-1].name if prev else None}, indent=1))

    lines = [f"# PageSpeed {today}", "", f"{len(jobs)} tests. **{len(alerts)} alerts.**", ""]
    lines += [f"- {a}" for a in alerts] + ([""] if alerts else [])
    lines += ["| Page | Device | Perf | A11y | BP | SEO | LCP | CLS | TBT | Field (real users) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        if "error" in r:
            continue
        s, l = r["scores"], r["lab"]
        field = ", ".join(f"{k} {v['p75']} {v['rating']}" for k, v in r["field"].items()) or "not enough traffic"
        lines.append(f"| {urllib.parse.urlsplit(r['url']).path} | {r['strategy']} | {s.get('performance')} | "
                     f"{s.get('accessibility')} | {s.get('best-practices')} | {s.get('seo')} | "
                     f"{l.get('LCP', {}).get('value')} | {l.get('CLS', {}).get('value')} | "
                     f"{l.get('TBT', {}).get('value')} | {field} |")
    ops = {}
    for r in results:
        for o in r.get("opportunities", []):
            ops.setdefault(o["title"], []).append(o["savings_ms"])
    if ops:
        lines += ["", "## Biggest opportunities (Lighthouse estimates)", ""]
        for t, v in sorted(ops.items(), key=lambda kv: -max(kv[1]))[:8]:
            lines.append(f"- {t}: up to {max(v)} ms, on {len(v)} test(s)")
    fails = sorted({f for r in results for f in r.get("failed_audits", [])})
    if fails:
        lines += ["", "## Failed audits (any page)", ""] + [f"- {f}" for f in fails]
    (REPORTS / f"{today}-pagespeed.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(1 if any("poor" in a for a in alerts) else 0)


if __name__ == "__main__":
    main()
