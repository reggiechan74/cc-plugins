# Kids Camp Planner — Plugin Improvements Design

**Date:** 2026-03-16
**Status:** Approved
**Scope:** Fix all issues identified in the plugin review

## Summary

Address 14 review findings across three waves: compliance & quick fixes, code robustness, and plugin UX. Each wave is independently shippable. The work brings the plugin to production quality with proper test coverage, robust YAML parsing, discoverable commands, and standards compliance.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| YAML parsing | Require `pyyaml`, replace all regex | Plugin already requires `openpyxl`; family profile YAML is too complex for regex |
| Slash commands | Curated 6 commands | Maps to actual user journey; avoids namespace clutter from 11 commands |
| Calendar staleness | Soft warning + offer to update | Low implementation effort; leverages existing 3-tier lookup |
| Test coverage | Full test suites for all 4 scripts | Comprehensive coverage including edge cases, mock API calls |
| Implementation order | Three waves (compliance → robustness → UX) | Risk-ordered; each wave independently shippable |

---

## Wave 1: Compliance & Quick Fixes

**Items:** README badges, plugin.json metadata, doc inconsistencies, agent descriptions

### 1.1 Add README Badges

Run `/update-badges` to add shields.io badges inside `<!-- badges-start -->` / `<!-- badges-end -->` markers immediately after the `# Kids Camp Planner` heading. Minimum badges: version, license, Claude Code plugin.

### 1.2 Add `homepage` and `repository` to plugin.json

Add fields to `.claude-plugin/plugin.json`:

```json
{
  "homepage": "https://github.com/reggiechan74/cc-plugins/tree/main/kids-camp-planner",
  "repository": "https://github.com/reggiechan74/cc-plugins"
}
```

### 1.3 Fix README Board Count and Abbreviation List

Update line referencing "12+ Ontario public school boards" to "14 Ontario public school boards." Also reconcile the listed abbreviations with actual files on disk.

**Actual files in `public-boards/`:** DDSB, DPCDSB, HDSB, HWDSB, OCDSB, PDSB, SCDSB, TCDSB, TDSB, TVDSB, UCDSB, WRDSB, YCDSB, YRDSB (14 boards).

The current README lists "TDSB, TCDSB, PDSB, DDSB, HDSB, YRDSB, YCDSB, OCSB, OCDSB, WRDSB, WCDSB, HWDSB" — OCSB and WCDSB do not have files; SCDSB, TVDSB, UCDSB, and DPCDSB are missing from the list. Replace with the accurate list.

### 1.4 Fix Script Documentation

The README lists "Python Scripts (4)" but ships with additional helper scripts and tests. Add subsections:

- **Helper Scripts (2):** `scrape_board_calendar.py` (draft quality — output requires manual review), `validate_calendar.py`
- **Tests (1):** `test_generate_annual_schedule.py`

### 1.5 Shorten Agent Description Fields

Move `<example>` blocks from the `description` frontmatter field into the system prompt body (below the `---` delimiter) for both agents.

**camp-researcher.md** — description becomes:
> Use this agent when the user needs to find, compare, or evaluate camp options for their children. Triggers proactively when camp research is needed.

**schedule-optimizer.md** — description becomes:
> Use this agent when the user has camp options researched and needs to build or optimize a schedule that balances coverage, budget, logistics, and preferences.

All example content is preserved, just moved below the frontmatter.

---

## Wave 2: Code Robustness

**Items:** pyyaml migration, test suites, tax estimates, lazy imports, scraper caveat, staleness detection

### 2.1 Replace Regex YAML Parsing with `pyyaml`

**Affected file:**
- `commute_calculator.py` — `parse_profile()` function (lines 50-107)

Note: `generate_annual_schedule.py` has no YAML parsing — it reads `.xlsx` and markdown calendar files only. No changes needed there for this item.

**Approach:**
- Read file, split on `---` markers, `yaml.safe_load()` the frontmatter block
- Navigate the resulting dict to extract fields. The `parents` block is a nested list-of-dicts (`data["parents"]` → `[{"name": ..., "work_address": ...}, ...]`) that needs careful key mapping to maintain the same return signature.
- Keep the same return signature from `parse_profile()` (`dict` with `home_address`, `work_addresses`, `api_key`, `max_commute`) so callers don't change
- Add `pyyaml` to prerequisites in README alongside `openpyxl`

### 2.2 Full Test Suites

All tests use `pytest`. API-calling functions mocked via `unittest.mock.patch` on `urllib.request.urlopen`. File-dependent tests use `tmp_path` fixture. No real network calls.

#### `test_budget_calculator.py`
Location: `skills/budget-optimization/scripts/`

Coverage:
- Simple mode: weekly rates, daily rates, mixed flags
- Sibling discount calculations (0%, 10%, edge: 100%)
- Early bird and multi-week discount stacking
- JSON input: weekly format, daily format
- Edge cases: 1 child, 4 children, 0 weeks/days, negative values
- CSV and markdown output rendering
- Tax estimate output (verify formula, not policy correctness)
- Budget limit over/under reporting

#### `test_summer_dates.py`
Location: `skills/plan-summer/scripts/`

Coverage:
- Labour Day calculation for multiple years (2025-2030)
- Leap year handling (2028)
- Partial first/last weeks
- Exclusion date subtraction
- Day-by-day output with week numbering
- Edge: last school day on a Friday vs Thursday
- Edge: first fall day before Labour Day (private schools)
- All 3 output formats (text, json, markdown)

#### `test_commute_calculator.py`
Location: `skills/commute-matrix/scripts/`

Coverage:
- `parse_profile()` with pyyaml (various profile shapes)
- `scan_providers()` with mock provider files
- `normalize_address()` edge cases
- `geocode()` with cache hit, cache miss (mock API), API failure
- `route_matrix()` response parsing (mock API)
- `compute_chains()` math: AM chain = home->camp + camp->work, PM chain = work->camp + camp->home
- `update_provider_files()` section replacement (Manual/Computed split)
- `render_markdown()` and `render_json()` output structure
- Constraint violation detection (exceeds max commute)
- Geocache load/save round-trip

#### `test_scrape_board_calendar.py`
Location: `skills/add-school-calendar/scripts/`

Import functions via `sys.path.insert(0, os.path.dirname(__file__))` + `from scrape_board_calendar import TableExtractor, fetch_and_extract, generate_draft`.

Coverage:
- `TableExtractor` (HTMLParser subclass) — feed it HTML strings directly: simple table, nested tags, empty cells, multiple tables on one page
- `generate_draft()` output structure: correct `# Board Name (ABBR)` header, `## YYYY-YYYY School Year` section, all extracted tables rendered as markdown, TODO placeholders present
- `fetch_and_extract()` with mocked `urllib.request.urlopen` — verify it calls `TableExtractor` and returns `(tables, html)`
- Malformed HTML handling: unclosed tags, no tables found (returns empty list)
- Edge: non-UTF8 encoding in response body

### 2.3 Make Tax Estimates Configurable

In `budget_calculator.py`:
- Add CLI args: `--tax-deduction-limit` (default: 8000), `--tax-marginal-rate` (default: 0.25)
- Add JSON input fields: `tax_deduction_limit`, `tax_marginal_rate` with same defaults
- **Reconcile the two tax formulas:** `render_markdown_simple()` (line 515) uses age-conditional logic (`8000 if age < 7 else 5000`), while `render_markdown_detailed()` (line 600) uses a flat `min(total, 5000)`. Unify both to use the `--tax-deduction-limit` value. Drop the age-conditional logic — it's based on outdated CRA rules and the user can override the limit per run. Both renderers should use `min(total, tax_deduction_limit) * tax_marginal_rate`.
- Add disclaimer to tax recovery section output: *"Estimates only — consult a tax professional. Based on CRA child care expense deduction (Line 21400). Limits and rates may change."*

### 2.4 Lazy-Import `openpyxl`

In `generate_annual_schedule.py`:
- Remove top-level `import openpyxl`
- Move import inside `update_xlsx()` and any other functions that need it
- Wrap in try/except: `"openpyxl is required for Excel output. Install with: pip install openpyxl"`
- Non-xlsx functionality (markdown output, calendar parsing) works without openpyxl

### 2.5 Add Scraper Caveat to README

In the README components section, note that `scrape_board_calendar.py` is draft quality: "Helper script (draft quality) — output requires manual review and reorganization into standard calendar format."

### 2.6 School Calendar Staleness Detection

**Logic:** Extract school year from `## YYYY-YYYY School Year` header. Parse the end year. If current date is after September 1 of the end year, the calendar is stale.

**Warning message:** *"Calendar data for [board] is from [year]. The current year may have different PA days and breaks. Would you like to search for updated calendar data?"*

**Where it's called:** In skill instructions for `plan-summer`, `plan-march-break`, `plan-pa-days`, and `generate-annual-schedule`.

**Insertion point in each SKILL.md:** Add immediately after the step that loads/reads calendar data (e.g., after "Read the calendar data from..." or after the 3-Tier lookup completes). The new step reads:

> **Check calendar staleness:** After loading calendar data, extract the school year from the `## YYYY-YYYY School Year` header. Parse the end year (e.g., 2026 from "2025-2026"). If the current date is after September 1 of that end year, warn: *"Calendar data for [board] is from [year]. The current year may have different PA days and breaks. Would you like to search for updated calendar data?"* If the user says yes, run the 3-Tier School Calendar Lookup to find updated data.

**Special case — `generate-annual-schedule`:** This skill passes the calendar as a `--calendar` CLI argument rather than having an explicit "load calendar data" step. For this skill, insert the staleness check *before* the script invocation step: "Before running the script, read the calendar file header and check for staleness as described above."

**Implementation:** Documented as instruction text in each skill. Not a shared Python module — skills instruct Claude to perform the check inline.

---

## Wave 3: Plugin UX

**Items:** slash commands, fast-path setup, module split

### 3.1 Add 6 Slash Commands

Create `commands/` directory with one markdown file per command using Claude Code command frontmatter.

**File naming:** `commands/camp-setup.md`, `commands/camp-research.md`, etc.

| Command | File | Skill/Agent | Arguments |
|---------|------|-------------|-----------|
| `/camp-setup` | `camp-setup.md` | setup skill | none |
| `/camp-research` | `camp-research.md` | camp-researcher agent / research-camps skill | optional: search focus |
| `/camp-plan` | `camp-plan.md` | plan-summer, plan-march-break, or plan-pa-days | optional: `summer`, `march-break`, `pa-days` |
| `/camp-budget` | `camp-budget.md` | budget-optimization skill | optional: period |
| `/camp-email` | `camp-email.md` | draft-email skill | optional: type and provider |
| `/camp-schedule` | `camp-schedule.md` | generate-annual-schedule skill | none |

**Example command file (`commands/camp-setup.md`):**

```markdown
---
name: camp-setup
description: Initialize the kids-camp-planner workspace and family profile
arguments:
  - name: directory
    description: Research directory name (default: camp-research)
    required: false
---

Read `.claude/kids-camp-planner.local.md` to check for existing configuration.
Read the family profile at `<research_dir>/family-profile.md` if it exists.

Then follow the setup skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/setup/SKILL.md`.

If a research directory argument was provided, use it as the directory name instead of asking.
```

Each command follows this pattern: read thin config, load family profile if it exists, then delegate to the corresponding skill's workflow. The command prompt provides the glue; the skill SKILL.md provides the detailed workflow steps.

### 3.2 Fast-Path Setup

Modify `skills/setup/SKILL.md` to detect pre-filled profiles:

1. Check if `<research_dir>/family-profile.md` exists with substantive content (not just template)
2. If yes: parse profile, present summary, ask "Does this look correct, or would you like to update specific fields?"
3. If user confirms: skip to Step 3 (API keys) and Step 4 (summary)
4. If user wants changes: ask which group to update, only collect that group's data

This enhances the existing re-running setup section (which already checks for existing config) by making the "update" path group-selective.

### 3.3 Split `generate_annual_schedule.py` into Modules

Current: 1,369 lines, single file.

Proposed structure with full function allocation:

```
skills/generate-annual-schedule/scripts/
├── generate_annual_schedule.py    # CLI entry point: main(), argument parsing,
│                                  # orchestration (~200 lines)
├── calendar_parser.py             # parse_calendar(), parse_date_flexible(),
│                                  # get_summer_holidays(), find_civic_holiday(),
│                                  # get_weekdays_between(), resolve_calendars()
│                                  # (~250 lines)
├── rate_resolver.py               # resolve_period_rate(), _read_rate_block(),
│                                  # _resolve_assignments() (~90 lines)
├── schedule_builder.py            # build_annual_days(), build_annual_days_multi()
│                                  # (~400 lines)
├── xlsx_handler.py                # read_provider_rates(), read_summer_assignments(),
│                                  # update_xlsx(), _vlookup_col_indices(),
│                                  # calculate_total_cols(), get_child_col_offsets(),
│                                  # validate_child_count()
│                                  # — lazy-imports openpyxl (~300 lines)
├── renderer.py                    # render_markdown(), _group_into_sections()
│                                  # (~340 lines)
└── test_generate_annual_schedule.py  # existing tests — update imports
```

Note: `read_provider_rates()` depends on openpyxl so it lives in `xlsx_handler.py`, not `rate_resolver.py`. `_group_into_sections()` is called by `render_markdown()` so it lives in `renderer.py`. `rate_resolver.py` is intentionally small — it contains only the pure logic for interpreting rate data after it has been read.

**Key decisions:**
- `generate_annual_schedule.py` remains the CLI entry point — existing `python3 path/to/generate_annual_schedule.py` invocations don't break
- Each module has a single responsibility
- `xlsx_handler.py` contains the lazy openpyxl import (from 2.4)
- Existing test file updates imports but test logic is unchanged — validates the refactor
- **Import strategy:** Use `sys.path` insertion in the entry point (`sys.path.insert(0, os.path.dirname(__file__))`) then absolute imports (`from calendar_parser import parse_calendar`). This matches the pattern already used in `test_generate_annual_schedule.py` (line 14) and works with direct `python3` invocation. No `__init__.py` or `-m` flag needed.

---

## Version Bumps

| Wave | Version | Commit scope |
|------|---------|-------------|
| Wave 1 | 0.1.1 | Compliance and doc fixes |
| Wave 2 | 0.2.0 | New dependency (pyyaml), test suites, code changes |
| Wave 3 | 0.3.0 | New commands, setup UX, module refactor |

## Out of Scope

- Roadmap items from ROADMAP.md (Phase 1-4 features like Easter coverage, fall break support, 4-child dynamic columns)
- New school calendar data
- Google Calendar MCP integration
- Any changes to the existing test file (`test_generate_annual_schedule.py`) beyond import path updates
