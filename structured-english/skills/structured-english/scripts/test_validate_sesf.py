#!/usr/bin/env python3
"""Tests for SESF v3/v4 validator — PROCEDURE, ACTION, and hybrid element support.

Run:  python3 -m pytest test_validate_sesf.py -v
  or: python3 test_validate_sesf.py
"""

import os
import sys
import tempfile

# Ensure the script directory is on the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_sesf import (
    parse_sesf,
    SESFDocument,
    ValidationResult,
    check_config_references,
    check_variable_threading,
    check_route_completeness,
    check_error_table_structure,
    check_notation_section,
    check_structural_completeness,
    check_cross_behavior,
    check_example_consistency,
    check_error_consistency,
    check_type_consistency,
)


def _write_temp_spec(spec: str) -> str:
    """Write a spec string to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".md", prefix="sesf_test_")
    with os.fdopen(fd, "w") as f:
        f.write(spec)
    return path


# ──────────────────────────────────────────────────────────────────────────
# Test 1: Parse a PROCEDURE block in a micro spec
# ──────────────────────────────────────────────────────────────────────────

def test_parse_procedure_block():
    spec = """\
Daily Report Generator

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Reporting | Status: active | Tier: micro

Purpose
Generate a daily sales summary report from transaction data.

PROCEDURE generate_report: Produce a formatted daily sales report

  STEP gather_data:
    COLLECT all transactions from the current business day

  STEP aggregate:
    COMPUTE total_sales as SUM of transaction amounts
    COMPUTE transaction_count as COUNT of transactions

  STEP format_output:
    PRODUCE a markdown report with date, total_sales, transaction_count

  ERROR no_transactions:
    WHEN transaction_count equals 0
    SEVERITY warning
    ACTION return empty report with note
    MESSAGE "No transactions found for the reporting period"

  EXAMPLE typical_day:
    INPUT: transactions for 2026-03-01 with 3 sales totaling $150.00
    EXPECTED: report showing date=2026-03-01, total=$150.00, count=3

Constraints
* Report covers a single calendar day only
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.procedures) == 1, (
            f"Expected 1 procedure, got {len(doc.procedures)}"
        )
        proc = doc.procedures[0]
        assert proc.name == "generate_report", (
            f"Expected name 'generate_report', got '{proc.name}'"
        )
        assert len(proc.steps) == 3, (
            f"Expected 3 steps, got {len(proc.steps)}"
        )
        assert proc.steps[0].name == "gather_data"
        assert proc.steps[1].name == "aggregate"
        assert proc.steps[2].name == "format_output"
        assert len(proc.errors) == 1, (
            f"Expected 1 error, got {len(proc.errors)}"
        )
        assert proc.errors[0].name == "no_transactions"
        assert len(proc.examples) == 1, (
            f"Expected 1 example, got {len(proc.examples)}"
        )
        assert proc.examples[0].name == "typical_day"
        print("  PASS  test_parse_procedure_block")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 2: Parse ACTION declaration in Functions section
# ──────────────────────────────────────────────────────────────────────────

def test_parse_action_declaration():
    spec = """\
Order Processor

Meta
* Version: 1.0.0
* Date: 2026-03-01
* Domain: E-commerce
* Status: active
* Tier: standard

Purpose
Process incoming orders through validation and fulfillment.

Scope
* IN SCOPE: order validation, payment processing
* OUT OF SCOPE: shipping logistics

Inputs
* order: Order - the incoming order - required

Outputs
* result: ProcessingResult - outcome of processing

Types

Order {
  id: string, required
  amount: number, required
}

ProcessingResult {
  status: string, required
}

Functions
FUNCTION validate_order(order: Order) -> boolean
ACTION send_confirmation(order: Order) -> void

BEHAVIOR process_order: Validate and process an incoming order

  RULE check_amount:
    WHEN order.amount > 0
    THEN validate_order(order)

  EXAMPLE valid_order:
    INPUT: order with amount=50.00
    EXPECTED: { "status": "processed" }

Constraints
* Orders with zero or negative amounts are rejected

Dependencies
* Payment gateway API
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert "validate_order" in doc.functions, (
            f"Expected 'validate_order' in functions, got {doc.functions}"
        )
        assert "send_confirmation" in doc.actions, (
            f"Expected 'send_confirmation' in actions, got {doc.actions}"
        )
        print("  PASS  test_parse_action_declaration")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 3: PROCEDURE with no STEP sub-blocks produces a warning
# ──────────────────────────────────────────────────────────────────────────

def test_procedure_requires_steps():
    spec = """\
Empty Procedure Spec

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
A procedure that declares no steps (should warn).

PROCEDURE empty_proc: A procedure with no steps defined

  EXAMPLE placeholder:
    INPUT: anything
    EXPECTED: nothing

Constraints
* None
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.procedures) == 1
        assert len(doc.procedures[0].steps) == 0

        results = check_structural_completeness(doc)
        # Should have a warning about empty steps
        warn_msgs = [r.message for r in results if r.status == "WARN"]
        has_step_warn = any("no steps" in m.lower() for m in warn_msgs)
        assert has_step_warn, (
            f"Expected a warning about missing steps, got warnings: {warn_msgs}"
        )
        print("  PASS  test_procedure_requires_steps")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 4: Mixed BEHAVIOR and PROCEDURE in the same spec
# ──────────────────────────────────────────────────────────────────────────

def test_mixed_behavior_and_procedure():
    spec = """\
Mixed Spec

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that both BEHAVIOR and PROCEDURE blocks are parsed in a single spec.

BEHAVIOR validate_input: Validate data

  RULE check_name:
    WHEN name is empty
    THEN reject

  EXAMPLE valid:
    INPUT: name="Alice"
    EXPECTED: accepted

PROCEDURE process_data: Process the validated data

  STEP clean:
    REMOVE whitespace from fields

  STEP transform:
    CONVERT dates to ISO 8601

  EXAMPLE processed:
    INPUT: date="March 1, 2026"
    EXPECTED: date="2026-03-01"

Constraints
* Input must be validated before processing
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.behaviors) == 1, (
            f"Expected 1 behavior, got {len(doc.behaviors)}"
        )
        assert doc.behaviors[0].name == "validate_input"
        assert len(doc.procedures) == 1, (
            f"Expected 1 procedure, got {len(doc.procedures)}"
        )
        assert doc.procedures[0].name == "process_data"
        assert len(doc.procedures[0].steps) == 2
        print("  PASS  test_mixed_behavior_and_procedure")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 5: Micro spec allows PROCEDURE only (no BEHAVIOR)
# ──────────────────────────────────────────────────────────────────────────

def test_micro_allows_procedure_only():
    spec = """\
Procedure-Only Micro

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
A micro spec with only a PROCEDURE and no BEHAVIOR block.

PROCEDURE do_work: Perform the work

  STEP first:
    DO the first thing

  EXAMPLE works:
    INPUT: trigger
    EXPECTED: done

Constraints
* Must complete within 5 seconds
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_structural_completeness(doc)

        # Should NOT have a FAIL about missing behaviors
        fail_msgs = [r.message for r in results if r.status == "FAIL"]
        has_behavior_fail = any(
            "no behavior" in m.lower() and "no procedure" not in m.lower()
            for m in fail_msgs
        )
        # The check should pass because we have a PROCEDURE
        behavior_or_proc_results = [
            r for r in results
            if r.category in ("behaviors", "procedures")
            and r.status in ("PASS", "FAIL")
        ]
        has_pass = any(r.status == "PASS" for r in behavior_or_proc_results)
        assert has_pass or not has_behavior_fail, (
            f"Micro with only PROCEDURE should pass structural check, "
            f"got fails: {fail_msgs}"
        )
        print("  PASS  test_micro_allows_procedure_only")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 6: Backward compat — v2 email validator still parses correctly
# ──────────────────────────────────────────────────────────────────────────

def test_backward_compat_v2_spec():
    spec = """\
Email Address Validator

Meta: Version 1.0.0 | Date 2026-03-01 | Domain: Input Validation | Status: active | Tier: micro

Purpose
Validate that a given string is a structurally valid email address before passing it to downstream systems.

BEHAVIOR validate_email: Check that an input string conforms to basic email address structure

  RULE contains_at_sign:
    input MUST contain exactly one "@" character

  RULE has_domain:
    WHEN input contains "@"
    THEN the portion after "@" MUST contain at least one "." character
         AND the portion after "@" MUST be at least 3 characters long

  ERROR invalid_email:
    WHEN input fails contains_at_sign OR has_domain
    SEVERITY critical
    ACTION reject input
    MESSAGE "Invalid email address: does not meet structural requirements"

  EXAMPLE valid_email:
    INPUT: "reggie.chan@tenebrus.ca"
    EXPECTED: { "valid": true }
    NOTES: Contains one @ with a valid domain portion (tenebrus.ca)

  EXAMPLE missing_at_sign:
    INPUT: "reggie.chan.tenebrus.ca"
    EXPECTED: { "valid": false,
                "error": "Invalid email address: does not meet structural requirements" }
    NOTES: No @ character present -- triggers contains_at_sign rule failure

Constraints
* Validation is structural only -- does not verify that the domain exists or accepts mail
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert doc.title == "Email Address Validator", (
            f"Expected title 'Email Address Validator', got '{doc.title}'"
        )
        assert len(doc.behaviors) == 1
        assert doc.behaviors[0].name == "validate_email"
        assert len(doc.behaviors[0].rules) == 2
        assert len(doc.behaviors[0].errors) == 1
        assert len(doc.behaviors[0].examples) == 2

        # Run structural checks — should have zero FAIL results
        results = check_structural_completeness(doc)
        fails = [r for r in results if r.status == "FAIL"]
        assert len(fails) == 0, (
            f"Expected 0 failures for v2 email validator, got: "
            f"{[f.message for f in fails]}"
        )
        print("  PASS  test_backward_compat_v2_spec")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 7: Parse @config block with flat and nested keys
# ──────────────────────────────────────────────────────────────────────────

def test_parse_config_block():
    spec = """\
Config Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that @config blocks with flat and nested keys are parsed correctly.

@config
  max_retries: 3
  timeout_ms: 5000
  thresholds:
    warning: 80
    critical: 95

BEHAVIOR check_thresholds: Validate values against config thresholds

  RULE warn_threshold:
    WHEN value > $config.thresholds.warning
    THEN flag as warning

  EXAMPLE over_warning:
    INPUT: value=85
    EXPECTED: warning flag set

Constraints
* Config values are read-only at runtime
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert doc.config is not None, "Expected @config to be parsed"
        assert "max_retries" in doc.config.entries, (
            f"Expected 'max_retries' in config entries, got {list(doc.config.entries.keys())}"
        )
        assert doc.config.entries["max_retries"] == "3"
        assert doc.config.entries["timeout_ms"] == "5000"
        # Nested keys should be dot-flattened
        assert "thresholds.warning" in doc.config.entries, (
            f"Expected 'thresholds.warning' in config entries, got {list(doc.config.entries.keys())}"
        )
        assert doc.config.entries["thresholds.warning"] == "80"
        assert doc.config.entries["thresholds.critical"] == "95"
        print("  PASS  test_parse_config_block")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 8: Parse @route table with first_match_wins and wildcard
# ──────────────────────────────────────────────────────────────────────────

def test_parse_route_table():
    spec = """\
Route Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that @route tables are parsed with correct rows and wildcard detection.

BEHAVIOR classify_request: Route requests to handlers

  @route request_router [first_match_wins]
  method == "GET" -> handle_get
  method == "POST" -> handle_post
  method == "PUT" -> handle_put
  method == "DELETE" -> handle_delete
  * -> handle_unknown

  EXAMPLE get_request:
    INPUT: method="GET"
    EXPECTED: routed to handle_get

Constraints
* All HTTP methods must be handled
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.behaviors) == 1
        beh = doc.behaviors[0]
        assert len(beh.routes) == 1, (
            f"Expected 1 route, got {len(beh.routes)}"
        )
        route = beh.routes[0]
        assert route.name == "request_router"
        assert route.mode == "first_match_wins"
        assert len(route.rows) == 5, (
            f"Expected 5 route rows, got {len(route.rows)}"
        )
        # Last row should be the wildcard
        assert route.rows[-1].condition.strip() == "*", (
            f"Expected last row to be wildcard, got '{route.rows[-1].condition}'"
        )
        assert route.rows[-1].outcome.strip() == "handle_unknown"
        print("  PASS  test_parse_route_table")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 9: Parse STEP with variable threading declarations
# ──────────────────────────────────────────────────────────────────────────

def test_parse_variable_threading():
    spec = """\
Variable Threading Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that STEP output variable declarations are parsed correctly.

PROCEDURE fetch_and_transform: Fetch data and transform it

  STEP fetch_data: -> $raw_data
    CALL external API to retrieve dataset

  STEP transform: -> $clean_data
    APPLY normalization to $raw_data

  STEP save:
    PERSIST $clean_data to storage

  EXAMPLE pipeline:
    INPUT: API endpoint URL
    EXPECTED: transformed data saved

Constraints
* Steps execute in declared order
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.procedures) == 1
        proc = doc.procedures[0]
        assert len(proc.steps) == 3

        # Step 1: produces $raw_data
        assert "$raw_data" in proc.steps[0].output_variables, (
            f"Expected '$raw_data' in step 0 outputs, got {proc.steps[0].output_variables}"
        )
        # Step 2: produces $clean_data
        assert "$clean_data" in proc.steps[1].output_variables, (
            f"Expected '$clean_data' in step 1 outputs, got {proc.steps[1].output_variables}"
        )
        # Step 3: no output variables
        assert len(proc.steps[2].output_variables) == 0, (
            f"Expected no outputs for step 2, got {proc.steps[2].output_variables}"
        )
        print("  PASS  test_parse_variable_threading")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 10: Parse compact ERRORS: markdown table
# ──────────────────────────────────────────────────────────────────────────

def test_parse_compact_error_table():
    spec = """\
Compact Error Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that compact ERRORS: tables are parsed correctly.

BEHAVIOR validate_data: Validate incoming data

  RULE check_required:
    WHEN required fields are missing
    THEN reject

  ERRORS:
  | Name | When | Severity | Action | Message |
  |------|------|----------|--------|---------|
  | missing_field | required field is null | critical | reject request | Required field missing |
  | invalid_format | field format invalid | warning | flag for review | Format does not match |
  | duplicate_entry | record already exists | info | skip silently | Duplicate detected |

  EXAMPLE valid_data:
    INPUT: all required fields present
    EXPECTED: accepted

Constraints
* All errors must be handled
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.behaviors) == 1
        beh = doc.behaviors[0]
        assert len(beh.compact_errors) == 3, (
            f"Expected 3 compact errors, got {len(beh.compact_errors)}"
        )
        # Check first error has all 5 fields
        ce = beh.compact_errors[0]
        assert ce.name == "missing_field", f"Expected name 'missing_field', got '{ce.name}'"
        assert ce.when == "required field is null"
        assert ce.severity == "critical"
        assert ce.action == "reject request"
        assert ce.message == "Required field missing"
        # Check second error
        ce2 = beh.compact_errors[1]
        assert ce2.name == "invalid_format"
        assert ce2.severity == "warning"
        # Check third error
        ce3 = beh.compact_errors[2]
        assert ce3.name == "duplicate_entry"
        assert ce3.severity == "info"
        print("  PASS  test_parse_compact_error_table")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 11: Parse compact EXAMPLES: one-line entries
# ──────────────────────────────────────────────────────────────────────────

def test_parse_compact_examples():
    spec = """\
Compact Examples Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that compact EXAMPLES: lines are parsed correctly.

BEHAVIOR classify_input: Classify input strings

  RULE classify:
    WHEN input is numeric
    THEN return "number"

  EXAMPLES:
  numeric: "42" -> "number"
  alpha: "hello" -> "string"
  empty: "" -> "empty"

Constraints
* Classification is deterministic
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.behaviors) == 1
        beh = doc.behaviors[0]
        assert len(beh.compact_examples) == 3, (
            f"Expected 3 compact examples, got {len(beh.compact_examples)}"
        )
        # Check each example has name, input, and expected populated
        ex1 = beh.compact_examples[0]
        assert ex1.name == "numeric", f"Expected name 'numeric', got '{ex1.name}'"
        assert ex1.input_desc == '"42"'
        assert ex1.expected == '"number"'

        ex2 = beh.compact_examples[1]
        assert ex2.name == "alpha"
        assert ex2.input_desc == '"hello"'
        assert ex2.expected == '"string"'

        ex3 = beh.compact_examples[2]
        assert ex3.name == "empty"
        assert ex3.expected == '"empty"'
        print("  PASS  test_parse_compact_examples")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 12: Config reference validation — $config.nonexistent triggers WARN
# ──────────────────────────────────────────────────────────────────────────

def test_config_reference_validation():
    spec = """\
Config Ref Validation Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that referencing a nonexistent config key produces a WARN.

@config
  max_retries: 3

BEHAVIOR retry_logic: Handle retries

  RULE check_limit:
    WHEN attempt_count > $config.nonexistent
    THEN stop retrying

  EXAMPLE over_limit:
    INPUT: attempt_count=5
    EXPECTED: stop

Constraints
* Retry limit is configurable
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_config_references(doc)
        warn_results = [r for r in results if r.status == "WARN"]
        assert len(warn_results) >= 1, (
            f"Expected at least 1 WARN for $config.nonexistent, got {len(warn_results)}: "
            f"{[r.message for r in results]}"
        )
        has_nonexistent_warn = any(
            "nonexistent" in r.message for r in warn_results
        )
        assert has_nonexistent_warn, (
            f"Expected a warning mentioning 'nonexistent', got: "
            f"{[r.message for r in warn_results]}"
        )
        print("  PASS  test_config_reference_validation")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 13: Variable threading validation — unproduced $var triggers WARN
# ──────────────────────────────────────────────────────────────────────────

def test_variable_threading_validation():
    spec = """\
Var Threading Validation Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that referencing an unproduced variable produces a WARN.

PROCEDURE process: Process data

  STEP compute:
    CALCULATE result from $undefined_var

  EXAMPLE test:
    INPUT: data
    EXPECTED: computed result

Constraints
* Variables must be produced before use
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_variable_threading(doc)
        warn_results = [r for r in results if r.status == "WARN"]
        assert len(warn_results) >= 1, (
            f"Expected at least 1 WARN for $undefined_var, got {len(warn_results)}: "
            f"{[r.message for r in results]}"
        )
        has_undefined_warn = any(
            "undefined_var" in r.message for r in warn_results
        )
        assert has_undefined_warn, (
            f"Expected a warning mentioning 'undefined_var', got: "
            f"{[r.message for r in warn_results]}"
        )
        print("  PASS  test_variable_threading_validation")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 14: Route branch count warning — @route with <3 branches
# ──────────────────────────────────────────────────────────────────────────

def test_route_branch_count_warning():
    spec = """\
Route Branch Count Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that a @route with fewer than 3 branches triggers a WARN.

BEHAVIOR simple_route: A route with too few branches

  @route binary_choice
  condition_a -> outcome_a
  condition_b -> outcome_b

  EXAMPLE route_test:
    INPUT: condition_a
    EXPECTED: outcome_a

Constraints
* Routes should have 3+ branches
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_route_completeness(doc)
        warn_results = [r for r in results if r.status == "WARN"]
        # Should warn about fewer than 3 branches
        has_branch_warn = any(
            "branch" in r.message.lower() or "2" in r.message
            for r in warn_results
        )
        assert has_branch_warn, (
            f"Expected a warning about branch count, got: "
            f"{[r.message for r in warn_results]}"
        )
        # Should also warn about missing wildcard
        has_wildcard_warn = any(
            "wildcard" in r.message.lower() for r in warn_results
        )
        assert has_wildcard_warn, (
            f"Expected a warning about missing wildcard, got: "
            f"{[r.message for r in warn_results]}"
        )
        print("  PASS  test_route_branch_count_warning")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 15: Notation section check — standard tier without Notation warns
# ──────────────────────────────────────────────────────────────────────────

def test_notation_section_check():
    spec = """\
Notation Missing Test

Meta
* Version: 1.0.0
* Date: 2026-03-01
* Domain: Testing
* Status: active
* Tier: standard

Purpose
Test that a standard tier spec without Notation section triggers a WARN.

Scope
* IN SCOPE: everything
* OUT OF SCOPE: nothing

Inputs
* data: string - input data - required

Outputs
* result: string - output result

Types

InputData {
  value: string, required
}

Functions
FUNCTION process(data: InputData) -> string

BEHAVIOR do_stuff: Process input

  RULE process_it:
    WHEN data is present
    THEN process it

  EXAMPLE test:
    INPUT: data="hello"
    EXPECTED: "processed"

Constraints
* None

Dependencies
* None
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_notation_section(doc)
        warn_results = [r for r in results if r.status == "WARN"]
        assert len(warn_results) >= 1, (
            f"Expected at least 1 WARN for missing Notation, got: "
            f"{[r.message for r in results]}"
        )
        has_notation_warn = any(
            "notation" in r.message.lower() for r in warn_results
        )
        assert has_notation_warn, (
            f"Expected a warning about missing Notation section, got: "
            f"{[r.message for r in warn_results]}"
        )
        print("  PASS  test_notation_section_check")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 16: Cross-procedure variable visibility (global scope)
# ──────────────────────────────────────────────────────────────────────────

def test_document_global_variable_scope():
    spec = """\
Global Variable Scope Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that variables produced in one procedure are visible in another.

PROCEDURE fetch_data: Retrieve data from source

  STEP retrieve: -> $data
    CALL API to get dataset

  EXAMPLE fetch:
    INPUT: endpoint URL
    EXPECTED: data retrieved

PROCEDURE transform_data: Transform the fetched data

  STEP normalize:
    APPLY normalization to $data

  EXAMPLE transform:
    INPUT: raw data
    EXPECTED: normalized data

Constraints
* Procedures execute in declared order
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_variable_threading(doc)
        # $data is produced in procedure 1, referenced in procedure 2
        # Variable threading check collects all produced vars globally,
        # so $data should be found as produced and no WARN should appear for it.
        warn_results = [r for r in results if r.status == "WARN"]
        data_warns = [r for r in warn_results if "$data" in r.message or "data" in r.message.split("$")[-1].split(" ")[0]]
        # Filter to only check for $data specifically (not other $vars)
        data_specific_warns = [r for r in warn_results if "data " in r.message or "data\n" in r.message or r.message.endswith("data")]
        # The $data variable should be recognized as produced
        pass_results = [r for r in results if r.status == "PASS"]
        # Either we get a PASS (all vars resolved) or no warn about $data
        no_data_warning = not any(
            "$data " in r.message or "$data\n" in r.message
            for r in warn_results
        )
        assert no_data_warning or len(pass_results) > 0, (
            f"Expected $data to be recognized as produced globally, but got warnings: "
            f"{[r.message for r in warn_results]}"
        )
        print("  PASS  test_document_global_variable_scope")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 17: Mixed error formats — both compact and traditional
# ──────────────────────────────────────────────────────────────────────────

def test_mixed_error_formats():
    spec = """\
Mixed Error Formats Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that a block can contain both compact ERRORS: table and traditional ERROR blocks.

BEHAVIOR validate_data: Validate with both error formats

  RULE check_required:
    WHEN required field is missing
    THEN reject

  ERRORS:
  | Name | When | Severity | Action | Message |
  |------|------|----------|--------|---------|
  | compact_err | field is null | warning | log it | Field was null |

  ERROR traditional_err:
    WHEN data is corrupted
    SEVERITY critical
    ACTION reject entirely
    MESSAGE "Data corruption detected"

  EXAMPLE test:
    INPUT: valid data
    EXPECTED: accepted

Constraints
* Both error formats are supported
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert len(doc.behaviors) == 1
        beh = doc.behaviors[0]
        assert len(beh.compact_errors) >= 1, (
            f"Expected at least 1 compact error, got {len(beh.compact_errors)}"
        )
        assert len(beh.errors) >= 1, (
            f"Expected at least 1 traditional error, got {len(beh.errors)}"
        )
        assert beh.compact_errors[0].name == "compact_err"
        assert beh.errors[0].name == "traditional_err"
        print("  PASS  test_mixed_error_formats")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 18: Type consistency — references to defined types
# ──────────────────────────────────────────────────────────────────────────

def test_type_consistency():
    spec = """\
Type Consistency Test

Meta
* Version: 1.0.0
* Date: 2026-03-01
* Domain: Testing
* Status: active
* Tier: standard

Purpose
Test that type reference validation works correctly.

Scope
* IN SCOPE: type checking
* OUT OF SCOPE: runtime validation

Inputs
* request: Request - incoming request - required

Outputs
* response: Response - outgoing response

Types

Request {
  url: string, required
  method: string, required
}

Response {
  status: number, required
  body: string, optional
}

OrphanedType {
  field: string, required
}

Functions
FUNCTION handle(req: Request) -> Response

BEHAVIOR process_request: Handle requests

  RULE check_url:
    WHEN request.url is empty
    THEN reject

  RULE check_method:
    WHEN request.method is invalid
    THEN return error Response

  EXAMPLE valid_request:
    INPUT: request with url="/api" and method="GET"
    EXPECTED: response with status=200

Constraints
* URL must be non-empty

Dependencies
* HTTP library
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_type_consistency(doc)
        # OrphanedType should trigger a WARN about being defined but never referenced
        warn_results = [r for r in results if r.status == "WARN"]
        has_orphan_warn = any(
            "OrphanedType" in r.message and "never referenced" in r.message
            for r in warn_results
        )
        assert has_orphan_warn, (
            f"Expected a warning about orphaned type 'OrphanedType', got: "
            f"{[r.message for r in warn_results]}"
        )
        # Request and Response should be recognized as referenced
        pass_results = [r for r in results if r.status == "PASS"]
        assert len(pass_results) >= 1, (
            f"Expected at least 1 PASS for referenced types, got: "
            f"{[r.message for r in results]}"
        )
        print("  PASS  test_type_consistency")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 19: Keyword capitalization — lowercase must/should/may detection
# ──────────────────────────────────────────────────────────────────────────

def test_keyword_capitalization():
    spec = """\
Keyword Capitalization Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that lowercase requirement keywords trigger WARN in structural check.

BEHAVIOR validate: Check inputs

  RULE require_name:
    name must not be empty

  RULE require_email:
    email should contain an @ character

  EXAMPLE valid:
    INPUT: name="Alice", email="a@b.com"
    EXPECTED: accepted

Constraints
* Fields must be validated
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_structural_completeness(doc)
        keyword_warns = [
            r for r in results
            if r.category == "keywords" and r.status == "WARN"
        ]
        # Should detect lowercase "must" and/or "should" in rule text
        assert len(keyword_warns) >= 1, (
            f"Expected at least 1 keyword capitalization WARN, got {len(keyword_warns)}: "
            f"{[r.message for r in results if r.category == 'keywords']}"
        )
        print("  PASS  test_keyword_capitalization")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 20: Standard section requirements — missing required sections
# ──────────────────────────────────────────────────────────────────────────

def test_standard_section_requirements():
    spec = """\
Missing Sections Test

Meta
* Version: 1.0.0
* Date: 2026-03-01
* Domain: Testing
* Status: active
* Tier: standard

Purpose
Test that missing required sections for standard tier produce FAIL results.

BEHAVIOR do_something: A behavior

  RULE always:
    WHEN true
    THEN proceed

  EXAMPLE test:
    INPUT: anything
    EXPECTED: proceeded

Constraints
* None
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_structural_completeness(doc)
        fail_results = [r for r in results if r.status == "FAIL"]
        # Standard tier requires: meta, purpose, scope, inputs, outputs, types,
        # functions, behaviors, constraints, dependencies
        # This spec is missing: scope, inputs, outputs, types, functions, dependencies
        missing_sections = {"scope", "inputs", "outputs", "types", "functions", "dependencies"}
        fail_messages = " ".join(r.message.lower() for r in fail_results)
        for section in missing_sections:
            assert section in fail_messages, (
                f"Expected FAIL about missing '{section}' section, got fails: "
                f"{[r.message for r in fail_results]}"
            )
        print("  PASS  test_standard_section_requirements")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 21: ERROR block missing WHEN clause
# ──────────────────────────────────────────────────────────────────────────

def test_error_when_clause():
    spec = """\
Error When Clause Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that an ERROR block missing WHEN clause triggers a WARN.

BEHAVIOR validate: Check input

  RULE check:
    WHEN input is invalid
    THEN reject

  ERROR missing_when:
    SEVERITY critical
    ACTION reject
    MESSAGE "Something went wrong"

  EXAMPLE test:
    INPUT: valid data
    EXPECTED: accepted

Constraints
* All errors should have WHEN clauses
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        results = check_error_consistency(doc)
        warn_results = [r for r in results if r.status == "WARN"]
        has_when_warn = any(
            "WHEN" in r.message and "missing_when" in r.message
            for r in warn_results
        )
        assert has_when_warn, (
            f"Expected a WARN about missing WHEN clause for 'missing_when', got: "
            f"{[r.message for r in warn_results]}"
        )
        print("  PASS  test_error_when_clause")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Test 22: YAML frontmatter stripping — spec with frontmatter parses OK
# ──────────────────────────────────────────────────────────────────────────

def test_yaml_frontmatter_stripping():
    spec = """\
---
name: test-skill
description: A test skill file
version: 1.0.0
---
Frontmatter Stripping Test

Meta: Version 1.0.0 | Date: 2026-03-01 | Domain: Testing | Status: active | Tier: micro

Purpose
Test that YAML frontmatter is stripped before parsing.

BEHAVIOR simple: A simple behavior

  RULE check:
    WHEN input is valid
    THEN accept

  EXAMPLE test:
    INPUT: valid data
    EXPECTED: accepted

Constraints
* Frontmatter should not interfere with parsing
"""
    path = _write_temp_spec(spec)
    try:
        doc = parse_sesf(path)
        assert doc.title == "Frontmatter Stripping Test", (
            f"Expected title 'Frontmatter Stripping Test', got '{doc.title}'"
        )
        assert "version" in doc.meta, (
            f"Expected 'version' in meta, got {doc.meta}"
        )
        assert len(doc.behaviors) == 1
        assert doc.behaviors[0].name == "simple"
        # Structural checks should pass
        results = check_structural_completeness(doc)
        fails = [r for r in results if r.status == "FAIL"]
        assert len(fails) == 0, (
            f"Expected 0 FAIL results after frontmatter stripping, got: "
            f"{[f.message for f in fails]}"
        )
        print("  PASS  test_yaml_frontmatter_stripping")
    finally:
        os.unlink(path)


# ──────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────

def main():
    tests = [
        test_parse_procedure_block,
        test_parse_action_declaration,
        test_procedure_requires_steps,
        test_mixed_behavior_and_procedure,
        test_micro_allows_procedure_only,
        test_backward_compat_v2_spec,
        test_parse_config_block,
        test_parse_route_table,
        test_parse_variable_threading,
        test_parse_compact_error_table,
        test_parse_compact_examples,
        test_config_reference_validation,
        test_variable_threading_validation,
        test_route_branch_count_warning,
        test_notation_section_check,
        test_document_global_variable_scope,
        test_mixed_error_formats,
        test_type_consistency,
        test_keyword_capitalization,
        test_standard_section_requirements,
        test_error_when_clause,
        test_yaml_frontmatter_stripping,
    ]

    passed = 0
    failed = 0
    errors = []

    print(f"\nRunning {len(tests)} tests...\n")

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((test_fn.__name__, str(e)))
            print(f"  FAIL  {test_fn.__name__}: {e}")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")

    if errors:
        print("\nFailures:")
        for name, msg in errors:
            print(f"  - {name}: {msg}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
