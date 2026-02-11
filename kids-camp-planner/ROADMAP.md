# Plan: Kids Camp Planner — Outstanding Feature Roadmap

## Context

After implementing the configurable research directory and two-file config architecture, an audit of all prior session transcripts identified 10 outstanding work items. Exploration confirmed that 2 of them (#7 provider template Manual/Computed split, #8 commute constraint filtering) are already implemented. The remaining 8 items are organized into 4 phases below.

**User decisions** (collected via AskUserQuestion):
- Calendar expansion: Tiers 1+2 (automate + populate 13 remaining public/Catholic boards)
- Multi-board families: Per-child school field, no limit on number of schools
- Max children: Up to 4, dynamic column layout in script + spreadsheet
- Rate tables: Per-period rate columns in Provider Comparison tab

---

## Phase 1: Calendar Parser Generalization

**Items**: #2 Good Friday/Easter Monday + #6 Fall Break Support
**Dependency**: None (foundational — Phases 2 and 3 depend on this)
**Core change**: Refactor `parse_calendar()` in `generate_annual_schedule.py` to parse ALL entries from the Holidays & Breaks table instead of only Christmas Break and March Break.

### Item 2: Good Friday / Easter Monday Coverage

**Problem**: `parse_calendar()` (line 120) only returns `pa_days`, `winter_break`, `march_break`. Single-day holidays (Good Friday, Easter Monday, Family Day, Thanksgiving, Victoria Day) are present in calendar markdown files but never parsed. These are school-off days requiring coverage.

**Files to modify (3)**:

| File | Change |
|------|--------|
| `skills/generate-annual-schedule/scripts/generate_annual_schedule.py` | Add `school_holidays` parsing to `parse_calendar()`; add school holiday block to `build_annual_days()` using `pa_provider`; add `"school_holiday"` to `_group_into_sections()`, `render_markdown()` summary, and `update_xlsx()` |
| `skills/generate-annual-schedule/SKILL.md` | Update "What the Script Reads" section; note `--pa-day-provider` also covers school holidays; update output description |
| `examples/sample-annual-schedule.md` | Add Thanksgiving, Family Day, Good Friday, Easter Monday, Victoria Day at chronological positions; update Annual Summary table with "School Holidays" row |

**Design**: Parse all rows from the Holidays & Breaks table. Single-day entries (`Weekdays Off` = 1) that fall during the school year (not summer) become `school_holiday` entries. Multi-day entries continue to be parsed as break periods. School holidays use `--pa-day-provider` since they're single-day coverage needs served by the same PA day program providers. Overrides JSON can still customize per-date, per-child.

**Filtering**: Exclude holidays during summer (Canada Day, Civic Holiday already handled by `get_summer_holidays()`), during winter break, or during March break to avoid double-counting. `seen_dates` set prevents duplicates with PA days.

### Item 6: Fall Break Support

**Problem**: GIST has fall break (Nov 3-7, 2025), KCS has midterm breaks. `parse_calendar()` does not parse these. No `--fall-break-provider` argument exists.

**Files to modify (2 — same files as Item 2, done together)**:

| File | Change |
|------|--------|
| `generate_annual_schedule.py` | Add `fall_break` parsing (match `\| Fall Break \|` and `\| Midterm [Bb]reak \|`); add `--fall-break-provider` arg (default: same as `--break-provider`); add fall break block to `build_annual_days()`; add to `_group_into_sections()`, `render_markdown()`, `update_xlsx()` |
| `skills/generate-annual-schedule/SKILL.md` | Add `--fall-break-provider` to args; update Step 2 defaults table; update output description |

**Design**: Fall break uses `--break-provider` by default (separate `--fall-break-provider` available). Output structure matches winter/March break. For calendars without fall breaks (e.g., TDSB), no section appears.

### Phase 1 Verification

- Run script with TCDSB calendar: should now produce Good Friday, Easter Monday, Family Day, Thanksgiving, Victoria Day sections
- Run script with GIST calendar: should also produce Fall Break section (Nov 3-7)
- Run with TDSB calendar: no fall break section
- Verify `seen_dates` prevents double-counting
- Verify existing summer holiday handling (`get_summer_holidays()`) still works
- Day count in Annual Summary should increase (currently 59 for TCDSB sample → ~64 with holidays)

---

## Phase 2: Multi-Board Family Support

**Item**: #3 Multi-Board Families
**Dependency**: Phase 1 (clean generalized parser)

**Problem**: Family profile has a single `school:` block. Script takes a single `--calendar` arg. Families with children at different schools (e.g., TDSB + GIST) can't represent this.

**Files to modify (7)**:

| File | Change |
|------|--------|
| `examples/family-profile.md` | Move `school:` under each child entry; keep top-level `school:` as deprecated fallback |
| `generate_annual_schedule.py` | Accept `--calendar CHILD:PATH` (multi) or `--calendar PATH` (single, backward compat); per-child calendar parsing; merge coverage dates; mark children "In school" when their school is in session |
| `skills/generate-annual-schedule/SKILL.md` | Document multi-calendar usage |
| `skills/setup/SKILL.md` | Collect school info per child in Step 2 Group 2; run 3-Tier Lookup per unique school |
| `skills/plan-pa-days/SKILL.md` | Per-child PA day lookup; highlight dates where only some children are off |
| `skills/plan-summer/SKILL.md` | Per-child summer window; overall window = union |
| `skills/plan-march-break/SKILL.md` | Handle different March break dates per child |

**Family profile schema change**:
```yaml
kids:
  - name: "Child 1"
    dob: "2017-05-15"
    school:
      type: "public"
      board: "TDSB"
      name: "Example Public School"
    interests: [...]
  - name: "Child 2"
    dob: "2019-09-20"
    school:
      type: "private"
      board: "TDSB"  # nearest public board
      name: "German International School Toronto"
      private_calendar_url: ""
      march_break_weeks: 2
    interests: [...]

# DEPRECATED — top-level school block (backward compat: used when no per-child school)
school:
  type: "public"
  board: "TDSB"
  name: "Example Public School"
```

**Script CLI change**: `--calendar` accepts either:
- `--calendar path/to/tcdsb.md` — applies to all children (backward compatible)
- `--calendar "Emma:path/to/tdsb.md" --calendar "Liam:path/to/gist.md"` — per-child

**Key logic**: On multi-board days where only some children are off, the others show "In school" with $0 cost. The merged calendar is the union of all children's off-school dates.

### Phase 2 Verification

- Two children at TDSB (identical calendars): output identical to current single-calendar
- One child TDSB + one GIST: GIST fall break shows only GIST child; misaligned PA days show correct children
- Single `--calendar` arg still works (backward compat)
- Setup skill collects school per child

---

## Phase 3: Spreadsheet Structural Changes

**Items**: #5 Up to 4 Children + #4 Per-Period Rates
**Dependency**: Phase 1 (for period types in rate lookup)

### Item 5: Up to 4 Children

**Problem**: `child_cols = [3, 9]` hardcoded at line 93. Hard error at line 763 for >2 children. Daily Schedule has fixed 16-column layout.

**Files to modify (3)**:

| File | Change |
|------|--------|
| `generate_annual_schedule.py` | Replace hardcoded `child_cols` with `SHARED_PREFIX_COLS=3, COLS_PER_CHILD=6` formula; remove max-2 check, add max-4 check; dynamic `max_col`, header generation, VLOOKUP formulas in `update_xlsx()` |
| `skills/generate-annual-schedule/SKILL.md` | Update column layout docs; remove "16 columns" references |
| `README.md` | Note up to 4 children supported |

**Column layout formula**: `total_cols = 3 + (N × 6) + 1` where N = child count.
- 2 children: 3 + 12 + 1 = 16 cols (A-P) — current
- 3 children: 3 + 18 + 1 = 22 cols (A-V)
- 4 children: 3 + 24 + 1 = 28 cols (A-AB)

Each child block: Camp Name, Before Care, Camp Fee, After Care, Lunch, Day Total (6 cols).

**`sample-budget.xlsx`**: Keep 2-child layout as-is. Script generates correct layout dynamically.

### Item 4: Per-Period Rate Differentiation

**Problem**: Provider Comparison has one rate set. All periods use summer rates. Disclaimer: "Non-summer rates are assumed equal to summer rates."

**Files to modify (5)**:

| File | Change |
|------|--------|
| `generate_annual_schedule.py` | Expand `read_provider_rates()` to read 3 rate sections (Summer cols C-F, PA Day cols G-J, Break cols K-N); return nested dict `{provider: {summer: {...}, pa_day: {...}, break: {...}}}`; fallback to summer if PA/break empty; pass period type to rate lookup in `build_annual_days()`; period-aware VLOOKUP column offsets in `update_xlsx()` |
| `examples/sample-budget.xlsx` | Add PA Day rate columns (G-J) and Break rate columns (K-N) to Provider Comparison tab; update VLOOKUP references |
| `skills/generate-annual-schedule/SKILL.md` | Update Provider Comparison column layout docs |
| `skills/budget-optimization/SKILL.md` | Reference per-period rates |
| `skills/research-camps/references/provider-template.md` | Add Summer/PA Day/Break rate sections to Costs table |

**Provider Comparison tab layout**:
```
A: Provider | B: Age Range | C-F: Summer (Daily, Before, After, Lunch) |
G-J: PA Day (Daily, Before, After, Lunch) | K-N: Break (Daily, Before, After, Lunch)
```

**Backward compat**: If PA Day/Break columns are empty or zero, fall back to Summer rates. Existing spreadsheets with only Summer rates continue to work.

**VLOOKUP approach**: Period label in column C (e.g., "Summer Wk 1", "PA Day", "Winter Break") determines which rate columns to reference. Use `IF`-based column index in VLOOKUP formula.

### Phase 3 Verification

- Existing 2-child sample-budget.xlsx: identical output (backward compat for both child count and rates)
- 3-child test: script generates 22-column Annual Schedule tab with correct VLOOKUPs
- Per-period rates: PA days show PA Day rates; breaks show Break rates; summer shows Summer rates
- Empty PA Day/Break rates: falls back to Summer rates

---

## Phase 4: Calendar Data Expansion

**Items**: #9 Scraping Script + #1 Populate Tiers 1+2 + #10 Contributing Guidelines
**Dependency**: None (can run in parallel with Phases 1-3)

### Item 9: Calendar Scraping Script

**Files to create (1)**:

| File | Purpose |
|------|---------|
| `skills/add-school-calendar/scripts/scrape_board_calendar.py` | Helper script: `--board-name`, `--abbreviation`, `--year`, `--url`; fetches HTML calendar page via `urllib.request`; outputs draft markdown in calendar-template format; targets common Ontario public board HTML table layouts |

**File to modify (1)**: `skills/add-school-calendar/SKILL.md` — document scraping script as optional Tier 3 accelerator.

**Realistic scope**: Handles HTML calendar pages (most boards publish these). PDF-only boards still use manual extraction via Claude Read tool. Script produces draft quality — human/agent review required.

### Item 1: Populate Tier 1+2 Calendars

**Files to create (12+)**:

Tier 1 (7 boards): `yrdsb.md`, `pdsb.md`, `ddsb.md`, `hdsb.md`, `ocdsb.md`, `dpcdsb.md`, `ycdsb.md`
Tier 2 (5 boards): `hwdsb.md`, `wrdsb.md`, `scdsb.md`, `tvdsb.md`, `ucdsb.md`

All in `skills/camp-planning/references/school-calendars/public-boards/`. Plus PDFs in `pdfs/[abbreviation]/` where available.

**Files to modify (3)**: `RESEARCH-PLAN.md` (status updates), `skills/camp-planning/SKILL.md` (reference list), `README.md` (Pre-Saved Calendar Data section)

**Execution**: For each board — web search → download PDF → extract data → create markdown → verify dates → update status. Use scraping script from Item 9 where HTML pages are available.

### Item 10: Contributing Guidelines

**Files to create (2)**:

| File | Purpose |
|------|---------|
| `CONTRIBUTING.md` | Submission format, PR workflow, quality checklist, link to calendar-template.md |
| `skills/add-school-calendar/scripts/validate_calendar.py` | Validates calendar markdown: required sections exist, dates parseable, correct school year, expected table columns, no date conflicts |

**File to modify (1)**: `README.md` — add Contributing section.

### Phase 4 Verification

- `scrape_board_calendar.py --help` shows expected arguments
- `validate_calendar.py` passes on existing TDSB/TCDSB files
- `validate_calendar.py` fails with clear errors on malformed input
- All 12 new board calendars pass validation
- RESEARCH-PLAN.md shows Tiers 1+2 complete

---

## Execution Order

```
Phase 1 ─────────────────────────> Phase 2 (Multi-Board)
  (Parser: holidays + fall break)     |
         |                            v
         └────────────────────────> Phase 3 (Children + Rates)

Phase 4 (Calendars) ──────────── runs independently / in parallel
```

**Recommended sequence**:
1. **Phase 1** first (foundational, unblocks 2 and 3)
2. **Phase 4** in parallel with Phase 1 (independent — data + docs work)
3. **Phase 2** after Phase 1 (schema change + multi-calendar merging)
4. **Phase 3** after Phase 1 (spreadsheet layout overhaul)

Phases 2 and 3 are independent of each other and can run in parallel.

---

## Risk Assessment

| Item | Risk | Mitigation |
|------|------|------------|
| #5 (4 children) | Column layout change breaks existing spreadsheets | Script regenerates tabs dynamically; document migration; keep sample at 2 children |
| #3 (Multi-board) | Complex edge cases in calendar merging | Test matrix: TDSB+TDSB, TDSB+TCDSB, TDSB+GIST |
| #4 (Per-period rates) | Complex VLOOKUP formulas with IF nesting | Generate formulas programmatically in Python |
| #1 (12 boards) | Board websites vary; data accuracy | Use official sources only; validate with script |
| #2, #6 | Low risk — targeted parser extensions | |

---

## Summary

| Phase | Items | New Files | Modified Files | Complexity |
|-------|-------|-----------|----------------|------------|
| 1 | #2 + #6 | 0 | 3 | Medium |
| 2 | #3 | 0 | 7 | High |
| 3 | #5 + #4 | 0 | 7 | High |
| 4 | #9 + #1 + #10 | 16+ | 5 | Medium (data-heavy) |
| **Total** | **8 items** | **16+** | **14 unique** | |

Central script `generate_annual_schedule.py` is touched by 5 of 8 items (all in Phases 1-3). The family profile schema changes (Phase 2) propagate to setup + 3 planning skills.
