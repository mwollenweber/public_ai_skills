# NOPD Monthly Public Records Requests — Runbook

Monthly routine for filing public records requests with the City of New Orleans (NextRequest portal) for NOPD records. Run at the start of each month, covering the month just ended.

## Inputs

Portal: https://nola.nextrequest.com/requests/new (must already be signed in)

Ask which templates are in scope this cycle — **not every template is filed every month**. Matt supplies the list. Confirm the target month if it isn't obviously the previous one.

Standard order (renumbered Sept 2026 — drones moved from step 2 to step 4):

| Step | Subject | Template doc ID |
|---|---|---|
| 1 | City of NOLA PN Template — NOPD ↔ Project NOLA communications / keywords | `1rkmbOIaHyatGPNDU7B_H3Xheqigt-msYfS6M-XHQI5A` |
| 2 | FRT and Surveillance Request — NOPD Forms 357 and 360 | `1DwqIpyOIAGjIra_nvXV_cdzCR0pgvJWRYKO28JcrUdI` |
| 3 | LA-SAFE Request For Information | `1sB7V2CixYDjpx8kRrV6dI0SB3PswbSUfh0P6ajq8D-4` |
| 4 | Monthly Drone Log Request — sUAS / drone flight logs | `1wY0pqwGOGYmfXN8f7N0iScdknD2yiTFJ56uCN9JM3UE` |

All go to department **Police Department (NOPD)**.

Read each template with the Google Drive connector (`read_file_content` on the doc ID) — that works and is the fast path. Only if the connector is unavailable, open the doc in the browser and screenshot it; Google Docs is canvas-rendered and plain text extraction from the page fails.

Matt's public copies: https://drive.google.com/drive/folders/1HBbNuGHwVmN9xLf9cqaf5xZ6L-Uold9H

## The one edit that changes every month

Each template hardcodes a date range. Replace it with the **previous calendar month**, in the templates' `YYYY-MMM-DD` format with an uppercase three-letter month:

- First day, e.g. `2026-AUG-01`
- Last day, e.g. `2026-AUG-31` (watch 28/29/30-day months)

Where it appears:

| Step | Location of date range |
|---|---|
| 1 | Opening paragraph, "…or emailed between X and Y involving any of the following…" |
| 2 | End of opening paragraph, "…or submitted between X and Y." |
| 3 | Line after the numbered list, "that were created, updated, edited, emailed, or submitted between X and Y." |
| 4 | First sentence, "For the period between X and Y." |

Everything else is copied verbatim. Do not fix wording — see the typo note under Gotchas.

## Procedure, per request

1. Read the template doc.
2. Go to https://nola.nextrequest.com/requests/new (fresh page for each request).
3. Set the **Request description** — see "Filling the description" below.
4. **Department:** type `Police` into the department search box, click `Police Department (NOPD)`, then press Escape. The dropdown reopens after selecting; verify the field reads "Police Department (NOPD)".
5. Fill the contact fields. Name and Email prefill; the rest are required and do **not** persist between submissions — re-enter every time:
   - Phone: 504-952-6541
   - Street address: 5900 Patton St
   - City: New Orleans · State: Louisiana (`LA`) · Zip: 70115
   - Company: blank
6. Run the verification snippet below.
7. Submit, then record the request number and URL.

## Filling the description

The description box is a Quill rich-text editor. **Typing long bodies into it is unreliable** — an email address like `LASAFE.REQUESTS@LA.GOV` triggers autolink handling that jumps the cursor and splices the remaining text into the middle of a list item.

**Set the content programmatically.** Write HTML into `.ql-editor` and dispatch an `input` event:

```js
const el = document.querySelector('.ql-editor');
const li = t => `<li data-list="ordered"><span class="ql-ui" contenteditable="false"></span>${t}</li>`;
el.innerHTML =
  `<p>…opening paragraph…</p><p><br></p>` +
  `<ol>${items.map(li).join('')}</ol><p><br></p>` +
  `<p>…each remaining paragraph in its own <p>, separated by <p><br></p>…</p>`;
el.dispatchEvent(new Event('input', {bubbles: true}));
```

Then verify Quill accepted it: re-read `el.innerText.length` and the `li` count. Content that survives an editor update cycle is synced to Quill's model and will submit correctly.

Injection also preserves the templates' bold, which typing cannot: use `<strong>NOPD Form 357</strong>` / `<strong>and NOPD Form 360</strong>` (step 2) and `<strong>ALL</strong>` (step 3), matching prior months. Never paste raw markdown `**asterisks**` — the editor takes them literally.

### Spacing conventions

One blank line (`<p><br></p>`) after the opening paragraph, before and after each list, and between each closing paragraph (digital format, exemption log, fee waiver, three-day response).

Exception — **step 1's criteria block runs tight**: `And matching the following criteria:`, the domain-matching line, the email-address line, and `OR matching ANY of the non-case-sensitive terms:` are consecutive with **no** blank lines between them, and the terms list follows immediately.

**Step 4's list** uses `a.` through `i.` lettering in the source doc, but every prior filing rendered it as a real 1–9 numbered list. Keep the numbered list for consistency with the filing history.

### If typing instead of injecting

Typing `1. ` at the start of an item auto-converts to a real ordered list; type the remaining items as plain text with no manual numbers. Press Enter on the trailing empty list item to exit the list. And **never interleave a `javascript_tool` call between two `type` actions in the same editor** — it drops focus and the next `type` lands wherever the cursor happens to be. Keep click → type → Enter → type in one `browser_batch`.

## Verify before submitting

```js
const f = document.querySelector('form'), el = document.querySelector('.ql-editor');
({fields: Array.from(f.querySelectorAll('input,textarea,select')).map(i => i.name+'='+i.value).filter(s => s.length < 60),
  descLen: el.innerText.length, li: el.querySelectorAll('li').length, head: el.innerText.slice(0,240)})
```

Check: the date range reads the target month, list item counts match the template, and phone/street/city/state/zip are all populated. `description=` showing empty in that dump is normal — the app serializes from Quill at submit time.

## Approval workflow

Default: draft one request at a time, present it for review, submit only after approval, then move to the next. "lgtm" means approved — proceed.

If Matt says up front to file them all, or approves the first and then simply hands over the next template, treat that as standing approval for the run and submit each as it's ready — still reporting the number after each.

## Gotchas

- **The Phone field silently clears.** Re-check it immediately before clicking Make request; it has come back empty after the other fields were filled.
- The form injects yellow guidance banners as you type, which shifts the page. Click controls by element reference rather than remembered screen coordinates, and re-read the page after the layout changes.
- After submitting, requests can't be edited. Corrections have to go in as a follow-up message on the request.
- Submitted requests show visibility "Unpublished" — that's the city's default pending review, not an error.
- The confirmation's "Received" date can lag a day behind — NextRequest's clock, not an error.
- Staff often strip the NOPD department assignment after intake and route to Law Admin. Expected; still select NOPD at submission.
- Requests post publicly, so the description is public text.
- All templates read "Because this request compromises a non-commercial project" — almost certainly meant to be "comprises." Left as-is each month so filings stay identical; fix in the source docs if you want it corrected.

## After the run

Report each number and URL (`https://nola.nextrequest.com/requests/<number>`), append a row to the filing log, and save the numbers to memory in `/areas/public-records-requests.md` with the template used, the covered range, and the due date.

## Filing log

| Coverage period | Filed | Request numbers |
|---|---|---|
| 2026-APR | 2026-05-18 | 26-10296, 26-10297, 26-10298 |
| 2026-JAN – 2026-MAY (catch-up) | 2026-06-06 | 26-11843, 26-11844, 26-11845, 26-11846 |
| 2026-JUN | 2026-07-13 | 26-14633, 26-14634, 26-14635, 26-14636 |
| 2026-JUL | 2026-08-11 | 26-16978, 26-16979, 26-16983, 26-16984 (old order: comms, drones, FRT, LA-SAFE) |
| 2026-AUG | 2026-09-09 | 26-19293 (comms), 26-19294 (FRT/surveillance), 26-19295 (LA-SAFE), 26-19296 (drones) |

## Next month

Coverage period 2026-SEP-01 through 2026-SEP-30, filed early October 2026.
