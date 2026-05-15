# L&D Gap Analysis: Course Curriculum Creator Plugin

**Date:** 2026-02-23
**Reviewer:** Expert Learning Development Manager Perspective
**Plugin Version:** 0.3.0
**Status:** Design Document (Roadmap)

---

## Executive Summary

The course-curriculum-creator plugin has a **strong pedagogical core** (75-80% complete) built on Understanding by Design (UbD) and Bloom's Revised Taxonomy. The command flow enforces correct instructional design sequencing through hooks, the Bloom's integration provides practical cognitive-level guidance, and the series architecture supports sophisticated multi-course progression.

What separates this from a **complete professional L&D system** are gaps in the organizational ecosystem surrounding course design: needs analysis upstream, accessibility throughout, transfer and evaluation downstream, and delivery mode flexibility.

This document catalogs all identified gaps with severity ratings, proposed approaches, trade-offs, and recommendations.

---

## Current Strengths

| Dimension | Rating | Notes |
|---|---|---|
| Pedagogical Framework (UbD) | **A+** | Deeply embedded, hook-enforced sequencing |
| Cognitive Taxonomy (Bloom's) | **A+** | Realistic time estimates, verb tables, scaffolding guidance |
| Assessment Design | **A** | Analytical rubrics, alignment matrices, embedded assessment |
| Course Sequencing (Series) | **A** | Bloom's Center-of-Gravity model, handoff mechanisms |
| Quality Assurance | **A** | Multi-stage validation, staleness detection (MD5), dedicated agent |
| Template/Reuse System | **A** | Full lifecycle: save, parameterize, restore, customize |
| Materials Generation | **A-** | 7 artifact types covering student and instructor needs |
| Feedback Processing | **B+** | 5-dimension analysis, prioritized action items |

---

## Gap Analysis

### Gap 1: Training Needs Assessment (TNA)

**Severity: CRITICAL**

**Current State:** Plugin starts at `create-course` (positioning: audience, value proposition, differentiation). No formal needs analysis step exists. Assumes the decision to build a course has already been made.

**Impact:** Without TNA, courses risk solving the wrong problem. The performance gap may stem from process issues, environmental factors, or motivation rather than a skills deficit. An L&D manager would never greenlight course development without a documented needs analysis.

#### Approaches

**A. Dedicated `assess-needs` command (Recommended)**
- New command producing `training-needs-analysis.md`
- Workflow: business problem -> performance gap -> root cause analysis (skills? motivation? environment?) -> training vs. non-training solutions -> target population analysis -> success metrics
- Output feeds into `create-course` as a prerequisite
- Add hook: can't `create-course` without a TNA or explicit `--skip-tna` flag
- Trade-off: Adds one step before design. Some users may find it bureaucratic for small workshops.

**B. Embed TNA into `create-course` as expanded first step**
- Expand `course-positioning.md` template with needs analysis fields
- Add sections: business driver, current state, desired state, gap analysis, training justification
- Trade-off: Conflates marketing (positioning) with diagnostics (needs analysis).

**C. Optional TNA skill (advisory only)**
- Skill guiding needs analysis thinking, loaded by curriculum-architect agent
- No enforced prerequisite
- Trade-off: Loses the enforcement that makes the plugin's UbD flow strong. Likely to be skipped.

**Recommendation:** Approach A. The plugin's strongest feature is enforcing correct sequencing. A TNA command maintains that discipline at the most critical decision point.

---

### Gap 2: Accessibility & Universal Design for Learning (UDL)

**Severity: CRITICAL**

**Current State:** Zero mention of accessibility, UDL principles, ADA/Section 508 compliance, or diverse learner needs. No guidance on multiple means of representation, engagement, or expression. No accommodation planning.

**Impact:** In professional L&D, accessibility is non-negotiable. Organizations face legal liability (ADA, Section 508, EU Accessibility Act). Beyond compliance, UDL improves learning for everyone. This is the single biggest professional credibility gap.

#### Approaches

**A. UDL skill + accessibility integration into existing commands (Recommended)**
- New skill: `universal-design-for-learning/SKILL.md`
  - Three UDL principles: Multiple Means of Representation, Engagement, Action & Expression
  - Practical guidance per principle for workshop contexts
  - Accommodation planning templates
- Modify `generate-outline`: UDL checkpoints per module ("Does this module offer at least 2 representation modes?")
- Modify `generate-lesson-plans`: accessibility considerations per activity
- Add UDL validation dimension to `quality-reviewer` agent
- Trade-off: Adds review criteria and slightly longer output. Worth it for professional credibility.

**B. Standalone `accessibility-review` command**
- Post-hoc review scanning curriculum for accessibility gaps
- Checks: single-modality activities, text-only assessments, timed activities without accommodations
- Trade-off: Post-hoc means accessibility is retrofitted, not designed-in. Violates UDL principle of "design for the margins from the start."

**C. Accessibility section in backward-design-methodology skill**
- Add UDL as a subsection of Stage 3 (Plan Learning Experiences)
- Trade-off: Minimal structural change but underweights accessibility by burying it.

**Recommendation:** Approach A. UDL is a design philosophy, not a checklist. It deserves its own skill with practical integration into activity and assessment commands.

---

### Gap 3: Transfer of Learning & Action Planning

**Severity: HIGH**

**Current State:** No command or guidance for post-workshop application. `post-assessment.md` artifact measures learning gains but doesn't bridge to workplace application. No action plans, manager briefings, follow-up touchpoints, job aids, or performance support tools.

**Impact:** The "forgetting curve" is brutal: 70% of training content is forgotten within 24 hours without reinforcement. Kirkpatrick Level 3 (behavior change) is what organizations actually pay for. A workshop without transfer mechanisms is entertainment, not training.

#### Approaches

**A. Dedicated `generate-transfer-plan` command (Recommended)**
- Generates `transfer-plan.md` with:
  - 30/60/90-day action plan template for learners
  - Manager briefing document (what was covered, how to reinforce)
  - Job aids / quick reference cards per key skill
  - Follow-up touchpoint schedule (email reminders, check-in questions)
  - Performance support tools (decision trees, checklists for on-the-job use)
- Derived from learning objectives: each objective maps to specific transfer activities
- Trade-off: Extends scope beyond "workshop creation" into "learning ecosystem." This is what separates professional L&D.

**B. Expand `generate-artifacts` with transfer-focused types**
- Add `--type job-aid`, `--type manager-brief`, `--type action-plan`
- Trade-off: Simpler implementation but transfer planning is conceptually different from materials creation.

**C. Add transfer section to lesson plans**
- Final module includes "Application Planning" section
- Trade-off: Only covers in-session planning, not post-workshop reinforcement.

**Recommendation:** Approach A. Transfer is a distinct phase of the learning lifecycle deserving its own command.

---

### Gap 4: Kirkpatrick Evaluation Model (Levels 3 & 4)

**Severity: HIGH**

**Current State:** Current evaluation covers Level 1 (Reaction: `course-evaluation.md`) and Level 2 (Learning: `post-assessment.md`). No support for Level 3 (Behavior: did they apply on the job?) or Level 4 (Results: did it impact business outcomes?).

**Impact:** L&D managers are increasingly accountable for demonstrating ROI. "Learners liked the workshop" (L1) and "they passed the quiz" (L2) don't answer "was this worth the investment?"

#### Approaches

**A. Dedicated `generate-evaluation-plan` command (Recommended)**
- Creates comprehensive `evaluation-plan.md` covering all 4 levels:
  - L1 (Reaction): Reference existing course-evaluation.md
  - L2 (Learning): Reference existing pre/post-assessment.md
  - L3 (Behavior): 30/60/90-day observation templates, manager check-in questions, self-report surveys, on-the-job performance checklists
  - L4 (Results): Business metric identification, baseline measurement plan, post-training comparison methodology, ROI calculation template
- Each objective maps to specific L3/L4 indicators
- Trade-off: L3/L4 measurement requires organizational cooperation beyond the designer's control. Plugin generates the plan but can't guarantee execution.

**B. Extend `process-workshop-feedback` to handle multi-level data**
- Accept L3 follow-up survey data and L4 business metrics
- Trade-off: Conflates immediate feedback with longitudinal evaluation.

**Recommendation:** Approach A. Evaluation planning should happen during design (backward design principle), not as an afterthought.

---

### Gap 5: Virtual/Hybrid Delivery Adaptation

**Severity: HIGH**

**Current State:** Entire plugin assumes in-person delivery. No guidance for virtual workshops (Zoom/Teams), hybrid formats, or asynchronous components.

**Impact:** Post-2020, virtual and hybrid delivery is standard. A 1-day in-person workshop cannot be delivered as a 1-day virtual workshop without significant adaptation (shorter sessions, more breaks, different engagement techniques, tech considerations).

#### Approaches

**A. Delivery mode as first-class parameter (Recommended)**
- Add `--mode in-person|virtual|hybrid` to `create-course`
- Mode-specific defaults propagate through all commands:
  - **Virtual:** Max 4-hour sessions, 10-min breaks every 45 min, breakout rooms replace table groups, digital whiteboard exercises, engagement polls every 15-20 min, tech check requirements
  - **Hybrid:** Dual-experience design, camera placement, equity between in-room and remote participants
  - **In-person:** Current behavior (default)
- New skill: `virtual-facilitation/SKILL.md` with platform-specific guidance
- Outline and lesson plan templates adapt per mode
- Trade-off: Significant implementation effort. Essentially triples the design surface area.

**B. Post-hoc `adapt-for-virtual` command**
- Takes existing in-person curriculum and generates a virtual adaptation
- Adjusts timing, suggests activity substitutions, adds tech requirements
- Trade-off: Adaptation is inferior to designing for the medium from the start. But pragmatic for converting existing courses.

**C. Virtual considerations as a section in backward-design skill**
- Advisory guidance, not enforced structural changes
- Trade-off: Lowest effort but won't produce well-designed virtual experiences.

**Recommendation:** Approach A for maximum professional value, or Approach B as a pragmatic near-term addition.

---

### Gap 6: Differentiated Instruction / Mixed-Level Audiences

**Severity: MEDIUM**

**Current State:** Plugin assumes a relatively homogeneous audience level. No guidance for mixed-level classrooms, extension activities for advanced learners, or scaffolding support for struggling learners within the same session.

**Impact:** Real workshops rarely have perfectly leveled audiences. Without differentiation strategies, you lose both ends: advanced learners disengage, struggling learners fall behind.

#### Approaches

**A. Differentiation layer in lesson plans (Recommended)**
- Modify `generate-lesson-plans` to include per-module:
  - **Floor activities:** Minimum successful completion for all learners
  - **Extension activities:** Stretch challenges for advanced learners
  - **Support scaffolds:** Additional guidance for struggling learners
- Add "Differentiation Strategy" section to lesson plan template
- Trade-off: Makes lesson plans longer. Instructors may not use all three tiers.

**B. Separate `generate-differentiated-paths` command**
- Creates parallel activity tracks
- Trade-off: Complex to implement, harder to manage in real-time delivery.

**Recommendation:** Approach A. Differentiation should be woven into lesson plans, not a separate document.

---

### Gap 7: Pre-work & Post-work Design

**Severity: MEDIUM**

**Current State:** Bloom's skill mentions pre-work briefly (suggesting Remember-level content as pre-work). No dedicated workflow for structured pre-course preparation or post-course reinforcement materials.

**Impact:** Pre-work can compress workshop time by moving foundational knowledge outside the classroom. Post-work reinforces learning and bridges to transfer.

#### Approaches

**A. Add artifact types to `generate-artifacts` (Recommended)**
- `--type pre-work`: Reading assignments, video links, self-assessment, preparation exercises (derived from Remember/Understand objectives)
- `--type post-work`: Application exercises, reflection prompts, resource compilation, learning journal template (derived from Apply+ objectives)
- Link pre-work to Day 1 morning modules; link post-work to capstone activities
- Trade-off: Minimal structural change, extends existing command pattern.

**B. Dedicated commands**
- Trade-off: Overkill for what are essentially artifact types.

**Recommendation:** Approach A. Clean extension of existing `generate-artifacts` command.

---

### Gap 8: Stakeholder Review Workflow

**Severity: MEDIUM**

**Current State:** No formal SME review or stakeholder approval process. Quality-reviewer agent validates pedagogical quality but doesn't facilitate external review.

**Impact:** In organizational L&D, courses go through: designer -> SME review -> stakeholder approval -> pilot -> revision -> deployment. Missing this process step risks misalignment with organizational needs.

#### Approaches

**A. Dedicated `generate-review-package` command (Recommended)**
- Creates stakeholder-friendly review document:
  - Executive summary (business need, audience, expected outcomes)
  - Curriculum overview (objectives, modules, timing)
  - Assessment strategy summary
  - SME review checklist with specific questions per module
  - Sign-off section
- Different from `export --format summary` (structured for review, not information)
- Trade-off: Adds a command producing a document for non-designers.

**B. Add review format to `export-curriculum`**
- New format: `--format review-package`
- Trade-off: Conflates export (output) with review (process).

**Recommendation:** Approach A. Review is a process step, not an export format.

---

### Gap 9: Pilot Testing Protocol

**Severity: LOW**

**Current State:** No guidance for running a pilot delivery, collecting pilot-specific feedback, or systematic iteration. `process-workshop-feedback` doesn't distinguish first-run pilot from steady-state delivery.

**Recommended Approach:** Add a `--pilot` flag to `process-workshop-feedback` that activates enhanced feedback collection: timing accuracy checks, activity effectiveness ratings per module, content gap identification, facilitation difficulty spots. Generate a `pilot-iteration-plan.md` with prioritized revisions.

---

### Gap 10: Content Licensing & IP Documentation

**Severity: LOW**

**Current State:** No tracking of third-party content, citation requirements, or licensing constraints.

**Recommended Approach:** Add a `content-sources.md` template to the course structure tracking: source material, licensing status, attribution requirements, expiration dates. Generate during `create-course`, populate during lesson plan creation.

---

## Proposed Phased Roadmap

### Phase 1: v0.4.0 — Professional Foundations
- Gap 1: Training Needs Assessment (CRITICAL)
- Gap 2: Accessibility & UDL (CRITICAL)
- Gap 7: Pre-work & Post-work artifacts (MEDIUM, low effort)

### Phase 2: v0.5.0 — Learning Ecosystem
- Gap 3: Transfer of Learning (HIGH)
- Gap 4: Kirkpatrick L3/L4 Evaluation (HIGH)
- Gap 6: Differentiated Instruction (MEDIUM)

### Phase 3: v0.6.0 — Delivery & Process
- Gap 5: Virtual/Hybrid Delivery (HIGH, high effort)
- Gap 8: Stakeholder Review Workflow (MEDIUM)

### Phase 4: v1.0.0 — Polish & Completeness
- Gap 9: Pilot Testing Protocol (LOW)
- Gap 10: Content Licensing & IP (LOW)
- Comprehensive integration testing across all new features

---

## Appendix: Component Inventory (v0.3.0)

| Component Type | Count | Items |
|---|---|---|
| Commands | 15 | create-course, generate-objectives, generate-rubrics, generate-outline, generate-lesson-plans, generate-description, generate-artifacts, export-curriculum, save-as-template, create-from-template, list-templates, generate-workshop-prep, process-workshop-feedback, design-series, review-curriculum |
| Agents | 2 | curriculum-architect, quality-reviewer |
| Skills | 2 | backward-design-methodology, blooms-taxonomy |
| Hooks | 1 | PreToolUse validation (prerequisite enforcement) |
| Examples | 3 | backward-design-1day, objectives-1day, objectives-2day |
| Reference docs | 2 | assessment-design, verb-tables |

**Projected additions from this roadmap:**
- Commands: +5 (assess-needs, generate-transfer-plan, generate-evaluation-plan, generate-review-package, adapt-for-virtual)
- Skills: +2 (universal-design-for-learning, virtual-facilitation)
- Artifact types: +2 (pre-work, post-work)
- Agent modifications: quality-reviewer gains UDL validation dimension
- Hook modifications: TNA prerequisite for create-course
