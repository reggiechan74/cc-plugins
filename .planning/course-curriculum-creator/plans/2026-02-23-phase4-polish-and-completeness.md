# Phase 4: Polish & Completeness — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add pilot testing protocol and content licensing/IP tracking to bring the plugin to v1.0.0 — a complete professional L&D curriculum design tool.

**Architecture:** Two independent workstreams — (1) a `--pilot` flag on the existing `process-workshop-feedback` command that activates enhanced pilot-specific feedback analysis and generates a `pilot-iteration-plan.md`; (2) a `content-sources.md` template added to the course directory during `create-course` and populated during `generate-lesson-plans`. Both integrate into the quality-reviewer agent and curriculum-architect autonomous workflow. All follow established v0.6.0 plugin conventions (markdown with YAML frontmatter, no runtime code).

**Tech Stack:** Markdown command/skill files with YAML frontmatter. No runtime code.

---

## Task 1: Add `--pilot` Flag to `process-workshop-feedback`

**Files:**
- Modify: `commands/process-workshop-feedback.md`

**Step 1: Read current file**

Read `commands/process-workshop-feedback.md`.

**Step 2: Update argument-hint**

Change the `argument-hint` line from:
```
argument-hint: "[feedback-file-or-notes]"
```
To:
```
argument-hint: "[feedback-file-or-notes] [--pilot]"
```

**Step 3: Add pilot mode section**

After the existing "## Feedback Analysis Framework" section (after Dimension 5: Overall Impact), add:

```markdown
## Pilot Mode (--pilot flag)

When invoked with `--pilot`, this command activates enhanced feedback collection designed for first-run deliveries. A pilot is fundamentally different from steady-state delivery — the goal is to validate the curriculum design itself, not just the instructor's delivery.

### Additional Pilot Dimensions

In addition to the standard 5 dimensions above, pilot mode adds:

### Dimension 6: Timing Accuracy (Pilot Only)
- Did each module finish within its allocated time?
- Which modules ran over? By how much?
- Which modules had excess time?
- Were breaks adequate?
- Was the overall workshop duration appropriate?

### Dimension 7: Activity Effectiveness (Pilot Only)
- For each practice activity: Did students achieve the intended outcome?
- Were instructions clear enough for students to begin without extra clarification?
- Was the scaffolding (guided → independent) progression smooth?
- Did differentiation tiers (floor/scaffold/extension) work as designed?
- Which activities should be kept, modified, or replaced?

### Dimension 8: Content Gaps (Pilot Only)
- Were there moments where students needed knowledge not yet covered?
- Were there topics included that turned out to be unnecessary?
- Did prerequisite assumptions hold (did students have the expected prior knowledge)?
- Were examples relevant and resonant with the actual audience?

### Dimension 9: Facilitation Difficulty (Pilot Only)
- Which sections were hardest to facilitate? Why?
- Were instructor notes sufficient?
- Were there unexpected questions the instructor wasn't prepared for?
- Did any transitions between modules feel abrupt or confusing?
```

**Step 4: Add pilot output format**

After the existing "## Output Format" section's closing ``` but before "## Error Handling", add:

```markdown
## Pilot Iteration Plan Output (--pilot only)

When `--pilot` is used, generate an additional file `04-materials/pilot-iteration-plan.md`:

```markdown
---
title: Pilot Iteration Plan - [Course Title]
pilotDate: [date of pilot, if known]
reportDate: YYYY-MM-DD
version: 0.1.0
status: action-required
iterationTarget: [date of next delivery, if known]
---

# Pilot Iteration Plan

## Course: [Course Title]
**Pilot Date:** [date]
**Generated:** [current date]
**Next Delivery Target:** [if known, or "TBD"]

---

## Pilot Summary

**Overall pilot assessment:** [READY FOR DELIVERY / NEEDS MINOR REVISIONS / NEEDS MAJOR REVISIONS / NEEDS REDESIGN]

**Key finding:** [1-2 sentence summary of the most important discovery from the pilot]

---

## Timing Reconciliation

| Module | Planned Duration | Actual Duration | Delta | Action |
|--------|-----------------|-----------------|-------|--------|
| Module 1: [Title] | [X] min | [Y] min | [+/- Z] min | [Keep / Adjust to [N] min / Split] |
| Module 2: [Title] | [X] min | [Y] min | [+/- Z] min | [Keep / Adjust to [N] min / Split] |

**Total planned:** [X] min | **Total actual:** [Y] min | **Delta:** [+/- Z] min

**Timing verdict:** [On track / Needs adjustment — specify which modules]

---

## Activity-by-Activity Assessment

### Module [N]: [Title]

| Activity | Effectiveness | Issue | Revision |
|----------|--------------|-------|----------|
| [Activity 1] | [Effective / Partially effective / Ineffective] | [What went wrong, if anything] | [Keep / Modify: specific change / Replace: with what] |
| [Activity 2] | [Effective / Partially effective / Ineffective] | [What went wrong, if anything] | [Keep / Modify: specific change / Replace: with what] |

[Repeat for each module]

---

## Content Gap Analysis

### Knowledge Gaps Discovered
| Gap | Where It Surfaced | Recommended Fix |
|-----|------------------|-----------------|
| [Missing concept] | [Module N, during activity X] | [Add to Module N instruction / Add as prerequisite / Add as pre-work] |

### Unnecessary Content
| Content | Why Unnecessary | Recommended Action |
|---------|----------------|-------------------|
| [Topic] | [Reason — audience already knew, not relevant, etc.] | [Remove / Condense / Move to extension challenge] |

---

## Facilitation Notes for Next Delivery

### Sections Requiring Extra Preparation
1. [Module/activity] — [Why it was difficult and what to prepare]
2. [Module/activity] — [Why it was difficult and what to prepare]

### Unexpected Questions to Prepare For
1. [Question] — [Suggested answer or resource]
2. [Question] — [Suggested answer or resource]

### Instructor Notes to Add/Update
1. [Location in lesson plans] — [Note to add]
2. [Location in lesson plans] — [Note to add]

---

## Prioritized Revision Plan

### Before Next Delivery (MUST DO)

| # | Revision | File to Modify | Effort |
|---|----------|---------------|--------|
| 1 | [Change] | [File path] | [Low/Medium/High] |
| 2 | [Change] | [File path] | [Low/Medium/High] |

### Before Next Delivery (SHOULD DO)

| # | Revision | File to Modify | Effort |
|---|----------|---------------|--------|
| 1 | [Change] | [File path] | [Low/Medium/High] |

### Future Iteration (NICE TO HAVE)

| # | Revision | File to Modify | Effort |
|---|----------|---------------|--------|
| 1 | [Change] | [File path] | [Low/Medium/High] |

---

## Version Recommendation

Based on pilot findings:
- **Recommended version bump:** [Patch / Minor / Major]
- **Rationale:** [Brief explanation]
- **Estimated revision effort:** [X hours]
```
```

**Step 5: Update error handling**

In the "## Error Handling" section, add after the existing entries:

```markdown
**Pilot mode without sufficient data:**
- If `--pilot` is used but feedback doesn't include timing or activity-level detail, warn: "⚠ Pilot mode works best with detailed per-module feedback. Missing: [timing data / activity-level observations / content gap notes]. The iteration plan will be generated with available data, but consider collecting more detailed feedback for the next pilot."
```

**Step 6: Commit**

```bash
git add course-curriculum-creator/commands/process-workshop-feedback.md
git commit -m "feat(commands): add --pilot flag to process-workshop-feedback for first-run analysis"
```

---

## Task 2: Add `content-sources.md` Template to `create-course`

**Files:**
- Modify: `commands/create-course.md`

**Step 1: Read current file**

Read `commands/create-course.md`.

**Step 2: Update directory structure**

In the "Create directory structure" section, add `content-sources.md` to the `01-planning/` directory:

Change:
```
├── 01-planning/
│   ├── course-positioning.md
│   ├── course-description.md
│   └── learning-objectives.md
```
To:
```
├── 01-planning/
│   ├── course-positioning.md
│   ├── course-description.md
│   ├── learning-objectives.md
│   └── content-sources.md
```

**Step 3: Update "Generate initial files" list**

In step 3 of Command Behavior, change:
```
3. **Generate initial files**:
   - `course-positioning.md` with YAML frontmatter and template content
   - `README.md` in project root with course overview
   - `.gitignore` (optional, based on settings)
```
To:
```
3. **Generate initial files**:
   - `course-positioning.md` with YAML frontmatter and template content
   - `content-sources.md` with tracking template (see File Generation section)
   - `README.md` in project root with course overview
   - `.gitignore` (optional, based on settings)
```

**Step 4: Add content-sources.md template**

After the existing "### 4. 04-materials/README.md" section, add:

```markdown
### 5. content-sources.md

```markdown
---
title: Content Sources & Licensing - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: tracking
lastUpdated: YYYY-MM-DD
---

# Content Sources & Licensing Tracker

## [Course Title]

**Purpose:** Track all third-party content, citations, and licensing requirements used in this course. Update this document whenever external content is incorporated into course materials.

**Why This Matters:** Professional course delivery requires clear attribution, license compliance, and awareness of content expiration. This tracker prevents IP violations and ensures materials can be legally distributed.

---

## Source Registry

[Add entries as content is incorporated during lesson plan and artifact development]

### Entry Template

| Field | Value |
|-------|-------|
| **Source Title** | [Title of source material] |
| **Author/Creator** | [Name or organization] |
| **Source Type** | [Book / Article / Video / Image / Framework / Tool / Dataset / Case Study / Software] |
| **URL/Location** | [Link or citation] |
| **License Type** | [CC-BY / CC-BY-SA / CC-BY-NC / MIT / Proprietary / Fair Use / Public Domain / Permission Granted] |
| **Usage in Course** | [Which module(s) and how it's used: quoted, adapted, referenced, screenshot] |
| **Attribution Required** | [Yes — exact text / No] |
| **Permission Status** | [Not needed / Requested / Granted / Denied] |
| **Expiration Date** | [If license or permission has a time limit, otherwise "None"] |
| **Notes** | [Any restrictions, conditions, or context] |

---

## Quick Reference: License Types

| License | Can Use in Course? | Can Distribute Handouts? | Attribution Needed? | Can Modify? |
|---------|-------------------|--------------------------|--------------------|----|
| **Public Domain** | Yes | Yes | No (but good practice) | Yes |
| **CC-BY** | Yes | Yes | Yes | Yes |
| **CC-BY-SA** | Yes | Yes (share-alike) | Yes | Yes (share-alike) |
| **CC-BY-NC** | Yes (if not charging) | Depends on fee structure | Yes | Yes |
| **Fair Use** | Limited (short excerpts) | Limited | Yes | Limited |
| **Proprietary** | Only with permission | Only with permission | Per agreement | No |
| **Permission Granted** | Per agreement | Per agreement | Per agreement | Per agreement |

---

## Frameworks & Models Used

[Track conceptual frameworks referenced in the course — these may have specific citation requirements]

| Framework/Model | Creator | Citation | License/Usage Notes |
|----------------|---------|----------|-------------------|
| [e.g., ADDIE Model] | [Creator] | [Proper citation] | [Public domain / Citation required / etc.] |

---

## Images, Diagrams & Media

[Track visual assets separately — these have stricter licensing requirements]

| Asset | Source | License | Used In | Attribution Text |
|-------|--------|---------|---------|-----------------|
| [Description] | [Source] | [License] | [Module/material] | [Required attribution] |

---

## Pre-Delivery Checklist

- [ ] All sources with "Permission Requested" status have been resolved
- [ ] All required attributions are included in course materials
- [ ] No expired licenses are in use
- [ ] Proprietary content has documented permission
- [ ] Handout distribution rights are confirmed for all included content
- [ ] Framework citations are accurate and complete

---

## Update Log

| Date | Change | Updated By |
|------|--------|-----------|
| [YYYY-MM-DD] | Initial tracker created | [Name] |
```
```

**Step 5: Update completion message**

In the "## Completion Message" section, add `content-sources.md` to the structure display:

Change:
```
  ├── 01-planning/
  │   ├── course-positioning.md (✓ initialized)
  │   ├── course-description.md (pending)
  │   └── learning-objectives.md (pending)
```
To:
```
  ├── 01-planning/
  │   ├── course-positioning.md (✓ initialized)
  │   ├── course-description.md (pending)
  │   ├── learning-objectives.md (pending)
  │   └── content-sources.md (✓ initialized)
```

**Step 6: Commit**

```bash
git add course-curriculum-creator/commands/create-course.md
git commit -m "feat(commands): add content-sources.md licensing tracker to create-course"
```

---

## Task 3: Add Content Source Prompts to `generate-lesson-plans`

**Files:**
- Modify: `commands/generate-lesson-plans.md`

**Step 1: Read current file**

Read `commands/generate-lesson-plans.md`.

**Step 2: Add content source reminder**

In the "## Post-Generation" section, after the existing validation block and before the `Prompt:` line, add:

```markdown
**Content Source Reminder:**
After generating lesson plans, check if any modules reference third-party content (frameworks, case studies, examples, tools, images). If so, prompt:

"Some modules reference external content. Would you like me to update `01-planning/content-sources.md` with source tracking entries for: [list referenced content]?"

If the user agrees, read `01-planning/content-sources.md` and append entries using the Source Registry entry template for each referenced source.
```

**Step 3: Commit**

```bash
git add course-curriculum-creator/commands/generate-lesson-plans.md
git commit -m "feat(commands): add content source tracking prompt to generate-lesson-plans"
```

---

## Task 4: Add Pilot Readiness and Content Licensing to Quality Reviewer

**Files:**
- Modify: `agents/quality-reviewer.md`

**Step 1: Read current file**

Read `agents/quality-reviewer.md`.

**Step 2: Add section 5d: Content Licensing Compliance**

After the existing "## 5c. Delivery Mode Validation" section, add:

```markdown
## 5d. Content Licensing Compliance

**Check curriculum for content licensing and attribution compliance:**

### Source Tracking
- Does `01-planning/content-sources.md` exist?
- Are all third-party frameworks, models, and case studies referenced in lesson plans tracked in content-sources.md?
- Are there untracked external references in lesson plans or artifacts?

### Attribution Completeness
- Do all sources with "Attribution Required: Yes" have attribution text in the relevant course materials (handouts, slides, instructor guide)?
- Are framework citations accurate and complete?

### License Compliance
- Are all sources marked with a valid license type?
- Are any "Permission Requested" entries still unresolved?
- Are any licenses expired or expiring before the next delivery?
- If course charges fees, are any CC-BY-NC sources being used improperly?

### Pre-Delivery Readiness
- Is the pre-delivery checklist in content-sources.md complete?
- Are there any "Denied" permission entries that require content removal?

**Document findings:**
- Rate content licensing compliance: COMPLIANT / PARTIALLY COMPLIANT / NON-COMPLIANT / NOT TRACKED
- Flag untracked external content references
- Flag unresolved permission requests
- Note upcoming license expirations
```

**Step 3: Add to report template**

In the "## 6. Generate Validation Report" section, after the "### Delivery Mode Validation" block, add:

```markdown
### Content Licensing Compliance
**Status**: PASS / FAIL / N/A

- Source tracking completeness
- Attribution accuracy in materials
- License compliance status
- Unresolved permissions or expirations
```

**Step 4: Update PASS criteria**

In the "# Quality Standards" section under "**PASS criteria for each stage:**", add:

```
- **Content Licensing**: All third-party content tracked in content-sources.md, attributions present in materials, no unresolved permissions, no expired licenses
```

**Step 5: Commit**

```bash
git add course-curriculum-creator/agents/quality-reviewer.md
git commit -m "feat(agents): add content licensing compliance to quality-reviewer"
```

---

## Task 5: Add Pilot and Content Phases to Curriculum Architect

**Files:**
- Modify: `agents/curriculum-architect.md`

**Step 1: Read current file**

Read `agents/curriculum-architect.md`.

**Step 2: Add Phase 9d: Content Source Tracking**

After the existing Phase 9c (Evaluation Planning) subsection, add:

```markdown
### Phase 9d: Content Source Tracking

After generating lesson plans and artifacts, review all modules for third-party content references:
1. Read `01-planning/content-sources.md`
2. Scan lesson plans and artifacts for external frameworks, case studies, examples, tools, or images
3. For each external reference found, add an entry to content-sources.md using the Source Registry template
4. Flag any sources that need permission or have unclear licensing
```

**Step 3: Update Phase 10 deliverables**

In Phase 10 (Deliverables & Handoff), add `content-sources.md` to the deliverables list:

Add to the existing deliverables list:
```
- `01-planning/content-sources.md` (populated with all third-party content references)
```

**Step 4: Commit**

```bash
git add course-curriculum-creator/agents/curriculum-architect.md
git commit -m "feat(agents): add content source tracking to curriculum-architect workflow"
```

---

## Task 6: Update README and Bump Version to 1.0.0

**Files:**
- Modify: `README.md`
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update plugin.json**

Change `"version": "0.6.0"` to `"version": "1.0.0"`.

**Step 2: Update README.md**

**a) What's New section**: Add v1.0.0 entry before v0.6.0:

```markdown
### v1.0.0 - Polish & Completeness
- Enhanced: `/process-workshop-feedback --pilot` flag for first-run pilot analysis with iteration planning
- Enhanced: `/create-course` now generates `content-sources.md` for IP/licensing tracking
- Enhanced: `/generate-lesson-plans` prompts for content source tracking after generation
- Enhanced: Quality reviewer validates content licensing compliance
- Enhanced: Curriculum architect tracks content sources in autonomous workflow
```

**b) Course Directory Structure section**: Add `content-sources.md` to the 01-planning/ directory listing:

Change:
```
├── 01-planning/
│   ├── course-positioning.md      # Market fit, audience, value proposition
│   ├── course-description.md      # Student-facing description
│   └── learning-objectives.md     # Bloom's-aligned outcomes
```
To:
```
├── 01-planning/
│   ├── course-positioning.md      # Market fit, audience, value proposition
│   ├── course-description.md      # Student-facing description
│   ├── learning-objectives.md     # Bloom's-aligned outcomes
│   └── content-sources.md         # Third-party content & licensing tracker
```

**Step 3: Commit**

```bash
git add course-curriculum-creator/README.md course-curriculum-creator/.claude-plugin/plugin.json
git commit -m "docs: update README and bump version to 1.0.0 for Phase 4 release"
```

---

## Task 7: Final Integration Verification

**Step 1: Verify all modified files have expected content**

```bash
# Check --pilot appears in process-workshop-feedback
grep -c "pilot" course-curriculum-creator/commands/process-workshop-feedback.md

# Check content-sources.md appears in create-course
grep -c "content-sources" course-curriculum-creator/commands/create-course.md

# Check content source prompt in generate-lesson-plans
grep -c "content-sources" course-curriculum-creator/commands/generate-lesson-plans.md

# Check 5d section in quality-reviewer
grep -c "5d" course-curriculum-creator/agents/quality-reviewer.md

# Check 9d phase in curriculum-architect
grep -c "9d" course-curriculum-creator/agents/curriculum-architect.md
```

**Step 2: Verify JSON and version**

```bash
python3 -c "import json; json.load(open('course-curriculum-creator/hooks/hooks.json')); print('hooks: VALID')"
python3 -c "import json; d=json.load(open('course-curriculum-creator/.claude-plugin/plugin.json')); print(f'version: {d[\"version\"]}')"
```
Expected: hooks VALID, version 1.0.0

**Step 3: Review git log**

```bash
git log --oneline 5888fd2..HEAD
git diff --stat 5888fd2..HEAD
```

---

## Summary of Phase 4 Deliverables

| # | Deliverable | Type | Files |
|---|---|---|---|
| 1 | `--pilot` flag in process-workshop-feedback | Command modification | `commands/process-workshop-feedback.md` |
| 2 | `content-sources.md` template in create-course | Command modification | `commands/create-course.md` |
| 3 | Content source tracking prompt in lesson plans | Command modification | `commands/generate-lesson-plans.md` |
| 4 | Content licensing validation in quality-reviewer | Agent modification | `agents/quality-reviewer.md` |
| 5 | Content source + pilot phases in curriculum-architect | Agent modification | `agents/curriculum-architect.md` |
| 6 | README + version bump to 1.0.0 | Documentation | `README.md`, `plugin.json` |
| 7 | Final integration verification | Verification | — |
