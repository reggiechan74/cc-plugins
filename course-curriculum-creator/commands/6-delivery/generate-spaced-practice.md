---
name: generate-spaced-practice
description: Generate a post-workshop spaced retrieval practice sequence to combat the forgetting curve with scheduled questions at expanding intervals
argument-hint: "[--format email|flashcards|lms|all] [--intervals custom]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Generate Spaced Practice Command

Generate a post-workshop spaced retrieval practice sequence to combat the forgetting curve with scheduled questions at expanding intervals.

## Prerequisites

- **Required:** `01-planning/learning-objectives.md` — extract objectives per module
- **Recommended:** `02-design/lesson-plans.md` — identify core content taught per module
- **Optional:** `03-assessment/rubrics.md` — calibrate question difficulty to match assessment expectations

## Staleness Check

Before generating, check source file hashes against any existing `04-materials/spaced-practice.md`:

1. Compute MD5 hash (first 8 characters) of each source file
2. Compare against `sourceHashes` in existing spaced practice frontmatter
3. If hashes differ, warn user: "Source files have changed since spaced practice was last generated. Regenerating will update questions to match current content."
4. If no existing file, proceed normally

## Command Behavior

When user invokes `/generate-spaced-practice [--format email|flashcards|lms|all] [--intervals custom]`:

1. **Load `blooms-taxonomy` skill** for cognitive level matching

2. **Read `01-planning/learning-objectives.md`** — extract objectives per module

3. **Read `02-design/lesson-plans.md`** — identify core content taught per module

4. **Read `03-assessment/rubrics.md`** — calibrate question difficulty to match assessment expectations

5. **For each module, generate 3-5 retrieval questions:**

### Question Design Rules

- **Match Bloom's level** of the module's objective (not just Remember-level recall)
- **Include brief answer keys** with 1-2 sentence explanations
- **Mix question formats by cognitive level:**
  - **Remember/Understand:** multiple choice, fill-in-the-blank, true/false with correction
  - **Apply:** short scenario + "what would you do?"
  - **Analyze:** "given this data/situation, what pattern do you see?"
  - **Evaluate:** "which option is best and why?"
- **No questions should test content not covered in lesson plans**

### Schedule

6. **Schedule questions at expanding intervals** (default): Day 1, Day 3, Day 7, Day 14, Day 30
   - Each practice session: 3-5 questions, max 5 minutes to complete
   - Questions cycle through modules so each module is revisited multiple times
   - Later sessions mix questions from different modules (interleaving for deeper retention)

7. **Format based on `--format` flag** (see Format Options below)

8. **Write output:** `04-materials/spaced-practice.md`

9. **Run staleness check** on source files

## Format Options

- `--format email` (default): Self-contained questions embedded in email body with "reveal answer" sections
- `--format flashcards`: Question/answer pairs, one per card, suitable for Anki or physical flashcard export
- `--format lms`: Structured quiz format with correct answer flagged, suitable for LMS import
- `--format all`: All three formats in one document

## Custom Intervals

`--intervals custom` prompts user for custom schedule. Default is Day 1, 3, 7, 14, 30.

## Output Format

```markdown
---
title: Spaced Practice Sequence - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match]
lastUpdated: YYYY-MM-DD
format: [email|flashcards|lms|all]
intervals: [1, 3, 7, 14, 30]
totalQuestions: [N]
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
  lesson-plans: "02-design/lesson-plans.md"
  rubrics: "03-assessment/rubrics.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
  lesson-plans: "[md5-first-8]"
  rubrics: "[md5-first-8]"
---

# Spaced Practice Sequence

## [Course Title]

**Purpose:** Combat the forgetting curve through scheduled retrieval practice at expanding intervals. Research shows spaced retrieval can double long-term retention compared to single post-workshop assessment.

**Schedule:** 5 practice sessions over 30 days (Day 1, 3, 7, 14, 30)
**Time per session:** 3-5 minutes
**Total questions:** [N] across all sessions

---

## Question Bank

### Module 1: [Title] — [Bloom's Level]

**Q1.1:** [Question text]
- **Format:** [Multiple choice / Scenario / Short answer]
- **Answer:** [Correct answer]
- **Explanation:** [1-2 sentence explanation of why]
- **Scheduled:** Day [N]

**Q1.2:** [Question text]
...

[Repeat for each module]

---

## Practice Sessions

### Day 1 — Immediate Retrieval

**Time:** 5 minutes | **Questions:** 5

1. [Q1.1] — Module 1
2. [Q2.1] — Module 2
3. [Q3.1] — Module 3
4. [Q4.1] — Module 4
5. [Q5.1] — Module 5

### Day 3 — Early Reinforcement

**Time:** 4 minutes | **Questions:** 4

[Questions drawn from different modules than Day 1 where possible]

### Day 7 — First Interval

**Time:** 5 minutes | **Questions:** 5

[Mix of new questions and revisited concepts from Day 1/3]

### Day 14 — Consolidation

**Time:** 4 minutes | **Questions:** 4

[Interleaved questions across all modules — tests connections between concepts]

### Day 30 — Long-Term Check

**Time:** 5 minutes | **Questions:** 5

[Higher-level questions — Apply/Analyze scenarios that combine multiple modules]

---

## Email Format (if --format email or all)

### Day [N] Email

**Subject:** [Course Title] — Quick Practice ([N] minutes)

**Body:**

Hi [Name],

Here's your Day [N] practice for [Course Title]. Takes about [N] minutes.

**Question 1:** [Question text]

<details>
<summary>Reveal Answer</summary>
[Answer + explanation]
</details>

[Repeat for each question]

---

## Flashcard Format (if --format flashcards or all)

### Card [N]
**Front:** [Question]
**Back:** [Answer + brief explanation]
**Tags:** [Module], [Bloom's level], [Day scheduled]

---

## LMS Format (if --format lms or all)

### Quiz: Day [N] Practice
**Time limit:** 5 minutes
**Passing score:** 70%
**Attempts:** Unlimited

| # | Question | Type | Correct Answer | Distractors | Points |
|---|----------|------|---------------|-------------|--------|
| 1 | [Text] | [MC/TF/SA] | [Answer] | [If MC: options] | 1 |
```

## Validation Checks

- Every module has at least 2 retrieval questions
- No questions test content not covered in lesson plans
- Question Bloom's level matches module objective level (no recall questions for Analyze objectives)
- Each practice session is completable in under 5 minutes
- All modules are represented across the 30-day schedule (no module forgotten)
- Answer explanations are present for every question

## Integration Points

- `generate-transfer-plan` references spaced practice schedule in follow-up touchpoint table:
  - Merge Day 1/3/7 practice emails into existing follow-up schedule
  - Note: spaced practice complements (does not replace) transfer application tasks
- `generate-evaluation-plan` can use spaced practice completion rates as supplementary L2 retention data
- `curriculum-architect` agent adds spaced practice generation as Phase 9e (after evaluation plan)

## Error Handling

**Missing learning objectives:**
- Error: "learning-objectives.md not found. Run `/generate-objectives` first."

**Missing lesson plans:**
- Warning: "lesson-plans.md not found. Questions will be based on objectives only (less specific). Generate lesson plans first for better question quality."

**Spaced practice already exists:**
- Prompt with overwrite/update/cancel options

## Implementation Notes

Generate questions that test genuine retrieval — not recognition. Questions should require learners to actively reconstruct knowledge rather than simply pick from obvious options. Spaced practice is most effective when it produces "desirable difficulty" — questions should feel challenging but achievable.

---

Generate a spaced retrieval practice sequence that helps learners retain workshop content long-term through scientifically-backed expanding interval schedules.
