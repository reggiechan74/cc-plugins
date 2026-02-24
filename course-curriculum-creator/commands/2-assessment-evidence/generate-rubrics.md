---
name: generate-rubrics
description: Generate assessment rubrics aligned to learning objectives
argument-hint: "[--scale 1-5] [--type analytical|performance|holistic]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
  - Skill
---

# Generate Rubrics Command

Create assessment rubrics aligned to learning objectives following backward design principles.

## Prerequisites

- Must be run within course project directory
- Requires `01-planning/learning-objectives.md` to exist

## Staleness Check

Before generating, check if source files have changed since this file was last generated:

1. If the output file `03-assessment/rubrics.md` already exists, read its YAML frontmatter `sourceHashes`
2. Compute current hash of each source file: `md5sum 01-planning/learning-objectives.md | cut -c1-8`
3. Compare hashes:
   - If hashes match: sources are unchanged, proceed normally
   - If hashes differ: warn the user: "⚠ Source file learning-objectives.md has changed since this file was last generated. Regenerating will incorporate these changes."
   - If output file doesn't exist: skip check, proceed with generation

When generating, always compute and write current source hashes to the output file's frontmatter.

## Command Behavior

1. **Load required skill**: Load `backward-design-methodology` skill for assessment design guidance
2. **Read learning objectives**: Parse objectives to understand what needs assessment
3. **Determine rubric specifications**:
   - Scale (default: 1-5 from settings)
   - Type (default: analytical from settings)
   - Criteria per objective
4. **Generate rubrics**: Create detailed evaluation criteria for each objective
5. **Write to file**: Save to `03-assessment/rubrics.md`
6. **Validate alignment**: Confirm rubrics measure objectives appropriately

## Skill Loading

```
Load backward-design-methodology skill for Stage 2 assessment design
```

Reference `references/assessment-design.md` for detailed rubric development guidance.

## Input Requirements

**Read from learning-objectives.md:**
- All learning objectives with cognitive levels
- Assessment methods specified
- Time allocations

**Read from settings (if available):**
- `rubric_scale`: Default scoring scale (1-4, 1-5, etc.)
- `rubric_type`: Default rubric type (analytical, performance, holistic)

**Prompt user if needed:**
- Rubric type preference if multiple objectives
- Specific criteria priorities
- Any custom requirements

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `rubric_scale`: Default scoring scale (e.g., 1-4 or 1-5) when not specified via arguments
- `rubric_type`: Default rubric type (analytical, performance, or holistic) when not specified via arguments

If settings file doesn't exist, use sensible defaults or prompt user.

## Rubric Types

### Analytical Rubrics (Recommended for Workshops)

**When to use:** Most workshop assessments
**Structure:** Multiple criteria evaluated separately
**Benefits:** Specific feedback, clear expectations

**Criteria per objective:** 3-5 criteria
**Scale:** 1-5 (default)

### Performance Rubrics

**When to use:** Skills demonstrations, procedures
**Structure:** Task completion with quality levels
**Benefits:** Process and product evaluation

### Holistic Rubrics

**When to use:** Quick assessments, overall impressions
**Structure:** Single overall score
**Benefits:** Faster evaluation (use sparingly)

## Rubric Generation Logic

### For Each Learning Objective:

1. **Identify assessment type** (from objective's assessment method)
2. **Select appropriate criteria** (3-5 per objective)
3. **Create performance level descriptors** (1-5 scale)
4. **Ensure cognitive level match** (rubric evaluates correct Bloom's level)

### Criteria Selection

**Based on cognitive level:**

**Understand objectives:**
- Accuracy of explanation
- Completeness of understanding
- Use of correct terminology
- Clarity of expression

**Apply objectives:**
- Correct methodology/framework use
- Accuracy of execution
- Appropriate application to context
- Quality of results

**Analyze objectives:**
- Depth of analysis
- Pattern recognition
- Evidence support
- Insight quality

**Evaluate objectives:**
- Criteria appropriateness
- Justification strength
- Decision quality
- Consideration of alternatives

**Create objectives:**
- Originality
- Feasibility
- Completeness
- Integration of concepts

### Descriptor Writing

**Performance levels (1-5 scale):**

1. **Beginning:** Minimal competency, major gaps
2. **Developing:** Partial competency, some gaps
3. **Proficient:** Meets expectations, minor gaps
4. **Advanced:** Exceeds expectations, strong performance
5. **Exemplary:** Exceptional, comprehensive mastery

**Descriptors must:**
- Be specific and observable
- Use concrete indicators (quantities, quality markers)
- Differentiate clearly between levels
- Align with objective's cognitive level

### UDL-Aligned Criteria

When writing rubric criteria, follow UDL Principle 3 (Multiple Means of Action & Expression):

- **Assess content and skill, not format**: Use "Demonstrates understanding of..." not "Writes a paragraph about..."
- **Allow multiple response formats**: Unless format IS the skill being assessed (e.g., "write a SQL query"), accept verbal, written, diagrammatic, or demonstrated responses
- **Criteria should be format-neutral**: "Identifies all five forces with supporting evidence" works whether the learner writes, diagrams, or presents verbally

## File Output Format

### 03-assessment/rubrics.md

```markdown
---
title: Assessment Rubrics - [Course Title]
date: YYYY-MM-DD
version: 0.1.0
status: draft
courseVersion: [match course version]
rubricScale: 1-5
rubricType: analytical
lastUpdated: YYYY-MM-DD
sourceFiles:
  learning-objectives: "01-planning/learning-objectives.md"
sourceHashes:
  learning-objectives: "[md5-first-8]"
---

# Assessment Rubrics

## Course: [Course Title]

**Assessment Philosophy:**
This course uses analytical rubrics (1-5 scale) to provide specific, actionable feedback on student performance. Each learning objective has a corresponding rubric with 3-5 criteria evaluated separately.

**Scale:**
- **1 (Beginning):** Minimal competency, significant gaps
- **2 (Developing):** Partial competency, noticeable gaps
- **3 (Proficient):** Meets expectations, minor improvements possible
- **4 (Advanced):** Exceeds expectations, strong mastery
- **5 (Exemplary):** Exceptional performance, comprehensive mastery

---

## Rubric 1: [Objective 1 Title]

**Learning Objective:**
[Full objective statement from learning-objectives.md]

**Cognitive Level:** [Bloom's level]
**Assessment Method:** [Method from objective]

### Evaluation Criteria

| Criterion | 1 (Beginning) | 2 (Developing) | 3 (Proficient) | 4 (Advanced) | 5 (Exemplary) |
|-----------|---------------|----------------|----------------|--------------|---------------|
| **[Criterion 1]** | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] |
| **[Criterion 2]** | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] |
| **[Criterion 3]** | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] |
| **[Criterion 4]** | [Descriptor - if applicable] | [Descriptor] | [Descriptor] | [Descriptor] | [Descriptor] |

**Scoring Guide:**
- **Total Points Possible:** [Number of criteria × 5]
- **Proficient Performance:** [70-80% of total] ([Calculate range])
- **Advanced Performance:** [80-90% of total] ([Calculate range])
- **Exemplary Performance:** [90-100% of total] ([Calculate range])

**Success Threshold:** Students should achieve at least Level 3 (Proficient) on all criteria to demonstrate objective mastery.

---

[Repeat for each objective]

---

## Assessment Schedule

| Objective | Assessment Timing | Assessment Type | Time Allocated | Rubric |
|-----------|-------------------|-----------------|----------------|--------|
| 1 | [Module X, Day X] | [Type] | [Minutes] | Rubric 1 |
| 2 | [Module X, Day X] | [Type] | [Minutes] | Rubric 2 |
| ... | | | | |

## Alignment Matrix

Validate that assessments measure intended outcomes:

| Learning Objective | Cognitive Level | Assessment Method | Rubric Criteria | Alignment Check |
|--------------------|-----------------|-------------------|-----------------|-----------------|
| [Objective 1] | [Level] | [Method] | [List criteria] | ✓ Method matches level |
| [Objective 2] | [Level] | [Method] | [List criteria] | ✓ Method matches level |

**Validation Notes:**
[Any notes on alignment or rationale for assessment choices]

## Formative Assessment Strategy

In addition to summative rubrics above, use these formative assessments throughout:

**Module Check-ins:**
- Exit tickets (2-3 min at module end)
- Quick polls (1-2 min after concepts)
- Think-pair-share (5 min mid-module)

**Peer Assessment:**
- Peer review using simplified rubrics (10-15 min during practice)
- Gallery walks with feedback (15-20 min for group work)

**Instructor Observation:**
- Circulate during practice activities
- Note common struggles for debrief
- Provide corrective feedback immediately

## Using These Rubrics

### During Workshop

1. **Share rubrics with students** at activity start (set expectations)
2. **Use for peer review** where appropriate (builds assessment literacy)
3. **Circulate and observe** using rubric criteria as observation guide
4. **Provide formative feedback** referencing rubric levels
5. **Use for self-assessment** (students rate themselves before submission)

### Post-Workshop

1. **Evaluate student work** using rubrics within 3-5 business days
2. **Provide scores and comments** for each criterion
3. **Highlight strengths and growth areas**
4. **Suggest next steps for continued learning**

### Rubric Refinement

After workshop delivery:
- Note any ambiguous descriptors that need clarification
- Adjust performance level expectations if too easy/hard
- Add criteria if important dimensions were missed
- Update for next offering

## Next Steps

1. Review rubrics for clarity and alignment with objectives
2. Plan learning activities that prepare students for these assessments: `/generate-outline` and `/generate-lesson-plans`
3. Integrate formative assessments into lesson plans
4. Share rubrics with students to set clear expectations

## Notes

- All rubrics use consistent 1-5 scale for comparability
- Criteria are specific and observable (not subjective)
- Descriptors differentiate performance levels clearly
- Rubrics align with objective cognitive levels (Apply rubrics assess application, not recall)
- Total assessment time fits within workshop schedule
```

## Post-Generation Actions

1. **Validate alignment**:
   - Confirm each objective has corresponding rubric
   - Check assessment methods match cognitive levels
   - Verify total assessment time is realistic

2. **Prompt user review**: "Review the generated rubrics. Would you like me to adjust criteria, descriptors, or scoring?"

3. **Suggest next step**: "Next: Plan learning activities that prepare students for these assessments using `/generate-outline`"

## Validation Checks

- [ ] Each learning objective has a rubric
- [ ] Rubric criteria match objective cognitive level
- [ ] Descriptors are specific and observable
- [ ] Performance levels clearly differentiated
- [ ] Assessment methods align with objectives
- [ ] Total assessment time fits in workshop schedule
- [ ] All rubrics use consistent scale

## Error Handling

**Missing learning-objectives.md:**
- "Error: learning-objectives.md not found. Generate objectives first using `/generate-objectives`"

**Rubrics already exist:**
- Prompt: "rubrics.md already exists. Options: (1) Regenerate (overwrites), (2) Add to existing, (3) Cancel"

**Cognitive level mismatch detected:**
- Warn: "Warning: Objective X is Analyze level but assessment method (quiz) typically measures Remember/Understand. Consider adjusting."

## Example Usage

**Basic:**
```
User: /generate-rubrics
[Plugin generates analytical rubrics with 1-5 scale]
```

**With arguments:**
```
User: /generate-rubrics --scale 1-4 --type performance
[Plugin generates performance rubrics with 1-4 scale]
```

---

Generate assessment rubrics that clearly define success criteria, provide specific feedback guidance, and align perfectly with learning objectives' cognitive levels.
