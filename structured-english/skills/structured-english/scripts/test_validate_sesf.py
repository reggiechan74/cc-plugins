#!/usr/bin/env python3
"""Tests for SESF v3 validator — PROCEDURE and ACTION block support.

Run:  python3 test_validate_sesf.py
"""

import os
import sys
import tempfile

# Ensure the script directory is on the import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_sesf import (
    parse_sesf,
    check_structural_completeness,
    check_error_consistency,
    check_example_consistency,
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

    print(f"\n{'─' * 50}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")

    if errors:
        print("\nFailures:")
        for name, msg in errors:
            print(f"  - {name}: {msg}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
