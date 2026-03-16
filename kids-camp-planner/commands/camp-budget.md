---
name: camp-budget
description: Generate a camp budget analysis with cost breakdown
arguments:
  - name: period
    description: "Period to budget: summer, march-break, pa-days, or annual"
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md` for budget constraints.

Then follow the budget-optimization skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/budget-optimization/SKILL.md`.

If a period argument was provided, scope the budget to that period. Otherwise, generate a budget for the most relevant upcoming period.
