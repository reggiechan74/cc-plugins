#!/usr/bin/env python3
"""
School Board Calendar Scraper (Draft Quality)

Fetches a school board calendar HTML page and produces a draft markdown file
in the standard calendar-template format. Output requires human/agent review.

Targets common Ontario public board HTML table layouts. PDF-only boards
still need manual extraction via Claude Read tool.

Usage:
    python3 scrape_board_calendar.py \
      --board-name "York Region District School Board" \
      --abbreviation YRDSB \
      --year 2025-2026 \
      --url "https://www2.yrdsb.ca/about-us/school-year-calendar" \
      --output skills/camp-planning/references/school-calendars/public-boards/yrdsb.md
"""

import argparse
import re
import sys
import urllib.request
from datetime import datetime
from html.parser import HTMLParser


class TableExtractor(HTMLParser):
    """Extract table data from HTML."""

    def __init__(self):
        super().__init__()
        self.tables = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._current_table = []
        self._current_row = []
        self._current_cell = ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._in_table = True
            self._current_table = []
        elif tag == "tr" and self._in_table:
            self._in_row = True
            self._current_row = []
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._current_cell = ""

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._in_cell:
            self._in_cell = False
            self._current_row.append(self._current_cell.strip())
        elif tag == "tr" and self._in_row:
            self._in_row = False
            if self._current_row:
                self._current_table.append(self._current_row)
        elif tag == "table" and self._in_table:
            self._in_table = False
            if self._current_table:
                self.tables.append(self._current_table)

    def handle_data(self, data):
        if self._in_cell:
            self._current_cell += data


def fetch_and_extract(url):
    """Fetch URL and extract tables."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    parser = TableExtractor()
    parser.feed(html)
    return parser.tables, html


def generate_draft(board_name, abbreviation, year, tables, html):
    """Generate draft markdown from extracted tables."""
    lines = []
    lines.append(f"# {board_name} ({abbreviation})\n")
    lines.append(f"- **Type**: Public")
    lines.append(f"- **Region**: [TODO: fill in region], Ontario")
    lines.append(f"- **Website**: [TODO: fill in website]")
    lines.append(f"- **Calendar URL pattern**: [TODO: fill in URL pattern]")
    lines.append("")
    lines.append("---\n")
    lines.append(f"## {year} School Year\n")
    lines.append(f"**Source**: {board_name} School Year Calendar ({year})\n")

    # Output all extracted tables for review
    lines.append("### Extracted Tables (REVIEW AND REORGANIZE)\n")
    for i, table in enumerate(tables, 1):
        lines.append(f"#### Table {i}\n")
        if table:
            # Build markdown table
            header = table[0]
            lines.append("| " + " | ".join(header) + " |")
            lines.append("|" + "|".join(["---" for _ in header]) + "|")
            for row in table[1:]:
                # Pad rows to match header length
                padded = row + [""] * (len(header) - len(row))
                lines.append("| " + " | ".join(padded[:len(header)]) + " |")
        lines.append("")

    lines.append("### Key Dates\n| Item | Date(s) |\n|------|---------|")
    lines.append("| [TODO] | [TODO] |\n")
    lines.append("### PA Days - Elementary\n| # | Date | Day | Purpose |\n|---|------|-----|---------|")
    lines.append("| [TODO] | [TODO] | [TODO] | [TODO] |\n")
    lines.append("### Holidays & Breaks\n| Holiday/Break | Date(s) | Weekdays Off |\n|---------------|---------|-------------|")
    lines.append("| [TODO] | [TODO] | [TODO] |\n")
    lines.append("### Summer Window (for camp planning)")
    lines.append("- **Last school day**: [TODO]")
    lines.append("- **First fall day**: [TODO]")
    lines.append("- **Summer coverage needed**: ~[TODO] weekdays (~[TODO] weeks)\n")
    lines.append("---\n")
    lines.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append(f"*Source: {board_name} {year} School Year Calendar*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scrape school board calendar from HTML page")
    parser.add_argument("--board-name", required=True, help="Full board name")
    parser.add_argument("--abbreviation", required=True, help="Short abbreviation (e.g., YRDSB)")
    parser.add_argument("--year", required=True, help="School year (e.g., 2025-2026)")
    parser.add_argument("--url", required=True, help="Calendar page URL")
    parser.add_argument("--output", help="Output markdown file path")
    args = parser.parse_args()

    print(f"Fetching {args.url}...")
    try:
        tables, html = fetch_and_extract(args.url)
    except Exception as e:
        print(f"Error fetching URL: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(tables)} tables")
    draft = generate_draft(args.board_name, args.abbreviation, args.year, tables, html)

    if args.output:
        with open(args.output, "w") as f:
            f.write(draft)
        print(f"Draft written to {args.output}")
        print("NOTE: This is a DRAFT. Review and reorganize into standard calendar format.")
    else:
        print(draft)


if __name__ == "__main__":
    main()
