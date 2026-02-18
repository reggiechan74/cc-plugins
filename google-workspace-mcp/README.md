# Google Workspace MCP for Claude Code

Model Context Protocol servers that integrate Gmail, Google Calendar, and Google Contacts with Claude Code.

## Install

```bash
claude plugin add github:reggiechan74/cc-plugins/google-workspace-mcp
```

## Features

**29 tools** across Google Workspace services:

### Gmail (22 tools)
- **Email**: send, draft, read, search, modify labels, delete
- **Batch**: bulk modify labels, bulk delete
- **Labels**: list, create, update, delete, get-or-create
- **Filters**: create, list, get, delete, create from template
- **Attachments**: download
- **Threads**: list, get full conversation view
- **Contacts**: look up by email

### Google Calendar (7 tools)
- **Calendars**: list all accessible calendars
- **Events**: create, get, update, delete
- **Queries**: list events (single calendar), list events multi (parallel multi-calendar with batch API)

### Reliability & Performance (v2.0.0)
- **OAuth auto-refresh**: tokens persist to disk automatically, no manual re-auth needed
- **Retry with backoff**: transient failures (401, 429, 5xx) auto-retry with exponential backoff
- **Read-only annotations**: non-mutating tools marked for optimized client handling
- **Concurrency control**: search and thread listing use batched parallel requests
- **Response trimming**: calendar events return only essential fields
- **In-memory caching**: calendar queries use 3-minute TTL cache with syncToken revalidation
- **MCP SDK 1.26.0**: latest protocol support

## Setup

### 1. Create GCP OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create an OAuth 2.0 Client ID (Desktop application type)
3. Download the JSON credentials file

### 2. Enable APIs

Enable these APIs in your GCP project:
- [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
- [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
- [People API](https://console.cloud.google.com/apis/library/people.googleapis.com)

### 3. Store Credentials

Copy the OAuth JSON to both config directories:

```bash
mkdir -p ~/.gmail-mcp ~/.calendar-mcp
cp your-oauth-keys.json ~/.gmail-mcp/gcp-oauth.keys.json
cp your-oauth-keys.json ~/.calendar-mcp/gcp-oauth.keys.json
```

### 4. Authenticate

Run `/authenticate` in Claude Code to complete the OAuth flow for both services.

## Calendar Shortnames

The calendar server supports optional shortname resolution. Edit the `CALENDAR_SHORTNAMES` map in `servers/calendar/index.js` to add your own mappings. Run `list_calendars` to discover your calendar IDs.

Example:

```js
const CALENDAR_SHORTNAMES = {
  work: "user@company.com",
  personal: "user@gmail.com",
  team: "abc123@group.calendar.google.com",
};
```

## License

MIT
