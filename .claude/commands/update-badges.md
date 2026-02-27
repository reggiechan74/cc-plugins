---
description: Add or update shields.io badges on plugin READMEs
allowed-tools: Read, Edit, Glob, Grep, AskUserQuestion
---

# Update Badges

Add or update shields.io badges on plugin README files.

**Arguments received:** $ARGUMENTS

## Instructions

### Step 1: Determine Targets

If `$ARGUMENTS` is provided, treat it as a plugin folder name (e.g., `nano-banana-plugin`). Validate that `/workspaces/claude-plugins/$ARGUMENTS/.claude-plugin/plugin.json` exists.

If `$ARGUMENTS` is empty, scan for all plugin directories by globbing `*/.claude-plugin/plugin.json` under `/workspaces/claude-plugins/`. Exclude `.git`, `.claude`, `.claude-plugin`, `node_modules`, `docs`, and hidden directories.

### Step 2: Auto-Detect Badges for Each Plugin

For each target plugin folder, read the following files to detect applicable badges:

1. **Read `.claude-plugin/plugin.json`** — extract `name`, `version`, `license`, `repository`, `keywords`
2. **Read `README.md`** — note existing badges (lines containing `img.shields.io`)
3. **Read `LICENSE`** — if present, confirm license type from first line
4. **Scan for language signals:**
   - Python files (`*.py`) → Python badge
   - `package.json` → Node.js badge
   - `*.ts` files → TypeScript badge
   - `*.sh` files only → Bash badge
5. **Scan skill files for API keywords:**
   - "Gemini" → `powered_by-Gemini_API-orange`
   - "OpenAI" → `powered_by-OpenAI-412991`
   - "Google" (Calendar, Gmail, etc.) → `Google_Workspace-4285F4`
   - "ArcGIS" or "Esri" → `ArcGIS-2C7AC3`
6. **Always include:** Claude Code plugin badge (`Claude_Code-plugin-blueviolet`)

Build a candidate list of badges. Each badge has:
- **label**: Display name (e.g., "Version", "License: MIT")
- **url**: Full shields.io markdown (e.g., `![Version](https://img.shields.io/badge/version-1.0.0-blue)`)
- **detected**: Whether it was auto-detected (true) or an optional addition

### Step 3: Present Badge Choices

Use `AskUserQuestion` with `multiSelect: true` to present the detected badges. Auto-detected badges should be listed first with "(Recommended)" in their label. Include these additional optional badges the user can opt into:

- GitHub Stars (live counter from shields.io GitHub API)
- GitHub Last Commit
- GitHub Issues
- Custom badge (user provides label, message, color)

### Step 4: Generate Badge Markdown

For each selected badge, generate a shields.io markdown image link. Use this format:

```
[![Label](https://img.shields.io/badge/ENCODED_LABEL-MESSAGE-COLOR)](OPTIONAL_LINK_URL)
```

**Badge URL encoding rules:**
- Spaces → `_` (shields.io uses underscores for spaces)
- Hyphens in label/message → `--` (shields.io escape for literal hyphen)
- Version numbers with dots are fine as-is

**Link URLs:**
- Version → GitHub release URL if repository field exists, otherwise no link
- License → `LICENSE` file in same directory
- Language → official language website
- Claude Code → `https://claude.ai/claude-code`
- GitHub Stars → `https://github.com/OWNER/REPO/stargazers`
- API badges → relevant API documentation URL

Arrange badges on a single line separated by newlines (one badge per line for clean diffs, but they render inline in markdown).

### Step 5: Insert or Replace in README

**If the README contains `<!-- badges-start -->` and `<!-- badges-end -->` markers:**
Replace everything between the markers (exclusive) with the generated badge lines.

**If the README does NOT have markers:**
Find the first `# ` heading line. Insert the badge block immediately after it, wrapped in markers:

```markdown
# Plugin Name

<!-- badges-start -->
[![Badge1](url1)](link1)
[![Badge2](url2)](link2)
<!-- badges-end -->
```

Leave one blank line before and after the badge block.

### Step 6: Report

After processing all plugins, report:
- Number of plugins updated
- For each plugin: which badges were added, updated, or unchanged
- Remind user to commit if changes were made

## Badge Color Reference

| Badge Type      | Color       | Example                                    |
|-----------------|-------------|--------------------------------------------|
| Version         | `blue`      | `version-1.0.0-blue`                       |
| License MIT     | `green`     | `license-MIT-green`                        |
| Python          | `yellow`    | `python-3.8+-yellow`                       |
| Node.js         | `339933`    | `node.js-18+-339933`                       |
| TypeScript      | `3178C6`    | `TypeScript-3178C6`                        |
| Claude Code     | `blueviolet`| `Claude_Code-plugin-blueviolet`            |
| Gemini API      | `orange`    | `powered_by-Gemini_API-orange`             |
| OpenAI          | `412991`    | `powered_by-OpenAI-412991`                 |
| Google Workspace| `4285F4`    | `Google_Workspace-4285F4`                  |
| GitHub Stars    | `yellow`    | Dynamic: `github/stars/OWNER/REPO`         |
| GitHub Issues   | `orange`    | Dynamic: `github/issues/OWNER/REPO`        |

## Example Output

```
Badges updated!

nano-banana-plugin:
  ✓ Version (1.0.0) - added
  ✓ License (MIT) - added
  ✓ Python 3.8+ - added
  ✓ Claude Code plugin - added
  ✓ Gemini API - added
  ✗ GitHub Stars - skipped (user declined)

Updated 1 plugin. Don't forget to commit!
```
