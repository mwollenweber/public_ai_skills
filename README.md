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
