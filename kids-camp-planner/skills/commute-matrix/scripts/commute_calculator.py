#!/usr/bin/env python3
"""
Commute Matrix Calculator

Calculate travel times between home, work, and camp locations using the
Geoapify Route Matrix API. Models full commute chains (Home -> Camp -> Work
in AM, Work -> Camp -> Home in PM) across multiple travel modes.

Usage:
    # Basic: compute commutes for all providers
    python3 commute_calculator.py \
        --profile .claude/kids-camp-planner.local.md \
        --providers camp-research/providers/ \
        --modes drive,transit \
        --output-md camp-research/commute-report.md \
        --output-json camp-research/commute-matrix.json \
        --geocache camp-research/geocache.json

    # With provider file updates
    python3 commute_calculator.py \
        --profile .claude/kids-camp-planner.local.md \
        --providers camp-research/providers/ \
        --modes drive,transit \
        --output-md camp-research/commute-report.md \
        --output-json camp-research/commute-matrix.json \
        --update-providers \
        --geocache camp-research/geocache.json

API: Geoapify Route Matrix (POST /v1/routematrix) + Geocoding (GET /v1/geocode/search)
Free tier: 3,000 matrix requests/day, 90,000 geocoding/month
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date


# ---------------------------------------------------------------------------
# Profile parsing
# ---------------------------------------------------------------------------

def parse_profile(profile_path):
    """Parse family profile YAML frontmatter for addresses and API key.

    Returns dict with keys: home_address, work_addresses, api_key, max_commute.
    work_addresses is a list of {name, address} dicts.
    """
    with open(profile_path, encoding="utf-8") as f:
        text = f.read()

    # Extract YAML frontmatter between --- markers
    m = re.match(r"^---\n(.*?\n)---", text, re.DOTALL)
    if not m:
        print("Error: Could not find YAML frontmatter in profile.", file=sys.stderr)
        sys.exit(1)

    yaml_text = m.group(1)

    result = {
        "home_address": "",
        "work_addresses": [],
        "api_key": "",
        "max_commute": 0,
    }

    # Home address
    hm = re.search(r'^home_address:\s*"?(.+?)"?\s*$', yaml_text, re.MULTILINE)
    if hm:
        result["home_address"] = hm.group(1).strip().strip('"')

    # Max commute
    mc = re.search(r'^max_commute_minutes:\s*(\d+)', yaml_text, re.MULTILINE)
    if mc:
        result["max_commute"] = int(mc.group(1))

    # API key
    ak = re.search(r'geoapify_api_key:\s*"?([^"\s]+)"?', yaml_text)
    if ak:
        result["api_key"] = ak.group(1).strip()

    # Parents and work addresses
    # Parse the parents block by finding each parent entry
    parents_block = re.search(r'^parents:\s*\n((?:[ \t]+.*\n)*)', yaml_text, re.MULTILINE)
    if parents_block:
        parent_text = parents_block.group(1)
        # Split into individual parent entries on "- name:"
        entries = re.split(r'(?=\s+-\s+name:)', parent_text)
        for entry in entries:
            nm = re.search(r'name:\s*"?([^"\n]+)"?', entry)
            wa = re.search(r'work_address:\s*"?([^"\n]+)"?', entry)
            if nm and wa:
                addr = wa.group(1).strip().strip('"')
                if addr:
                    result["work_addresses"].append({
                        "name": nm.group(1).strip().strip('"'),
                        "address": addr,
                    })

    return result


# ---------------------------------------------------------------------------
# Provider scanning
# ---------------------------------------------------------------------------

def scan_providers(providers_dir):
    """Scan provider markdown files for camp names and addresses.

    Returns list of {name, address, file_path} dicts.
    """
    providers = []
    if not os.path.isdir(providers_dir):
        print(f"Warning: Providers directory not found: {providers_dir}", file=sys.stderr)
        return providers

    for fname in sorted(os.listdir(providers_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(providers_dir, fname)
        with open(fpath, encoding="utf-8") as f:
            text = f.read()

        # Camp name from first H1
        nm = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        # Address from **Location**: line
        addr = re.search(r'\*\*Location\*\*:\s*(.+)$', text, re.MULTILINE)

        if nm and addr:
            providers.append({
                "name": nm.group(1).strip(),
                "address": addr.group(1).strip(),
                "file_path": fpath,
            })
        elif nm:
            print(f"Warning: No address found in {fname}, skipping.", file=sys.stderr)

    return providers


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------

def load_geocache(cache_path):
    """Load geocoding cache from JSON file."""
    if cache_path and os.path.isfile(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_geocache(cache, cache_path):
    """Save geocoding cache to JSON file."""
    if not cache_path:
        return
    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def normalize_address(address):
    """Normalize address for cache key: lowercase, strip extra whitespace."""
    return re.sub(r'\s+', ' ', address.strip().lower())


def geocode(address, api_key, cache):
    """Geocode an address using Geoapify API, with caching.

    Returns {lat, lon, formatted_address} or None on failure.
    """
    key = normalize_address(address)
    if key in cache:
        return cache[key]

    if not api_key:
        print(f"Error: No API key — cannot geocode '{address}'.", file=sys.stderr)
        return None

    params = urllib.parse.urlencode({"text": address, "apiKey": api_key})
    url = f"https://api.geoapify.com/v1/geocode/search?{params}"

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"Error geocoding '{address}': {e}", file=sys.stderr)
        return None

    features = data.get("features", [])
    if not features:
        print(f"Warning: No geocoding results for '{address}'.", file=sys.stderr)
        return None

    props = features[0].get("properties", {})
    geom = features[0].get("geometry", {})
    coords = geom.get("coordinates", [0, 0])

    result = {
        "lat": coords[1],
        "lon": coords[0],
        "formatted": props.get("formatted", address),
        "cached_at": str(date.today()),
    }
    cache[key] = result
    return result


# ---------------------------------------------------------------------------
# Route matrix
# ---------------------------------------------------------------------------

def route_matrix(sources, targets, mode, api_key):
    """Call Geoapify Route Matrix API.

    sources/targets: list of {lat, lon} dicts.
    mode: one of 'drive', 'transit', 'walk', 'bicycle'.

    Returns 2D list [source_idx][target_idx] of {duration_sec, distance_m}
    or None on failure.
    """
    if not api_key:
        print("Error: No API key — cannot compute route matrix.", file=sys.stderr)
        return None

    # Map user-friendly mode names to Geoapify API values
    # Note: Geoapify route matrix does not support "transit" directly;
    # "bus" is the closest supported mode for public transit routing.
    mode_map = {
        "drive": "drive",
        "transit": "bus",
        "walk": "walk",
        "bicycle": "bicycle",
    }
    api_mode = mode_map.get(mode, mode)

    body = {
        "mode": api_mode,
        "sources": [{"location": [s["lon"], s["lat"]]} for s in sources],
        "targets": [{"location": [t["lon"], t["lat"]]} for t in targets],
    }

    url = f"https://api.geoapify.com/v1/routematrix?apiKey={api_key}"
    data = json.dumps(body).encode("utf-8")

    try:
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"Error in route matrix ({mode}): {e}", file=sys.stderr)
        return None

    # Parse results into 2D array
    sources_count = len(sources)
    targets_count = len(targets)
    matrix = [[None] * targets_count for _ in range(sources_count)]

    for entry in result.get("sources_to_targets", []):
        for item in entry:
            si = item.get("source_index", 0)
            ti = item.get("target_index", 0)
            matrix[si][ti] = {
                "duration_sec": item.get("time", 0),
                "distance_m": item.get("distance", 0),
            }

    return matrix


# ---------------------------------------------------------------------------
# Chain computation
# ---------------------------------------------------------------------------

def compute_chains(home_geo, camps, work_addresses, modes, api_key, cache):
    """Compute full AM/PM commute chains for all camps.

    Returns dict keyed by camp name:
    {
        camp_name: {
            "address": str,
            "lat": float, "lon": float,
            "modes": {
                mode: {
                    "direct": {"home_to_camp": min, "camp_to_home": min, "distance_km": float},
                    "chains": {
                        parent_name: {"am": min, "pm": min}
                    }
                }
            }
        }
    }
    """
    if not camps:
        return {}

    # Geocode all camp addresses
    camp_geos = []
    valid_camps = []
    for camp in camps:
        geo = geocode(camp["address"], api_key, cache)
        if geo:
            camp_geos.append(geo)
            valid_camps.append(camp)
        else:
            print(f"Warning: Skipping {camp['name']} — could not geocode.", file=sys.stderr)

    if not valid_camps:
        print("Error: No camps could be geocoded.", file=sys.stderr)
        return {}

    # Geocode work addresses
    work_geos = []
    valid_works = []
    for w in work_addresses:
        geo = geocode(w["address"], api_key, cache)
        if geo:
            work_geos.append(geo)
            valid_works.append(w)
        else:
            print(f"Warning: Skipping work address for {w['name']} — could not geocode.", file=sys.stderr)

    # Build location list: [home, camp0, camp1, ..., work0, work1, ...]
    # Index mapping:
    #   0 = home
    #   1..len(valid_camps) = camps
    #   len(valid_camps)+1.. = work addresses
    all_locations = [{"lat": home_geo["lat"], "lon": home_geo["lon"]}]
    for cg in camp_geos:
        all_locations.append({"lat": cg["lat"], "lon": cg["lon"]})
    for wg in work_geos:
        all_locations.append({"lat": wg["lat"], "lon": wg["lon"]})

    home_idx = 0
    camp_start = 1
    work_start = camp_start + len(valid_camps)

    commute_data = {}

    for mode in modes:
        # Single matrix call with all locations as both sources and targets
        matrix = route_matrix(all_locations, all_locations, mode, api_key)
        if not matrix:
            print(f"Warning: Route matrix failed for mode '{mode}', skipping.", file=sys.stderr)
            continue

        for ci, camp in enumerate(valid_camps):
            camp_idx = camp_start + ci

            if camp["name"] not in commute_data:
                commute_data[camp["name"]] = {
                    "address": camp["address"],
                    "lat": camp_geos[ci]["lat"],
                    "lon": camp_geos[ci]["lon"],
                    "file_path": camp.get("file_path", ""),
                    "modes": {},
                }

            # Direct home <-> camp
            h2c = matrix[home_idx][camp_idx]
            c2h = matrix[camp_idx][home_idx]

            h2c_min = round(h2c["duration_sec"] / 60) if h2c else None
            c2h_min = round(c2h["duration_sec"] / 60) if c2h else None
            h2c_km = round(h2c["distance_m"] / 1000, 1) if h2c else None

            mode_data = {
                "direct": {
                    "home_to_camp": h2c_min,
                    "camp_to_home": c2h_min,
                    "distance_km": h2c_km,
                },
                "chains": {},
            }

            # Chain calculations for each parent
            for wi, work in enumerate(valid_works):
                work_idx = work_start + wi
                c2w = matrix[camp_idx][work_idx]
                w2c = matrix[work_idx][camp_idx]

                c2w_min = round(c2w["duration_sec"] / 60) if c2w else None
                w2c_min = round(w2c["duration_sec"] / 60) if w2c else None

                am_chain = None
                pm_chain = None

                if h2c_min is not None and c2w_min is not None:
                    am_chain = h2c_min + c2w_min
                if w2c_min is not None and c2h_min is not None:
                    pm_chain = w2c_min + c2h_min

                mode_data["chains"][work["name"]] = {
                    "am": am_chain,
                    "pm": pm_chain,
                    "home_to_camp": h2c_min,
                    "camp_to_work": c2w_min,
                    "work_to_camp": w2c_min,
                    "camp_to_home": c2h_min,
                }

            commute_data[camp["name"]]["modes"][mode] = mode_data

    return commute_data


# ---------------------------------------------------------------------------
# Output: Markdown report
# ---------------------------------------------------------------------------

def render_markdown(commute_data, home_address, max_commute, modes):
    """Render commute report as markdown."""
    lines = []
    lines.append("# Commute Analysis\n")
    lines.append(f"**Home**: {home_address}")
    lines.append(f"**Max commute**: {max_commute} minutes")
    lines.append(f"**Generated**: {date.today()}\n")

    if not commute_data:
        lines.append("*No commute data available. Check that provider files have addresses and the API key is configured.*\n")
        return "\n".join(lines)

    # Determine which parents appear
    all_parents = set()
    for camp_info in commute_data.values():
        for mode, mdata in camp_info["modes"].items():
            all_parents.update(mdata["chains"].keys())
    parent_list = sorted(all_parents)

    # --- Summary table ---
    lines.append("## Summary\n")

    # Build header
    header_parts = ["Camp"]
    for mode in modes:
        header_parts.append(f"Direct ({mode})")
    for parent in parent_list:
        header_parts.append(f"AM Chain ({parent})")
        header_parts.append(f"PM Chain ({parent})")
    header_parts.append("Status")
    lines.append("| " + " | ".join(header_parts) + " |")
    lines.append("|" + "|".join(["------"] * len(header_parts)) + "|")

    # Build rows
    violations = []
    for camp_name, camp_info in sorted(commute_data.items()):
        row = [camp_name]
        exceeds = False
        best_chain = None

        for mode in modes:
            mdata = camp_info["modes"].get(mode, {})
            direct = mdata.get("direct", {})
            h2c = direct.get("home_to_camp")
            dist = direct.get("distance_km")
            if h2c is not None and dist is not None:
                row.append(f"{h2c} min / {dist} km")
            elif h2c is not None:
                row.append(f"{h2c} min")
            else:
                row.append("--")

        for parent in parent_list:
            for chain_type in ["am", "pm"]:
                # Use first available mode for summary
                val = None
                for mode in modes:
                    mdata = camp_info["modes"].get(mode, {})
                    chains = mdata.get("chains", {}).get(parent, {})
                    v = chains.get(chain_type)
                    if v is not None:
                        if val is None:
                            val = v
                        break
                if val is not None:
                    row.append(f"{val} min")
                    if max_commute > 0 and val > max_commute:
                        exceeds = True
                    if best_chain is None or val < best_chain:
                        best_chain = val
                else:
                    row.append("--")

        status = "EXCEEDS MAX" if exceeds else "OK"
        row.append(f"**{status}**")
        lines.append("| " + " | ".join(row) + " |")

        if exceeds:
            violations.append(camp_name)

    lines.append("")

    # --- Detailed chains ---
    lines.append("## Detailed Chains\n")

    for camp_name, camp_info in sorted(commute_data.items()):
        lines.append(f"### {camp_name}")
        lines.append(f"**Address**: {camp_info['address']}\n")

        # Build detail table
        route_labels = ["Home -> Camp", "Camp -> Home"]
        for parent in parent_list:
            route_labels.extend([
                f"Camp -> {parent} Work",
                f"{parent} Work -> Camp",
            ])
        for parent in parent_list:
            route_labels.extend([
                f"**AM Chain ({parent})**",
                f"**PM Chain ({parent})**",
            ])

        header = "| Route | " + " | ".join(modes) + " |"
        sep = "|-------|" + "|".join(["-------"] * len(modes)) + "|"
        lines.append(header)
        lines.append(sep)

        for label in route_labels:
            row = [label]
            for mode in modes:
                mdata = camp_info["modes"].get(mode, {})
                direct = mdata.get("direct", {})
                chains_all = mdata.get("chains", {})

                val = None
                if label == "Home -> Camp":
                    val = direct.get("home_to_camp")
                elif label == "Camp -> Home":
                    val = direct.get("camp_to_home")
                else:
                    for parent in parent_list:
                        chains = chains_all.get(parent, {})
                        if label == f"Camp -> {parent} Work":
                            val = chains.get("camp_to_work")
                            break
                        elif label == f"{parent} Work -> Camp":
                            val = chains.get("work_to_camp")
                            break
                        elif label == f"**AM Chain ({parent})**":
                            val = chains.get("am")
                            break
                        elif label == f"**PM Chain ({parent})**":
                            val = chains.get("pm")
                            break

                row.append(f"{val} min" if val is not None else "--")
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")

    # --- Constraint violations ---
    if violations:
        lines.append("## Constraint Violations\n")
        for camp_name in violations:
            camp_info = commute_data[camp_name]
            details = []
            for mode in modes:
                mdata = camp_info["modes"].get(mode, {})
                for parent_name, chains in mdata.get("chains", {}).items():
                    for chain_type in ["am", "pm"]:
                        v = chains.get(chain_type)
                        if v is not None and max_commute > 0 and v > max_commute:
                            details.append(f"{chain_type.upper()} chain {v} min exceeds {max_commute} min max ({mode}, {parent_name})")
            lines.append(f"- **{camp_name}**: " + "; ".join(details))
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output: JSON
# ---------------------------------------------------------------------------

def render_json(commute_data, home_address, home_geo, max_commute, modes):
    """Render structured JSON output for schedule-optimizer consumption."""
    camps_json = {}

    for camp_name, camp_info in commute_data.items():
        camp_entry = {
            "address": camp_info["address"],
            "lat": camp_info["lat"],
            "lon": camp_info["lon"],
            "modes": {},
            "exceeds_max": False,
            "best_mode": None,
            "best_chain_minutes": None,
        }

        best_overall = None

        for mode in modes:
            mdata = camp_info["modes"].get(mode, {})
            direct = mdata.get("direct", {})
            chains = mdata.get("chains", {})

            mode_entry = {
                "direct": {
                    "home_to_camp": direct.get("home_to_camp"),
                    "camp_to_home": direct.get("camp_to_home"),
                    "distance_km": direct.get("distance_km"),
                },
                "chains": {},
            }

            for parent_name, chain_data in chains.items():
                am = chain_data.get("am")
                pm = chain_data.get("pm")
                mode_entry["chains"][parent_name] = {"am": am, "pm": pm}

                # Track worst chain for this camp
                for v in [am, pm]:
                    if v is not None:
                        if max_commute > 0 and v > max_commute:
                            camp_entry["exceeds_max"] = True
                        if best_overall is None or v < best_overall:
                            best_overall = v
                            camp_entry["best_mode"] = mode
                            camp_entry["best_chain_minutes"] = v

            camp_entry["modes"][mode] = mode_entry

        # If no chains computed, use direct home->camp as best
        if best_overall is None:
            for mode in modes:
                mdata = camp_info["modes"].get(mode, {})
                h2c = mdata.get("direct", {}).get("home_to_camp")
                if h2c is not None:
                    camp_entry["best_mode"] = mode
                    camp_entry["best_chain_minutes"] = h2c
                    if max_commute > 0 and h2c > max_commute:
                        camp_entry["exceeds_max"] = True
                    break

        camps_json[camp_name] = camp_entry

    return {
        "generated": str(date.today()),
        "home": {
            "address": home_address,
            "lat": home_geo["lat"] if home_geo else None,
            "lon": home_geo["lon"] if home_geo else None,
        },
        "max_commute_minutes": max_commute,
        "camps": camps_json,
    }


# ---------------------------------------------------------------------------
# Provider file updates
# ---------------------------------------------------------------------------

def update_provider_files(commute_data, modes):
    """Update provider markdown files with computed commute data.

    Splits the Distance & Commute section into Manual and Computed subsections.
    Preserves any manual data (transit accessible, parking) and replaces the
    Computed subsection with fresh API results.
    """
    for camp_name, camp_info in commute_data.items():
        fpath = camp_info.get("file_path")
        if not fpath or not os.path.isfile(fpath):
            continue

        with open(fpath, encoding="utf-8") as f:
            text = f.read()

        # Find the Distance & Commute section
        pattern = r'(## Distance & Commute\n)(.*?)(\n## |\n---|\Z)'
        m = re.search(pattern, text, re.DOTALL)
        if not m:
            continue

        section_header = m.group(1)
        old_content = m.group(2)
        next_section = m.group(3)

        # Extract manual data from old content
        manual_lines = []
        manual_fields = ["transit accessible", "parking"]
        for line in old_content.strip().split("\n"):
            line_lower = line.lower()
            # Keep lines that are manual fields (not computed ones)
            if any(f in line_lower for f in manual_fields):
                manual_lines.append(line)
            # Also keep lines under a ### Manual subsection
            elif line.startswith("### Manual"):
                continue  # skip the header, we'll re-add it
            elif line.startswith("### Computed"):
                break  # stop at computed section

        if not manual_lines:
            # Try to extract from the flat list format
            for line in old_content.strip().split("\n"):
                line_lower = line.lower()
                if any(f in line_lower for f in manual_fields):
                    manual_lines.append(line)

        # Build new section
        new_content = "\n### Manual\n"
        if manual_lines:
            new_content += "\n".join(manual_lines) + "\n"
        else:
            new_content += "- **Transit accessible**: [Yes/No]\n"
            new_content += "- **Parking**: [Available/Street/None]\n"

        new_content += "\n### Computed\n"
        new_content += "<!-- Auto-updated by commute-matrix skill -- do not edit manually -->\n"

        # Add computed data
        for mode in modes:
            mdata = camp_info["modes"].get(mode, {})
            direct = mdata.get("direct", {})
            h2c = direct.get("home_to_camp")
            dist = direct.get("distance_km")

            if mode == "drive":
                if dist is not None:
                    new_content += f"- **Distance from home**: {dist} km\n"
                if h2c is not None:
                    new_content += f"- **Drive time**: {h2c} minutes\n"
            elif mode == "transit":
                if h2c is not None:
                    new_content += f"- **Transit time**: {h2c} minutes\n"
            elif mode == "walk":
                if h2c is not None:
                    new_content += f"- **Walk time**: {h2c} minutes\n"
            elif mode == "bicycle":
                if h2c is not None:
                    new_content += f"- **Bicycle time**: {h2c} minutes\n"

        # Add chain summaries (use first mode with chains, typically drive)
        chains_added = False
        for mode in modes:
            mdata = camp_info["modes"].get(mode, {})
            for parent_name, chains in mdata.get("chains", {}).items():
                am = chains.get("am")
                pm = chains.get("pm")
                if am is not None:
                    new_content += f"- **AM chain ({mode})**: Home -> Camp -> {parent_name} Work = {am} min\n"
                if pm is not None:
                    new_content += f"- **PM chain ({mode})**: {parent_name} Work -> Camp -> Home = {pm} min\n"
                chains_added = True

        # Add status
        exceeds = False
        for mode in modes:
            mdata = camp_info["modes"].get(mode, {})
            for chains in mdata.get("chains", {}).values():
                for v in [chains.get("am"), chains.get("pm")]:
                    if v is not None and camp_info.get("max_commute", 0) > 0 and v > camp_info.get("max_commute", 0):
                        exceeds = True

        new_content += f"- **Status**: {'EXCEEDS MAX' if exceeds else 'OK'}\n"
        new_content += f"- *Last computed: {date.today()}*\n"

        # Replace section
        replacement = section_header + new_content + next_section
        new_text = text[:m.start()] + replacement + text[m.end():]

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_text)

        print(f"Updated: {fpath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Calculate commute times between home, work, and camp locations using Geoapify API."
    )
    parser.add_argument("--profile", required=True,
                        help="Path to family profile (.claude/kids-camp-planner.local.md)")
    parser.add_argument("--providers", required=True,
                        help="Path to providers directory (camp-research/providers/)")
    parser.add_argument("--modes", default="drive,transit",
                        help="Comma-separated travel modes: drive, transit, walk, bicycle (default: drive,transit)")
    parser.add_argument("--output-md",
                        help="Output path for commute report markdown")
    parser.add_argument("--output-json",
                        help="Output path for commute matrix JSON")
    parser.add_argument("--update-providers", action="store_true",
                        help="Update provider files with computed commute data")
    parser.add_argument("--geocache",
                        help="Path to geocoding cache file (camp-research/geocache.json)")

    args = parser.parse_args()
    modes = [m.strip() for m in args.modes.split(",") if m.strip()]

    # Step 1: Parse profile
    print("Reading family profile...", file=sys.stderr)
    profile = parse_profile(args.profile)

    if not profile["home_address"]:
        print("Error: No home_address found in profile.", file=sys.stderr)
        sys.exit(1)

    if not profile["api_key"]:
        print(
            "Error: No Geoapify API key found in profile.\n"
            "Add your key under apis.geoapify_api_key in your family profile.\n"
            "Get a free key at https://myprojects.geoapify.com/",
            file=sys.stderr,
        )
        sys.exit(1)

    # Step 2: Scan providers
    print("Scanning provider files...", file=sys.stderr)
    providers = scan_providers(args.providers)
    if not providers:
        print("Error: No provider files with addresses found.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(providers)} providers: {', '.join(p['name'] for p in providers)}", file=sys.stderr)

    # Step 3: Geocode home
    cache = load_geocache(args.geocache)
    print("Geocoding addresses...", file=sys.stderr)
    home_geo = geocode(profile["home_address"], profile["api_key"], cache)
    if not home_geo:
        print("Error: Could not geocode home address.", file=sys.stderr)
        sys.exit(1)

    # Step 4: Compute chains
    print(f"Computing route matrix for modes: {', '.join(modes)}...", file=sys.stderr)
    commute_data = compute_chains(
        home_geo, providers, profile["work_addresses"],
        modes, profile["api_key"], cache,
    )

    # Save geocache
    save_geocache(cache, args.geocache)

    if not commute_data:
        print("Error: No commute data computed.", file=sys.stderr)
        sys.exit(1)

    print(f"Computed commute data for {len(commute_data)} camps.", file=sys.stderr)

    # Step 5: Generate markdown report
    if args.output_md:
        md = render_markdown(commute_data, profile["home_address"], profile["max_commute"], modes)
        os.makedirs(os.path.dirname(args.output_md) or ".", exist_ok=True)
        with open(args.output_md, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Wrote commute report: {args.output_md}", file=sys.stderr)

    # Step 6: Generate JSON output
    if args.output_json:
        json_data = render_json(commute_data, profile["home_address"], home_geo, profile["max_commute"], modes)
        os.makedirs(os.path.dirname(args.output_json) or ".", exist_ok=True)
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
        print(f"Wrote commute matrix: {args.output_json}", file=sys.stderr)

    # Step 7: Update provider files
    if args.update_providers:
        print("Updating provider files...", file=sys.stderr)
        update_provider_files(commute_data, modes)

    # Print summary to stdout
    print("\n# Commute Summary\n")
    for camp_name, camp_info in sorted(commute_data.items()):
        best_mode = None
        best_chain = None
        for mode in modes:
            mdata = camp_info["modes"].get(mode, {})
            direct = mdata.get("direct", {})
            h2c = direct.get("home_to_camp")
            for chains in mdata.get("chains", {}).values():
                for v in [chains.get("am"), chains.get("pm")]:
                    if v is not None and (best_chain is None or v < best_chain):
                        best_chain = v
                        best_mode = mode
            if h2c is not None and (best_chain is None or h2c < best_chain):
                best_chain = h2c
                best_mode = mode

        status = "OK"
        if best_chain is not None and profile["max_commute"] > 0 and best_chain > profile["max_commute"]:
            status = "EXCEEDS MAX"

        print(f"- {camp_name}: {best_chain} min ({best_mode}) [{status}]")


if __name__ == "__main__":
    main()
