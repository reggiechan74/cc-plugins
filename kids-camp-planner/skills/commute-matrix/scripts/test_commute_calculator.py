"""Tests for commute_calculator.py."""

import json
import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(__file__))
from commute_calculator import (
    compute_chains,
    geocode,
    load_geocache,
    normalize_address,
    parse_profile,
    render_json,
    render_markdown,
    route_matrix,
    save_geocache,
    scan_providers,
    update_provider_files,
)


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


# ---------------------------------------------------------------------------
# Provider scanning
# ---------------------------------------------------------------------------

class TestScanProviders:
    """Tests for scan_providers()."""

    def test_valid_provider(self, tmp_path):
        p = tmp_path / "camp-a.md"
        p.write_text("# Sunny Camp\n**Location**: 100 Main St, Toronto, ON\n")
        results = scan_providers(str(tmp_path))
        assert len(results) == 1
        assert results[0]["name"] == "Sunny Camp"
        assert results[0]["address"] == "100 Main St, Toronto, ON"
        assert results[0]["file_path"] == str(p)

    def test_missing_address_skipped(self, tmp_path, capsys):
        p = tmp_path / "camp-b.md"
        p.write_text("# Camp No Address\nSome text here.\n")
        results = scan_providers(str(tmp_path))
        assert results == []
        captured = capsys.readouterr()
        assert "No address found" in captured.err

    def test_non_md_files_ignored(self, tmp_path):
        (tmp_path / "notes.txt").write_text("# Camp Txt\n**Location**: 1 St\n")
        (tmp_path / "data.json").write_text('{"name": "Camp"}')
        results = scan_providers(str(tmp_path))
        assert results == []

    def test_nonexistent_dir_returns_empty(self, tmp_path, capsys):
        results = scan_providers(str(tmp_path / "nonexistent"))
        assert results == []
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_sorted_order(self, tmp_path):
        (tmp_path / "z-camp.md").write_text("# Z Camp\n**Location**: 999 Z St\n")
        (tmp_path / "a-camp.md").write_text("# A Camp\n**Location**: 111 A St\n")
        results = scan_providers(str(tmp_path))
        assert results[0]["name"] == "A Camp"
        assert results[1]["name"] == "Z Camp"


# ---------------------------------------------------------------------------
# Normalize address
# ---------------------------------------------------------------------------

class TestNormalizeAddress:
    """Tests for normalize_address()."""

    def test_lowercase_and_strip(self):
        assert normalize_address("  123 MAIN ST  ") == "123 main st"

    def test_collapse_whitespace(self):
        assert normalize_address("123   Main   St") == "123 main st"

    def test_mixed(self):
        result = normalize_address("  100  Queen's  Park , Toronto  ")
        assert result == result.lower()
        assert "  " not in result


# ---------------------------------------------------------------------------
# Geocode
# ---------------------------------------------------------------------------

class TestGeocode:
    """Tests for geocode()."""

    def test_cache_hit(self):
        cache = {"123 main st": {"lat": 43.65, "lon": -79.38, "formatted": "123 Main St"}}
        result = geocode("123 Main St", "fake-key", cache)
        assert result["lat"] == 43.65

    def test_cache_miss_calls_api(self):
        cache = {}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "features": [{
                "properties": {"formatted": "123 Main St, Toronto"},
                "geometry": {"coordinates": [-79.38, 43.65]},
            }]
        }).encode()
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("commute_calculator.urllib.request.urlopen", return_value=mock_resp):
            result = geocode("123 Main St", "fake-key", cache)

        assert result is not None
        assert result["lat"] == 43.65
        assert result["lon"] == -79.38
        # Result cached
        assert "123 main st" in cache

    def test_no_api_key_returns_none(self, capsys):
        result = geocode("123 Main St", "", {})
        assert result is None
        captured = capsys.readouterr()
        assert "No API key" in captured.err

    def test_api_failure_returns_none(self, capsys):
        import urllib.error
        with patch("commute_calculator.urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
            result = geocode("123 Main St", "fake-key", {})
        assert result is None
        captured = capsys.readouterr()
        assert "Error geocoding" in captured.err


# ---------------------------------------------------------------------------
# Geocache
# ---------------------------------------------------------------------------

class TestGeocache:
    """Tests for load_geocache() / save_geocache() round-trip."""

    def test_round_trip(self, tmp_path):
        cache_file = str(tmp_path / "geocache.json")
        data = {"toronto": {"lat": 43.65, "lon": -79.38}}
        save_geocache(data, cache_file)
        loaded = load_geocache(cache_file)
        assert loaded == data

    def test_nonexistent_file_returns_empty(self, tmp_path):
        result = load_geocache(str(tmp_path / "missing.json"))
        assert result == {}

    def test_none_path_returns_empty(self):
        result = load_geocache(None)
        assert result == {}

    def test_none_path_save_is_noop(self, tmp_path):
        # Should not raise
        save_geocache({"key": "val"}, None)


# ---------------------------------------------------------------------------
# Route matrix
# ---------------------------------------------------------------------------

class TestRouteMatrix:
    """Tests for route_matrix()."""

    def test_no_api_key_returns_none(self, capsys):
        sources = [{"lat": 43.6, "lon": -79.3}]
        targets = [{"lat": 43.7, "lon": -79.4}]
        result = route_matrix(sources, targets, "drive", "")
        assert result is None
        captured = capsys.readouterr()
        assert "No API key" in captured.err

    def test_basic_matrix_parsing(self):
        sources = [{"lat": 43.6, "lon": -79.3}, {"lat": 43.7, "lon": -79.4}]
        targets = [{"lat": 43.6, "lon": -79.3}, {"lat": 43.7, "lon": -79.4}]
        api_response = {
            "sources_to_targets": [
                [
                    {"source_index": 0, "target_index": 0, "time": 0, "distance": 0},
                    {"source_index": 0, "target_index": 1, "time": 600, "distance": 5000},
                ],
                [
                    {"source_index": 1, "target_index": 0, "time": 660, "distance": 5200},
                    {"source_index": 1, "target_index": 1, "time": 0, "distance": 0},
                ],
            ]
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(api_response).encode()
        mock_resp.__enter__ = lambda s: mock_resp
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch("commute_calculator.urllib.request.urlopen", return_value=mock_resp):
            matrix = route_matrix(sources, targets, "drive", "fake-key")

        assert matrix is not None
        assert matrix[0][1]["duration_sec"] == 600
        assert matrix[1][0]["duration_sec"] == 660


# ---------------------------------------------------------------------------
# Compute chains
# ---------------------------------------------------------------------------

class TestComputeChains:
    """Tests for compute_chains() — verifies AM/PM math."""

    def _make_matrix_response(self):
        """
        3x3 matrix: home=0, camp=1, work=2
        h2c = matrix[0][1] = 600s = 10min
        c2h = matrix[1][0] = 660s = 11min
        c2w = matrix[1][2] = 900s = 15min
        w2c = matrix[2][1] = 960s = 16min
        AM = h2c + c2w = 10 + 15 = 25
        PM = w2c + c2h = 16 + 11 = 27
        """
        return [
            [  # source 0 (home)
                {"duration_sec": 0, "distance_m": 0},     # -> home
                {"duration_sec": 600, "distance_m": 5000}, # -> camp
                {"duration_sec": 1200, "distance_m": 10000}, # -> work
            ],
            [  # source 1 (camp)
                {"duration_sec": 660, "distance_m": 5100}, # -> home
                {"duration_sec": 0, "distance_m": 0},      # -> camp
                {"duration_sec": 900, "distance_m": 7000}, # -> work
            ],
            [  # source 2 (work)
                {"duration_sec": 1100, "distance_m": 9000}, # -> home
                {"duration_sec": 960, "distance_m": 7100},  # -> camp
                {"duration_sec": 0, "distance_m": 0},       # -> work
            ],
        ]

    def test_am_pm_chain_math(self):
        home_geo = {"lat": 43.6, "lon": -79.3}
        camps = [{"name": "Fun Camp", "address": "100 Camp Rd", "file_path": ""}]
        work_addresses = [{"name": "Alice", "address": "200 Work Ave"}]

        camp_geo = {"lat": 43.65, "lon": -79.35, "formatted": "100 Camp Rd", "cached_at": "2025-01-01"}
        work_geo = {"lat": 43.7, "lon": -79.4, "formatted": "200 Work Ave", "cached_at": "2025-01-01"}

        matrix = self._make_matrix_response()

        with patch("commute_calculator.geocode", side_effect=[camp_geo, work_geo]):
            with patch("commute_calculator.route_matrix", return_value=matrix):
                result = compute_chains(home_geo, camps, work_addresses, ["drive"], "fake-key", {})

        assert "Fun Camp" in result
        drive_data = result["Fun Camp"]["modes"]["drive"]
        chain = drive_data["chains"]["Alice"]
        assert chain["am"] == 25   # h2c(10) + c2w(15)
        assert chain["pm"] == 27   # w2c(16) + c2h(11)

    def test_empty_camps_returns_empty(self):
        result = compute_chains({"lat": 43.6, "lon": -79.3}, [], [], ["drive"], "key", {})
        assert result == {}


# ---------------------------------------------------------------------------
# Update provider files
# ---------------------------------------------------------------------------

class TestUpdateProviderFiles:
    """Tests for update_provider_files()."""

    def test_computed_section_updated(self, tmp_path):
        provider_file = tmp_path / "camp.md"
        provider_file.write_text(
            "# Sunny Camp\n\n"
            "## Distance & Commute\n"
            "- **Transit accessible**: Yes\n"
            "- **Parking**: Available\n"
            "\n## Other Section\n"
        )
        commute_data = {
            "Sunny Camp": {
                "address": "100 Main St",
                "lat": 43.65,
                "lon": -79.38,
                "file_path": str(provider_file),
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 20, "camp_to_home": 22, "distance_km": 15.0},
                        "chains": {
                            "Alice": {"am": 35, "pm": 38, "home_to_camp": 20, "camp_to_work": 15, "work_to_camp": 16, "camp_to_home": 22}
                        },
                    }
                },
            }
        }
        update_provider_files(commute_data, ["drive"])
        updated = provider_file.read_text()
        assert "### Computed" in updated
        assert "**Drive time**: 20 minutes" in updated
        assert "**Distance from home**: 15.0 km" in updated

    def test_manual_data_preserved(self, tmp_path):
        provider_file = tmp_path / "camp2.md"
        provider_file.write_text(
            "# Camp Two\n\n"
            "## Distance & Commute\n"
            "- **Transit accessible**: Yes\n"
            "- **Parking**: Street\n"
            "\n## Notes\n"
        )
        commute_data = {
            "Camp Two": {
                "address": "200 Other St",
                "lat": 43.7,
                "lon": -79.4,
                "file_path": str(provider_file),
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 10, "camp_to_home": 11, "distance_km": 8.0},
                        "chains": {},
                    }
                },
            }
        }
        update_provider_files(commute_data, ["drive"])
        updated = provider_file.read_text()
        assert "Transit accessible" in updated
        assert "Street" in updated


# ---------------------------------------------------------------------------
# Render markdown
# ---------------------------------------------------------------------------

class TestRenderMarkdown:
    """Tests for render_markdown()."""

    def test_empty_data_returns_no_data_message(self):
        md = render_markdown({}, "123 Main St", 30, ["drive"])
        assert "No commute data available" in md

    def test_exceeds_max_flagged(self):
        commute_data = {
            "Far Camp": {
                "address": "999 Far Rd",
                "lat": 44.0,
                "lon": -80.0,
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 60, "camp_to_home": 65, "distance_km": 50.0},
                        "chains": {
                            "Alice": {"am": 90, "pm": 95}
                        },
                    }
                },
            }
        }
        md = render_markdown(commute_data, "123 Main St", 30, ["drive"])
        assert "EXCEEDS MAX" in md

    def test_ok_status_within_limit(self):
        commute_data = {
            "Near Camp": {
                "address": "50 Near St",
                "lat": 43.66,
                "lon": -79.39,
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 10, "camp_to_home": 11, "distance_km": 5.0},
                        "chains": {
                            "Alice": {"am": 20, "pm": 22}
                        },
                    }
                },
            }
        }
        md = render_markdown(commute_data, "123 Main St", 30, ["drive"])
        assert "**OK**" in md


# ---------------------------------------------------------------------------
# Render JSON
# ---------------------------------------------------------------------------

class TestRenderJson:
    """Tests for render_json()."""

    def _sample_data(self):
        return {
            "Camp Alpha": {
                "address": "100 Alpha Ave",
                "lat": 43.65,
                "lon": -79.38,
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 15, "camp_to_home": 16, "distance_km": 10.0},
                        "chains": {
                            "Alice": {"am": 28, "pm": 30}
                        },
                    }
                },
            }
        }

    def test_structure_verification(self):
        home_geo = {"lat": 43.60, "lon": -79.30}
        data = render_json(self._sample_data(), "123 Main St", home_geo, 30, ["drive"])
        assert "generated" in data
        assert data["home"]["address"] == "123 Main St"
        assert data["max_commute_minutes"] == 30
        assert "Camp Alpha" in data["camps"]
        camp = data["camps"]["Camp Alpha"]
        assert "modes" in camp
        assert "exceeds_max" in camp

    def test_exceeds_max_flag(self):
        home_geo = {"lat": 43.60, "lon": -79.30}
        commute_data = {
            "Far Camp": {
                "address": "999 Far Rd",
                "lat": 44.0,
                "lon": -80.0,
                "modes": {
                    "drive": {
                        "direct": {"home_to_camp": 60, "camp_to_home": 65, "distance_km": 50.0},
                        "chains": {
                            "Alice": {"am": 90, "pm": 95}
                        },
                    }
                },
            }
        }
        data = render_json(commute_data, "123 Main St", home_geo, 30, ["drive"])
        assert data["camps"]["Far Camp"]["exceeds_max"] is True

    def test_within_max_flag_false(self):
        home_geo = {"lat": 43.60, "lon": -79.30}
        data = render_json(self._sample_data(), "123 Main St", home_geo, 30, ["drive"])
        assert data["camps"]["Camp Alpha"]["exceeds_max"] is False
