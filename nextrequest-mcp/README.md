# nextrequest-mcp

MCP server for NextRequest public records portals (defaults to `nola.nextrequest.com`, the City of New Orleans portal). Talks directly to the portal's JSON API under `/client/` — no HTML scraping.

## Tools

| Tool | Auth | Description |
|---|---|---|
| `list_requests` | none | List/search requests: `search_term`, `open`, `closed`, `overdue`, `due_soon`, `pending`, `requester_ids`, `department_ids`, paging, sorting |
| `get_request` | none | Full detail for one request (text, state, due date, departments, POC, requester) |
| `get_request_timeline` | none | Message/event timeline for a request |
| `list_request_documents` | none | Documents attached to a request |
| `search_documents` | none | Full-text search released documents portal-wide |
| `send_message` | cookie + opt-in | Post a "Message agency" message on a request. Off by default. |

## Setup

```bash
npm install
npm run build
```

Register with Claude Code:

```bash
claude mcp add nextrequest -- node "$(pwd)/dist/index.js"
```

Or in `claude_desktop_config.json` / `.mcp.json`:

```json
{
  "mcpServers": {
    "nextrequest": {
      "command": "node",
      "args": ["/absolute/path/to/nextrequest-mcp/dist/index.js"],
      "env": {
        "NEXTREQUEST_BASE": "https://nola.nextrequest.com",
        "NEXTREQUEST_ALLOW_WRITES": "false"
      }
    }
  }
}
```

## Environment variables

- `NEXTREQUEST_BASE` — portal origin (default `https://nola.nextrequest.com`; any NextRequest portal works, e.g. another city's)
- `NEXTREQUEST_COOKIE` — your logged-in session cookie, required only for `send_message`. In your browser, DevTools → Application → Cookies on the portal, copy the `Cookie` request header value (the `_nextrequest_session=...` cookie is the important part). Treat it like a password; it expires when your session does.
- `NEXTREQUEST_ALLOW_WRITES` — must be the string `true` to enable `send_message`. Everything else is read-only.

## Write mechanics

`send_message` fetches a CSRF token from `GET /client/csrf_token` (session-bound), then POSTs JSON to `/client/notifications` with `note_type: "requester"` / `state: "requester"`, which is exactly what the portal's own "Message agency" button sends. Messages post publicly to the request timeline and cannot be deleted by the requester — the tool description warns the model accordingly.

## Notes

- Read endpoints are anonymous and public; be a good citizen (the server sends an identifying User-Agent).
- Automating authenticated writes against a hosted portal may be subject to NextRequest/CivicPlus terms of service — verify before enabling writes.
