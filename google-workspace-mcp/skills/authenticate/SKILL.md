---
name: authenticate
description: Authenticate Gmail and Google Calendar MCP servers. Use after first install, after codespace rebuild, or when MCP authentication fails. Runs OAuth flow for both Gmail and Calendar services.
---

# Google Workspace Authentication

Authenticate the Gmail and Google Calendar MCP servers via OAuth 2.0.

## Prerequisites

1. A Google Cloud Platform project with a Desktop-type OAuth 2.0 Client ID
2. Download the OAuth JSON and place it in BOTH locations:
   - `~/.gmail-mcp/gcp-oauth.keys.json`
   - `~/.calendar-mcp/gcp-oauth.keys.json`
3. Enable these APIs in the GCP project:
   - Gmail API
   - Google Calendar API
   - People API (for contact lookup)

## Procedure

1. Verify OAuth keys exist:
   ```bash
   ls ~/.gmail-mcp/gcp-oauth.keys.json ~/.calendar-mcp/gcp-oauth.keys.json
   ```

2. Create config directories if missing:
   ```bash
   mkdir -p ~/.gmail-mcp ~/.calendar-mcp
   ```

3. Authenticate Gmail server (opens browser for OAuth consent):
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/servers/gmail/index.js auth
   ```

4. Authenticate Calendar server:
   ```bash
   node ${CLAUDE_PLUGIN_ROOT}/servers/calendar/index.js auth
   ```

5. Verify credentials were created:
   ```bash
   ls ~/.gmail-mcp/credentials.json ~/.calendar-mcp/credentials.json
   ```

6. Test connectivity by running `/mcp` to reconnect both servers.

7. Report success/failure to user.

## Troubleshooting

- **Port 3000 conflict**: `lsof -ti:3000 | xargs kill -9` then retry
- **Browser doesn't open**: Copy the auth URL from terminal output manually
- **People API error**: Ensure People API is enabled in GCP console
- **Token expired**: Re-run this authentication flow. Tokens auto-refresh during normal use but may expire after prolonged inactivity.
