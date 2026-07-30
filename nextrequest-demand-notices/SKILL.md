---
name: nextrequest-demand-notices
description: >
  Send Louisiana-law demand notices to the records custodian for overdue
  public records requests on nola.nextrequest.com (the City of New Orleans
  NextRequest portal). Filters the requester's open requests, verifies each
  one is genuinely past due against the live on-page due date (never the
  stale list view), composes a statutory demand message citing La. R.S.
  44:1 et seq. and 44:35, and posts it via "Message agency". Use this
  whenever the user asks to send demand letters or follow-ups on overdue
  NOLA public records requests, to "nag the city" about late records, to
  check which of their NextRequest requests are past due and escalate, or
  to re-run the overdue-records demand sweep. Also use it when the user
  mentions NextRequest, the New Orleans records portal, or Louisiana
  public records deadlines in the context of their own pending requests.
compatibility: Requires browser tools able to drive nola.nextrequest.com, and an existing signed-in requester session (or the credential-autofill flow) — never enter passwords manually.
---

# Send Overdue-Request Demand Notices on NextRequest

Post a Louisiana-law demand message to the records custodian for each of
the requester's open requests that is **genuinely** past due. Posting a
message on NextRequest is **public and irreversible** — the entire
procedure below is built around not sending a demand that the timeline
doesn't support. A wrong send (see Notes) is worse than a missed one.

## Procedure

### 1. Filter the request list

On the portal's Requests page, check the **"My requests"** filter and the
**"Open"** status filter, then click **Apply**. This yields the
requester's open requests — the candidate set.

If not signed in, stop and use the credential-autofill flow (or ask the
user to sign in). Never type credentials directly.

### 2. Verify each candidate on its own page — never trust the list view

List-view due dates are frequently stale. For each candidate, open the
request's page and read:

- the live **Due** date in the **Dates** panel, and
- the **full timeline** (staff messages, extensions, invoices, document
  events).

The on-page Due date is the only date that counts. Cross-check it against
what the list showed; a mismatch means the list was stale, not the page.

### 3. Skip rules

Skip the request — and record the reason — if **any** of these hold:

- **Not actually overdue**: the live due date is today or in the future
  (e.g., staff extended it and the list never updated).
- **Ball is in the requester's court**: staff have an outstanding
  question or unresolved dispute awaiting the requester's reply (e.g.,
  "request is overly broad, please provide employee names"). A demand
  letter here is unfounded and undermines the requester's position.
- **Payment, not production, is the open issue**: records were already
  compiled/invoiced and the request is waiting on the requester to pay.

### 4. Calculate dates for each genuinely overdue request

- **Age** = submission ("Received") date → today, in days.
- **Days past due** = live due date → today, in days.
- **Deadline** = 10 business days counted from tomorrow (skip weekends;
  count Mon–Fri only).

Compute rather than eyeball — for example:

```bash
python3 -c "
from datetime import date, timedelta
d = date.today()
n = 0
while n < 10:
    d += timedelta(days=1)
    if d.weekday() < 5: n += 1
print(d.strftime('%B %-d, %Y'))"
```

### 5. Compose the message

Use the template below, filling every bracketed field. For the
`[months/beyond]` phrase, state the overdue span naturally (e.g., "more
than four months beyond" or "well beyond").

Style rules — the tone is firm but professional, not bombastic:

- No "I hereby demand".
- No "(ten business days...)" parenthetical after the deadline date.
- No "Please treat this as a formal notice" line.
- No "Thank you" / "Sincerely" sign-off — the requester's name alone.

### 6. Confirm, then send

Before sending anything, present the user with the send list (request
numbers, day counts, draft text) and the skip list — unless the user's
invoking request already explicitly authorized sending without review.
Posting is public and cannot be recalled.

For each approved request:

1. **Re-verify the live Due date** on the request page immediately before
   sending — this is the check that would have prevented the prior
   erroneous send.
2. Click **"Message agency"**.
3. Type the composed message into the editor.
4. Click **"Send external message"**.
5. Confirm the **"Your message was sent"** banner appears before moving
   on; if it doesn't, treat the send as unconfirmed and report it.

### 7. Report

End with three sections:

- **Sent** — each request with a link, its age, and days past due.
- **Skipped** — each request with a link and the specific skip reason.
- **Errors** — anything that failed or couldn't be confirmed.

## Message Template

> Dear Records Custodian,
>
> I am writing regarding my public records request No. [NUMBER],
> submitted on [SUBMISSION DATE]. As of today, [TODAY], this request is
> [X] days old and is past its due date by [Y] days (the stated due date
> was [DUE DATE]).
>
> Under the Louisiana Public Records Law (La. R.S. 44:1 et seq.), a
> custodian must provide access to public records promptly, and no later
> than three business days after a request, or provide a written estimate
> of the time reasonably necessary to produce them. This request has now
> gone [months/beyond] its own estimated due date without production of
> the records.
>
> Please comply with your obligations under Louisiana law and fulfill
> this records request no later than [DEADLINE]. If any portion of the
> responsive records is withheld, please provide a written explanation
> citing the specific statutory exemption relied upon for each
> withholding.
>
> Failure to comply may result in my pursuit of the remedies available
> under La. R.S. 44:35, including a writ of mandamus, along with civil
> penalties, attorney's fees, and court costs.
>
> [REQUESTER NAME]

## Notes

- Requester in prior use: **Matthew Wollenweber**.
- Always cross-check the on-page Due date against the list value. The
  mismatch caused one erroneous send in a prior run (request **26-1642**,
  which had been extended to a future date while the list still showed it
  overdue). That is why steps 2 and 6.1 both re-read the live date.
