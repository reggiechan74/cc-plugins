# /update-spec Command Design

## Summary

Add a new `/update-spec` command to the structured-english plugin that upgrades existing SESF specifications from any previous format version (v1, v2, v3) to v4.

## Design Decisions

- **Separate command**: `/update-spec` is distinct from `/write-spec` (new specs) and `/assess-doc` (evaluate non-SESF docs). The upgrade workflow has different inputs, analysis, and output than authoring from scratch.
- **Any version to v4**: Auto-detect the source SESF format version and apply the appropriate migration path.
- **Overwrite in place**: Replace the original file. Git history preserves the original.
- **Format + suggestions**: Auto-apply format migrations. Flag v4 opportunities (potential @config, @route, $variable) as suggestions for user approval.
- **Detect + delegate**: The command handles version detection and migration analysis. The structured-english skill handles the actual rewrite, reusing its existing v4 knowledge.

## Command File

Path: `structured-english/commands/update-spec.md`

```yaml
---
description: Upgrade an existing SESF specification to the latest format version (v4)
argument-hint: <path to SESF spec file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---
```

## Workflow (6 Steps)

### Step 1: Load the Skill

Read the `structured-english` skill for v4 rules.

### Step 2: Read and Detect Version

Read the spec file. Detect the SESF format version using structural signals:

| Detection Signal | Inferred Format |
|-----------------|-----------------|
| Has @config, @route, or $variable threading | Already v4 — report "already current" and exit |
| Has PROCEDURE or ACTION blocks, no hybrid notation | v3 |
| Has BEHAVIOR blocks only, no PROCEDURE/ACTION, no hybrid notation | v1/v2 |
| No BEHAVIOR or PROCEDURE blocks found | Not an SESF spec — suggest `/write-spec` or `/assess-doc` instead |

Also detect the tier from the Meta section (micro/standard/complex) or infer from structure.

### Step 3: Analyze Gaps

Compare the spec against v4 requirements. Produce two lists:

**Format migrations** (will auto-apply):
- Missing Notation section (required for standard/complex)
- Section ordering doesn't match v4 order
- Verbose ERROR blocks → compact ERRORS tables
- Verbose EXAMPLE blocks → compact EXAMPLES format
- Meta date update
- `-- none` stubs for empty required sections

**v4 opportunity suggestions** (present for user approval):
- Repeated threshold/config values across behaviors → @config candidate
- IF/ELSE IF chains with 3+ branches → @route candidate
- PROCEDURE steps that pass results implicitly → $variable threading candidate
- v1/v2 specs with step-by-step concerns embedded in prose → PROCEDURE block candidate

### Step 4: Present Migration Report

Show the report to the user:

```
## Migration Report: <filename>

**Detected format**: SESF v3 (Standard tier)
**Target format**: SESF v4

### Format migrations (will apply automatically):
- Add Notation section after Meta
- Convert N verbose ERROR blocks → compact ERRORS tables
- Convert N verbose EXAMPLE blocks → compact EXAMPLES format
- Reorder sections to v4 order
- Update Meta date

### v4 opportunities (suggestions):
- @config candidate: <description>
- @route candidate: <description>
- $variable threading: <description>

Proceed with migration?
```

Use AskUserQuestion to confirm. If there are suggestions, ask which ones to include.

### Step 5: Delegate to Skill

Pass the original spec content plus the migration context (source version, confirmed migrations, accepted suggestions) to the structured-english skill. The skill rewrites the spec following its v4 rules.

### Step 6: Validate and Save

Run the SESF validator on the rewritten spec. Fix any failures. Overwrite the original file.

## Migration Rules by Source Version

### v1/v2 → v4

Format migrations:
- Add Notation section (Standard/Complex tiers)
- Reorder sections to v4 ordering
- Convert verbose ERROR blocks to compact 5-column ERRORS tables
- Convert verbose EXAMPLE blocks to compact `name: input -> expected` format
- Add `-- none` stubs for empty required sections
- Update Meta date to today

Suggestions:
- Consider adding PROCEDURE blocks for step-by-step concerns currently in prose
- Extract repeated values to @config
- Convert 3+ branch IF chains to @route tables
- Add $variable threading in any new PROCEDURE blocks

### v3 → v4

Format migrations:
- Add Notation section (Standard/Complex tiers)
- Convert verbose ERROR blocks to compact ERRORS tables
- Convert verbose EXAMPLE blocks to compact EXAMPLES format
- Ensure section ordering matches v4 order
- Update Meta date to today
- Add `-- none` stubs for empty required sections

Suggestions:
- Extract repeated values to @config
- Convert 3+ branch IF chains to @route tables
- Add $variable threading to existing PROCEDURE blocks

## Ancillary Changes

- **README.md**: Add `/update-spec` to the commands table
- **Root README.md**: Add `/update-spec` to the structured-english section
- **plugin.json**: Bump plugin version to 5.1.0 (new command)
- **marketplace.json**: Update structured-english version
