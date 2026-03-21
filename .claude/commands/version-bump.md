---
description: "Bump a plugin's version across plugin.json, README badge, marketplace.json, and CHANGELOG"
argument-hint: "<plugin-name> <new-version>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Version Bump

Bump a plugin's version consistently across all files that reference it.

**Arguments received:** $ARGUMENTS

## Instructions

### Step 1: Parse Arguments

Extract `<plugin-name>` and `<new-version>` from the arguments.

- If no arguments provided, ask: "Which plugin and what version? (e.g., `math-paper-creator 0.5.0`)"
- If only plugin name provided, read current version from its `plugin.json` and suggest the next minor bump. Ask user to confirm or specify a different version.
- Validate the version follows semver (X.Y.Z).

### Step 2: Locate Files

Find all files that need updating for the given plugin:

1. **Plugin manifest:** `<plugin-dir>/.claude-plugin/plugin.json` — the `"version"` field
2. **README badge:** `<plugin-dir>/README.md` — the shields.io version badge between `<!-- badges-start -->` and `<!-- badges-end -->`
3. **Marketplace registry:** `.claude-plugin/marketplace.json` — the `"version"` field for this plugin's entry
4. **Changelog:** `<plugin-dir>/CHANGELOG.md` — add a new `## [X.Y.Z] - YYYY-MM-DD` section

If any file doesn't exist, note it and skip (e.g., some plugins may not have a CHANGELOG).

### Step 3: Read Current State

Read each file and verify the current version. Report:

```
Current version: X.Y.Z
New version: A.B.C

Files to update:
  - <plugin-dir>/.claude-plugin/plugin.json
  - <plugin-dir>/README.md (badge)
  - .claude-plugin/marketplace.json
  - <plugin-dir>/CHANGELOG.md
```

### Step 4: Update Versions

Update each file:

1. **plugin.json:** Change `"version": "X.Y.Z"` to `"version": "A.B.C"`
2. **README.md:** Change `version-X.Y.Z-blue` to `version-A.B.C-blue` in the badge URL
3. **marketplace.json:** Change the version for this plugin's entry only (match by plugin name)
4. **CHANGELOG.md:** If it exists, insert a new section at the top (after the header):
   ```markdown
   ## [A.B.C] - YYYY-MM-DD

   ### Added
   -

   ### Changed
   -
   ```
   Leave the entries as placeholders for the user to fill in. If the user provided changelog notes in the arguments or conversation, populate them.

### Step 5: Commit and Push

```bash
git add <plugin-dir>/.claude-plugin/plugin.json <plugin-dir>/README.md .claude-plugin/marketplace.json <plugin-dir>/CHANGELOG.md
git commit -m "chore(<plugin-name>): bump version to A.B.C"
git push
```

### Step 6: Report

```
Version bumped: X.Y.Z → A.B.C

Updated files:
  ✓ <plugin-dir>/.claude-plugin/plugin.json
  ✓ <plugin-dir>/README.md (badge)
  ✓ .claude-plugin/marketplace.json
  ✓ <plugin-dir>/CHANGELOG.md

Committed and pushed.
```

## Execution

Now execute the version bump following the steps above.
