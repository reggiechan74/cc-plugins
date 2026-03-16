---
name: camp-setup
description: Initialize the kids-camp-planner workspace and family profile
arguments:
  - name: directory
    description: Research directory name (default: camp-research)
    required: false
---

Read `.claude/kids-camp-planner.local.md` to check for existing configuration.
Read the family profile at `<research_dir>/family-profile.md` if it exists.

Then follow the setup skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/setup/SKILL.md`.

If a research directory argument was provided, use it as the directory name instead of asking.
