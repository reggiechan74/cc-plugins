#!/usr/bin/env python3
"""SESF v2 Structural Validator

Parses SESF v2 specification files (markdown) and validates them for
structural correctness. Checks section completeness based on the declared
tier (micro, standard, complex) and validates behavior block structure.

Usage:
    python3 validate_sesf.py <spec_file.md>

Exit codes:
    0 - All checks passed (may include warnings)
    1 - One or more checks failed, or file is not a valid SESF spec
"""

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
    precedence: list = field(default_factory=list)  # ordered list of rule names


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
    "audience",
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
    """Parse an SESF v2 specification file and return an SESFDocument."""
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
    in_type_block = False
    current_type: Optional[SESFType] = None
    meta_started = False

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
        nonlocal current_behavior
        _finish_sub_block()
        if current_behavior:
            doc.behaviors.append(current_behavior)
            current_behavior = None

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

        # --- Skip empty lines (but don't change section) ---
        if not stripped:
            # Append to current section content if we have one
            if current_section and current_section in doc.sections:
                doc.sections[current_section].append("")
            continue

        # --- Spec separator: stop at first `---` after we've started parsing ---
        if stripped == "---" and (doc.title or doc.meta):
            _finish_behavior()
            _finish_type()
            break

        # --- Title detection: `# Title` (only if not yet found) ---
        if not doc.title and stripped.startswith("#"):
            # Could be `# Title` or just `Title` at the top
            title = stripped.lstrip("#").strip()
            if title:
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
        low_stripped = stripped.lower()
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
            # Close any open behavior / type before switching sections
            _finish_behavior()
            _finish_type()

            current_section = section_match
            if current_section not in doc.sections:
                doc.sections[current_section] = []

            # Handle Meta section
            if section_match == "meta":
                meta_started = True
                # Check if rest of line has pipe-delimited meta
                rest = stripped[len(section_match):].strip().lstrip(":").strip()
                if "|" in rest:
                    doc.meta.update(_parse_meta_pipe(rest))
            continue

        # --- BEHAVIOR detection (must come before section-specific handlers
        #     so that BEHAVIOR lines are not consumed by e.g. Functions) ---
        behavior_match = re.match(r"^\s*BEHAVIOR\s+(\w+)\s*:", stripped)
        if behavior_match:
            _finish_behavior()
            _finish_type()
            current_section = "behaviors"
            if "behaviors" not in doc.sections:
                doc.sections["behaviors"] = []
            current_behavior = SESFBehavior(
                name=behavior_match.group(1), line_number=line_num
            )
            doc.sections["behaviors"].append(stripped)
            continue

        # --- PRECEDENCE detection (can appear after behaviors, at top level) ---
        prec_header_match = re.match(r"^PRECEDENCE\s*:", stripped)
        if prec_header_match and not raw_line.startswith((" ", "\t")):
            _finish_behavior()
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

        # --- Inside Functions section: capture FUNCTION declarations ---
        if current_section == "functions":
            doc.sections["functions"].append(stripped)
            func_match = re.match(r"^FUNCTION\s+(\w+)\s*\(", stripped)
            if func_match:
                doc.functions.append(func_match.group(1))
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

            # RULE detection
            rule_match = re.match(r"^\s*RULE\s+(\w+)\s*:", stripped)
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

            # ERROR detection
            error_match = re.match(r"^\s*ERROR\s+(\w+)\s*:", stripped)
            if error_match:
                _finish_sub_block()
                current_error = SESFError(
                    name=error_match.group(1), line_number=line_num
                )
                continue

            # EXAMPLE detection
            example_match = re.match(r"^\s*EXAMPLE\s+(\w+)\s*:", stripped)
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
            prec_match_inline = re.match(r"^PRECEDENCE\s*:", stripped)
            if prec_match_inline and not raw_line.startswith((" ", "\t")):
                _finish_behavior()
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
    # Behaviors can also be detected via doc.behaviors even if the section
    # keyword "Behaviors" wasn't explicitly used (specs may jump straight to
    # BEHAVIOR blocks).
    if doc.behaviors:
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

    # 3. Meta field completeness
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
                status="WARN",
                message=f"Meta field '{mf}' missing or empty",
            ))

    # 4. At least one BEHAVIOR block
    if doc.behaviors:
        results.append(ValidationResult(
            category="behaviors",
            status="PASS",
            message=f"Found {len(doc.behaviors)} BEHAVIOR block(s)",
        ))
    else:
        results.append(ValidationResult(
            category="behaviors",
            status="FAIL",
            message="No BEHAVIOR blocks found",
        ))

    # 5. Each behavior has at least one RULE
    for beh in doc.behaviors:
        if beh.rules:
            results.append(ValidationResult(
                category="behaviors",
                status="PASS",
                message=f"BEHAVIOR '{beh.name}' has {len(beh.rules)} rule(s)",
                line_number=beh.line_number,
            ))
        else:
            results.append(ValidationResult(
                category="behaviors",
                status="WARN",
                message=f"BEHAVIOR '{beh.name}' has no rules",
                line_number=beh.line_number,
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
    """Collect all textual content from behaviors (rules, errors, examples)."""
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


def check_error_consistency(doc: SESFDocument) -> list:
    """Check that ERROR blocks are well-formed and consistent.

    Checks:
    - Each ERROR has a valid severity (critical, warning, info) — WARN if missing
    - Each ERROR has ACTION and MESSAGE fields — WARN if missing
    - Warn on behaviors with errors but no rules (orphaned errors)
    - PASS summary for behaviors with properly-defined errors

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    for beh in doc.behaviors:
        if not beh.errors:
            continue

        # Check for orphaned errors (errors without rules)
        if not beh.rules:
            results.append(ValidationResult(
                category="error_consistency",
                status="WARN",
                message=f"BEHAVIOR '{beh.name}' has {len(beh.errors)} error(s) "
                        f"but no rules (orphaned errors)",
                line_number=beh.line_number,
            ))

        well_defined_count = 0

        for err in beh.errors:
            issues: list[str] = []

            # Check severity
            if err.severity is None:
                issues.append("SEVERITY")
            elif err.severity.lower() not in VALID_SEVERITIES:
                results.append(ValidationResult(
                    category="error_consistency",
                    status="WARN",
                    message=f"ERROR '{err.name}' in BEHAVIOR '{beh.name}' has "
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
                    message=f"ERROR '{err.name}' in BEHAVIOR '{beh.name}' "
                            f"missing: {', '.join(issues)}",
                    line_number=err.line_number,
                ))
            else:
                well_defined_count += 1

        if well_defined_count > 0:
            results.append(ValidationResult(
                category="error_consistency",
                status="PASS",
                message=f"BEHAVIOR '{beh.name}' has {well_defined_count} "
                        f"well-defined error(s)",
                line_number=beh.line_number,
            ))

    return results


# ---------------------------------------------------------------------------
# Example consistency check
# ---------------------------------------------------------------------------

def check_example_consistency(doc: SESFDocument) -> list:
    """Check that behaviors have adequate example coverage.

    Checks:
    - Each behavior has at least one EXAMPLE — WARN if no examples
    - Warn on behaviors where the number of examples is less than the
      number of rules (heuristic: each rule should ideally have a
      demonstrating example)
    - PASS summary for behaviors with good example coverage

    Returns a list of ValidationResult objects.
    """
    results: list[ValidationResult] = []

    for beh in doc.behaviors:
        num_examples = len(beh.examples)
        num_rules = len(beh.rules)

        if num_examples == 0:
            results.append(ValidationResult(
                category="example_consistency",
                status="WARN",
                message=f"BEHAVIOR '{beh.name}' has no examples",
                line_number=beh.line_number,
            ))
            continue

        # Has at least one example — PASS
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

    # Print results grouped by category
    has_fail = False
    current_cat = None
    for r in results:
        # Print category header when it changes
        if r.category != current_cat:
            current_cat = r.category
            label = current_cat.replace("_", " ").title()
            print(f"\n  ── {label} ──")
        symbol = {
            "PASS": "\u2713",
            "WARN": "\u26a0",
            "FAIL": "\u2717",
        }[r.status]
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
