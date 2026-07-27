# NOLA council agenda data sources (manual workflow)

Use this when `scripts/search_agendas.py` breaks or you need to dig deeper.
All endpoints verified working July 2026.

## 1. Legistar web API (regular council meetings + legislation database)

Base: `https://webapi.legistar.com/v1/cityofno` — no auth, OData filters,
JSON via `Accept: application/json`.

- **Events** (regular meetings only):
  `GET /Events?$filter=EventDate ge datetime'2026-07-01'&$orderby=EventDate`
  Useful fields: `EventId`, `EventDate`, `EventTime`, `EventAgendaStatusName`
  (`Final` when published), `EventAgendaFile` (PDF URL on
  `cityofno.legistar1.com`), `EventInSiteURL`.
- **Agenda items for an event**:
  `GET /Events/{EventId}/EventItems` — search `EventItemTitle` and the whole
  JSON blob; titles alone can miss content.
- **Legislation search** (pending matters, whether or not scheduled):
  `GET /Matters?$filter=substringof('drone', MatterTitle) and MatterIntroDate ge datetime'2025-01-01'`
  Note: `substringof` is case-insensitive but matches raw substrings — short
  keywords false-positive (e.g. "uas" matches "q**uas**i-public"), so re-check
  results with a word-boundary regex client-side. Useful fields: `MatterFile` (TMP-####),
  `MatterTitle` (contains CAL. NO. and full brief), `MatterStatusName`,
  `MatterAgendaDate`, `MatterPassedDate`, `MatterIntroDate`.

## 2. council.nola.gov (full calendar including committees)

- **Calendar RSS**: `https://council.nola.gov/meetings/?rss=events` — every
  scheduled meeting for the year: title, `pubDate` (meeting datetime, GMT),
  and meeting-page link (strip the `?feed=events` suffix).
- **Meeting pages** (e.g.
  `/meetings/2026/committees/criminal-justice/20260727-criminal-justice/`):
  - Granicus agenda link, **unquoted href** — match
    `href=["']?(https://cityofno\.granicus\.com/GeneratedAgendaViewer\.php[^"' >]+)`.
    Two formats exist: `?event_id=<guid>` and `?view_id=42&event_id=<int>`.
    The viewer page is the agenda itself as HTML — strip tags and search.
  - Attachment links: `/getattachment/<guid>/file` (PDF or Word). Check the
    magic bytes (`%PDF`) before parsing.
  - Unpublished agendas say "The agenda is forthcoming."

## 3. PDF text extraction

`pypdf` works on these agendas. Regular-meeting agendas run ~28 pages /
~40k chars. On this machine, install into a scratchpad venv
(`python3 -m venv venv && venv/bin/pip install pypdf`) — system pip is
externally managed.

## Known relevant matters (as of July 2026, for continuity)

- CAL. NO. 35,450 / 35,451 — NOPD 8th District Drone Program funding (French
  Quarter EDD), King by request, introduced 5/21/26, pending.
- CAL. NO. 35,133 — surveillance-technology public dashboard (NOPD +
  Real-Time Crime Center), Moreno/Morrell/Harris/King, introduced 6/12/25,
  held repeatedly, pending.
- CAL. NO. 35,137 — Ch. 147 surveillance-technology code amendments —
  withdrawn late 2025.
- NOPD Drone Annual Report — received into record 6/24/26.
