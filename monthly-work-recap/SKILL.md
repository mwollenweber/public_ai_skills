---
name: monthly-surveillance-recap
description: "Write Matt's monthly \"[Month] [Year] in Review\" surveillance recap for insomniac.tech — gather the month's blog posts, records requests, complaints, IG posts, and repo commits, build the metrics table, verify every claim, then stage in WordPress."
---

# Monthly Surveillance Recap

A chronological, link-dense recap of Matt's surveillance work for the month just ended, published on insomniac.tech. The point of the post is to drive petition signatures; the log of work is the evidence behind the ask.

Run it at the end of the month or in the first week of the following month.

## Standing facts

- Blog: https://insomniac.tech (WordPress, `/wp-admin/`)
- NextRequest requester id: **818818** — https://nola.nextrequest.com/requests?requester_ids=818818
- Complaint PDFs ("Initial Complaint Emails"): https://drive.google.com/drive/folders/1mHbZJrOvf7quzMeScyH_mDG6LJqD_ohJ
- PIB complaint tracker (Google Sheet, tabs Filings / Cases): https://docs.google.com/spreadsheets/d/1S0JhBWmBZfFmdVxDC95gPztAoz3YBxuAjfhWnqwluBY/edit
- Public request templates: https://drive.google.com/drive/folders/1HBbNuGHwVmN9xLf9cqaf5xZ6L-Uold9H
- Skills repo: https://github.com/mwollenweber/public_ai_skills
- Instagram: https://www.instagram.com/matthew.wollenweber/
- Petition: https://www.change.org/p/stop-illegal-surveillance-in-new-orleans
- Complaints always go to `policemonitor@nolaipm.gov`, `hotline@nolaoig.gov`, `nopdpib@nola.gov`

Ask Matt at the start, in one message, for: (1) the current petition signature count; (2) anything that happened off these sources (a talk, a council appearance, press, a meetup, a new petition); (3) any complaints he filed himself that aren't in the Drive folder yet (he sometimes files from a previous document without exporting the PDF). Keep working while you wait.

## 1. Gather

Do all of this before writing a word. Most of it needs the logged-in browser (Claude in Chrome). Open a **new tab** for scraping; don't navigate the tab Matt is working in.

### Blog posts

WordPress REST API, via WebFetch:

```
https://insomniac.tech/wp-json/wp/v2/posts?after=YYYY-MM-01T00:00:00&before=YYYY-MM-01T00:00:00&per_page=20&orderby=date&order=asc&_fields=date,link,title
```

Query in halves (e.g. 1st–14th, 15th–end) — a single call gets summarized down and silently drops posts. WebFetch caches by URL for ~15 minutes and has returned the *first* half's cached result for a second-half query with the same shape; if the second call returns the same posts as the first, vary the `after=` boundary (e.g. `T23:59:59`) and drop `_fields`. Keep paging (`after=<last date>`) until the tool says EMPTY. Then WebFetch each post URL for the specifics you plan to cite (request numbers, officer names, counts, Drive/gist links).

### Records requests (NextRequest)

The public request pages are login-walled to WebFetch, and the site is a SPA so fetching HTML gets you a shell. Use the JSON API from a logged-in tab with `javascript_tool`:

```js
// all requests (page_size caps at 100; `page`/`offset` are ignored)
const base='/client/requests?requester_ids[]=818818&page_size=100';
const a=await (await fetch(base,{headers:{Accept:'application/json'}})).json();
// the OTHER 100 — flip the sort, then dedupe by id
const b=await (await fetch(base+'&sort_field=request_date&sort_order=asc',{headers:{Accept:'application/json'}})).json();
```

Each record has `id`, `request_date` (MM/DD/YYYY, may be a day earlier than Matt's notes because of timezone), `due_date`, `request_state`, `department_names` (a string, not an array), `request_text`. Stash the merged map on `window.__reqs` so later calls don't refetch.

- **Filed this month:** filter `request_date` on `MM/DD/YYYY`.
- **Activity this month:** `/client/requests/{id}/timeline` per request returns `{total_count, timeline:[{timeline_name, timeline_display_text (HTML), timeline_byline}]}`. Filter `timeline_byline` on `/Month \d+, YYYY/`. `timeline_name` values worth keeping: `Request Closed`, `Request Reopened`, `Document(s) Released to Requester` (display text is the filename), `Invoice Sent - $N`, `Invoice Paid`, `External Message`. Strip HTML from `timeline_display_text`. Fan out with `Promise.all` in batches of ~80; a sequential loop over 150+ requests times the tool out. Drop `Request Opened` / `Department Assignment` / auto-acknowledgement noise.
- Non-surveillance requests (e.g. Mardi Gras float incidents) show up in the same account. Read `request_text` and leave them out.

### Complaints

On the Drive folder page, Drive's new UI has no `[data-id]` on rows. Use:

```js
[...document.querySelectorAll('[role="row"]')].map(r=>{const id=(r.outerHTML.match(/data-id="([^"]+)"/)||[])[1]; const t=r.innerText.split('\n'); return id+' :: '+t[0]+' :: '+(t.find(x=>/^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/.test(x))||'')})
```

Output truncates around 2 KB, so `slice` the array and page. The Drive connector (`mcp__Google_Drive__search_files` with `parentId=`) has returned `{}` for this folder — use the browser for the listing.

Then read each candidate PDF with `mcp__Google_Drive__read_file_content` — the export contains the Gmail header with the **actual send timestamp**, which is what determines whether it counts for this month. Also read any PDF the blog posts link that is *not* in the folder listing (some live elsewhere in Drive).

Complaints against NOPD Public Affairs / social media (the @nopdnews First Amendment track) are a separate thread from the FRT complaints. They may exist only as an "Exhibit A" transcription in an escalation packet rather than a Gmail export; count them, and link nothing if there's no shareable PDF.

### PIB adjudications

Read the tracker sheet's **Cases** tab with `mcp__Google_Drive__read_file_content`. The connector only returns a sample (~10 of 18 rows), so cross-check against the most recent scoreboard post and Matt's notes. Count: case numbers closed this month and their disposition (sustained / not sustained / "No further investigation" / "Other as approved by the Captain"), new case numbers opened, and cases still without a closing letter.

### Instagram

Grab post shortcodes from the profile grid (`document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]')`), then for each:

```js
const t = await (await fetch('/p/'+code+'/')).text();
t.match(/<meta property="og:description" content="([^"]{0,600})"/)
```

That yields date, caption, like and comment counts without hitting the rate-limited `web_profile_info` endpoint. Pinned posts sort to the front of the grid and are usually out of date order — check dates, don't assume grid position. Posts with no caption need a screenshot to classify (an annotated complaint email counts; a bike photo doesn't). Include only surveillance-related posts. Reels are the "videos" metric.

### Repo

`api.github.com` needs repo access this session may not have, and WebFetch is blocked by GitHub's robots.txt. Read `https://github.com/mwollenweber/public_ai_skills/commits/main/` in the browser tab with `get_page_text`. Also catch tools published outside the repo (GitHub gists linked from posts).

### National context (optional)

WebSearch for the month's ALPR/facial-recognition news. Matt has asked to keep this minimal: no 404 Media plugs, no vendor tallies that drift between outlets. One sentence at most, and only if it's a hard fact (a state order, a court ruling) with a second source.

## 2. Draft

Target **600–700 words** excluding URLs (a heavy month runs long; don't cut items to hit 500). Structure:

1. **Title:** `[Month] [Year] in Review`
2. **Opening paragraph — generic, not a list of deliverables.** A strong month continuing the fight against illegal surveillance in New Orleans, and thanks to the people who read, share, sign and show up. No scene-setting, no throat-clearing, no inventory of what was filed (the table does that).
3. **The ask, up front** — link the petition, name who it goes to (City Council and Mayor Moreno), state the current signature count, and ask readers to sign, share it on social media, and ask their friends to sign. Say the rest of the post is the reason it exists.
4. **"[Month] by the numbers"** — a two-column table (`Metric | Month Year`) with one row each: Complaints filed (IPM, OIG, PIB) · Complaints adjudicated by PIB · Sustained · Closed without investigation (quote the box PIB checked) · Cases still awaiting a closing letter · Public records requests filed · Records productions received · Public meetups · Blog posts · Videos. Keep outcome rows separate; don't merge them into one cell.
5. **Status paragraph** — where the production review stands: which productions/months are fully worked ("every qualifying thread is now a filed complaint"), what's next, and what's blocking it (usually an overdue request — name it, link it, give the filed date and how long it's been open, computed from the actual dates).
6. **"Here's my [Month] work:"** then one bold-dated paragraph per item, chronological:
   `**Sep 13 — [Post Title](url).** One or two sentences.`
   Blog posts link the title. Requests link the request number. Complaints link the officer's name to the PDF. IG posts get a trailing `([IG](url))`. Skills link the repo; scripts link the gist.
7. **"The City answered"** — one dated block grouping every City response, not one line each.
8. **Close** — repeat the petition link, ask them to share it and ask one friend who lives here to sign.

Voice: direct, plain, short sentences, fact-grounded. No rhetorical flourish, no hype, no em-dash-heavy throat-clearing. Fragments for emphasis are fine ("New Orleans is not the exception. It's the pattern."). **No dollar amounts** — not invoice totals, not budget figures; use percentages or plain words instead.

## 3. Verify — do not skip

Check every factual claim against the source before publishing, and tell Matt anything you could not verify. Real errors this process has caught:

- **Drive's "modified" date is not the filing date.** Complaint PDFs re-saved in September were actually emailed in January. Open every complaint PDF and read the Gmail send timestamp. If a PDF has no timestamp, say so — don't infer one from the file date.
- **Complaints can be filed without a PDF in the folder.** Matt sometimes files from a previous document and skips the export. Report the folder-verified count, list the ones his notes say he filed that you couldn't verify, and let him settle the number.
- **Matt's own dates and years drift.** "October and November 2026 emails" meant 2025; "almost 10 months" was 8.5. Compute durations from the actual dates and use the production's real date range. Correct it in the draft and tell him why.
- **Request numbers don't map to templates by sequence.** Consecutive numbers filed the same day are not in template order. Read each `request_text` and confirm what the request actually asks for before describing it.
- **Don't over-claim what the complaints allege.** Some threads are person-tracking or video requests, not facial recognition. His complaint emails say "illegal use of FRT and mass surveillance" — use that framing for a mixed batch.
- **Watch which vendor is which.** Project NOLA runs Dahua hardware (FCC-banned from new sale); Flock is the ALPR company; Axon is the ALPR audit-log request. Don't merge them.
- **Date blocks must contain their contents.** If a City message lands Aug 17, don't file it under an "Aug 19–25" heading.
- **Quote counts and quotes exactly.** Cross-check any national figure against a second outlet; they drift.
- **Escalations: filed vs. drafted.** If notes say an escalation packet was *built*, don't write that it was *sent*. Ask.
- Flag any claim only Matt can confirm (e.g. "my best-performing post ever", meetup count) rather than asserting it.

## 4. Publish

Draft in WordPress and leave it for Matt to publish. Open `https://insomniac.tech/wp-admin/post-new.php` in the scraping tab (the first `navigate` sometimes doesn't take — screenshot to confirm the editor loaded, then retry). Build Gutenberg block HTML (`<!-- wp:paragraph -->…`, `<!-- wp:table --><figure class="wp-block-table"><table>…</table></figure><!-- /wp:table -->`) and inject it:

```js
window.__html = "...block html...";
wp.data.dispatch('core/block-editor').resetBlocks(wp.blocks.parse(window.__html));
wp.data.dispatch('core/editor').editPost({title:'Month Year in Review'});
```

For later edits, string-replace on `window.__html` and `resetBlocks` again, or `updateBlockAttributes(clientId, {content})` for a single paragraph.

`javascript_tool` gotchas on wp-admin:
- Any call whose **return value** contains a string (title, block content, even `'ok'`) comes back `[BLOCKED: Cookie/query string data]` — but the code still ran. Return a **number** only (e.g. `getBlocks().length`, or an `indexOf` check) and confirm with a screenshot.
- Setting the title makes WordPress **autosave a draft** on its own (URL changes to `post.php?post=NNNN`). That's fine; tell Matt the post number. **Never click Publish or Save draft yourself.**

Also save a markdown copy to `/mnt/user-data/outputs/` and deliver it with SendUserFile. Re-send it after each revision round.

## javascript_tool gotchas (general)

- Printing a URL containing a query string gets the whole result blocked. Strip links before printing (`.replace(/<a href="[^"]*">/g,'[L]')`).
- Navigating the tab clears `window.*` globals — re-fetch rather than relying on state from a previous call.
- Long `await` loops fail; batch with `Promise.all`.
- `fetch` is same-origin — be on the right site's tab before calling its API.
- Output truncates around ~2 KB; slice and page through results.
- Bash/curl in the workspace can't reach insomniac.tech; use WebFetch or the browser.
