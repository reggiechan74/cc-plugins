# google-workspace-mcp

Gmail, Google Calendar, and Google Contacts MCP servers for Claude Code.

## Install

```bash
claude plugin add github:reggiechan74/cc-plugins/google-workspace-mcp
```

## First-Time Setup

### 1. Create GCP OAuth Credentials

1. Go to [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials)
2. Create an **OAuth 2.0 Client ID** (Desktop app type)
3. Download the JSON file
4. Save it to both locations:
   ```bash
   mkdir -p ~/.gmail-mcp ~/.calendar-mcp
   cp ~/Downloads/client_secret_*.json ~/.gmail-mcp/gcp-oauth.keys.json
   cp ~/Downloads/client_secret_*.json ~/.calendar-mcp/gcp-oauth.keys.json
   ```

### 2. Enable Required APIs

Enable these in your GCP project:
- [Gmail API](https://console.developers.google.com/apis/api/gmail.googleapis.com/overview)
- [Google Calendar API](https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview)
- [People API](https://console.developers.google.com/apis/api/people.googleapis.com/overview) (for contact lookup)

### 3. Authenticate

Run the `/authenticate` skill in Claude Code:
```
/authenticate
```

This runs the OAuth flow for both Gmail and Calendar servers.

## Tools (28)

### Gmail (22 tools)

| Tool | Description |
|------|-------------|
| `send_email` | Send an email with optional CC, BCC, attachments |
| `draft_email` | Create a draft email |
| `read_email` | Read a specific email by message ID |
| `search_emails` | Search emails using Gmail query syntax |
| `modify_email` | Add/remove labels on an email |
| `delete_email` | Permanently delete an email |
| `list_email_labels` | List all Gmail labels |
| `create_label` | Create a new label |
| `update_label` | Update label name or visibility |
| `delete_label` | Delete a label |
| `get_or_create_label` | Get existing label or create if missing |
| `batch_modify_emails` | Modify labels on multiple emails |
| `batch_delete_emails` | Delete multiple emails in batches |
| `create_filter` | Create a Gmail filter with criteria and actions |
| `list_filters` | List all Gmail filters |
| `get_filter` | Get details of a specific filter |
| `delete_filter` | Delete a Gmail filter |
| `create_filter_from_template` | Create filter from predefined template |
| `download_attachment` | Download an email attachment |
| `list_threads` | List email threads matching a query |
| `get_thread` | Get full conversation thread |
| `lookup_contact` | Look up contact by email via Google People API |

### Google Calendar (6 tools)

| Tool | Description |
|------|-------------|
| `list_calendars` | List all accessible calendars |
| `list_events` | List events in a time range |
| `create_event` | Create a new calendar event |
| `get_event` | Get details of a specific event |
| `update_event` | Update an existing event |
| `delete_event` | Delete a calendar event |

## Authentication Details

- **Gmail OAuth keys:** `~/.gmail-mcp/gcp-oauth.keys.json`
- **Gmail tokens:** `~/.gmail-mcp/credentials.json`
- **Calendar OAuth keys:** `~/.calendar-mcp/gcp-oauth.keys.json`
- **Calendar tokens:** `~/.calendar-mcp/credentials.json`
- **Gmail scopes:** `gmail.modify`, `gmail.settings.basic`, `contacts.readonly`
- **Calendar scopes:** `calendar`

## Troubleshooting

**"Credentials missing" warning on session start:**
Run `/authenticate` to set up OAuth tokens.

**"Insufficient Permission" on lookup_contact:**
Enable the [People API](https://console.developers.google.com/apis/api/people.googleapis.com/overview) in your GCP project.

**Port 3000 busy during auth:**
```bash
lsof -ti:3000 | xargs kill
```
Then re-run `/authenticate`.

**Token expired / refresh errors:**
Re-run `/authenticate` to get fresh tokens.

## License

MIT
