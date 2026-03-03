# /update-spec Command Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a `/update-spec` command that upgrades existing SESF specs from any previous format version to v4.

**Architecture:** A single command file (`update-spec.md`) handles version detection and migration analysis, then delegates the actual rewrite to the `structured-english` skill. Ancillary updates to README, plugin.json, marketplace.json, and root README.

**Tech Stack:** Markdown command file, Python validator (existing), shell commands for validation.

---

### Task 1: Create the /update-spec command file

**Files:**
- Create: `structured-english/commands/update-spec.md`
- Reference: `structured-english/commands/write-spec.md` (pattern to follow)
- Reference: `structured-english/commands/assess-doc.md` (pattern to follow)

**Step 1: Write the command file**

Create `structured-english/commands/update-spec.md` with this exact content:

```markdown
---
description: Upgrade an existing SESF specification to the latest format version (v4)
argument-hint: <path to SESF spec file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Upgrade a Specification to SESF v4

Upgrade an existing SESF specification from any previous format version (v1, v2, v3) to the latest format (v4). Preserves the spec's domain logic while migrating notation, section structure, and compact formats.

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for SESF v4 specifications. Read it fully before proceeding.

Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md` for the complete v4 syntax.

### Step 2: Read and Detect Version

If the user provided a file path in the arguments, read it. Otherwise, ask:

- "Which SESF specification file should I upgrade?"

Read the full file content. Then detect the SESF format version using structural signals:

| Signal | Inferred Format |
|--------|-----------------|
| Has @config, @route, or $variable threading ($ prefixed variables in STEP declarations) | Already v4 |
| Has PROCEDURE or ACTION blocks, but no @config/@route/$variable threading | v3 |
| Has BEHAVIOR blocks only, no PROCEDURE/ACTION blocks, no hybrid notation | v1/v2 |
| No BEHAVIOR or PROCEDURE blocks found | Not an SESF spec |

**If already v4**: Report "This spec is already in SESF v4 format. No migration needed." and stop.

**If not an SESF spec**: Report "This file doesn't appear to be an SESF specification. Use `/write-spec` to create a new spec, or `/assess-doc` to evaluate whether this document would benefit from SESF conversion." and stop.

Also detect the tier from the Meta section (`Tier:` field) or infer it:
- 1 BEHAVIOR or 1 PROCEDURE → micro
- Multiple BEHAVIORs/PROCEDUREs or shared Types → standard
- PRECEDENCE block or State/Flow → complex

### Step 3: Analyze Gaps

Compare the spec against SESF v4 requirements. Build two lists:

**Format migrations** (will apply automatically):

For all source versions:
- Section ordering: check against v4 order (Meta, Notation, Purpose, Audience, Scope, Inputs, Outputs, @config, Types, Functions, Behaviors/Procedures, Constraints, Precedence, Dependencies, Changelog)
- Verbose ERROR blocks → compact ERRORS: tables (5 columns: name, when, severity, action, message)
- Verbose EXAMPLE blocks → compact EXAMPLES: format (name: input -> expected)
- Meta date → update to today's date
- Empty required sections → add `-- none` stubs

For standard/complex tiers:
- Missing Notation section → add after Meta with standard symbol definitions ($, @, ->, MUST/SHOULD/MAY/CAN)

For v1/v2 only:
- Missing required sections for the tier → add with appropriate content or `-- none` stubs

**v4 opportunity suggestions** (present for user approval):

Scan the spec content and flag:
- **@config candidates**: Look for numeric literals, string constants, or list values that appear in 2+ different rules or behaviors. These are candidates for extraction to a centralized @config block.
- **@route candidates**: Look for IF/ELSE IF chains or WHEN/THEN/ELSE WHEN chains with 3 or more branches on the same subject. These are candidates for @route decision tables.
- **$variable threading candidates**: In PROCEDURE blocks, look for steps that describe producing a result used by later steps without explicit $variable declarations. These are candidates for -> $var syntax.
- **PROCEDURE candidates** (v1/v2 only): Look for step-by-step instructions or workflow descriptions within BEHAVIOR blocks or prose sections that would be better expressed as PROCEDURE blocks.

### Step 4: Present Migration Report

Present the analysis to the user:

```
## Migration Report: <filename>

**Detected format**: SESF <version> (<tier> tier)
**Target format**: SESF v4

### Format migrations (will apply automatically):
- <list each format change>

### v4 opportunities (suggestions):
- <list each suggestion with specific evidence from the spec>
```

If there are no suggestions, omit the suggestions section.

Use `AskUserQuestion` to ask the user to confirm and, if there are suggestions, which ones to include:

- "Proceed with the migration? If there are suggestions listed above, which would you like me to include?"

Options:
- "Migrate format only" — apply only the automatic format migrations
- "Migrate format + all suggestions" — apply format migrations and all suggested v4 enhancements
- "Migrate format + selected suggestions" — let me choose which suggestions to include
- "Cancel" — do not modify the file

If the user selects specific suggestions, ask which ones to include.

### Step 5: Rewrite the Specification

Using the `structured-english` skill's v4 rules, rewrite the specification:

1. Read the template at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/template.md` for the target tier
2. Read the examples at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/references/examples.md` for reference
3. Preserve ALL domain logic — rules, conditions, error handling, examples — from the original spec
4. Apply the confirmed format migrations
5. Apply any accepted v4 opportunity suggestions
6. Follow v4 section ordering, compact table formats, and notation conventions
7. Write in natural English throughout

**Critical**: The rewrite MUST preserve the spec's domain content. Do not add new rules, remove existing rules, or change the behavior of existing logic. Only change the format and notation.

### Step 6: Validate and Save

Run the structural validator:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/structured-english/scripts/validate_sesf.py <output-file>
```

Fix any failures. Warnings about example count are acceptable.

Overwrite the original file with the upgraded spec.

Report the result:

```
Upgrade complete: <filename>
- Format: SESF <old_version> → SESF v4
- Tier: <tier>
- Validation: <N> passed, <N> warnings, 0 failures
- Suggestions applied: <list or "none">
```
```

**Step 2: Verify the file was created**

Run: `ls -la structured-english/commands/update-spec.md`
Expected: File exists with ~180 lines

**Step 3: Commit**

```bash
git add structured-english/commands/update-spec.md
git commit -m "feat(structured-english): add /update-spec command for version migration"
```

---

### Task 2: Update the plugin README

**Files:**
- Modify: `structured-english/README.md:39-43` (slash commands section)
- Modify: `structured-english/README.md:56-62` (What's included table)

**Step 1: Add /update-spec to the slash commands section**

In `structured-english/README.md`, find the slash commands block (around line 39-43):

```
/write-spec payment webhook handler
/write-spec email classification agent
/assess-doc path/to/existing-document.md
```

Add after the last line:

```
/update-spec path/to/old-v2-spec.md
```

**Step 2: Update the What's included table**

In `structured-english/README.md`, find the Commands row in the What's included table (around line 59):

```
| **Commands** | `/write-spec` -- guided specification creation workflow; `/assess-doc` -- evaluate whether an existing document would benefit from SESF conversion |
```

Replace with:

```
| **Commands** | `/write-spec` -- guided specification creation workflow; `/assess-doc` -- evaluate whether an existing document would benefit from SESF conversion; `/update-spec` -- upgrade an existing SESF spec from any previous version to v4 |
```

**Step 3: Verify the changes look correct**

Read the modified sections to confirm formatting.

**Step 4: Commit**

```bash
git add structured-english/README.md
git commit -m "docs(structured-english): add /update-spec to README"
```

---

### Task 3: Bump plugin version and update marketplace

**Files:**
- Modify: `structured-english/.claude-plugin/plugin.json` (version 5.0.0 → 5.1.0)
- Modify: `.claude-plugin/marketplace.json` (structured-english version 5.0.0 → 5.1.0)

**Step 1: Bump plugin.json version**

In `structured-english/.claude-plugin/plugin.json`, change:

```json
"version": "5.0.0",
```

to:

```json
"version": "5.1.0",
```

**Step 2: Update marketplace.json**

In `.claude-plugin/marketplace.json`, find the structured-english entry and change:

```json
"version": "5.0.0"
```

to:

```json
"version": "5.1.0"
```

**Step 3: Commit**

```bash
git add structured-english/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore(structured-english): bump plugin version to 5.1.0"
```

---

### Task 4: Update root README

**Files:**
- Modify: `README.md:349-351` (structured-english commands section)

**Step 1: Add /update-spec to the root README commands list**

In `README.md`, find the structured-english Commands section (around line 349-351):

```markdown
**Commands:**
- `/write-spec <domain>` - Guided SESF specification creation with block type selection, authoring, and validation
- `/assess-doc <path>` - Evaluate whether a document would benefit from SESF conversion
```

Add after the last command:

```markdown
- `/update-spec <path>` - Upgrade an existing SESF spec from any previous version to v4
```

**Step 2: Update the plugin badge count if needed**

Check the badge at the top of README.md — it should show the correct plugin count (13). No change needed unless the count is wrong.

**Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add /update-spec to root README"
```

---

### Task 5: Update plugin README badges

**Files:**
- Modify: `structured-english/README.md:4` (plugin badge version)

**Step 1: Update the plugin version badge**

In `structured-english/README.md`, change:

```markdown
[![Plugin](https://img.shields.io/badge/plugin-v5.0.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
```

to:

```markdown
[![Plugin](https://img.shields.io/badge/plugin-v5.1.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/structured-english)
```

The SESF badge stays at v4.0.0 since the format itself hasn't changed.

**Step 2: Commit**

```bash
git add structured-english/README.md
git commit -m "chore(structured-english): update plugin badge to v5.1.0"
```

---

### Task 6: Push to remote

**Step 1: Push all commits**

```bash
git push
```

Expected: All 5 commits pushed to origin/main.
