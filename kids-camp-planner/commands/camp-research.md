---
name: camp-research
description: Research and document camp providers in your area
arguments:
  - name: focus
    description: Search focus (e.g., "STEM camps", "week 3 alternatives", "swimming")
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md` for location, ages, and constraints.

Then follow the research-camps skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/research-camps/SKILL.md`.

If a search focus was provided, use it to narrow the research scope. Otherwise, research broadly based on the family profile.
