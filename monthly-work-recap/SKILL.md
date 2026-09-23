---
name: monthly-surveillance-recap
description: "Write Matt's monthly \"[Month] [Year] in Review\" surveillance recap for insomniac.tech — gather the month's blog posts, records requests, complaints, IG posts, and repo commits, verify every claim, then draft and publish."
---

# Monthly Surveillance Recap

A chronological, link-dense recap of Matt's surveillance work for the month just ended, published on insomniac.tech. The point of the post is to drive petition signatures; the log of work is the evidence behind the ask.

Run it in the first week of the following month.

## Standing facts

- Blog: https://insomniac.tech (WordPress, `/wp-admin/`)
- NextRequest requester id: **818818** — https://nola.nextrequest.com/requests?requester_ids=818818
- Complaint PDFs ("Initial Complaint Emails"): https://drive.google.com/drive/folders/1mHbZJrOvf7quzMeScyH_mDG6LJqD_ohJ
- Public request templates: https://drive.google.com/drive/folders/1HBbNuGHwVmN9xLf9cqaf5xZ6L-Uold9H
- Skills repo: https://github.com/mwollenweber/public_ai_skills
- Instagram: https://www.instagram.com/matthew.wollenweber/
- Petition: https://www.change.org/p/stop-illegal-surveillance-in-new-orleans
- Complaints always go to `policemonitor@nolaipm.gov`, `hotline@nolaoig.gov`, `nopdpib@nola.gov`

Ask Matt at the start whether anything happened off these sources (a talk, a council appearance, press, a new petition) — the sources below only capture what left a trace.

## 1. Gather

Do all of this before writing a word. Most of it needs the logged-in browser (Claude in Chrome). Open a **new tab** for scraping; don't navigate the tab Matt is working in.

### Blog posts

WordPress REST API, via WebFetch:

```
https://insomniac.tech/wp-json/wp/v2/posts?after=YYYY-MM-01T00:00:00&before=YYYY-MM-01T00:00:00&per_page=20&orderby=date&order=asc&_fields=date,link,title
```

Query in two halves (e.g. 1st–14th, 14th–end) — a single call gets summarized down and silently drops posts. Then WebFetch each post URL for the specifics you plan to cite.

### Records requests (NextRequest)

The public request pages are login-walled to WebFetch, and the site is a SPA so fetching HTML gets you a shell. Use the JSON API from a logged-in tab with `javascript_tool`:

```js
// all requests (page_size caps at 100; `page`/`offset` are ignored)
const base='/client/requests?requester_ids[]=818818&page_size=100';
const a=await (await fetch(base,{headers:{Accept:'application/json'}})).json();
// the OTHER 100 — flip the sort, then dedupe by id
const b=await (await fetch(base+'&sort_field=request_date&sort_order=asc',{headers:{Accept:'application/json'}})).json();
```

Each record has `id`, `request_date`, `due_date`, `request_state`, `department_names`, `request_text`.

- **Filed this month:** filter `request_date` on `MM/DD/YYYY`.
- **Activity this month:** `/client/requests/{id}/timeline` per request, filter `timeline_byline` on `/Month \d+, YYYY/`. Look for `Request Closed`, `Document(s) Released to Requester`, `Invoice Sent`, `External Message`. Fan out with `Promise.all` in batches of ~80; a sequential loop over 155 requests times the tool out.
- **Released documents:** `/client/requests/{id}/folders` shows counts; for actual filenames load `https://nola.nextrequest.com/requests/{id}` in the tab and `get_page_text` (the Documents entries appear in the timeline).

### Complaints

List the Drive folder in the browser (`get_page_text` on the folder URL gives names + modified dates; `document.querySelectorAll('[data-id]')` gives file IDs for links).

Then read each candidate PDF with `mcp__Google_Drive__read_file_content` — the export contains the Gmail header with the **actual send timestamp**, which is what determines whether it counts for this month.

### Instagram

Grab post shortcodes from the profile grid (`document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]')`), then for each:

```js
const t = await (await fetch('/p/'+code+'/')).text();
t.match(/<meta property="og:description" content="([^"]{0,600})"/)
```

That yields date, caption, like and comment counts without hitting the rate-limited `web_profile_info` endpoint. Pinned posts sort to the front of the grid and are usually out of date order — check dates, don't assume grid position. Include only surveillance-related posts.

### Repo

`api.github.com` needs repo access this session may not have, and WebFetch is blocked by GitHub's robots.txt. Read `https://github.com/mwollenweber/public_ai_skills/commits/` in the browser tab instead.

### National context (optional, one short paragraph)

WebSearch for the month's ALPR/facial-recognition news — Flock contract cancellations, state legislation, major reporting. Attribute counts to whoever compiled them; advocacy-group tallies move between outlets.

## 2. Draft

Target **500–600 words**. Structure:

1. **Title:** `[Month] [Year] in Review`
2. **Opening paragraph** — action-led, first person, summarizing what he *did*: "In August I trained a room at the Healing Center to pull NOPD records, published my request templates, filed four complaints…" Never open with a scene-setting or throat-clearing sentence.
3. **Optional second paragraph** — national context, ending on why New Orleans is the pattern rather than the exception.
4. **The ask, up front** — one short paragraph linking the petition, naming who it goes to (City Council and Mayor Moreno), and saying the rest of the post is the reason it exists.
5. **"Here's my August work:"** then one bold-dated paragraph per item, chronological:
   `**Aug 13 — [Post Title](url).** One or two sentences.`
   Blog posts link the title. Requests link the request number. Complaints link the officer's name to the PDF. IG posts get a trailing `([IG](url))`.
6. **Close** — repeat the petition link and ask the reader to send it to one person who lives here.

Voice: direct, plain, short sentences, fact-grounded. No rhetorical flourish, no hype, no em-dash-heavy throat-clearing. Fragments for emphasis are fine ("New Orleans is not the exception. It's the pattern."). Group the City's responses into one dated block rather than one line each.

## 3. Verify — do not skip

Check every factual claim against the source before publishing, and tell Matt anything you could not verify. Real errors this process has caught:

- **Drive's "modified" date is not the filing date.** A complaint PDF re-saved in August was actually emailed two months earlier. Open every complaint PDF and read the Gmail send timestamp. If a PDF has no timestamp, say so — don't infer one from the file date.
- **Request numbers don't map to templates by sequence.** Consecutive numbers filed the same day are not in template order. Read each `request_text` and confirm what the request actually asks for before describing it.
- **Don't over-claim what the complaints allege.** Some threads are person-tracking or video requests, not facial recognition. His complaint emails say "illegal use of FRT and mass surveillance" — use that framing for a mixed batch.
- **Watch which vendor is which.** Project NOLA runs Dahua hardware (FCC-banned from new sale); Flock is the ALPR company. Don't merge them.
- **Date blocks must contain their contents.** If a City message lands Aug 17, don't file it under an "Aug 19–25" heading.
- **Quote counts and quotes exactly.** Cross-check any national figure against a second outlet; they drift.
- Flag any claim only Matt can confirm (e.g. "my best-performing post ever") rather than asserting it.

## 4. Publish

Draft in WordPress and leave it for Matt to publish. In the editor tab:

```js
wp.data.select('core/editor').getEditedPostContent()          // read
wp.data.select('core/block-editor').getBlocks()               // find the block
wp.data.dispatch('core/block-editor').updateBlockAttributes(clientId, {content: html})
```

**Never click Publish or Save draft.** Make the edits and tell him they're unsaved.

Also save a markdown copy to `/mnt/user-data/outputs/` and deliver it with SendUserFile.

## javascript_tool gotchas

- Printing a URL containing a query string gets the whole result blocked. Strip links before printing (`.replace(/<a href="[^"]*">/g,'[L]')`).
- Navigating the tab clears `window.*` globals — re-fetch rather than relying on state from a previous call.
- Long `await` loops fail; batch with `Promise.all`.
- `fetch` is same-origin — be on the right site's tab before calling its API.
- Output truncates around ~2 KB; slice and page through results.
