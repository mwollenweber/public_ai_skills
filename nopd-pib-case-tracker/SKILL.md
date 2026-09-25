---
name: "nopd-pib-case-tracker"
description: "Build or refresh Matt's NOPD PIB Complaint Tracker Google Sheet from his PIB email: case ID, officers, investigator, status, disposition, filing PDF link, and date filed for each case."
---

# NOPD PIB Case Tracker

Rebuild the tracker that maps every NOPD Public Integrity Bureau (PIB) case number Matt has received to:

- the officers covered
- the investigator
- whether the case is open or closed
- the disposition
- a link to the filing PDF
- the date the complaint was filed

The sources are his Gmail (mjw@insomniac.tech) and his Drive complaints folders.

Use this skill when Matt asks for any of these, even if he doesn't name the tracker:

- update, refresh or rebuild the PIB tracker
- find his PIB case, complaint, CTN or control numbers
- which complaints are open or closed
- what PIB decided

## Constants

- **Gmail:** mjw@insomniac.tech, at `mail.google.com/mail/u/0`. There is no Gmail connector, so use Claude in Chrome.
- **Filing PDFs:** the Drive folder "Initial Complaint Emails", `1mHbZJrOvf7quzMeScyH_mDG6LJqD_ohJ`.
  - It sits inside the NOPD folder, `1w0qvjz5loDPvL35aygRbwhIWrSpPdEU0`.
  - This folder is shared with PIB investigators. Never put the tracker in it.
- **Closing letters:**
  - Loose PDFs in the NOPD folder.
  - Case subfolders:
    - `2026-0003-0` = `171J2lq_K4Zxr4A1AavJmiXLZ_2ADgJf-`
    - `2026-0059-P` = `1PLEduFDDke945vuX5dx6XObzDbgD84g6`
    - `2026-0061-P` = `12axa6mjrEOeiPWJ6yqj9fn-kC8yBSb9N`
    - `2025-0366-P` = `1lNUFBD1YjhhueThGwNFUJQWIq-Z77nAK` (its `Findings Letter` subfolder holds photos of the letter)
  - Other closing letters exist only as Gmail attachments.
- **Tracker:** the Google Sheet "NOPD PIB Complaint Tracker", `1S0JhBWmBZfFmdVxDC95gPztAoz3YBxuAjfhWnqwluBY`.
  - It lives in the mjw@insomniac.tech My Drive root and is private.
  - A refresh replaces its contents in place so the URL stays the same.
- **Case ID patterns:**
  - `20\d\d[-.]\d{3,4}-?[A-Z]`, e.g. 2026-0126-I or 2026.0056-O.
  - OIPM referral numbers look like `CC2026-0105`.
  - Suffixes change: a case opened as 0084-P closed as 0084-N. Don't treat the suffix as meaningful unless a letter explains it.

## Before starting

Matt wants clarifying questions. Ask one AskUserQuestion covering:

- **Lookback:** default is 2 years.
- **Full rebuild or new activity only:** new activity means anything since the tracker's "As of" date.

If he's away, default to a full rebuild over 2 years and say so.

Load the `chrome-browser` skill. Call `tabs_context_mcp`, then work in your own new tabs and close them at the end.

## Step 1: Find the PIB emails

1. In your tab, search Gmail for `from:nola.gov newer_than:2y`.
2. Read the result rows with JS:
   - rows: `tr.zA`
   - date: `.xW span[title]`
   - legacy thread ID: `[data-legacy-thread-id]`
   - senders: `span[email]`
   - subject: `.y6` / `.bog`
   - case IDs: regex over each row's `textContent`
3. Keep every PIB thread, including ones whose subject has no case ID. Signs of a PIB thread:
   - "PIB Investigation"
   - "Public Integrity Bureau"
   - "closing letter"
   - "CTN"
   - PIB staff senders, e.g. Diane.Walker, srcontreras, Dwight.Richards, sekennedy, nhickman, alambrose, TWimberly
4. Run a second search for forwards and OIPM/OIG context: `(CTN OR "closing letter" OR "tracking number" OR "control number" OR PIB) newer_than:2y -from:nola.gov`.

## Step 2: Read each thread in full

- **Never navigate to Gmail's print view.** It opens the print dialog and freezes the tab. If that happens, close the tab.
- **Fetch the print view from JS inside the Gmail tab instead:**
  - Get `ik` from `GLOBALS[9]`.
  - URL: `/mail/u/0/?ik=${ik}&view=pt&search=all&permthid=thread-f:${BigInt('0x'+legacyHex)}`
  - Quoted text comes back collapsed, so the output stays small.
- **Strip HTML with regex.** DOMParser and innerHTML are blocked by TrustedHTML.
- **Don't return long text from `javascript_tool`.** Its output is cut at about 1,000 characters, and output containing query strings is blocked. Instead:
  1. Replace the page body with `<article><pre>` holding the text, via `textContent`.
  2. Read it with `get_page_text`, a few threads at a time.
  3. Reload the tab before using Gmail's UI again.

For each case, record:

- the case ID and any alternate numbers
- who emailed about it (the investigator)
- the date it was assigned
- officers named
- filings referenced: Matt's email send dates, subject lines, OIPM CC numbers
- any closing-letter attachment, with its file name and date

## Step 3: Get the dispositions from the closing letters

The emails only say "attached is the closing letter". The disposition is in the attachment.

**Drive first.**

- The Drive connector is signed in as mwollenweber@gmail.com, so `search_files` returns nothing for these folders.
- List the folders in the Chrome Drive UI and collect the `data-id` attributes.
- Then call `mcp__Google_Drive__read_file_content` by file ID. This works.

**Image-only PDFs.** When `read_file_content` returns nothing:

- Open `https://drive.google.com/thumbnail?id=FILEID&sz=w560` in a tab.
- Use `zoom` to read it.

**Letters that exist only as Gmail attachments.**

1. Fetch the print-view HTML.
2. Find the `attid` link and change `disp=attd` to `disp=safe`.
3. Fetch the bytes in JS.
4. Check the image filter:
   - **`/DCTDecode` (JPEG):**
     1. Slice out the stream bytes.
     2. Make a Blob URL and show it in an `<img>`.
     3. Screenshot it.
   - **`/CCITTFaxDecode`:**
     1. Open the thread in Gmail's normal UI.
     2. Click the attachment card to open Gmail's previewer.
     3. Screenshot it.

Chrome's built-in PDF viewer does not render in screenshots.

From each letter, record:

- the closing date
- the per-officer finding (Sustained, Not Sustained, Unfounded or Exonerated), with the rule cited and any corrective action
- or, for a preliminary inquiry, the "no further investigation" reason quoted closely
- every officer the letter lists, by email date
- the investigator or contact the letter names
- initials in the signature block, e.g. `AEK/KAS/djr` = Dwight J. Richards

## Step 4: Get the filing dates

1. Search `in:sent newer_than:2y subject:(complaint OR complaints)`. Page through with `/p2`.
2. Fetch each thread's print view.
3. Take the date and recipients of the first message from mjw@insomniac.tech.
4. Flag threads that contain later sends from Matt. Re-sends can land in a different PIB case.
5. The Gmail send time is the filing date. The PDF's modified date in Drive is not.

## Step 5: List the filing PDFs

- Drive virtualizes the list:
  - Setting `scrollTop` from JS doesn't load more files.
  - Scroll with the mouse wheel over the list area, then collect `data-id` and tooltip names after each scroll until the count stops growing.
- Skip Google Docs copies of PDFs.
- Check the case subfolders for filings missing from the main folder. For example, the Biscoe complaint PDF is only in the 2026-0059-P folder.

## Step 6: Match filings to cases

- **Direct:** a PIB letter or email names the officer and the email date, or the date range, e.g. "You sent your complaints on September 9-13".
  - Consolidated cases list filings by email date. For example, 2026-0037-N covered the Jan 3-22, 2026 emails and 2026-0003-O covered Feb 1-16, 2026.
- **Inferred:** PIB didn't name the filing. Match by officer, send-date window and OIPM CC numbers. Mark the row Inferred.
- **Filings in two cases:** one filing can belong to two cases, e.g. an original send and a re-send. Show both.
- **No case found:** mark the filing "None found".
- **Unidentified case numbers:** give them a Cases row with Officers = "Not identified".
- **Discrepancies:** never resolve them silently. Put them in Notes. Examples:
  - the email and the letter give different numbers
  - a P→N reclassification
  - a "duplicate of X" claim that X's letter doesn't support
  - typos in a letter

## Step 7: Build the workbook

Use openpyxl, and write the build script to the scratchpad. Create three tabs.

**Filings** — one row per filing, 100+ rows. Columns:

- Case ID
- Officer(s) in filing
- Investigator
- Status
- Outcome / disposition
- Filing PDF, hyperlinked to `https://drive.google.com/file/d/ID/view`
- Date filed
- Case match (Direct / Inferred)
- Notes

Include filings that have no PDF, with the file name prefixed "(no PDF in folder)".

**Cases** — one row per case ID. Columns:

- Case ID
- Date filed (the earliest filing)
- Officer(s) covered
- Investigator
- Status
- Outcome / disposition
- Closing letter date
- Closing letter link: the Drive file, or the Gmail thread for attachment-only letters
- Number of filing PDFs
- PIB email threads, as `https://mail.google.com/mail/u/0/#all/<legacyHex>`
- Notes

**Sources & method** — the as-of date, the searches used, and what Direct, Inferred and Open mean.

Formatting:

- A header fill
- Wrapped text
- Freeze pane at B2
- Auto-filter

For status, write `Closed`, or `Open (no closing letter in email as of YYYY-MM-DD)`.

## Step 8: Check the links

From a tab on drive.google.com:

1. Fetch `/file/d/ID/view` for every file ID you used.
2. Compare each page `<title>` to the expected file name.
3. Fix any mismatch before publishing.

## Step 9: Publish to the Google Sheet

Don't use Drive MCP `create_file`:

- It creates files in the gmail account, not mjw@insomniac.tech.
- A base64 xlsx is too large to pass reliably.

Import through the browser:

1. Copy the xlsx into the working directory (`/home/claude`). `file_upload` rejects `/mnt/user-data/outputs`.
2. Open the tracker, `docs.google.com/spreadsheets/d/<trackerId>/edit`. For a new tracker, use `/spreadsheets/u/0/create`.
3. Choose File > Import, then the Upload tab. Don't click Browse: it opens a native dialog.
4. Get the file into the picker:
   1. The picker's `<input type=file>` is inside a same-origin iframe (`docs.google.com/picker`), and `find` can't reach it.
   2. Create a temporary `<input type=file aria-label="Claude xlsx upload input">` in the top document.
   3. `find` it and `file_upload` the xlsx to it.
   4. In JS, move the file across: `new DataTransfer()`, `dt.items.add(file)`, `pickerInput.files = dt.files`, then dispatch a `change` event.
   5. Remove the temporary input.
5. Choose Import location "Replace spreadsheet", then Import data.
6. For a new sheet, rename it in the title box: click it, press cmd+a, Delete, type the name, Return.
7. Check the tabs, hyperlinks and share state. It should stay private.

The picker also saves a copy of the xlsx to Matt's My Drive. Tell him; don't delete it without asking.

## Report

Keep the report short:

- the tracker link
- counts: total cases, closed versus open, how many sustained
- then list:
  - inferred matches
  - PIB discrepancies
  - unidentified case numbers
  - filings with no case or no PDF

Open means no closing letter was found in email, not that PIB confirmed the case is open.

Never email PIB or any other party as part of this skill. It is read-only apart from the tracker.