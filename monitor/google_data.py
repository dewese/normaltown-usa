#!/usr/bin/env python3
"""Pull Google Search Console + GA4 data with a read-only service account. Stdlib + openssl.

One-time setup (see monitor/README.md):
  - monitor/private/google-service-account.json   the key file from Google Cloud
  - that account's email added as a user in Search Console (Restricted is enough) and in GA4
    (Viewer), with the Search Console API, Google Analytics Data API and Google Analytics
    Admin API enabled in the Cloud project
  - optional monitor/private/config.json: {"gsc_site": "sc-domain:normaltownusa.com",
    "ga4_property": "123456789"}  (both are auto-detected if left out)

Writes monitor/private/reports/<date>-gsc.json, <date>-ga4.json and <date>-google.md.
Comparisons are last 28 days vs the 28 before, ending 3 days ago (Search Console lags).

Usage: python3 monitor/google_data.py [--gsc-only | --ga4-only] [--inspect]
  --inspect  also runs the URL Inspection API on every sitemap URL (index status per page)
Exit 2 = not set up yet.
"""
import base64
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SITE = "https://www.normaltownusa.com"
ROOT = Path(__file__).resolve().parent
PRIVATE = ROOT / "private"
REPORTS = PRIVATE / "reports"
SA_FILE = PRIVATE / "google-service-account.json"
SCOPES = "https://www.googleapis.com/auth/webmasters.readonly https://www.googleapis.com/auth/analytics.readonly"


def b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def access_token(sa):
    now = int(time.time())
    header = b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = b64(json.dumps({"iss": sa["client_email"], "scope": SCOPES, "aud": sa["token_uri"],
                             "iat": now, "exp": now + 3600}).encode())
    signing_input = f"{header}.{claims}".encode()
    fd, keypath = tempfile.mkstemp(dir=PRIVATE, suffix=".pem")
    try:
        os.chmod(keypath, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(sa["private_key"])
        sig = subprocess.run(["openssl", "dgst", "-sha256", "-sign", keypath], input=signing_input,
                             capture_output=True, check=True).stdout
    finally:
        os.unlink(keypath)
    body = urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                                   "assertion": f"{signing_input.decode()}.{b64(sig)}"}).encode()
    with urllib.request.urlopen(sa["token_uri"], data=body, timeout=30) as r:
        return json.load(r)["access_token"]


class Api:
    def __init__(self, token):
        self.token = token

    def call(self, url, body=None):
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Authorization": f"Bearer {self.token}",
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{e.code} on {url.split('?')[0]}: {e.read().decode()[:300]}")


def windows():
    end = dt.date.today() - dt.timedelta(days=3)
    cur = (end - dt.timedelta(days=27), end)
    prev = (cur[0] - dt.timedelta(days=28), cur[0] - dt.timedelta(days=1))
    return cur, prev


def pct(a, b):
    return "new" if not b else f"{(a - b) / b * 100:+.0f}%"


# ------------------------------------------------------------------ Search Console
def gsc(api, cfg, inspect):
    site = cfg.get("gsc_site")
    if not site:
        sites = [s["siteUrl"] for s in api.call("https://www.googleapis.com/webmasters/v3/sites").get("siteEntry", [])
                 if "normaltownusa.com" in s["siteUrl"]]
        if not sites:
            raise RuntimeError("service account has no Search Console property for normaltownusa.com")
        site = sorted(sites, key=lambda s: not s.startswith("sc-domain:"))[0]
    base = f"https://www.googleapis.com/webmasters/v3/sites/{urllib.parse.quote(site, safe='')}"
    (c0, c1), (p0, p1) = windows()

    def q(start, end, dims, limit=1000):
        return api.call(f"{base}/searchAnalytics/query",
                        {"startDate": str(start), "endDate": str(end), "dimensions": dims,
                         "rowLimit": limit, "dataState": "final"}).get("rows", [])

    out = {"site": site, "current": [str(c0), str(c1)], "previous": [str(p0), str(p1)]}
    tot = lambda rows: {"clicks": sum(r["clicks"] for r in rows), "impressions": sum(r["impressions"] for r in rows)}
    cur_d, prev_d = q(c0, c1, ["date"]), q(p0, p1, ["date"])
    out["totals"] = {"current": tot(cur_d), "previous": tot(prev_d)}
    for t, rows in (("current", cur_d), ("previous", prev_d)):
        imp = out["totals"][t]["impressions"]
        out["totals"][t]["avg_position"] = round(sum(r["position"] * r["impressions"] for r in rows) / imp, 1) if imp else None
    out["daily"] = [{"date": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"]} for r in cur_d]
    for dim in ("query", "page"):
        cur = {r["keys"][0]: r for r in q(c0, c1, [dim])}
        prv = {r["keys"][0]: r for r in q(p0, p1, [dim])}
        rows = []
        for k, r in cur.items():
            pr = prv.get(k, {})
            rows.append({dim: k, "clicks": r["clicks"], "impressions": r["impressions"],
                         "ctr": round(r["ctr"] * 100, 1), "position": round(r["position"], 1),
                         "prev_clicks": pr.get("clicks", 0), "prev_impressions": pr.get("impressions", 0),
                         "prev_position": round(pr["position"], 1) if pr else None})
        rows.sort(key=lambda r: (-r["clicks"], -r["impressions"]))
        out[f"by_{dim}"] = rows
        out[f"lost_{dim}"] = sorted(({dim: k, "prev_clicks": r["clicks"], "prev_impressions": r["impressions"]}
                                     for k, r in prv.items() if k not in cur and r["impressions"] >= 10),
                                    key=lambda r: -r["prev_impressions"])[:20]
    qp = q(c0, c1, ["query", "page"], 5000)
    out["query_page"] = [{"query": r["keys"][0], "page": r["keys"][1], "clicks": r["clicks"],
                          "impressions": r["impressions"], "position": round(r["position"], 1)} for r in qp]
    # striking distance: ranking 5-20 with real impressions -> title/content tune-ups move these
    out["striking_distance"] = sorted(
        (r for r in out["query_page"] if 5 <= r["position"] <= 20 and r["impressions"] >= 5),
        key=lambda r: -r["impressions"])[:40]
    # demand with no dedicated page: query gets impressions but the ranking page ranks > 20
    out["content_gaps"] = sorted((r for r in out["by_query"] if r["position"] > 20 and r["impressions"] >= 5),
                                 key=lambda r: -r["impressions"])[:30]
    try:
        out["sitemaps"] = [{"path": s["path"], "lastDownloaded": s.get("lastDownloaded"),
                            "errors": s.get("errors"), "warnings": s.get("warnings"),
                            "contents": s.get("contents")}
                           for s in api.call(f"{base}/sitemaps").get("sitemap", [])]
    except RuntimeError as e:
        out["sitemaps_error"] = str(e)
    if inspect:
        with urllib.request.urlopen(SITE + "/sitemap.xml", timeout=30) as r:
            urls = re.findall(r"<loc>([^<]+)</loc>", r.read().decode())

        def ins(u):
            try:
                res = api.call("https://searchconsole.googleapis.com/v1/urlInspection/index:inspect",
                               {"inspectionUrl": u, "siteUrl": site})["inspectionResult"]["indexStatusResult"]
                return {"url": u, "verdict": res.get("verdict"), "coverage": res.get("coverageState"),
                        "lastCrawl": res.get("lastCrawlTime"), "googleCanonical": res.get("googleCanonical")}
            except Exception as e:
                return {"url": u, "error": str(e)[:200]}
        with cf.ThreadPoolExecutor(4) as ex:
            out["inspection"] = list(ex.map(ins, urls))
    return out


# ------------------------------------------------------------------ GA4
def ga4(api, cfg):
    prop = cfg.get("ga4_property")
    if not prop:
        props = [p for a in api.call("https://analyticsadmin.googleapis.com/v1beta/accountSummaries").get("accountSummaries", [])
                 for p in a.get("propertySummaries", [])]
        if not props:
            raise RuntimeError("service account cannot see any GA4 property")
        prop = props[0]["property"].split("/")[-1]
    (c0, c1), (p0, p1) = windows()
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport"
    ranges = [{"startDate": str(c0), "endDate": str(c1), "name": "cur"},
              {"startDate": str(p0), "endDate": str(p1), "name": "prev"}]

    def rep(dims, mets, limit=250, order=None, flt=None):
        body = {"dateRanges": ranges, "dimensions": [{"name": d} for d in dims],
                "metrics": [{"name": m} for m in mets], "limit": limit}
        if order:
            body["orderBys"] = [{"metric": {"metricName": order}, "desc": True}]
        if flt:
            body["dimensionFilter"] = flt
        res = api.call(url, body)
        rows = {}
        for r in res.get("rows", []):
            dv = [d["value"] for d in r["dimensionValues"]]
            rng = dv[-1]  # dateRange is appended as the last dimension when 2 ranges are given
            k = tuple(dv[:-1])
            rows.setdefault(k, {"cur": {}, "prev": {}})
            rows[k][rng] = {m: float(v["value"]) for m, v in zip(mets, r["metricValues"])}
        return [{**{d: k[i] for i, d in enumerate(dims)}, **{f"{m}": rows[k]["cur"].get(m, 0) for m in mets},
                 **{f"prev_{m}": rows[k]["prev"].get(m, 0) for m in mets}} for k in rows]

    core = ["sessions", "totalUsers", "newUsers", "engagedSessions", "engagementRate",
            "averageSessionDuration", "screenPageViews", "keyEvents"]
    out = {"property": prop, "current": [str(c0), str(c1)], "previous": [str(p0), str(p1)]}
    tot = rep([], core)
    out["totals"] = tot[0] if tot else {}
    out["by_channel"] = sorted(rep(["sessionDefaultChannelGroup"], ["sessions", "engagedSessions", "keyEvents"]),
                               key=lambda r: -r["sessions"])
    out["by_source"] = sorted(rep(["sessionSource"], ["sessions", "keyEvents"], 50),
                              key=lambda r: -r["sessions"])[:25]
    out["landing_pages"] = sorted(rep(["landingPage"], ["sessions", "engagementRate", "keyEvents", "averageSessionDuration"], 200),
                                  key=lambda r: -r["sessions"])
    out["pages"] = sorted(rep(["pagePath"], ["screenPageViews", "userEngagementDuration", "keyEvents"], 200),
                          key=lambda r: -r["screenPageViews"])
    out["key_events"] = sorted((r for r in rep(["eventName"], ["eventCount", "keyEvents"], 100)
                                if r["keyEvents"] or r["prev_keyEvents"]), key=lambda r: -r["keyEvents"])
    out["key_events_by_page"] = sorted((r for r in rep(["eventName", "pagePath"], ["keyEvents"], 500)
                                        if r["keyEvents"]), key=lambda r: -r["keyEvents"])[:40]
    out["outbound_clicks"] = sorted(rep(["linkDomain"], ["eventCount"], 50,
                                        flt={"filter": {"fieldName": "eventName",
                                                        "stringFilter": {"value": "click"}}}),
                                    key=lambda r: -r["eventCount"])[:20]
    out["ai_referrals"] = [r for r in out["by_source"] if re.search(
        r"chatgpt|openai|perplexity|claude|gemini|copilot|bing", r["sessionSource"], re.I)]
    out["devices"] = rep(["deviceCategory"], ["sessions", "engagementRate"])
    return out


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    if not SA_FILE.exists():
        msg = f"Google data skipped: {SA_FILE.relative_to(ROOT.parent)} not found (see monitor/README.md)."
        (REPORTS / f"{today}-google.md").write_text(f"# Google data {today}\n\n{msg}\n")
        print(msg)
        sys.exit(2)
    cfg_file = PRIVATE / "config.json"
    cfg = json.loads(cfg_file.read_text()) if cfg_file.exists() else {}
    api = Api(access_token(json.loads(SA_FILE.read_text())))
    lines, failed = [f"# Google data {today}", ""], False

    if "--ga4-only" not in sys.argv:
        try:
            g = gsc(api, cfg, "--inspect" in sys.argv)
            (REPORTS / f"{today}-gsc.json").write_text(json.dumps(g, indent=1))
            c, p = g["totals"]["current"], g["totals"]["previous"]
            lines += [f"## Search Console ({g['site']}, {g['current'][0]} to {g['current'][1]} vs prior 28 days)", "",
                      f"- Clicks {c['clicks']} ({pct(c['clicks'], p['clicks'])}), impressions {c['impressions']} "
                      f"({pct(c['impressions'], p['impressions'])}), avg position {c['avg_position']} (was {p['avg_position']})", "",
                      "Top queries:", ""]
            lines += [f"- {r['query']}: {r['clicks']} clicks / {r['impressions']} impr, pos {r['position']}"
                      f" (was {r['prev_position']})" for r in g["by_query"][:15]]
            lines += ["", "Top pages:", ""]
            lines += [f"- {r['page'].replace(SITE, '')}: {r['clicks']} clicks / {r['impressions']} impr, pos {r['position']}"
                      for r in g["by_page"][:15]]
            lines += ["", "Striking distance (pos 5-20):", ""]
            lines += [f"- \"{r['query']}\" -> {r['page'].replace(SITE, '')}: pos {r['position']}, {r['impressions']} impr"
                      for r in g["striking_distance"][:15]]
            if g.get("inspection"):
                cov = {}
                for r in g["inspection"]:
                    cov.setdefault(r.get("coverage") or r.get("error", "error")[:60], []).append(r["url"])
                lines += ["", "Index status (URL Inspection):", ""]
                lines += [f"- {k}: {len(v)}" for k, v in sorted(cov.items(), key=lambda kv: -len(kv[1]))]
            lines.append("")
        except Exception as e:
            failed = True
            lines += [f"## Search Console FAILED", "", f"{e}", ""]
    if "--gsc-only" not in sys.argv:
        try:
            a = ga4(api, cfg)
            (REPORTS / f"{today}-ga4.json").write_text(json.dumps(a, indent=1))
            t = a["totals"]
            lines += [f"## GA4 (property {a['property']}, same window)", "",
                      f"- Sessions {t.get('sessions', 0):.0f} ({pct(t.get('sessions', 0), t.get('prev_sessions', 0))}), "
                      f"users {t.get('totalUsers', 0):.0f}, engagement rate {t.get('engagementRate', 0) * 100:.0f}%, "
                      f"key events {t.get('keyEvents', 0):.0f} ({pct(t.get('keyEvents', 0), t.get('prev_keyEvents', 0))})", "",
                      "Channels: " + ", ".join(f"{r['sessionDefaultChannelGroup']} {r['sessions']:.0f}" for r in a["by_channel"]), "",
                      "Key events: " + (", ".join(f"{r['eventName']} {r['keyEvents']:.0f} (was {r['prev_keyEvents']:.0f})"
                                                   for r in a["key_events"]) or "none"), "",
                      "AI-assistant referrals: " + (", ".join(f"{r['sessionSource']} {r['sessions']:.0f}"
                                                              for r in a["ai_referrals"]) or "none"), "",
                      "Top landing pages:", ""]
            lines += [f"- {r['landingPage']}: {r['sessions']:.0f} sessions, {r['engagementRate'] * 100:.0f}% engaged, "
                      f"{r['keyEvents']:.0f} key events" for r in a["landing_pages"][:15]]
            lines.append("")
        except Exception as e:
            failed = True
            lines += ["## GA4 FAILED", "", f"{e}", ""]
    (REPORTS / f"{today}-google.md").write_text("\n".join(lines))
    print("\n".join(lines))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
