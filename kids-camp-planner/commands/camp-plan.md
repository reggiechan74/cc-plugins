---
name: camp-plan
description: Plan camp coverage for a school break period
arguments:
  - name: period
    description: "Period to plan: summer, march-break, or pa-days"
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md`.

Route to the appropriate planning skill based on the period argument:
- `summer` → Follow `${CLAUDE_PLUGIN_ROOT}/skills/plan-summer/SKILL.md`
- `march-break` → Follow `${CLAUDE_PLUGIN_ROOT}/skills/plan-march-break/SKILL.md`
- `pa-days` → Follow `${CLAUDE_PLUGIN_ROOT}/skills/plan-pa-days/SKILL.md`

If no period argument was provided, ask the user which period they'd like to plan using AskUserQuestion:
- Summer camps (Jun-Aug)
- March break (Mar)
- PA days (throughout the school year)
