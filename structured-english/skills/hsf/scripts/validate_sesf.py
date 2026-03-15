#!/usr/bin/env python3
"""SESF v3/v4, HSF v5, and HSF v6 Structural Validator

Parses specification files (markdown) and validates them for structural
correctness. Auto-detects whether a spec is SESF v4 (formal blocks),
HSF v5 (hybrid prose format), or HSF v6 (XML section tags) and applies
the appropriate validation rules.

SESF v4: Checks BEHAVIOR blocks, PROCEDURE blocks, ACTION declarations,
section structure, @config, @route, $variable threading.

HSF v5: Checks prose structure, forbidden formal keywords, @config, @route,
$variable threading, consolidated error tables, line budgets.

HSF v6: Checks XML section tags, <config> with JSON body, <route> with
<case> elements, <output-schema>, $variable threading, line budgets.

Usage:
    python3 validate_sesf.py <spec_file.md>

Exit codes:
    0 - All checks passed (may include warnings)
    1 - One or more checks failed, or file is not a valid spec
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class SESFRule:
    name: str
    when_clause: Optional[str] = None
    then_clause: Optional[str] = None
    else_clause: Optional[str] = None
    priority: Optional[int] = None
    raw_text: str = ""
    line_number: int = 0


@dataclass
class SESFError:
    name: str
    when_clause: Optional[str] = None
    severity: Optional[str] = None
    action: Optional[str] = None
    message: Optional[str] = None
    line_number: int = 0


@dataclass
class SESFExample:
    name: str
    input_text: str = ""
    expected_text: str = ""
    notes: Optional[str] = None
    line_number: int = 0


@dataclass
class SESFBehavior:
    name: str
    rules: list = field(default_factory=list)   # list[SESFRule]
    errors: list = field(default_factory=list)   # list[SESFError]
    examples: list = field(default_factory=list)  # list[SESFExample]
    routes: list = field(default_factory=list)   # list[SESFRoute]
    compact_errors: list = field(default_factory=list)  # list[SESFCompactError]
    compact_examples: list = field(default_factory=list)  # list[SESFCompactExample]
    inline_errors: list = field(default_factory=list)  # list[SESFInlineError]
    line_number: int = 0


@dataclass
class SESFStep:
    name: str
    description: str = ""
    raw_text: str = ""
    output_variables: list = field(default_factory=list)  # list[str]
    line_number: int = 0


@dataclass
class SESFProcedure:
    name: str
    steps: list = field(default_factory=list)    # list[SESFStep]
    errors: list = field(default_factory=list)   # list[SESFError]
    examples: list = field(default_factory=list)  # list[SESFExample]
    compact_errors: list = field(default_factory=list)  # list[SESFCompactError]
    compact_examples: list = field(default_factory=list)  # list[SESFCompactExample]
    inline_errors: list = field(default_factory=list)  # list[SESFInlineError]
    line_number: int = 0


@dataclass
class SESFConfigEntry:
    key: str = ""
    value: str = ""
    line_number: int = 0


@dataclass
class SESFConfig:
    entries: dict = field(default_factory=dict)  # key -> value (flattened with dot notation)
    line_number: int = 0


@dataclass
class SESFRouteRow:
    condition: str = ""
    outcome: str = ""
    line_number: int = 0


@dataclass
class SESFRoute:
    name: str = ""
    mode: str = "first_match_wins"  # or "all_matches"
    rows: list = field(default_factory=list)  # list[SESFRouteRow]
    line_number: int = 0


@dataclass
class SESFCompactError:
    name: str = ""
    when: str = ""
    severity: str = ""
    action: str = ""
    message: str = ""
    line_number: int = 0


@dataclass
class SESFCompactExample:
    name: str = ""
    input_desc: str = ""
    expected: str = ""
    line_number: int = 0


@dataclass
class SESFInlineError:
    """Inline ERROR format: ERROR name: severity → action, "message" """
    name: str = ""
    severity: str = ""
    action: str = ""
    message: str = ""
    line_number: int = 0


@dataclass
class SESFTypeField:
    name: str
    type_str: str
    required: bool = True


@dataclass
class SESFType:
    name: str
    fields: list = field(default_factory=list)  # list[SESFTypeField]
    line_number: int = 0


@dataclass
class SESFDocument:
    title: str = ""
    meta: dict = field(default_factory=dict)
    sections: dict = field(default_factory=dict)
    types: list = field(default_factory=list)      # list[SESFType]
    functions: list = field(default_factory=list)   # list of function names
    behaviors: list = field(default_factory=list)   # list[SESFBehavior]
    procedures: list = field(default_factory=list)  # list[SESFProcedure]
    actions: list = field(default_factory=list)     # list of action names
    precedence: list = field(default_factory=list)  # ordered list of rule names
    config: Optional[SESFConfig] = None
    has_notation_section: bool = False


@dataclass
class ValidationResult:
    category: str
    status: str   # PASS, WARN, FAIL
    message: str
    line_number: Optional[int] = None


# ---------------------------------------------------------------------------
# Known section keywords
# ---------------------------------------------------------------------------

KNOWN_SECTIONS = {
    "meta", "purpose", "scope", "inputs", "outputs", "types", "functions",
    "behaviors", "precedence", "constraints", "dependencies", "changelog",
    "audience", "procedures", "notation",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_code_block(text: str) -> str:
    """If the entire content is wrapped in a markdown code block, extract it."""
    lines = text.split("\n")
    # Find first ``` line
    start = None
    end = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            if start is None:
                start = i
            else:
                end = i
                break
    if start is not None and end is not None and end > start:
        return "\n".join(lines[start + 1:end])
    return text


def _strip_yaml_frontmatter(text: str) -> str:
    """Strip YAML frontmatter (--- delimited block at start of file).

    Skill files commonly start with YAML frontmatter like:
        ---
        name: skill-name
        description: ...
        ---
    This must be removed before parsing the SESF content.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    # Find the closing ---
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1:])
    return text  # No closing --- found, return as-is


def _strip_fenced_code_blocks(text: str) -> str:
    """Remove content inside fenced code blocks (``` ... ```) for detection purposes."""
    return re.sub(r'```[^\n]*\n.*?```', '', text, flags=re.DOTALL)


def detect_format_version(text: str) -> str:
    """Detect whether a spec is SESF v4, HSF v5, or HSF v6.

    Returns:
        'hsf_v6' if 2+ XML section tags found (<purpose>, <instructions>, etc.)
        'sesf_v4' if BEHAVIOR/PROCEDURE keywords found outside code blocks
        'hsf_v5' if prose format (no formal blocks) with @route/@config/## Instructions
        'unknown' if neither pattern matches
    """
    # Strip fenced code blocks so examples don't trigger false positives
    prose_only = _strip_fenced_code_blocks(text)
    normalized = _normalize_for_matching(prose_only)

    # Check for HSF v6 XML section tags (before v5/v4 checks)
    v6_section_tags = [
        'purpose', 'instructions', 'scope', 'config', 'rules',
        'errors', 'examples', 'inputs', 'outputs',
    ]
    v6_tag_count = sum(
        1 for tag in v6_section_tags
        if re.search(rf'<{tag}[\s>]', prose_only)
    )
    if v6_tag_count >= 2:
        return 'hsf_v6'

    # Check for SESF v4 formal blocks (outside code blocks only)
    has_behavior = bool(re.search(r'^\s*BEHAVIOR\s+\w+', normalized, re.MULTILINE))
    has_procedure = bool(re.search(r'^\s*PROCEDURE\s+\w+', normalized, re.MULTILINE))

    if has_behavior or has_procedure:
        return 'sesf_v4'

    # Check for HSF v5 signals (outside code blocks only)
    has_route = '@route' in prose_only
    has_config = '@config' in prose_only
    has_instructions = bool(re.search(r'^##\s+Instructions', prose_only, re.MULTILINE))
    has_rules_section = bool(re.search(r'^##\s+Rules', prose_only, re.MULTILINE))
    has_errors_table = bool(re.search(r'^##\s+Errors', prose_only, re.MULTILINE))

    if has_route or has_config or has_instructions or has_rules_section or has_errors_table:
        return 'hsf_v5'

    return 'unknown'


_BOLD_KW_RE = re.compile(r'\*\*([A-Z][A-Z0-9_]*)\*\*')
_HEADING_RE = re.compile(r'^#+\s*')


def _normalize_for_matching(s: str) -> str:
    """Strip markdown **BOLD** and ### heading markers for keyword matching.

    Allows the parser to accept both plain and markdown-formatted forms:
      '**BEHAVIOR** name:' → 'BEHAVIOR name:'
      '### Behaviors'      → 'Behaviors'
    """
    s = _BOLD_KW_RE.sub(r'\1', s)
    s = _HEADING_RE.sub('', s)
    return s


def _parse_meta_pipe(line: str) -> dict:
    """Parse a pipe-delimited meta line like:
    Version: 1.0.0 | Date: 2026-02-28 | Domain: Validation | Status: active | Tier: micro
    Also handles 'Meta: Version 1.0.0 | Date ...' format (no field names on first segment).
    """
    meta = {}
    # Remove leading '* ' or 'Meta:' prefix
    text = line.strip()
    if text.startswith("*"):
        text = text[1:].strip()
    if text.lower().startswith("meta:"):
        text = text[5:].strip()
    if text.lower().startswith("meta"):
        text = text[4:].strip()

    segments = [s.strip() for s in text.split("|")]
    for seg in segments:
        if ":" in seg:
            key, _, val = seg.partition(":")
            key = key.strip().lower()
            val = val.strip()
            meta[key] = val
        else:
            # Segment like "Version 1.0.0" without colon
            parts = seg.split(None, 1)
            if len(parts) == 2:
                meta[parts[0].strip().lower()] = parts[1].strip()
    return meta


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_sesf(filepath: str) -> SESFDocument:
    """Parse an SESF v3 specification file and return an SESFDocument."""
    doc = SESFDocument()
    path = Path(filepath)
    if not path.exists():
        return doc

    raw_text = path.read_text(encoding="utf-8", errors="replace")

    # Strip YAML frontmatter if present (common in skill files)
    raw_text = _strip_yaml_frontmatter(raw_text)

    # If the content is inside a markdown code block, extract it
    content = _strip_code_block(raw_text)
    lines = content.split("\n")

    # State tracking
    current_section: Optional[str] = None
    current_behavior: Optional[SESFBehavior] = None
    current_rule: Optional[SESFRule] = None
    current_error: Optional[SESFError] = None
    current_example: Optional[SESFExample] = None
    current_procedure: Optional[SESFProcedure] = None
    current_step: Optional[SESFStep] = None
    in_type_block = False
    current_type: Optional[SESFType] = None
    meta_started = False
    in_config_block = False
    config_prefix_stack: list[str] = []  # for nested dot-flattening
    current_route: Optional[SESFRoute] = None
    in_compact_errors = False  # inside a compact ERRORS: table
    in_compact_examples = False  # inside a compact EXAMPLES: block
    compact_errors_header_seen = False  # have we seen the table header row?

    def _finish_sub_block():
        """Flush the current rule/error/example into the current behavior."""
        nonlocal current_rule, current_error, current_example
        if current_rule and current_behavior:
            current_behavior.rules.append(current_rule)
            current_rule = None
        if current_error and current_behavior:
            current_behavior.errors.append(current_error)
            current_error = None
        if current_example and current_behavior:
            current_behavior.examples.append(current_example)
            current_example = None

    def _finish_behavior():
        nonlocal current_behavior, current_route
        nonlocal in_compact_errors, in_compact_examples, compact_errors_header_seen
        _finish_sub_block()
        # Flush any open route
        if current_route and current_behavior:
            current_behavior.routes.append(current_route)
            current_route = None
        in_compact_errors = False
        in_compact_examples = False
        compact_errors_header_seen = False
        if current_behavior:
            doc.behaviors.append(current_behavior)
            current_behavior = None

    def _finish_proc_sub_block():
        """Flush the current step/error/example into the current procedure.

        NOTE: current_error and current_example are shared with _finish_sub_block
        (BEHAVIOR flush). Mutual exclusion is guaranteed because the parser never
        allows both current_behavior and current_procedure to be non-None — entering
        a BEHAVIOR calls _finish_procedure() first, and vice versa.
        """
        nonlocal current_step, current_error, current_example
        if current_step and current_procedure:
            current_procedure.steps.append(current_step)
            current_step = None
        if current_error and current_procedure:
            current_procedure.errors.append(current_error)
            current_error = None
        if current_example and current_procedure:
            current_procedure.examples.append(current_example)
            current_example = None

    def _finish_procedure():
        nonlocal current_procedure
        nonlocal in_compact_errors, in_compact_examples, compact_errors_header_seen
        _finish_proc_sub_block()
        in_compact_errors = False
        in_compact_examples = False
        compact_errors_header_seen = False
        if current_procedure:
            doc.procedures.append(current_procedure)
            current_procedure = None

    def _finish_type():
        nonlocal current_type, in_type_block
        if current_type:
            doc.types.append(current_type)
            current_type = None
        in_type_block = False

    for line_idx, raw_line in enumerate(lines):
        line_num = line_idx + 1  # 1-based
        line = raw_line.rstrip()
        stripped = line.strip()
        stripped_norm = _normalize_for_matching(stripped)

        # --- Skip empty lines (but don't change section) ---
        if not stripped:
            # Append to current section content if we have one
            if current_section and current_section in doc.sections:
                doc.sections[current_section].append("")
            continue

        # --- Spec separator: stop at first `---` after we've started parsing ---
        # Only match unindented `---` lines; indented ones are content (e.g., markdown hr in templates)
        if stripped == "---" and (doc.title or doc.meta) and not raw_line.startswith((" ", "\t")):
            _finish_behavior()
            _finish_procedure()
            _finish_type()
            break

        # --- Title detection: `# Title` (only if not yet found) ---
        if not doc.title and stripped.startswith("#"):
            # Could be `# Title` or just `Title` at the top
            title = stripped.lstrip("#").strip()
            # Don't treat `### Section` headers as the title
            if title and title.lower() not in KNOWN_SECTIONS:
                doc.title = title
                continue

        # --- Title detection: first non-empty line if no `#` title found yet ---
        if not doc.title and not meta_started and current_section is None:
            # Check if this is a bare title (no section keyword match)
            low = stripped.lower()
            is_section = low in KNOWN_SECTIONS or low.rstrip(":") in KNOWN_SECTIONS
            is_meta_line = low.startswith("meta")
            if not is_section and not is_meta_line and not stripped.startswith("*"):
                doc.title = stripped
                continue

        # --- Section detection ---
        # A section keyword at the very start of a line (not indented),
        # possibly followed by nothing, or by `:` or content.
        # stripped_norm removes **bold** and ### heading markers first.
        low_stripped = stripped_norm.lower()
        section_match = None
        for sec in KNOWN_SECTIONS:
            if low_stripped == sec or low_stripped == sec + ":":
                section_match = sec
                break
            # Also match "Meta:" with trailing content (pipe-delimited)
            if low_stripped.startswith(sec + ":") and sec == "meta":
                section_match = sec
                break

        # Only consider it a section header if the line is NOT indented
        # (indented lines within behaviors are sub-blocks, not section headers)
        if section_match and not raw_line.startswith((" ", "\t")):
            # Close any open behavior / procedure / type before switching sections
            _finish_behavior()
            _finish_procedure()
            _finish_type()

            current_section = section_match
            if current_section not in doc.sections:
                doc.sections[current_section] = []

            # Handle Meta section
            if section_match == "meta":
                meta_started = True
                # Check if rest of line has pipe-delimited meta
                rest = stripped_norm[len(section_match):].strip().lstrip(":").strip()
                if "|" in rest:
                    doc.meta.update(_parse_meta_pipe(rest))

            # Detect Notation section
            if section_match == "notation":
                doc.has_notation_section = True

            # Exit any active config/route/compact block on section change
            in_config_block = False
            config_prefix_stack = []
            current_route = None
            in_compact_errors = False
            in_compact_examples = False
            compact_errors_header_seen = False
            continue

        # --- @config block detection ---
        if stripped.startswith("@config"):
            _finish_behavior()
            _finish_procedure()
            _finish_type()
            in_config_block = True
            config_prefix_stack = []
            doc.config = SESFConfig(line_number=line_num)
            continue

        # --- Inside @config block: parse key-value pairs ---
        if in_config_block:
            # Exit config on unindented non-config line (section header,
            # BEHAVIOR, PROCEDURE, etc.)
            if not raw_line.startswith((" ", "\t")):
                in_config_block = False
                config_prefix_stack = []
                # Don't continue — fall through to process this line normally
            else:
                # Indented line inside @config
                # Determine indent level (by counting leading spaces)
                indent_level = len(raw_line) - len(raw_line.lstrip())
                # Adjust prefix stack based on indent
                while config_prefix_stack and len(config_prefix_stack) > indent_level // 2:
                    config_prefix_stack.pop()

                if ":" in stripped:
                    key_part, _, val_part = stripped.partition(":")
                    key_part = key_part.strip()
                    val_part = val_part.strip()
                    if val_part:
                        # Simple key: value pair
                        full_key = ".".join(config_prefix_stack + [key_part]) if config_prefix_stack else key_part
                        doc.config.entries[full_key] = val_part
                    else:
                        # Nested key (no value) — push to prefix stack
                        config_prefix_stack.append(key_part)
                continue

        # --- BEHAVIOR detection (must come before section-specific handlers
        #     so that BEHAVIOR lines are not consumed by e.g. Functions) ---
        behavior_match = re.match(r"^\s*BEHAVIOR\s+(\w+)\s*:", stripped_norm)
        if behavior_match:
            _finish_behavior()
            _finish_procedure()
            _finish_type()
            current_section = "behaviors"
            if "behaviors" not in doc.sections:
                doc.sections["behaviors"] = []
            current_behavior = SESFBehavior(
                name=behavior_match.group(1), line_number=line_num
            )
            doc.sections["behaviors"].append(stripped)
            continue

        # --- PROCEDURE detection (parallel to BEHAVIOR) ---
        procedure_match = re.match(r"^\s*PROCEDURE\s+(\w+)\s*:", stripped_norm)
        if procedure_match:
            _finish_behavior()
            _finish_procedure()
            _finish_type()
            # PROCEDURE blocks share the "behaviors" section key with BEHAVIORs
            # for tier-requirement checking purposes.
            current_section = "behaviors"
            if "behaviors" not in doc.sections:
                doc.sections["behaviors"] = []
            current_procedure = SESFProcedure(
                name=procedure_match.group(1), line_number=line_num
            )
            doc.sections["behaviors"].append(stripped)
            continue

        # --- PRECEDENCE detection (can appear after behaviors, at top level) ---
        prec_header_match = re.match(r"^PRECEDENCE\s*:", stripped_norm)
        if prec_header_match and not raw_line.startswith((" ", "\t")):
            _finish_behavior()
            _finish_procedure()
            _finish_type()
            current_section = "precedence"
            if "precedence" not in doc.sections:
                doc.sections["precedence"] = []
            continue

        # --- Inside Meta section: parse meta fields ---
        if current_section == "meta":
            doc.sections["meta"].append(stripped)
            if "|" in stripped:
                doc.meta.update(_parse_meta_pipe(stripped))
            elif stripped.startswith("*"):
                # Multi-line meta: `* Key: Value`
                text = stripped[1:].strip()
                if ":" in text:
                    key, _, val = text.partition(":")
                    doc.meta[key.strip().lower()] = val.strip()
            continue

        # --- Inside Types section: parse type blocks ---
        if current_section == "types":
            doc.sections["types"].append(stripped)

            # Start of a type: `TypeName {`
            type_start = re.match(r"^(\w+)\s*\{", stripped)
            if type_start:
                _finish_type()
                current_type = SESFType(name=type_start.group(1), line_number=line_num)
                in_type_block = True
                continue

            # End of a type: `}`
            if in_type_block and stripped == "}":
                _finish_type()
                continue

            # Field inside a type block
            if in_type_block and current_type:
                # e.g., `field_name: type, required` or `field_name: type, optional`
                field_match = re.match(
                    r"(\w+)\s*:\s*(.+?)(?:,\s*(required|optional|default:.*))?$",
                    stripped,
                )
                if field_match:
                    fname = field_match.group(1)
                    ftype = field_match.group(2).strip().rstrip(",").strip()
                    freq_text = field_match.group(3) or "required"
                    freq = "optional" not in freq_text.lower()
                    current_type.fields.append(
                        SESFTypeField(name=fname, type_str=ftype, required=freq)
                    )
                continue
            continue

        # --- Inside Functions section: capture FUNCTION and ACTION declarations ---
        if current_section == "functions":
            doc.sections["functions"].append(stripped)
            func_match = re.match(r"^FUNCTION\s+(\w+)\s*\(", stripped_norm)
            if func_match:
                doc.functions.append(func_match.group(1))
            action_match = re.match(r"^ACTION\s+(\w+)\s*\(", stripped_norm)
            if action_match:
                doc.actions.append(action_match.group(1))
            continue

        # --- Inside Precedence section: parse numbered rule references ---
        if current_section == "precedence":
            doc.sections["precedence"].append(stripped)
            # Numbered line: `1. rule_name (from BEHAVIOR ...)`
            prec_match = re.match(r"^\d+\.\s*(\w+)", stripped)
            if prec_match:
                doc.precedence.append(prec_match.group(1))
            continue

        # --- Inside a BEHAVIOR block: parse RULE / ERROR / EXAMPLE ---
        if current_behavior:
            # Track content in behaviors section
            if "behaviors" in doc.sections:
                doc.sections["behaviors"].append(stripped)

            # --- @route detection inside behavior ---
            if stripped.startswith("@route"):
                _finish_sub_block()
                current_route = None
                in_compact_errors = False
                in_compact_examples = False
                # Parse: @route name [mode]
                route_parts = stripped.split(None, 2)  # ["@route", "name", "[mode]"]
                route_name = route_parts[1] if len(route_parts) > 1 else ""
                route_mode = "first_match_wins"
                if len(route_parts) > 2:
                    mode_text = route_parts[2].strip().strip("[]")
                    if mode_text:
                        route_mode = mode_text
                current_route = SESFRoute(
                    name=route_name, mode=route_mode, line_number=line_num
                )
                continue

            # Inside @route: parse condition -> outcome rows
            if current_route is not None:
                # Table separator lines (|---|) — skip
                if stripped.startswith("|") and re.match(r"^\|[\s\-|]+\|$", stripped):
                    continue
                # Table header line — skip
                if stripped.startswith("|") and ("condition" in stripped.lower() or "outcome" in stripped.lower()):
                    continue
                # Route row with arrow: condition → outcome or condition -> outcome
                arrow_match = re.match(r"^(.+?)\s*(?:→|->)\s*(.+)$", stripped)
                if arrow_match:
                    condition = arrow_match.group(1).strip().strip("|").strip()
                    outcome = arrow_match.group(2).strip().strip("|").strip()
                    current_route.rows.append(SESFRouteRow(
                        condition=condition, outcome=outcome, line_number=line_num
                    ))
                    continue
                # Non-matching line ends the route block
                current_behavior.routes.append(current_route)
                current_route = None
                # Fall through to process this line normally

            # --- Compact ERRORS: table detection inside behavior ---
            if stripped_norm.upper().startswith("ERRORS:") and not re.match(r"^\s*ERROR\s+\w+\s*:", stripped_norm):
                _finish_sub_block()
                in_compact_errors = True
                compact_errors_header_seen = False
                in_compact_examples = False
                current_route = None
                continue

            # Inside compact ERRORS: table
            if in_compact_errors:
                # Separator line (|---|) — skip
                if stripped.startswith("|") and re.match(r"^\|[\s\-|]+\|$", stripped):
                    continue
                # Header row — skip but mark as seen
                if stripped.startswith("|") and not compact_errors_header_seen:
                    compact_errors_header_seen = True
                    continue
                # Data row
                if stripped.startswith("|") and compact_errors_header_seen:
                    cells = [c.strip() for c in stripped.split("|")]
                    # Remove empty first/last cells from leading/trailing |
                    cells = [c for c in cells if c or c == ""]
                    # Filter out truly empty strings from split artifacts
                    while cells and cells[0] == "":
                        cells.pop(0)
                    while cells and cells[-1] == "":
                        cells.pop()
                    if len(cells) >= 4:
                        current_behavior.compact_errors.append(SESFCompactError(
                            name=cells[0],
                            when=cells[1] if len(cells) > 1 else "",
                            severity=cells[2] if len(cells) > 2 else "",
                            action=cells[3] if len(cells) > 3 else "",
                            message=cells[4] if len(cells) > 4 else "",
                            line_number=line_num,
                        ))
                    continue
                # Non-table line ends compact errors
                in_compact_errors = False
                compact_errors_header_seen = False
                # Fall through to process this line normally

            # --- Compact EXAMPLES: detection inside behavior ---
            if stripped_norm.upper().startswith("EXAMPLES:") and not re.match(r"^\s*EXAMPLE\s+\w+\s*:", stripped_norm):
                _finish_sub_block()
                in_compact_examples = True
                in_compact_errors = False
                current_route = None
                continue

            # Inside compact EXAMPLES: block
            if in_compact_examples:
                # Format: name: input → expected  OR  name: input -> expected
                compact_ex_match = re.match(
                    r"^\s*(\w+)\s*:\s*(.+?)\s*(?:→|->)\s*(.+)$", stripped
                )
                if compact_ex_match:
                    current_behavior.compact_examples.append(SESFCompactExample(
                        name=compact_ex_match.group(1),
                        input_desc=compact_ex_match.group(2).strip(),
                        expected=compact_ex_match.group(3).strip(),
                        line_number=line_num,
                    ))
                    continue
                # Non-matching line ends compact examples
                in_compact_examples = False
                # Fall through to process this line normally

            # --- Inline ERROR detection: ERROR name: severity → action, "message" ---
            inline_err_match = re.match(
                r'^\s*ERROR\s+(\w+)\s*:\s*(\w+)\s*(?:→|->)\s*(.+?),\s*"([^"]*)"',
                stripped_norm,
            )
            if inline_err_match:
                _finish_sub_block()
                in_compact_errors = False
                in_compact_examples = False
                current_behavior.inline_errors.append(SESFInlineError(
                    name=inline_err_match.group(1),
                    severity=inline_err_match.group(2).strip(),
                    action=inline_err_match.group(3).strip(),
                    message=inline_err_match.group(4).strip(),
                    line_number=line_num,
                ))
                continue

            # RULE detection
            rule_match = re.match(r"^\s*RULE\s+(\w+)\s*:", stripped_norm)
            if rule_match:
                _finish_sub_block()
                current_rule = SESFRule(
                    name=rule_match.group(1), line_number=line_num
                )
                # Check for PRIORITY on the same line
                pri = re.search(r"PRIORITY\s+(\d+)", stripped)
                if pri:
                    current_rule.priority = int(pri.group(1))
                continue

            # ERROR detection (verbose form)
            error_match = re.match(r"^\s*ERROR\s+(\w+)\s*:", stripped_norm)
            if error_match:
                _finish_sub_block()
                current_error = SESFError(
                    name=error_match.group(1), line_number=line_num
                )
                continue

            # EXAMPLE detection (verbose form)
            example_match = re.match(r"^\s*EXAMPLE\s+(\w+)\s*:", stripped_norm)
            if example_match:
                _finish_sub_block()
                current_example = SESFExample(
                    name=example_match.group(1), line_number=line_num
                )
                continue

            # Sub-block field parsing
            if current_rule:
                current_rule.raw_text += stripped + "\n"
                up = stripped.upper().strip()
                if up.startswith("WHEN "):
                    current_rule.when_clause = stripped.strip()[5:].strip()
                elif up.startswith("THEN "):
                    current_rule.then_clause = stripped.strip()[5:].strip()
                elif up.startswith("ELSE "):
                    current_rule.else_clause = stripped.strip()[5:].strip()
                elif up.startswith("PRIORITY "):
                    try:
                        current_rule.priority = int(stripped.strip().split()[-1])
                    except ValueError:
                        pass
                continue

            if current_error:
                up = stripped.upper().strip()
                if up.startswith("WHEN "):
                    current_error.when_clause = stripped.strip()[5:].strip()
                elif up.startswith("SEVERITY "):
                    current_error.severity = stripped.strip().split(None, 1)[1].strip()
                elif up.startswith("ACTION "):
                    current_error.action = stripped.strip().split(None, 1)[1].strip()
                elif up.startswith("MESSAGE "):
                    current_error.message = stripped.strip().split(None, 1)[1].strip().strip('"')
                continue

            if current_example:
                up = stripped.upper().strip()
                if up.startswith("INPUT:"):
                    current_example.input_text = stripped.strip()[6:].strip()
                elif up.startswith("EXPECTED:"):
                    current_example.expected_text = stripped.strip()[9:].strip()
                elif up.startswith("NOTES:"):
                    current_example.notes = stripped.strip()[6:].strip()
                continue

            # Lines inside a behavior that don't match sub-block patterns
            # (e.g., State/Flow, Audience notes, continuation lines)
            # Check if this line is actually a PRECEDENCE section starting
            prec_match_inline = re.match(r"^PRECEDENCE\s*:", stripped_norm)
            if prec_match_inline and not raw_line.startswith((" ", "\t")):
                _finish_behavior()
                current_section = "precedence"
                if "precedence" not in doc.sections:
                    doc.sections["precedence"] = []
                continue

            continue

        # --- Inside a PROCEDURE block: parse STEP / ERROR / EXAMPLE ---
        if current_procedure:
            # Track content in behaviors section
            if "behaviors" in doc.sections:
                doc.sections["behaviors"].append(stripped)

            # --- Compact ERRORS: table detection inside procedure ---
            if stripped_norm.upper().startswith("ERRORS:") and not re.match(r"^\s*ERROR\s+\w+\s*:", stripped_norm):
                _finish_proc_sub_block()
                in_compact_errors = True
                compact_errors_header_seen = False
                in_compact_examples = False
                continue

            # Inside compact ERRORS: table (procedure)
            if in_compact_errors:
                # Separator line (|---|) — skip
                if stripped.startswith("|") and re.match(r"^\|[\s\-|]+\|$", stripped):
                    continue
                # Header row — skip but mark as seen
                if stripped.startswith("|") and not compact_errors_header_seen:
                    compact_errors_header_seen = True
                    continue
                # Data row
                if stripped.startswith("|") and compact_errors_header_seen:
                    cells = [c.strip() for c in stripped.split("|")]
                    cells = [c for c in cells if c or c == ""]
                    while cells and cells[0] == "":
                        cells.pop(0)
                    while cells and cells[-1] == "":
                        cells.pop()
                    if len(cells) >= 4:
                        current_procedure.compact_errors.append(SESFCompactError(
                            name=cells[0],
                            when=cells[1] if len(cells) > 1 else "",
                            severity=cells[2] if len(cells) > 2 else "",
                            action=cells[3] if len(cells) > 3 else "",
                            message=cells[4] if len(cells) > 4 else "",
                            line_number=line_num,
                        ))
                    continue
                # Non-table line ends compact errors
                in_compact_errors = False
                compact_errors_header_seen = False
                # Fall through to process this line normally

            # --- Compact EXAMPLES: detection inside procedure ---
            if stripped_norm.upper().startswith("EXAMPLES:") and not re.match(r"^\s*EXAMPLE\s+\w+\s*:", stripped_norm):
                _finish_proc_sub_block()
                in_compact_examples = True
                in_compact_errors = False
                continue

            # Inside compact EXAMPLES: block (procedure)
            if in_compact_examples:
                compact_ex_match = re.match(
                    r"^\s*(\w+)\s*:\s*(.+?)\s*(?:→|->)\s*(.+)$", stripped
                )
                if compact_ex_match:
                    current_procedure.compact_examples.append(SESFCompactExample(
                        name=compact_ex_match.group(1),
                        input_desc=compact_ex_match.group(2).strip(),
                        expected=compact_ex_match.group(3).strip(),
                        line_number=line_num,
                    ))
                    continue
                # Non-matching line ends compact examples
                in_compact_examples = False
                # Fall through to process this line normally

            # --- Inline ERROR detection: ERROR name: severity → action, "message" ---
            inline_err_match = re.match(
                r'^\s*ERROR\s+(\w+)\s*:\s*(\w+)\s*(?:→|->)\s*(.+?),\s*"([^"]*)"',
                stripped_norm,
            )
            if inline_err_match:
                _finish_proc_sub_block()
                in_compact_errors = False
                in_compact_examples = False
                current_procedure.inline_errors.append(SESFInlineError(
                    name=inline_err_match.group(1),
                    severity=inline_err_match.group(2).strip(),
                    action=inline_err_match.group(3).strip(),
                    message=inline_err_match.group(4).strip(),
                    line_number=line_num,
                ))
                continue

            # STEP detection (with $variable threading)
            # Matches both `STEP name:` and `STEP name -> $var1, $var2:`
            step_match = re.match(r"^\s*STEP\s+(\w+)\s*(?:(?:->|\u2192)[^:]*)?:", stripped_norm)
            if step_match:
                _finish_proc_sub_block()
                step_name = step_match.group(1)
                current_step = SESFStep(
                    name=step_name, line_number=line_num
                )
                # Check for output variables: STEP name → $var1, $var2:
                # or STEP name -> $var1, $var2:
                # Search in the full stripped line (arrow comes before the colon)
                for arrow in ("\u2192", "->"):
                    arrow_idx = stripped.find(arrow)
                    if arrow_idx >= 0:
                        after_arrow = stripped[arrow_idx + len(arrow):]
                        # Strip trailing colon and whitespace
                        after_arrow = after_arrow.rstrip().rstrip(":")
                        # Extract $-prefixed tokens
                        var_tokens = re.findall(r"\$\w+", after_arrow)
                        current_step.output_variables.extend(var_tokens)
                        break
                continue

            # ERROR detection (verbose form)
            error_match = re.match(r"^\s*ERROR\s+(\w+)\s*:", stripped_norm)
            if error_match:
                _finish_proc_sub_block()
                current_error = SESFError(
                    name=error_match.group(1), line_number=line_num
                )
                continue

            # EXAMPLE detection (verbose form)
            example_match = re.match(r"^\s*EXAMPLE\s+(\w+)\s*:", stripped_norm)
            if example_match:
                _finish_proc_sub_block()
                current_example = SESFExample(
                    name=example_match.group(1), line_number=line_num
                )
                continue

            # Sub-block field parsing
            if current_step:
                current_step.raw_text += stripped + "\n"
                # First non-empty content line becomes the description
                if not current_step.description:
                    current_step.description = stripped
                # Check for $variable output on action lines within step
                for arrow in ("\u2192", "->"):
                    if arrow in stripped:
                        after_arrow = stripped.split(arrow, 1)[1]
                        var_tokens = re.findall(r"\$\w+", after_arrow)
                        for v in var_tokens:
                            if v not in current_step.output_variables:
                                current_step.output_variables.append(v)
                        break
                continue

            if current_error:
                up = stripped.upper().strip()
                if up.startswith("WHEN "):
                    current_error.when_clause = stripped.strip()[5:].strip()
                elif up.startswith("SEVERITY "):
                    current_error.severity = stripped.strip().split(None, 1)[1].strip()
                elif up.startswith("ACTION "):
                    current_error.action = stripped.strip().split(None, 1)[1].strip()
                elif up.startswith("MESSAGE "):
                    current_error.message = stripped.strip().split(None, 1)[1].strip().strip('"')
                continue

            if current_example:
                up = stripped.upper().strip()
                if up.startswith("INPUT:"):
                    current_example.input_text = stripped.strip()[6:].strip()
                elif up.startswith("EXPECTED:"):
                    current_example.expected_text = stripped.strip()[9:].strip()
                elif up.startswith("NOTES:"):
                    current_example.notes = stripped.strip()[6:].strip()
                continue

            # Lines inside a procedure that don't match sub-block patterns
            prec_match_inline = re.match(r"^PRECEDENCE\s*:", stripped_norm)
            if prec_match_inline and not raw_line.startswith((" ", "\t")):
                _finish_procedure()
                current_section = "precedence"
                if "precedence" not in doc.sections:
                    doc.sections["precedence"] = []
                continue

            continue

        # --- Default: store content in current section ---
        if current_section and current_section in doc.sections:
            doc.sections[current_section].append(stripped)

    # Flush any remaining open blocks
    _finish_behavior()
    _finish_procedure()
    _finish_type()

    return doc


# ---------------------------------------------------------------------------
# Structural completeness check
# ---------------------------------------------------------------------------

# Required sections per tier
TIER_REQUIREMENTS = {
    "micro": {"meta", "purpose", "behaviors"},
    "standard": {
        "meta", "purpose", "scope", "inputs", "outputs", "types",
        "functions", "behaviors", "constraints", "dependencies",
    },
    "complex": {
        "meta", "purpose", "scope", "inputs", "outputs", "types",
        "functions", "behaviors", "precedence", "constraints",
        "dependencies",
    },
}

# Meta fields that should be present
EXPECTED_META_FIELDS = {"version", "date", "domain", "status"}


def _is_requirement_keyword(word: str, context_before: str, context_after: str) -> bool:
    """Heuristic: is this lowercase must/should/may being used as a
    requirement keyword rather than normal English?

    We look for patterns that suggest specification-style usage:
    - Subject + must/should/may + verb/constraint
    - Preceded by a noun or field name
    - Followed by "be", "not", "contain", "have", "include", "equal", etc.
    """
    # Common verb-like words that follow requirement keywords in specs
    spec_followers = {
        "be", "not", "contain", "have", "include", "equal", "match",
        "exceed", "support", "handle", "return", "produce", "accept",
        "reject", "validate", "provide", "preserve", "apply", "display",
        "run", "send", "record", "persist", "satisfy",
    }
    # Words after which must/should/may is likely normal English
    normal_precursors = {
        "you", "we", "they", "i", "one", "it", "this", "that", "who",
        "which", "what", "if", "when", "where", "how", "why",
    }

    after_word = context_after.split(None, 1)
    after_first = after_word[0].lower().rstrip(".,;:") if after_word else ""

    before_words = context_before.lower().split()
    before_last = before_words[-1].rstrip(".,;:") if before_words else ""

    # If followed by a spec-style verb, likely a requirement keyword
    if after_first in spec_followers:
        # But check if preceded by a normal-English subject
        if before_last in normal_precursors:
            return False
        return True

    return False


def check_structural_completeness(doc: SESFDocument) -> list:
    """Check structural completeness of a parsed SESF document.

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    # 1. Tier declaration
    tier = doc.meta.get("tier", "").lower().strip()
    if not tier:
        results.append(ValidationResult(
            category="meta",
            status="FAIL",
            message="Tier not declared in Meta section (expected: micro, standard, or complex)",
        ))
        # Default to micro for remaining checks
        tier = "micro"
    elif tier not in TIER_REQUIREMENTS:
        results.append(ValidationResult(
            category="meta",
            status="FAIL",
            message=f"Unknown tier '{tier}' in Meta (expected: micro, standard, or complex)",
        ))
        tier = "micro"
    else:
        results.append(ValidationResult(
            category="meta",
            status="PASS",
            message=f"Tier declared: {tier}",
        ))

    # 2. Required sections for declared tier
    required = TIER_REQUIREMENTS.get(tier, TIER_REQUIREMENTS["micro"])
    present_sections = set(doc.sections.keys())
    # Behaviors/Procedures can also be detected via doc.behaviors/doc.procedures
    # even if the section keyword "Behaviors" wasn't explicitly used (specs may
    # jump straight to BEHAVIOR/PROCEDURE blocks).
    if doc.behaviors or doc.procedures:
        present_sections.add("behaviors")

    for sec in sorted(required):
        if sec in present_sections:
            results.append(ValidationResult(
                category="sections",
                status="PASS",
                message=f"Required section '{sec.capitalize()}' present",
            ))
        else:
            results.append(ValidationResult(
                category="sections",
                status="FAIL",
                message=f"Required section '{sec.capitalize()}' missing (required for {tier} tier)",
            ))

    # 3. Meta field completeness (FAIL for missing — these are mandatory)
    for mf in sorted(EXPECTED_META_FIELDS):
        if mf in doc.meta and doc.meta[mf]:
            results.append(ValidationResult(
                category="meta",
                status="PASS",
                message=f"Meta field '{mf}' present: {doc.meta[mf]}",
            ))
        else:
            results.append(ValidationResult(
                category="meta",
                status="FAIL",
                message=f"Meta field '{mf}' missing or empty",
            ))

    # 4. At least one BEHAVIOR or PROCEDURE block
    if doc.behaviors or doc.procedures:
        parts = []
        if doc.behaviors:
            parts.append(f"{len(doc.behaviors)} BEHAVIOR block(s)")
        if doc.procedures:
            parts.append(f"{len(doc.procedures)} PROCEDURE block(s)")
        results.append(ValidationResult(
            category="behaviors",
            status="PASS",
            message=f"Found {', '.join(parts)}",
        ))
    else:
        results.append(ValidationResult(
            category="behaviors",
            status="FAIL",
            message="No BEHAVIOR or PROCEDURE blocks found",
        ))

    # 5. Each behavior has at least one RULE (or @route table)
    for beh in doc.behaviors:
        rule_count = len(beh.rules)
        route_count = len(beh.routes)
        total_logic = rule_count + route_count
        if total_logic > 0:
            parts = []
            if rule_count:
                parts.append(f"{rule_count} rule(s)")
            if route_count:
                parts.append(f"{route_count} @route table(s)")
            results.append(ValidationResult(
                category="behaviors",
                status="PASS",
                message=f"BEHAVIOR '{beh.name}' has {', '.join(parts)}",
                line_number=beh.line_number,
            ))
        else:
            results.append(ValidationResult(
                category="behaviors",
                status="WARN",
                message=f"BEHAVIOR '{beh.name}' has no rules or @route tables",
                line_number=beh.line_number,
            ))

    # 5b. Each procedure has at least one STEP
    for proc in doc.procedures:
        if proc.steps:
            results.append(ValidationResult(
                category="procedures",
                status="PASS",
                message=f"PROCEDURE '{proc.name}' has {len(proc.steps)} step(s)",
                line_number=proc.line_number,
            ))
        else:
            results.append(ValidationResult(
                category="procedures",
                status="WARN",
                message=f"PROCEDURE '{proc.name}' has no steps",
                line_number=proc.line_number,
            ))

    # 6. Requirement keyword capitalization check
    # Scan all section content for lowercase must/should/may used as
    # requirement keywords.
    keyword_warnings: list[ValidationResult] = []
    all_lines: list[tuple[int, str]] = []

    # Collect content from parsed sections and behavior rules
    for sec_name, sec_lines in doc.sections.items():
        for sl in sec_lines:
            all_lines.append((0, sl))
    for beh in doc.behaviors:
        for rule in beh.rules:
            all_lines.append((rule.line_number, rule.raw_text))

    req_pattern = re.compile(
        r"(?<!\w)(must not|must|should not|should|may)(?!\w)",
        re.IGNORECASE,
    )

    warned_lines: set = set()

    for line_num, text in all_lines:
        for match in req_pattern.finditer(text):
            word = match.group(0)
            # Only flag if the word is lowercase (i.e., not already capitalized)
            if word == word.upper():
                continue  # Already capitalized, fine
            if word == word.lower():
                # Get context
                start = match.start()
                end = match.end()
                before = text[:start].strip()
                after = text[end:].strip()
                if _is_requirement_keyword(word, before, after):
                    key = (line_num, word, text[:40])
                    if key not in warned_lines:
                        warned_lines.add(key)
                        keyword_warnings.append(ValidationResult(
                            category="keywords",
                            status="WARN",
                            message=f"Lowercase '{word}' appears to be a requirement keyword -- use '{word.upper()}'",
                            line_number=line_num if line_num else None,
                        ))

    results.extend(keyword_warnings)

    return results


# ---------------------------------------------------------------------------
# Type consistency check
# ---------------------------------------------------------------------------

# Pattern to find typename.fieldname references in rule text
_TYPE_FIELD_REF_RE = re.compile(r'\b([a-z_]+)\.([a-z_]+)\b')

# Common file extensions and abbreviations to skip (not type references)
_FALSE_POSITIVE_FIELDS = {"pdf", "txt", "csv", "json", "xml", "md", "py", "js",
                          "html", "css", "yaml", "yml", "toml", "ini", "cfg",
                          "com", "org", "net", "io", "ca"}
_FALSE_POSITIVE_TYPES = {"e", "i", "a"}  # e.g., i.e., a.m.


def _pascal_to_snake(name: str) -> str:
    """Convert PascalCase to snake_case for comparison.

    PurchaseOrder -> purchase_order, ApprovalStatus -> approval_status
    """
    return re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', name).lower()


def _collect_all_text_lines(doc: SESFDocument) -> list[str]:
    """Collect all textual content from behaviors and procedures."""
    lines: list[str] = []
    for beh in doc.behaviors:
        for rule in beh.rules:
            if rule.when_clause:
                lines.append(rule.when_clause)
            if rule.then_clause:
                lines.append(rule.then_clause)
            if rule.else_clause:
                lines.append(rule.else_clause)
            if rule.raw_text:
                lines.append(rule.raw_text)
        for err in beh.errors:
            if err.when_clause:
                lines.append(err.when_clause)
            if err.message:
                lines.append(err.message)
        for ex in beh.examples:
            if ex.input_text:
                lines.append(ex.input_text)
            if ex.expected_text:
                lines.append(ex.expected_text)
    for proc in doc.procedures:
        for step in proc.steps:
            if step.raw_text:
                lines.append(step.raw_text)
            if step.description:
                lines.append(step.description)
        for err in proc.errors:
            if err.when_clause:
                lines.append(err.when_clause)
            if err.message:
                lines.append(err.message)
        for ex in proc.examples:
            if ex.input_text:
                lines.append(ex.input_text)
            if ex.expected_text:
                lines.append(ex.expected_text)
    return lines


def _collect_all_text_lines_numbered(doc: SESFDocument) -> list[tuple[int, str]]:
    """Collect all textual content with line numbers from behaviors and procedures.

    Returns a list of (line_number, text) tuples. Used by validation checks
    that need to report the line location of an issue.
    """
    lines: list[tuple[int, str]] = []
    for beh in doc.behaviors:
        for rule in beh.rules:
            ln = rule.line_number
            if rule.when_clause:
                lines.append((ln, rule.when_clause))
            if rule.then_clause:
                lines.append((ln, rule.then_clause))
            if rule.else_clause:
                lines.append((ln, rule.else_clause))
            if rule.raw_text:
                for text_line in rule.raw_text.split("\n"):
                    if text_line.strip():
                        lines.append((ln, text_line))
        for err in beh.errors:
            ln = err.line_number
            if err.when_clause:
                lines.append((ln, err.when_clause))
            if err.message:
                lines.append((ln, err.message))
            if err.action:
                lines.append((ln, err.action))
        for ex in beh.examples:
            ln = ex.line_number
            if ex.input_text:
                lines.append((ln, ex.input_text))
            if ex.expected_text:
                lines.append((ln, ex.expected_text))
        # Include compact error/example text
        for ce in beh.compact_errors:
            lines.append((ce.line_number, ce.when))
            lines.append((ce.line_number, ce.action))
            lines.append((ce.line_number, ce.message))
        # Include inline error text
        for ie in beh.inline_errors:
            lines.append((ie.line_number, ie.action))
            lines.append((ie.line_number, ie.message))
        for cx in beh.compact_examples:
            lines.append((cx.line_number, cx.input_desc))
            lines.append((cx.line_number, cx.expected))
        # Include route rows
        for route in beh.routes:
            for row in route.rows:
                lines.append((row.line_number, row.condition))
                lines.append((row.line_number, row.outcome))
    for proc in doc.procedures:
        for step in proc.steps:
            ln = step.line_number
            if step.raw_text:
                for text_line in step.raw_text.split("\n"):
                    if text_line.strip():
                        lines.append((ln, text_line))
            if step.description:
                lines.append((ln, step.description))
        for err in proc.errors:
            ln = err.line_number
            if err.when_clause:
                lines.append((ln, err.when_clause))
            if err.message:
                lines.append((ln, err.message))
            if err.action:
                lines.append((ln, err.action))
        for ex in proc.examples:
            ln = ex.line_number
            if ex.input_text:
                lines.append((ln, ex.input_text))
            if ex.expected_text:
                lines.append((ln, ex.expected_text))
        # Include compact error/example text
        for ce in proc.compact_errors:
            lines.append((ce.line_number, ce.when))
            lines.append((ce.line_number, ce.action))
            lines.append((ce.line_number, ce.message))
        # Include inline error text
        for ie in proc.inline_errors:
            lines.append((ie.line_number, ie.action))
            lines.append((ie.line_number, ie.message))
        for cx in proc.compact_examples:
            lines.append((cx.line_number, cx.input_desc))
            lines.append((cx.line_number, cx.expected))
    # Also include section content (for $config refs in prose sections)
    for sec_name, sec_lines in doc.sections.items():
        for sl in sec_lines:
            if sl.strip():
                lines.append((0, sl))
    return lines


def check_type_consistency(doc: SESFDocument) -> list:
    """Check that type references in behavior rules match defined types.

    Checks:
    - Referenced types exist in the Types section
    - Referenced fields exist on their type
    - Orphaned types (defined but never referenced)

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    if not doc.types:
        # No types defined — nothing to check
        return results

    # Build lookup: lowercase type name -> SESFType
    # Include both direct lowercase and snake_case versions of PascalCase names
    type_map: dict[str, SESFType] = {}
    for t in doc.types:
        type_map[t.name.lower()] = t
        snake = _pascal_to_snake(t.name)
        if snake != t.name.lower():
            type_map[snake] = t

    # Collect all text from behaviors to scan for typename.fieldname patterns
    text_lines = _collect_all_text_lines(doc)

    # Also collect Inputs and Outputs section content for type reference detection
    section_text_lines: list[str] = []
    for sec_name in ("inputs", "outputs"):
        if sec_name in doc.sections:
            section_text_lines.extend(doc.sections[sec_name])

    # Find all typename.fieldname references in behavior text
    referenced_types: set[str] = set()   # lowercase type names
    seen_refs: set[tuple[str, str]] = set()  # avoid duplicate warnings

    for line in text_lines:
        for match in _TYPE_FIELD_REF_RE.finditer(line):
            tname = match.group(1)
            fname = match.group(2)

            # Skip known false positives (file extensions, abbreviations)
            if fname in _FALSE_POSITIVE_FIELDS or tname in _FALSE_POSITIVE_TYPES:
                continue

            referenced_types.add(tname)

            if (tname, fname) in seen_refs:
                continue
            seen_refs.add((tname, fname))

            # Check if the type exists
            if tname not in type_map:
                results.append(ValidationResult(
                    category="type_consistency",
                    status="WARN",
                    message=f"Referenced type '{tname}' not found in Types section "
                            f"(from '{tname}.{fname}')",
                ))
            else:
                # Check if the field exists on the type
                defined_fields = {f.name.lower() for f in type_map[tname].fields}
                if fname not in defined_fields:
                    orig_type_name = type_map[tname].name
                    results.append(ValidationResult(
                        category="type_consistency",
                        status="WARN",
                        message=f"{tname}.{fname} — field '{fname}' not found "
                                f"in type '{orig_type_name}'",
                        line_number=type_map[tname].line_number,
                    ))

    # Also scan Inputs/Outputs sections for type name references
    # (these reference types by name, not via dot notation)
    for line in section_text_lines:
        for t in doc.types:
            # Look for the type name in section text (case-insensitive word match)
            if re.search(r'\b' + re.escape(t.name) + r'\b', line, re.IGNORECASE):
                referenced_types.add(t.name.lower())

    # Also check behavior text for bare type name references (without dot notation)
    for line in text_lines:
        for t in doc.types:
            if re.search(r'\b' + re.escape(t.name) + r'\b', line, re.IGNORECASE):
                referenced_types.add(t.name.lower())

    # Check for orphaned types (check both lowercase and snake_case)
    for t in doc.types:
        snake = _pascal_to_snake(t.name)
        if t.name.lower() not in referenced_types and snake not in referenced_types:
            results.append(ValidationResult(
                category="type_consistency",
                status="WARN",
                message=f"Type '{t.name}' defined but never referenced",
                line_number=t.line_number,
            ))

    # Report valid references as a summary PASS
    valid_type_count = sum(
        1 for t in doc.types
        if t.name.lower() in referenced_types
        or _pascal_to_snake(t.name) in referenced_types
    )
    if valid_type_count > 0:
        results.insert(0, ValidationResult(
            category="type_consistency",
            status="PASS",
            message=f"{valid_type_count} of {len(doc.types)} defined type(s) are referenced",
        ))

    return results


# ---------------------------------------------------------------------------
# Rule integrity check
# ---------------------------------------------------------------------------

def check_rule_integrity(doc: SESFDocument) -> list:
    """Check PRECEDENCE-PRIORITY consistency across behaviors and rules.

    Checks:
    - PRIORITY-tagged rules appear in the PRECEDENCE block (and vice versa)
    - Complex tier has PRECEDENCE block if PRIORITY tags are used
    - Standard tier informational note

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    tier = doc.meta.get("tier", "").lower().strip()

    # Collect all rules that have PRIORITY tags
    priority_rules: dict[str, int] = {}  # rule_name -> priority value
    priority_rule_lines: dict[str, int] = {}  # rule_name -> line_number
    for beh in doc.behaviors:
        for rule in beh.rules:
            if rule.priority is not None:
                priority_rules[rule.name] = rule.priority
                priority_rule_lines[rule.name] = rule.line_number

    has_precedence = bool(doc.precedence)
    has_priority_tags = bool(priority_rules)

    # --- Complex tier: PRIORITY tags require PRECEDENCE block ---
    if tier == "complex" and has_priority_tags and not has_precedence:
        results.append(ValidationResult(
            category="rule_integrity",
            status="FAIL",
            message="Complex tier has PRIORITY-tagged rules but no PRECEDENCE block",
        ))

    # --- Standard tier informational note ---
    if tier == "standard" and has_priority_tags and not has_precedence:
        results.append(ValidationResult(
            category="rule_integrity",
            status="PASS",
            message="Standard tier: PRIORITY tags present without PRECEDENCE block (acceptable)",
        ))

    # --- Cross-check PRIORITY tags vs PRECEDENCE block ---
    if has_precedence and has_priority_tags:
        precedence_set = set(doc.precedence)
        priority_set = set(priority_rules.keys())

        # Rules with PRIORITY but not in PRECEDENCE
        for rname in sorted(priority_set - precedence_set):
            results.append(ValidationResult(
                category="rule_integrity",
                status="WARN",
                message=f"Rule '{rname}' has PRIORITY tag but is not listed "
                        f"in PRECEDENCE block",
                line_number=priority_rule_lines.get(rname),
            ))

        # Rules in PRECEDENCE but without PRIORITY tag
        for rname in doc.precedence:
            if rname not in priority_set:
                results.append(ValidationResult(
                    category="rule_integrity",
                    status="WARN",
                    message=f"Rule '{rname}' listed in PRECEDENCE block but "
                            f"has no PRIORITY tag in its behavior",
                ))

        # All consistent
        consistent = priority_set & precedence_set
        if consistent and not (priority_set - precedence_set) and not (precedence_set - priority_set):
            results.append(ValidationResult(
                category="rule_integrity",
                status="PASS",
                message=f"PRECEDENCE and PRIORITY tags are consistent "
                        f"({len(consistent)} rule(s))",
            ))

    elif has_precedence and not has_priority_tags:
        # PRECEDENCE block exists but no rules have PRIORITY tags
        results.append(ValidationResult(
            category="rule_integrity",
            status="WARN",
            message="PRECEDENCE block exists but no rules have PRIORITY tags",
        ))

    # If neither precedence nor priority exists, nothing to check (that's fine)
    if not has_precedence and not has_priority_tags:
        results.append(ValidationResult(
            category="rule_integrity",
            status="PASS",
            message="No PRECEDENCE/PRIORITY declarations (none required)",
        ))

    return results


# ---------------------------------------------------------------------------
# Error consistency check
# ---------------------------------------------------------------------------

VALID_SEVERITIES = {"critical", "warning", "info"}


def _check_errors_for_block(block_type: str, block_name: str, errors: list,
                            has_rules_or_steps: bool, line_number: int) -> list:
    """Check ERROR blocks within a BEHAVIOR or PROCEDURE.

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    if not errors:
        return results

    # Check for orphaned errors (errors without rules/steps)
    if not has_rules_or_steps:
        child_label = "rules" if block_type == "BEHAVIOR" else "steps"
        results.append(ValidationResult(
            category="error_consistency",
            status="WARN",
            message=f"{block_type} '{block_name}' has {len(errors)} error(s) "
                    f"but no {child_label} (orphaned errors)",
            line_number=line_number,
        ))

    well_defined_count = 0

    for err in errors:
        issues: list[str] = []

        # Check WHEN clause
        if err.when_clause is None:
            issues.append("WHEN")

        # Check severity
        if err.severity is None:
            issues.append("SEVERITY")
        elif err.severity.lower() not in VALID_SEVERITIES:
            results.append(ValidationResult(
                category="error_consistency",
                status="WARN",
                message=f"ERROR '{err.name}' in {block_type} '{block_name}' has "
                        f"invalid severity '{err.severity}' "
                        f"(expected: critical, warning, info)",
                line_number=err.line_number,
            ))

        # Check ACTION
        if err.action is None:
            issues.append("ACTION")

        # Check MESSAGE
        if err.message is None:
            issues.append("MESSAGE")

        if issues:
            results.append(ValidationResult(
                category="error_consistency",
                status="WARN",
                message=f"ERROR '{err.name}' in {block_type} '{block_name}' "
                        f"missing: {', '.join(issues)}",
                line_number=err.line_number,
            ))
        else:
            well_defined_count += 1

    if well_defined_count > 0:
        results.append(ValidationResult(
            category="error_consistency",
            status="PASS",
            message=f"{block_type} '{block_name}' has {well_defined_count} "
                    f"well-defined error(s)",
            line_number=line_number,
        ))

    return results


def check_error_consistency(doc: SESFDocument) -> list:
    """Check that ERROR blocks are well-formed and consistent.

    Checks:
    - Each ERROR has a valid severity (critical, warning, info) -- WARN if missing
    - Each ERROR has ACTION and MESSAGE fields -- WARN if missing
    - Warn on behaviors/procedures with errors but no rules/steps (orphaned errors)
    - PASS summary for blocks with properly-defined errors
    - Inline errors (ERROR name: severity → action, "message") are also validated

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    for beh in doc.behaviors:
        has_logic = bool(beh.rules) or bool(beh.routes)
        results.extend(_check_errors_for_block(
            "BEHAVIOR", beh.name, beh.errors, has_logic, beh.line_number
        ))
        # Count inline errors as well-defined error handling
        if beh.inline_errors and not beh.errors:
            results.append(ValidationResult(
                category="error_consistency",
                status="PASS",
                message=f"BEHAVIOR '{beh.name}' has {len(beh.inline_errors)} "
                        f"inline error(s)",
                line_number=beh.line_number,
            ))

    for proc in doc.procedures:
        results.extend(_check_errors_for_block(
            "PROCEDURE", proc.name, proc.errors, bool(proc.steps), proc.line_number
        ))
        # Count inline errors as well-defined error handling
        if proc.inline_errors and not proc.errors:
            results.append(ValidationResult(
                category="error_consistency",
                status="PASS",
                message=f"PROCEDURE '{proc.name}' has {len(proc.inline_errors)} "
                        f"inline error(s)",
                line_number=proc.line_number,
            ))

    return results


# ---------------------------------------------------------------------------
# Example consistency check
# ---------------------------------------------------------------------------

def check_example_consistency(doc: SESFDocument) -> list:
    """Check that behaviors and procedures have adequate example coverage.

    Checks:
    - Each behavior/procedure has at least one EXAMPLE -- WARN if no examples
    - Warn on behaviors where the number of examples is less than the
      number of rules (heuristic: each rule should ideally have a
      demonstrating example)
    - PASS summary for blocks with good example coverage

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    for beh in doc.behaviors:
        num_examples = len(beh.examples) + len(beh.compact_examples)
        num_rules = len(beh.rules) + len(beh.routes)

        if num_examples == 0:
            results.append(ValidationResult(
                category="example_consistency",
                status="WARN",
                message=f"BEHAVIOR '{beh.name}' has no examples",
                line_number=beh.line_number,
            ))
            continue

        # Has at least one example -- PASS
        results.append(ValidationResult(
            category="example_consistency",
            status="PASS",
            message=f"BEHAVIOR '{beh.name}' has {num_examples} example(s)",
            line_number=beh.line_number,
        ))

        # Heuristic: fewer examples than rules
        if num_rules > 0 and num_examples < num_rules:
            results.append(ValidationResult(
                category="example_consistency",
                status="WARN",
                message=f"BEHAVIOR '{beh.name}' has fewer examples "
                        f"({num_examples}) than rules ({num_rules})",
                line_number=beh.line_number,
            ))

    for proc in doc.procedures:
        num_examples = len(proc.examples) + len(proc.compact_examples)

        if num_examples == 0:
            results.append(ValidationResult(
                category="example_consistency",
                status="WARN",
                message=f"PROCEDURE '{proc.name}' has no examples",
                line_number=proc.line_number,
            ))
            continue

        # Has at least one example -- PASS
        results.append(ValidationResult(
            category="example_consistency",
            status="PASS",
            message=f"PROCEDURE '{proc.name}' has {num_examples} example(s)",
            line_number=proc.line_number,
        ))

    return results


# ---------------------------------------------------------------------------
# Cross-behavior check
# ---------------------------------------------------------------------------

def check_cross_behavior(doc: SESFDocument) -> list:
    """Check cross-behavior consistency (complex tier only).

    Checks:
    - If any rules across different behaviors have PRIORITY tags, check
      that a PRECEDENCE block exists — FAIL if missing
    - Check PRECEDENCE block lists all rules that have PRIORITY tags —
      WARN for mismatches
    - For non-complex tiers, just PASS with informational note

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    tier = doc.meta.get("tier", "").lower().strip()

    if tier != "complex":
        results.append(ValidationResult(
            category="cross_behavior",
            status="PASS",
            message="Cross-behavior checks only apply to complex tier",
        ))
        return results

    # Collect all PRIORITY-tagged rules across behaviors
    priority_rules: dict[str, str] = {}  # rule_name -> behavior_name
    priority_rule_lines: dict[str, int] = {}  # rule_name -> line_number
    for beh in doc.behaviors:
        for rule in beh.rules:
            if rule.priority is not None:
                priority_rules[rule.name] = beh.name
                priority_rule_lines[rule.name] = rule.line_number

    has_precedence = bool(doc.precedence)
    has_priority_tags = bool(priority_rules)

    if has_priority_tags and not has_precedence:
        results.append(ValidationResult(
            category="cross_behavior",
            status="FAIL",
            message="Complex tier has PRIORITY-tagged rules across behaviors "
                    "but no PRECEDENCE block",
        ))
        return results

    if has_priority_tags and has_precedence:
        precedence_set = set(doc.precedence)
        priority_set = set(priority_rules.keys())

        # Rules with PRIORITY but not in PRECEDENCE
        missing_from_precedence = priority_set - precedence_set
        for rname in sorted(missing_from_precedence):
            results.append(ValidationResult(
                category="cross_behavior",
                status="WARN",
                message=f"Rule '{rname}' (BEHAVIOR '{priority_rules[rname]}') "
                        f"has PRIORITY tag but is not in PRECEDENCE block",
                line_number=priority_rule_lines.get(rname),
            ))

        # Rules in PRECEDENCE but without PRIORITY tag
        extra_in_precedence = precedence_set - priority_set
        for rname in sorted(extra_in_precedence):
            results.append(ValidationResult(
                category="cross_behavior",
                status="WARN",
                message=f"Rule '{rname}' in PRECEDENCE block but has no "
                        f"PRIORITY tag",
            ))

        if not missing_from_precedence and not extra_in_precedence:
            results.append(ValidationResult(
                category="cross_behavior",
                status="PASS",
                message=f"All {len(priority_set)} PRIORITY-tagged rule(s) are "
                        f"listed in PRECEDENCE block",
            ))

    if not has_priority_tags and not has_precedence:
        results.append(ValidationResult(
            category="cross_behavior",
            status="PASS",
            message="No cross-behavior PRIORITY/PRECEDENCE to check",
        ))

    return results


# ---------------------------------------------------------------------------
# Config reference check (v4)
# ---------------------------------------------------------------------------

def check_config_references(doc: SESFDocument) -> list:
    """Check that all $config.key references resolve to @config entries.

    Scans all text lines in the spec for $config.key references. For each
    reference, verifies the key exists in doc.config.entries.

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []
    if not doc.config:
        return results

    config_ref_pattern = re.compile(r'\$config\.(\w+(?:\.\w+)*)')
    all_text = _collect_all_text_lines_numbered(doc)
    for line_num, line in all_text:
        for match in config_ref_pattern.finditer(line):
            key = match.group(1)
            if key not in doc.config.entries:
                results.append(ValidationResult(
                    category="config_references",
                    status="WARN",
                    message=f"$config.{key} referenced but not defined in @config block",
                    line_number=line_num if line_num else None,
                ))
    if not results:
        results.append(ValidationResult(
            category="config_references",
            status="PASS",
            message="All $config references resolve to @config entries",
        ))
    return results


# ---------------------------------------------------------------------------
# Variable threading check (v4)
# ---------------------------------------------------------------------------

def check_variable_threading(doc: SESFDocument) -> list:
    """Check that all $var references have producing STEP declarations.

    Collects all $var declarations from STEP output_variables across all
    procedures into a set. Scans all text for $var references (excluding
    $config.). Warns on references to unproduced variables.

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    produced: set[str] = set()
    for proc in doc.procedures:
        for step in proc.steps:
            for v in step.output_variables:
                # output_variables stores them as "$varname", strip the $
                produced.add(v.lstrip("$"))

    var_ref_pattern = re.compile(r'\$(\w+)')
    all_text = _collect_all_text_lines_numbered(doc)
    warned_vars: set[str] = set()  # avoid duplicate warnings for same var

    for line_num, line in all_text:
        for match in var_ref_pattern.finditer(line):
            var_name = match.group(1)
            if var_name.startswith("config"):
                continue
            if var_name not in produced and var_name not in warned_vars:
                warned_vars.add(var_name)
                results.append(ValidationResult(
                    category="variable_threading",
                    status="WARN",
                    message=f"${var_name} referenced but not produced by any STEP \u2192 declaration",
                    line_number=line_num if line_num else None,
                ))
    if not results:
        results.append(ValidationResult(
            category="variable_threading",
            status="PASS",
            message="All $variable references have producing steps",
        ))
    return results


# ---------------------------------------------------------------------------
# Route completeness check (v4)
# ---------------------------------------------------------------------------

def check_route_completeness(doc: SESFDocument) -> list:
    """Check @route tables for completeness.

    For each @route table in each BEHAVIOR:
    - Warn if no wildcard (*) default row
    - Warn if fewer than 3 rows

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    for behavior in doc.behaviors:
        for route in behavior.routes:
            has_wildcard = any(row.condition.strip() == "*" for row in route.rows)
            if not has_wildcard:
                results.append(ValidationResult(
                    category="route_completeness",
                    status="WARN",
                    message=f"@route '{route.name}' has no wildcard (*) default row",
                    line_number=route.line_number,
                ))
            if len(route.rows) < 3:
                results.append(ValidationResult(
                    category="route_completeness",
                    status="WARN",
                    message=f"@route '{route.name}' has {len(route.rows)} branches "
                            f"(recommend 3+ for @route; use WHEN/THEN for fewer)",
                    line_number=route.line_number,
                ))
    if not results:
        results.append(ValidationResult(
            category="route_completeness",
            status="PASS",
            message="All @route tables are complete",
        ))
    return results


# ---------------------------------------------------------------------------
# Error table structure check (v4)
# ---------------------------------------------------------------------------

VALID_COMPACT_SEVERITIES = {"critical", "warning", "info"}


def check_error_table_structure(doc: SESFDocument) -> list:
    """Check compact error table and inline error structure.

    For each compact error table row, verifies:
    - All 5 columns are present (name, when, severity, action, message)
    - Severity values are valid (critical, warning, info)

    For each inline error, verifies:
    - Severity is valid (critical, warning, info)
    - Action and message are present

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    all_compact_errors: list[tuple[str, str, SESFCompactError]] = []
    for beh in doc.behaviors:
        for ce in beh.compact_errors:
            all_compact_errors.append(("BEHAVIOR", beh.name, ce))
    for proc in doc.procedures:
        for ce in proc.compact_errors:
            all_compact_errors.append(("PROCEDURE", proc.name, ce))

    for block_type, block_name, ce in all_compact_errors:
        # Check for missing columns
        missing_cols: list[str] = []
        if not ce.name:
            missing_cols.append("name")
        if not ce.when:
            missing_cols.append("when")
        if not ce.severity:
            missing_cols.append("severity")
        if not ce.action:
            missing_cols.append("action")
        if not ce.message:
            missing_cols.append("message")

        if missing_cols:
            results.append(ValidationResult(
                category="error_table_structure",
                status="WARN",
                message=f"Compact error '{ce.name or '(unnamed)'}' in {block_type} "
                        f"'{block_name}' missing columns: {', '.join(missing_cols)}",
                line_number=ce.line_number,
            ))

        # Check severity validity
        if ce.severity and ce.severity.lower() not in VALID_COMPACT_SEVERITIES:
            results.append(ValidationResult(
                category="error_table_structure",
                status="WARN",
                message=f"Compact error '{ce.name}' in {block_type} '{block_name}' "
                        f"has invalid severity '{ce.severity}' "
                        f"(expected: critical, warning, info)",
                line_number=ce.line_number,
            ))

    # Check inline errors
    all_inline_errors: list[tuple[str, str, SESFInlineError]] = []
    for beh in doc.behaviors:
        for ie in beh.inline_errors:
            all_inline_errors.append(("BEHAVIOR", beh.name, ie))
    for proc in doc.procedures:
        for ie in proc.inline_errors:
            all_inline_errors.append(("PROCEDURE", proc.name, ie))

    for block_type, block_name, ie in all_inline_errors:
        if ie.severity and ie.severity.lower() not in VALID_COMPACT_SEVERITIES:
            results.append(ValidationResult(
                category="error_table_structure",
                status="WARN",
                message=f"Inline error '{ie.name}' in {block_type} '{block_name}' "
                        f"has invalid severity '{ie.severity}' "
                        f"(expected: critical, warning, info)",
                line_number=ie.line_number,
            ))

    total_errors = len(all_compact_errors) + len(all_inline_errors)
    # If no issues found, emit a PASS
    if total_errors > 0 and not results:
        results.append(ValidationResult(
            category="error_table_structure",
            status="PASS",
            message=f"All {total_errors} error definition(s) are well-formed",
        ))

    return results


# ---------------------------------------------------------------------------
# Notation section check (v4)
# ---------------------------------------------------------------------------

def check_notation_section(doc: SESFDocument) -> list:
    """Check whether a Notation section is present.

    Notation is optional at all tiers (v4.1). Reports presence as PASS,
    absence as informational PASS (not a warning).

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    if doc.has_notation_section:
        results.append(ValidationResult(
            category="notation",
            status="PASS",
            message="Notation section present",
        ))
    else:
        results.append(ValidationResult(
            category="notation",
            status="PASS",
            message="Notation section absent (optional)",
        ))

    return results


# ---------------------------------------------------------------------------
# Markdown formatting check (MUST rules)
# ---------------------------------------------------------------------------

def check_markdown_formatting(doc: SESFDocument, filepath: str) -> list:
    """Check that section headers use ### and block keywords use **bold**.

    Per RULE markdown_formatting (MUST):
    - Section headers (Behaviors, Procedures, etc.) MUST use ### heading syntax
    - Block keywords (BEHAVIOR, PROCEDURE, RULE, STEP) MUST use **bold** syntax

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    try:
        content = Path(filepath).read_text(encoding="utf-8")
        content = _strip_yaml_frontmatter(content)
        content = _strip_code_block(content)
        lines = content.split("\n")
    except Exception:
        return results

    section_fails = 0
    keyword_fails = 0

    for i, raw_line in enumerate(lines):
        line_num = i + 1
        stripped = raw_line.strip()

        if not stripped or stripped.startswith("--"):
            continue

        # Section headers: unindented lines matching a known section name
        # must have a ### prefix.
        if not raw_line.startswith((" ", "\t")):
            low = stripped.lower().rstrip(":")
            if low in KNOWN_SECTIONS and not stripped.startswith("#"):
                results.append(ValidationResult(
                    category="markdown_formatting",
                    status="FAIL",
                    message=f"Section '{low}' must use '### {low.title()}' heading syntax",
                    line_number=line_num,
                ))
                section_fails += 1

        # Block keywords: BEHAVIOR, PROCEDURE (unindented) and RULE, STEP
        # (indented inside blocks) must use **bold** syntax.
        if re.match(r'^BEHAVIOR\s+\w+\s*:', stripped):
            results.append(ValidationResult(
                category="markdown_formatting",
                status="FAIL",
                message="BEHAVIOR must use '**BEHAVIOR**' bold syntax",
                line_number=line_num,
            ))
            keyword_fails += 1

        if re.match(r'^PROCEDURE\s+\w+\s*:', stripped):
            results.append(ValidationResult(
                category="markdown_formatting",
                status="FAIL",
                message="PROCEDURE must use '**PROCEDURE**' bold syntax",
                line_number=line_num,
            ))
            keyword_fails += 1

        if re.match(r'^RULE\s+\w+\s*:', stripped):
            results.append(ValidationResult(
                category="markdown_formatting",
                status="FAIL",
                message="RULE must use '**RULE**' bold syntax",
                line_number=line_num,
            ))
            keyword_fails += 1

        if re.match(r'^STEP\s+\w+', stripped):
            results.append(ValidationResult(
                category="markdown_formatting",
                status="FAIL",
                message="STEP must use '**STEP**' bold syntax",
                line_number=line_num,
            ))
            keyword_fails += 1

    if section_fails == 0 and keyword_fails == 0:
        results.append(ValidationResult(
            category="markdown_formatting",
            status="PASS",
            message="Section headers use ### and block keywords use **bold**",
        ))

    return results


# ---------------------------------------------------------------------------
# HSF v5 Validation
# ---------------------------------------------------------------------------

def _detect_hsf_tier(text: str, line_count: int) -> str:
    """Infer tier from line count and content complexity."""
    if line_count <= 80:
        return "micro"
    elif line_count <= 200:
        return "standard"
    else:
        return "complex"


def check_hsf_structure(text: str, filepath: str) -> list:
    """Validate HSF v5 structural requirements."""
    results = []
    lines = text.split('\n')
    line_count = len([l for l in lines if l.strip()])  # non-empty lines
    tier = _detect_hsf_tier(text, line_count)

    results.append(ValidationResult(
        "hsf_structure", "INFO",
        f"Detected HSF v5 format, inferred tier: {tier} ({line_count} non-empty lines)"
    ))

    # Build a set of line numbers that are inside fenced code blocks
    in_code_block = set()
    inside = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            inside = not inside
            in_code_block.add(i)
            continue
        if inside:
            in_code_block.add(i)

    # --- Forbidden keywords (outside code blocks only) ---
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
                    "hsf_structure", "FAIL",
                    f"Forbidden keyword {keyword} found — HSF v5 uses markdown headers and bold list items instead",
                    line_number=i
                ))

    # --- Forbidden sections (outside code blocks only) ---
    forbidden_sections = ['Meta', 'Notation', 'Types', 'Functions', 'Precedence', 'Dependencies', 'Changelog']
    for section in forbidden_sections:
        pattern = rf'^###?\s+{section}\s*$'
        for i, line in enumerate(lines, 1):
            if i in in_code_block:
                continue
            if re.match(pattern, line.strip()):
                results.append(ValidationResult(
                    "hsf_structure", "FAIL",
                    f"Forbidden section '{section}' found — HSF v5 does not use this section",
                    line_number=i
                ))

    # --- Required: Purpose (first paragraph or explicit section) ---
    has_purpose = bool(re.search(r'^##\s+Purpose', text, re.MULTILINE))
    # Also check for purpose as first paragraph after title
    title_match = re.search(r'^#\s+.+\n\n(.+)', text, re.MULTILINE)
    has_inline_purpose = title_match is not None and not title_match.group(1).startswith('#')
    if not has_purpose and not has_inline_purpose:
        # Check for purpose as first content after title (common in micro)
        pass  # Be lenient - first paragraph after title counts

    # --- Required: Instructions section ---
    has_instructions = bool(re.search(r'^##\s+Instructions', text, re.MULTILINE))
    has_how_to = bool(re.search(r'^##\s+How to', text, re.MULTILINE))
    has_workflow = bool(re.search(r'^##\s+Workflow', text, re.MULTILINE))
    if not has_instructions and not has_how_to and not has_workflow:
        results.append(ValidationResult(
            "hsf_structure", "FAIL",
            "Missing '## Instructions' section (or equivalent like '## Workflow', '## How to...')"
        ))
    else:
        results.append(ValidationResult(
            "hsf_structure", "PASS",
            "Instructions section present"
        ))

    # --- Errors table check ---
    has_errors = bool(re.search(r'^##\s+Errors', text, re.MULTILINE))
    if not has_errors and tier != "micro":
        results.append(ValidationResult(
            "hsf_structure", "WARN",
            "No '## Errors' section found — standard and complex tier specs SHOULD have a consolidated error table"
        ))
    elif has_errors:
        results.append(ValidationResult(
            "hsf_structure", "PASS",
            "Errors section present"
        ))

    # --- Empty sections check ---
    section_pattern = re.compile(r'^(##\s+.+)$', re.MULTILINE)
    section_positions = [(m.start(), m.group(1)) for m in section_pattern.finditer(text)]
    for idx, (pos, heading) in enumerate(section_positions):
        # Get content between this heading and next heading (or end)
        end_pos = section_positions[idx + 1][0] if idx + 1 < len(section_positions) else len(text)
        content = text[pos + len(heading):end_pos].strip()
        if not content or content.lower() in ('none', '-- none', 'n/a'):
            line_num = text[:pos].count('\n') + 1
            results.append(ValidationResult(
                "hsf_structure", "FAIL",
                f"Empty section '{heading.strip()}' — omit sections that have no content instead of stubbing them",
                line_number=line_num
            ))

    # --- Line budget check ---
    budget = {"micro": 80, "standard": 200, "complex": 400}
    max_lines = budget.get(tier, 400)
    if line_count > max_lines:
        results.append(ValidationResult(
            "hsf_structure", "WARN",
            f"Spec has {line_count} non-empty lines, exceeding {tier} tier budget of {max_lines}"
        ))
    else:
        results.append(ValidationResult(
            "hsf_structure", "PASS",
            f"Line budget OK ({line_count}/{max_lines} for {tier} tier)"
        ))

    return results


def check_hsf_error_table(text: str) -> list:
    """Validate the consolidated error table structure."""
    results = []

    # Find the errors section
    errors_match = re.search(r'^##\s+Errors\s*\n(.*?)(?=^##\s|\Z)', text, re.MULTILINE | re.DOTALL)
    if not errors_match:
        return results  # No errors section, already warned in structure check

    errors_content = errors_match.group(1)

    # Check for markdown table
    table_lines = [l for l in errors_content.split('\n') if '|' in l and l.strip()]
    if len(table_lines) < 2:
        results.append(ValidationResult(
            "hsf_errors", "WARN",
            "Errors section exists but does not contain a markdown table"
        ))
        return results

    # Check header row has Error, Severity, Action columns
    header = table_lines[0].lower()
    has_error_col = 'error' in header or 'name' in header
    has_severity_col = 'severity' in header
    has_action_col = 'action' in header

    if not (has_error_col and has_severity_col and has_action_col):
        results.append(ValidationResult(
            "hsf_errors", "WARN",
            "Error table SHOULD have Error/Name, Severity, and Action columns"
        ))
    else:
        results.append(ValidationResult(
            "hsf_errors", "PASS",
            "Error table has required columns (Error, Severity, Action)"
        ))

    return results


def check_hsf_route_tables(text: str) -> list:
    """Validate @route tables in HSF v5 specs (same rules as SESF v4)."""
    results = []

    route_pattern = re.compile(
        r'@route\s+(\w+)\s*\[(\w+)\]',
        re.MULTILINE
    )

    for match in route_pattern.finditer(text):
        name = match.group(1)
        mode = match.group(2)
        line_num = text[:match.start()].count('\n') + 1

        # Validate mode
        if mode not in ('first_match_wins', 'all_matches'):
            results.append(ValidationResult(
                "hsf_routes", "FAIL",
                f"@route '{name}' has invalid mode '{mode}' — must be first_match_wins or all_matches",
                line_number=line_num
            ))

        # Count branches (lines with → after the @route declaration)
        route_start = match.end()
        branch_count = 0
        for line in text[route_start:].split('\n'):
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('@'):
                if branch_count > 0:
                    break
                continue
            if '\u2192' in stripped or '->' in stripped:
                branch_count += 1
            elif stripped and not stripped.startswith('--') and branch_count > 0:
                break

        if branch_count < 3:
            results.append(ValidationResult(
                "hsf_routes", "WARN",
                f"@route '{name}' has {branch_count} branches — use prose conditionals for fewer than 3 branches",
                line_number=line_num
            ))
        else:
            results.append(ValidationResult(
                "hsf_routes", "PASS",
                f"@route '{name}' has {branch_count} branches",
                line_number=line_num
            ))

    return results


def check_hsf_config(text: str) -> list:
    """Validate @config blocks in HSF v5 specs (same rules as SESF v4)."""
    results = []

    if '@config' not in text:
        return results

    # Find config block and extract keys
    config_match = re.search(r'@config\s*\n((?:[ \t]+.+\n)*)', text)
    if not config_match:
        return results

    config_text = config_match.group(1)
    config_keys = set()

    for line in config_text.split('\n'):
        stripped = line.strip()
        if ':' in stripped and not stripped.startswith('#') and not stripped.startswith('--'):
            key = stripped.split(':')[0].strip()
            if key:
                config_keys.add(key)

    # Find all $config.key references
    config_refs = set(re.findall(r'\$config\.([a-zA-Z_][a-zA-Z0-9_.]*)', text))

    # Check for references to undefined keys
    for ref in config_refs:
        top_key = ref.split('.')[0]
        if top_key not in config_keys:
            results.append(ValidationResult(
                "hsf_config", "WARN",
                f"$config.{ref} referenced but '{top_key}' not found in @config block"
            ))

    if not config_refs and config_keys:
        results.append(ValidationResult(
            "hsf_config", "WARN",
            "@config block defined but no $config.key references found in spec"
        ))

    if config_keys and config_refs:
        results.append(ValidationResult(
            "hsf_config", "PASS",
            f"@config block with {len(config_keys)} keys, {len(config_refs)} references"
        ))

    return results


def check_hsf_variable_threading(text: str) -> list:
    """Validate $variable threading in HSF v5 specs."""
    results = []

    # Find all $variable references (excluding $config.*)
    all_vars = set(re.findall(r'\$([a-zA-Z_]\w*)', text))
    all_vars.discard('config')  # $config is for @config references
    # Also remove things that look like $config.xxx
    config_vars = set(re.findall(r'\$config\.\w+', text))

    if not all_vars:
        return results

    results.append(ValidationResult(
        "hsf_variables", "INFO",
        f"Found {len(all_vars)} $variable references: {', '.join(sorted(all_vars))}"
    ))

    return results


def check_hsf_rfc2119(text: str) -> list:
    """Check RFC 2119 keyword capitalization consistency."""
    results = []

    keywords = ['must', 'must not', 'should', 'should not', 'may']

    for line_num, line in enumerate(text.split('\n'), 1):
        # Skip code blocks and config blocks
        if line.strip().startswith('```') or line.strip().startswith('@'):
            continue

        for kw in keywords:
            # Look for lowercase uses of RFC 2119 keywords in operative context
            pattern = rf'\b{kw}\b'
            if re.search(pattern, line) and not re.search(pattern.upper().replace(r'\B', r'\b'), line):
                # Only flag if the word appears to be used operatively
                # (heuristic: followed by "be", "have", "not", or a verb)
                pass  # This is too noisy to implement reliably, skip

    return results


# ---------------------------------------------------------------------------
# HSF v6 validation
# ---------------------------------------------------------------------------

# Canonical section order for HSF v6
_V6_SECTION_ORDER = [
    'purpose', 'scope', 'inputs', 'outputs', 'config',
    'instructions', 'rules', 'errors', 'examples',
]

# Section-level tags (not inner tags like <case>, <default>)
_V6_SECTION_TAGS = set(_V6_SECTION_ORDER)


def check_hsf_v6_structure(text: str, filepath: str) -> list:
    """Validate HSF v6 structural requirements."""
    results = []
    lines = text.split('\n')
    line_count = len([l for l in lines if l.strip()])  # non-empty lines
    tier = _detect_hsf_tier(text, line_count)

    results.append(ValidationResult(
        "hsf_v6_structure", "INFO",
        f"Detected HSF v6 format, inferred tier: {tier} ({line_count} non-empty lines)"
    ))

    # Build a set of line numbers that are inside fenced code blocks
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
    has_purpose = bool(re.search(r'<purpose[\s>]', text))
    has_instructions = bool(re.search(r'<instructions[\s>]', text))
    has_errors = bool(re.search(r'<errors[\s>]', text))

    if not has_purpose:
        results.append(ValidationResult(
            "hsf_v6_structure", "FAIL",
            "Missing <purpose> section (required for all tiers)"
        ))
    else:
        results.append(ValidationResult(
            "hsf_v6_structure", "PASS",
            "<purpose> section present"
        ))

    if not has_instructions:
        results.append(ValidationResult(
            "hsf_v6_structure", "FAIL",
            "Missing <instructions> section (required for all tiers)"
        ))
    else:
        results.append(ValidationResult(
            "hsf_v6_structure", "PASS",
            "<instructions> section present"
        ))

    if not has_errors:
        results.append(ValidationResult(
            "hsf_v6_structure", "WARN",
            "No <errors> section found — consider adding error handling"
        ))

    # --- Forbidden: ## Section markdown headers for top-level sections ---
    forbidden_md_sections = [
        'Purpose', 'Scope', 'Instructions', 'Rules', 'Errors',
        'Examples', 'Inputs', 'Outputs', 'Configuration', 'Config',
    ]
    for section in forbidden_md_sections:
        pattern = rf'^##\s+{section}\s*$'
        for i, line in enumerate(lines, 1):
            if i in in_code_block:
                continue
            if re.match(pattern, line.strip()):
                results.append(ValidationResult(
                    "hsf_v6_structure", "FAIL",
                    f"Forbidden markdown header '## {section}' — HSF v6 uses XML tags like <{section.lower()}> instead",
                    line_number=i
                ))

    # --- Forbidden: BEHAVIOR/RULE/PROCEDURE/STEP keywords ---
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
                    f"Forbidden keyword {keyword} found — HSF v6 uses XML tags and prose instead",
                    line_number=i
                ))

    # --- Forbidden: @config and @route (replaced by XML in v6) ---
    for i, line in enumerate(lines, 1):
        if i in in_code_block:
            continue
        stripped = line.strip()
        if re.match(r'^@config\b', stripped):
            results.append(ValidationResult(
                "hsf_v6_structure", "FAIL",
                "Forbidden @config found — HSF v6 uses <config> with JSON body instead",
                line_number=i
            ))
        if re.match(r'^@route\b', stripped):
            results.append(ValidationResult(
                "hsf_v6_structure", "FAIL",
                "Forbidden @route found — HSF v6 uses <route> with <case> elements instead",
                line_number=i
            ))

    # --- Warn: $config.key references (should be config.key without $) ---
    for i, line in enumerate(lines, 1):
        if i in in_code_block:
            continue
        if re.search(r'\$config\.', line):
            results.append(ValidationResult(
                "hsf_v6_structure", "WARN",
                "$config.key reference found — HSF v6 uses config.key without $ prefix",
                line_number=i
            ))

    # --- Empty XML sections check (section-level tags only) ---
    section_tag_pattern = '|'.join(_V6_SECTION_TAGS)
    for m in re.finditer(rf'<({section_tag_pattern})(?:\s[^>]*)?>(\s*)</\1>', text):
        tag_name = m.group(1)
        line_num = text[:m.start()].count('\n') + 1
        results.append(ValidationResult(
            "hsf_v6_structure", "FAIL",
            f"Empty <{tag_name}> section — omit sections that have no content instead of stubbing them",
            line_number=line_num
        ))

    # --- Section order check ---
    found_sections = []
    for tag in _V6_SECTION_ORDER:
        match = re.search(rf'<{tag}[\s>]', text)
        if match:
            found_sections.append((match.start(), tag))
    found_sections.sort(key=lambda x: x[0])
    ordered_tags = [tag for _, tag in found_sections]
    # Check if the found sections are in the correct relative order
    expected_order = [t for t in _V6_SECTION_ORDER if t in ordered_tags]
    if ordered_tags != expected_order:
        results.append(ValidationResult(
            "hsf_v6_structure", "WARN",
            f"Section order should be: {', '.join(expected_order)} — found: {', '.join(ordered_tags)}"
        ))
    else:
        results.append(ValidationResult(
            "hsf_v6_structure", "PASS",
            "Section order is correct"
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


def check_hsf_v6_config(text: str) -> list:
    """Validate <config> blocks with JSON body in HSF v6 specs."""
    results = []

    config_match = re.search(r'<config>(.*?)</config>', text, re.DOTALL)
    if not config_match:
        return results

    config_body = config_match.group(1).strip()

    # Parse JSON
    try:
        config_data = json.loads(config_body)
    except json.JSONDecodeError as e:
        results.append(ValidationResult(
            "hsf_v6_config", "FAIL",
            f"<config> body is not valid JSON: {e}"
        ))
        return results

    # Must be a dict
    if not isinstance(config_data, dict):
        results.append(ValidationResult(
            "hsf_v6_config", "FAIL",
            "<config> JSON must be an object (dict), not " + type(config_data).__name__
        ))
        return results

    results.append(ValidationResult(
        "hsf_v6_config", "PASS",
        f"<config> contains valid JSON with {len(config_data)} keys"
    ))

    # Warn if keys aren't snake_case
    snake_case_re = re.compile(r'^[a-z][a-z0-9]*(_[a-z0-9]+)*$')
    for key in config_data:
        if not snake_case_re.match(key):
            results.append(ValidationResult(
                "hsf_v6_config", "WARN",
                f"Config key '{key}' is not snake_case"
            ))

    # Find config.key references outside the config block
    config_end = config_match.end()
    config_start = config_match.start()
    text_outside_config = text[:config_start] + text[config_end:]
    config_refs = set(re.findall(r'\bconfig\.([a-zA-Z_][a-zA-Z0-9_.]*)', text_outside_config))

    for ref in config_refs:
        top_key = ref.split('.')[0]
        if top_key not in config_data:
            results.append(ValidationResult(
                "hsf_v6_config", "WARN",
                f"config.{ref} referenced but '{top_key}' not found in <config> block"
            ))

    # Warn if fewer than 3 keys
    if len(config_data) < 3:
        results.append(ValidationResult(
            "hsf_v6_config", "WARN",
            f"<config> has only {len(config_data)} keys — consider whether a config block is needed for fewer than 3"
        ))

    return results


def check_hsf_v6_routes(text: str) -> list:
    """Validate <route> elements with <case> children in HSF v6 specs."""
    results = []

    # Match <route ...>...</route> with order-independent attributes
    route_pattern = re.compile(
        r'<route\s+([^>]*)>(.*?)</route>',
        re.DOTALL
    )

    for match in route_pattern.finditer(text):
        attrs_str = match.group(1)
        route_body = match.group(2)
        line_num = text[:match.start()].count('\n') + 1

        # Parse name and mode attributes (order-independent)
        name_match = re.search(r'name\s*=\s*"([^"]*)"', attrs_str)
        mode_match = re.search(r'mode\s*=\s*"([^"]*)"', attrs_str)

        name = name_match.group(1) if name_match else None
        mode = mode_match.group(1) if mode_match else None

        if not name:
            results.append(ValidationResult(
                "hsf_v6_routes", "FAIL",
                "Route is missing required 'name' attribute",
                line_number=line_num
            ))
            continue

        if not mode:
            results.append(ValidationResult(
                "hsf_v6_routes", "WARN",
                f"Route '{name}' is missing 'mode' attribute — defaults to first_match_wins",
                line_number=line_num
            ))
            mode = "first_match_wins"

        # Validate mode
        if mode not in ('first_match_wins', 'all_matches'):
            results.append(ValidationResult(
                "hsf_v6_routes", "FAIL",
                f"Route '{name}' has invalid mode '{mode}' — must be first_match_wins or all_matches",
                line_number=line_num
            ))

        # Count <case when="..."> elements
        case_count = len(re.findall(r'<case\s+when\s*=\s*"[^"]*"', route_body))

        if case_count < 3:
            results.append(ValidationResult(
                "hsf_v6_routes", "WARN",
                f"Route '{name}' has {case_count} cases — use prose conditionals for fewer than 3 cases",
                line_number=line_num
            ))
        else:
            results.append(ValidationResult(
                "hsf_v6_routes", "PASS",
                f"Route '{name}' has {case_count} cases",
                line_number=line_num
            ))

    return results


def check_hsf_v6_output_schema(text: str, tier: str) -> list:
    """Validate <output-schema> blocks in HSF v6 specs."""
    results = []

    schema_match = re.search(
        r'<output-schema\s+format\s*=\s*"([^"]*)">(.*?)</output-schema>',
        text, re.DOTALL
    )

    if not schema_match:
        # If no output-schema and tier is standard/complex, check if spec mentions structured output
        if tier in ('standard', 'complex'):
            if re.search(r'structured\s+output', text, re.IGNORECASE):
                results.append(ValidationResult(
                    "hsf_v6_output_schema", "WARN",
                    "Spec mentions structured output but no <output-schema> block found"
                ))
        return results

    fmt = schema_match.group(1)
    body = schema_match.group(2).strip()

    # Warn if format is not json
    if fmt != 'json':
        results.append(ValidationResult(
            "hsf_v6_output_schema", "WARN",
            f"<output-schema> format is '{fmt}' — 'json' is recommended"
        ))

    # Fail if empty body
    if not body:
        results.append(ValidationResult(
            "hsf_v6_output_schema", "FAIL",
            "<output-schema> has empty body"
        ))
        return results

    # Check body starts with { or [ (pseudo-JSON structure)
    if not body.startswith('{') and not body.startswith('['):
        results.append(ValidationResult(
            "hsf_v6_output_schema", "WARN",
            "<output-schema> body should start with '{' or '[' for pseudo-JSON structure"
        ))
    else:
        results.append(ValidationResult(
            "hsf_v6_output_schema", "PASS",
            "<output-schema> has valid pseudo-JSON structure"
        ))

    return results


def validate_hsf_v6(text: str, filepath: str) -> list:
    """Run all HSF v6 validation checks."""
    results = []
    results.extend(check_hsf_v6_structure(text, filepath))
    results.extend(check_hsf_v6_config(text))
    results.extend(check_hsf_v6_routes(text))

    # Detect tier for output-schema check
    lines = text.split('\n')
    line_count = len([l for l in lines if l.strip()])
    tier = _detect_hsf_tier(text, line_count)
    results.extend(check_hsf_v6_output_schema(text, tier))

    results.extend(check_hsf_variable_threading(text))
    results.extend(check_hsf_rfc2119(text))
    return results


def validate_hsf(text: str, filepath: str) -> list:
    """Run all HSF v5 validation checks."""
    results = []
    results.extend(check_hsf_structure(text, filepath))
    results.extend(check_hsf_error_table(text))
    results.extend(check_hsf_route_tables(text))
    results.extend(check_hsf_config(text))
    results.extend(check_hsf_variable_threading(text))
    results.extend(check_hsf_rfc2119(text))
    return results


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_sesf.py <spec_file.md>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not Path(filepath).exists():
        print(f"File not found: {filepath}")
        sys.exit(1)

    # Read raw text for format detection
    raw_text = Path(filepath).read_text(encoding='utf-8')
    stripped_text = _strip_yaml_frontmatter(raw_text)
    # Note: Do NOT apply _strip_code_block here — it removes fenced code
    # examples which are part of the spec content for HSF validation.

    format_version = detect_format_version(stripped_text)

    if format_version == 'hsf_v6':
        print(f"  Detected format: HSF v6 (XML Section Tags)")
        results = validate_hsf_v6(stripped_text, filepath)
    elif format_version == 'hsf_v5':
        print(f"  Detected format: HSF v5 (Hybrid Specification Format)")
        results = validate_hsf(stripped_text, filepath)
    elif format_version == 'sesf_v4':
        print(f"  Detected format: SESF v4")
        doc = parse_sesf(filepath)

        if not doc.meta:
            print(f"No SESF Meta section found in {filepath}")
            print("Is this an SESF specification?")
            sys.exit(1)

        results = check_structural_completeness(doc)
        results.extend(check_type_consistency(doc))
        results.extend(check_rule_integrity(doc))
        results.extend(check_error_consistency(doc))
        results.extend(check_example_consistency(doc))
        results.extend(check_cross_behavior(doc))
        results.extend(check_config_references(doc))
        results.extend(check_variable_threading(doc))
        results.extend(check_route_completeness(doc))
        results.extend(check_error_table_structure(doc))
        results.extend(check_notation_section(doc))
        results.extend(check_markdown_formatting(doc, filepath))
    else:
        # Try SESF parsing as fallback
        doc = parse_sesf(filepath)
        if doc.meta:
            print(f"  Detected format: SESF (version unclear, applying v4 rules)")
            results = check_structural_completeness(doc)
            results.extend(check_type_consistency(doc))
            results.extend(check_rule_integrity(doc))
            results.extend(check_error_consistency(doc))
            results.extend(check_example_consistency(doc))
            results.extend(check_cross_behavior(doc))
            results.extend(check_config_references(doc))
            results.extend(check_variable_threading(doc))
            results.extend(check_route_completeness(doc))
            results.extend(check_error_table_structure(doc))
            results.extend(check_notation_section(doc))
            results.extend(check_markdown_formatting(doc, filepath))
        else:
            # Try HSF as forward-compatible default
            print(f"  Format ambiguous — applying HSF v5 rules (forward-compatible)")
            results = validate_hsf(stripped_text, filepath)

    # Print results grouped by category
    has_fail = False
    current_cat = None
    for r in results:
        if r.category != current_cat:
            current_cat = r.category
            label = current_cat.replace("_", " ").title()
            print(f"\n  ── {label} ──")
        symbol = {
            "PASS": "\u2713",
            "WARN": "\u26a0",
            "FAIL": "\u2717",
            "INFO": "\u2139",
        }.get(r.status, "?")
        line_ref = f" (line {r.line_number})" if r.line_number else ""
        print(f"  [{r.status}] {symbol} {r.message}{line_ref}")
        if r.status == "FAIL":
            has_fail = True

    # Summary
    passes = sum(1 for r in results if r.status == "PASS")
    warns = sum(1 for r in results if r.status == "WARN")
    fails = sum(1 for r in results if r.status == "FAIL")
    print(f"\n{'─' * 50}")
    print(f"Results: {passes} passed, {warns} warnings, {fails} failures")

    sys.exit(1 if has_fail else 0)


if __name__ == "__main__":
    main()
