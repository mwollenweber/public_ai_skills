---
name: nola-agenda-search
description: >
  Sweep New Orleans City Council AND committee meeting agendas (current and
  future) for surveillance-related topics — drones, UAV/sUAS, facial
  recognition, Project NOLA, ALPR/license plate readers, Flock Safety,
  cameras, biometrics, Real-Time Crime Center, the OIPM/Independent Police
  Monitor, or any custom keyword list — and, when something matches, put the meeting on the user's
  Google Calendar and alert them with a summary. Use this whenever the user
  asks what's on upcoming NOLA council or committee agendas, whether a topic
  (especially surveillance or policing tech) is before the council, to "check
  the agendas", or to re-run the CouncilWatch sweep. Also use it for
  questions about pending NOLA legislation on these topics even when no
  meeting is named.
compatibility: Requires network access, Python 3 with `pypdf`, a Google Calendar connector for event creation, and PushNotification for alerts.
---

# NOLA Council Agenda Search

Sweep every published current/future New Orleans City Council agenda —
regular meetings AND committees (Criminal Justice, Governmental Affairs,
Joint Utility/Telecom, Quality of Life, Budget, ABCB hearings) — for a
keyword list, plus the Legistar legislation database for pending matters.
When something matches: calendar it, alert the user, summarize.

## Step 1 — Run the sweep

```bash
python3 scripts/search_agendas.py --json matches.json   # default surveillance+OIPM keywords
python3 scripts/search_agendas.py --keywords "short term rental" --json matches.json
```

The script already covers committees (via the council.nola.gov RSS calendar
and Granicus agenda pages) and regular meetings (via Legistar), merged and
deduped. Output is concise and matches-only; `--verbose` lists every meeting
checked if the user asks for the full audit trail.

`pypdf` is required for the PDF agendas regular meetings use — install into a
scratchpad venv if missing. If the script errors, the site layout may have
changed: consult `references/data-sources.md` for the manual workflow, fix
the script, continue.

## Step 2 — Calendar matched meetings (upcoming only)

`meeting_matches` includes both meetings matched by full agenda text AND
pending legislation whose `MatterAgendaDate` names a today-or-later meeting
(merged in under a `legislation:<file>` hit key even when that meeting's own
agenda isn't published yet) — the script does this merge itself, so treat
every entry in `meeting_matches` the same way.

For each entry in `meeting_matches` whose date is today or later, ALWAYS
check the user's Google Calendar first (search/list events for that day) —
never skip this check:

1. Look for an existing event that day matching the meeting title.
2. If absent, create it: title `NOLA Council: <meeting title>`, start from
   `start_utc` (convert to America/Chicago; council meetings are typically
   1.5–3 h, default 2 h), description containing the matched keywords, a hit
   snippet or note for each agenda item/legislation match (e.g. calendar
   number and brief), and the meeting-page URL plus any legislation link.
3. If an event already exists but is missing a hit that's now present
   (e.g. a new legislation match landed on an already-calendared date),
   update its description rather than skipping it.

Only past meetings are excluded from calendaring. If no calendar tool is
available, say so and give the user the meeting details to add manually.

## Step 3 — Alert + summary

When there are matches, send a push notification (PushNotification tool) —
one line, e.g. "NOLA agenda hit: drone item on 8/6 council agenda". Then give
a summary structured as:

1. **Bottom line** — what matched, one sentence.
2. **Matched meetings** — date, meeting, keyword(s), one-line description of
   the agenda item, link. Note "added to your calendar" per event.
3. **Matching pending legislation** — calendar number, status, last agenda
   date, one-line gist. Flag anything pending as likely to reappear when the
   next regular-meeting agenda posts.

When nothing matches, no notification and no calendar events — reply with a
single line like "No matches; N published agendas searched (M upcoming
meetings have no agenda posted yet)" and the date of the next unpublished
regular-meeting agenda worth re-checking.

## Why both sources matter

Legistar only hosts regular council meetings; committee agendas exist solely
as Granicus pages linked (with unquoted `href`s) from council.nola.gov
meeting pages. Agendas typically publish only days before a meeting, so "no
match" on a far-future meeting means "not published yet", not "clear" — the
unpublished count in the script output captures this. Pending legislation
(status Regular Agenda/Held, no passed date) can resurface on any future
agenda even after months dormant.
