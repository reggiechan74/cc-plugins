---
name: rubric-creator
description: |
  Professional-grade rubric creation skill with validity, reliability, and fairness controls.

  USE RUBRIC-CREATOR FOR:
  - Creating assessment frameworks for any domain
  - Building scoring systems with inter-rater reliability
  - Generating pilot testing and calibration materials
  - Converting existing rubrics to new domains

  Three modes: interactive (guided questionnaire), template (pre-built domains), example-based (adapt existing rubric).

  Includes: anchor examples, critical barriers, confidence flagging, bias review, maintenance lifecycle.

  See templates/ for detailed template definitions with anchor examples.
---

# Rubric Creator Skill

Create a structured scoring rubric for any activity, document, or assessment using a proven meta-framework with professional-grade validity, reliability, and fairness controls.

## Table of Contents

- [Usage](#usage)
- [Options](#options)
- [Available Templates](#available-templates)
- [Examples](#examples)
- [Execution Instructions](#execution-instructions)
- [Mode 1: Interactive Mode](#mode-1-interactive-mode---interactive)
- [Mode 2: Template Mode](#mode-2-template-mode---template-domain)
- [Mode 3: Example-Based Mode](#mode-3-example-based-mode---from-example-file)
- [Rubric Template Structure](#rubric-template-structure)
- [Output Generation](#output-generation)
- [Pilot Testing Protocol](#pilot-testing-protocol)
- [Rubric Maintenance Lifecycle](#rubric-maintenance-lifecycle)
- [Error Handling](#error-handling)
- [Related Skills](#related-skills)

---

## Usage

```
/rubric-creator [options]
```

Or simply describe what you want to assess and this skill will guide you through rubric creation.

## Options

| Option | Description |
|--------|-------------|
| `--interactive` | Guided questionnaire to build a custom rubric step-by-step |
| `--template [domain]` | Generate from pre-built template (see available templates below) |
| `--from-example [file]` | Analyze an existing rubric and create a variant for a new domain |
| `--output [path]` | Specify output file path (default: auto-generated in current directory) |
| `--with-pilot` | Include pilot testing worksheet in output |
| `--with-calibration` | Include scorer calibration materials |

## Available Templates

| Template | Domain | Description |
|----------|--------|-------------|
| `regulatory-compliance` | Legal/Regulatory | Assess compliance with regulations, bylaws, policies |
| `document-quality` | Documentation | Evaluate reports, proposals, technical documents |
| `code-review` | Software | Score code quality, maintainability, security |
| `vendor-evaluation` | Procurement | Assess vendor proposals, RFP responses |
| `risk-assessment` | Risk Management | Evaluate project, operational, or financial risks |
| `performance-review` | HR/Management | Employee or team performance assessment |
| `research-quality` | Academic/Research | Evaluate research papers, methodologies, citations |

See `templates/` directory for detailed template definitions with criteria and anchor examples.

## Examples

```bash
# Interactive mode - guided creation
/rubric-creator --interactive

# Generate from template with pilot materials
/rubric-creator --template regulatory-compliance --output bylaws/zoning_rubric.md --with-pilot

# Create variant from existing rubric
/rubric-creator --from-example Research_Reports/assessment_rubric_framework.md --output new_domain_rubric.md

# Full professional package with calibration materials
/rubric-creator --interactive --with-pilot --with-calibration
```

---

## Execution Instructions

When this skill is invoked, follow these steps based on the mode:

### Mode Detection

1. Parse arguments to determine mode:
   - If `--interactive` flag present → Interactive Mode
   - If `--template [domain]` present → Template Mode
   - If `--from-example [file]` present → Example-Based Mode
   - If no mode specified → Default to Interactive Mode

2. Parse optional flags:
   - `--output [path]` - Custom output path
   - `--with-pilot` - Generate pilot testing worksheet
   - `--with-calibration` - Generate scorer calibration pack

---

## MODE 1: Interactive Mode (`--interactive`)

Guide the user through rubric creation with a structured questionnaire.

### Phase 0: Alignment & Validity Foundation

**CRITICAL:** This phase establishes what the rubric should measure and why. Skip this and validity suffers.

Use AskUserQuestion to gather alignment parameters:

**Question Set 0A: Assessment Alignment**
```
Question: "What standards, objectives, or expectations should this rubric align with?"
Header: "Alignment"
Options:
- "External Standards" - Professional standards, regulations, accreditation criteria (e.g., CUSPAP, ISO, GAAP)
- "Internal Objectives" - Organizational goals, learning outcomes, KPIs, project success criteria
- "Stakeholder Expectations" - Client requirements, user needs, contractual obligations
- "Best Practice Benchmarks" - Industry norms, competitor analysis, published frameworks
MultiSelect: true
```

**Question Set 0B: Construct Definition**
```
Question: "In one sentence, what quality or characteristic does this rubric measure?"
Header: "Construct"
Free text response - Examples:
- "Regulatory feasibility for digital billboard installation"
- "Technical document completeness and accuracy"
- "Employee contribution to team objectives"
```

**Question Set 0C: Validation Approach**
```
Question: "How will you validate that this rubric measures what it claims to measure?"
Header: "Validation"
Options:
- "Expert Review" - Domain experts will review criteria for face validity
- "Pilot Testing" - Trial scoring on sample items before deployment
- "Stakeholder Feedback" - Those being assessed will review for fairness
- "Statistical Analysis" - Correlation with known outcomes or other measures
MultiSelect: true
```

### Phase 1: Foundation Questions

**Question Set 1: Purpose & Scope**
```
Question: "What type of activity or document will this rubric assess?"
Header: "Assessment Target"
Options:
- "Regulatory/Legal Compliance" - Bylaws, regulations, policies, contracts
- "Document/Deliverable Quality" - Reports, proposals, technical docs
- "Process/Performance" - Workflows, employee performance, project execution
- "Technical Evaluation" - Code, systems, vendor solutions
```

**Question Set 2: Scoring Purpose**
```
Question: "What is the primary purpose of scoring?"
Header: "Scoring Goal"
Options:
- "Go/No-Go Decision" - Binary pass/fail with supporting rationale
- "Comparative Ranking" - Compare multiple items against each other
- "Gap Analysis" - Identify areas needing improvement
- "Compliance Verification" - Verify adherence to standards
```

**Question Set 3: Score Granularity**
```
Question: "How granular should the scoring be?"
Header: "Granularity"
Options:
- "High (200-300 points)" - Many criteria with fine distinctions
- "Medium (100-200 points)" - Balanced detail and usability
- "Low (50-100 points)" - Simplified, quick assessment
- "Custom" - Specify total points manually
```

**Question Set 4: Number of Categories**
```
Question: "How many major assessment categories do you need?"
Header: "Categories"
Options:
- "3-4 categories" - Focused assessment on key dimensions
- "5-6 categories" - Comprehensive coverage
- "7-8 categories" - Detailed multi-dimensional analysis
- "Custom" - Specify categories manually
```

### Phase 2: Category Definition

For each category (based on Phase 1 answer), ask:

```
Question: "What should Category [N] assess?"
Header: "Category [N]"
Options: [Generate contextually appropriate options based on assessment type]
```

Allow user to provide custom category names via "Other" option.

**Weight Assignment with Justification:**
```
Question: "How important is '[Category Name]' relative to other categories?"
Header: "Weight"
Options:
- "Critical (25-30%)" - Deal-breaker if scored low
- "High (15-24%)" - Very important but not sole determinant
- "Medium (10-14%)" - Standard importance
- "Low (5-9%)" - Nice-to-have, minor factor
```

**Weight Rationale (Required):**
```
Question: "Why is '[Category Name]' weighted at [X]%? (Required for audit trail)"
Header: "Rationale"
Free text response - Examples:
- "Legal compliance is 25% because non-compliance is a regulatory blocker"
- "Formatting is 10% because it affects perception but not substance"
- "Security is 20% because vulnerabilities create liability"
```

### Phase 3: Criteria Development

For each category, generate 3-6 criteria based on:
- Assessment type selected in Phase 1
- Category purpose defined in Phase 2
- Industry best practices for the domain
- Alignment requirements from Phase 0

**Criterion Independence Check (REQUIRED):**

Before presenting criteria to user, verify:

1. **No Double-Counting:** Each aspect scored in only one criterion
   - ❌ Bad: "Communication clarity" in Cat 3 AND "Report writing" in Cat 4
   - ✅ Good: Clearly delineated scope for each

2. **No Hidden Dependencies:** Criteria should be scorable independently
   - ❌ Bad: Criterion B cannot be high if Criterion A is low
   - ✅ Good: Each criterion stands alone

3. **Exhaustive Coverage:** No important aspects left unscored
   - Ask: "What could go wrong that this rubric wouldn't catch?"

4. **Alignment Traceability:** Each criterion traces to Phase 0 alignment source
   - Document: "This criterion addresses [Standard X / Objective Y]"

Present generated criteria to user for approval/modification:
```
Question: "Review the proposed criteria for '[Category Name]'. Select any you want to modify or remove:"
Header: "Criteria Review"
Options: [List generated criteria with descriptions]
MultiSelect: true
```

**Critical Barrier Identification:**
```
Question: "Which criteria represent 'hard stops' where a low score indicates fundamental problems regardless of overall score?"
Header: "Critical Barriers"
Options: [List all criteria in category]
MultiSelect: true
```

For each selected critical barrier:
```
Question: "At what score threshold does '[Criterion]' become a critical barrier?"
Header: "Threshold"
Options:
- "Score = 0" - Complete absence is unacceptable
- "Score ≤ 1" - Near-absence is unacceptable
- "Score ≤ 2" - Below minimum threshold
- "Bottom quartile" - Relative to scale maximum
```

### Phase 4: Scoring Scale Design

**Scale Consistency Guidelines:**

1. **Prefer uniform scale depth within categories**
   - ❌ Mixed: 0-6 pts, 0-10 pts, 0-4 pts in same category
   - ✅ Consistent: All criteria in category use 0-6 scale

2. **Limit total scale types per rubric to 2-3**
   - Primary scale: Numeric range (most criteria)
   - Secondary scale: Qualitative levels (subjective criteria)
   - Tertiary scale: Binary/ternary (yes/no items)

3. **Document scale rationale for non-standard choices**

For each criterion, determine appropriate scale type:

| Criterion Type | Recommended Scale | Example |
|----------------|-------------------|---------|
| Measurable quantities | Numeric range (0-6 pts with thresholds) | Setback distances, word counts |
| Quality assessments | Qualitative levels (Excellent/Good/Fair/Poor) | Writing quality, design aesthetic |
| Yes/No with nuance | Ternary (Yes=full/Partial=half/No=0) | Compliance checks |
| Counts or enumerations | Count-based (4+ items = 10 pts) | Number of zones, references |

**Anchor Example Requirement:**

For EVERY criterion level, require at least one anchor example:
```
Question: "Provide a concrete example of [Score Level] performance for '[Criterion Name]':"
Header: "Anchor Example"
Free text response - Example:
- For "10 pts - Excellent": "Document includes all 5 required sections with comprehensive detail exceeding 2 pages each"
- For "0 pts - Not specified": "Document contains no table of contents and sections are unlabeled"
```

### Phase 5: Bias Review

Before finalizing, conduct systematic bias review:

**Content Bias Check:**
```
Question: "Review criteria for content bias. Do any criteria:"
Header: "Content Bias"
Options:
- "Favor specific demographics, regions, or organizational sizes"
- "Use non-neutral or loaded language"
- "Lack diverse scenario representation in examples"
- "None identified" - Criteria appear neutral
MultiSelect: true
```

**Structural Bias Check:**
```
Question: "Review structure for bias. Does the rubric:"
Header: "Structural Bias"
Options:
- "Systematically disadvantage certain item types in point distribution"
- "Unfairly penalize 'Not Applicable' responses"
- "Include criteria unachievable without specific resources/budget"
- "None identified" - Structure appears fair
MultiSelect: true
```

**Scorer Bias Mitigation:**
```
Question: "What scorer bias mitigations should be included?"
Header: "Scorer Bias"
Options:
- "Blind scoring" - Scorer cannot identify item creator
- "Randomized order" - Criteria presented in random order to prevent anchoring
- "Dual scoring" - Two independent scorers required
- "Calibration requirement" - Scorers must calibrate before independent scoring
MultiSelect: true
```

For any bias identified, document mitigation strategy before proceeding.

### Phase 6: Generate Rubric

After gathering all inputs, generate the complete rubric using the **Rubric Template Structure** below.

---

## MODE 2: Template Mode (`--template [domain]`)

Generate a rubric from pre-built templates. Each template provides:
- Pre-defined categories with weights and justifications
- Standard criteria for the domain with anchor examples
- Appropriate scoring scales with consistency
- Domain-specific interpretation bands
- Pre-identified critical barriers
- Bias review findings for the domain

**Reference:** See `templates/` directory for full template definitions.

### Template: `regulatory-compliance`

**Categories:**
1. Permitted Activities & Scope (20%) - *Justification: Foundational; if activities aren't permitted, other factors are moot*
2. Dimensional/Quantitative Requirements (20%) - *Justification: Objective, measurable compliance factors*
3. Technical & Operational Standards (25%) - *Justification: Core operational viability*
4. Regulatory Process & Approvals (15%) - *Justification: Pathway to implementation*
5. Regulatory Clarity & Definitions (12%) - *Justification: Affects interpretation risk*
6. External Jurisdiction Overlay (8%) - *Justification: Secondary constraint layer*

**Total Points:** 250
**Interpretation:** Highly Favorable → Prohibitive
**Critical Barriers:** Category 1 items (prohibition = automatic fail)

### Template: `document-quality`

**Categories:**
1. Content Completeness (25%) - *Justification: Missing content cannot be compensated by quality*
2. Technical Accuracy (25%) - *Justification: Errors undermine credibility and utility*
3. Structure & Organization (15%) - *Justification: Affects usability but not substance*
4. Writing Quality & Clarity (15%) - *Justification: Communication effectiveness*
5. Citations & Evidence (10%) - *Justification: Supports claims but secondary to content*
6. Formatting & Presentation (10%) - *Justification: Professional appearance, lowest priority*

**Total Points:** 200
**Interpretation:** Excellent → Unacceptable
**Critical Barriers:** Technical Accuracy items (major errors = automatic revision required)

### Template: `code-review`

**Categories:**
1. Functionality & Correctness (25%) - *Justification: Code must work correctly*
2. Code Quality & Readability (20%) - *Justification: Maintainability over time*
3. Security & Safety (20%) - *Justification: Vulnerabilities create liability*
4. Performance & Efficiency (15%) - *Justification: User experience and cost*
5. Testing & Coverage (10%) - *Justification: Confidence in correctness*
6. Documentation (10%) - *Justification: Knowledge transfer*

**Total Points:** 150
**Interpretation:** Production Ready → Major Revision Required
**Critical Barriers:** Security items (any vulnerability = automatic block), Functionality items (broken code = automatic block)

### Template: `vendor-evaluation`

**Categories:**
1. Technical Capability (25%) - *Justification: Must be able to deliver*
2. Cost & Value (20%) - *Justification: Budget constraints are real*
3. Experience & References (20%) - *Justification: Track record predicts future*
4. Implementation Approach (15%) - *Justification: How they'll deliver matters*
5. Support & Maintenance (10%) - *Justification: Long-term relationship*
6. Risk & Compliance (10%) - *Justification: Protect the organization*

**Total Points:** 200
**Interpretation:** Highly Recommended → Not Recommended
**Critical Barriers:** Risk & Compliance items (compliance failure = disqualification)

### Template: `risk-assessment`

**Categories:**
1. Probability of Occurrence (25%) - *Justification: Likelihood drives prioritization*
2. Impact Severity (25%) - *Justification: Consequences drive urgency*
3. Mitigation Feasibility (20%) - *Justification: Can we actually address it?*
4. Detection Capability (15%) - *Justification: Can we see it coming?*
5. Control Effectiveness (15%) - *Justification: Do current controls work?*

**Total Points:** 100
**Interpretation:** Critical Risk → Negligible Risk (INVERTED - higher = more risk)
**Critical Barriers:** Impact Severity (catastrophic impact = automatic escalation regardless of probability)

### Template: `performance-review`

**Categories:**
1. Goal Achievement (25%) - *Justification: Primary measure of contribution*
2. Quality of Work (20%) - *Justification: Output standards matter*
3. Collaboration & Communication (20%) - *Justification: Team effectiveness*
4. Initiative & Problem-Solving (15%) - *Justification: Growth and adaptability*
5. Professional Development (10%) - *Justification: Future potential*
6. Attendance & Reliability (10%) - *Justification: Basic expectations*

**Total Points:** 100
**Interpretation:** Exceeds Expectations → Does Not Meet Expectations
**Critical Barriers:** Attendance & Reliability (chronic issues = performance plan regardless of other scores)

### Template: `research-quality`

**Categories:**
1. Research Design & Methodology (25%) - *Justification: Foundation of validity*
2. Literature Review & Context (20%) - *Justification: Situates contribution*
3. Data Analysis & Findings (20%) - *Justification: Core scientific work*
4. Conclusions & Implications (15%) - *Justification: Value of contribution*
5. Citation Quality & Integrity (10%) - *Justification: Academic honesty*
6. Presentation & Clarity (10%) - *Justification: Communication of findings*

**Total Points:** 200
**Interpretation:** Publication Ready → Major Revision Required
**Critical Barriers:** Citation Quality & Integrity (plagiarism = automatic rejection)

### Template Customization

After selecting a template, prompt user:
```
Question: "Do you want to customize this template?"
Header: "Customize"
Options:
- "Use as-is" - Generate rubric with default settings
- "Adjust weights" - Modify category weights (requires new justifications)
- "Add/remove categories" - Customize category structure
- "Modify criteria" - Fine-tune individual criteria
- "Update anchor examples" - Customize examples for your context
```

---

## MODE 3: Example-Based Mode (`--from-example [file]`)

Analyze an existing rubric and create a variant for a new domain.

### Step 1: Read and Analyze Source Rubric

Read the specified file and extract:

1. **Structure Analysis:**
   - Number of categories
   - Category weights (as % of total)
   - Number of criteria per category
   - Scoring scale types used
   - Total point value

2. **Pattern Extraction:**
   - Scoring instruction patterns
   - Boundary rule patterns
   - Interpretation band structure
   - Special rules (cascade, defaults, etc.)
   - Critical barrier definitions

3. **Quality Feature Extraction:**
   - Anchor example patterns
   - Weight justification patterns
   - Bias mitigation approaches
   - Inter-rater reliability mechanisms

4. **Documentation Patterns:**
   - Header format
   - Category/criterion naming conventions
   - Note/warning box usage
   - Version history format

### Step 2: Gather New Domain Information

```
Question: "What domain should the new rubric assess?"
Header: "New Domain"
Options:
- "Regulatory/Legal" - Different regulation type
- "Technical/Engineering" - Different technical domain
- "Business/Operations" - Different business process
- "Custom" - Describe the new domain
```

```
Question: "How closely should the new rubric follow the source structure?"
Header: "Similarity"
Options:
- "Very close (80%+)" - Same structure, different terminology
- "Moderate (50-80%)" - Similar structure, some category changes
- "Loose (20-50%)" - Inspired by structure, significant changes
- "Framework only" - Use meta-structure, all new content
```

```
Question: "What alignment sources apply to the new domain?"
Header: "New Alignment"
Free text response - Examples:
- "ISO 27001 for information security"
- "PMBOK for project management"
- "APA guidelines for academic writing"
```

### Step 3: Generate Mapping

Create a mapping table showing:

| Source Category | New Category | Similarity | Weight Change | Justification |
|-----------------|--------------|------------|---------------|---------------|
| [Source Cat 1] | [Proposed New Cat 1] | [%] | [Same/+/-] | [Why] |
| ... | ... | ... | ... | ... |

Present mapping to user for approval/modification.

### Step 4: Criterion Adaptation

For each criterion being adapted:

1. **Terminology Translation:** Map source terms to new domain terms
2. **Anchor Example Creation:** Generate new domain-specific examples
3. **Scale Appropriateness:** Verify scale still makes sense for new domain
4. **Critical Barrier Review:** Reassess which criteria are critical barriers

### Step 5: Generate New Rubric

Apply the source rubric's:
- Scoring instruction patterns
- Scale type patterns
- Documentation structure
- Interpretation band structure
- Bias mitigation approaches

With the new domain's:
- Category names and descriptions
- Criteria specific to new domain
- Domain-specific terminology
- Appropriate point values
- New anchor examples
- Updated alignment statement

---

## Rubric Template Structure

All generated rubrics MUST follow this structure:

```markdown
# [Assessment Type] Assessment Rubric

**Version:** 1.0
**Total Maximum Score:** [N] points
**Normalized Score:** (Achieved Points / [N]) × 100% = X%
**Last Validated:** [Date]
**Next Review Due:** [Date + maintenance interval]

---

## Alignment Statement

**This rubric measures:** [Clear statement of construct from Phase 0]

**Aligned with:**
- [Standard/objective 1 from Phase 0]
- [Standard/objective 2 from Phase 0]

**Validation method:** [From Phase 0 - Expert Review / Pilot Testing / etc.]

**Validation status:** [Pending / Validated on DATE / Requires revalidation]

---

## Table of Contents

- [Alignment Statement](#alignment-statement)
- [Scoring Instructions](#scoring-instructions)
  - [Level Scoring Rules](#level-scoring-rules)
  - [Boundary Handling](#boundary-handling)
  - [Evidence Requirements](#evidence-requirements)
  - [Default Handling](#default-handling)
  - [Confidence Flagging](#confidence-flagging)
  - [Special Rules](#special-rules)
- [Inter-Rater Reliability Protocol](#inter-rater-reliability-protocol)
- [Critical Barrier Definitions](#critical-barrier-definitions)
- [Category 1: [Name]](#category-1-name)
- [Category 2: [Name]](#category-2-name)
- ...
- [Summary: Total Scoring Framework](#summary-total-scoring-framework)
- [Category Weight Justification](#category-weight-justification)
- [Score Interpretation Bands](#score-interpretation-bands)
- [Key Interpretation Rules Summary](#key-interpretation-rules-summary)
- [Bias Review Findings](#bias-review-findings)
- [Version History](#version-history)

---

## Scoring Instructions

### Level Scoring Rules

1. **Only predefined point values may be assigned** - no intermediate scores permitted
2. **For numeric ranges:**
   - Boundaries use "< X" or "X to < Y" format to eliminate overlaps
   - A value exactly at a boundary goes to the LOWER point category
   - Example: If scale is "10m to <15m = 4 pts" and "15m to <20m = 3 pts", then exactly 15m scores 3 pts
3. **For qualitative criteria:**
   - Scorer must select the best-matching description
   - Choose the single closest match - no averaging
   - When between two levels, choose the LOWER level unless evidence clearly supports higher

### Boundary Handling

[Specify how boundary cases are handled for this domain]

**Standard boundary rules:**
- Numeric values at exact boundaries → assign to lower point category
- Qualitative assessments between levels → assign to lower level unless preponderance of evidence supports higher
- Missing data → score as 0 unless criterion specifies alternative

### Evidence Requirements

[Specify what counts as evidence - explicit statements, inferences, documentation]

**Standard evidence hierarchy:**
1. **Explicit statement** in source document (strongest)
2. **Clear implication** from multiple consistent statements
3. **Reasonable inference** from context (weakest - flag with low confidence)

**Citation requirement:** Every score above 0 must have a direct citation or documented rationale.

### Default Handling

- **Unknown/Not Specified values:** Score as **0 points** unless otherwise noted
- **Not Applicable items:** [Specify: Score 0 / Exclude from total / Pro-rate remaining]
- [Any domain-specific default rules]

### Confidence Flagging

For each score, indicate confidence level:

| Confidence | Definition | Action Required |
|------------|------------|-----------------|
| **High** | Clear evidence, unambiguous criterion match | None |
| **Medium** | Some interpretation required, evidence partially applicable | Document reasoning |
| **Low** | Significant uncertainty, scorer judgment heavily involved | Flag for review |

**Low confidence scores** should be reviewed by second scorer or escalated to supervisor.

### Special Rules

[Any cascade rules, interaction rules, or domain-specific scoring logic]

---

## Inter-Rater Reliability Protocol

### Calibration Requirement

Before scoring independently, all scorers must:

1. **Review anchor examples** for each criterion level
2. **Calibrate on 3+ sample items** with experienced scorer present
3. **Achieve ≥85% agreement** on calibration items before independent scoring
4. **Re-calibrate** if more than 30 days since last calibration

### Disagreement Resolution

When two scorers differ:

| Difference | Resolution |
|------------|------------|
| 1 level (e.g., 8 vs 7) | Use lower score, document both perspectives |
| 2+ levels (e.g., 8 vs 5) | Required: Discussion and consensus, or escalate to third scorer |
| Critical barrier triggered by one scorer | Conservative approach: treat as triggered, investigate |

### Reliability Targets

- **Target:** Cohen's Kappa ≥ 0.80 OR percentage agreement ≥ 85%
- **Minimum acceptable:** Kappa ≥ 0.60 OR percentage agreement ≥ 75%
- **Below minimum:** Pause scoring, identify problematic criteria, clarify/retrain

---

## Critical Barrier Definitions

Certain criteria represent "hard stops" where low scores indicate fundamental problems regardless of overall score.

| Criterion | Barrier Threshold | Consequence |
|-----------|-------------------|-------------|
| [Criterion ID] | Score ≤ [N] | [Action: e.g., "Automatic fail", "Requires remediation plan", "Escalate to committee"] |
| [Criterion ID] | Score = 0 | [Action] |

### Barrier Override Process

If a critical barrier is triggered but overall assessment should proceed:

1. **Document specific justification** explaining exceptional circumstances
2. **Require supervisor/committee approval** (specify approver role)
3. **Note exception in final report** with approval reference
4. **Track override** for pattern analysis

---

## Category 1: [Category Name] ([X] points)

> **[Context note or critical warning if applicable]**

**Alignment:** This category addresses [Standard/Objective from alignment statement]

### **1A. [Subcategory Name] ([Y] points)**

**1A1. [Criterion name] (0-[Z] pts)**

| Score | Description | Anchor Example |
|-------|-------------|----------------|
| **[Z]** | [Best case description] | *[Concrete example of Z-level performance]* |
| **[Z-n]** | [Next level description] | *[Concrete example]* |
| ... | ... | ... |
| **0** | [Worst case / not specified] | *[Concrete example of 0-level or N/A]* |

> **Note:** [Clarifying note if needed]

**1A2. [Criterion name] (0-[Z] pts)**

| Score | Description | Anchor Example |
|-------|-------------|----------------|
| **[Z]** | [Best case description] | *[Concrete example]* |
| ... | ... | ... |
| **0** | [Worst case / not specified] | *[Concrete example]* |

[Repeat for all criteria in category]

---

[Repeat Category structure for all categories]

---

## Summary: Total Scoring Framework

| Category | Sub-Items | Max Points | % of Total |
|----------|-----------|------------|------------|
| **1. [Category Name]** | [N] items | **[X]** | [Y]% |
| **2. [Category Name]** | [N] items | **[X]** | [Y]% |
| ... | ... | ... | ... |
| **TOTAL** | **[N] scoreable items** | **[Total]** | **100%** |

---

## Category Weight Justification

| Category | Weight | Rationale |
|----------|--------|-----------|
| [Category 1] | [X]% | [Why this weight was chosen - from Phase 2] |
| [Category 2] | [Y]% | [Why this weight was chosen] |
| ... | ... | ... |

**Weight validation:** Weights were [validated by expert review / derived from stakeholder input / based on industry standards].

---

## Score Interpretation Bands

| Normalized Score | Rating | Interpretation | Recommended Action |
|-----------------|--------|----------------|-------------------|
| **85-100%** | **[Top Tier Label]** | [Practical meaning for this domain] | [Action: Approve, proceed, etc.] |
| **70-84%** | **[Second Tier]** | [Practical meaning] | [Action] |
| **55-69%** | **[Third Tier]** | [Practical meaning] | [Action] |
| **40-54%** | **[Fourth Tier]** | [Practical meaning] | [Action] |
| **25-39%** | **[Fifth Tier]** | [Practical meaning] | [Action] |
| **0-24%** | **[Bottom Tier]** | [Practical meaning] | [Action] |

**Note:** These bands are guidelines. Critical barrier triggers may override band-based recommendations.

---

## Usage Notes

1. **Assess each [item type] independently** using this rubric
2. **Score all [N] items** - use 0 for "not specified/not addressed" unless criterion specifies otherwise
3. **Calculate raw score** by summing all item scores
4. **Calculate normalized score** as (Raw Score / [Total]) × 100%
5. **Check critical barriers** before applying interpretation band
6. **Apply interpretation band** to determine overall rating
7. **Document scoring rationale** with specific citations/evidence for each score
8. **Flag low-confidence scores** for review
9. **Complete bias attestation** confirming no known conflicts of interest

---

## Key Interpretation Rules Summary

**Rule 1: [Rule Name]**
- [Clear, actionable statement]

**Rule 2: [Rule Name]**
- [Clear, actionable statement]

**Rule 3: Evidence Requirement**
- Every non-zero score requires documented evidence or citation

**Rule 4: Confidence Flagging**
- Low-confidence scores must be flagged and may require second review

**Rule 5: Critical Barrier Precedence**
- Critical barrier triggers override interpretation band recommendations

[Continue for all key rules - typically 5-8 rules]

---

## Bias Review Findings

This rubric was reviewed for bias on [Date].

### Content Bias Assessment
- [Finding 1 or "No content bias identified"]
- [Finding 2]
- **Mitigation:** [How bias was addressed]

### Structural Bias Assessment
- [Finding 1 or "No structural bias identified"]
- **Mitigation:** [How bias was addressed]

### Scorer Bias Mitigations
- [Mitigation 1: e.g., "Blind scoring recommended"]
- [Mitigation 2: e.g., "Dual scoring required for high-stakes decisions"]

### Bias Review Schedule
Next bias review due: [Date - typically annually or when criteria change]

---

## Version History

| Version | Date | Changes | Validated |
|---------|------|---------|-----------|
| 1.0 | [YYYY-MM-DD] | Initial rubric framework | [Yes/Pending] |
| 1.1 | [YYYY-MM-DD] | [Specific changes] | [Yes/Pending] |
```

---

## Output Generation

### File Naming

If `--output` not specified, generate filename:
```
[assessment-type]-rubric_v1.0.md
```

Examples:
- `regulatory-compliance-rubric_v1.0.md`
- `code-review-rubric_v1.0.md`
- `vendor-evaluation-rubric_v1.0.md`

### Post-Generation Actions

After generating the rubric:

1. **Display summary:**
   ```
   ✅ Rubric generated successfully

   📊 Summary:
      - Total Points: [N]
      - Categories: [N]
      - Criteria: [N]
      - Critical Barriers: [N]
      - Output: [file path]

   🎯 Alignment:
      - Construct: [From Phase 0]
      - Standards: [List from Phase 0]

   ⚠️ Validation Status: PENDING
      - Rubric requires pilot testing before deployment
      - See Pilot Testing Protocol below

   📝 Next steps:
      1. Review generated rubric for domain accuracy
      2. Verify anchor examples are realistic
      3. Conduct pilot testing on 3-5 sample items
      4. Calibrate scorers before deployment
      5. Update version and iterate based on pilot findings
   ```

2. **Offer follow-up actions:**
   ```
   Question: "What would you like to do next?"
   Header: "Next Steps"
   Options:
   - "Review and edit" - Open rubric for manual editing
   - "Generate pilot worksheet" - Create pilot testing materials
   - "Generate calibration pack" - Create scorer calibration materials
   - "Create scoring template" - Generate JSON scoring template
   - "Done" - Finish rubric creation
   ```

---

## Pilot Testing Protocol

**REQUIRED before deploying any new rubric at scale.**

See `rules/pilot-testing.md` for the complete pilot testing worksheet template.

See `rules/calibration-pack.md` for the scorer calibration pack template.

---

## Rubric Maintenance Lifecycle

### Maintenance Schedule

| Trigger | Action | Owner |
|---------|--------|-------|
| After every 10 uses | Review scorer feedback, identify pain points | Rubric Owner |
| Quarterly | Analyze score distributions for ceiling/floor effects | Rubric Owner |
| Annually | Full validity review against current standards | Domain Expert |
| When aligned standards change | Immediate revision to maintain alignment | Rubric Owner |
| Inter-rater agreement drops below 80% | Clarify ambiguous criteria, retrain scorers | Rubric Owner |
| New edge case identified | Add to anchor examples, consider criterion update | Rubric Owner |

### Score Distribution Analysis

Monitor for these warning signs:

| Pattern | Indicates | Action |
|---------|-----------|--------|
| >80% items score in top band | Ceiling effect - criteria too easy | Raise standards or add discrimination |
| >80% items score in bottom band | Floor effect - criteria too hard | Lower standards or review fairness |
| Bimodal distribution | Two distinct populations | Consider separate rubrics or review criteria |
| Single criterion always 0 or max | Poor discrimination | Revise criterion or anchor examples |

### Version Numbering

- **Major version (X.0):** Structural changes (categories added/removed, point totals changed)
- **Minor version (X.Y):** Criteria clarifications, anchor example updates, weight adjustments
- **Patch version (X.Y.Z):** Typo fixes, formatting corrections

---

## Error Handling

| Error | Resolution |
|-------|------------|
| Invalid template name | Display available templates and prompt for selection |
| Source file not found | Prompt for correct file path |
| Incomplete questionnaire | Allow partial save and resume |
| Invalid point allocation | Flag issue, show what doesn't sum correctly, suggest corrections |
| Weights don't sum to 100% | Automatically normalize or prompt for adjustment |
| Missing anchor examples | Block generation until examples provided |
| Critical barrier without threshold | Prompt for threshold definition |

---

## Related Skills

- `/score-bylaw` - Score using existing bylaw assessment rubric
- `/verify-citations` - Verify rubric source citations
- `/socratic-transform` - Convert rubric into learning framework
