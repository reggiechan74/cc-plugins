---
name: camp-email
description: Draft an email to a camp provider
arguments:
  - name: details
    description: "Email type and provider (e.g., 'inquiry YMCA', 'waitlist Science Camp')"
    required: false
---

Read `.claude/kids-camp-planner.local.md` to get the `research_dir` path.
Read the family profile at `<research_dir>/family-profile.md` for personalization.

Then follow the draft-email skill workflow from `${CLAUDE_PLUGIN_ROOT}/skills/draft-email/SKILL.md`.

If details were provided, parse the email type (inquiry, registration, waitlist, special-needs, cancellation, logistics) and provider name from the argument. Otherwise, ask the user what type of email they need and which provider it's for.
