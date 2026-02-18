#!/usr/bin/env node
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

// Import helper modules
import {
  createEmailMessage,
  createEmailWithNodemailer,
  extractEmailContent,
} from "./email-utils.js";
import {
  createLabel,
  updateLabel,
  deleteLabel,
  listLabels,
  getOrCreateLabel,
} from "./label-manager.js";
import {
  createFilter,
  listFilters,
  getFilter,
  deleteFilter,
  filterTemplates,
} from "./filter-manager.js";
import { listThreads, getThread } from "./thread-manager.js";
import { lookupContact } from "./contact-lookup.js";

// ---------------------------------------------------------------------------
// Configuration paths
// ---------------------------------------------------------------------------
const CONFIG_DIR = path.join(os.homedir(), ".gmail-mcp");
const CALENDAR_CONFIG_DIR = path.join(os.homedir(), ".calendar-mcp");
const CREDENTIALS_PATH =
  process.env.GMAIL_CREDENTIALS_PATH ||
  path.join(CONFIG_DIR, "credentials.json");

function resolveOAuthPath() {
  if (process.env.GMAIL_OAUTH_PATH) return process.env.GMAIL_OAUTH_PATH;
  const gmailOAuth = path.join(CONFIG_DIR, "gcp-oauth.keys.json");
  if (fs.existsSync(gmailOAuth)) return gmailOAuth;
  const calendarOAuth = path.join(CALENDAR_CONFIG_DIR, "gcp-oauth.keys.json");
  if (fs.existsSync(calendarOAuth)) return calendarOAuth;
  return gmailOAuth; // Default — used in error messages
}

// ---------------------------------------------------------------------------
// OAuth2 configuration
// ---------------------------------------------------------------------------
let oauth2Client;

async function loadCredentials() {
  try {
    // Create config directory if it doesn't exist
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }

    // Check for OAuth keys in current directory first, copy to config dir
    const localOAuthPath = path.join(process.cwd(), "gcp-oauth.keys.json");
    const oauthPath = resolveOAuthPath();

    if (fs.existsSync(localOAuthPath)) {
      const targetPath = path.join(CONFIG_DIR, "gcp-oauth.keys.json");
      fs.copyFileSync(localOAuthPath, targetPath);
      console.error(
        "OAuth keys found in current directory, copied to global config."
      );
    }

    if (!fs.existsSync(oauthPath)) {
      console.error(
        "Error: OAuth keys file not found. Please place gcp-oauth.keys.json in",
        CONFIG_DIR,
        "or",
        CALENDAR_CONFIG_DIR
      );
      process.exit(1);
    }

    const keysContent = JSON.parse(fs.readFileSync(oauthPath, "utf8"));
    const keys = keysContent.installed || keysContent.web;

    if (!keys) {
      console.error(
        'Error: Invalid OAuth keys file format. File should contain either "installed" or "web" credentials.'
      );
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
  server.listen(3000);

  return new Promise((resolve, reject) => {
    const authUrl = oauth2Client.generateAuthUrl({
      access_type: "offline",
      scope: [
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.settings.basic",
        "https://www.googleapis.com/auth/contacts.readonly",
      ],
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
// Zod schema definitions (22 tools)
// ---------------------------------------------------------------------------

// Core email schemas
const SendEmailSchema = z.object({
  to: z.array(z.string()).describe("List of recipient email addresses"),
  subject: z.string().describe("Email subject"),
  body: z
    .string()
    .describe(
      "Email body content (used for text/plain or when htmlBody not provided)"
    ),
  htmlBody: z
    .string()
    .optional()
    .describe("HTML version of the email body"),
  mimeType: z
    .enum(["text/plain", "text/html", "multipart/alternative"])
    .optional()
    .default("text/plain")
    .describe("Email content type"),
  cc: z.array(z.string()).optional().describe("List of CC recipients"),
  bcc: z.array(z.string()).optional().describe("List of BCC recipients"),
  threadId: z.string().optional().describe("Thread ID to reply to"),
  inReplyTo: z.string().optional().describe("Message ID being replied to"),
  attachments: z
    .array(z.string())
    .optional()
    .describe("List of file paths to attach to the email"),
});

const ReadEmailSchema = z.object({
  messageId: z.string().describe("ID of the email message to retrieve"),
});

const SearchEmailsSchema = z.object({
  query: z
    .string()
    .describe("Gmail search query (e.g., 'from:example@gmail.com')"),
  maxResults: z
    .number()
    .optional()
    .describe("Maximum number of results to return"),
});

const ModifyEmailSchema = z.object({
  messageId: z.string().describe("ID of the email message to modify"),
  labelIds: z
    .array(z.string())
    .optional()
    .describe("List of label IDs to apply"),
  addLabelIds: z
    .array(z.string())
    .optional()
    .describe("List of label IDs to add to the message"),
  removeLabelIds: z
    .array(z.string())
    .optional()
    .describe("List of label IDs to remove from the message"),
});

const DeleteEmailSchema = z.object({
  messageId: z.string().describe("ID of the email message to delete"),
});

const ListEmailLabelsSchema = z
  .object({})
  .describe("Retrieves all available Gmail labels");

// Batch schemas
const BatchModifyEmailsSchema = z.object({
  messageIds: z.array(z.string()).describe("List of message IDs to modify"),
  addLabelIds: z
    .array(z.string())
    .optional()
    .describe("List of label IDs to add to all messages"),
  removeLabelIds: z
    .array(z.string())
    .optional()
    .describe("List of label IDs to remove from all messages"),
  batchSize: z
    .number()
    .optional()
    .default(50)
    .describe("Number of messages to process in each batch (default: 50)"),
});

const BatchDeleteEmailsSchema = z.object({
  messageIds: z.array(z.string()).describe("List of message IDs to delete"),
  batchSize: z
    .number()
    .optional()
    .default(50)
    .describe(
      "Number of messages to process in each batch (default: 50)"
    ),
});

// Label schemas
const CreateLabelSchema = z
  .object({
    name: z.string().describe("Name for the new label"),
    messageListVisibility: z
      .enum(["show", "hide"])
      .optional()
      .describe("Whether to show or hide the label in the message list"),
    labelListVisibility: z
      .enum(["labelShow", "labelShowIfUnread", "labelHide"])
      .optional()
      .describe("Visibility of the label in the label list"),
  })
  .describe("Creates a new Gmail label");

const UpdateLabelSchema = z
  .object({
    id: z.string().describe("ID of the label to update"),
    name: z.string().optional().describe("New name for the label"),
    messageListVisibility: z
      .enum(["show", "hide"])
      .optional()
      .describe("Whether to show or hide the label in the message list"),
    labelListVisibility: z
      .enum(["labelShow", "labelShowIfUnread", "labelHide"])
      .optional()
      .describe("Visibility of the label in the label list"),
  })
  .describe("Updates an existing Gmail label");

const DeleteLabelSchema = z
  .object({
    id: z.string().describe("ID of the label to delete"),
  })
  .describe("Deletes a Gmail label");

const GetOrCreateLabelSchema = z
  .object({
    name: z.string().describe("Name of the label to get or create"),
    messageListVisibility: z
      .enum(["show", "hide"])
      .optional()
      .describe("Whether to show or hide the label in the message list"),
    labelListVisibility: z
      .enum(["labelShow", "labelShowIfUnread", "labelHide"])
      .optional()
      .describe("Visibility of the label in the label list"),
  })
  .describe("Gets an existing label by name or creates it if it doesn't exist");

// Filter schemas
const CreateFilterSchema = z
  .object({
    criteria: z
      .object({
        from: z
          .string()
          .optional()
          .describe("Sender email address to match"),
        to: z
          .string()
          .optional()
          .describe("Recipient email address to match"),
        subject: z.string().optional().describe("Subject text to match"),
        query: z
          .string()
          .optional()
          .describe("Gmail search query (e.g., 'has:attachment')"),
        negatedQuery: z
          .string()
          .optional()
          .describe("Text that must NOT be present"),
        hasAttachment: z
          .boolean()
          .optional()
          .describe("Whether to match emails with attachments"),
        excludeChats: z
          .boolean()
          .optional()
          .describe("Whether to exclude chat messages"),
        size: z.number().optional().describe("Email size in bytes"),
        sizeComparison: z
          .enum(["unspecified", "smaller", "larger"])
          .optional()
          .describe("Size comparison operator"),
      })
      .describe("Criteria for matching emails"),
    action: z
      .object({
        addLabelIds: z
          .array(z.string())
          .optional()
          .describe("Label IDs to add to matching emails"),
        removeLabelIds: z
          .array(z.string())
          .optional()
          .describe("Label IDs to remove from matching emails"),
        forward: z
          .string()
          .optional()
          .describe("Email address to forward matching emails to"),
      })
      .describe("Actions to perform on matching emails"),
  })
  .describe("Creates a new Gmail filter");

const ListFiltersSchema = z
  .object({})
  .describe("Retrieves all Gmail filters");

const GetFilterSchema = z
  .object({
    filterId: z.string().describe("ID of the filter to retrieve"),
  })
  .describe("Gets details of a specific Gmail filter");

const DeleteFilterSchema = z
  .object({
    filterId: z.string().describe("ID of the filter to delete"),
  })
  .describe("Deletes a Gmail filter");

const CreateFilterFromTemplateSchema = z
  .object({
    template: z
      .enum([
        "fromSender",
        "withSubject",
        "withAttachments",
        "largeEmails",
        "containingText",
        "mailingList",
      ])
      .describe("Pre-defined filter template to use"),
    parameters: z
      .object({
        senderEmail: z
          .string()
          .optional()
          .describe("Sender email (for fromSender template)"),
        subjectText: z
          .string()
          .optional()
          .describe("Subject text (for withSubject template)"),
        searchText: z
          .string()
          .optional()
          .describe("Text to search for (for containingText template)"),
        listIdentifier: z
          .string()
          .optional()
          .describe("Mailing list identifier (for mailingList template)"),
        sizeInBytes: z
          .number()
          .optional()
          .describe("Size threshold in bytes (for largeEmails template)"),
        labelIds: z
          .array(z.string())
          .optional()
          .describe("Label IDs to apply"),
        archive: z
          .boolean()
          .optional()
          .describe("Whether to archive (skip inbox)"),
        markAsRead: z
          .boolean()
          .optional()
          .describe("Whether to mark as read"),
        markImportant: z
          .boolean()
          .optional()
          .describe("Whether to mark as important"),
      })
      .describe("Template-specific parameters"),
  })
  .describe("Creates a filter using a pre-defined template");

// Attachment schema
const DownloadAttachmentSchema = z.object({
  messageId: z
    .string()
    .describe("ID of the email message containing the attachment"),
  attachmentId: z.string().describe("ID of the attachment to download"),
  filename: z
    .string()
    .optional()
    .describe(
      "Filename to save the attachment as (if not provided, uses original filename)"
    ),
  savePath: z
    .string()
    .optional()
    .describe(
      "Directory path to save the attachment (defaults to current directory)"
    ),
});

// NEW enhancement schemas
const ListThreadsSchema = z.object({
  query: z
    .string()
    .describe("Gmail search query to find threads"),
  maxResults: z
    .number()
    .optional()
    .describe("Maximum number of threads to return"),
});

const GetThreadSchema = z.object({
  threadId: z.string().describe("ID of the thread to retrieve"),
  format: z
    .enum(["full", "metadata", "minimal"])
    .optional()
    .default("full")
    .describe("Response format (default: full)"),
});

const LookupContactSchema = z.object({
  email: z.string().describe("Email address to look up in Google Contacts"),
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

  // Support `node index.js auth` for interactive OAuth flow
  if (process.argv[2] === "auth") {
    await authenticate();
    console.log("Authentication completed successfully");
    process.exit(0);
  }

  // Initialize Gmail API
  const gmail = google.gmail({ version: "v1", auth: oauth2Client });

  // -------------------------------------------------------------------
  // Server implementation
  // -------------------------------------------------------------------
  const server = new Server(
    { name: "gmail", version: "2.1.0" },
    { capabilities: { tools: {} } }
  );

  // -------------------------------------------------------------------
  // Tool registration — 22 tools
  // -------------------------------------------------------------------
  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
      // Core email (6)
      {
        name: "send_email",
        description: "Sends a new email",
        inputSchema: zodToJsonSchema(SendEmailSchema),
      },
      {
        name: "draft_email",
        description: "Draft a new email",
        inputSchema: zodToJsonSchema(SendEmailSchema),
      },
      {
        name: "read_email",
        description: "Retrieves the content of a specific email",
        inputSchema: zodToJsonSchema(ReadEmailSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "search_emails",
        description: "Searches for emails using Gmail search syntax",
        inputSchema: zodToJsonSchema(SearchEmailsSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "modify_email",
        description: "Modifies email labels (move to different folders)",
        inputSchema: zodToJsonSchema(ModifyEmailSchema),
      },
      {
        name: "delete_email",
        description: "Permanently deletes an email",
        inputSchema: zodToJsonSchema(DeleteEmailSchema),
      },
      // Labels (5)
      {
        name: "list_email_labels",
        description: "Retrieves all available Gmail labels",
        inputSchema: zodToJsonSchema(ListEmailLabelsSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "create_label",
        description: "Creates a new Gmail label",
        inputSchema: zodToJsonSchema(CreateLabelSchema),
      },
      {
        name: "update_label",
        description: "Updates an existing Gmail label",
        inputSchema: zodToJsonSchema(UpdateLabelSchema),
      },
      {
        name: "delete_label",
        description: "Deletes a Gmail label",
        inputSchema: zodToJsonSchema(DeleteLabelSchema),
      },
      {
        name: "get_or_create_label",
        description:
          "Gets an existing label by name or creates it if it doesn't exist",
        inputSchema: zodToJsonSchema(GetOrCreateLabelSchema),
      },
      // Batch (2)
      {
        name: "batch_modify_emails",
        description: "Modifies labels for multiple emails in batches",
        inputSchema: zodToJsonSchema(BatchModifyEmailsSchema),
      },
      {
        name: "batch_delete_emails",
        description: "Permanently deletes multiple emails in batches",
        inputSchema: zodToJsonSchema(BatchDeleteEmailsSchema),
      },
      // Filters (4)
      {
        name: "create_filter",
        description:
          "Creates a new Gmail filter with custom criteria and actions",
        inputSchema: zodToJsonSchema(CreateFilterSchema),
      },
      {
        name: "list_filters",
        description: "Retrieves all Gmail filters",
        inputSchema: zodToJsonSchema(ListFiltersSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "get_filter",
        description: "Gets details of a specific Gmail filter",
        inputSchema: zodToJsonSchema(GetFilterSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "delete_filter",
        description: "Deletes a Gmail filter",
        inputSchema: zodToJsonSchema(DeleteFilterSchema),
      },
      {
        name: "create_filter_from_template",
        description:
          "Creates a filter using a pre-defined template for common scenarios",
        inputSchema: zodToJsonSchema(CreateFilterFromTemplateSchema),
      },
      // Attachment (1)
      {
        name: "download_attachment",
        description: "Downloads an email attachment to a specified location",
        inputSchema: zodToJsonSchema(DownloadAttachmentSchema),
        annotations: { readOnlyHint: true },
      },
      // NEW enhancements (3)
      {
        name: "list_threads",
        description:
          "Lists email threads matching a search query with message counts",
        inputSchema: zodToJsonSchema(ListThreadsSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "get_thread",
        description:
          "Retrieves a full email thread as a conversation view with all messages",
        inputSchema: zodToJsonSchema(GetThreadSchema),
        annotations: { readOnlyHint: true },
      },
      {
        name: "lookup_contact",
        description:
          "Looks up a contact by email address in Google Contacts",
        inputSchema: zodToJsonSchema(LookupContactSchema),
        annotations: { readOnlyHint: true },
      },
    ],
  }));

  // -------------------------------------------------------------------
  // Tool handler
  // -------------------------------------------------------------------
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    // -----------------------------------------------------------------
    // Helper: send or draft an email
    // -----------------------------------------------------------------
    async function handleEmailAction(action, validatedArgs) {
      let message;
      try {
        if (validatedArgs.attachments && validatedArgs.attachments.length > 0) {
          // Use Nodemailer for MIME with attachments
          message = await createEmailWithNodemailer(validatedArgs);

          const encodedMessage = Buffer.from(message)
            .toString("base64")
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/=+$/, "");

          if (action === "send") {
            const result = await gmail.users.messages.send({
              userId: "me",
              requestBody: {
                raw: encodedMessage,
                ...(validatedArgs.threadId && {
                  threadId: validatedArgs.threadId,
                }),
              },
            });
            return {
              content: [
                {
                  type: "text",
                  text: `Email sent successfully with ID: ${result.data.id}`,
                },
              ],
            };
          } else {
            const response = await gmail.users.drafts.create({
              userId: "me",
              requestBody: {
                message: {
                  raw: encodedMessage,
                  ...(validatedArgs.threadId && {
                    threadId: validatedArgs.threadId,
                  }),
                },
              },
            });
            return {
              content: [
                {
                  type: "text",
                  text: `Email draft created successfully with ID: ${response.data.id}`,
                },
              ],
            };
          }
        } else {
          // Simple email without attachments
          message = createEmailMessage(validatedArgs);

          const encodedMessage = Buffer.from(message)
            .toString("base64")
            .replace(/\+/g, "-")
            .replace(/\//g, "_")
            .replace(/=+$/, "");

          const messageRequest = {
            raw: encodedMessage,
          };
          if (validatedArgs.threadId) {
            messageRequest.threadId = validatedArgs.threadId;
          }

          if (action === "send") {
            const response = await gmail.users.messages.send({
              userId: "me",
              requestBody: messageRequest,
            });
            return {
              content: [
                {
                  type: "text",
                  text: `Email sent successfully with ID: ${response.data.id}`,
                },
              ],
            };
          } else {
            const response = await gmail.users.drafts.create({
              userId: "me",
              requestBody: { message: messageRequest },
            });
            return {
              content: [
                {
                  type: "text",
                  text: `Email draft created successfully with ID: ${response.data.id}`,
                },
              ],
            };
          }
        }
      } catch (error) {
        if (validatedArgs.attachments && validatedArgs.attachments.length > 0) {
          console.error(
            `Failed to send email with ${validatedArgs.attachments.length} attachments:`,
            error.message
          );
        }
        throw error;
      }
    }

    // -----------------------------------------------------------------
    // Helper: process operations in batches with retry
    // -----------------------------------------------------------------
    async function processBatches(items, batchSize, processFn) {
      const successes = [];
      const failures = [];

      for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize);
        try {
          const results = await processFn(batch);
          successes.push(...results);
        } catch (_error) {
          // If batch fails, retry individual items
          for (const item of batch) {
            try {
              const result = await processFn([item]);
              successes.push(...result);
            } catch (itemError) {
              failures.push({ item, error: itemError });
            }
          }
        }
      }

      return { successes, failures };
    }

    // -----------------------------------------------------------------
    // Route to handlers (wrapped with retry for transient failures)
    // -----------------------------------------------------------------
    try {
      return await withRetry(async () => {
      switch (name) {
        // =============================================================
        // SEND / DRAFT
        // =============================================================
        case "send_email":
        case "draft_email": {
          const validatedArgs = SendEmailSchema.parse(args);
          const action = name === "send_email" ? "send" : "draft";
          return await handleEmailAction(action, validatedArgs);
        }

        // =============================================================
        // READ EMAIL
        // =============================================================
        case "read_email": {
          const validatedArgs = ReadEmailSchema.parse(args);
          const response = await gmail.users.messages.get({
            userId: "me",
            id: validatedArgs.messageId,
            format: "full",
          });

          const headers = response.data.payload?.headers || [];
          const subject =
            headers.find((h) => h.name?.toLowerCase() === "subject")?.value ||
            "";
          const from =
            headers.find((h) => h.name?.toLowerCase() === "from")?.value || "";
          const to =
            headers.find((h) => h.name?.toLowerCase() === "to")?.value || "";
          const date =
            headers.find((h) => h.name?.toLowerCase() === "date")?.value || "";
          const threadId = response.data.threadId || "";

          const { text, html } = extractEmailContent(
            response.data.payload || {}
          );
          let body = text || html || "";

          const contentTypeNote =
            !text && html
              ? "[Note: This email is HTML-formatted. Plain text version not available.]\n\n"
              : "";

          // Collect attachment info
          const attachments = [];
          const processAttachmentParts = (part) => {
            if (part.body && part.body.attachmentId) {
              const filename =
                part.filename || `attachment-${part.body.attachmentId}`;
              attachments.push({
                id: part.body.attachmentId,
                filename,
                mimeType: part.mimeType || "application/octet-stream",
                size: part.body.size || 0,
              });
            }
            if (part.parts) {
              part.parts.forEach((subpart) => processAttachmentParts(subpart));
            }
          };
          if (response.data.payload) {
            processAttachmentParts(response.data.payload);
          }

          const attachmentInfo =
            attachments.length > 0
              ? `\n\nAttachments (${attachments.length}):\n` +
                attachments
                  .map(
                    (a) =>
                      `- ${a.filename} (${a.mimeType}, ${Math.round(a.size / 1024)} KB, ID: ${a.id})`
                  )
                  .join("\n")
              : "";

          return {
            content: [
              {
                type: "text",
                text: `Thread ID: ${threadId}\nSubject: ${subject}\nFrom: ${from}\nTo: ${to}\nDate: ${date}\n\n${contentTypeNote}${body}${attachmentInfo}`,
              },
            ],
          };
        }

        // =============================================================
        // SEARCH EMAILS
        // =============================================================
        case "search_emails": {
          const validatedArgs = SearchEmailsSchema.parse(args);
          const response = await gmail.users.messages.list({
            userId: "me",
            q: validatedArgs.query,
            maxResults: validatedArgs.maxResults || 10,
          });

          const messages = response.data.messages || [];

          // Fetch metadata in concurrency-controlled batches to avoid rate limits
          const CONCURRENCY = 10;
          const results = [];
          for (let i = 0; i < messages.length; i += CONCURRENCY) {
            const batch = messages.slice(i, i + CONCURRENCY);
            const batchResults = await Promise.all(
              batch.map(async (msg) => {
                const detail = await gmail.users.messages.get({
                  userId: "me",
                  id: msg.id,
                  format: "metadata",
                  metadataHeaders: ["Subject", "From", "Date"],
                  fields: "id,payload/headers",
                });
                const headers = detail.data.payload?.headers || [];
                return {
                  id: msg.id,
                  subject:
                    headers.find((h) => h.name === "Subject")?.value || "",
                  from: headers.find((h) => h.name === "From")?.value || "",
                  date: headers.find((h) => h.name === "Date")?.value || "",
                };
              })
            );
            results.push(...batchResults);
          }

          return {
            content: [
              {
                type: "text",
                text: results
                  .map(
                    (r) =>
                      `ID: ${r.id}\nSubject: ${r.subject}\nFrom: ${r.from}\nDate: ${r.date}\n`
                  )
                  .join("\n"),
              },
            ],
          };
        }

        // =============================================================
        // MODIFY EMAIL
        // =============================================================
        case "modify_email": {
          const validatedArgs = ModifyEmailSchema.parse(args);
          const requestBody = {};
          if (validatedArgs.labelIds) {
            requestBody.addLabelIds = validatedArgs.labelIds;
          }
          if (validatedArgs.addLabelIds) {
            requestBody.addLabelIds = validatedArgs.addLabelIds;
          }
          if (validatedArgs.removeLabelIds) {
            requestBody.removeLabelIds = validatedArgs.removeLabelIds;
          }

          await gmail.users.messages.modify({
            userId: "me",
            id: validatedArgs.messageId,
            requestBody,
          });

          return {
            content: [
              {
                type: "text",
                text: `Email ${validatedArgs.messageId} labels updated successfully`,
              },
            ],
          };
        }

        // =============================================================
        // DELETE EMAIL
        // =============================================================
        case "delete_email": {
          const validatedArgs = DeleteEmailSchema.parse(args);
          await gmail.users.messages.delete({
            userId: "me",
            id: validatedArgs.messageId,
          });
          return {
            content: [
              {
                type: "text",
                text: `Email ${validatedArgs.messageId} deleted successfully`,
              },
            ],
          };
        }

        // =============================================================
        // LIST EMAIL LABELS
        // =============================================================
        case "list_email_labels": {
          const labelResults = await listLabels(gmail);
          const systemLabels = labelResults.system;
          const userLabels = labelResults.user;

          return {
            content: [
              {
                type: "text",
                text:
                  `Found ${labelResults.count.total} labels (${labelResults.count.system} system, ${labelResults.count.user} user):\n\n` +
                  "System Labels:\n" +
                  systemLabels
                    .map((l) => `ID: ${l.id}\nName: ${l.name}\n`)
                    .join("\n") +
                  "\nUser Labels:\n" +
                  userLabels
                    .map((l) => `ID: ${l.id}\nName: ${l.name}\n`)
                    .join("\n"),
              },
            ],
          };
        }

        // =============================================================
        // BATCH MODIFY EMAILS
        // =============================================================
        case "batch_modify_emails": {
          const validatedArgs = BatchModifyEmailsSchema.parse(args);
          const messageIds = validatedArgs.messageIds;
          const batchSize = validatedArgs.batchSize || 50;

          const requestBody = {};
          if (validatedArgs.addLabelIds) {
            requestBody.addLabelIds = validatedArgs.addLabelIds;
          }
          if (validatedArgs.removeLabelIds) {
            requestBody.removeLabelIds = validatedArgs.removeLabelIds;
          }

          const { successes, failures } = await processBatches(
            messageIds,
            batchSize,
            async (batch) => {
              const results = await Promise.all(
                batch.map(async (messageId) => {
                  await gmail.users.messages.modify({
                    userId: "me",
                    id: messageId,
                    requestBody,
                  });
                  return { messageId, success: true };
                })
              );
              return results;
            }
          );

          const successCount = successes.length;
          const failureCount = failures.length;
          let resultText = `Batch label modification complete.\n`;
          resultText += `Successfully processed: ${successCount} messages\n`;
          if (failureCount > 0) {
            resultText += `Failed to process: ${failureCount} messages\n\n`;
            resultText += `Failed message IDs:\n`;
            resultText += failures
              .map(
                (f) =>
                  `- ${f.item.substring(0, 16)}... (${f.error.message})`
              )
              .join("\n");
          }

          return {
            content: [{ type: "text", text: resultText }],
          };
        }

        // =============================================================
        // BATCH DELETE EMAILS
        // =============================================================
        case "batch_delete_emails": {
          const validatedArgs = BatchDeleteEmailsSchema.parse(args);
          const messageIds = validatedArgs.messageIds;
          const batchSize = validatedArgs.batchSize || 50;

          const { successes, failures } = await processBatches(
            messageIds,
            batchSize,
            async (batch) => {
              const results = await Promise.all(
                batch.map(async (messageId) => {
                  await gmail.users.messages.delete({
                    userId: "me",
                    id: messageId,
                  });
                  return { messageId, success: true };
                })
              );
              return results;
            }
          );

          const successCount = successes.length;
          const failureCount = failures.length;
          let resultText = `Batch delete operation complete.\n`;
          resultText += `Successfully deleted: ${successCount} messages\n`;
          if (failureCount > 0) {
            resultText += `Failed to delete: ${failureCount} messages\n\n`;
            resultText += `Failed message IDs:\n`;
            resultText += failures
              .map(
                (f) =>
                  `- ${f.item.substring(0, 16)}... (${f.error.message})`
              )
              .join("\n");
          }

          return {
            content: [{ type: "text", text: resultText }],
          };
        }

        // =============================================================
        // CREATE LABEL
        // =============================================================
        case "create_label": {
          const validatedArgs = CreateLabelSchema.parse(args);
          const result = await createLabel(gmail, validatedArgs.name, {
            messageListVisibility: validatedArgs.messageListVisibility,
            labelListVisibility: validatedArgs.labelListVisibility,
          });
          return {
            content: [
              {
                type: "text",
                text: `Label created successfully:\nID: ${result.id}\nName: ${result.name}\nType: ${result.type}`,
              },
            ],
          };
        }

        // =============================================================
        // UPDATE LABEL
        // =============================================================
        case "update_label": {
          const validatedArgs = UpdateLabelSchema.parse(args);
          const updates = {};
          if (validatedArgs.name) updates.name = validatedArgs.name;
          if (validatedArgs.messageListVisibility)
            updates.messageListVisibility =
              validatedArgs.messageListVisibility;
          if (validatedArgs.labelListVisibility)
            updates.labelListVisibility = validatedArgs.labelListVisibility;

          const result = await updateLabel(gmail, validatedArgs.id, updates);
          return {
            content: [
              {
                type: "text",
                text: `Label updated successfully:\nID: ${result.id}\nName: ${result.name}\nType: ${result.type}`,
              },
            ],
          };
        }

        // =============================================================
        // DELETE LABEL
        // =============================================================
        case "delete_label": {
          const validatedArgs = DeleteLabelSchema.parse(args);
          const result = await deleteLabel(gmail, validatedArgs.id);
          return {
            content: [{ type: "text", text: result.message }],
          };
        }

        // =============================================================
        // GET OR CREATE LABEL
        // =============================================================
        case "get_or_create_label": {
          const validatedArgs = GetOrCreateLabelSchema.parse(args);
          const result = await getOrCreateLabel(gmail, validatedArgs.name, {
            messageListVisibility: validatedArgs.messageListVisibility,
            labelListVisibility: validatedArgs.labelListVisibility,
          });
          const action =
            result.type === "user" && result.name === validatedArgs.name
              ? "found existing"
              : "created new";
          return {
            content: [
              {
                type: "text",
                text: `Successfully ${action} label:\nID: ${result.id}\nName: ${result.name}\nType: ${result.type}`,
              },
            ],
          };
        }

        // =============================================================
        // CREATE FILTER
        // =============================================================
        case "create_filter": {
          const validatedArgs = CreateFilterSchema.parse(args);
          const result = await createFilter(
            gmail,
            validatedArgs.criteria,
            validatedArgs.action
          );

          const criteriaText = Object.entries(validatedArgs.criteria)
            .filter(([_, value]) => value !== undefined)
            .map(([key, value]) => `${key}: ${value}`)
            .join(", ");
          const actionText = Object.entries(validatedArgs.action)
            .filter(
              ([_, value]) =>
                value !== undefined &&
                (Array.isArray(value) ? value.length > 0 : true)
            )
            .map(([key, value]) =>
              `${key}: ${Array.isArray(value) ? value.join(", ") : value}`
            )
            .join(", ");

          return {
            content: [
              {
                type: "text",
                text: `Filter created successfully:\nID: ${result.id}\nCriteria: ${criteriaText}\nActions: ${actionText}`,
              },
            ],
          };
        }

        // =============================================================
        // LIST FILTERS
        // =============================================================
        case "list_filters": {
          const result = await listFilters(gmail);
          const filters = result.filters;

          if (filters.length === 0) {
            return {
              content: [{ type: "text", text: "No filters found." }],
            };
          }

          const filtersText = filters
            .map((filter) => {
              const criteriaEntries = Object.entries(filter.criteria || {})
                .filter(([_, value]) => value !== undefined)
                .map(([key, value]) => `${key}: ${value}`)
                .join(", ");
              const actionEntries = Object.entries(filter.action || {})
                .filter(
                  ([_, value]) =>
                    value !== undefined &&
                    (Array.isArray(value) ? value.length > 0 : true)
                )
                .map(([key, value]) =>
                  `${key}: ${Array.isArray(value) ? value.join(", ") : value}`
                )
                .join(", ");
              return `ID: ${filter.id}\nCriteria: ${criteriaEntries}\nActions: ${actionEntries}\n`;
            })
            .join("\n");

          return {
            content: [
              {
                type: "text",
                text: `Found ${result.count} filters:\n\n${filtersText}`,
              },
            ],
          };
        }

        // =============================================================
        // GET FILTER
        // =============================================================
        case "get_filter": {
          const validatedArgs = GetFilterSchema.parse(args);
          const result = await getFilter(gmail, validatedArgs.filterId);

          const criteriaText = Object.entries(result.criteria || {})
            .filter(([_, value]) => value !== undefined)
            .map(([key, value]) => `${key}: ${value}`)
            .join(", ");
          const actionText = Object.entries(result.action || {})
            .filter(
              ([_, value]) =>
                value !== undefined &&
                (Array.isArray(value) ? value.length > 0 : true)
            )
            .map(([key, value]) =>
              `${key}: ${Array.isArray(value) ? value.join(", ") : value}`
            )
            .join(", ");

          return {
            content: [
              {
                type: "text",
                text: `Filter details:\nID: ${result.id}\nCriteria: ${criteriaText}\nActions: ${actionText}`,
              },
            ],
          };
        }

        // =============================================================
        // DELETE FILTER
        // =============================================================
        case "delete_filter": {
          const validatedArgs = DeleteFilterSchema.parse(args);
          const result = await deleteFilter(gmail, validatedArgs.filterId);
          return {
            content: [{ type: "text", text: result.message }],
          };
        }

        // =============================================================
        // CREATE FILTER FROM TEMPLATE
        // =============================================================
        case "create_filter_from_template": {
          const validatedArgs = CreateFilterFromTemplateSchema.parse(args);
          const template = validatedArgs.template;
          const params = validatedArgs.parameters;
          let filterConfig;

          switch (template) {
            case "fromSender":
              if (!params.senderEmail)
                throw new Error(
                  "senderEmail is required for fromSender template"
                );
              filterConfig = filterTemplates.fromSender(
                params.senderEmail,
                params.labelIds,
                params.archive
              );
              break;
            case "withSubject":
              if (!params.subjectText)
                throw new Error(
                  "subjectText is required for withSubject template"
                );
              filterConfig = filterTemplates.withSubject(
                params.subjectText,
                params.labelIds,
                params.markAsRead
              );
              break;
            case "withAttachments":
              filterConfig = filterTemplates.withAttachments(params.labelIds);
              break;
            case "largeEmails":
              if (!params.sizeInBytes)
                throw new Error(
                  "sizeInBytes is required for largeEmails template"
                );
              filterConfig = filterTemplates.largeEmails(
                params.sizeInBytes,
                params.labelIds
              );
              break;
            case "containingText":
              if (!params.searchText)
                throw new Error(
                  "searchText is required for containingText template"
                );
              filterConfig = filterTemplates.containingText(
                params.searchText,
                params.labelIds,
                params.markImportant
              );
              break;
            case "mailingList":
              if (!params.listIdentifier)
                throw new Error(
                  "listIdentifier is required for mailingList template"
                );
              filterConfig = filterTemplates.mailingList(
                params.listIdentifier,
                params.labelIds,
                params.archive
              );
              break;
            default:
              throw new Error(`Unknown template: ${template}`);
          }

          const result = await createFilter(
            gmail,
            filterConfig.criteria,
            filterConfig.action
          );
          return {
            content: [
              {
                type: "text",
                text: `Filter created from template '${template}':\nID: ${result.id}\nTemplate used: ${template}`,
              },
            ],
          };
        }

        // =============================================================
        // DOWNLOAD ATTACHMENT
        // =============================================================
        case "download_attachment": {
          const validatedArgs = DownloadAttachmentSchema.parse(args);

          try {
            const attachmentResponse =
              await gmail.users.messages.attachments.get({
                userId: "me",
                messageId: validatedArgs.messageId,
                id: validatedArgs.attachmentId,
              });

            if (!attachmentResponse.data.data) {
              throw new Error("No attachment data received");
            }

            const data = attachmentResponse.data.data;
            const buffer = Buffer.from(data, "base64url");

            const savePath = validatedArgs.savePath || process.cwd();
            let filename = validatedArgs.filename;

            if (!filename) {
              // Get original filename from the message parts
              const messageResponse = await gmail.users.messages.get({
                userId: "me",
                id: validatedArgs.messageId,
                format: "full",
              });

              const findAttachment = (part) => {
                if (
                  part.body &&
                  part.body.attachmentId === validatedArgs.attachmentId
                ) {
                  return (
                    part.filename ||
                    `attachment-${validatedArgs.attachmentId}`
                  );
                }
                if (part.parts) {
                  for (const subpart of part.parts) {
                    const found = findAttachment(subpart);
                    if (found) return found;
                  }
                }
                return null;
              };

              filename =
                findAttachment(messageResponse.data.payload) ||
                `attachment-${validatedArgs.attachmentId}`;
            }

            // Ensure save directory exists
            if (!fs.existsSync(savePath)) {
              fs.mkdirSync(savePath, { recursive: true });
            }

            const fullPath = path.join(savePath, filename);
            fs.writeFileSync(fullPath, buffer);

            return {
              content: [
                {
                  type: "text",
                  text: `Attachment downloaded successfully:\nFile: ${filename}\nSize: ${buffer.length} bytes\nSaved to: ${fullPath}`,
                },
              ],
            };
          } catch (error) {
            return {
              content: [
                {
                  type: "text",
                  text: `Failed to download attachment: ${error.message}`,
                },
              ],
              isError: true,
            };
          }
        }

        // =============================================================
        // NEW: LIST THREADS
        // =============================================================
        case "list_threads": {
          const validatedArgs = ListThreadsSchema.parse(args);
          const threads = await listThreads(
            gmail,
            validatedArgs.query,
            validatedArgs.maxResults
          );

          if (threads.length === 0) {
            return {
              content: [
                {
                  type: "text",
                  text: "No threads found matching that query.",
                },
              ],
            };
          }

          const threadsText = threads
            .map(
              (t) =>
                `Thread ID: ${t.id}\nSubject: ${t.subject}\nFrom: ${t.from}\nDate: ${t.date}\nMessages: ${t.messageCount}\nLast message: ${t.lastMessageDate}\nSnippet: ${t.snippet}\n`
            )
            .join("\n");

          return {
            content: [
              {
                type: "text",
                text: `Found ${threads.length} threads:\n\n${threadsText}`,
              },
            ],
          };
        }

        // =============================================================
        // NEW: GET THREAD
        // =============================================================
        case "get_thread": {
          const validatedArgs = GetThreadSchema.parse(args);
          const thread = await getThread(
            gmail,
            validatedArgs.threadId,
            validatedArgs.format
          );

          const messagesText = thread.messages
            .map(
              (m, i) =>
                `--- Message ${i + 1} of ${thread.messageCount} ---\n` +
                `ID: ${m.id}\n` +
                `From: ${m.from}\n` +
                `To: ${m.to}\n` +
                `Date: ${m.date}\n` +
                `Subject: ${m.subject}\n` +
                (m.isHtml
                  ? "[Note: HTML content]\n"
                  : "") +
                `\n${m.body}\n`
            )
            .join("\n");

          return {
            content: [
              {
                type: "text",
                text: `Thread ${thread.id} (${thread.messageCount} messages):\n\n${messagesText}`,
              },
            ],
          };
        }

        // =============================================================
        // NEW: LOOKUP CONTACT
        // =============================================================
        case "lookup_contact": {
          const validatedArgs = LookupContactSchema.parse(args);
          const result = await lookupContact(oauth2Client, validatedArgs.email);

          if (!result.found) {
            return {
              content: [{ type: "text", text: result.message }],
            };
          }

          const contactsText = result.contacts
            .map(
              (c) =>
                `Name: ${c.displayName}\n` +
                `Email: ${c.email}\n` +
                (c.organization
                  ? `Organization: ${c.organization}\n`
                  : "") +
                (c.title ? `Title: ${c.title}\n` : "") +
                (c.photoUrl ? `Photo: ${c.photoUrl}\n` : "")
            )
            .join("\n");

          return {
            content: [
              {
                type: "text",
                text: `Contact found for ${validatedArgs.email}:\n\n${contactsText}`,
              },
            ],
          };
        }

        // =============================================================
        // UNKNOWN TOOL
        // =============================================================
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

  // -------------------------------------------------------------------
  // Start server
  // -------------------------------------------------------------------
  const transport = new StdioServerTransport();
  server.connect(transport).catch((error) => {
    console.error("Fatal error running server:", error);
    process.exit(1);
  });
  console.error("Enhanced Gmail MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
