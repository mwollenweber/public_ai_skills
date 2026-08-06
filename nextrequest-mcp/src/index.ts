#!/usr/bin/env node
/**
 * MCP server for NextRequest public records portals (nola.nextrequest.com by default).
 *
 * NextRequest is a Vue SPA backed by a JSON API under /client/. The read
 * endpoints are public (no auth). Sending a message to the agency requires a
 * logged-in session cookie (NEXTREQUEST_COOKIE) and is additionally gated
 * behind NEXTREQUEST_ALLOW_WRITES=true.
 *
 * Verified endpoints (2026-08, nola portal):
 *   GET  /client/requests?search_term=&open=true&overdue=true&requester_ids=&page_number=
 *   GET  /client/requests/:pretty_id
 *   GET  /client/requests/:pretty_id/timeline?page_number=
 *   GET  /client/request_documents?request_id=:pretty_id
 *   GET  /client/documents?search_term=&page_number=
 *   GET  /client/csrf_token
 *   POST /client/notifications   { note_text, note_type: "requester", state: "requester", request_id }
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const BASE = (process.env.NEXTREQUEST_BASE ?? "https://nola.nextrequest.com").replace(/\/+$/, "");
const COOKIE = process.env.NEXTREQUEST_COOKIE ?? "";
const ALLOW_WRITES = process.env.NEXTREQUEST_ALLOW_WRITES === "true";

const UA = "nextrequest-mcp/0.1 (personal automation; contact portal owner via portal)";

async function api(path: string, init: RequestInit = {}): Promise<any> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "User-Agent": UA,
      "Accept": "application/json",
      ...(COOKIE ? { "Cookie": COOKIE } : {}),
      ...(init.headers ?? {}),
    },
  });
  const text = await res.text();
  if (!res.ok) {
    throw new Error(`${init.method ?? "GET"} ${path} -> HTTP ${res.status}: ${text.slice(0, 300)}`);
  }
  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`${path} returned non-JSON (are you hitting the right portal?): ${text.slice(0, 200)}`);
  }
}

function json(data: unknown) {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

const stripHtml = (s: string | null | undefined) =>
  (s ?? "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();

const server = new McpServer({ name: "nextrequest", version: "0.1.0" });

server.tool(
  "list_requests",
  "List/search public records requests on the portal. All filters optional. Returns request id, state, dates, department, requester, and text.",
  {
    search_term: z.string().optional().describe("Full-text search over request text"),
    open: z.boolean().optional().describe("Only open requests"),
    closed: z.boolean().optional().describe("Only closed requests"),
    overdue: z.boolean().optional().describe("Only overdue requests"),
    due_soon: z.boolean().optional().describe("Only requests due soon"),
    pending: z.boolean().optional().describe("Only pending requests"),
    requester_ids: z.array(z.number()).optional().describe("Filter by requester user id(s)"),
    department_ids: z.array(z.number()).optional().describe("Filter by department id(s)"),
    page_number: z.number().int().min(1).optional().describe("Page of results (default 1)"),
    sort_field: z.string().optional().describe("Sort field, e.g. 'id' or 'request_date'"),
    sort_order: z.enum(["asc", "desc"]).optional(),
  },
  async (args) => {
    const p = new URLSearchParams();
    if (args.search_term) p.set("search_term", args.search_term);
    for (const flag of ["open", "closed", "overdue", "due_soon", "pending"] as const) {
      if (args[flag]) p.set(flag, "true");
    }
    for (const id of args.requester_ids ?? []) p.append("requester_ids[]", String(id));
    for (const id of args.department_ids ?? []) p.append("department_ids[]", String(id));
    p.set("page_number", String(args.page_number ?? 1));
    p.set("sort_field", args.sort_field ?? "id");
    p.set("sort_order", args.sort_order ?? "desc");
    const data = await api(`/client/requests?${p}`);
    return json(data);
  }
);

server.tool(
  "get_request",
  "Get full detail for one request by its number (e.g. '25-22468'): text, state, due date, departments, point of contact, requester.",
  { request_id: z.string().describe("Request number, e.g. 25-22468") },
  async ({ request_id }) => {
    const data = await api(`/client/requests/${encodeURIComponent(request_id)}`);
    if (typeof data.request_text === "string") data.request_text_plain = stripHtml(data.request_text);
    return json(data);
  }
);

server.tool(
  "get_request_timeline",
  "Get the message/event timeline for a request (messages from agency and requester, state changes, document releases). Paged; page 1 is most recent.",
  {
    request_id: z.string().describe("Request number, e.g. 25-22468"),
    page_number: z.number().int().min(1).optional(),
  },
  async ({ request_id, page_number }) => {
    const data = await api(
      `/client/requests/${encodeURIComponent(request_id)}/timeline?page_number=${page_number ?? 1}`
    );
    for (const ev of data.timeline ?? []) {
      ev.timeline_display_text_plain = stripHtml(ev.timeline_display_text);
    }
    return json(data);
  }
);

server.tool(
  "list_request_documents",
  "List documents attached to a request (title, visibility, file type, document path).",
  { request_id: z.string().describe("Request number, e.g. 25-22468") },
  async ({ request_id }) => {
    const data = await api(`/client/request_documents?request_id=${encodeURIComponent(request_id)}`);
    return json(data);
  }
);

server.tool(
  "search_documents",
  "Full-text search released documents across the whole portal by title/content.",
  {
    search_term: z.string(),
    page_number: z.number().int().min(1).optional(),
  },
  async ({ search_term, page_number }) => {
    const p = new URLSearchParams({ search_term, page_number: String(page_number ?? 1) });
    const data = await api(`/client/documents?${p}`);
    return json(data);
  }
);

server.tool(
  "send_message",
  "Send a message to the agency on a request ('Message agency'). WRITE ACTION — posts publicly to the request timeline and cannot be undone. Requires NEXTREQUEST_COOKIE (logged-in session) and NEXTREQUEST_ALLOW_WRITES=true. Plain text is wrapped in <p>; basic HTML allowed.",
  {
    request_id: z.string().describe("Request number, e.g. 25-22468"),
    body: z.string().describe("Message text (plain text or simple HTML)"),
  },
  async ({ request_id, body }) => {
    if (!ALLOW_WRITES) {
      throw new Error("Writes are disabled. Set NEXTREQUEST_ALLOW_WRITES=true in the server env to enable send_message.");
    }
    if (!COOKIE) {
      throw new Error("NEXTREQUEST_COOKIE is not set; a logged-in session cookie is required to send messages.");
    }
    const { csrf_token } = await api(`/client/csrf_token`);
    if (!csrf_token) throw new Error("Could not obtain CSRF token from /client/csrf_token.");

    const note_text = /<[a-z][\s\S]*>/i.test(body) ? body : `<p>${body.replace(/\n{2,}/g, "</p><p>").replace(/\n/g, "<br>")}</p>`;
    const data = await api(`/client/notifications`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token,
      },
      body: JSON.stringify({
        note_text,
        note_type: "requester",
        state: "requester",
        request_id,
        required: false,
        message_template_ids: [],
      }),
    });
    return json({ ok: true, request_id, response: data });
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
console.error(`nextrequest-mcp: connected (base=${BASE}, writes=${ALLOW_WRITES ? "ENABLED" : "disabled"}, cookie=${COOKIE ? "set" : "not set"})`);
