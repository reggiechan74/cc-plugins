# Kids Camp Planner — Plugin Improvements Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address all 14 review findings to bring the kids-camp-planner plugin to production quality.

**Architecture:** Three sequential waves (compliance → robustness → UX), each independently shippable with its own version bump. Wave 1 is doc-only. Wave 2 adds pyyaml dependency, test suites, and code fixes. Wave 3 adds commands, setup UX, and refactors the largest script into modules.

**Tech Stack:** Python 3, pytest, pyyaml, openpyxl (lazy), Claude Code plugin conventions (commands, skills, agents)

**Spec:** `kids-camp-planner/specs/2026-03-16-plugin-improvements-design.md`

---

## Chunk 1: Wave 1 — Compliance & Quick Fixes

### Task 1: Add README badges

**Files:**
- Modify: `kids-camp-planner/README.md` (line 1, after heading)

- [ ] **Step 1: Add badge markers and badges to README**

Insert immediately after the `# Kids Camp Planner` heading (line 1):

```markdown
<!-- badges-start -->
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/reggiechan74/cc-plugins/tree/main/kids-camp-planner)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](https://docs.anthropic.com/en/docs/claude-code)
<!-- badges-end -->
```

- [ ] **Step 2: Verify badges render correctly**

Visually inspect the README and confirm the badge markers are present and the markdown is valid.

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/README.md
git commit -m "chore(kids-camp-planner): add shields.io badges to README"
```

---

### Task 2: Add homepage and repository to plugin.json

**Files:**
- Modify: `kids-camp-planner/.claude-plugin/plugin.json`

- [ ] **Step 1: Add fields to plugin.json**

Add `homepage` and `repository` fields to the existing JSON object:

```json
{
  "name": "kids-camp-planner",
  "version": "0.1.0",
  "description": "Plan and book kids' summer camps, March break programs, and PA day coverage with budget tracking, schedule optimization, and provider research for Ontario families",
  "author": {
    "name": "Reggie Chan"
  },
  "homepage": "https://github.com/reggiechan74/cc-plugins/tree/main/kids-camp-planner",
  "repository": "https://github.com/reggiechan74/cc-plugins",
  "keywords": [
    "kids",
    "camp",
    "summer-camp",
    "march-break",
    "pa-days",
    "childcare",
    "planning",
    "budget",
    "ontario",
    "school",
    "scheduling"
  ],
  "license": "MIT"
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('kids-camp-planner/.claude-plugin/plugin.json'))"`
Expected: No output (valid JSON)

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/.claude-plugin/plugin.json
git commit -m "chore(kids-camp-planner): add homepage and repository to plugin.json"
```

---

### Task 3: Fix README board count and abbreviation list

**Files:**
- Modify: `kids-camp-planner/README.md` (lines 230-231)

- [ ] **Step 1: Update board count and abbreviation list**

Find the line containing "12+ Ontario public school boards" (around line 230) and replace:

Old: `Ships with calendar data for 12+ Ontario public school boards (TDSB, TCDSB, PDSB, DDSB, HDSB, YRDSB, YCDSB, OCSB, OCDSB, WRDSB, WCDSB, HWDSB) plus private schools (GIST, KCS)`

New: `Ships with calendar data for 14 Ontario public school boards (DDSB, DPCDSB, HDSB, HWDSB, OCDSB, PDSB, SCDSB, TCDSB, TDSB, TVDSB, UCDSB, WRDSB, YCDSB, YRDSB) plus private schools (GIST, KCS)`

Also update the Key Features section (line 18) which says "Pre-Saved Calendars: Ships with TDSB, TCDSB, GIST, and KCS calendar data; extensible to other Ontario schools". Replace with: "Pre-Saved Calendars: Ships with 14 Ontario public board calendars plus GIST and KCS private school data; extensible to other Ontario schools"

- [ ] **Step 2: Verify count matches files on disk**

Run: `ls kids-camp-planner/skills/camp-planning/references/school-calendars/public-boards/*.md | wc -l`
Expected: `14`

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/README.md
git commit -m "fix(kids-camp-planner): correct board count and abbreviation list in README"
```

---

### Task 4: Fix script documentation in README

**Files:**
- Modify: `kids-camp-planner/README.md` (around lines 121-129)

- [ ] **Step 1: Add helper scripts and tests subsections**

Find the `### Python Scripts (4)` section (around line 121). After the existing 4-script table, add:

```markdown
### Helper Scripts (2)

| Script | Purpose |
|--------|---------|
| `scrape_board_calendar.py` | HTML calendar page scraper (draft quality — output requires manual review and reorganization) |
| `validate_calendar.py` | Calendar markdown validation |

### Tests (1)

| File | Purpose |
|------|---------|
| `test_generate_annual_schedule.py` | Pytest suite for annual schedule generation |
```

- [ ] **Step 2: Commit**

```bash
git add kids-camp-planner/README.md
git commit -m "docs(kids-camp-planner): add helper scripts and tests to README"
```

---

### Task 5: Shorten agent description fields

**Files:**
- Modify: `kids-camp-planner/agents/camp-researcher.md`
- Modify: `kids-camp-planner/agents/schedule-optimizer.md`

- [ ] **Step 1: Refactor camp-researcher.md frontmatter**

Replace the `description` field in the frontmatter (everything between the `---` delimiters) with a concise 1-2 sentence description. Move the `<example>` blocks below the closing `---` into the system prompt body.

New frontmatter `description` field:
```
description: Use this agent when the user needs to find, compare, or evaluate camp options for their children. Triggers proactively when camp research is needed.
```

Move the three `<example>` blocks (starting at "Context: User is planning summer camps") to immediately below the closing `---` delimiter, before the "You are a camp research specialist" paragraph. Wrap them in a section header:

```markdown
## Triggering Examples

<example>
Context: User is planning summer camps and mentions needing to find options
...
</example>
```

- [ ] **Step 2: Refactor schedule-optimizer.md frontmatter**

Same pattern. New frontmatter `description` field:
```
description: Use this agent when the user has camp options researched and needs to build or optimize a schedule that balances coverage, budget, logistics, and preferences.
```

Move the three `<example>` blocks below the closing `---` with the same `## Triggering Examples` header.

- [ ] **Step 3: Verify frontmatter is valid YAML**

Check that both files have valid frontmatter by confirming the `---` delimiters are intact and the description field is a single string (not a multi-line block with `<example>` tags).

- [ ] **Step 4: Commit**

```bash
git add kids-camp-planner/agents/camp-researcher.md kids-camp-planner/agents/schedule-optimizer.md
git commit -m "refactor(kids-camp-planner): shorten agent description fields, move examples to body"
```

---

### Task 6: Version bump to 0.1.1

**Files:**
- Modify: `kids-camp-planner/.claude-plugin/plugin.json`
- Modify: `kids-camp-planner/README.md` (badge version)

- [ ] **Step 1: Update version in plugin.json**

Change `"version": "0.1.0"` to `"version": "0.1.1"`.

- [ ] **Step 2: Update version badge in README**

Change the version badge URL from `version-0.1.0-blue` to `version-0.1.1-blue`.

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/.claude-plugin/plugin.json kids-camp-planner/README.md
git commit -m "chore(kids-camp-planner): bump version to 0.1.1"
```

---

## Chunk 2: Wave 2 — Code Robustness (Part 1: pyyaml migration + budget calculator tests)

### Task 7: Replace regex YAML parsing with pyyaml in commute_calculator.py

**Files:**
- Modify: `kids-camp-planner/skills/commute-matrix/scripts/commute_calculator.py` (lines 50-107)
- Modify: `kids-camp-planner/README.md` (prerequisites section)

- [ ] **Step 1: Write failing test for parse_profile with pyyaml**

Create `kids-camp-planner/skills/commute-matrix/scripts/test_commute_calculator.py` with the first test:

```python
"""Tests for commute_calculator.py."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from commute_calculator import parse_profile


class TestParseProfile:
    """Tests for parse_profile() with pyyaml-based parsing."""

    def test_basic_profile(self, tmp_path):
        """Parse a minimal family profile with home address and one parent."""
        profile = tmp_path / "family-profile.md"
        profile.write_text(
            "---\n"
            'home_address: "123 Main St, Toronto, ON"\n'
            "max_commute_minutes: 30\n"
            "parents:\n"
            '  - name: "Alice"\n'
            '    work_address: "456 Bay St, Toronto, ON"\n'
            "---\n"
            "# Family Notes\n"
        )
        result = parse_profile(str(profile))
        assert result["home_address"] == "123 Main St, Toronto, ON"
        assert result["max_commute"] == 30
        assert len(result["work_addresses"]) == 1
        assert result["work_addresses"][0]["name"] == "Alice"
        assert result["work_addresses"][0]["address"] == "456 Bay St, Toronto, ON"

    def test_two_parents(self, tmp_path):
        """Parse profile with two parents having work addresses."""
        profile = tmp_path / "family-profile.md"
        profile.write_text(
            "---\n"
            'home_address: "123 Main St"\n'
            "max_commute_minutes: 45\n"
            "parents:\n"
            '  - name: "Alice"\n'
            '    work_address: "456 Bay St"\n'
            '  - name: "Bob"\n'
            '    work_address: "789 King St"\n'
            "---\n"
        )
        result = parse_profile(str(profile))
        assert len(result["work_addresses"]) == 2
        assert result["work_addresses"][1]["name"] == "Bob"

    def test_missing_optional_fields(self, tmp_path):
        """Profile without max_commute or api_key returns defaults."""
        profile = tmp_path / "family-profile.md"
        profile.write_text(
            "---\n"
            'home_address: "123 Main St"\n'
            "---\n"
        )
        result = parse_profile(str(profile))
        assert result["home_address"] == "123 Main St"
        assert result["max_commute"] == 0
        assert result["api_key"] == ""
        assert result["work_addresses"] == []

    def test_api_key_from_profile(self, tmp_path):
        """Parse geoapify API key from profile."""
        profile = tmp_path / "family-profile.md"
        profile.write_text(
            "---\n"
            'home_address: "123 Main St"\n'
            "apis:\n"
            '  geoapify_api_key: "test-key-123"\n'
            "---\n"
        )
        result = parse_profile(str(profile))
        assert result["api_key"] == "test-key-123"

    def test_parent_without_work_address(self, tmp_path):
        """Parent without work_address is skipped in work_addresses list."""
        profile = tmp_path / "family-profile.md"
        profile.write_text(
            "---\n"
            'home_address: "123 Main St"\n'
            "parents:\n"
            '  - name: "Alice"\n'
            '    work_address: "456 Bay St"\n'
            '  - name: "Bob"\n'
            "---\n"
        )
        result = parse_profile(str(profile))
        assert len(result["work_addresses"]) == 1

    def test_address_with_special_characters(self, tmp_path):
        """Address with commas, colons, and apostrophes parses correctly."""
        profile = tmp_path / "family-profile.md"
        profile.write_text(
            "---\n"
            "home_address: \"100 Queen's Park Cres, Suite 5: Toronto, ON M5S 2C6\"\n"
            "---\n"
        )
        result = parse_profile(str(profile))
        assert "Queen's Park" in result["home_address"]
        assert "Suite 5:" in result["home_address"]

    def test_no_frontmatter(self, tmp_path):
        """Profile without YAML frontmatter exits with error."""
        profile = tmp_path / "family-profile.md"
        profile.write_text("# Just a markdown file\nNo frontmatter here.\n")
        with pytest.raises(SystemExit):
            parse_profile(str(profile))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd kids-camp-planner && python3 -m pytest skills/commute-matrix/scripts/test_commute_calculator.py::TestParseProfile -v`
Expected: Some tests FAIL (regex parser can't handle all cases, especially `test_api_key_from_profile` with nested `apis` block and `test_address_with_special_characters`)

- [ ] **Step 3: Rewrite parse_profile() using pyyaml**

Add `import yaml` at the module top level (near the other imports around line 43). Then replace the `parse_profile()` function in `commute_calculator.py` (lines 50-107):

```python
def parse_profile(profile_path):
    """Parse family profile YAML frontmatter for addresses and API key.

    Returns dict with keys: home_address, work_addresses, api_key, max_commute.
    work_addresses is a list of {name, address} dicts.
    """

    with open(profile_path, encoding="utf-8") as f:
        text = f.read()

    # Extract YAML frontmatter between --- markers
    m = re.match(r"^---\n(.*?\n)---", text, re.DOTALL)
    if not m:
        print("Error: Could not find YAML frontmatter in profile.", file=sys.stderr)
        sys.exit(1)

    data = yaml.safe_load(m.group(1))
    if not data:
        data = {}

    result = {
        "home_address": str(data.get("home_address", "")),
        "work_addresses": [],
        "api_key": "",
        "max_commute": int(data.get("max_commute_minutes", 0)),
    }

    # API key from nested apis block
    apis = data.get("apis", {})
    if apis:
        result["api_key"] = str(apis.get("geoapify_api_key", ""))

    # Parents and work addresses
    parents = data.get("parents", [])
    if parents:
        for parent in parents:
            name = parent.get("name", "")
            work_addr = parent.get("work_address", "")
            if name and work_addr:
                result["work_addresses"].append({
                    "name": str(name),
                    "address": str(work_addr),
                })

    return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd kids-camp-planner && python3 -m pytest skills/commute-matrix/scripts/test_commute_calculator.py::TestParseProfile -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Add pyyaml to README prerequisites**

In the README prerequisites section (around line 236), change:
```
- Python 3.x (for budget calculator and date scripts)
```
to:
```
- Python 3.x (for budget calculator and date scripts)
- PyYAML (`pip install pyyaml`) — for parsing family profile YAML
```

- [ ] **Step 6: Commit**

```bash
git add kids-camp-planner/skills/commute-matrix/scripts/test_commute_calculator.py \
       kids-camp-planner/skills/commute-matrix/scripts/commute_calculator.py \
       kids-camp-planner/README.md
git commit -m "refactor(kids-camp-planner): replace regex YAML parsing with pyyaml"
```

---

### Task 8: Write test suite for budget_calculator.py

**Files:**
- Create: `kids-camp-planner/skills/budget-optimization/scripts/test_budget_calculator.py`

- [ ] **Step 1: Write comprehensive test suite**

Create `kids-camp-planner/skills/budget-optimization/scripts/test_budget_calculator.py`:

```python
"""Tests for budget_calculator.py."""

import json
import os
import sys
import tempfile
from argparse import Namespace
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from budget_calculator import (
    calculate_simple_budget,
    calculate_json_budget,
    format_currency,
    render_markdown_simple,
    render_markdown_detailed,
    render_csv_simple,
    render_csv_detailed,
)


class TestFormatCurrency:
    def test_integer_amount(self):
        assert format_currency(300) == "$300"

    def test_float_amount(self):
        assert format_currency(300.50) == "$300.50"

    def test_large_amount(self):
        assert format_currency(5000) == "$5,000"

    def test_zero(self):
        assert format_currency(0) == "$0"


class TestCalculateSimpleBudgetWeekly:
    """Test weekly rate calculations."""

    def _make_args(self, **kwargs):
        defaults = {
            "kids": 1, "weeks": 8, "base_cost": 300,
            "before_care": 0, "after_care": 0, "lunch": 0,
            "days": None, "daily_rate": None,
            "before_care_daily": 0, "after_care_daily": 0, "lunch_daily": 0,
            "sibling_discount": 0, "early_bird": 0, "registration_fee": 0,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_single_child_basic(self):
        args = self._make_args(kids=1, weeks=8, base_cost=300)
        results, total = calculate_simple_budget(args)
        assert len(results) == 1
        assert results[0]["total"] == 2400  # 300 * 8

    def test_two_children_no_discount(self):
        args = self._make_args(kids=2, weeks=8, base_cost=300)
        results, total = calculate_simple_budget(args)
        assert total == 4800  # 300 * 8 * 2

    def test_sibling_discount(self):
        args = self._make_args(kids=2, weeks=8, base_cost=300, sibling_discount=10)
        results, total = calculate_simple_budget(args)
        # Child 1: 300*8 = 2400, Child 2: 300*8 - 300*0.1*8 = 2400 - 240 = 2160
        assert results[0]["sibling_discount"] == 0
        assert results[1]["sibling_discount"] == 240
        assert total == 4560

    def test_early_bird_discount(self):
        args = self._make_args(kids=1, weeks=8, base_cost=300, early_bird=25)
        results, total = calculate_simple_budget(args)
        assert results[0]["early_bird_discount"] == 200  # 25 * 8
        assert total == 2200

    def test_with_care_and_lunch(self):
        args = self._make_args(
            kids=1, weeks=8, base_cost=300,
            before_care=50, after_care=50, lunch=35,
        )
        results, total = calculate_simple_budget(args)
        assert results[0]["total"] == (300 + 50 + 50 + 35) * 8  # 3480

    def test_registration_fee(self):
        args = self._make_args(kids=1, weeks=8, base_cost=300, registration_fee=50)
        results, total = calculate_simple_budget(args)
        assert results[0]["registration"] == 50
        assert total == 2450

    def test_four_children(self):
        args = self._make_args(kids=4, weeks=8, base_cost=300)
        results, total = calculate_simple_budget(args)
        assert len(results) == 4

    def test_100_percent_sibling_discount(self):
        args = self._make_args(kids=2, weeks=8, base_cost=300, sibling_discount=100)
        results, total = calculate_simple_budget(args)
        assert results[1]["sibling_discount"] == 2400  # 100% off base


class TestCalculateSimpleBudgetDaily:
    """Test daily rate calculations."""

    def _make_args(self, **kwargs):
        defaults = {
            "kids": 1, "weeks": 8, "base_cost": 300,
            "before_care": 0, "after_care": 0, "lunch": 0,
            "days": 40, "daily_rate": 60,
            "before_care_daily": 0, "after_care_daily": 0, "lunch_daily": 0,
            "sibling_discount": 0, "early_bird": 0, "registration_fee": 0,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_single_child_daily(self):
        args = self._make_args(kids=1, days=40, daily_rate=60)
        results, total = calculate_simple_budget(args)
        assert results[0]["total"] == 2400  # 60 * 40

    def test_daily_with_care(self):
        args = self._make_args(
            kids=1, days=40, daily_rate=60,
            before_care_daily=10, after_care_daily=10, lunch_daily=7,
        )
        results, total = calculate_simple_budget(args)
        assert results[0]["total"] == (60 + 10 + 10 + 7) * 40  # 3480

    def test_seven_pa_days(self):
        """Budget for 7 PA days at daily rates."""
        args = self._make_args(kids=2, days=7, daily_rate=45)
        results, total = calculate_simple_budget(args)
        assert total == 630  # 45 * 7 * 2


class TestCalculateJsonBudgetWeekly:
    """Test JSON weekly input format."""

    def test_basic_weekly_json(self):
        data = {
            "children": [{"name": "Emma", "age": 7}],
            "budget_limit": 5000,
            "weeks": [
                {
                    "week_number": 1,
                    "start_date": "2025-06-30",
                    "assignments": {
                        "Emma": {
                            "provider": "YMCA",
                            "base_cost": 300,
                            "before_care": 50,
                            "after_care": 50,
                            "lunch": 0,
                        }
                    },
                }
            ],
            "discounts": {},
            "registration_fees": {},
        }
        result = calculate_json_budget(data)
        assert result["grand_total"] == 400
        assert result["budget_limit"] == 5000
        assert len(result["children"]) == 1

    def test_multi_week_discount(self):
        weeks = []
        for i in range(5):
            weeks.append({
                "week_number": i + 1,
                "assignments": {
                    "Emma": {"provider": "YMCA", "base_cost": 300}
                },
            })
        data = {
            "children": [{"name": "Emma", "age": 7}],
            "weeks": weeks,
            "discounts": {"multi_week_threshold": 4, "multi_week_percent": 5},
        }
        result = calculate_json_budget(data)
        # 5 weeks * 300 = 1500, minus 5% multi-week = 75
        assert result["children"][0]["multi_week_discount"] == 75


class TestCalculateJsonBudgetDaily:
    """Test JSON daily input format."""

    def test_basic_daily_json(self):
        data = {
            "children": [{"name": "Emma", "age": 7}],
            "budget_limit": 5000,
            "days": [
                {
                    "date": "2025-06-30",
                    "assignments": {
                        "Emma": {
                            "provider": "YMCA",
                            "daily_rate": 60,
                            "before_care": 10,
                            "after_care": 10,
                            "lunch": 7,
                        }
                    },
                }
            ],
            "discounts": {},
            "registration_fees": {},
        }
        result = calculate_json_budget(data)
        assert result["grand_total"] == 87


class TestRendering:
    """Test output rendering functions."""

    def test_markdown_simple_output(self):
        results = [{
            "child": "Child 1",
            "camp_fees": 2400,
            "before_after": 800,
            "lunch_cost": 280,
            "registration": 50,
            "subtotal": 3530,
            "sibling_discount": 0,
            "early_bird_discount": 200,
            "total": 3330,
        }]
        args = Namespace(budget_limit=0)
        output = render_markdown_simple(results, 3330, args)
        assert "# Camp Budget Summary" in output
        assert "$3,330" in output
        assert "Tax Recovery Estimate" in output

    def test_csv_simple_output(self):
        results = [{
            "child": "Child 1",
            "camp_fees": 2400,
            "before_after": 0,
            "lunch_cost": 0,
            "registration": 0,
            "subtotal": 2400,
            "sibling_discount": 0,
            "early_bird_discount": 0,
            "total": 2400,
        }]
        output = render_csv_simple(results, 2400)
        assert "Child 1" in output
        assert "TOTAL" in output

    def test_budget_limit_over(self):
        results = [{
            "child": "Child 1",
            "camp_fees": 5000,
            "before_after": 0,
            "lunch_cost": 0,
            "registration": 0,
            "subtotal": 5000,
            "sibling_discount": 0,
            "early_bird_discount": 0,
            "total": 5000,
        }]
        args = Namespace(budget_limit=4000)
        output = render_markdown_simple(results, 5000, args)
        assert "OVER budget" in output

    def test_budget_limit_under(self):
        results = [{
            "child": "Child 1",
            "camp_fees": 2000,
            "before_after": 0,
            "lunch_cost": 0,
            "registration": 0,
            "subtotal": 2000,
            "sibling_discount": 0,
            "early_bird_discount": 0,
            "total": 2000,
        }]
        args = Namespace(budget_limit=4000)
        output = render_markdown_simple(results, 2000, args)
        assert "UNDER budget" in output
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd kids-camp-planner && python3 -m pytest skills/budget-optimization/scripts/test_budget_calculator.py -v`
Expected: All tests PASS (these test existing behavior)

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/skills/budget-optimization/scripts/test_budget_calculator.py
git commit -m "test(kids-camp-planner): add comprehensive test suite for budget_calculator.py"
```

---

### Task 9: Make tax estimates configurable

**Files:**
- Modify: `kids-camp-planner/skills/budget-optimization/scripts/budget_calculator.py` (lines 515-517, 598-603, 648-668)
- Modify: `kids-camp-planner/skills/budget-optimization/scripts/test_budget_calculator.py`

- [ ] **Step 1: Write failing tests for configurable tax**

Add to `test_budget_calculator.py`:

```python
class TestTaxEstimates:
    """Test configurable tax estimate calculations."""

    def test_default_tax_limit(self):
        results = [{
            "child": "Child 1",
            "camp_fees": 10000,
            "before_after": 0,
            "lunch_cost": 0,
            "registration": 0,
            "subtotal": 10000,
            "sibling_discount": 0,
            "early_bird_discount": 0,
            "total": 10000,
        }]
        args = Namespace(budget_limit=0, tax_deduction_limit=8000, tax_marginal_rate=0.25)
        output = render_markdown_simple(results, 10000, args)
        # min(10000, 8000) * 0.25 = 2000
        assert "$2,000" in output

    def test_custom_tax_limit(self):
        results = [{
            "child": "Child 1",
            "camp_fees": 10000,
            "before_after": 0,
            "lunch_cost": 0,
            "registration": 0,
            "subtotal": 10000,
            "sibling_discount": 0,
            "early_bird_discount": 0,
            "total": 10000,
        }]
        args = Namespace(budget_limit=0, tax_deduction_limit=5000, tax_marginal_rate=0.30)
        output = render_markdown_simple(results, 10000, args)
        # min(10000, 5000) * 0.30 = 1500
        assert "$1,500" in output

    def test_disclaimer_present(self):
        results = [{
            "child": "Child 1",
            "camp_fees": 2000,
            "before_after": 0,
            "lunch_cost": 0,
            "registration": 0,
            "subtotal": 2000,
            "sibling_discount": 0,
            "early_bird_discount": 0,
            "total": 2000,
        }]
        args = Namespace(budget_limit=0, tax_deduction_limit=8000, tax_marginal_rate=0.25)
        output = render_markdown_simple(results, 2000, args)
        assert "Estimates only" in output
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd kids-camp-planner && python3 -m pytest skills/budget-optimization/scripts/test_budget_calculator.py::TestTaxEstimates -v`
Expected: FAIL — `test_custom_tax_limit` fails because the current code uses hardcoded `8000`/`0.25` instead of the custom values; `test_disclaimer_present` fails because the disclaimer text doesn't exist yet

- [ ] **Step 3: Add CLI args for tax configuration**

In `budget_calculator.py`, add to the `main()` argument parser (around line 665):

```python
parser.add_argument("--tax-deduction-limit", type=float, default=8000,
                    help="Maximum child care expense deduction (default: 8000)")
parser.add_argument("--tax-marginal-rate", type=float, default=0.25,
                    help="Estimated marginal tax rate (default: 0.25)")
```

- [ ] **Step 4: Update render_markdown_simple() tax section**

Replace the tax estimate section in `render_markdown_simple()` (around lines 512-518):

```python
    # Tax estimate
    tax_limit = getattr(args, 'tax_deduction_limit', 8000)
    tax_rate = getattr(args, 'tax_marginal_rate', 0.25)
    lines.append("## Tax Recovery Estimate\n")
    lines.append("*Estimates only — consult a tax professional. Based on CRA child care expense deduction (Line 21400). Limits and rates may change.*\n")
    for r in results:
        deductible = min(r["total"], tax_limit)
        estimated_savings = deductible * tax_rate
        lines.append(f"- **{r['child']}**: {format_currency(r['total'])} eligible, ~{format_currency(estimated_savings)} estimated tax savings (at ~{tax_rate:.0%} marginal rate)")
    lines.append("")
```

- [ ] **Step 5: Update render_markdown_detailed() tax section**

Replace the tax estimate section in `render_markdown_detailed()` (around lines 598-603):

```python
    # Tax estimate
    tax_limit = data.get("tax_deduction_limit", 8000)
    tax_rate = data.get("tax_marginal_rate", 0.25)
    lines.append("## Tax Recovery Estimate\n")
    lines.append("*Estimates only — consult a tax professional. Based on CRA child care expense deduction (Line 21400). Limits and rates may change.*\n")
    for r in results:
        deductible = min(r["total"], tax_limit)
        estimated_savings = deductible * tax_rate
        lines.append(f"- **{r['child']}**: {format_currency(r['total'])} eligible, ~{format_currency(estimated_savings)} estimated tax savings")
    lines.append("")
```

- [ ] **Step 6: Run all budget tests to verify they pass**

Run: `cd kids-camp-planner && python3 -m pytest skills/budget-optimization/scripts/test_budget_calculator.py -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add kids-camp-planner/skills/budget-optimization/scripts/budget_calculator.py \
       kids-camp-planner/skills/budget-optimization/scripts/test_budget_calculator.py
git commit -m "feat(kids-camp-planner): make tax estimates configurable with disclaimer"
```

---

## Chunk 3: Wave 2 — Code Robustness (Part 2: summer_dates tests + commute tests)

### Task 10: Write test suite for summer_dates.py

**Files:**
- Create: `kids-camp-planner/skills/plan-summer/scripts/test_summer_dates.py`

- [ ] **Step 1: Write comprehensive test suite**

Create `kids-camp-planner/skills/plan-summer/scripts/test_summer_dates.py`:

```python
"""Tests for summer_dates.py."""

import json
import os
import sys
from datetime import date
from io import StringIO
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from summer_dates import (
    find_labour_day,
    get_weekdays,
    get_weeks,
    get_individual_days,
    parse_date,
    main,
)


class TestFindLabourDay:
    """Labour Day is the first Monday in September."""

    def test_2025(self):
        assert find_labour_day(2025) == date(2025, 9, 1)

    def test_2026(self):
        assert find_labour_day(2026) == date(2026, 9, 7)

    def test_2027(self):
        assert find_labour_day(2027) == date(2027, 9, 6)

    def test_2028_leap_year(self):
        assert find_labour_day(2028) == date(2028, 9, 4)

    def test_2029(self):
        assert find_labour_day(2029) == date(2029, 9, 3)

    def test_2030(self):
        assert find_labour_day(2030) == date(2030, 9, 2)


class TestGetWeekdays:
    def test_full_week(self):
        """Monday to Friday gives 5 weekdays."""
        days = get_weekdays(date(2025, 6, 30), date(2025, 7, 4))
        assert len(days) == 5

    def test_includes_boundaries(self):
        """Start and end dates are included."""
        days = get_weekdays(date(2025, 6, 30), date(2025, 6, 30))
        assert len(days) == 1
        assert days[0] == date(2025, 6, 30)

    def test_skips_weekends(self):
        """Saturday and Sunday are excluded."""
        days = get_weekdays(date(2025, 7, 4), date(2025, 7, 7))
        assert len(days) == 2  # Friday + Monday

    def test_weekend_only_range(self):
        """Saturday to Sunday gives 0 weekdays."""
        days = get_weekdays(date(2025, 7, 5), date(2025, 7, 6))
        assert len(days) == 0


class TestGetWeeks:
    def test_full_weeks(self):
        """8 full Mon-Fri weeks."""
        weeks = get_weeks(date(2025, 6, 30), date(2025, 8, 22))
        full_weeks = [w for w in weeks if not w["partial"]]
        assert len(full_weeks) == 8

    def test_partial_first_week(self):
        """Start on Wednesday gives partial first week."""
        weeks = get_weeks(date(2025, 7, 2), date(2025, 7, 11))
        assert weeks[0]["partial"] is True
        assert weeks[0]["weekdays"] == 3  # Wed, Thu, Fri

    def test_partial_last_week(self):
        """End on Wednesday gives partial last week."""
        weeks = get_weeks(date(2025, 6, 30), date(2025, 7, 9))
        last = weeks[-1]
        assert last["weekdays"] == 2  # Mon, Tue (Jul 7-8) or partial


class TestGetIndividualDays:
    def test_day_count(self):
        """Should match get_weekdays count."""
        days = get_individual_days(date(2025, 6, 30), date(2025, 7, 11))
        weekdays = get_weekdays(date(2025, 6, 30), date(2025, 7, 11))
        assert len(days) == len(weekdays)

    def test_week_numbering(self):
        """Days in the same Mon-Fri week share a week number."""
        days = get_individual_days(date(2025, 6, 30), date(2025, 7, 4))
        week_nums = {d["week_number"] for d in days}
        assert len(week_nums) == 1

    def test_day_of_week_format(self):
        """Day of week is 3-letter abbreviation."""
        days = get_individual_days(date(2025, 6, 30), date(2025, 6, 30))
        assert days[0]["day_of_week"] == "Mon"


class TestMainCLI:
    """Integration tests using main() with patched sys.argv."""

    def test_json_output(self):
        with patch("sys.argv", [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--format", "json",
        ]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                output = json.loads(mock_out.getvalue())
                assert output["year"] == 2025
                assert output["total_weekdays"] > 0
                assert len(output["weeks"]) > 0

    def test_markdown_output(self):
        with patch("sys.argv", [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--format", "markdown",
        ]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                output = mock_out.getvalue()
                assert "# Summer 2025 Coverage Window" in output
                assert "Week-by-Week Breakdown" in output

    def test_text_output(self):
        with patch("sys.argv", [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--format", "text",
        ]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                output = mock_out.getvalue()
                assert "Summer 2025 Coverage Window" in output

    def test_exclusion_dates(self):
        with patch("sys.argv", [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--exclude", "2025-07-14:2025-07-18",
            "--format", "json",
        ]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                output = json.loads(mock_out.getvalue())
                assert output["excluded_weekdays"] == 5
                assert output["coverage_weekdays"] == output["total_weekdays"] - 5

    def test_output_days_flag(self):
        with patch("sys.argv", [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-26",
            "--format", "json",
            "--output-days",
        ]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                output = json.loads(mock_out.getvalue())
                assert "days" in output
                assert len(output["days"]) == output["total_weekdays"]

    def test_private_school_early_start(self):
        """First fall day before Labour Day (private school scenario)."""
        with patch("sys.argv", [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-20",
            "--first-fall-day", "2025-08-25",
            "--format", "json",
        ]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                output = json.loads(mock_out.getvalue())
                assert output["first_fall_day"] == "2025-08-25"
                assert output["coverage_end"] < "2025-08-25"

    def test_last_school_day_friday(self):
        """Coverage starts the following Monday."""
        with patch("sys.argv", [
            "summer_dates.py",
            "--year", "2025",
            "--last-school-day", "2025-06-27",  # Friday
            "--format", "json",
        ]):
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                main()
                output = json.loads(mock_out.getvalue())
                assert output["coverage_start"] == "2025-06-30"  # Monday
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `cd kids-camp-planner && python3 -m pytest skills/plan-summer/scripts/test_summer_dates.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/skills/plan-summer/scripts/test_summer_dates.py
git commit -m "test(kids-camp-planner): add comprehensive test suite for summer_dates.py"
```

---

### Task 11: Complete commute_calculator.py test suite

**Files:**
- Modify: `kids-camp-planner/skills/commute-matrix/scripts/test_commute_calculator.py`

- [ ] **Step 1: Add remaining test classes**

Append to the existing `test_commute_calculator.py` (which already has `TestParseProfile` from Task 7):

```python
import json
import tempfile
from unittest.mock import patch, MagicMock

from commute_calculator import (
    scan_providers,
    normalize_address,
    geocode,
    load_geocache,
    save_geocache,
    route_matrix,
    compute_chains,
    render_markdown,
    render_json,
    update_provider_files,
)


class TestScanProviders:
    def test_valid_provider(self, tmp_path):
        """Scan a provider file with name and address."""
        p = tmp_path / "ymca.md"
        p.write_text("# YMCA Day Camp\n\n**Location**: 100 College St, Toronto\n")
        providers = scan_providers(str(tmp_path))
        assert len(providers) == 1
        assert providers[0]["name"] == "YMCA Day Camp"
        assert providers[0]["address"] == "100 College St, Toronto"

    def test_provider_without_address(self, tmp_path):
        """Provider without Location line is skipped."""
        p = tmp_path / "mystery.md"
        p.write_text("# Mystery Camp\n\nNo address here.\n")
        providers = scan_providers(str(tmp_path))
        assert len(providers) == 0

    def test_non_md_files_ignored(self, tmp_path):
        """Non-markdown files are ignored."""
        (tmp_path / "notes.txt").write_text("not a provider")
        providers = scan_providers(str(tmp_path))
        assert len(providers) == 0

    def test_nonexistent_directory(self):
        providers = scan_providers("/nonexistent/path")
        assert providers == []

    def test_sorted_by_filename(self, tmp_path):
        """Providers returned in sorted filename order."""
        (tmp_path / "b-camp.md").write_text("# B Camp\n\n**Location**: 2 St\n")
        (tmp_path / "a-camp.md").write_text("# A Camp\n\n**Location**: 1 St\n")
        providers = scan_providers(str(tmp_path))
        assert providers[0]["name"] == "A Camp"
        assert providers[1]["name"] == "B Camp"


class TestNormalizeAddress:
    def test_lowercase_and_strip(self):
        assert normalize_address("  123 Main ST  ") == "123 main st"

    def test_collapse_whitespace(self):
        assert normalize_address("123  Main   St") == "123 main st"


class TestGeocode:
    def test_cache_hit(self):
        cache = {"123 main st": {"lat": 43.65, "lon": -79.38, "formatted": "123 Main St"}}
        result = geocode("123 Main St", "fake-key", cache)
        assert result["lat"] == 43.65

    def test_cache_miss_with_api(self):
        mock_response = json.dumps({
            "features": [{
                "properties": {"formatted": "123 Main St, Toronto"},
                "geometry": {"coordinates": [-79.38, 43.65]},
            }]
        }).encode()

        cache = {}
        with patch("commute_calculator.urllib.request.urlopen") as mock_url:
            mock_url.return_value.__enter__ = lambda s: MagicMock(read=lambda: mock_response)
            mock_url.return_value.__exit__ = MagicMock(return_value=False)
            result = geocode("123 Main St", "test-key", cache)

        assert result["lat"] == 43.65
        assert "123 main st" in cache  # cached after lookup

    def test_no_api_key(self):
        result = geocode("123 Main St", "", {})
        assert result is None

    def test_api_failure(self):
        cache = {}
        with patch("commute_calculator.urllib.request.urlopen", side_effect=Exception("timeout")):
            result = geocode("123 Main St", "test-key", cache)
        assert result is None


class TestGeocache:
    def test_round_trip(self, tmp_path):
        cache_path = str(tmp_path / "geocache.json")
        cache = {"123 main st": {"lat": 43.65, "lon": -79.38}}
        save_geocache(cache, cache_path)
        loaded = load_geocache(cache_path)
        assert loaded == cache

    def test_load_nonexistent(self):
        assert load_geocache("/nonexistent/cache.json") == {}

    def test_load_none_path(self):
        assert load_geocache(None) == {}


class TestRouteMatrix:
    def test_basic_matrix(self):
        mock_response = json.dumps({
            "sources_to_targets": [[
                {"source_index": 0, "target_index": 0, "time": 600, "distance": 5000},
                {"source_index": 0, "target_index": 1, "time": 1200, "distance": 10000},
            ]]
        }).encode()

        with patch("commute_calculator.urllib.request.urlopen") as mock_url:
            mock_url.return_value.__enter__ = lambda s: MagicMock(read=lambda: mock_response)
            mock_url.return_value.__exit__ = MagicMock(return_value=False)
            matrix = route_matrix(
                [{"lat": 43.65, "lon": -79.38}],
                [{"lat": 43.65, "lon": -79.38}, {"lat": 43.70, "lon": -79.40}],
                "drive", "test-key",
            )

        assert matrix[0][0]["duration_sec"] == 600
        assert matrix[0][1]["distance_m"] == 10000

    def test_no_api_key(self):
        result = route_matrix([{"lat": 0, "lon": 0}], [{"lat": 0, "lon": 0}], "drive", "")
        assert result is None


class TestComputeChains:
    def test_am_pm_chain_math(self):
        """AM chain = home->camp + camp->work, PM chain = work->camp + camp->home."""
        home = {"lat": 43.65, "lon": -79.38}
        camps = [{"name": "Test Camp", "address": "1 St", "file_path": ""}]
        works = [{"name": "Alice", "address": "2 St"}]

        # Mock geocode to return fixed coords
        def mock_geocode(addr, key, cache):
            coords = {
                "1 st": {"lat": 43.66, "lon": -79.39, "formatted": "1 St"},
                "2 st": {"lat": 43.67, "lon": -79.40, "formatted": "2 St"},
            }
            return coords.get(normalize_address(addr))

        # Mock route_matrix to return known values
        # Locations: [home(0), camp(1), work(2)]
        mock_matrix = [
            [None, {"duration_sec": 600, "distance_m": 3000}, {"duration_sec": 1200, "distance_m": 6000}],
            [{"duration_sec": 660, "distance_m": 3100}, None, {"duration_sec": 900, "distance_m": 4000}],
            [{"duration_sec": 1260, "distance_m": 6100}, {"duration_sec": 960, "distance_m": 4100}, None],
        ]

        with patch("commute_calculator.geocode", side_effect=mock_geocode):
            with patch("commute_calculator.route_matrix", return_value=mock_matrix):
                result = compute_chains(home, camps, works, ["drive"], "key", {})

        camp_data = result["Test Camp"]
        chains = camp_data["modes"]["drive"]["chains"]["Alice"]
        # AM: home->camp (10min) + camp->work (15min) = 25min
        assert chains["am"] == 25
        # PM: work->camp (16min) + camp->home (11min) = 27min
        assert chains["pm"] == 27


class TestUpdateProviderFiles:
    def test_updates_computed_section(self, tmp_path):
        """Provider file gets updated Computed subsection."""
        provider = tmp_path / "test-camp.md"
        provider.write_text(
            "# Test Camp\n\n"
            "## Distance & Commute\n"
            "- **Transit accessible**: Yes\n"
            "- **Parking**: Street\n"
            "\n## Programs\n"
        )
        commute_data = {
            "Test Camp": {
                "address": "1 St",
                "lat": 43.66, "lon": -79.39,
                "file_path": str(provider),
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 15, "camp_to_home": 16, "distance_km": 8.5},
                        "chains": {},
                    }
                },
            }
        }
        update_provider_files(commute_data, ["drive"])
        content = provider.read_text()
        assert "### Computed" in content
        assert "15 minutes" in content
        assert "8.5 km" in content
        assert "Transit accessible" in content  # Manual data preserved


class TestRenderMarkdown:
    def test_empty_data(self):
        output = render_markdown({}, "123 Main St", 30, ["drive"])
        assert "No commute data available" in output

    def test_exceeds_max_flagged(self):
        data = {
            "Far Camp": {
                "address": "999 Far Rd",
                "lat": 44.0, "lon": -80.0,
                "file_path": "",
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 45, "camp_to_home": 50, "distance_km": 60},
                        "chains": {
                            "Alice": {"am": 60, "pm": 65, "home_to_camp": 45, "camp_to_work": 15, "work_to_camp": 15, "camp_to_home": 50}
                        },
                    }
                },
            }
        }
        output = render_markdown(data, "123 Main", 30, ["drive"])
        assert "EXCEEDS MAX" in output
        assert "Constraint Violations" in output


class TestRenderJson:
    def test_structure(self):
        data = {
            "Test Camp": {
                "address": "1 St",
                "lat": 43.66, "lon": -79.39,
                "file_path": "",
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 15, "camp_to_home": 16, "distance_km": 8.5},
                        "chains": {"Alice": {"am": 25, "pm": 27}},
                    }
                },
            }
        }
        home_geo = {"lat": 43.65, "lon": -79.38}
        result = render_json(data, "123 Main", home_geo, 30, ["drive"])
        assert "generated" in result
        assert "camps" in result
        assert "Test Camp" in result["camps"]
        camp = result["camps"]["Test Camp"]
        assert camp["best_chain_minutes"] is not None
        assert camp["exceeds_max"] is False
```

- [ ] **Step 2: Run full commute test suite**

Run: `cd kids-camp-planner && python3 -m pytest skills/commute-matrix/scripts/test_commute_calculator.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/skills/commute-matrix/scripts/test_commute_calculator.py
git commit -m "test(kids-camp-planner): complete commute_calculator.py test suite"
```

---

### Task 12: Write test suite for scrape_board_calendar.py

**Files:**
- Create: `kids-camp-planner/skills/add-school-calendar/scripts/test_scrape_board_calendar.py`

- [ ] **Step 1: Write test suite**

Create `kids-camp-planner/skills/add-school-calendar/scripts/test_scrape_board_calendar.py`:

```python
"""Tests for scrape_board_calendar.py."""

import json
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from scrape_board_calendar import TableExtractor, fetch_and_extract, generate_draft


class TestTableExtractor:
    def test_simple_table(self):
        html = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"
        parser = TableExtractor()
        parser.feed(html)
        assert len(parser.tables) == 1
        assert parser.tables[0] == [["A", "B"], ["1", "2"]]

    def test_multiple_tables(self):
        html = (
            "<table><tr><td>T1</td></tr></table>"
            "<p>gap</p>"
            "<table><tr><td>T2</td></tr></table>"
        )
        parser = TableExtractor()
        parser.feed(html)
        assert len(parser.tables) == 2

    def test_empty_cells(self):
        html = "<table><tr><td></td><td>X</td></tr></table>"
        parser = TableExtractor()
        parser.feed(html)
        assert parser.tables[0] == [["", "X"]]

    def test_nested_tags_in_cells(self):
        html = "<table><tr><td><strong>Bold</strong> text</td></tr></table>"
        parser = TableExtractor()
        parser.feed(html)
        assert parser.tables[0] == [["Bold text"]]

    def test_no_tables(self):
        html = "<p>No tables here</p>"
        parser = TableExtractor()
        parser.feed(html)
        assert parser.tables == []

    def test_unclosed_tags(self):
        """Malformed HTML with unclosed tags should not crash."""
        html = "<table><tr><td>Data<tr><td>More"
        parser = TableExtractor()
        parser.feed(html)
        # Should not raise; may have partial data
        assert isinstance(parser.tables, list)

    def test_th_and_td_mixed(self):
        html = "<table><tr><th>Header</th></tr><tr><td>Data</td></tr></table>"
        parser = TableExtractor()
        parser.feed(html)
        assert parser.tables[0] == [["Header"], ["Data"]]


class TestGenerateDraft:
    def test_output_structure(self):
        tables = [[["Date", "Event"], ["Sep 2", "First Day"]]]
        draft = generate_draft("Test Board", "TB", "2025-2026", tables, "<html></html>")
        assert "# Test Board (TB)" in draft
        assert "## 2025-2026 School Year" in draft
        assert "Sep 2" in draft
        assert "[TODO]" in draft

    def test_empty_tables(self):
        draft = generate_draft("Test Board", "TB", "2025-2026", [], "<html></html>")
        assert "# Test Board (TB)" in draft
        assert "Extracted Tables" in draft

    def test_multiple_tables_rendered(self):
        tables = [
            [["A", "B"], ["1", "2"]],
            [["C", "D"], ["3", "4"]],
        ]
        draft = generate_draft("Board", "B", "2025-2026", tables, "")
        assert "Table 1" in draft
        assert "Table 2" in draft


class TestFetchAndExtract:
    def test_with_mocked_url(self):
        html = b"<html><table><tr><td>Data</td></tr></table></html>"
        mock_resp = MagicMock()
        mock_resp.read.return_value = html
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("scrape_board_calendar.urllib.request.urlopen", return_value=mock_resp):
            tables, raw_html = fetch_and_extract("http://example.com")

        assert len(tables) == 1
        assert tables[0] == [["Data"]]
        assert "table" in raw_html
```

- [ ] **Step 2: Run tests**

Run: `cd kids-camp-planner && python3 -m pytest skills/add-school-calendar/scripts/test_scrape_board_calendar.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/skills/add-school-calendar/scripts/test_scrape_board_calendar.py
git commit -m "test(kids-camp-planner): add test suite for scrape_board_calendar.py"
```

---

## Chunk 4: Wave 2 — Code Robustness (Part 3: lazy imports, staleness, README, version bump)

### Task 13: Lazy-import openpyxl in generate_annual_schedule.py

**Files:**
- Modify: `kids-camp-planner/skills/generate-annual-schedule/scripts/generate_annual_schedule.py`

- [ ] **Step 1: Identify all openpyxl imports and usages**

Run: `grep -n 'openpyxl' kids-camp-planner/skills/generate-annual-schedule/scripts/generate_annual_schedule.py`

Note the top-level import lines and all functions that use openpyxl.

- [ ] **Step 2: Remove both top-level imports, add lazy imports**

Remove BOTH top-level openpyxl imports (there are two):
```python
import openpyxl                          # line 47
from openpyxl.utils import get_column_letter  # line 48
```

In each function that uses openpyxl (primarily `update_xlsx()`, `read_provider_rates()`, `read_summer_assignments()`), add at the function start:

```python
try:
    import openpyxl
    from openpyxl.utils import get_column_letter
except ImportError:
    print("Error: openpyxl is required for Excel output. Install with: pip install openpyxl",
          file=sys.stderr)
    sys.exit(1)
```

Note: `get_column_letter` is used by `update_xlsx()`. Include it in the import block for any function that needs it.

- [ ] **Step 3: Verify markdown-only path works without openpyxl**

Run a test that exercises markdown output without xlsx. The existing test suite should cover this — run it:

Run: `cd kids-camp-planner && python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v -k "not xlsx and not update"` (or identify markdown-only tests)

If all tests require openpyxl, just verify the import is lazy by reading the file.

- [ ] **Step 4: Commit**

```bash
git add kids-camp-planner/skills/generate-annual-schedule/scripts/generate_annual_schedule.py
git commit -m "refactor(kids-camp-planner): lazy-import openpyxl for non-xlsx functionality"
```

---

### Task 14: Add school calendar staleness detection to skills

**Files:**
- Modify: `kids-camp-planner/skills/plan-summer/SKILL.md`
- Modify: `kids-camp-planner/skills/plan-march-break/SKILL.md`
- Modify: `kids-camp-planner/skills/plan-pa-days/SKILL.md`
- Modify: `kids-camp-planner/skills/generate-annual-schedule/SKILL.md`

- [ ] **Step 1: Read each SKILL.md to identify insertion points**

Read all 4 SKILL.md files. For each, identify the step where calendar data is loaded or the 3-Tier lookup completes.

- [ ] **Step 2: Add staleness check to plan-summer/SKILL.md**

After the 3-Tier School Calendar Lookup completes (after Tier 3), add:

```markdown
**Check calendar staleness:** After loading calendar data, extract the school year from the `## YYYY-YYYY School Year` header. Parse the end year (e.g., 2026 from "2025-2026"). If the current date is after September 1 of that end year, warn: *"Calendar data for [board] is from [year]. The current year may have different PA days and breaks. Would you like to search for updated calendar data?"* If the user says yes, run the 3-Tier School Calendar Lookup to find updated data.
```

- [ ] **Step 3: Add staleness check to plan-march-break/SKILL.md**

Same text, inserted after the calendar loading step.

- [ ] **Step 4: Add staleness check to plan-pa-days/SKILL.md**

Same text, inserted after the calendar loading step.

- [ ] **Step 5: Add staleness check to generate-annual-schedule/SKILL.md**

Insert *before* the script invocation step:

```markdown
**Check calendar staleness:** Before running the script, read the calendar file header and check for staleness. Extract the school year from the `## YYYY-YYYY School Year` header. Parse the end year (e.g., 2026 from "2025-2026"). If the current date is after September 1 of that end year, warn: *"Calendar data for [board] is from [year]. The current year may have different PA days and breaks. Would you like to search for updated calendar data?"* If the user says yes, run the 3-Tier School Calendar Lookup to find updated data before proceeding.
```

- [ ] **Step 6: Commit**

```bash
git add kids-camp-planner/skills/plan-summer/SKILL.md \
       kids-camp-planner/skills/plan-march-break/SKILL.md \
       kids-camp-planner/skills/plan-pa-days/SKILL.md \
       kids-camp-planner/skills/generate-annual-schedule/SKILL.md
git commit -m "feat(kids-camp-planner): add school calendar staleness detection to planning skills"
```

---

### Task 15: Add scraper caveat to README

**Files:**
- Modify: `kids-camp-planner/README.md`

This was partially addressed in Task 4 (helper scripts subsection). Verify the caveat text is present. If not already included, ensure the helper scripts table entry for `scrape_board_calendar.py` says "(draft quality — output requires manual review and reorganization)".

- [ ] **Step 1: Verify caveat is present**

Read the README and confirm the scraper caveat text exists in the helper scripts section added in Task 4.

- [ ] **Step 2: Commit if changes needed**

Only commit if a change was made.

---

### Task 16: Version bump to 0.2.0

**Files:**
- Modify: `kids-camp-planner/.claude-plugin/plugin.json`
- Modify: `kids-camp-planner/README.md` (badge version)

- [ ] **Step 1: Update version in plugin.json**

Change `"version": "0.1.1"` to `"version": "0.2.0"`.

- [ ] **Step 2: Update version badge in README**

Change the version badge from `version-0.1.1-blue` to `version-0.2.0-blue`.

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/.claude-plugin/plugin.json kids-camp-planner/README.md
git commit -m "chore(kids-camp-planner): bump version to 0.2.0"
```

---

## Chunk 5: Wave 3 — Plugin UX

### Task 17: Create 6 slash commands

**Files:**
- Create: `kids-camp-planner/commands/camp-setup.md`
- Create: `kids-camp-planner/commands/camp-research.md`
- Create: `kids-camp-planner/commands/camp-plan.md`
- Create: `kids-camp-planner/commands/camp-budget.md`
- Create: `kids-camp-planner/commands/camp-email.md`
- Create: `kids-camp-planner/commands/camp-schedule.md`

- [ ] **Step 1: Create commands directory**

```bash
mkdir -p kids-camp-planner/commands
```

- [ ] **Step 2: Create camp-setup.md**

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

- [ ] **Step 3: Create camp-research.md**

```markdown
---
name: camp-research
description: Research and document camp providers in your area
arguments:
  - name: focus
    description: Search focus (e.g., "STEM camps", "week 3 alternatives", "swimming")
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md` for location, ages, and constraints.

Then follow the research-camps skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/research-camps/SKILL.md`.

If a search focus was provided, use it to narrow the research scope. Otherwise, research broadly based on the family profile.
```

- [ ] **Step 4: Create camp-plan.md**

```markdown
---
name: camp-plan
description: Plan camp coverage for a school break period
arguments:
  - name: period
    description: "Period to plan: summer, march-break, or pa-days"
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md`.

Route to the appropriate planning skill based on the period argument:
- `summer` → Follow `${CLAUDE_PLUGIN_ROOT}/skills/plan-summer/SKILL.md`
- `march-break` → Follow `${CLAUDE_PLUGIN_ROOT}/skills/plan-march-break/SKILL.md`
- `pa-days` → Follow `${CLAUDE_PLUGIN_ROOT}/skills/plan-pa-days/SKILL.md`

If no period argument was provided, ask the user which period they'd like to plan using AskUserQuestion:
- Summer camps (Jun-Aug)
- March break (Mar)
- PA days (throughout the school year)
```

- [ ] **Step 5: Create camp-budget.md**

```markdown
---
name: camp-budget
description: Generate a camp budget analysis with cost breakdown
arguments:
  - name: period
    description: "Period to budget: summer, march-break, pa-days, or annual"
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md` for budget constraints.

Then follow the budget-optimization skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/budget-optimization/SKILL.md`.

If a period argument was provided, scope the budget to that period. Otherwise, generate a budget for the most relevant upcoming period.
```

- [ ] **Step 6: Create camp-email.md**

```markdown
---
name: camp-email
description: Draft an email to a camp provider
arguments:
  - name: details
    description: "Email type and provider (e.g., 'inquiry YMCA', 'waitlist Science Camp')"
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md` for personalization.

Then follow the draft-email skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/draft-email/SKILL.md`.

If details were provided, parse the email type (inquiry, registration, waitlist, special-needs, cancellation, logistics) and provider name from the argument. Otherwise, ask the user what type of email they need and which provider it's for.
```

- [ ] **Step 7: Create camp-schedule.md**

```markdown
---
name: camp-schedule
description: Generate a consolidated annual camp schedule
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md`.

Then follow the generate-annual-schedule skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/generate-annual-schedule/SKILL.md`.

This consolidates summer, PA days, winter break, and March break into one annual view with markdown and optional xlsx output.
```

- [ ] **Step 8: Commit**

```bash
git add kids-camp-planner/commands/
git commit -m "feat(kids-camp-planner): add 6 slash commands for key workflows"
```

---

### Task 18: Add fast-path setup to setup skill

**Files:**
- Modify: `kids-camp-planner/skills/setup/SKILL.md` (lines 146-156, re-running setup section)

- [ ] **Step 1: Read current SKILL.md re-running section**

Read `kids-camp-planner/skills/setup/SKILL.md` lines 146-156 to understand the current re-running logic.

- [ ] **Step 2: Replace re-running setup section**

Replace the "Re-Running Setup" section with an enhanced version:

```markdown
## Re-Running Setup

If a `.claude/kids-camp-planner.local.md` file already exists:
1. Read it to get the `research_dir` path
2. Read `<research_dir>/family-profile.md` for existing family data
3. Parse the profile and present a summary to the user:
   - Number of children and their names/ages
   - School board and type
   - Budget overview (per-week and per-day targets)
   - Key constraints (commute, care hours, dietary)
   - Vacation dates
4. Ask the user using AskUserQuestion: "Does this profile look correct? You can:
   - **Confirm** — skip to API key configuration (Step 3)
   - **Update specific sections** — tell me which group to update (Children, School, Parents, Location, Budget, Vacation, School Dates)
   - **Start fresh** — replace the entire profile"
5. If the user confirms: skip directly to Step 3 (API keys) and Step 4 (summary)
6. If the user wants to update: ask which group(s), then collect only those groups' data. Preserve all other existing data.
7. If the user wants to start fresh: proceed from Step 1 as normal.

If `research_dir` points to a directory that doesn't exist, treat it as a fresh setup starting from Step 1.
```

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/skills/setup/SKILL.md
git commit -m "feat(kids-camp-planner): add fast-path setup for pre-filled profiles"
```

---

### Task 19: Split generate_annual_schedule.py into modules

**Files:**
- Modify: `kids-camp-planner/skills/generate-annual-schedule/scripts/generate_annual_schedule.py`
- Create: `kids-camp-planner/skills/generate-annual-schedule/scripts/calendar_parser.py`
- Create: `kids-camp-planner/skills/generate-annual-schedule/scripts/rate_resolver.py`
- Create: `kids-camp-planner/skills/generate-annual-schedule/scripts/schedule_builder.py`
- Create: `kids-camp-planner/skills/generate-annual-schedule/scripts/xlsx_handler.py`
- Create: `kids-camp-planner/skills/generate-annual-schedule/scripts/renderer.py`
- Modify: `kids-camp-planner/skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py`

This is a large refactor. Follow this sequence carefully:

- [ ] **Step 1: Run existing tests as baseline**

Run: `cd kids-camp-planner && python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: All tests PASS. Note the count.

- [ ] **Step 2: Create calendar_parser.py**

Extract these functions from `generate_annual_schedule.py`:
- `parse_calendar()` (line 218)
- `parse_date_flexible()` (line 354)
- `get_weekdays_between()` (line 365)
- `find_civic_holiday()` (line 377)
- `get_summer_holidays()` (line 386)
- `resolve_calendars()` (line 412)

Add at the top (trace all stdlib dependencies from the extracted functions and include them — at minimum):
```python
"""Calendar parsing utilities for Ontario school calendars."""

import os
import re
import sys
from datetime import date, timedelta
```

Note: The implementer must trace all imports used by each extracted function and include them. The imports listed here are the minimum known set — add any others found during extraction (e.g., `json`, `os.path`).

- [ ] **Step 3: Create rate_resolver.py**

Extract these functions:
- `resolve_period_rate()` (line 82)
- `_read_rate_block()` (line 103)
- `_resolve_assignments()` (line 401)

Add at the top:
```python
"""Rate resolution logic for camp provider pricing."""
```

- [ ] **Step 4: Create schedule_builder.py**

Extract these functions:
- `build_annual_days()` (line 437)
- `build_annual_days_multi()` (line 594)

Add at the top (trace all stdlib dependencies from the extracted functions and include them — at minimum):
```python
"""Build annual day-by-day schedules from calendar and assignment data."""

from datetime import date, timedelta

from calendar_parser import get_weekdays_between, get_summer_holidays, find_civic_holiday
from rate_resolver import _resolve_assignments
```

Note: The implementer must trace all imports used by `build_annual_days()` and `build_annual_days_multi()` and add them here.

- [ ] **Step 5: Create xlsx_handler.py**

Extract these functions:
- `calculate_total_cols()` (line 59)
- `get_child_col_offsets()` (line 64)
- `validate_child_count()` (line 69)
- `read_provider_rates()` (line 131)
- `read_summer_assignments()` (line 181)
- `_vlookup_col_indices()` (line 1109)
- `update_xlsx()` (line 1125)

Add lazy openpyxl import:
```python
"""Excel spreadsheet reading and writing for camp schedules."""

import sys

from rate_resolver import _read_rate_block, resolve_period_rate


def _require_openpyxl():
    """Lazy-import openpyxl and return (openpyxl, get_column_letter) tuple."""
    try:
        import openpyxl
        from openpyxl.utils import get_column_letter
        return openpyxl, get_column_letter
    except ImportError:
        print("Error: openpyxl is required for Excel output. Install with: pip install openpyxl",
              file=sys.stderr)
        sys.exit(1)
```

Each function that needs openpyxl calls `openpyxl, get_column_letter = _require_openpyxl()` at its start. Functions that don't need `get_column_letter` can use `openpyxl, _ = _require_openpyxl()`.

- [ ] **Step 6: Create renderer.py**

Extract these functions:
- `_group_into_sections()` (line 1007)
- `render_markdown()` (line 801)

Add at the top (trace all stdlib dependencies from the extracted functions and include them — at minimum):
```python
"""Markdown rendering for annual camp schedules."""

from datetime import date

from rate_resolver import resolve_period_rate
```

Note: The implementer must trace all imports used by `render_markdown()` and `_group_into_sections()` and add them here.

- [ ] **Step 7: Update generate_annual_schedule.py entry point**

Replace the function definitions with imports. Keep `main()` and argument parsing. Add:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from calendar_parser import parse_calendar, parse_date_flexible, resolve_calendars
from rate_resolver import resolve_period_rate
from schedule_builder import build_annual_days, build_annual_days_multi
from xlsx_handler import (
    read_provider_rates, read_summer_assignments, update_xlsx,
    calculate_total_cols, get_child_col_offsets, validate_child_count,
)
from renderer import render_markdown
```

- [ ] **Step 8: Update test imports**

In `test_generate_annual_schedule.py`, update the imports to point to the new modules. Replace:

```python
from generate_annual_schedule import (
    parse_calendar,
    parse_date_flexible,
    ...
)
```

With imports from the specific modules:

```python
from calendar_parser import parse_calendar, parse_date_flexible, ...
from rate_resolver import resolve_period_rate, ...
from schedule_builder import build_annual_days, build_annual_days_multi
from xlsx_handler import update_xlsx, calculate_total_cols, ...
from renderer import render_markdown
from generate_annual_schedule import main
```

- [ ] **Step 9: Run tests to verify refactor**

Run: `cd kids-camp-planner && python3 -m pytest skills/generate-annual-schedule/scripts/test_generate_annual_schedule.py -v`
Expected: Same number of tests PASS as in Step 1. Zero failures.

- [ ] **Step 10: Commit**

```bash
git add kids-camp-planner/skills/generate-annual-schedule/scripts/
git commit -m "refactor(kids-camp-planner): split generate_annual_schedule.py into focused modules"
```

---

### Task 20: Version bump to 0.3.0

**Files:**
- Modify: `kids-camp-planner/.claude-plugin/plugin.json`
- Modify: `kids-camp-planner/README.md` (badge version)

- [ ] **Step 1: Update version in plugin.json**

Change `"version": "0.2.0"` to `"version": "0.3.0"`.

- [ ] **Step 2: Update version badge in README**

Change the version badge from `version-0.2.0-blue` to `version-0.3.0-blue`.

- [ ] **Step 3: Commit**

```bash
git add kids-camp-planner/.claude-plugin/plugin.json kids-camp-planner/README.md
git commit -m "chore(kids-camp-planner): bump version to 0.3.0"
```
