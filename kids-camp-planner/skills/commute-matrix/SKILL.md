---
name: Commute Matrix
description: This skill should be used when the user asks to "calculate commutes", "commute matrix", "travel times", "update commute data", "how far is each camp", "filter by commute", "commute analysis", "check commute times", "driving time to camps", "transit time to camps", or needs automated commute calculations between home, work, and camp locations. Requires a Geoapify API key in the family profile.
version: 0.1.0
---

# Commute Matrix

## Overview

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`. The API key is stored in `.claude/kids-camp-planner.local.md` under `apis.geoapify_api_key`.

Calculate travel times between home, work, and camp locations using the Geoapify Route Matrix API. Models full commute chains (Home -> Camp -> Work in the morning, Work -> Camp -> Home in the evening) across multiple travel modes, and flags providers that exceed the family's maximum commute constraint.

## Prerequisites

- **Geoapify API key**: Free tier at https://myprojects.geoapify.com/ (3,000 matrix requests/day, 90,000 geocoding/month)
- Key stored in `.claude/kids-camp-planner.local.md` under `apis.geoapify_api_key`
- If no API key is configured, prompt the user to set one up (link to the setup skill)

## Workflow

### Step 1: Read Configuration and Family Profile

Read `.claude/kids-camp-planner.local.md` to extract:
- `research_dir` — path to the research directory
- `apis.geoapify_api_key` — API authentication

Read `<research_dir>/family-profile.md` to extract:
- `home_address` — origin for all commute calculations
- `parents[].work_address` — destinations for chain calculations
- `max_commute_minutes` — hard constraint threshold

If no API key is found, inform the user:
> To use automated commute calculations, you need a free Geoapify API key.
> Get one at https://myprojects.geoapify.com/ and add it to `.claude/kids-camp-planner.local.md`
> under `apis.geoapify_api_key`, or run the setup skill to configure it.

### Step 2: Scan Provider Files

Read all `<research_dir>/providers/*.md` files and extract:
- Camp name (H1 heading)
- Address (from `**Location**:` line in Basic Information section)
- File path (for later updates)

### Step 3: Run Commute Calculator

Execute the commute calculator script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/commute-matrix/scripts/commute_calculator.py \
  --profile <research_dir>/family-profile.md \
  --providers <research_dir>/providers/ \
  --api-key <GEOAPIFY_API_KEY> \
  --modes drive,transit \
  --output-md <research_dir>/commute-report.md \
  --output-json <research_dir>/commute-matrix.json \
  --update-providers \
  --geocache <research_dir>/geocache.json
```

Read the API key from `.claude/kids-camp-planner.local.md` (`apis.geoapify_api_key`) and pass it via `--api-key`.

**Arguments:**
- `--profile`: Path to family profile (reads home address, work addresses, max commute)
- `--providers`: Directory containing provider markdown files
- `--api-key`: Geoapify API key (read from `.claude/kids-camp-planner.local.md`)
- `--modes`: Comma-separated travel modes: `drive`, `transit`, `walk`, `bicycle` (default: `drive,transit`)
- `--output-md`: Path for commute report markdown
- `--output-json`: Path for structured JSON output (consumed by schedule-optimizer)
- `--update-providers`: Flag to update provider files' Distance & Commute section
- `--geocache`: Path to geocoding cache file (avoids re-geocoding known addresses)

Replace `<research_dir>` with the actual research directory path from the thin config, and `<GEOAPIFY_API_KEY>` with the actual key value.

### Step 4: Review Results

After the script runs, present the user with:
1. **Summary table** showing each camp's direct drive/transit time and chain times
2. **Constraint violations** — camps exceeding `max_commute_minutes`
3. **Recommendations** — suggest removing flagged camps or adjusting the constraint

### Step 5: Update Provider Files (Optional)

If `--update-providers` was used, the script splits each provider's `Distance & Commute` section into:
- **Manual** — user-provided data (transit accessible, parking)
- **Computed** — API-calculated data (distances, times, chains, status)

The computed subsection is auto-updated on each run; manual data is preserved.

## Output Files

### Commute Report (`<research_dir>/commute-report.md`)

Human-readable markdown with:
- Summary table (all camps, all modes, chain times, status)
- Detailed per-camp chain breakdowns
- Constraint violation list

### Commute Matrix JSON (`<research_dir>/commute-matrix.json`)

Structured data consumed by the schedule-optimizer agent:
- Per-camp, per-mode direct times and chain times
- `exceeds_max` flag for constraint filtering
- `best_mode` and `best_chain_minutes` for quick optimization

### Geocache (`<research_dir>/geocache.json`)

Caches geocoding results to avoid redundant API calls. Keyed by normalized (lowercased, stripped) address. Safe to delete to force re-geocoding.

## Integration with Other Skills

- **Schedule Optimizer**: Reads `<research_dir>/commute-matrix.json` to apply commute constraints and preferences
- **Research Camps**: Provider template includes Manual/Computed commute subsections
- **Setup**: Collects Geoapify API key during initial configuration

## Troubleshooting

- **"No API key found"**: Add `geoapify_api_key` under `apis:` in `.claude/kids-camp-planner.local.md`
- **"Could not geocode address"**: Check the address format — include city, province, postal code
- **"Rate limit exceeded"**: Free tier allows 3,000 matrix requests/day; wait or upgrade
- **Stale data**: Delete `<research_dir>/geocache.json` to force re-geocoding, then re-run
