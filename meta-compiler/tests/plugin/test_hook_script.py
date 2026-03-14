"""Integration tests for the validate-math-md.sh hook script."""

import json
import subprocess
from pathlib import Path
import tempfile

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate-math-md.sh"
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_hook(tool_name: str, file_path: str, content: str = "") -> subprocess.CompletedProcess:
    """Simulate a PostToolUse hook invocation."""
    hook_input = json.dumps({
        "hook_event_name": "PostToolUse",
        "tool_name": tool_name,
        "tool_input": {
            "file_path": file_path,
            "content": content,
        },
        "tool_response": {"success": True},
    })
    return subprocess.run(
        ["bash", str(SCRIPT)],
        input=hook_input,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=30,
    )


class TestHookFiltering:
    """Hook should only process .math.md files."""

    def test_ignores_regular_md_files(self):
        result = run_hook("Write", "/tmp/notes.md")
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_ignores_python_files(self):
        result = run_hook("Write", "/tmp/code.py")
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_ignores_non_write_tools(self):
        result = run_hook("Read", "/tmp/model.math.md")
        assert result.returncode == 0
        assert result.stdout.strip() == ""


class TestHookValidation:
    """Hook should validate .math.md files and return structured feedback."""

    def test_valid_document_passes(self, tmp_path):
        doc = tmp_path / "valid.math.md"
        doc.write_text(
            '# Test\n\n$$x \\in \\mathbb{R}$$\n\n'
            '```python:validate\n'
            'Set("W", description="Workers")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        if result.stdout.strip():
            output = json.loads(result.stdout)
            assert output.get("decision") != "block"

    def test_invalid_document_blocks(self, tmp_path):
        doc = tmp_path / "invalid.math.md"
        doc.write_text(
            '# Test\n\n'
            '```python:validate\n'
            'Parameter("cap", index=["W"], domain="nonneg_real",\n'
            '          units="hours", description="Capacity")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "BLOCK" in output["reason"] or "not registered" in output["reason"]

    def test_coverage_warning_reported(self, tmp_path):
        """Document has 2 math blocks but only 1 validation block — must warn."""
        doc = tmp_path / "uncovered.math.md"
        doc.write_text(
            '# Test\n\n'
            '## Section A\n\n'
            '$$x \\in \\mathbb{R}$$\n\n'
            '```python:validate\n'
            'Set("W", description="Workers")\n'
            'registry.run_tests()\n'
            '```\n\n'
            '## Section B\n\n'
            '$$y \\in \\mathbb{R}$$\n\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        assert result.stdout.strip(), "Expected coverage warning output, got nothing"
        output = json.loads(result.stdout)
        context = output.get("hookSpecificOutput", {}).get("additionalContext", "")
        assert "math block" in context.lower() or "unvalidated" in context.lower() or "coverage" in context.lower()
