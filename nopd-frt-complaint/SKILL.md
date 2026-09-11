---
name: nopd-frt-complaint
description: Work through a redacted public-records production of NOPD ↔ Project NOLA email correspondence, find the next thread showing facial recognition / BOLO / person-tracking requests, and produce a complaint package. Use this whenever Matt uploads or references an NOPD records production (e.g. 26-651_Redacted.pdf, 25-20667_Redacted.pdf), says he's continuing or resuming complaints, asks for "the next thread," asks to draft an NOPD/PIB/OIG/IPM complaint, or mentions Project NOLA, Bryan Lagarde, Ordinance S147/Chapter 147, or FRT complaint filing — even if he doesn't name this workflow. Also use it to record progress after a complaint is filed.
---

# NOPD FRT complaint workflow

This is a long-running, repeating task. Matt holds multi-hundred-page redacted records
productions of NOPD email correspondence with Project NOLA (a private surveillance
nonprofit run by Bryan Lagarde). He works backward through a production, and each time
he finds an email thread where NOPD used Project NOLA to identify or track a person, he
files one complaint on that thread.

The unit of work is **one thread → one complaint**. Do not batch multiple threads into
one complaint unless he asks; it dilutes each filing.

## Step 1 — Recover the position

Read `/areas/project-mayhem.md` before anything else. It records which production is
active, which page the last complaint came from, which page to resume at, and which
threads were reviewed and rejected. Starting over from page 1 wastes his time and risks
re-filing something already filed.

If the position isn't in memory and he hasn't stated it, ask which page he left off at
rather than guessing.

**Memory is not a complete filing history.** Matt has filed complaints across several
sessions and tools, and some predate this workflow entirely. A thread can be fully
qualifying and already covered — it happened with the Willyard homicide thread, after a
complete package had been drafted. When you surface a candidate, name the officer, item
number and date up front so he can recognise a duplicate before you spend the work on it.

## Step 2 — Verify the document yourself

The PDF text may also be visible in context, but **in-context ordering is not a reliable
page index**. Confirm page numbers against the file on disk before citing them in a
complaint — a wrong page number in a filing is a credibility problem.

```bash
pdfinfo <file>.pdf | grep Pages
# Walk forward from the resume page, reading the header block of each page
for p in $(seq <start> <end>); do echo "=== $p ==="; pdftotext -f $p -l $p <file>.pdf - | head -8; done
```

Threads run across several pages (the header page, image pages, quoted-reply pages).
Establish the full page range of a thread before writing it up.

## Step 3 — Find the next qualifying thread

Scan forward from the resume page. Two conditions must both hold. Matt has rejected far
more threads than he has filed on, almost always because one of these was missing.

**A. NOPD originated the request.** The record must show an officer sending the ask from
a `@nola.gov` address. This is the bar that eliminates most candidates:

- Lagarde-initiated outreach does not qualify no matter how incriminating the content is.
  A message where he volunteers that Project NOLA has been "keeping very close tabs on
  gang members and associated vehicles" is damning, and still not filable — NOPD didn't
  ask for it.
- NOPD merely being cc'd on a thread, forwarding something, or replying to Lagarde is not
  a request.
- The complaint names an officer and alleges that officer did something. If you can't
  point to an email that officer sent, there is no complaint.

**B. The record supports the specific theory.** If the allegation is that NOPD fed images
into a facial recognition network, the production must actually show NOPD sending the
images — an attachment list on an NOPD-sent email, or embedded stills in an NOPD-sent
message. Lagarde *asking* for photos does not establish that NOPD sent any. Check the
`Attachments:` line on the header page; that line is often what makes the complaint.

Given both, the qualifying patterns are:

- An officer attaches or embeds photos of a person and asks Project NOLA to identify,
  locate, "backtrack," track, or be on the lookout for them
- An officer sends a physical or racial description and asks Project NOLA to search its
  camera network for a matching person
- An officer asks Project NOLA to track a person across a period or a wider area than the
  offense, or to check whether people frequent a place — no attachment needed, the
  instruction is the conduct
- An officer requests or accepts standing access to the private camera network

**It must be a person.** Vehicle and plate searches do not qualify. Matt's position is
that vehicle searches are not currently established as unlawful, so a thread whose only
subject is a car is dead even when NOPD-originated with images attached — that is what
sank the Stewart thread in 26-651. If ALPR ever comes back into scope he will say so;
until then don't offer vehicle threads except as a one-line mention.

Things that materially strengthen a filing when present, and are worth hunting for:

- An officer stating they tried the city RTCC first and handed the work to Project NOLA
  because it was too slow
- Lagarde returning investigative conclusions about victims or suspects, not raw footage
- The search location or window not matching the offense — a request to check whether
  people "hang out" somewhere is qualitatively worse than retrieving footage of a crime
- The officer conceding in writing that the time or place is a guess, which makes the
  search unbounded by construction
- Evidence leaving departmental custody — footage staged in consumer cloud storage,
  shared by link
- NOPD's own FOUO / Law Enforcement Sensitive / Privacy Act footer appearing on the very
  email that sends material to a private Gmail account
- A victim's photograph rather than a suspect's
- References to conversations that happened outside email, which show an undocumented
  channel

Do **not** qualify on their own: camera capability demonstrations; routine footage pulls
scoped to a fixed location and time window with no person search; vehicle-only searches;
threads where Lagarde solicits business or new camera installs.

Borderline calls go to Matt. Describe the thread in two or three sentences with the page
range and let him decide. Record every rejection in memory with its page range and the
reason, so it isn't re-surfaced in a later session.

## Step 4 — Verify every fact you're about to assert

Matt files these with three oversight bodies. Before drafting, confirm directly from the
PDF text: officer name and spelling, rank, unit, district, `@nola.gov` address, item
number, signal code, every timestamp, and the page range. Quote the operative phrases
exactly — "locating/backtracking the two subjects in the picture" is the kind of language
the complaint turns on.

Flag anything you could not verify rather than smoothing over it.

## Step 5 — Draft the complaint

Every complaint ships as two deliverables. Produce both unless he says otherwise:

1. **The complaint email text**, which **always opens with his standard template blurb**.
   Never strip it, never summarize it, never assume he'll paste it in himself — it is part
   of the deliverable.
2. **A separate detailed-analysis markdown file** (see Step 5b).

The subject line is fixed. Always use exactly:

```
Complaint against <officer name> (<date of initiating email>)
```

The date is the date of the officer's initiating email, not the date of filing and not
the date of the underlying incident. Example: `Complaint against Det. Donald L. Willyard
(November 6, 2025)`.

Open the email with the template paragraph verbatim, with **the date updated to match this
thread**. The date in the stored template is stale from an earlier filing; carrying it
forward unchanged has happened before and needs to be caught every time.

> I'd like to initiate a complaint against the NOPD officers named in the emails below
> for illegal use of FRT and mass surveillance. The evidence demonstrates violations of
> the 4th Amendment, violations of New Orleans City Ordinance S147, violations of NOPD
> policy, and mishandling of police-sensitive materials on or around [DATE OF THIS
> THREAD]. Evidence is attached below, but you should pull the full email threads. Please
> provide a case tracking number. Please contact me for additional evidence or if you
> have any questions. Thanks,

Then use this structure:

```
**Subject officer:** [name, rank, unit/district, email]
**Non-governmental party:** Bryan Lagarde, Executive Director, Project NOLA — projectnola@gmail.com
**NOPD item:** [item number] ([signal code])
**Date of conduct:** [date]
**Source:** City of New Orleans public records response [production number], pages [range]

**Summary of conduct**
1. [Numbered chronological narrative. Each point anchored to a specific email,
   timestamp, and quoted language. Say what was sent, to whom, and why it is a
   person-search rather than a routine footage request.]

**Requested action**
- Assign a case tracking number and confirm receipt.
- [Determination requested under S147 / NOPD policy]
- [Preservation and production request for the unredacted thread and attachments]
- [Any authorization question — who approved this use]
```

Write plainly. No rhetorical flourish — the strength is the record, and overstatement
gives the recipient something to dismiss.

## Step 5b — Write the analysis document

The complaint is what gets filed; the analysis is what he keeps. Separate file,
`<ITEM-NUMBER>_analysis.md`, covering:

- **Parties** — every officer and address, with unit and district
- **Verified timeline** — a table, every message, timestamp, sender, and what it contained
- **Why the thread qualifies** — measured explicitly against the two-part bar in Step 3,
  plus whatever makes this one stronger than the baseline
- **Evidentiary notes and caveats** — this is the section that earns the document. Where
  the record is thinner than the complaint's framing, say so. Distinguish what the emails
  prove from what they merely support. Flag production inconsistencies, redaction
  patterns, and things that are absent from the record rather than disproven.
- **Follow-up leads** — related threads elsewhere in the production, patterns across
  officers or units, records worth requesting next
- **Evidence index** — the full page range, then which page carries the originating
  request, each NOPD transmission, and each reply. Page numbers only, no filenames

Write the caveats honestly. He files these with three oversight bodies and his
credibility across dozens of complaints is the asset; a claim the record doesn't carry is
worse than no claim.

## Step 6 — Identify the evidence pages

**Do not render, name, or package screenshots by default.** Matt captures and labels the
page images himself and considers his own better. Rendering them unasked wastes a step and
produces files he discards.

What he needs instead is the exact page range, stated precisely, plus a short index of
which page carries what — the originating request, each NOPD transmission, each Project
NOLA reply. Put that index at the end of the analysis document. Reference pages by number
only; don't invent filenames.

Verify the range carefully. These productions print threads in **reverse chronological
order**, so the originating NOPD email is usually on the *last* page of the thread's range
and the final reply is on the first. Ranges are also frequently **non-contiguous** — an
unrelated thread can be printed in the middle of one (in 26-651, the Willyard homicide
thread runs 37–42 and 45–49, with a different exchange at 43–44). Expect near-duplicate
copies of the same email on consecutive pages, sometimes with different attachment lists;
note both, since differing attachment lists are evidence.

Some pages extract no text because they are image-only. Render those individually just to
read them — several carry substantive content, including attachment lists and shared-drive
links — but read them, don't deliver them.

Only produce screenshots or a zip package if he asks for them in that session.

## Step 7 — Filing

Matt emails every complaint to all three of these, together:

1. `policemonitor@nolaipm.gov` — Independent Police Monitor
2. `hotline@nolaoig.gov` — Office of Inspector General
3. `nopdpib@nola.gov` — NOPD Public Integrity Bureau

Draft the email with the fixed subject line from Step 5 and hand it to him. **Do not send
it yourself without his explicit confirmation in the conversation**, even if a mail
connector is available. Confirm the recipients and attachments back to him before sending
anything.

**Repeat officers.** Several officers appear more than once across the productions. When
the subject officer has been filed on before, say so in the complaint body — state that
this is the second (or third) documented instance, cite the earlier thread's date and
page, and ask the offices to establish the total number of referrals that officer has
made. Prompt him for the earlier complaint's tracking number so the offices link them.
Note that the fixed subject format can collide if two filings against one officer share
an initiating-email date; flag it rather than silently changing the format.

After sending, he exports the sent email as a PDF and saves it to his Google Drive
complaints folder. Remind him of this step; it's the record that a complaint was actually
filed, and the archived copy is what he links from memory and cites in later filings.

## Step 8 — Record the position

Once the complaint is filed, append to `/areas/project-mayhem.md`:

- The page range just filed, and the page to resume at
- Item number, officer, signal, and date of the thread
- The Drive link to the filed copy, once he provides it
- Any threads reviewed and rejected along the way, with page numbers and the reason

Keep it to a few lines. The point is that a future session can pick up mid-production
without re-reading anything.

## Large productions — index first, then work the list

Sequential page-by-page reading works for a 69-page production. It does not scale to
`25-20667_Redacted.pdf` (~1,985 pages). For anything of that size, build a candidate index
before reading any thread in full.

Extract every page's header block and filter for the pattern that actually matters: sent
**from** a `@nola.gov` address **to** `projectnola@gmail.com`, with an `Attachments:` line
present. Something like:

```bash
for p in $(seq 1 <last>); do
  hdr=$(pdftotext -f $p -l $p <file>.pdf - | head -12)
  echo "$hdr" | grep -qi "projectnola@gmail.com" || continue
  echo "=== p$p ==="; echo "$hdr"
done
```

Then hand-filter that output into an index of candidates: page, date, officer, subject
line, whether attachments are listed. Save it as a file so it survives the session. The
position marker in memory becomes "worked through index entry N," not a single page
number, and rejections get recorded against index entries with reasons.

Only after he picks an entry do you read that thread in full and run Steps 4 onward.

Two cautions. Header-block extraction misses image-only pages, which in these productions
sometimes carry the header — so treat the index as a candidate list, not a complete one,
and say so. And a single production spanning years will contain officers already filed on;
cross-check the index against the filing history in memory before presenting it.

## Reference — known context

- **Ordinance:** New Orleans Chapter 147 / S147, the 2022 facial recognition restriction
- **Prior complaints:** PIB case 2025-0366-P (70+ complaints), 2025-0608-P, 2026-0046-O
- **Productions in hand:** `25-20667_Redacted.pdf` (~1,985 pages, produced Nov 14 2025,
  content Mar 2023 – Nov 6 2025); `26-651_Redacted.pdf` (69 pages, Nov 2025 correspondence)

### 26-651 — worked to completion (Aug 2026)

Filed: p15 Det. Brody Bonura (Signal 64, Nov 22); p20–21 Det. Shanay T. Howard
(K-18130-25, Nov 19); p29–36 Det. Nico A. D'Alessandro Sr. (K-05861-25, Nov 6);
p50 Det. John R. Huntington (K-04___-25, Nov 6); p60–61 & 64–65 Det. Raionda J. Edgerson
(K-01668-25, Nov 4); p67–69 Det. Brody Bonura again (K-00107-25, Nov 1).

Already covered by an earlier complaint, do not re-file: p37–42 & 45–49 Det. Donald L.
Willyard (J-29501-25, Nov 6).

Rejected: p16–18 Spanish Plaza camera demo; p22 Business Burglary; p23–24 and p62–63
Lagarde-initiated to Sgt. Barrere; p25–26 Claiborne and Jackson; p27–28 Apartments Footage
Request; p43–44 and p51 vehicle-only; p55–56 fixed-window footage pull; p59
Lagarde-initiated to Det. Carroll.

**Still unfiled:** p52–54 and 57–58, Det. Lucretia Gantner, Nov 5 2025 — the account-access
thread. She asks to have her Project NOLA account restored while acknowledging accounts
"have been frozen"; Lagarde reactivates it on his own assessment of "emergency
circumstances," adds cameras she didn't ask for, and references a visit from Supt.
Kirkpatrick. It is the only thread in the production about standing access rather than a
single search, and structurally the largest allegation left. Matt has passed over it twice
without saying why; offer it once more, then stop pushing.

### Recurring names

8th District Persons Crimes (334 Royal St) accounts for most of the correspondence:
Bonura, D'Alessandro, Cherny, Howard, Huntington. ISB/Homicide (1615 Poydras): Willyard,
Barrere, Stewart, Marshall. Others seen once: Edgerson (3rd District), Gantner and Dulaney
(6th District), Brown (1st District), Singleton (5th District), Lane, Carroll, Henderson.
The unit concentration supports asking for unit-level rather than officer-level findings.
- **Complaint template doc:**
  https://docs.google.com/document/d/1l8la3w0mCclXj1Hzf0qo8gpCCA1NMBNq4ucogfSYoJI
  (Google returns a sign-in wall to `web_fetch` — ask him to paste the text if you need
  more than the opening paragraph reproduced above)
