---
name: Research Camps
description: This skill should be used when the user asks to "research camps", "find camps near me", "search for camps", "look up camp providers", "what camps are available", "compare camp options", "create camp provider files", "find day camps in [area]", or needs help discovering, evaluating, and documenting camp providers in their area. Creates structured provider markdown files in the research folder.
version: 0.1.0
---

# Research Camps

## Overview

**Locate research directory:** Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path (default: `camp-research`). All user data paths below are relative to this directory. The family profile is at `<research_dir>/family-profile.md`.

Discover, evaluate, and document camp providers for a family's area, creating structured provider files in the `<research_dir>/providers/` directory. Each provider gets its own markdown file with standardized information for easy comparison. Providers are cross-referenced from period-specific schedule files (summer, March break, PA days).

## Research Workflow

### Step 1: Define Search Criteria

Read the family profile from `<research_dir>/family-profile.md` to determine:
- Home address and maximum commute time
- Children's ages (determines eligible programs)
- Children's interests (guides specialty camp search)
- Budget range (filters out unaffordable options)
- Before/after care needs
- Lunch preferences

### Step 2: Conduct Research

Use web search to find camp providers. Search in this order:

**1. Municipal programs (best value):**
- Search: "[municipality] summer camp registration [year]"
- Search: "[municipality] recreation programs children [year]"
- Check the municipal recreation portal directly

**2. Established organizations:**
- Search: "YMCA day camp [city/area] [year]"
- Search: "Boys and Girls Club [city/area] camps"
- Search: "[city] community centre summer programs"

**3. Private and specialty camps:**
- Search: "day camps near [home address area] [year]"
- Search: "[interest] camp [city] children" (e.g., "robotics camp Toronto children")
- Search: "best day camps [area] [year]"
- Check Ontario Camps Association directory: ontariocamps.ca

**4. Niche and interest-based:**
- Search based on each child's interests
- Check local sports clubs, art studios, music schools for camp programs
- Look at university/college campus programs

### Step 3: Create Provider Files

For each camp provider found, create a markdown file in `<research_dir>/providers/` using the standard template.

**File naming:** Use kebab-case: `provider-name.md` (e.g., `ymca-downtown.md`, `city-of-toronto-parks-rec.md`)

**Provider file template:** Use the template at `<research_dir>/templates/provider-template.md` (seeded during setup from the plugin). The template includes sections for: basic information, distance & commute, programs offered, costs (with discount tracking), quality indicators, logistics, suitability rating, and notes.

For completed examples showing all fields filled in with realistic data, see `<research_dir>/examples/ymca-cedar-glen.md` and `<research_dir>/examples/boulderz-etobicoke.md`.

### Step 4: Verify Key Details

For the most promising providers, verify critical details:
- Confirm current-year pricing (costs change annually)
- Check registration status (open, full, waitlist)
- Verify age eligibility for each child
- Confirm before/after care hours match parent schedules

If details cannot be confirmed via web search, note them as "needs verification" and suggest the user confirm by phone/email (offer to draft an inquiry email via the draft-email skill).

### Step 5: Create Comparison Summary

After researching multiple providers, generate a comparison table:

```markdown
# Camp Provider Comparison - [Area]

| Provider | Ages | $/Day | $/Week | Before Care | After Care | Lunch | Distance | Rating |
|----------|------|-------|--------|-------------|------------|-------|----------|--------|
| YMCA Downtown | 4-12 | $56 | $280 | $10/day | $10/day | Pack | 3.2 km | Strong |
| City Parks Rec | 6-12 | $39 | $195 | $8/day | $8/day | Pack | 1.5 km | Strong |
| Science Camp | 7-12 | $85 | $425 | No | No | Incl | 8.1 km | Good |
```

Include daily rates ($/Day) alongside weekly rates for accurate partial-week and PA day costing.

Save this comparison to `<research_dir>/providers/comparison-summary.md`.

## Research Tips

### Finding Current-Year Information
- Always include the year in search queries
- Municipal program guides are usually published in January-February
- Check "What's New" sections on recreation portals
- Look for PDF program guides (often more detailed than web pages)

### Evaluating Online Reviews
- Check Google Reviews, Facebook reviews, and parent forums
- Look for reviews from the most recent year
- Pay attention to recurring themes (positive and negative)
- Weight reviews from parents with similar-aged children more heavily

### Hidden Gems
- Library-run programs (free or very low cost)
- Conservation authority camps (nature-focused, affordable)
- University faculty/staff camps (sometimes open to public)
- Ethnic/cultural community centres (multilingual options)
- Church-run VBS programs (often free, typically July)

## Additional Resources

### Reference Files

- **`<research_dir>/templates/provider-template.md`** - Blank provider file template for quick copying (seeded during setup)
- **`<research_dir>/examples/ymca-cedar-glen.md`** - Completed example provider file (YMCA Cedar Glen, multi-program)
- **`<research_dir>/examples/boulderz-etobicoke.md`** - Specialty camp example (Boulderz Climbing, single-program)
