# Public AI Skills

A collection of [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills) I've built and use. Each skill is a self-contained directory with a `SKILL.md` describing the workflow, plus any scripts or reference docs it needs. More skills will be added over time.

To install one, copy its directory into `~/.claude/skills/` (or `.claude/skills/` inside a project), then just ask Claude to do the task — it picks up the skill automatically.

## Skills

### [nola-agenda-search](nola-agenda-search/)

Sweeps New Orleans City Council and committee agendas, plus pending Legistar legislation, for surveillance-related topics (drones, facial recognition, ALPRs, etc.) or any custom keyword list. On a match it adds the meeting to your Google Calendar and sends a push alert with a summary — pair it with a scheduled routine for automatic monitoring.

**Use it:** ask Claude "check the NOLA council agendas" or "is anything about drones before the council?" Requires Python 3 with `pypdf`, a Google Calendar connector, and push notifications.

### [nextrequest-demand-notices](nextrequest-demand-notices/)

Sends Louisiana-law demand notices for overdue public records requests on nola.nextrequest.com. It filters your open requests, verifies each one is genuinely past due against the live on-page due date (the list view is often stale), skips requests where staff are waiting on you or payment is the open issue, then posts a statutory demand citing La. R.S. 44:1 et seq. and 44:35 via "Message agency" — with a confirmation step before anything public goes out.

**Use it:** ask Claude "send demand letters for my overdue NextRequest requests" or "which of my NOLA records requests are past due? escalate them." Requires browser tools and a signed-in NextRequest requester session.

### [nopd-monthly-records-requests](nopd-monthly-records-requests/)

Runbook for the monthly batch of NOPD public records requests on nola.nextrequest.com — Project NOLA communications, facial recognition and surveillance forms (NOPD Forms 357/360), LA-SAFE requests for information, and drone flight logs. It pulls each template from Google Drive, swaps in the previous calendar month's date range, fills the form (injecting the description into the Quill editor, since typing it is unreliable), verifies the fields, and submits one request at a time after approval, then logs the request numbers.

**Use it:** ask Claude "file this month's NOPD records requests" or "run the monthly NextRequest filings for August." Requires browser tools, a signed-in NextRequest session, and a Google Drive connector.

### [nopd-frt-complaint](nopd-frt-complaint/)

Works through a redacted NOPD ↔ Project NOLA email production one thread at a time and turns each qualifying thread into a misconduct complaint. A thread qualifies only when an NOPD officer, writing from a `@nola.gov` address, asked Project NOLA to identify, track, or look out for a *person* (vehicle-only searches and Lagarde-initiated outreach don't count). It verifies every name, item number, timestamp, and page range against the PDF, drafts the complaint email with a fixed subject line and standard opening, and writes a separate analysis file with caveats and an evidence index. It then hands you the draft for the IPM, OIG, and PIB. Nothing is sent without your confirmation. It keeps a running log of filed, rejected, and outstanding threads so later sessions resume where the last one stopped, and for productions of thousands of pages it builds a candidate index first.

**Use it:** ask Claude "find the next thread in 26-651" or "draft a complaint on pages 52–58." Requires the production PDF on disk and `pdftotext` (poppler) or Python `pypdf`; a mail connector is optional.

### [monthly-nopd-surveillance-report](monthly-nopd-surveillance-report/)

Writes the release post for a finished NOPD ↔ Project NOLA records production — one production, one post, distinct from both the per-thread complaints (`nopd-frt-complaint`) and the monthly recap (`monthly-work-recap`). Deconflicts against three sources (sent mail, the Drive complaints folder, and the blog) before drafting so it never describes a complaint as new when it was already filed or already written up, verifies the document's true date span and every count against the PDF, then drafts a short, link-dense post naming what NOPD did, one bullet per filed thread, and hands it over with exactly one placeholder left (the production PDF link).

**Use it:** ask Claude to write the release post for a finished production (e.g. "write the release post for 26-651"). Requires the production PDF, a Google Drive folder listing (via Claude in Chrome — the Drive MCP connector can't enumerate it), and ideally a mail connector to check for complaints already filed.

### [nopd-pib-case-tracker](nopd-pib-case-tracker/)

Builds or refreshes a Google Sheet that maps every NOPD Public Integrity Bureau (PIB) case number to its officers, investigator, open/closed status, disposition, filing PDF, and filing date. It sweeps Gmail for PIB threads and sent complaints, reads each closing letter (from Drive or as a Gmail attachment, including image-only PDFs) to get the per-officer findings, and matches filings to cases, marking each match Direct or Inferred. Discrepancies like reclassified suffixes or conflicting numbers go in Notes instead of being resolved silently. It then writes a three-tab workbook (Filings, Cases, Sources & method), checks every Drive link, and imports the workbook over the existing sheet so the URL stays the same. It never emails PIB or anyone else.

**Use it:** ask Claude "refresh the PIB tracker" or "which of my PIB complaints are still open?" Requires Claude in Chrome with signed-in Gmail, Drive, and Sheets sessions, a Google Drive connector, and Python `openpyxl`.

### [monthly-work-recap](monthly-work-recap/)

Writes a monthly "[Month] [Year] in Review" recap post for a surveillance-accountability blog. Gathers everything the month left a trace of — WordPress posts, NextRequest filings and agency responses, complaint PDFs in Drive, Instagram posts, and repo commits — then drafts a short, chronological, link-dense post and runs a verification pass over every date, number, and case ID before anything is published.

**Use it:** ask Claude "write my August in review" or "draft the monthly recap." Requires browser tools with signed-in sessions for NextRequest, Google Drive, Instagram, and WordPress.
