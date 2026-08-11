# NOPD Monthly Public Records Requests — Runbook

Monthly routine for filing four public records requests with the City of New
Orleans (NextRequest portal) for NOPD records.

## Inputs

Portal: https://nola.nextrequest.com/requests/new (must already be signed in)

Templates, filed in this order every month:

1. City of NOLA FOIA Template — communications / ProjectNOLA keywords
   https://docs.google.com/document/d/1rkmbOIaHyatGPNDU7B_H3Xheqigt-msYfS6M-XHQI5A/edit
2. Monthly Drone Log Request — sUAS / drone flight logs
   https://docs.google.com/document/d/1wY0pqwGOGYmfXN8f7N0iScdknD2yiTFJ56uCN9JM3UE/edit
3. FRT and Surveillance Request — NOPD Forms 357 and 360
   https://docs.google.com/document/d/1DwqIpyOIAGjIra_nvXV_cdzCR0pgvJWRYKO28JcrUdI/edit
4. LA-SAFE Request For Information Request
   https://docs.google.com/document/d/1sB7V2CixYDjpx8kRrV6dI0SB3PswbSUfh0P6ajq8D-4/edit

## The one edit that changes every month

Each template hardcodes a date range. Replace it with the **previous calendar
month**, using the templates' `YYYY-MMM-DD` format with an uppercase
three-letter month:

- First day, e.g. `2026-JUL-01`
- Last day, e.g. `2026-JUL-31` (watch 28/29/30-day months)

Where it appears:

| Template | Location of date range |
|---|---|
| 1 | Opening paragraph, "...or emailed between X and Y involving any of the following..." |
| 2 | First sentence, "For the period between X and Y." |
| 3 | End of opening paragraph, "...or submitted between X and Y." |
| 4 | Line after the numbered list, "that were created, updated, edited, emailed, or submitted between X and Y." |

Everything else is copied verbatim from the template.

## Procedure, per request

1. Open the template doc and read the body. Google Docs is canvas-rendered, so
   text extraction usually fails — take a screenshot and read/zoom instead.
2. Go to https://nola.nextrequest.com/requests/new
3. Type the template body into **Request description**, substituting the new
   date range.
4. **Department:** type `Police` and choose `Police Department (NOPD)`.
   The dropdown reopens after selecting — click a neutral part of the page to
   dismiss it, then verify the field reads "Police Department (NOPD)".
5. Fill the required contact fields (these come from My Settings and don't
   change month to month; Name and Email prefill automatically):
   - Phone, Street address, City, State (Louisiana), Zip
6. **Stop. Do not submit.** Show the draft for approval first.
7. On approval, click **Make request** and record the request number.

## Formatting conventions

- **Numbered lists:** type `1. ` at the start of the first item — the editor
  auto-converts to a real ordered list. Type the remaining items as plain text
  (no manual numbers). After the last item press Enter twice to exit the list;
  that also leaves the blank line that belongs after the list.
- **Spacing:** one blank line after the opening paragraph and before/after each
  list. One blank line between each of the closing paragraphs (digital format,
  exemption log, fee waiver, three-day response).
  In template 1, the criteria block runs tight: `And matching the following
  criteria:`, the domain-matching line, the email-address line, and `OR matching
  ANY of the non-case-sensitive terms:` are consecutive lines with **no** blank
  lines between them, and the terms list follows immediately.
- **Bold and links:** the templates bold `NOPD Form 357` / `and NOPD Form 360`
  (template 3) and `ALL` (template 4), and hyperlink the LA-SAFE address
  (template 4). Reproduce these with the editor's Bold button to stay consistent
  with prior months.
- **Template 2's list** uses `a.` through `i.` lettering in the source doc, but
  prior filings rendered it as a real 1–9 numbered list. Prefer the numbered
  list for consistency with the filing history.

## Approval workflow

Draft one request at a time, present it for review, submit only after approval,
then move to the next. "lgtm" means approved — proceed.

## Gotchas

- The NextRequest form injects yellow guidance banners as you type, which shifts
  the page. Click form controls by element reference rather than by remembered
  screen coordinates, and re-read the page after the layout changes.
- After submitting, requests can't be edited. Corrections have to go in as a
  follow-up message on the request.
- Submitted requests show visibility "Unpublished" — that's the city's default
  pending review, not an error.
- Staff often strip the NOPD department assignment after intake and route to Law
  Admin. Expected; still select NOPD at submission.
- All four templates read "Because this request compromises a non-commercial
  project" — almost certainly meant to be "comprises." Left as-is each month so
  filings stay identical; fix in the source docs if you want it corrected.

## Filing log

| Coverage period | Filed | Request numbers |
|---|---|---|
| 2026-APR | 2026-05-18 | 26-10296, 26-10297, 26-10298 |
| 2026-JAN – 2026-MAY (catch-up) | 2026-06-06 | 26-11843, 26-11844, 26-11845, 26-11846 |
| 2026-JUN | 2026-07-13 | 26-14633, 26-14634, 26-14635, 26-14636 |
| 2026-JUL | 2026-08-11 | 26-16978 (t1), 26-16979 (t2), 26-16983 (t3), 26-16984 (t4) |

## Next month

Coverage period 2026-AUG-01 through 2026-AUG-31, filed early September 2026.