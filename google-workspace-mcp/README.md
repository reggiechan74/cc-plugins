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

> **Token expiry warning:** If your GCP app is in "Testing" publishing status (the default), Google enforces a **7-day refresh token expiry**. You will need to re-authenticate weekly by running `/authenticate` again. Publishing the app to "Production" removes this limit, but requires Google's verification process (privacy policy, homepage, domain verification) — even for personal-use apps.

### 2. Enable APIs

Enable these APIs in your GCP project:
- [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
- [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
- [People API](https://console.cloud.google.com/apis/library/people.googleapis.com)

### 3. Store Credentials

Each server reads OAuth app credentials from its own config directory. Copy the same OAuth JSON to both:

```bash
mkdir -p ~/.gmail-mcp ~/.calendar-mcp
cp your-oauth-keys.json ~/.gmail-mcp/gcp-oauth.keys.json
cp your-oauth-keys.json ~/.calendar-mcp/gcp-oauth.keys.json
```

> **Why two copies?** The Gmail and Calendar servers run as independent MCP processes, each loading credentials from its own directory. The Gmail server has a fallback to `~/.calendar-mcp/` if its own copy is missing, but the Calendar server does not — so both copies are required.

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

## Ephemeral Environments (Codespaces, Containers)

The `~/.gmail-mcp/` and `~/.calendar-mcp/` directories are lost on environment rebuild. To persist credentials:

1. **Store OAuth app keys as environment secrets:**
   ```bash
   # Codespaces: store as user-level secret
   gh secret set GOOGLE_OAUTH_CREDENTIALS --user --body "$(cat ~/.gmail-mcp/gcp-oauth.keys.json)"
   ```

2. **Store user tokens after first authentication:**
   ```bash
   gh secret set GMAIL_CREDENTIALS --user --body "$(cat ~/.gmail-mcp/credentials.json)"
   gh secret set CALENDAR_CREDENTIALS --user --body "$(cat ~/.calendar-mcp/credentials.json)"
   ```

3. **Hydrate on rebuild** (add to your `postCreateCommand` or startup script):
   ```bash
   mkdir -p ~/.gmail-mcp ~/.calendar-mcp
   echo "$GOOGLE_OAUTH_CREDENTIALS" > ~/.gmail-mcp/gcp-oauth.keys.json
   echo "$GOOGLE_OAUTH_CREDENTIALS" > ~/.calendar-mcp/gcp-oauth.keys.json
   echo "$GMAIL_CREDENTIALS" > ~/.gmail-mcp/credentials.json
   echo "$CALENDAR_CREDENTIALS" > ~/.calendar-mcp/credentials.json
   ```

The servers auto-refresh and persist access tokens to disk during normal use, so you only need to update the secrets periodically (or when the refresh token expires).

## License

MIT
