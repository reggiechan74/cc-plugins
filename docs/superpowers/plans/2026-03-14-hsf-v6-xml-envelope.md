# HSF v6: XML Envelope + Output Schemas Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade HSF from v5 to v6 — replace `@config`/`@route` with XML/JSON equivalents, add `<output-schema>`, wrap all sections in XML tags. No backward compatibility.

**Architecture:** The validator detects v6 by looking for XML section tags (`<purpose>`, `<instructions>`, etc.) instead of `## Section` markdown headers. Config validation parses JSON inside `<config>` instead of custom YAML-like `@config`. Route validation parses `<route>` XML elements instead of `@route` lines. New `<output-schema>` validation checks JSON presence for standard+ tiers. All HSF skill/reference/template/example files are rewritten for v6. Three command files updated.

**Tech Stack:** Python 3 (validator), Markdown (specs/skills/commands), pytest (tests)

**Spec:** `docs/superpowers/specs/2026-03-14-hsf-v6-xml-envelope-design.md`

---

## Chunk 1: Validator — Format Detection + XML Structure Validation

### Task 1: Update format detection to recognize HSF v6

**Files:**
- Modify: `structured-english/skills/hsf/scripts/validate_sesf.py:248-282` (detect_format_version)
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write failing test for v6 detection**

```python
def test_detect_format_v6():
    """HSF v6 is detected by XML section tags."""
    v6_spec = """\
---
title: Test Spec
tier: micro
---

<purpose>
Validate incoming webhook payloads.
</purpose>

<instructions>
### Phase 1: Check Payload

1. Parse the JSON body.
2. Validate required fields.
</instructions>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| parse_failure | critical | Reject with HTTP 400. |
</errors>
"""
    from validate_sesf import detect_format_version
    assert detect_format_version(v6_spec) == "hsf_v6"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_detect_format_v6 -v`
Expected: FAIL — returns "hsf_v5" or "unknown", not "hsf_v6"

- [ ] **Step 3: Update detect_format_version to detect v6**

In `validate_sesf.py`, update `detect_format_version()` to check for XML section tags before the existing v5/v4 checks:

```python
# Add at the top of detect_format_version, before existing checks:
# HSF v6: XML section tags
xml_section_tags = ['<purpose>', '<instructions>', '<scope>', '<config>', '<rules>', '<errors>', '<examples>', '<inputs>', '<outputs>']
xml_tag_count = sum(1 for tag in xml_section_tags if tag in text)
if xml_tag_count >= 2:
    return "hsf_v6"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_detect_format_v6 -v`
Expected: PASS

- [ ] **Step 5: Write test that v5 specs still detect as v5 (not v6)**

```python
def test_detect_format_v5_not_v6():
    """v5 specs with ## headers and @config should NOT detect as v6."""
    v5_spec = """\
# Test Spec

Purpose here.

## Instructions

Do things.

@config
  key: value

## Errors

| Error | Severity | Action |
|-------|----------|--------|
| err | critical | halt |
"""
    from validate_sesf import detect_format_version
    assert detect_format_version(v5_spec) == "hsf_v5"
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_detect_format_v5_not_v6 -v`
Expected: PASS (v5 detection should still work since XML tags aren't present)

- [ ] **Step 7: Commit**

```bash
git add structured-english/skills/hsf/scripts/validate_sesf.py structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "feat: detect HSF v6 format by XML section tags"
```

### Task 2: Add v6 XML structure validation

**Files:**
- Modify: `structured-english/skills/hsf/scripts/validate_sesf.py` (add `check_hsf_v6_structure` function)
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write failing test for v6 structure — valid micro spec**

```python
def test_v6_structure_valid_micro():
    """A valid v6 micro spec should pass structure checks."""
    spec = """\
<purpose>
Validate webhook payloads before forwarding.
</purpose>

<scope>
**Not in scope:** retry logic, authentication.
</scope>

<instructions>
1. Parse the JSON body.
2. Validate required fields.
3. Forward if valid.
</instructions>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| parse_failure | critical | Reject with HTTP 400. |
</errors>
"""
    from validate_sesf import check_hsf_v6_structure
    results = check_hsf_v6_structure(spec, "test.md")
    fails = [r for r in results if r.status == "FAIL"]
    assert len(fails) == 0, f"Unexpected failures: {[r.message for r in fails]}"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_structure_valid_micro -v`
Expected: FAIL — `check_hsf_v6_structure` doesn't exist yet

- [ ] **Step 3: Write check_hsf_v6_structure function**

Add to `validate_sesf.py`:

```python
def check_hsf_v6_structure(text: str, filepath: str) -> list:
    """Validate HSF v6 structural requirements — XML envelope with prose content."""
    results = []
    lines = text.split('\n')
    line_count = len([l for l in lines if l.strip()])
    tier = _detect_hsf_tier(text, line_count)

    results.append(ValidationResult(
        "hsf_v6_structure", "INFO",
        f"Detected HSF v6 format, inferred tier: {tier} ({line_count} non-empty lines)"
    ))

    # Build set of lines inside fenced code blocks
    in_code_block = set()
    inside = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            inside = not inside
            in_code_block.add(i)
            continue
        if inside:
            in_code_block.add(i)

    # --- Required sections ---
    # <purpose> is required at all tiers
    if '<purpose>' not in text:
        results.append(ValidationResult(
            "hsf_v6_structure", "FAIL",
            "Missing <purpose> section — required at all tiers"
        ))
    else:
        # Check it's not empty
        purpose_match = re.search(r'<purpose>\s*(.*?)\s*</purpose>', text, re.DOTALL)
        if purpose_match and not purpose_match.group(1).strip():
            results.append(ValidationResult(
                "hsf_v6_structure", "FAIL",
                "Empty <purpose> section — omit sections that have no content"
            ))
        else:
            results.append(ValidationResult(
                "hsf_v6_structure", "PASS",
                "<purpose> section present"
            ))

    # <instructions> is required at all tiers
    if '<instructions>' not in text:
        results.append(ValidationResult(
            "hsf_v6_structure", "FAIL",
            "Missing <instructions> section — required at all tiers"
        ))
    else:
        results.append(ValidationResult(
            "hsf_v6_structure", "PASS",
            "<instructions> section present"
        ))

    # <errors> is required at all tiers
    if '<errors>' not in text:
        results.append(ValidationResult(
            "hsf_v6_structure", "WARN",
            "No <errors> section found — specs SHOULD have a consolidated error table"
        ))
    else:
        results.append(ValidationResult(
            "hsf_v6_structure", "PASS",
            "<errors> section present"
        ))

    # --- Forbidden: ## markdown headers for top-level sections ---
    forbidden_md_sections = [
        'Purpose', 'Scope', 'Instructions', 'Rules', 'Errors',
        'Examples', 'Inputs', 'Outputs', 'Configuration', 'Config'
    ]
    for section in forbidden_md_sections:
        pattern = rf'^##\s+{section}\s*$'
        for i, line in enumerate(lines, 1):
            if i in in_code_block:
                continue
            if re.match(pattern, line.strip()):
                results.append(ValidationResult(
                    "hsf_v6_structure", "FAIL",
                    f"Forbidden '## {section}' header — HSF v6 uses XML tags (<{section.lower()}>) instead of markdown headers for top-level sections",
                    line_number=i
                ))

    # --- Forbidden formal keywords (same as v5) ---
    forbidden_keywords = [
        (r'^\s*BEHAVIOR\s+\w+', '**BEHAVIOR**'),
        (r'^\s*RULE\s+\w+', '**RULE**'),
        (r'^\s*PROCEDURE\s+\w+', '**PROCEDURE**'),
        (r'^\s*STEP\s+\w+', '**STEP**'),
    ]
    for pattern, keyword in forbidden_keywords:
        for i, line in enumerate(lines, 1):
            if i in in_code_block:
                continue
            norm_line = _normalize_for_matching(line)
            if re.match(pattern, norm_line):
                results.append(ValidationResult(
                    "hsf_v6_structure", "FAIL",
                    f"Forbidden keyword {keyword} found — HSF v6 uses prose with markdown headers",
                    line_number=i
                ))

    # --- Forbidden: @config and @route (replaced by XML) ---
    for i, line in enumerate(lines, 1):
        if i in in_code_block:
            continue
        if re.match(r'^\s*@config\s*$', line.strip()):
            results.append(ValidationResult(
                "hsf_v6_structure", "FAIL",
                "@config is replaced by <config> with JSON body in HSF v6",
                line_number=i
            ))
        if re.match(r'^\s*@route\s+', line.strip()):
            results.append(ValidationResult(
                "hsf_v6_structure", "FAIL",
                "@route is replaced by <route> XML elements in HSF v6",
                line_number=i
            ))

    # --- Forbidden: $config.key references (should be config.key without $) ---
    for i, line in enumerate(lines, 1):
        if i in in_code_block:
            continue
        if '$config.' in line:
            results.append(ValidationResult(
                "hsf_v6_structure", "WARN",
                "Use `config.key` instead of `$config.key` — the $ prefix is reserved for $variable threading in v6",
                line_number=i
            ))

    # --- Empty XML sections check (section-level tags only) ---
    section_tags = '|'.join(['purpose', 'scope', 'inputs', 'outputs', 'config', 'instructions', 'rules', 'errors', 'examples'])
    for m in re.finditer(rf'<({section_tags})>\s*</\1>', text, re.DOTALL):
        results.append(ValidationResult(
            "hsf_v6_structure", "FAIL",
            f"Empty <{m.group(1)}> section — omit sections that have no content"
        ))

    # --- Section order check ---
    section_order = ['purpose', 'scope', 'inputs', 'outputs', 'config', 'instructions', 'rules', 'errors', 'examples']
    found_sections = []
    for tag in section_order:
        match = re.search(rf'<{tag}>', text)
        if match:
            found_sections.append((tag, match.start()))

    for idx in range(len(found_sections) - 1):
        if found_sections[idx][1] > found_sections[idx + 1][1]:
            results.append(ValidationResult(
                "hsf_v6_structure", "WARN",
                f"<{found_sections[idx][0]}> appears after <{found_sections[idx + 1][0]}> — sections SHOULD follow standard order: {', '.join(section_order)}"
            ))

    # --- Line budget check ---
    budget = {"micro": 80, "standard": 200, "complex": 400}
    max_lines = budget.get(tier, 400)
    if line_count > max_lines:
        results.append(ValidationResult(
            "hsf_v6_structure", "WARN",
            f"Spec has {line_count} non-empty lines, exceeding {tier} tier budget of {max_lines}"
        ))
    else:
        results.append(ValidationResult(
            "hsf_v6_structure", "PASS",
            f"Line budget OK ({line_count}/{max_lines} for {tier} tier)"
        ))

    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_structure_valid_micro -v`
Expected: PASS

- [ ] **Step 5: Write failing test for v6 structure — forbidden ## headers**

```python
def test_v6_structure_forbidden_markdown_headers():
    """v6 specs MUST NOT use ## headers for top-level sections."""
    spec = """\
<purpose>
Test spec.
</purpose>

## Instructions

Do things.

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| err | critical | halt |
</errors>
"""
    from validate_sesf import check_hsf_v6_structure
    results = check_hsf_v6_structure(spec, "test.md")
    fails = [r for r in results if r.status == "FAIL"]
    fail_msgs = [r.message for r in fails]
    assert any("## Instructions" in m for m in fail_msgs), f"Expected forbidden header failure, got: {fail_msgs}"
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_structure_forbidden_markdown_headers -v`
Expected: PASS (the function already checks for this)

- [ ] **Step 7: Write failing test for forbidden @config/@route**

```python
def test_v6_structure_forbidden_at_config():
    """v6 specs MUST NOT use @config — use <config> with JSON instead."""
    spec = """\
<purpose>
Test spec.
</purpose>

@config
  key: value
  key2: value2
  key3: value3

<instructions>
Do things.
</instructions>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| err | critical | halt |
</errors>
"""
    from validate_sesf import check_hsf_v6_structure
    results = check_hsf_v6_structure(spec, "test.md")
    fails = [r for r in results if r.status == "FAIL"]
    fail_msgs = [r.message for r in fails]
    assert any("@config is replaced" in m for m in fail_msgs), f"Expected @config forbidden failure, got: {fail_msgs}"
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_structure_forbidden_at_config -v`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add structured-english/skills/hsf/scripts/validate_sesf.py structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "feat: add HSF v6 XML structure validation"
```

### Task 3: Add v6 JSON config validation

**Files:**
- Modify: `structured-english/skills/hsf/scripts/validate_sesf.py` (add `check_hsf_v6_config`)
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write failing test for valid JSON config**

```python
def test_v6_config_valid_json():
    """<config> with valid JSON should pass."""
    spec = """\
<config>
{
  "max_retries": 3,
  "timeout_ms": 30000,
  "output_dir": "/tmp/results/"
}
</config>
"""
    from validate_sesf import check_hsf_v6_config
    results = check_hsf_v6_config(spec)
    fails = [r for r in results if r.status == "FAIL"]
    assert len(fails) == 0
    passes = [r for r in results if r.status == "PASS"]
    assert len(passes) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_config_valid_json -v`
Expected: FAIL — function doesn't exist

- [ ] **Step 3: Write check_hsf_v6_config function**

```python
def check_hsf_v6_config(text: str) -> list:
    """Validate <config> block contains valid JSON in HSF v6."""
    results = []
    import json

    config_match = re.search(r'<config>\s*(.*?)\s*</config>', text, re.DOTALL)
    if not config_match:
        return results

    config_body = config_match.group(1).strip()
    if not config_body:
        results.append(ValidationResult(
            "hsf_v6_config", "FAIL",
            "Empty <config> section — omit if no configuration values"
        ))
        return results

    # Parse JSON
    try:
        config_obj = json.loads(config_body)
    except json.JSONDecodeError as e:
        results.append(ValidationResult(
            "hsf_v6_config", "FAIL",
            f"<config> contains invalid JSON: {e}"
        ))
        return results

    if not isinstance(config_obj, dict):
        results.append(ValidationResult(
            "hsf_v6_config", "FAIL",
            "<config> JSON must be an object (not array or scalar)"
        ))
        return results

    config_keys = set(config_obj.keys())

    # Check snake_case keys
    for key in config_keys:
        if key != key.lower() or ' ' in key or '-' in key:
            results.append(ValidationResult(
                "hsf_v6_config", "WARN",
                f"Config key '{key}' SHOULD use snake_case"
            ))

    # Find config.key references in the text (outside <config> block)
    text_without_config = text[:config_match.start()] + text[config_match.end():]
    config_refs = set(re.findall(r'(?<!\$)config\.([a-zA-Z_][a-zA-Z0-9_.]*)', text_without_config))

    # Check for references to undefined keys
    for ref in config_refs:
        top_key = ref.split('.')[0]
        if top_key not in config_keys:
            results.append(ValidationResult(
                "hsf_v6_config", "WARN",
                f"config.{ref} referenced but '{top_key}' not found in <config> JSON"
            ))

    # Check for fewer than 3 values
    if len(config_keys) < 3:
        results.append(ValidationResult(
            "hsf_v6_config", "WARN",
            f"<config> has {len(config_keys)} keys — use inline prose for fewer than 3 values"
        ))

    results.append(ValidationResult(
        "hsf_v6_config", "PASS",
        f"<config> with {len(config_keys)} keys, valid JSON"
    ))

    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_config_valid_json -v`
Expected: PASS

- [ ] **Step 5: Write test for invalid JSON config**

```python
def test_v6_config_invalid_json():
    """<config> with invalid JSON should fail."""
    spec = """\
<config>
  max_retries: 3
  timeout_ms: 30000
</config>
"""
    from validate_sesf import check_hsf_v6_config
    results = check_hsf_v6_config(spec)
    fails = [r for r in results if r.status == "FAIL"]
    assert len(fails) >= 1
    assert any("invalid JSON" in r.message for r in fails)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_config_invalid_json -v`
Expected: PASS

- [ ] **Step 7: Write test for config reference to undefined key**

```python
def test_v6_config_undefined_ref():
    """References to config keys not in <config> JSON should warn."""
    spec = """\
<config>
{
  "max_retries": 3,
  "timeout_ms": 30000,
  "output_dir": "/tmp/"
}
</config>

<instructions>
If the count exceeds `config.max_items`, reject it.
</instructions>
"""
    from validate_sesf import check_hsf_v6_config
    results = check_hsf_v6_config(spec)
    warns = [r for r in results if r.status == "WARN"]
    assert any("max_items" in r.message for r in warns)
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_config_undefined_ref -v`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add structured-english/skills/hsf/scripts/validate_sesf.py structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "feat: add HSF v6 JSON config validation"
```

### Task 4: Add v6 XML route validation

**Files:**
- Modify: `structured-english/skills/hsf/scripts/validate_sesf.py` (add `check_hsf_v6_routes`)
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write failing test for valid route**

```python
def test_v6_route_valid():
    """A valid <route> with 3+ cases should pass."""
    spec = """\
<route name="doc_type" mode="first_match_wins">
  <case when="has invoice header">invoice processing</case>
  <case when="has PO number">purchase order processing</case>
  <case when="has packing slip">shipping doc processing</case>
  <default>manual review</default>
</route>
"""
    from validate_sesf import check_hsf_v6_routes
    results = check_hsf_v6_routes(spec)
    fails = [r for r in results if r.status == "FAIL"]
    assert len(fails) == 0
    passes = [r for r in results if r.status == "PASS"]
    assert len(passes) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_route_valid -v`
Expected: FAIL — function doesn't exist

- [ ] **Step 3: Write check_hsf_v6_routes function**

```python
def check_hsf_v6_routes(text: str) -> list:
    """Validate <route> elements in HSF v6 specs."""
    results = []

    # Match <route ...> with any attribute order
    route_pattern = re.compile(
        r'<route\s+([^>]+)>(.*?)</route>',
        re.DOTALL
    )

    for match in route_pattern.finditer(text):
        attrs_str = match.group(1)
        body = match.group(2)
        line_num = text[:match.start()].count('\n') + 1

        # Extract name and mode from attributes (order-independent)
        name_match = re.search(r'name="([^"]+)"', attrs_str)
        mode_match = re.search(r'mode="([^"]+)"', attrs_str)

        name = name_match.group(1) if name_match else "(unnamed)"
        mode = mode_match.group(1) if mode_match else None

        if not name_match:
            results.append(ValidationResult(
                "hsf_v6_routes", "FAIL",
                f"<route> missing required name attribute",
                line_number=line_num
            ))

        if not mode_match:
            results.append(ValidationResult(
                "hsf_v6_routes", "WARN",
                f"<route name=\"{name}\"> missing mode attribute — defaults to first_match_wins",
                line_number=line_num
            ))
        elif mode not in ('first_match_wins', 'all_matches'):
            results.append(ValidationResult(
                "hsf_v6_routes", "FAIL",
                f"<route name=\"{name}\"> has invalid mode '{mode}' — must be first_match_wins or all_matches",
                line_number=line_num
            ))

        # Count <case> elements
        cases = re.findall(r'<case\s+when="[^"]*">', body)
        has_default = '<default>' in body

        if len(cases) < 3:
            results.append(ValidationResult(
                "hsf_v6_routes", "WARN",
                f"<route name=\"{name}\"> has {len(cases)} cases — use prose conditionals for fewer than 3 branches",
                line_number=line_num
            ))
        else:
            results.append(ValidationResult(
                "hsf_v6_routes", "PASS",
                f"<route name=\"{name}\"> has {len(cases)} cases" + (" + default" if has_default else ""),
                line_number=line_num
            ))

    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_route_valid -v`
Expected: PASS

- [ ] **Step 5: Write test for route with too few branches**

```python
def test_v6_route_under_threshold():
    """<route> with fewer than 3 cases should warn."""
    spec = """\
<route name="size_check" mode="first_match_wins">
  <case when="file size > 10MB">reject</case>
  <default>accept</default>
</route>
"""
    from validate_sesf import check_hsf_v6_routes
    results = check_hsf_v6_routes(spec)
    warns = [r for r in results if r.status == "WARN"]
    assert len(warns) >= 1
    assert any("fewer than 3" in r.message for r in warns)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_route_under_threshold -v`
Expected: PASS

- [ ] **Step 7: Write test for invalid mode attribute**

```python
def test_v6_route_invalid_mode():
    """<route> with invalid mode should fail."""
    spec = """\
<route name="classifier" mode="best_match">
  <case when="condition A">outcome A</case>
  <case when="condition B">outcome B</case>
  <case when="condition C">outcome C</case>
</route>
"""
    from validate_sesf import check_hsf_v6_routes
    results = check_hsf_v6_routes(spec)
    fails = [r for r in results if r.status == "FAIL"]
    assert len(fails) >= 1
    assert any("invalid mode" in r.message for r in fails)
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_route_invalid_mode -v`
Expected: PASS

- [ ] **Step 9: Write test for route with reversed attribute order**

```python
def test_v6_route_reversed_attrs():
    """<route> with mode before name should still be detected."""
    spec = """\
<route mode="first_match_wins" name="classifier">
  <case when="condition A">outcome A</case>
  <case when="condition B">outcome B</case>
  <case when="condition C">outcome C</case>
</route>
"""
    from validate_sesf import check_hsf_v6_routes
    results = check_hsf_v6_routes(spec)
    passes = [r for r in results if r.status == "PASS"]
    assert len(passes) >= 1
    assert any("classifier" in r.message for r in passes)
```

- [ ] **Step 10: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_route_reversed_attrs -v`
Expected: PASS

- [ ] **Step 11: Commit**

```bash
git add structured-english/skills/hsf/scripts/validate_sesf.py structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "feat: add HSF v6 XML route validation"
```

### Task 4b: Add tests for $config.key warning, empty sections, and section order

**Files:**
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write test for $config.key warning**

```python
def test_v6_dollar_config_warning():
    """$config.key should warn — use config.key in v6."""
    spec = """\
<purpose>
Test spec.
</purpose>

<instructions>
If the count exceeds `$config.max_items`, reject it.
</instructions>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| err | critical | halt |
</errors>
"""
    from validate_sesf import check_hsf_v6_structure
    results = check_hsf_v6_structure(spec, "test.md")
    warns = [r for r in results if r.status == "WARN"]
    assert any("$config" in r.message for r in warns)
```

- [ ] **Step 2: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_dollar_config_warning -v`
Expected: PASS

- [ ] **Step 3: Write test for empty XML section detection**

```python
def test_v6_empty_section_detected():
    """Empty XML section tags like <rules></rules> should fail."""
    spec = """\
<purpose>
Test spec.
</purpose>

<instructions>
Do things.
</instructions>

<rules></rules>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| err | critical | halt |
</errors>
"""
    from validate_sesf import check_hsf_v6_structure
    results = check_hsf_v6_structure(spec, "test.md")
    fails = [r for r in results if r.status == "FAIL"]
    assert any("Empty <rules>" in r.message for r in fails)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_empty_section_detected -v`
Expected: PASS

- [ ] **Step 5: Write test for section order violation**

```python
def test_v6_section_order_warning():
    """Sections out of standard order should warn."""
    spec = """\
<instructions>
Do things.
</instructions>

<purpose>
Test spec.
</purpose>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| err | critical | halt |
</errors>
"""
    from validate_sesf import check_hsf_v6_structure
    results = check_hsf_v6_structure(spec, "test.md")
    warns = [r for r in results if r.status == "WARN"]
    assert any("order" in r.message.lower() for r in warns)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_section_order_warning -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "test: add HSF v6 edge case tests — $config warning, empty sections, order"
```

### Task 5: Add v6 output-schema validation

**Files:**
- Modify: `structured-english/skills/hsf/scripts/validate_sesf.py` (add `check_hsf_v6_output_schema`)
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write failing test for valid output-schema**

```python
def test_v6_output_schema_valid():
    """A valid <output-schema> with JSON should pass."""
    spec = """\
<output-schema format="json">
{
  "id": "string",
  "status": "pass | fail",
  "items": ["string"]
}
</output-schema>
"""
    from validate_sesf import check_hsf_v6_output_schema
    results = check_hsf_v6_output_schema(spec, "standard")
    fails = [r for r in results if r.status == "FAIL"]
    assert len(fails) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_output_schema_valid -v`
Expected: FAIL — function doesn't exist

- [ ] **Step 3: Write check_hsf_v6_output_schema function**

```python
def check_hsf_v6_output_schema(text: str, tier: str) -> list:
    """Validate <output-schema> blocks in HSF v6 specs."""
    results = []

    schema_pattern = re.compile(
        r'<output-schema\s+format="([^"]+)"\s*>(.*?)</output-schema>',
        re.DOTALL
    )

    schemas = list(schema_pattern.finditer(text))

    if not schemas and tier in ('standard', 'complex'):
        # Check if there's structured output mentioned without a schema
        has_structured_output = bool(re.search(
            r'(?:generate|produce|output|return)\s+(?:a\s+)?(?:structured|JSON|json)',
            text, re.IGNORECASE
        ))
        if has_structured_output:
            results.append(ValidationResult(
                "hsf_v6_output_schema", "WARN",
                "Spec mentions structured output but has no <output-schema> — SHOULD include one for standard+ tiers"
            ))
        return results

    for match in schemas:
        fmt = match.group(1)
        body = match.group(2).strip()
        line_num = text[:match.start()].count('\n') + 1

        if fmt != "json":
            results.append(ValidationResult(
                "hsf_v6_output_schema", "WARN",
                f"<output-schema format=\"{fmt}\"> — only 'json' is currently supported",
                line_number=line_num
            ))

        if not body:
            results.append(ValidationResult(
                "hsf_v6_output_schema", "FAIL",
                "Empty <output-schema> block",
                line_number=line_num
            ))
        else:
            # Note: output-schema body is pseudo-JSON with descriptive type
            # annotations like "string", "float 0.0-1.0", "string | null".
            # These are not valid JSON values, so we do NOT json.loads() the body.
            # We only check that it's non-empty and structurally looks like JSON
            # (starts with { or [).
            stripped_body = body.strip()
            if not (stripped_body.startswith('{') or stripped_body.startswith('[')):
                results.append(ValidationResult(
                    "hsf_v6_output_schema", "WARN",
                    f"<output-schema format=\"json\"> body doesn't look like JSON — expected to start with {{ or [",
                    line_number=line_num
                ))
            results.append(ValidationResult(
                "hsf_v6_output_schema", "PASS",
                f"<output-schema> present with {fmt} format",
                line_number=line_num
            ))

    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_output_schema_valid -v`
Expected: PASS

- [ ] **Step 5: Write test for missing output-schema when structured output mentioned**

```python
def test_v6_output_schema_missing_warn():
    """Standard+ specs mentioning structured output without <output-schema> should warn."""
    spec = """\
<instructions>
### Phase 3: Output

Generate a structured JSON record containing the results.
</instructions>
"""
    from validate_sesf import check_hsf_v6_output_schema
    results = check_hsf_v6_output_schema(spec, "standard")
    warns = [r for r in results if r.status == "WARN"]
    assert len(warns) >= 1
    assert any("output-schema" in r.message.lower() for r in warns)
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_output_schema_missing_warn -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add structured-english/skills/hsf/scripts/validate_sesf.py structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "feat: add HSF v6 output-schema validation"
```

### Task 6: Wire up v6 validation pipeline + update main()

**Files:**
- Modify: `structured-english/skills/hsf/scripts/validate_sesf.py` (add `validate_hsf_v6`, update `main`)
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write failing test for full v6 validation pipeline**

```python
def test_v6_full_validation_standard():
    """Full v6 validation on a valid standard spec should have no failures."""
    spec = """\
---
title: Test Processor
tier: standard
---

<purpose>
Process test documents through classification and extraction.
</purpose>

<scope>
**In scope:**
- Document classification
- Field extraction

**Not in scope:**
- Payment processing
</scope>

<config>
{
  "max_pages": 50,
  "confidence_threshold": 0.85,
  "output_format": "JSON"
}
</config>

<instructions>
### Phase 1: Classify

1. Read the document header.
2. Classify using the route table:

<route name="doc_type" mode="first_match_wins">
  <case when="has invoice header">invoice</case>
  <case when="has PO number">purchase order</case>
  <case when="has packing slip">shipping doc</case>
  <default>unclassified</default>
</route>

### Phase 2: Extract

Extract fields based on classification. If confidence is below `config.confidence_threshold`, flag for review.

### Phase 3: Output

Generate the result:

<output-schema format="json">
{
  "doc_type": "string",
  "fields": {
    "[field_name]": {
      "value": "string | null",
      "confidence": "float 0.0-1.0"
    }
  },
  "requires_review": "boolean"
}
</output-schema>
</instructions>

<rules>
- **No modification:** MUST NOT alter extracted values. Flag incorrect values instead.
- **Audit trail:** EVERY decision MUST be logged with timestamp.
</rules>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| unsupported_format | critical | Reject with supported format list. |
| low_confidence | warning | Flag for review, continue processing. |
</errors>

<examples>
confidence_at_threshold: confidence=0.85 exactly → passes (threshold is "below 0.85")
</examples>
"""
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(spec)
    try:
        from validate_sesf import validate_hsf_v6, _strip_yaml_frontmatter
        stripped = _strip_yaml_frontmatter(spec)
        results = validate_hsf_v6(stripped, path)
        fails = [r for r in results if r.status == "FAIL"]
        assert len(fails) == 0, f"Unexpected failures: {[r.message for r in fails]}"
    finally:
        os.unlink(path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_full_validation_standard -v`
Expected: FAIL — `validate_hsf_v6` doesn't exist

- [ ] **Step 3: Write validate_hsf_v6 and update main()**

Add `validate_hsf_v6`:

```python
def validate_hsf_v6(text: str, filepath: str) -> list:
    """Run all HSF v6 validation checks."""
    results = []
    results.extend(check_hsf_v6_structure(text, filepath))

    # Determine tier for output-schema check
    lines = text.split('\n')
    line_count = len([l for l in lines if l.strip()])
    tier = _detect_hsf_tier(text, line_count)

    results.extend(check_hsf_v6_config(text))
    results.extend(check_hsf_v6_routes(text))
    results.extend(check_hsf_v6_output_schema(text, tier))
    results.extend(check_hsf_variable_threading(text))
    results.extend(check_hsf_rfc2119(text))
    return results
```

Update `main()` — add v6 detection branch before v5:

```python
# In main(), after format_version detection:
if format_version == 'hsf_v6':
    print(f"  Detected format: HSF v6 (XML Envelope)")
    results = validate_hsf_v6(stripped_text, filepath)
elif format_version == 'hsf_v5':
    # ... existing v5 code
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_full_validation_standard -v`
Expected: PASS

- [ ] **Step 5: Run full test suite to ensure nothing is broken**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py -v`
Expected: All existing tests still pass + all new v6 tests pass

- [ ] **Step 6: Commit**

```bash
git add structured-english/skills/hsf/scripts/validate_sesf.py structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "feat: wire up HSF v6 full validation pipeline"
```

## Chunk 2: Skill Files — Reference, Template, Examples

### Task 7: Rewrite HSF skill SKILL.md for v6

**Files:**
- Modify: `structured-english/skills/hsf/SKILL.md`

The SKILL.md needs to be rewritten to describe v6 rules instead of v5. Key changes:

- [ ] **Step 1: Read current SKILL.md for full context**

Run: Read `structured-english/skills/hsf/SKILL.md` (already read in exploration)

- [ ] **Step 2: Rewrite SKILL.md for v6**

Replace the entire file. Key changes throughout:

1. Description: "HSF v6" instead of "HSF v5", mention XML envelope + JSON config + output-schema
2. Configuration section: use `<config>` with JSON, not `@config` with YAML-like syntax
3. `validator_path`, `reference_path`, `template_path`, `examples_path` stay the same (same file locations)
4. Instructions section "How to Structure the Document": replace `##` section headers with XML tags, keep `###` for phases
5. "How to Use @route and @config" becomes "How to Use `<route>` and `<config>`" with XML/JSON syntax
6. Add new section "How to Use `<output-schema>`"
7. Rules section: update "Format Compliance" to forbid `@config`, `@route`, `##` section headers; require XML tags
8. Rules section: update "Notation Usage" to reference XML elements instead of `@` notation
9. Update `$config.key` → `config.key` throughout
10. Quality Checklist: update for v6 checks
11. Errors table: update error names/messages for v6

- [ ] **Step 3: Validate the rewritten SKILL.md is internally consistent**

Read through the rewritten file and verify no v5 references remain outside of code examples showing "what not to do."

- [ ] **Step 4: Commit**

```bash
git add structured-english/skills/hsf/SKILL.md
git commit -m "feat: rewrite HSF skill for v6 — XML envelope, JSON config, output-schema"
```

### Task 8: Rewrite reference.md for v6

**Files:**
- Modify: `structured-english/skills/hsf/assets/reference.md`

- [ ] **Step 1: Rewrite reference.md**

Key changes throughout:

1. Opening paragraph: update to reference XML envelope, JSON config, XML route, output-schema
2. "Section Reference": show XML tags instead of `##` headers, same order
3. "Configuration" section: show `<config>` with JSON body, `config.key` references (no `$` prefix)
4. "@config" becomes "`<config>` — JSON Configuration" with JSON syntax and rules
5. "@route" becomes "`<route>` — Decision Tables" with XML `<case>`/`<default>` syntax
6. Add new "`<output-schema>` — Structured Output Specification" section
7. "$variable Threading" stays the same
8. "ERROR Table Format" shows the table inside `<errors>` tags
9. "EXAMPLES Format" shows content inside `<examples>` tags
10. "Requirement Keywords" stays the same
11. "Writing Rules" section: update examples to show rules inside `<rules>` tags
12. "Converting Rules to Prose": update "After" example to show v6 format (inside `<rules>` or `<instructions>`)
13. "Quality Checklist" and "Anti-Patterns" tables: update for v6
14. All tier examples: rewrite in v6 format with XML envelope

- [ ] **Step 2: Commit**

```bash
git add structured-english/skills/hsf/assets/reference.md
git commit -m "feat: rewrite HSF reference for v6 — XML envelope, JSON config, output-schema"
```

### Task 9: Rewrite template.md for v6

**Files:**
- Modify: `structured-english/skills/hsf/assets/template.md`

- [ ] **Step 1: Rewrite template.md**

Key changes:

1. "What is new" section: update for v6
2. Micro template: XML envelope (`<purpose>`, `<instructions>`, `<errors>`), no `<config>` or `<route>` at micro
3. Standard template: full XML envelope, `<config>` with JSON placeholder, `<route>` with XML case syntax, `<output-schema>` placeholder
4. Complex template: same as standard plus `<inputs>`, `<outputs>`, `$variable` threading, `<output-schema>`
5. Notes for each tier: update to reference XML tags instead of `##` headers

- [ ] **Step 2: Commit**

```bash
git add structured-english/skills/hsf/assets/template.md
git commit -m "feat: rewrite HSF templates for v6 — XML envelope structure"
```

### Task 10: Rewrite examples.md for v6

**Files:**
- Modify: `structured-english/skills/hsf/references/examples.md`

- [ ] **Step 1: Rewrite examples.md**

Convert all three tier examples to v6 format:

1. **Micro (Webhook Signature Validator):** Wrap in `<purpose>`, `<scope>` (or inline "Not in scope"), `<instructions>`, `<errors>`. No `<config>` (only 2 values → inline). No `<route>` (no multi-branch decisions).
2. **Standard (Document Processing Pipeline):** Full XML envelope. `<config>` with JSON body. `<route>` with XML cases. `<output-schema>` in the output phase. `<rules>`, `<errors>`, `<examples>`.
3. **Complex (Multi-Phase Meeting Analysis):** Full XML envelope. `<config>` with JSON. Two `<route>` tables inside `<instructions>`. `$variable` threading preserved. `<output-schema>` in deliverable phase. `<rules>`, `<errors>`, `<examples>`.

All `$config.key` references → `config.key`. All `@config` → `<config>` with JSON. All `@route` → `<route>` with XML.

- [ ] **Step 2: Commit**

```bash
git add structured-english/skills/hsf/references/examples.md
git commit -m "feat: rewrite HSF examples for v6 — all three tiers in XML envelope format"
```

## Chunk 3: Command Files

### Task 11: Update write-LLM-spec.md

**Files:**
- Modify: `structured-english/commands/write-LLM-spec.md`

- [ ] **Step 1: Update write-LLM-spec.md**

Key changes:

1. Description line: "HSF v6" instead of "HSF v5"
2. Audience section: add "XML section tags for unambiguous structure" to the optimization list
3. Step 3 (Select Tier): update notation elements list — `<config>` replaces `@config`, `<route>` replaces `@route`, add `<output-schema>`
4. Step 4 (Write): update rule list — XML tags for sections, no `##` headers, `<config>` with JSON, `<route>` with XML cases, `<output-schema>` for structured outputs, `config.key` not `$config.key`
5. LLM-specific optimizations: add "Use XML tags for section boundaries — LLMs parse these with near-perfect accuracy"

- [ ] **Step 2: Commit**

```bash
git add structured-english/commands/write-LLM-spec.md
git commit -m "feat: update write-LLM-spec command for HSF v6"
```

### Task 12: Update assess-LLM-doc.md

**Files:**
- Modify: `structured-english/commands/assess-LLM-doc.md`

- [ ] **Step 1: Update assess-LLM-doc.md**

Key changes:

1. Step 3 (Assess): add signal FOR conversion: "Document specifies structured output but has no schema — `<output-schema>` would improve LLM compliance with output shape"
2. Step 3: add signal FOR conversion: "Document uses markdown headers for section boundaries — XML tags provide more reliable parsing for LLMs"
3. Step 4 (Present Assessment): update suggested features to include XML envelope and output-schema
4. References to "HSF v5" → "HSF v6"

- [ ] **Step 2: Commit**

```bash
git add structured-english/commands/assess-LLM-doc.md
git commit -m "feat: update assess-LLM-doc command for HSF v6"
```

### Task 13: Update convert-human-to-llm.md

**Files:**
- Modify: `structured-english/commands/convert-human-to-llm.md`

- [ ] **Step 1: Update convert-human-to-llm.md**

Key changes:

1. Title/description: "HSF v6" instead of "HSF v5"
2. "When to Use" section: update format names
3. Step 2: update detection — if it looks like HSF v6 (has XML section tags), say "already in HSF v6 format"
4. Step 3 (Analyze and Map): update the conversion mapping table per the design spec:
   - `@config` block → `<config>` with JSON body
   - `@route` table → `<route>` with `<case>`/`<default>` elements
   - `## Section` headers → XML section tags
   - `$config.key` references → `config.key`
5. Key decisions: add "Output schema: For phases that produce structured output, add `<output-schema>` blocks"
6. Step 5 (Convert): update to output v6 format — XML envelope, JSON config, XML routes
7. LLM optimizations: add "Wrap sections in XML tags for unambiguous boundaries"

- [ ] **Step 2: Commit**

```bash
git add structured-english/commands/convert-human-to-llm.md
git commit -m "feat: update convert-human-to-llm command for HSF v6"
```

## Chunk 4: Integration Test + Final Validation

### Task 14: End-to-end validation test

**Files:**
- Test: `structured-english/skills/hsf/scripts/test_validate_sesf.py`

- [ ] **Step 1: Write integration test — run validator CLI on a v6 spec file**

```python
def test_v6_cli_end_to_end():
    """Running the validator CLI on a v6 spec should exit 0."""
    import subprocess, tempfile, os
    spec = """\
---
title: E2E Test Spec
tier: micro
---

<purpose>
Validate test payloads.
</purpose>

<scope>
**Not in scope:** retry logic.
</scope>

<instructions>
1. Parse the input.
2. Validate required fields.
3. Return result.
</instructions>

<errors>
| Error | Severity | Action |
|-------|----------|--------|
| parse_failure | critical | Reject with error message. |
</errors>
"""
    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(spec)
    try:
        script = os.path.join(os.path.dirname(__file__), "validate_sesf.py")
        result = subprocess.run(
            ["python3", script, path],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Validator failed:\n{result.stdout}\n{result.stderr}"
        assert "HSF v6" in result.stdout
    finally:
        os.unlink(path)
```

- [ ] **Step 2: Run test**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py::test_v6_cli_end_to_end -v`
Expected: PASS

- [ ] **Step 3: Run the validator on the design spec's full example**

Extract the full example from the design spec and run the validator on it to verify it passes.

Run: `cd structured-english/skills/hsf/scripts && python3 validate_sesf.py <temp-file-with-example>`
Expected: 0 failures

- [ ] **Step 4: Run complete test suite**

Run: `cd structured-english/skills/hsf/scripts && python3 -m pytest test_validate_sesf.py -v`
Expected: ALL tests pass (old SESF tests + old HSF v5 tests + new v6 tests)

- [ ] **Step 5: Commit**

```bash
git add structured-english/skills/hsf/scripts/test_validate_sesf.py
git commit -m "test: add HSF v6 end-to-end validator test"
```
