"""Tests for scrape_board_calendar.py."""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from scrape_board_calendar import TableExtractor, fetch_and_extract, generate_draft


class TestTableExtractor:
    """Tests for the TableExtractor HTML parser."""

    def _parse(self, html):
        parser = TableExtractor()
        parser.feed(html)
        return parser.tables

    def test_simple_table(self):
        html = (
            "<table>"
            "<tr><th>Name</th><th>Date</th></tr>"
            "<tr><td>PA Day</td><td>Sep 5</td></tr>"
            "</table>"
        )
        tables = self._parse(html)
        assert len(tables) == 1
        assert tables[0][0] == ["Name", "Date"]
        assert tables[0][1] == ["PA Day", "Sep 5"]

    def test_multiple_tables(self):
        html = (
            "<table><tr><td>A</td></tr></table>"
            "<table><tr><td>B</td></tr></table>"
        )
        tables = self._parse(html)
        assert len(tables) == 2
        assert tables[0][0] == ["A"]
        assert tables[1][0] == ["B"]

    def test_empty_cells(self):
        html = "<table><tr><td></td><td>Value</td></tr></table>"
        tables = self._parse(html)
        assert tables[0][0] == ["", "Value"]

    def test_nested_tags_in_cell(self):
        html = "<table><tr><td><strong>Bold</strong> text</td></tr></table>"
        tables = self._parse(html)
        assert "Bold" in tables[0][0][0]
        assert "text" in tables[0][0][0]

    def test_no_tables_returns_empty(self):
        html = "<html><body><p>No tables here</p></body></html>"
        tables = self._parse(html)
        assert tables == []

    def test_unclosed_tags_handled(self):
        # HTMLParser is lenient; test it doesn't crash
        html = "<table><tr><td>Unclosed"
        try:
            tables = self._parse(html)
            # May or may not produce a table depending on parser behavior
        except Exception as e:
            pytest.fail(f"Parser raised unexpectedly: {e}")

    def test_th_and_td_mixed(self):
        html = (
            "<table>"
            "<tr><th>Header 1</th><th>Header 2</th></tr>"
            "<tr><td>Cell 1</td><td>Cell 2</td></tr>"
            "</table>"
        )
        tables = self._parse(html)
        assert len(tables) == 1
        assert tables[0][0] == ["Header 1", "Header 2"]
        assert tables[0][1] == ["Cell 1", "Cell 2"]


class TestGenerateDraft:
    """Tests for generate_draft()."""

    def test_output_structure_headers(self):
        draft = generate_draft("Test Board", "TB", "2025-2026", [], "<html></html>")
        assert "# Test Board (TB)" in draft
        assert "## 2025-2026 School Year" in draft
        assert "TODO" in draft

    def test_todo_placeholders_present(self):
        draft = generate_draft("Any Board", "AB", "2024-2025", [], "")
        assert "[TODO]" in draft
        assert "### Key Dates" in draft
        assert "### PA Days - Elementary" in draft
        assert "### Holidays & Breaks" in draft
        assert "### Summer Window" in draft

    def test_empty_tables_no_table_content(self):
        draft = generate_draft("Board", "BD", "2025-2026", [], "")
        # No table rows should appear if tables is empty
        assert "#### Table" not in draft

    def test_multiple_tables_rendered(self):
        tables = [
            [["Month", "Event"], ["September", "First day"]],
            [["Date", "Holiday"], ["Dec 25", "Christmas"]],
        ]
        draft = generate_draft("Board", "BD", "2025-2026", tables, "")
        assert "#### Table 1" in draft
        assert "#### Table 2" in draft
        assert "September" in draft
        assert "Dec 25" in draft

    def test_board_name_and_abbreviation_in_output(self):
        draft = generate_draft("York Region DSB", "YRDSB", "2025-2026", [], "")
        assert "York Region DSB" in draft
        assert "YRDSB" in draft


class TestFetchAndExtract:
    """Tests for fetch_and_extract() — mocked urllib."""

    def _make_mock_response(self, html_content):
        mock_resp = MagicMock()
        mock_resp.read.return_value = html_content.encode("utf-8")
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_returns_tables_and_html(self):
        html = (
            "<html><body>"
            "<table><tr><td>Hello</td></tr></table>"
            "</body></html>"
        )
        mock_resp = self._make_mock_response(html)
        with patch("scrape_board_calendar.urllib.request.urlopen", return_value=mock_resp):
            tables, returned_html = fetch_and_extract("http://example.com/calendar")

        assert isinstance(tables, list)
        assert len(tables) == 1
        assert tables[0][0] == ["Hello"]
        assert "Hello" in returned_html

    def test_returns_html_string(self):
        html = "<html><body><p>No tables</p></body></html>"
        mock_resp = self._make_mock_response(html)
        with patch("scrape_board_calendar.urllib.request.urlopen", return_value=mock_resp):
            tables, returned_html = fetch_and_extract("http://example.com/")

        assert tables == []
        assert isinstance(returned_html, str)
        assert "No tables" in returned_html

    def test_multiple_tables_returned(self):
        html = (
            "<table><tr><td>T1</td></tr></table>"
            "<table><tr><td>T2</td></tr></table>"
        )
        mock_resp = self._make_mock_response(html)
        with patch("scrape_board_calendar.urllib.request.urlopen", return_value=mock_resp):
            tables, _ = fetch_and_extract("http://example.com/")

        assert len(tables) == 2
