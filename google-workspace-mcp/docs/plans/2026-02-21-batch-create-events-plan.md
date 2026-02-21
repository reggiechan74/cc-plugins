# Batch Create Events Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `create_events_batch` tool to the calendar MCP server that creates multiple events across calendars in a single Google Batch API call.

**Architecture:** New `batchInsertEvents()` function mirrors existing `batchListEvents()` but constructs POST requests with JSON bodies. A new Zod schema wraps an array of the existing `CreateEventSchema`. The tool handler parses multipart responses into per-event success/error results.

**Tech Stack:** Node.js, Google Calendar Batch API, Zod, MCP SDK (all already in use)

---

### Task 1: Add the Zod schema

**Files:**
- Modify: `servers/calendar/index.js:504` (after `ListEventsMultiSchema`)

**Step 1: Add `CreateEventsBatchSchema` after `ListEventsMultiSchema` (line 504)**

Insert after the closing `});` of `ListEventsMultiSchema`:

```js
const CreateEventsBatchSchema = z.object({
  events: z
    .array(CreateEventSchema)
    .min(1)
    .max(50)
    .describe(
      "Array of events to create (max 50). Each event has: calendarId (optional, defaults to primary), summary (required), start (required), end (required), description (optional), location (optional)"
    ),
});
```

**Step 2: Verify no syntax errors**

Run: `node -c servers/calendar/index.js`
Expected: no output (clean parse)

**Step 3: Commit**

```bash
git add servers/calendar/index.js
git commit -m "feat(calendar): add CreateEventsBatchSchema for batch event creation"
```

---

### Task 2: Add the `batchInsertEvents()` function

**Files:**
- Modify: `servers/calendar/index.js:258` (after `batchListEvents()`)

**Step 1: Add `batchInsertEvents` function after `batchListEvents` (after line 258)**

Insert after the closing `}` of `batchListEvents`:

```js
async function batchInsertEvents(events) {
  const { token } = await oauth2Client.getAccessToken();
  if (!token) throw new Error("No access token for batch request");

  const boundary = `batch_insert_${Date.now()}`;

  // Build multipart request body with POST sub-requests
  let body = "";
  for (let i = 0; i < events.length; i++) {
    const evt = events[i];
    const { calendarId, ...eventData } = evt;
    const jsonBody = JSON.stringify(eventData);
    body += `--${boundary}\r\n`;
    body += `Content-Type: application/http\r\n`;
    body += `Content-ID: <evt${i}>\r\n\r\n`;
    body += `POST /calendar/v3/calendars/${encodeURIComponent(calendarId)}/events HTTP/1.1\r\n`;
    body += `Content-Type: application/json\r\n`;
    body += `Content-Length: ${Buffer.byteLength(jsonBody)}\r\n\r\n`;
    body += `${jsonBody}\r\n`;
  }
  body += `--${boundary}--`;

  const response = await fetch(
    "https://www.googleapis.com/batch/calendar/v3",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": `multipart/mixed; boundary=${boundary}`,
      },
      body,
    }
  );

  if (!response.ok) {
    throw new Error(`Batch API returned ${response.status}`);
  }

  const responseText = await response.text();
  const contentType = response.headers.get("content-type") || "";
  const respBoundary = contentType.match(/boundary=([^\s;]+)/)?.[1];

  if (!respBoundary) {
    throw new Error("No boundary in batch response");
  }

  const parts = responseText.split(`--${respBoundary}`).slice(1, -1);

  // Collect unique calendarIds that had successful inserts for cache invalidation
  const invalidatedCalendars = new Set();

  const results = parts.map((part, i) => {
    const calendarId = events[i].calendarId;
    try {
      // Extract HTTP status from the sub-response
      const statusMatch = part.match(/HTTP\/1\.1\s+(\d+)/);
      const httpStatus = statusMatch ? parseInt(statusMatch[1], 10) : 0;

      const jsonStart = part.indexOf("{");
      const jsonEnd = part.lastIndexOf("}");
      if (jsonStart === -1 || jsonEnd === -1) {
        return { index: i, calendarId, status: "error", error: "No JSON in response" };
      }
      const data = JSON.parse(part.slice(jsonStart, jsonEnd + 1));

      if (httpStatus >= 200 && httpStatus < 300) {
        invalidatedCalendars.add(calendarId);
        return {
          index: i,
          calendarId,
          status: "created",
          eventId: data.id,
          summary: events[i].summary,
        };
      } else {
        const errMsg = data.error?.message || `HTTP ${httpStatus}`;
        return { index: i, calendarId, status: "error", error: errMsg };
      }
    } catch (err) {
      return { index: i, calendarId, status: "error", error: err.message };
    }
  });

  // Invalidate cache for calendars that had successful inserts
  for (const calId of invalidatedCalendars) {
    invalidateCalendar(calId);
  }

  return results;
}
```

**Step 2: Verify no syntax errors**

Run: `node -c servers/calendar/index.js`
Expected: no output (clean parse)

**Step 3: Commit**

```bash
git add servers/calendar/index.js
git commit -m "feat(calendar): add batchInsertEvents() for batch event creation via Google Batch API"
```

---

### Task 3: Register the tool and add the handler

**Files:**
- Modify: `servers/calendar/index.js:606` (tool list, after `list_events_multi` entry)
- Modify: `servers/calendar/index.js:762` (switch statement, before `default:`)

**Step 1: Add tool registration after the `list_events_multi` entry (after line 606)**

Insert after the `list_events_multi` tool object's closing `},`:

```js
      {
        name: "create_events_batch",
        description:
          "Creates multiple events across one or more calendars in a single call using the Google Batch API. Much faster than calling create_event separately for each event. Returns per-event success/failure results.",
        inputSchema: zodToJsonSchema(CreateEventsBatchSchema),
      },
```

**Step 2: Add the switch case before `default:` (before the existing `default:` line)**

Insert before `default:`:

```js
        case "create_events_batch": {
          const validatedArgs = CreateEventsBatchSchema.parse(args);
          const resolvedEvents = validatedArgs.events.map((evt) => ({
            ...evt,
            calendarId: resolveCalendarId(evt.calendarId),
          }));
          const results = await batchInsertEvents(resolvedEvents);
          const created = results.filter((r) => r.status === "created").length;
          return {
            content: [
              {
                type: "text",
                text:
                  `Created ${created}/${results.length} events:\n` +
                  JSON.stringify(results),
              },
            ],
          };
        }
```

**Step 3: Verify no syntax errors**

Run: `node -c servers/calendar/index.js`
Expected: no output (clean parse)

**Step 4: Commit**

```bash
git add servers/calendar/index.js
git commit -m "feat(calendar): register create_events_batch tool with handler"
```

---

### Task 4: Bump version and verify startup

**Files:**
- Modify: `servers/calendar/index.js:552` (server version string)

**Step 1: Update the server version**

Change the version in `new Server(...)` from `"4.1.0"` to `"4.2.0"`.

**Step 2: Verify the server starts and lists the new tool**

Run: `cd servers/calendar && timeout 5 node index.js 2>&1 || true`

The server should start without errors (it will hang waiting for stdio transport — that's expected). Verify no crash on startup.

**Step 3: Commit**

```bash
git add servers/calendar/index.js
git commit -m "chore(calendar): bump version to 4.2.0 for batch create events"
```
