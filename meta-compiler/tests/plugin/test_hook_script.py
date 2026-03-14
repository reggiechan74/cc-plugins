"""Integration tests for the validate-model-md.sh hook script."""

import json
import subprocess
from pathlib import Path
import tempfile

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate-model-md.sh"
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
    """Hook should only process .model.md files."""

    def test_ignores_regular_md_files(self):
        result = run_hook("Write", "/tmp/notes.md")
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_ignores_python_files(self):
        result = run_hook("Write", "/tmp/code.py")
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_ignores_non_write_tools(self):
        result = run_hook("Read", "/tmp/model.model.md")
        assert result.returncode == 0
        assert result.stdout.strip() == ""


class TestHookValidation:
    """Hook should validate .model.md files and return structured feedback."""

    def test_valid_document_passes(self, tmp_path):
        doc = tmp_path / "valid.model.md"
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
        doc = tmp_path / "invalid.model.md"
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
        doc = tmp_path / "uncovered.model.md"
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


class TestHookEdgeCases:
    """Edge cases for the hook script."""

    def test_handles_edit_tool(self, tmp_path):
        """Hook should trigger on Edit tool, not just Write."""
        doc = tmp_path / "test.model.md"
        doc.write_text(
            '```python:validate\n'
            'Parameter("x", index=["MISSING"], domain="real",\n'
            '          units="hours", description="Bad param")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Edit", str(doc))
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["decision"] == "block", "Edit tool should trigger validation, not be ignored"

    def test_nonexistent_file_exits_cleanly(self):
        """Hook should exit 0 when the .model.md file doesn't exist."""
        result = run_hook("Write", "/tmp/nonexistent.model.md")
        assert result.returncode == 0

    def test_empty_document(self, tmp_path):
        """Hook should handle an empty .model.md file gracefully."""
        doc = tmp_path / "empty.model.md"
        doc.write_text("")
        result = run_hook("Write", str(doc))
        assert result.returncode == 0

    def test_document_with_only_prose(self, tmp_path):
        """Hook should pass on a document with prose but no validation blocks."""
        doc = tmp_path / "prose.model.md"
        doc.write_text("# Title\n\nSome prose about math.\n")
        result = run_hook("Write", str(doc))
        assert result.returncode == 0

    def test_valid_json_output_on_block(self, tmp_path):
        """Block response must be valid JSON."""
        doc = tmp_path / "bad.model.md"
        doc.write_text(
            '```python:validate\n'
            'Parameter("x", index=["NONEXISTENT"], domain="real",\n'
            '          units="hours", description="Bad param")\n'
            'registry.run_tests()\n'
            '```\n'
        )
        result = run_hook("Write", str(doc))
        assert result.returncode == 0
        output = json.loads(result.stdout)  # Must be valid JSON
        assert output["decision"] == "block"
