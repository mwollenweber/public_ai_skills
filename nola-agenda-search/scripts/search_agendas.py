#!/usr/bin/env python3
"""Sweep New Orleans City Council agendas (current + future) for keywords.

Covers BOTH publishing systems (see references/data-sources.md):
  1. council.nola.gov RSS calendar -> meeting pages -> Granicus agenda HTML
     and /getattachment PDF/Word attachments. This is the ONLY source for
     committee agendas (Criminal Justice, Governmental Affairs, Joint
     Utility/Telecom, Quality of Life, Budget, etc.).
  2. Legistar API (cityofno) -> regular-meeting agenda PDFs + item JSON.
     Hits here are merged into the matching calendar meeting by date so
     regular meetings aren't double-reported.
  3. Legistar Matters -> legislation matching keywords, scheduled or not
     (pending only by default; --include-resolved for passed/withdrawn).

Output is concise, matches-only markdown. Use --json FILE to also write
structured match data (for calendaring/alerting), --verbose for the full
per-meeting listing.
"""
import argparse
import datetime as dt
import email.utils
import html
import io
import json
import re
import sys
import urllib.parse
import urllib.request

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

UA = {"User-Agent": "Mozilla/5.0 (CouncilWatch agenda sweep)"}
LEGISTAR = "https://webapi.legistar.com/v1/cityofno"
RSS_URL = "https://council.nola.gov/meetings/?rss=events"

DEFAULT_KEYWORDS = [
    "drone", "uav", "suas", "unmanned",
    "facial recognition", "face recognition", "biometric",
    "project nola", "surveillance",
    "license plate", "alpr",
    "real-time crime", "real time crime",
    "oipm", "police monitor",  # "police monitor" also catches "independent police monitor"
    "flock",   # Flock Safety ALPR vendor (also matches "Flock Group")
    "camera",  # also matches "cameras"; noisier but the user wants it
]


def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def fetch_json(url):
    return json.loads(fetch(url).decode("utf-8"))


def strip_html(raw):
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def pdf_text(data):
    if PdfReader is None:
        return None
    return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)


def keyword_pattern(kw):
    # Short tokens like "uas"/"alpr" false-positive inside words ("quasi"),
    # so anchor them at word boundaries.
    esc = re.escape(kw)
    return re.compile(r"\b%s\b" % esc if len(kw) <= 4 else esc, re.I)


def find_hits(text, patterns, context=120, per_kw=2):
    """Return {keyword: [snippet, ...]} with overlapping snippets deduped."""
    hits = {}
    for kw, pat in patterns:
        seen = set()
        for m in pat.finditer(text):
            lo, hi = max(0, m.start() - context), m.end() + context
            snippet = re.sub(r"\s+", " ", text[lo:hi]).strip()
            key = snippet[:60]
            if key in seen:
                continue
            seen.add(key)
            hits.setdefault(kw, []).append(snippet)
            if len(hits[kw]) >= per_kw:
                break
    return hits


def merge_hits(into, new):
    for kw, snips in new.items():
        cur = into.setdefault(kw, [])
        for s in snips:
            if s[:60] not in {c[:60] for c in cur}:
                cur.append(s)


def calendar_meetings(lookback_days, horizon_days):
    """Parse the RSS calendar into meeting dicts within the window."""
    xml = fetch(RSS_URL).decode("utf-8", "ignore")
    today = dt.date.today()
    lo, hi = today - dt.timedelta(days=lookback_days), today + dt.timedelta(days=horizon_days)
    rows = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        title = re.search(r"<title><!\[CDATA\[(.*?)\]\]>", item).group(1)
        pub = re.search(r"<pubDate>(.*?)</pubDate>", item).group(1)
        link = re.search(r"<link><!\[CDATA\[(.*?)\]\]>", item).group(1)
        when = email.utils.parsedate_to_datetime(pub)  # meeting start, GMT
        if lo <= when.date() <= hi:
            rows.append({"date": when.date(), "start_utc": when.isoformat(),
                         "title": title.strip(), "url": link.replace("?feed=events", ""),
                         "hits": {}, "sources": []})
    return sorted(rows, key=lambda r: r["date"])


def meeting_agenda_texts(page_url):
    """Return (texts, unpublished, errors) for one meeting page."""
    page = fetch(page_url).decode("utf-8", "ignore")
    texts, errors = [], []
    # hrefs are often UNQUOTED on this site; match both forms.
    for url in set(re.findall(
            r"href=[\"']?(https://cityofno\.granicus\.com/GeneratedAgendaViewer\.php[^\"' >]+)", page)):
        try:
            texts.append(("granicus agenda", strip_html(fetch(url).decode("utf-8", "ignore"))))
        except Exception as e:
            errors.append(f"granicus fetch failed: {e}")
    for path in set(re.findall(r"href=[\"']?(/getattachment/[a-f0-9-]+/file)", page)):
        try:
            data = fetch("https://council.nola.gov" + path)
        except Exception as e:
            errors.append(f"attachment fetch failed: {e}")
            continue
        if data[:4] == b"%PDF":
            t = pdf_text(data)
            if t is None:
                errors.append("PDF attachment skipped: pypdf not installed")
            else:
                texts.append(("attachment pdf", t))
        else:
            texts.append(("attachment", data.decode("utf-8", "ignore")))
    unpublished = not texts
    return texts, unpublished, errors


def legistar_events(lookback_days, horizon_days):
    today = dt.date.today()
    lo = (today - dt.timedelta(days=lookback_days)).isoformat()
    hi = (today + dt.timedelta(days=horizon_days)).isoformat()
    q = urllib.parse.quote(f"EventDate ge datetime'{lo}' and EventDate le datetime'{hi}'")
    return fetch_json(f"{LEGISTAR}/Events?$filter={q}&$orderby=EventDate")


def search_matters(keywords, since, include_resolved):
    found = {}
    for kw in keywords:
        safe = kw.replace("'", "''")
        q = urllib.parse.quote(
            f"substringof('{safe}', MatterTitle) and MatterIntroDate ge datetime'{since}'")
        try:
            matters = fetch_json(f"{LEGISTAR}/Matters?$filter={q}")
        except Exception as e:
            print(f"warning: matters query failed for {kw!r}: {e}", file=sys.stderr)
            continue
        pat = keyword_pattern(kw)
        for m in matters:
            title = m.get("MatterTitle") or ""
            if not pat.search(title):  # drop loose server-side matches ("quasi" for uas)
                continue
            resolved = m.get("MatterPassedDate") or (m.get("MatterStatusName") == "Withdrawn")
            if resolved and not include_resolved:
                continue
            found.setdefault(m["MatterId"], (m, set()))[1].add(kw)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--keywords", nargs="+", default=DEFAULT_KEYWORDS)
    ap.add_argument("--extra-keywords", nargs="+", default=[])
    ap.add_argument("--lookback-days", type=int, default=1)
    ap.add_argument("--horizon-days", type=int, default=120)
    ap.add_argument("--matters-since", default=None,
                    help="YYYY-MM-DD floor for legislation search (default: 18 months ago)")
    ap.add_argument("--include-resolved", action="store_true",
                    help="also list passed/withdrawn legislation")
    ap.add_argument("--json", metavar="FILE", help="write structured matches to FILE")
    ap.add_argument("--verbose", action="store_true",
                    help="list every meeting checked, not just matches")
    args = ap.parse_args()

    keywords = [k.lower() for k in args.keywords + args.extra_keywords]
    patterns = [(k, keyword_pattern(k)) for k in keywords]
    since = args.matters_since or (dt.date.today() - dt.timedelta(days=548)).isoformat()

    if PdfReader is None:
        print("warning: pypdf not installed - PDF agendas skipped (pip install pypdf)",
              file=sys.stderr)

    # --- Sweep all calendar meetings (committees + regular + hearings) ---
    meetings = calendar_meetings(args.lookback_days, args.horizon_days)
    searched = unpublished = 0
    for mtg in meetings:
        try:
            texts, unpub, errors = meeting_agenda_texts(mtg["url"])
        except Exception as e:
            mtg["error"] = str(e)
            continue
        mtg["errors"] = errors
        if unpub:
            unpublished += 1
            mtg["unpublished"] = True
            continue
        searched += 1
        for label, text in texts:
            merge_hits(mtg["hits"], find_hits(text, patterns))
        if mtg["hits"]:
            mtg["sources"].append("agenda")

    # --- Legistar regular-meeting agendas; merge hits by date ---
    by_date = {m["date"]: m for m in meetings if "Regular" in m["title"] or "Budget" in m["title"]}
    for ev in legistar_events(args.lookback_days, args.horizon_days):
        date = dt.date.fromisoformat(ev["EventDate"][:10])
        blobs = []
        if ev.get("EventAgendaFile"):
            try:
                t = pdf_text(fetch(ev["EventAgendaFile"]))
                if t:
                    blobs.append(t)
            except Exception:
                pass
        try:
            blobs.append(json.dumps(fetch_json(f"{LEGISTAR}/Events/{ev['EventId']}/EventItems")))
        except Exception:
            pass
        hits = {}
        for text in blobs:
            merge_hits(hits, find_hits(text, patterns))
        if not hits:
            continue
        mtg = by_date.get(date)
        if mtg is None:
            mtg = {"date": date, "start_utc": None, "title": f"City Council {ev.get('EventTime') or ''}".strip(),
                   "url": ev.get("EventInSiteURL", ""), "hits": {}, "sources": []}
            meetings.append(mtg)
        merge_hits(mtg["hits"], hits)
        if "legistar" not in mtg["sources"]:
            mtg["sources"].append("legistar")

    matched = sorted((m for m in meetings if m["hits"]), key=lambda m: m["date"])

    # Legistar stores one snapshot per agenda appearance, so a held ordinance
    # shows up once per meeting it was on. Collapse by CAL. NO., keeping the
    # most recent snapshot.
    matters = []
    seen_cal = {}
    for m, kws in sorted(search_matters(keywords, since, args.include_resolved).values(),
                         key=lambda x: x[0].get("MatterAgendaDate") or "", reverse=True):
        cal = re.search(r"CAL\.\s*NO\.\s*([\d,]+)", m.get("MatterTitle") or "")
        key = cal.group(1) if cal else m["MatterId"]
        if key in seen_cal:
            seen_cal[key].update(kws)
        else:
            seen_cal[key] = set(kws)
            matters.append((m, seen_cal[key]))

    # --- Report (matches only unless --verbose) ---
    today = dt.date.today().isoformat()
    print(f"# NOLA agenda sweep {today} - "
          f"{len(matched)} meeting match(es), {len(matters)} legislation match(es)")
    print(f"({searched} published agendas searched incl. committees; "
          f"{unpublished} upcoming meetings have no agenda yet)\n")

    if matched:
        print("## Meetings with matches")
        for m in matched:
            print(f"- **{m['date']} {m['title']}** <{m['url']}>")
            for kw, snips in m["hits"].items():
                print(f"    - [{kw}] ...{snips[0][:220]}...")
    if matters:
        print("\n## Matching legislation (pending)" if not args.include_resolved
              else "\n## Matching legislation")
        for m, kws in matters:
            title = re.sub(r"\s+", " ", (m.get("MatterTitle") or ""))
            print(f"- {m.get('MatterFile')} | {m.get('MatterStatusName')} | "
                  f"last agenda {(m.get('MatterAgendaDate') or 'n/a')[:10]} | [{', '.join(sorted(kws))}]")
            print(f"    {title[:200]}")
    if not matched and not matters:
        print("No matches on any published agenda or in pending legislation.")

    if args.verbose:
        print("\n## All meetings checked")
        for m in sorted(meetings, key=lambda m: m["date"]):
            status = ("ERROR: " + m["error"]) if m.get("error") else \
                     "agenda not published yet" if m.get("unpublished") else \
                     f"{len(m['hits'])} keyword(s) matched" if m["hits"] else "no hits"
            print(f"- {m['date']} {m['title']} - {status}")

    if args.json:
        out = {
            "generated": today, "keywords": keywords,
            "agendas_searched": searched, "agendas_unpublished": unpublished,
            "meeting_matches": [
                {"date": m["date"].isoformat(), "start_utc": m["start_utc"],
                 "title": m["title"], "url": m["url"], "hits": m["hits"]}
                for m in matched],
            "legislation_matches": [
                {"file": m.get("MatterFile"), "status": m.get("MatterStatusName"),
                 "last_agenda": (m.get("MatterAgendaDate") or "")[:10] or None,
                 "keywords": sorted(kws),
                 "title": re.sub(r"\s+", " ", (m.get("MatterTitle") or ""))}
                for m, kws in matters],
        }
        with open(args.json, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\n(structured matches written to {args.json})")


if __name__ == "__main__":
    main()
