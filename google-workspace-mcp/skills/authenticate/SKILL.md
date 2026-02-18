---
name: authenticate
description: Authenticate Gmail and Google Calendar MCP servers. Use after first install, after codespace rebuild, or when MCP authentication fails.
allowed-tools: Bash
---

# Authenticate Google Workspace MCP

**Purpose:** Run OAuth authentication for Gmail and Google Calendar MCP servers.

**Use When:**
- First time installing this plugin
- After a codespace rebuild
- MCP servers show "No access, refresh token" errors
- After `~/.gmail-mcp/credentials.json` or `~/.calendar-mcp/credentials.json` are missing

## Prerequisites

You need a Google Cloud Platform OAuth 2.0 Client ID. If you don't have one:

1. Go to https://console.cloud.google.com/apis/credentials
2. Create an OAuth 2.0 Client ID (Desktop app type)
3. Download the JSON file
4. Save it to BOTH locations:
   - `~/.gmail-mcp/gcp-oauth.keys.json`
   - `~/.calendar-mcp/gcp-oauth.keys.json`

You also need these APIs enabled in your GCP project:
- Gmail API
- Google Calendar API
- People API (for contact lookup)

## Execution Steps

### Step 1: Check Prerequisites

```bash
echo "=== Checking OAuth client keys ==="
ls -la ~/.gmail-mcp/gcp-oauth.keys.json 2>/dev/null || echo "ERROR: No Gmail OAuth keys found at ~/.gmail-mcp/gcp-oauth.keys.json"
ls -la ~/.calendar-mcp/gcp-oauth.keys.json 2>/dev/null || echo "ERROR: No Calendar OAuth keys found at ~/.calendar-mcp/gcp-oauth.keys.json"
echo ""
echo "=== Checking existing credentials ==="
ls -la ~/.gmail-mcp/credentials.json 2>/dev/null && echo "Gmail: credentials exist" || echo "Gmail: needs authentication"
ls -la ~/.calendar-mcp/credentials.json 2>/dev/null && echo "Calendar: credentials exist" || echo "Calendar: needs authentication"
```

If OAuth keys are missing, stop and instruct the user to set up GCP credentials per the prerequisites section.

### Step 2: Create config directories

```bash
mkdir -p ~/.gmail-mcp ~/.calendar-mcp
```

### Step 3: Authenticate Gmail

```bash
echo "Starting Gmail authentication..."
node ${CLAUDE_PLUGIN_ROOT}/servers/gmail/index.js auth
```

This opens a browser for Google OAuth. Wait for the user to complete authentication. The process displays a URL and waits for the OAuth callback on port 3000.

Gmail scopes: `gmail.modify`, `gmail.settings.basic`, `contacts.readonly`

### Step 4: Authenticate Google Calendar

```bash
echo "Starting Google Calendar authentication..."
node ${CLAUDE_PLUGIN_ROOT}/servers/calendar/index.js auth
```

Same OAuth flow but for Calendar scope. Wait for completion.

Calendar scopes: `calendar`

### Step 5: Verify Credentials

```bash
echo "=== Verifying credentials ==="
ls -la ~/.gmail-mcp/credentials.json && echo "Gmail: OK" || echo "Gmail: FAILED"
ls -la ~/.calendar-mcp/credentials.json && echo "Calendar: OK" || echo "Calendar: FAILED"
```

### Step 6: Test Connectivity

Test both MCP servers:

**Test Gmail:**
- Use `mcp__gmail__search_emails` with query `is:inbox` and `maxResults: 3`

**Test Calendar:**
- Use `mcp__google-calendar__list_events` with today's date range

### Step 7: Report Status

Provide summary:
- Gmail MCP Server: [AUTHENTICATED/FAILED]
- Google Calendar MCP Server: [AUTHENTICATED/FAILED]

## Troubleshooting

- **Port 3000 busy:** `lsof -ti:3000 | xargs kill` then retry
- **Browser doesn't open:** Manually copy/paste the URL displayed in terminal
- **lookup_contact returns "Insufficient Permission":** Enable People API at `https://console.developers.google.com/apis/api/people.googleapis.com/overview`
- **Token expired:** Re-run `/authenticate` to get fresh tokens
