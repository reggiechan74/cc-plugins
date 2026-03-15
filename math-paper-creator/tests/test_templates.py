"""Tests for template file structure and content conformance."""

import re
from pathlib import Path

import yaml
import pytest

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

EXPECTED_TEMPLATES = [
    "optimization",
    "statistical",
    "game-theoretic",
    "simulation",
    "decision-analysis",
    "financial-pricing",
    "actuarial",
    "econometric",
    "queueing",
    "graph-network",
]

VALID_SYMBOL_TYPES = {"Set", "Parameter", "Variable", "Expression", "Constraint", "Objective", "none"}


def _parse_template(path: Path):
    """Parse a template file into frontmatter dict and body string."""
    text = path.read_text()
    match = re.match(r"^---\n(.+?)\n---\n(.*)$", text, re.DOTALL)
    assert match, f"{path.name}: missing YAML frontmatter"
    frontmatter = yaml.safe_load(match.group(1))
    body = match.group(2)
    return frontmatter, body


class TestTemplateFilesExist:
    def test_checklist_exists(self):
        assert (TEMPLATES_DIR / "_checklist.md").is_file()

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_template_exists(self, name):
        assert (TEMPLATES_DIR / f"{name}.md").is_file()


class TestChecklistStructure:
    def test_has_required_section(self):
        text = (TEMPLATES_DIR / "_checklist.md").read_text()
        assert "### Required" in text

    def test_has_advisories_section(self):
        text = (TEMPLATES_DIR / "_checklist.md").read_text()
        assert "### Advisories" in text


class TestTemplateFrontmatter:
    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_has_name(self, name):
        fm, _ = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "name" in fm and isinstance(fm["name"], str)

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_has_description(self, name):
        fm, _ = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "description" in fm and isinstance(fm["description"], str)

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_has_keywords(self, name):
        fm, _ = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "keywords" in fm and isinstance(fm["keywords"], list) and len(fm["keywords"]) > 0


class TestTemplateBody:
    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_has_outline_heading(self, name):
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "## Outline" in body

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_has_title_placeholder(self, name):
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "# {title}" in body

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_has_introduction(self, name):
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "### Introduction" in body

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_introduction_not_optional(self, name):
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "### Introduction (optional)" not in body

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_has_conclusion(self, name):
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "### Conclusion" in body

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_conclusion_not_optional(self, name):
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        assert "### Conclusion (optional)" not in body

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_symbol_types_valid(self, name):
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        for match in re.finditer(r"\*\*Symbols:\*\*\s*(.+)", body):
            raw = match.group(1).strip()
            types = {t.strip() for t in raw.split(",")}
            invalid = types - VALID_SYMBOL_TYPES
            assert not invalid, f"{name}: invalid symbol types: {invalid}"

    @pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
    def test_every_section_has_symbols_line(self, name):
        """Every ### section in the outline must have a **Symbols:** line."""
        _, body = _parse_template(TEMPLATES_DIR / f"{name}.md")
        outline_start = body.find("## Outline")
        assert outline_start != -1
        outline_body = body[outline_start:]
        sections = re.findall(r"###\s+.+", outline_body)
        # Get text between each section heading
        parts = re.split(r"###\s+.+", outline_body)[1:]  # skip before first ###
        for heading, part in zip(sections, parts):
            assert "**Symbols:**" in part, f"{name}: section {heading.strip()} missing **Symbols:** line"
