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
        profile = tmp_path / "family-profile.md"
        profile.write_text("---\nhome_address: \"123 Main St\"\n---\n")
        result = parse_profile(str(profile))
        assert result["home_address"] == "123 Main St"
        assert result["max_commute"] == 0
        assert result["api_key"] == ""
        assert result["work_addresses"] == []

    def test_api_key_from_profile(self, tmp_path):
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
        profile = tmp_path / "family-profile.md"
        profile.write_text("# Just a markdown file\nNo frontmatter here.\n")
        with pytest.raises(SystemExit):
            parse_profile(str(profile))
