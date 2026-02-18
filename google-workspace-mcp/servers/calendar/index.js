#!/usr/bin/env node
/**
 * Enhanced Google Calendar MCP Server
 *
 * Based on @gongrzhe/server-calendar-autoauth-mcp v1.0.2
 * Enhancements:
 *   - list_calendars tool to discover all available calendars
 *   - Optional calendarId parameter on all tools (default: 'primary')
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

// Configuration paths — same as original for credential reuse
const CONFIG_DIR = path.join(os.homedir(), ".calendar-mcp");
const OAUTH_PATH =
  process.env.CALENDAR_OAUTH_PATH ||
  path.join(CONFIG_DIR, "gcp-oauth.keys.json");
const CREDENTIALS_PATH =
  process.env.CALENDAR_CREDENTIALS_PATH ||
  path.join(CONFIG_DIR, "credentials.json");

let oauth2Client;

async function loadCredentials() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  const localOAuthPath = path.join(process.cwd(), "gcp-oauth.keys.json");
  if (fs.existsSync(localOAuthPath)) {
    fs.copyFileSync(localOAuthPath, OAUTH_PATH);
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
  if (fs.existsSync(CREDENTIALS_PATH)) {
    const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf8"));
    oauth2Client.setCredentials(credentials);
  }
}

async function authenticate() {
  const server = http.createServer();
  server.listen(3000);
  return new Promise((resolve, reject) => {
    const authUrl = oauth2Client.generateAuthUrl({
      access_type: "offline",
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
// Schema definitions — enhanced with optional calendarId on all tools
// ---------------------------------------------------------------------------

const CalendarIdField = z
  .string()
  .optional()
  .default("primary")
  .describe(
    'Calendar ID to operate on. Use "primary" for the main calendar, or a specific calendar ID from list_calendars. Defaults to "primary".'
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

  const server = new Server({
    name: "google-calendar",
    version: "2.0.0",
    capabilities: { tools: {} },
  });

  // --- List tools -----------------------------------------------------------

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      {
        name: "list_calendars",
        description:
          "Lists all calendars the user has access to, including their IDs, names, and access roles. Use this to discover calendar IDs for other tools.",
        inputSchema: zodToJsonSchema(ListCalendarsSchema),
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
          "Lists events within a specified time range. Optionally specify calendarId to query a specific calendar.",
        inputSchema: zodToJsonSchema(ListEventsSchema),
      },
    ],
  }));

  // --- Call tool handler ----------------------------------------------------

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    try {
      switch (name) {
        // ---- NEW: list_calendars -------------------------------------------
        case "list_calendars": {
          const response = await calendarApi.calendarList.list();
          const calendars = (response.data.items || []).map((cal) => ({
            id: cal.id,
            summary: cal.summary,
            description: cal.description || "",
            primary: cal.primary || false,
            accessRole: cal.accessRole,
            backgroundColor: cal.backgroundColor,
          }));
          return {
            content: [
              {
                type: "text",
                text:
                  `Found ${calendars.length} calendars:\n` +
                  JSON.stringify(calendars, null, 2),
              },
            ],
          };
        }

        // ---- create_event (enhanced with calendarId) -----------------------
        case "create_event": {
          const validatedArgs = CreateEventSchema.parse(args);
          const { calendarId, ...eventData } = validatedArgs;
          const response = await calendarApi.events.insert({
            calendarId,
            requestBody: eventData,
          });
          return {
            content: [
              {
                type: "text",
                text:
                  `Event created with ID: ${response.data.id}\n` +
                  `Calendar: ${calendarId}\n` +
                  `Title: ${validatedArgs.summary}\n` +
                  `Start: ${validatedArgs.start.dateTime}\n` +
                  `End: ${validatedArgs.end.dateTime}`,
              },
            ],
          };
        }

        // ---- get_event (enhanced with calendarId) --------------------------
        case "get_event": {
          const validatedArgs = GetEventSchema.parse(args);
          const response = await calendarApi.events.get({
            calendarId: validatedArgs.calendarId,
            eventId: validatedArgs.eventId,
          });
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(response.data, null, 2),
              },
            ],
          };
        }

        // ---- update_event (enhanced with calendarId) -----------------------
        case "update_event": {
          const validatedArgs = UpdateEventSchema.parse(args);
          const { eventId, calendarId, ...updates } = validatedArgs;
          const response = await calendarApi.events.patch({
            calendarId,
            eventId,
            requestBody: updates,
          });
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

        // ---- delete_event (enhanced with calendarId) -----------------------
        case "delete_event": {
          const validatedArgs = DeleteEventSchema.parse(args);
          await calendarApi.events.delete({
            calendarId: validatedArgs.calendarId,
            eventId: validatedArgs.eventId,
          });
          return {
            content: [
              {
                type: "text",
                text: `Event deleted: ${validatedArgs.eventId} (calendar: ${validatedArgs.calendarId})`,
              },
            ],
          };
        }

        // ---- list_events (enhanced with calendarId) ------------------------
        case "list_events": {
          const validatedArgs = ListEventsSchema.parse(args);
          const response = await calendarApi.events.list({
            calendarId: validatedArgs.calendarId,
            timeMin: validatedArgs.timeMin,
            timeMax: validatedArgs.timeMax,
            maxResults: validatedArgs.maxResults || 10,
            orderBy: validatedArgs.orderBy || "startTime",
            singleEvents: true,
          });
          return {
            content: [
              {
                type: "text",
                text:
                  `Found ${response.data.items?.length || 0} events` +
                  ` (calendar: ${validatedArgs.calendarId}):\n` +
                  JSON.stringify(response.data.items, null, 2),
              },
            ],
          };
        }

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
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
  console.error("Enhanced Google Calendar MCP Server running on stdio");
}

main().catch(console.error);
