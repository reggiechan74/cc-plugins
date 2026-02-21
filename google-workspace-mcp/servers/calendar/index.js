#!/usr/bin/env node
/**
 * Enhanced Google Calendar MCP Server v4.0.0
 *
 * Features:
 *   - list_calendars tool to discover all available calendars
 *   - Optional calendarId parameter on all tools (default: 'primary')
 *   - list_events_multi: batched multi-calendar queries via Google Batch API
 *   - Trimmed responses: only essential fields (summary, start, end, etc.)
 *   - Google API fields parameter: reduce network transfer
 *   - In-memory cache with 3-minute TTL + syncToken-based revalidation
 *   - Calendar shortname resolver (user-configurable)
 *   - Compact JSON responses (no pretty-printing)
 *   - Cache invalidation on write operations
 *
 * OAuth credentials reuse the same ~/.calendar-mcp/ directory as the original.
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import { OAuth2Client } from "google-auth-library";
import fs from "fs";
import path from "path";
import http from "http";
import open from "open";
import os from "os";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const CONFIG_DIR = path.join(os.homedir(), ".calendar-mcp");
const OAUTH_PATH =
  process.env.CALENDAR_OAUTH_PATH ||
  path.join(CONFIG_DIR, "gcp-oauth.keys.json");
const CREDENTIALS_PATH =
  process.env.CALENDAR_CREDENTIALS_PATH ||
  path.join(CONFIG_DIR, "credentials.json");

let oauth2Client;

// ---------------------------------------------------------------------------
// Calendar shortname resolver
// ---------------------------------------------------------------------------

// Customize these mappings with your own calendar shortnames.
// Run list_calendars to discover your calendar IDs, then add entries below.
// Example:
//   work: "user@company.com",
//   personal: "user@gmail.com",
//   team: "abc123@group.calendar.google.com",
const CALENDAR_SHORTNAMES = {};

function resolveCalendarId(id) {
  if (!id) return "primary";
  const lower = id.toLowerCase();
  return CALENDAR_SHORTNAMES[lower] || id;
}

// ---------------------------------------------------------------------------
// Response trimming
// ---------------------------------------------------------------------------

const EVENT_FIELDS =
  "items(id,summary,start,end,location,description,status," +
  "attendees(email,displayName,responseStatus,self)),nextSyncToken";

function trimEvent(event) {
  const trimmed = {
    id: event.id,
    summary: event.summary,
    start: event.start,
    end: event.end,
  };
  if (event.location) trimmed.location = event.location;
  if (event.description) trimmed.description = event.description;
  if (event.attendees?.length) {
    trimmed.attendees = event.attendees.map((a) => {
      const att = { displayName: a.displayName || a.email };
      if (a.responseStatus && a.responseStatus !== "needsAction")
        att.responseStatus = a.responseStatus;
      if (a.self) att.self = true;
      return att;
    });
  }
  return trimmed;
}

// ---------------------------------------------------------------------------
// In-memory cache with TTL + syncToken revalidation
// ---------------------------------------------------------------------------

const CACHE_TTL = 3 * 60 * 1000; // 3 minutes
const MAX_CACHE_ENTRIES = 50;
const eventCache = new Map(); // cacheKey -> { events, timestamp, syncToken }

function makeCacheKey(calendarId, timeMin, timeMax) {
  return `${calendarId}|${timeMin}|${timeMax}`;
}

function getCached(key) {
  const entry = eventCache.get(key);
  if (entry && Date.now() - entry.timestamp < CACHE_TTL) {
    return entry;
  }
  return null;
}

function setCache(key, events, syncToken) {
  // Evict oldest entries if cache is full
  if (eventCache.size >= MAX_CACHE_ENTRIES) {
    const oldest = eventCache.keys().next().value;
    eventCache.delete(oldest);
  }
  eventCache.set(key, { events, timestamp: Date.now(), syncToken });
}

function invalidateCalendar(calendarId) {
  for (const key of eventCache.keys()) {
    if (key.startsWith(calendarId + "|")) {
      eventCache.delete(key);
    }
  }
}

// Fetch events with cache + syncToken optimization
async function fetchEventsWithCache(
  calendarApi,
  calendarId,
  timeMin,
  timeMax,
  maxResults
) {
  const key = makeCacheKey(calendarId, timeMin, timeMax);

  // Fresh cache hit — return immediately
  const cached = getCached(key);
  if (cached) return cached.events;

  // Expired cache with syncToken — quick revalidation
  const expired = eventCache.get(key);
  if (expired?.syncToken) {
    try {
      const syncResp = await calendarApi.events.list({
        calendarId,
        syncToken: expired.syncToken,
      });
      if (!syncResp.data.items?.length) {
        // No changes — refresh cache with existing data
        setCache(
          key,
          expired.events,
          syncResp.data.nextSyncToken || expired.syncToken
        );
        return expired.events;
      }
      // Changes detected — fall through to full fetch
    } catch {
      // syncToken invalid (410 Gone) — fall through to full fetch
    }
  }

  // Full fetch
  const response = await calendarApi.events.list({
    calendarId,
    timeMin,
    timeMax,
    maxResults: maxResults || 10,
    orderBy: "startTime",
    singleEvents: true,
    fields: EVENT_FIELDS,
  });

  const events = (response.data.items || []).map(trimEvent);
  setCache(key, events, response.data.nextSyncToken);
  return events;
}

// ---------------------------------------------------------------------------
// Google Batch API for multi-calendar queries
// ---------------------------------------------------------------------------

async function batchListEvents(requests) {
  const { token } = await oauth2Client.getAccessToken();
  if (!token) throw new Error("No access token for batch request");

  const boundary = `batch_cal_${Date.now()}`;

  // Build multipart request body
  let body = "";
  for (let i = 0; i < requests.length; i++) {
    const req = requests[i];
    const params = new URLSearchParams({
      timeMin: req.timeMin,
      timeMax: req.timeMax,
      maxResults: String(req.maxResults || 10),
      orderBy: "startTime",
      singleEvents: "true",
      fields: EVENT_FIELDS,
    });
    body += `--${boundary}\r\n`;
    body += `Content-Type: application/http\r\n`;
    body += `Content-ID: <cal${i}>\r\n\r\n`;
    body += `GET /calendar/v3/calendars/${encodeURIComponent(req.calendarId)}/events?${params}\r\n\r\n`;
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

  return parts.map((part, i) => {
    const calId = requests[i].calendarId;
    try {
      const jsonStart = part.indexOf("{");
      const jsonEnd = part.lastIndexOf("}");
      if (jsonStart === -1 || jsonEnd === -1) {
        return { calendar: calId, events: [] };
      }
      const data = JSON.parse(part.slice(jsonStart, jsonEnd + 1));
      const events = (data.items || []).map(trimEvent);
      // Cache each calendar result individually
      const key = makeCacheKey(calId, requests[i].timeMin, requests[i].timeMax);
      setCache(key, events, data.nextSyncToken);
      return { calendar: calId, events };
    } catch (err) {
      return { calendar: calId, events: [], error: err.message };
    }
  });
}

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

  if (parts.length !== events.length) {
    console.error(`Batch response had ${parts.length} parts for ${events.length} requests`);
  }

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

// Fetch multiple calendars: cache first, then batch uncached, fallback to Promise.all
async function fetchMultiWithCache(calendarApi, calendarIds, timeMin, timeMax, maxResults) {
  const cached = new Map();
  const uncachedIds = [];

  for (const calId of calendarIds) {
    const key = makeCacheKey(calId, timeMin, timeMax);
    const hit = getCached(key);
    if (hit) {
      cached.set(calId, hit.events);
    } else {
      uncachedIds.push(calId);
    }
  }

  let fetched = new Map();

  if (uncachedIds.length > 0) {
    // Try batch API first, fallback to Promise.all
    try {
      if (typeof globalThis.fetch === "function") {
        const batchResults = await batchListEvents(
          uncachedIds.map((calId) => ({ calendarId: calId, timeMin, timeMax, maxResults }))
        );
        for (const r of batchResults) {
          fetched.set(r.calendar, r);
        }
      } else {
        throw new Error("fetch not available");
      }
    } catch {
      // Fallback: parallel individual fetches with cache/syncToken
      const fallbackResults = await Promise.all(
        uncachedIds.map(async (calId) => {
          try {
            const events = await fetchEventsWithCache(
              calendarApi, calId, timeMin, timeMax, maxResults
            );
            return { calendar: calId, events };
          } catch (err) {
            return { calendar: calId, events: [], error: err.message };
          }
        })
      );
      for (const r of fallbackResults) {
        fetched.set(r.calendar, r);
      }
    }
  }

  // Assemble results in original calendar order
  return calendarIds.map((calId) => {
    if (cached.has(calId)) {
      return { calendar: calId, events: cached.get(calId) };
    }
    return fetched.get(calId) || { calendar: calId, events: [] };
  });
}

// ---------------------------------------------------------------------------
// OAuth setup
// ---------------------------------------------------------------------------

async function loadCredentials() {
  try {
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
    if (!fs.existsSync(OAUTH_PATH)) {
      console.error(
        "Error: OAuth keys file not found. Place gcp-oauth.keys.json in",
        CONFIG_DIR
      );
      process.exit(1);
    }
    const keysContent = JSON.parse(fs.readFileSync(OAUTH_PATH, "utf8"));
    const keys = keysContent.installed || keysContent.web;
    if (!keys) {
      console.error("Error: Invalid OAuth keys file format.");
      process.exit(1);
    }
    oauth2Client = new OAuth2Client(
      keys.client_id,
      keys.client_secret,
      "http://localhost:3000/oauth2callback"
    );
    // Auto-persist refreshed tokens to disk
    oauth2Client.on("tokens", (tokens) => {
      try {
        const existing = fs.existsSync(CREDENTIALS_PATH)
          ? JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf8"))
          : {};
        fs.writeFileSync(
          CREDENTIALS_PATH,
          JSON.stringify({ ...existing, ...tokens })
        );
        console.error("OAuth tokens refreshed and saved.");
      } catch (err) {
        console.error("Failed to save refreshed tokens:", err.message);
      }
    });

    if (fs.existsSync(CREDENTIALS_PATH)) {
      const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf8"));
      oauth2Client.setCredentials(credentials);
    }
  } catch (error) {
    console.error("Error loading credentials:", error);
    process.exit(1);
  }
}

async function authenticate() {
  const server = http.createServer();
  await new Promise((resolve, reject) => {
    server.on("error", (err) => {
      if (err.code === "EADDRINUSE") {
        reject(new Error("Port 3000 is already in use. Close the other process and try again."));
      } else {
        reject(err);
      }
    });
    server.listen(3000, resolve);
  });
  return new Promise((resolve, reject) => {
    const authUrl = oauth2Client.generateAuthUrl({
      access_type: "offline",
      prompt: "consent",
      scope: ["https://www.googleapis.com/auth/calendar"],
    });
    console.log("Please visit this URL to authenticate:", authUrl);
    open(authUrl);
    server.on("request", async (req, res) => {
      if (!req.url?.startsWith("/oauth2callback")) return;
      const url = new URL(req.url, "http://localhost:3000");
      const code = url.searchParams.get("code");
      if (!code) {
        res.writeHead(400);
        res.end("No code provided");
        reject(new Error("No code provided"));
        return;
      }
      try {
        const { tokens } = await oauth2Client.getToken(code);
        oauth2Client.setCredentials(tokens);
        fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify(tokens));
        res.writeHead(200);
        res.end("Authentication successful! You can close this window.");
        server.close();
        resolve();
      } catch (error) {
        res.writeHead(500);
        res.end("Authentication failed");
        reject(error);
      }
    });
  });
}

// ---------------------------------------------------------------------------
// Schema definitions
// ---------------------------------------------------------------------------

const CalendarIdField = z
  .string()
  .optional()
  .default("primary")
  .describe(
    'Calendar ID or shortname (if configured in CALENDAR_SHORTNAMES). Use "primary" for the main calendar. Defaults to "primary".'
  );

const ListCalendarsSchema = z.object({});

const CreateEventSchema = z.object({
  calendarId: CalendarIdField,
  summary: z.string().describe("Event title"),
  start: z.object({
    dateTime: z.string().describe("Start time (ISO format)"),
    timeZone: z.string().optional().describe("Time zone"),
  }),
  end: z.object({
    dateTime: z.string().describe("End time (ISO format)"),
    timeZone: z.string().optional().describe("Time zone"),
  }),
  description: z.string().optional().describe("Event description"),
  location: z.string().optional().describe("Event location"),
});

const GetEventSchema = z.object({
  calendarId: CalendarIdField,
  eventId: z.string().describe("ID of the event to retrieve"),
});

const UpdateEventSchema = z.object({
  calendarId: CalendarIdField,
  eventId: z.string().describe("ID of the event to update"),
  summary: z.string().optional().describe("New event title"),
  start: z
    .object({
      dateTime: z.string().describe("New start time (ISO format)"),
      timeZone: z.string().optional().describe("Time zone"),
    })
    .optional(),
  end: z
    .object({
      dateTime: z.string().describe("New end time (ISO format)"),
      timeZone: z.string().optional().describe("Time zone"),
    })
    .optional(),
  description: z.string().optional().describe("New event description"),
  location: z.string().optional().describe("New event location"),
});

const DeleteEventSchema = z.object({
  calendarId: CalendarIdField,
  eventId: z.string().describe("ID of the event to delete"),
});

const ListEventsSchema = z.object({
  calendarId: CalendarIdField,
  timeMin: z.string().describe("Start of time range (ISO format)"),
  timeMax: z.string().describe("End of time range (ISO format)"),
  maxResults: z
    .number()
    .optional()
    .describe("Maximum number of events to return"),
  orderBy: z
    .enum(["startTime", "updated"])
    .optional()
    .describe("Sort order"),
});

const ListEventsMultiSchema = z.object({
  calendarIds: z
    .array(z.string())
    .describe(
      "Array of calendar IDs or shortnames (if configured in CALENDAR_SHORTNAMES) to query in parallel"
    ),
  timeMin: z.string().describe("Start of time range (ISO format)"),
  timeMax: z.string().describe("End of time range (ISO format)"),
  maxResults: z
    .number()
    .optional()
    .describe("Maximum number of events per calendar (default 10)"),
});

const CreateEventsBatchSchema = z.object({
  events: z
    .array(CreateEventSchema)
    .min(1)
    .max(50)
    .describe(
      "Array of events to create (max 50). Each event has: calendarId (optional, defaults to primary), summary (required), start (required), end (required), description (optional), location (optional)"
    ),
});

// ---------------------------------------------------------------------------
// Retry wrapper with exponential backoff
// ---------------------------------------------------------------------------
async function withRetry(fn, maxRetries = 2) {
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === maxRetries) throw err;
      const isAuthError =
        err.code === 401 || err.message?.includes("invalid_grant");
      const isTransient = err.code === 429 || (err.code >= 500 && err.code < 600);
      if (!isAuthError && !isTransient) throw err;
      if (isAuthError && oauth2Client) {
        try {
          const { credentials } = await oauth2Client.refreshAccessToken();
          oauth2Client.setCredentials(credentials);
          console.error("Token refreshed via retry wrapper.");
        } catch (_refreshErr) {
          throw err;
        }
      }
      const delay = 1000 * Math.pow(2, i);
      console.error(
        `Retrying after ${delay}ms (attempt ${i + 1}/${maxRetries})...`
      );
      await new Promise((r) => setTimeout(r, delay));
    }
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  await loadCredentials();

  if (process.argv[2] === "auth") {
    await authenticate();
    console.log("Authentication completed successfully");
    process.exit(0);
  }

  const calendarApi = google.calendar({ version: "v3", auth: oauth2Client });

  const server = new Server(
    { name: "google-calendar", version: "4.1.0" },
    { capabilities: { tools: {} } }
  );

  // --- List tools -----------------------------------------------------------

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: "list_calendars",
        description:
          "Lists all calendars the user has access to, including their IDs, names, and access roles. Use this to discover calendar IDs for other tools.",
        inputSchema: zodToJsonSchema(ListCalendarsSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "create_event",
        description:
          "Creates a new event in Google Calendar. Optionally specify calendarId to target a specific calendar.",
        inputSchema: zodToJsonSchema(CreateEventSchema),
      },
      {
        name: "get_event",
        description:
          "Retrieves details of a specific event. Optionally specify calendarId.",
        inputSchema: zodToJsonSchema(GetEventSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "update_event",
        description:
          "Updates an existing event. Optionally specify calendarId.",
        inputSchema: zodToJsonSchema(UpdateEventSchema),
      },
      {
        name: "delete_event",
        description:
          "Deletes an event from the calendar. Optionally specify calendarId.",
        inputSchema: zodToJsonSchema(DeleteEventSchema),
      },
      {
        name: "list_events",
        description:
          "Lists events within a specified time range for a single calendar. Returns trimmed fields only.",
        inputSchema: zodToJsonSchema(ListEventsSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "list_events_multi",
        description:
          "Lists events from multiple calendars in parallel in a single call. Much faster than calling list_events separately for each calendar. Returns trimmed fields grouped by calendar.",
        inputSchema: zodToJsonSchema(ListEventsMultiSchema),
        annotations: { readOnlyHint: true },
      },
    ],
  }));

  // --- Call tool handler ----------------------------------------------------

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    try {
      return await withRetry(async () => {
      switch (name) {
        case "list_calendars": {
          const response = await calendarApi.calendarList.list();
          const calendars = (response.data.items || []).map((cal) => ({
            id: cal.id,
            summary: cal.summary,
            description: cal.description || "",
            primary: cal.primary || false,
            accessRole: cal.accessRole,
          }));
          return {
            content: [
              {
                type: "text",
                text: `Found ${calendars.length} calendars:\n${JSON.stringify(calendars)}`,
              },
            ],
          };
        }

        case "create_event": {
          const validatedArgs = CreateEventSchema.parse(args);
          const calendarId = resolveCalendarId(validatedArgs.calendarId);
          const { calendarId: _, ...eventData } = validatedArgs;
          const response = await calendarApi.events.insert({
            calendarId,
            requestBody: eventData,
          });
          invalidateCalendar(calendarId);
          return {
            content: [
              {
                type: "text",
                text:
                  `Event created: ${response.data.id}\n` +
                  `Calendar: ${calendarId}\n` +
                  `Title: ${validatedArgs.summary}\n` +
                  `Start: ${validatedArgs.start.dateTime}\n` +
                  `End: ${validatedArgs.end.dateTime}`,
              },
            ],
          };
        }

        case "get_event": {
          const validatedArgs = GetEventSchema.parse(args);
          const calendarId = resolveCalendarId(validatedArgs.calendarId);
          const response = await calendarApi.events.get({
            calendarId,
            eventId: validatedArgs.eventId,
          });
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(trimEvent(response.data)),
              },
            ],
          };
        }

        case "update_event": {
          const validatedArgs = UpdateEventSchema.parse(args);
          const calendarId = resolveCalendarId(validatedArgs.calendarId);
          const { eventId, calendarId: _, ...updates } = validatedArgs;
          await calendarApi.events.patch({
            calendarId,
            eventId,
            requestBody: updates,
          });
          invalidateCalendar(calendarId);
          return {
            content: [
              {
                type: "text",
                text:
                  `Event updated: ${eventId}\n` +
                  `Calendar: ${calendarId}\n` +
                  `New title: ${updates.summary || "(unchanged)"}\n` +
                  `New start: ${updates.start?.dateTime || "(unchanged)"}\n` +
                  `New end: ${updates.end?.dateTime || "(unchanged)"}`,
              },
            ],
          };
        }

        case "delete_event": {
          const validatedArgs = DeleteEventSchema.parse(args);
          const calendarId = resolveCalendarId(validatedArgs.calendarId);
          await calendarApi.events.delete({
            calendarId,
            eventId: validatedArgs.eventId,
          });
          invalidateCalendar(calendarId);
          return {
            content: [
              {
                type: "text",
                text: `Event deleted: ${validatedArgs.eventId} (calendar: ${calendarId})`,
              },
            ],
          };
        }

        case "list_events": {
          const validatedArgs = ListEventsSchema.parse(args);
          const calendarId = resolveCalendarId(validatedArgs.calendarId);
          const events = await fetchEventsWithCache(
            calendarApi,
            calendarId,
            validatedArgs.timeMin,
            validatedArgs.timeMax,
            validatedArgs.maxResults
          );
          return {
            content: [
              {
                type: "text",
                text: `Found ${events.length} events (calendar: ${calendarId}):\n${JSON.stringify(events)}`,
              },
            ],
          };
        }

        case "list_events_multi": {
          const validatedArgs = ListEventsMultiSchema.parse(args);
          const resolvedIds = validatedArgs.calendarIds.map(resolveCalendarId);
          const results = await fetchMultiWithCache(
            calendarApi,
            resolvedIds,
            validatedArgs.timeMin,
            validatedArgs.timeMax,
            validatedArgs.maxResults
          );
          const totalEvents = results.reduce(
            (sum, r) => sum + r.events.length,
            0
          );
          return {
            content: [
              {
                type: "text",
                text: `Found ${totalEvents} events across ${results.length} calendars:\n${JSON.stringify(results)}`,
              },
            ],
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
      }); // end withRetry
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  });

  const transport = new StdioServerTransport();
  server.connect(transport).catch((error) => {
    console.error("Fatal error running server:", error);
    process.exit(1);
  });
  console.error("Enhanced Google Calendar MCP Server v4.1.0 running on stdio");
}

main().catch(console.error);
