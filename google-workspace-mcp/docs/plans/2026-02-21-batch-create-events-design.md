# Design: `create_events_batch` tool

**Date**: 2026-02-21
**Server**: `google-workspace-mcp/servers/calendar`

## Purpose

Add a batch event creation endpoint to the calendar MCP server. Allows creating multiple events across one or more calendars in a single tool call using Google's Batch HTTP API.

## Schema

```js
const CreateEventsBatchSchema = z.object({
  events: z.array(CreateEventSchema)
    .min(1).max(50)
    .describe("Array of events to create (max 50, each with calendarId, summary, start, end, description?, location?)")
});
```

Each element reuses the existing `CreateEventSchema` shape. The 50-event cap matches Google's Batch API limit per request.

## Core function: `batchInsertEvents(events)`

Mirrors `batchListEvents()` (lines 189-258) but constructs POST requests with JSON bodies:

```
--boundary
Content-Type: application/http
Content-ID: <evt0>

POST /calendar/v3/calendars/{calendarId}/events HTTP/1.1
Content-Type: application/json

{"summary":"...","start":{...},"end":{...}}
--boundary--
```

Posts to `https://www.googleapis.com/batch/calendar/v3` with `multipart/mixed` content type.

### Response parsing

Same multipart split pattern as `batchListEvents()`. Each part is parsed to extract:
- **Success**: HTTP status in 2xx range, extract created event `id` and trimmed data
- **Failure**: Non-2xx status, extract error message from response JSON

### Return value

Array of per-event results:
```js
[
  { index: 0, calendarId: "primary", status: "created", eventId: "abc123", summary: "Team standup" },
  { index: 1, calendarId: "work", status: "error", error: "Calendar not found" },
]
```

## Cache invalidation

After the batch completes, `invalidateCalendar()` is called for each unique `calendarId` that had at least one successful insert.

## Tool registration

```js
{
  name: "create_events_batch",
  description: "Creates multiple events across one or more calendars in a single call using the Google Batch API. Much faster than calling create_event separately. Returns per-event success/failure results.",
  inputSchema: zodToJsonSchema(CreateEventsBatchSchema),
}
```

No `readOnlyHint` annotation (write operation).

## Response format

Summary line + full JSON:
```
Created 3/5 events:
[{"index":0,"calendarId":"primary","status":"created","eventId":"abc",...}, ...]
```

## Error handling

- Whole-batch failure (e.g., auth error, network): handled by existing `withRetry()` wrapper
- Per-event failures: captured in results array, never roll back successful inserts
- Batch API unavailable: not adding a fallback (unlike `list_events_multi`); write operations should fail explicitly rather than silently falling back

## Approach

Approach A (Batch HTTP API) was chosen over sequential `events.insert()` calls for:
- Single HTTP round-trip
- Consistency with existing `batchListEvents()` pattern
- Better rate-limit behavior
