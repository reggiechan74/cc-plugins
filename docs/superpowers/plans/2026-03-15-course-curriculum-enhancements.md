# Course Curriculum Creator Enhancements Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 10 enhancements to the course-curriculum-creator plugin: 7 new files (3 commands, 4 references), 6 modified files (3 enhancements, 2 agent updates, 1 README), plus marketplace README and version bump.

**Architecture:** All additions are markdown content files following existing plugin conventions (YAML frontmatter, staleness checks, AskUserQuestion-driven workflows). New commands slot into the stage-numbered directory structure. Reference files go into `references/` subdirectories under their parent skills. Existing file modifications append new sections at documented anchor points.

**Tech Stack:** Markdown with YAML frontmatter. Claude Code plugin system (commands, skills, agents, references).

**Spec:** `docs/superpowers/specs/2026-03-15-course-curriculum-enhancements-design.md`

---

## Chunk 1: Reference Files

These have no dependencies on other new files and provide foundational material referenced by commands and skills.

### Task 1: Create formative-assessment-techniques reference

**Files:**
- Create: `course-curriculum-creator/skills/backward-design-methodology/references/formative-assessment-techniques.md`

- [ ] **Step 1: Verify parent directory exists**

Run: `ls course-curriculum-creator/skills/backward-design-methodology/references/`
Expected: `assessment-design.md` already present

- [ ] **Step 2: Write the formative-assessment-techniques.md file**

Create the file with content from spec Section 2.1. The file contains:
- Technique catalog table organized by cognitive level tier (Remember/Understand, Apply/Analyze, Evaluate/Create)
- Each technique entry: name, time, group size, description, what to look for, virtual equivalent
- Instructor decision rules table (>80% correct → proceed, 50-80% → re-teach, <50% → stop, bimodal → split)
- Technique selection guide (4 criteria: cognitive level, time, information needed, energy level)
- Integration guidance for generate-lesson-plans

- [ ] **Step 3: Verify file was created**

Run: `wc -l course-curriculum-creator/skills/backward-design-methodology/references/formative-assessment-techniques.md`
Expected: File exists, substantial line count

- [ ] **Step 4: Commit**

```bash
git add course-curriculum-creator/skills/backward-design-methodology/references/formative-assessment-techniques.md
git commit -m "feat(course-curriculum): add formative assessment techniques reference"
```

---

### Task 2: Create accessibility-specifications reference

**Files:**
- Create: `course-curriculum-creator/skills/universal-design-for-learning/references/accessibility-specifications.md`

- [ ] **Step 1: Verify parent directory exists, create if needed**

Run: `ls course-curriculum-creator/skills/universal-design-for-learning/references/ 2>/dev/null || mkdir -p course-curriculum-creator/skills/universal-design-for-learning/references/`

- [ ] **Step 2: Write the accessibility-specifications.md file**

Create the file with content from spec Section 2.2. The file contains:
- WCAG 2.1 AA color contrast requirements (4.5:1 normal, 3:1 large text, 3:1 non-text)
- Compliant color combinations table with specific hex values and ratios
- Color usage rules and contrast checking tools
- Typography: recommended accessible fonts table (Atkinson Hyperlegible, Source Sans Pro, Open Sans)
- Minimum sizes by context table (projected slides, printed handouts, digital docs)
- Spacing and layout specifications (1.5 line spacing, 50-75 char line length, left-aligned)
- Document accessibility checklist (structure, images, text content, PDF-specific)
- Slide accessibility checklist (titles, alt text, animations, reading order)
- Video/audio requirements (captions, transcripts, audio description)
- Quick 10-item compliance check for pre-delivery audit

- [ ] **Step 3: Verify file was created**

Run: `wc -l course-curriculum-creator/skills/universal-design-for-learning/references/accessibility-specifications.md`
Expected: File exists, substantial line count

- [ ] **Step 4: Commit**

```bash
git add course-curriculum-creator/skills/universal-design-for-learning/references/accessibility-specifications.md
git commit -m "feat(course-curriculum): add WCAG 2.1 AA accessibility specifications reference"
```

---

### Task 3: Create cultural-adaptation reference

**Files:**
- Create: `course-curriculum-creator/skills/universal-design-for-learning/references/cultural-adaptation.md`

- [ ] **Step 1: Ensure parent directory exists**

Run: `ls course-curriculum-creator/skills/universal-design-for-learning/references/ 2>/dev/null || mkdir -p course-curriculum-creator/skills/universal-design-for-learning/references/`

- [ ] **Step 2: Write the cultural-adaptation.md file**

Create the file with content from spec Section 2.3. The file contains:
- Examples & case studies: selection principles, "what to avoid" table (sports metaphors, pop culture, currency, holidays), case study adaptation 5-step process
- Communication norms: feedback/participation styles table (direct vs. indirect, individual vs. group, power distance, uncertainty avoidance, face-saving), activity adjustments per dimension
- Time & pacing: factor/consideration/adaptation table (punctuality, break expectations, pace of discourse, meeting duration)
- Localization checklist: content items (currency, regulations, dates, units, images) and language items (idioms, acronyms, reading level, terminology, glossary) and facilitation items (cultural appropriateness, anonymous feedback, hierarchy, timing)

- [ ] **Step 3: Verify file was created**

Run: `wc -l course-curriculum-creator/skills/universal-design-for-learning/references/cultural-adaptation.md`
Expected: File exists

- [ ] **Step 4: Commit**

```bash
git add course-curriculum-creator/skills/universal-design-for-learning/references/cultural-adaptation.md
git commit -m "feat(course-curriculum): add cultural adaptation guide reference"
```

---

### Task 4: Create content-curation reference

**Files:**
- Create: `course-curriculum-creator/skills/backward-design-methodology/references/content-curation.md`

- [ ] **Step 1: Write the content-curation.md file**

Create the file with content from spec Section 2.4. The file contains:
- RARBA evaluation framework table (Recency, Authority, Relevance, Bias, Accessibility) with scoring guide (13-15 include, 10-12 caveats, 7-9 consider alternatives, <7 exclude)
- Case study selection: real vs. fictional vs. anonymized vs. participant-generated comparison table
- Adapting published case studies: 6-step process
- Framework attribution: common frameworks table (Porter's, SWOT, Bloom's, Design Thinking, Agile, Kirkpatrick) with minimum attribution guidance
- Citation style for training materials (simplified, not full APA)
- Source types comparison table (academic, industry reports, trade publications, news, blogs, vendor, Wikipedia)
- Red flags checklist (10 items: single source claims, outdated data, vendor marketing, no author, circular citations, survivorship bias, absolute claims, paywalled, copyrighted images, outdated UI)

- [ ] **Step 2: Verify file was created**

Run: `wc -l course-curriculum-creator/skills/backward-design-methodology/references/content-curation.md`
Expected: File exists

- [ ] **Step 3: Commit**

```bash
git add course-curriculum-creator/skills/backward-design-methodology/references/content-curation.md
git commit -m "feat(course-curriculum): add content curation guide reference"
```

---

## Chunk 2: Enhancements to Existing Files

These append new sections to existing files at documented anchor points. No dependencies on new commands.

### Task 5: Add affective domain section to Bloom's taxonomy skill

**Files:**
- Modify: `course-curriculum-creator/skills/blooms-taxonomy/SKILL.md`

- [ ] **Step 1: Read the file to locate insertion point**

Read `course-curriculum-creator/skills/blooms-taxonomy/SKILL.md` and find the `## Intensive Workshop Considerations` heading. The new section inserts BEFORE this heading (after `## Scaffolding Strategies` section ends).

- [ ] **Step 2: Append the affective domain section**

Insert the `## Affective Domain (Krathwohl's Taxonomy)` section from spec Section 3.1 before `## Intensive Workshop Considerations`. Content includes:
- When to use / when NOT to use affective objectives
- Five affective levels (Receiving, Responding, Valuing, Organizing, Characterizing) each with: definition, action verbs, example objectives, instructional strategies, assessment approach
- Pairing cognitive and affective objectives table (3 examples)
- Workshop considerations: quantity limits (1-2), level ceiling (Receiving/Responding/Valuing), assessment approach (no quizzes), integration with `/generate-objectives`

- [ ] **Step 3: Verify the file is well-formed**

Run: `grep -c "^## " course-curriculum-creator/skills/blooms-taxonomy/SKILL.md`
Expected: One more heading than before (the new `## Affective Domain` section added)

- [ ] **Step 4: Commit**

```bash
git add course-curriculum-creator/skills/blooms-taxonomy/SKILL.md
git commit -m "feat(course-curriculum): add affective domain (Krathwohl's taxonomy) to Bloom's skill"
```

---

### Task 6: Add co-facilitation support to generate-lesson-plans

**Files:**
- Modify: `course-curriculum-creator/commands/3-learning-plan/generate-lesson-plans.md`

- [ ] **Step 1: Read the file to locate insertion point**

Read `course-curriculum-creator/commands/3-learning-plan/generate-lesson-plans.md` and find the `## Delivery Mode Adaptations` section. The new section appends AFTER the final `---` separator that follows that section, just before the closing paragraph.

- [ ] **Step 2: Append the co-facilitation section**

Insert the `## Co-Facilitation Support` section from spec Section 3.2 after `## Delivery Mode Adaptations`. Content includes:
- `--facilitators N` argument (default: 1)
- Per-module role table template (Lead, Support, Observer)
- Role rotation guidance (alternate every 2-3 modules)
- Handoff protocol template (timing status, energy, unresolved questions, struggling learners, misconceptions)
- Split instructor notes (Lead Notes + Support Notes)
- Co-facilitation planning checklist (6 items)

- [ ] **Step 3: Verify the section was added**

Run: `grep "Co-Facilitation Support" course-curriculum-creator/commands/3-learning-plan/generate-lesson-plans.md`
Expected: Match found

- [ ] **Step 4: Commit**

```bash
git add course-curriculum-creator/commands/3-learning-plan/generate-lesson-plans.md
git commit -m "feat(course-curriculum): add co-facilitation support to generate-lesson-plans"
```

---

### Task 7: Add inter-course transition design to design-series

**Files:**
- Modify: `course-curriculum-creator/commands/0-analysis/design-series.md`

- [ ] **Step 1: Read the file to locate insertion point**

Read `course-curriculum-creator/commands/0-analysis/design-series.md` and find `## Settings Integration`. The new section inserts BEFORE `## Settings Integration` (after `## Output Format` section ends).

- [ ] **Step 2: Append the inter-course transition section**

Insert the `## Inter-Course Transition Design` section from spec Section 3.3 before `## Settings Integration`. Content includes:
- Retention bridge: review module (15-20 min), prerequisite concept map table, recommended time gaps table
- Placement assessment: length (5-8 questions), format (scenario-based), passing threshold (80%), result interpretation, template
- Bridge assignments: post-N / pre-N+1 activity table, design principles (4 items), total bridge time cap (2 hours)
- Series plan output addition: transition section template with review module, placement assessment, bridge activities, recommended gap

- [ ] **Step 3: Verify the section was added**

Run: `grep "Inter-Course Transition Design" course-curriculum-creator/commands/0-analysis/design-series.md`
Expected: Match found

- [ ] **Step 4: Commit**

```bash
git add course-curriculum-creator/commands/0-analysis/design-series.md
git commit -m "feat(course-curriculum): add inter-course transition design to design-series"
```

---

## Chunk 3: New Commands

Three new command files. Each follows existing command conventions (YAML frontmatter with name, description, argument-hint, allowed-tools).

### Task 8: Create generate-learner-profile command

**Files:**
- Create: `course-curriculum-creator/commands/0-analysis/generate-learner-profile.md`

- [ ] **Step 1: Write the generate-learner-profile.md file**

Create the file with full content from spec Section 1.1. The file contains:
- YAML frontmatter: name, description, argument-hint (`[--from-tna]`), allowed-tools (AskUserQuestion, Bash, Read, Write, Edit)
- Command behavior: 5 interactive dimensions (prior knowledge, motivational drivers, learning preferences, transfer environment, resistance points)
- Each dimension: specific AskUserQuestion prompts with multiple-choice options where possible
- Pre-population from course-positioning.md and TNA when available
- Design Implications section generation (finding → curriculum impact → action table)
- Output format: full markdown template with YAML frontmatter (sourceFiles, sourceHashes), 6 sections with tables
- Integration points section (lesson-plans, transfer-plan, pre-work, quality-reviewer, curriculum-architect)
- Error handling: no course directory, missing positioning, skipped sections
- Settings integration from `.claude/course-curriculum-creator.local.md`
- Implementation notes: date retrieval, path handling, DO NOT list

- [ ] **Step 2: Verify file was created and has expected structure**

Run: `grep -c "^## \|^### " course-curriculum-creator/commands/0-analysis/generate-learner-profile.md`
Expected: Multiple section headings present

- [ ] **Step 3: Commit**

```bash
git add course-curriculum-creator/commands/0-analysis/generate-learner-profile.md
git commit -m "feat(course-curriculum): add /generate-learner-profile command"
```

---

### Task 9: Create generate-pre-work command

**Files:**
- Create: `course-curriculum-creator/commands/3-learning-plan/generate-pre-work.md`

- [ ] **Step 1: Write the generate-pre-work.md file**

Create the file with full content from spec Section 1.2. The file contains:
- YAML frontmatter: name, description, argument-hint (`[--format full|micro-only|emails-only]`), allowed-tools (Bash, Read, Write, Edit, Skill)
- Prerequisites: learning-objectives.md required, learner-profile.md optional
- Staleness check section (same md5 hash pattern as other commands)
- Command behavior: load blooms-taxonomy skill, read objectives (identify Remember/Understand + implied prerequisites from Apply+), read learner profile, design micro-learning units
- Micro-learning unit design rules: max 3 units, max 30 min total, 10-15 min each, two paths (fast track 2-3 min, full path 10-15 min), dependency ordering
- Readiness self-assessment: 5-8 questions, answer key, score interpretation
- Email templates: T-7 days welcome, T-2 days reminder
- Format options section (full, micro-only, emails-only)
- Output format: full markdown template with YAML frontmatter including totalEstimatedTime, sourceFiles, sourceHashes
- Validation checks: time cap (30 min warning), objective mapping, self-assessment matches prerequisites, fast track exists
- Integration points: lesson-plans (adjust Day 1 Module 1), workshop-prep (T-14/T-7/T-2/T-1 checklist), curriculum-architect (Phase 7.5)
- Error handling: missing objectives, no Remember/Understand objectives, pre-work already exists
- Implementation notes: date retrieval, DO NOT list

- [ ] **Step 2: Verify file was created**

Run: `grep -c "^## \|^### " course-curriculum-creator/commands/3-learning-plan/generate-pre-work.md`
Expected: Multiple section headings present

- [ ] **Step 3: Commit**

```bash
git add course-curriculum-creator/commands/3-learning-plan/generate-pre-work.md
git commit -m "feat(course-curriculum): add /generate-pre-work command"
```

---

### Task 10: Create generate-spaced-practice command

**Files:**
- Create: `course-curriculum-creator/commands/6-delivery/generate-spaced-practice.md`

- [ ] **Step 1: Write the generate-spaced-practice.md file**

Create the file with full content from spec Section 1.3. The file contains:
- YAML frontmatter: name, description, argument-hint (`[--format email|flashcards|lms|all] [--intervals custom]`), allowed-tools (Bash, Read, Write, Edit, Skill)
- Prerequisites: learning-objectives.md required, lesson-plans.md recommended, rubrics.md optional
- Staleness check section
- Command behavior: load blooms-taxonomy skill, read objectives + lesson plans + rubrics, generate 3-5 retrieval questions per module
- Question design rules: match Bloom's level, include answer keys with explanations, mix formats by level (MC for Remember, scenario for Apply, pattern-finding for Analyze, justification for Evaluate)
- Schedule: expanding intervals (Day 1, 3, 7, 14, 30), 3-5 questions per session, max 5 min each, module cycling, later sessions interleave
- Format options: email (with reveal-answer sections), flashcards (Anki-compatible), LMS (quiz import structure), all
- Custom intervals option
- Output format: full markdown template with YAML frontmatter (format, intervals, totalQuestions, sourceFiles, sourceHashes), question bank organized by module, practice sessions organized by day, format-specific output sections
- Validation checks: 2+ questions per module, no off-curriculum questions, Bloom's level match, <5 min per session, all modules represented
- Integration points: transfer-plan (merge into follow-up schedule), evaluation-plan (completion rates as L2 data), curriculum-architect (Phase 9e)
- Error handling: missing objectives, missing lesson plans (advisory), already exists
- Implementation notes

- [ ] **Step 2: Verify file was created**

Run: `grep -c "^## \|^### " course-curriculum-creator/commands/6-delivery/generate-spaced-practice.md`
Expected: Multiple section headings present

- [ ] **Step 3: Commit**

```bash
git add course-curriculum-creator/commands/6-delivery/generate-spaced-practice.md
git commit -m "feat(course-curriculum): add /generate-spaced-practice command"
```

---

## Chunk 4: Agent Integration Updates and README

Update the two agents to reference new commands/artifacts, and update the README to document all additions.

### Task 11: Update curriculum-architect agent

**Files:**
- Modify: `course-curriculum-creator/agents/curriculum-architect.md`

- [ ] **Step 1: Read the agent file to understand current phase structure**

Read `course-curriculum-creator/agents/curriculum-architect.md`. Identify:
- Phase 3 (Course Initialization) — new Phase 3.5 goes after this
- Phase 7 (Detailed Lesson Plans) — new Phase 7.5 goes after this
- Phase 9c (Evaluation Planning) — new Phase 9e goes after this
- Phase 10 (Deliverables) — update file list

- [ ] **Step 2: Add Phase 3.5 — Learner Profile**

After Phase 3 (Course Initialization), insert:

```markdown
## Phase 3.5: Learner Profile (Optional)

If sufficient audience information is available from Phase 1 requirements or TNA:

Read `${CLAUDE_PLUGIN_ROOT}/commands/0-analysis/generate-learner-profile.md` using the Read tool.
Follow its instructions to generate a learner profile analyzing prior knowledge, motivational drivers, learning constraints, transfer environment, and resistance points.

If learner information is limited, skip this phase — it can be generated later when more audience data is available.
```

- [ ] **Step 3: Add Phase 7.5 — Pre-Work Materials**

After Phase 7 (Detailed Lesson Plans), insert:

```markdown
## Phase 7.5: Pre-Work Materials (If Applicable)

If learning objectives include Remember or Understand-level prerequisites that could be covered before Day 1:

Read `${CLAUDE_PLUGIN_ROOT}/commands/3-learning-plan/generate-pre-work.md` using the Read tool.
Follow its instructions to design micro-learning units covering prerequisite knowledge.

Skip if all objectives are at Apply level or higher with no implied prerequisites.
```

- [ ] **Step 4: Add Phase 9e — Spaced Practice**

After Phase 9c (Evaluation Planning) or Phase 9d (Content Source Tracking), insert:

```markdown
### Phase 9e: Spaced Practice Sequence

Read `${CLAUDE_PLUGIN_ROOT}/commands/6-delivery/generate-spaced-practice.md` using the Read tool.
Follow its instructions to generate:
- 3-5 retrieval questions per module at appropriate Bloom's level
- Expanding interval schedule (Day 1, 3, 7, 14, 30)
- Email format for delivery
```

- [ ] **Step 5: Update Phase 10 deliverables list**

In the Phase 10 summary report template, add to the "## Generated Files" list:

```markdown
10. `01-planning/learner-profile.md` — Learner profile (if generated)
11. `04-materials/pre-work.md` — Pre-work materials (if applicable)
12. `04-materials/spaced-practice.md` — Spaced retrieval practice sequence
```

- [ ] **Step 6: Commit**

```bash
git add course-curriculum-creator/agents/curriculum-architect.md
git commit -m "feat(course-curriculum): add learner profile, pre-work, and spaced practice phases to curriculum-architect"
```

---

### Task 12: Update quality-reviewer agent

**Files:**
- Modify: `course-curriculum-creator/agents/quality-reviewer.md`

- [ ] **Step 1: Read the agent file to understand current validation structure**

Read `course-curriculum-creator/agents/quality-reviewer.md`. Identify:
- Section 4 (Stage 3 Validation: Learning Activities) — add learner profile check
- Section 5 (Overall Coherence Check) — add affective objective check
- After Section 5d (Content Licensing Compliance) — add Section 5e

- [ ] **Step 2: Add learner profile check to Stage 3 Validation**

In Section 4 (Stage 3 Validation), under the `### Differentiation` subsection, add:

```markdown
### Learner Profile Alignment
- If `01-planning/learner-profile.md` exists:
  - Do differentiation tiers match profile findings? (e.g., if profile shows mixed skill levels, are floor/scaffold/extension tiers meaningfully different?)
  - Do examples and scenarios match the audience's domain context from the profile?
  - Does the transfer plan account for the transfer environment assessment?
  - If profile identifies resistance points, are they addressed in module introductions?
```

- [ ] **Step 3: Add affective objective check to Overall Coherence**

In Section 5 (Overall Coherence Check), under `### Horizontal Consistency`, add:

```markdown
### Affective Objective Validation
- If learning objectives include affective objectives (Krathwohl's taxonomy):
  - Are affective objectives paired with related cognitive objectives?
  - Do affective objectives use appropriate assessment methods (reflection, observation, attitude scales — NOT quizzes)?
  - Are affective objectives limited to Receiving/Responding/Valuing levels for 1-2 day workshops?
  - Is the total count of affective objectives 1-2 maximum?
```

- [ ] **Step 4: Add Section 5e — Pre-Work Validation**

After Section 5d (Content Licensing Compliance), add:

```markdown
## 5e. Pre-Work Validation (if applicable)

**Check pre-work materials for quality and alignment:**

### Coverage
- Does pre-work map to specific objectives or prerequisites?
- Are Remember/Understand prerequisites that could be pre-work actually covered in pre-work?
- Does Day 1 Module 1 adjust for pre-work content (not re-teaching)?

### Design Quality
- Is total pre-work time 30 minutes or less?
- Does every unit have both a fast track and full path?
- Are self-assessment questions aligned with prerequisite concepts?
- Are email templates provided for T-7 and T-2 distribution?

### Spaced Practice Validation (if applicable)
- Do retrieval questions match the Bloom's level of their module's objective?
- Is every module represented in the question bank?
- Are practice sessions completable in under 5 minutes each?
- Do later sessions interleave questions across modules?

**Document findings:**
- Rate pre-work quality: STRONG / ADEQUATE / NEEDS IMPROVEMENT / NOT PRESENT
- Flag any pre-work that exceeds 30-minute time cap
- Flag modules without corresponding spaced practice questions
```

- [ ] **Step 5: Update quality ratings**

In the `## Quality Standards` section, update the PASS criteria to include:

```markdown
- **Pre-Work (if exists)**: Maps to prerequisites, under 30 min, fast track + full path, email templates present
- **Spaced Practice (if exists)**: Questions match Bloom's levels, all modules covered, sessions under 5 min
```

- [ ] **Step 6: Commit**

```bash
git add course-curriculum-creator/agents/quality-reviewer.md
git commit -m "feat(course-curriculum): add learner profile, affective, and pre-work validation to quality-reviewer"
```

---

### Task 13: Update plugin README

**Files:**
- Modify: `course-curriculum-creator/README.md`

- [ ] **Step 1: Add new commands to Stage 0 table**

In the `### Stage 0: Analysis & Initialization` table, add a row:

```markdown
| `/generate-learner-profile` | Generate learner profile analyzing prior knowledge, motivations, constraints, and transfer environment |
```

- [ ] **Step 2: Add new command to Stage 3 table**

In the `### Stage 3: Learning Plan` table, add a row:

```markdown
| `/generate-pre-work` | Design pre-workshop micro-learning units covering prerequisites |
```

- [ ] **Step 3: Add new command to Stage 6 table**

In the `### Stage 6: Delivery & Iteration` table, add a row:

```markdown
| `/generate-spaced-practice` | Generate post-workshop spaced retrieval practice sequence |
```

- [ ] **Step 4: Update each skill entry with reference file mentions**

Under `### backward-design-methodology`, add to the bullet list:
```markdown
- Reference files: assessment design, formative assessment techniques, content curation
```

Under `### blooms-taxonomy`, add:
```markdown
- Affective domain support (Krathwohl's taxonomy) for attitude-change objectives
```

Under `### universal-design-for-learning`, add:
```markdown
- Reference files: accessibility specifications (WCAG 2.1 AA), cultural adaptation guide
```

- [ ] **Step 5: Update Features list**

Add to the `## Features` list:

```markdown
- **Learner Analysis**: Generate learner profiles with prior knowledge, motivations, and transfer environment
- **Pre-Work Design**: Micro-learning units with fast track/full path for prerequisite coverage
- **Spaced Practice**: Post-workshop retrieval practice at expanding intervals to combat forgetting curve
- **Affective Objectives**: Krathwohl's taxonomy support for attitude-change workshops
- **Co-Facilitation**: Multi-facilitator support with role rotation and handoff protocols
- **Accessibility Standards**: WCAG 2.1 AA specifications for training materials
- **Cultural Adaptation**: Localization guidance for cross-cultural delivery
- **Content Curation**: RARBA framework for evaluating third-party content quality
- **Series Transitions**: Inter-course retention bridges, placement assessments, and bridge assignments
```

- [ ] **Step 6: Add What's New entry**

Add a new version entry at the top of `## What's New`:

```markdown
### v1.1.0 - Learner Analysis, Retention & Inclusivity
- New: `/generate-learner-profile` command for audience analysis across 5 dimensions
- New: `/generate-pre-work` command for micro-learning prerequisite coverage
- New: `/generate-spaced-practice` command for post-workshop retrieval practice
- New: Formative assessment techniques reference with decision rules
- New: WCAG 2.1 AA accessibility specifications reference
- New: Cultural adaptation guide for cross-cultural delivery
- New: Content curation guide with RARBA evaluation framework
- New: Affective domain (Krathwohl's taxonomy) in Bloom's skill
- Enhanced: Co-facilitation support in `/generate-lesson-plans` with role rotation and handoff protocols
- Enhanced: Inter-course transition design in `/design-series` with retention bridges and placement assessments
- Enhanced: Curriculum architect generates learner profiles, pre-work, and spaced practice
- Enhanced: Quality reviewer validates learner profiles, affective objectives, pre-work, and spaced practice
```

- [ ] **Step 7: Update course directory structure**

In the `## Course Directory Structure` section, add new files:

```markdown
├── 01-planning/
│   ├── course-positioning.md
│   ├── course-description.md
│   ├── learning-objectives.md
│   ├── learner-profile.md          # Audience analysis (optional)
│   └── content-sources.md
├── 02-design/
│   ├── course-outline.md
│   └── lesson-plans.md
├── 03-assessment/
│   └── rubrics.md
└── 04-materials/
    ├── pre-work.md                 # Pre-workshop micro-learning (optional)
    ├── spaced-practice.md          # Post-workshop retrieval practice (optional)
    └── [other artifacts]
```

- [ ] **Step 8: Commit**

```bash
git add course-curriculum-creator/README.md
git commit -m "docs(course-curriculum): update README with new commands, features, and v1.1.0 changelog"
```

---

### Task 14: Update marketplace README

**Files:**
- Modify: `README.md` (repo root)

- [ ] **Step 1: Update course-curriculum-creator description in repo README**

Find the `### course-curriculum-creator` section in the repo root README.md. Add the new commands to the commands list and add key new features to the features list.

Add to **Features:**
```markdown
- Learner profile generation for audience analysis
- Pre-work micro-learning units with fast track/full path options
- Post-workshop spaced retrieval practice to combat forgetting curve
- Affective domain (Krathwohl's taxonomy) for attitude-change objectives
- WCAG 2.1 AA accessibility specifications
- Co-facilitation support with role rotation and handoff protocols
```

Add to **Commands:**
```markdown
- `/generate-learner-profile` - Audience analysis across 5 dimensions
- `/generate-pre-work` - Pre-workshop micro-learning prerequisites
- `/generate-spaced-practice` - Post-workshop spaced retrieval practice
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update marketplace README with course-curriculum-creator v1.1.0 features"
```

---

### Task 15: Update plugin version

**Files:**
- Modify: `course-curriculum-creator/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Read current plugin.json**

Read `course-curriculum-creator/.claude-plugin/plugin.json` to confirm current version.

- [ ] **Step 2: Bump version to 1.1.0 in plugin.json**

Update the `version` field from `"1.0.0"` to `"1.1.0"`.

- [ ] **Step 3: Bump version in marketplace.json**

Read `.claude-plugin/marketplace.json`, find the `course-curriculum-creator` entry, update version from `"1.0.0"` to `"1.1.0"`.

- [ ] **Step 4: Commit**

```bash
git add course-curriculum-creator/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore(course-curriculum): bump version to 1.1.0"
```
