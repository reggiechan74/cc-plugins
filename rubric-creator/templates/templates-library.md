# Rubric Templates Library

Reference library for `/create-rubric` command. Contains detailed template definitions for each supported domain with professional-grade validity, reliability, and fairness controls.

---

## Table of Contents

- [Template: regulatory-compliance](#template-regulatory-compliance)
- [Template: document-quality](#template-document-quality)
- [Template: code-review](#template-code-review)
- [Template: vendor-evaluation](#template-vendor-evaluation)
- [Template: risk-assessment](#template-risk-assessment)
- [Template: performance-review](#template-performance-review)
- [Template: research-quality](#template-research-quality)
- [Customization Guidelines](#customization-guidelines)
- [Anchor Example Standards](#anchor-example-standards)
- [Inter-Rater Reliability Benchmarks](#inter-rater-reliability-benchmarks)

---

## Template: regulatory-compliance

**Purpose:** Assess compliance with regulations, bylaws, policies, or legal requirements.

**Total Points:** 250
**Categories:** 6

### Alignment Statement

**This rubric measures:** Regulatory feasibility and compliance level for proposed activities under applicable legal frameworks.

**Typically aligned with:**
- Municipal bylaws and zoning regulations
- Provincial/state statutes
- Federal regulations
- Industry-specific compliance standards

### Category Structure

| # | Category | Points | Weight | Criteria | Justification |
|---|----------|--------|--------|----------|---------------|
| 1 | Permitted Activities & Scope | 50 | 20% | 5 | Foundational; if activities aren't permitted, other factors are moot |
| 2 | Dimensional/Quantitative Requirements | 50 | 20% | 7 | Objective, measurable compliance factors |
| 3 | Technical & Operational Standards | 60 | 24% | 8 | Core operational viability |
| 4 | Regulatory Process & Approvals | 40 | 16% | 8 | Pathway to implementation |
| 5 | Regulatory Clarity & Definitions | 30 | 12% | 2 | Affects interpretation risk |
| 6 | External Jurisdiction Overlay | 20 | 8% | 4 | Secondary constraint layer |

### Criteria Details with Anchor Examples

**Category 1: Permitted Activities & Scope (50 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 1A1. Number/type of permitted zones | 0-10 | **10:** "Commercial, Industrial, Employment, and Utility zones all permit the activity" / **0:** "Activity prohibited in all zones" |
| 1A2. Geographic extent of permissions | 0-10 | **10:** ">50% of municipality in permitted zones" / **0:** "No permitted zones exist" |
| 1A3. Strategic location quality | 0-10 | **10:** "All permitted zones along major highways (>40,000 AADT)" / **0:** "No data available or no permitted zones" |
| 1B1. Special provisions for target use | 0-10 | **10:** "Explicit favorable provisions with relaxed standards" / **0:** "Target use explicitly excluded" |
| 1B2. Provision favorability vs. general rules | 0-10 | **10:** "More permissive than general zones" / **0:** "N/A or prohibited" |

**Category 2: Dimensional/Quantitative Requirements (50 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 2A1. Primary setback/buffer | 0-6 | **6:** "<5m from property line" / **0:** "Not specified or >50m" |
| 2A2. Secondary zone buffer | 0-6 | **6:** "<30m from residential" / **0:** "Not specified or >200m" |
| 2A3. ROW/boundary setbacks | 0-6 | **6:** "<10m from road ROW" / **0:** "Not specified or >100m" |
| 2A4. Spacing requirements | 0-6 | **6:** "<300m minimum spacing" / **0:** "Not specified or >2000m" |
| 2A5. Critical location setbacks | 0-6 | **6:** "<30m from intersection" / **0:** "Not specified or >200m" |
| 2B. Maximum size/area | 0-10 | **10:** "≥30 m² permitted" / **0:** "<5m² or prohibited" |
| 2C. Maximum height/scale | 0-10 | **10:** "≥15m permitted" / **0:** "<3m or prohibited" |

**Category 3: Technical & Operational Standards (60 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 3A1. Primary technical limit (peak) | 0-8 | **8:** "≥8000 NITs daytime permitted" / **0:** "Not specified or prohibited" |
| 3A2. Secondary technical limit (off-peak) | 0-8 | **8:** "500-1000 NITs nighttime with auto-dimming" / **0:** "Not specified or prohibited" |
| 3A3. Adaptive technology provisions | 0-5 | **5:** "Automatic dimming explicitly encouraged" / **0:** "Not addressed" |
| 3A4. Measurement & enforcement | 0-4 | **4:** "Clear quantitative standards with enforcement procedures" / **0:** "Not addressed" |
| 3B. Operational timing | 0-20 | **20:** "<6 second minimum dwell" / **0:** "Static only or not specified" |
| 3C1. Operational mode restrictions | 0-6 | **6:** "Instant transitions explicitly allowed" / **0:** "Not addressed" |
| 3C2. Transition requirements | 0-5 | **5:** "<2 second transitions allowed" / **0:** "Not addressed" |
| 3C3. Prohibited operations | 0-4 | **4:** "Animation/video explicitly allowed" / **0:** "Explicitly prohibited or not addressed" |

**Category 4: Regulatory Process & Approvals (40 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 4A1. Timeline certainty | 0-6 | **6:** "60 days from complete application" / **0:** "No permitting process exists" |
| 4A2. Approval type/authority | 0-6 | **6:** "Ministerial/as-of-right approval" / **0:** "No approval process or impossible" |
| 4A3. Application requirements clarity | 0-4 | **4:** "Complete checklist published" / **0:** "Not specified" |
| 4A4. Appeal mechanism | 0-4 | **4:** "Clear appeal to tribunal with procedures" / **0:** "Not addressed" |
| 4B1. Minor variance availability | 0-6 | **6:** "Committee of Adjustment with criteria" / **0:** "Not addressed" |
| 4B2. Major variance/rezoning | 0-5 | **5:** "Clear process with reasonable likelihood" / **0:** "Not addressed" |
| 4B3. Variance track record | 0-4 | **4:** "Evidence of approved similar variances" / **0:** "Not assessed or prohibition makes moot" |
| 4C. Fee structure | 0-5 | **5:** "<$5,000 total fees" / **0:** "Not specified" |

**Category 5: Regulatory Clarity & Definitions (30 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 5A. Primary activity definition | 0-15 | **15:** "Comprehensive definition with technical terms and clear distinctions" / **0:** "Not defined" |
| 5B. Secondary classification definition | 0-15 | **15:** "Clear definition with examples and criteria" / **0:** "Not defined" |

**Category 6: External Jurisdiction Overlay (20 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 6A1. External jurisdiction trigger | 0-5 | **5:** "No external overlay or >800m trigger" / **0:** "Blanket requirement or not addressed" |
| 6A2. External process clarity | 0-5 | **5:** "Clear process documented with contact info" / **0:** "Not addressed despite jurisdiction presence" |
| 6A3. External processing timeline | 0-5 | **5:** "≤60 days or no external approval needed" / **0:** "N/A" |
| 6A4. External approval likelihood | 0-5 | **5:** "Routine/automatic if criteria met" / **0:** "N/A" |

### Critical Barriers

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| 1A1 (Zone permissions) | Score = 0 | Automatic fail - activity prohibited |
| 1B1 (Special provisions) | Score = 0 (explicit exclusion) | Automatic fail - target use excluded |
| Category 1 Total | = 0 | Trigger prohibition cascade for Categories 2-3 |

### Interpretation Bands

| Score | Rating | Meaning | Recommended Action |
|-------|--------|---------|-------------------|
| 85-100% | Highly Favorable | Strong feasibility; minimal barriers | Proceed with standard application |
| 70-84% | Favorable | Good feasibility; standard approach viable | Proceed with minor accommodations |
| 55-69% | Moderate | Conditional feasibility; constraints exist | Site-specific analysis required |
| 40-54% | Restrictive | Limited feasibility; major barriers | Creative solutions or variance needed |
| 25-39% | Very Restrictive | Very limited; substantial barriers | Consider alternative jurisdictions |
| 0-24% | Prohibitive | Not feasible; prohibition in effect | Seek bylaw amendment or relocate |

### Special Rules

1. **Third-Party Focus:** Assess off-premise/billboard advertising, NOT on-premise signage
2. **Explicit Specification:** Score only explicit bylaw statements, not inferences
3. **General Provisions Apply:** "All signs" rules apply unless explicitly excluded
4. **Prohibition Cascade:** When Cat 1 = 0, score Cats 2-3 on general provisions only
5. **External Jurisdiction Defaults:** Score 0 when not addressed (flags uncertainty)

### Bias Review Findings

**Content Bias:** Template is jurisdiction-neutral; adjust examples for local context.
**Structural Bias:** Lower scores for "not specified" may disadvantage newer/smaller municipalities with less developed bylaws.
**Mitigation:** Note in rationale when low scores reflect regulatory silence vs. prohibition.

---

## Template: document-quality

**Purpose:** Evaluate quality of reports, proposals, technical documents, or deliverables.

**Total Points:** 200
**Categories:** 6

### Alignment Statement

**This rubric measures:** Document completeness, accuracy, and communication effectiveness for professional deliverables.

**Typically aligned with:**
- Professional writing standards
- Organizational style guides
- Industry documentation requirements
- Academic or technical publication standards

### Category Structure

| # | Category | Points | Weight | Criteria | Justification |
|---|----------|--------|--------|----------|---------------|
| 1 | Content Completeness | 50 | 25% | 5 | Missing content cannot be compensated by quality |
| 2 | Technical Accuracy | 50 | 25% | 5 | Errors undermine credibility and utility |
| 3 | Structure & Organization | 30 | 15% | 4 | Affects usability but not substance |
| 4 | Writing Quality & Clarity | 30 | 15% | 4 | Communication effectiveness |
| 5 | Citations & Evidence | 20 | 10% | 3 | Supports claims but secondary to content |
| 6 | Formatting & Presentation | 20 | 10% | 3 | Professional appearance, lowest priority |

### Criteria Details with Anchor Examples

**Category 1: Content Completeness (50 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 1A. Scope coverage | 0-15 | **15:** "All required topics addressed with appropriate depth" / **0:** "Major required sections missing" |
| 1B. Depth of analysis | 0-12 | **12:** "Analysis exceeds requirements with insightful detail" / **0:** "Surface-level treatment only" |
| 1C. Key findings/conclusions | 0-10 | **10:** "Clear, actionable conclusions with supporting rationale" / **0:** "No conclusions stated" |
| 1D. Recommendations | 0-8 | **8:** "Specific, prioritized recommendations with implementation guidance" / **0:** "No recommendations" |
| 1E. Limitations acknowledged | 0-5 | **5:** "Honest assessment of constraints and assumptions" / **0:** "No limitations discussed" |

**Category 2: Technical Accuracy (50 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 2A. Factual correctness | 0-15 | **15:** "All facts verified and accurate" / **0:** "Multiple significant factual errors" |
| 2B. Methodology soundness | 0-12 | **12:** "Appropriate methods well-executed" / **0:** "Methodology fundamentally flawed" |
| 2C. Data quality | 0-10 | **10:** "Reliable, current data from authoritative sources" / **0:** "Unreliable or outdated data" |
| 2D. Calculations/analysis | 0-8 | **8:** "All computations correct and reproducible" / **0:** "Calculation errors affect conclusions" |
| 2E. Terminology precision | 0-5 | **5:** "Technical terms used correctly throughout" / **0:** "Pervasive terminology errors" |

**Category 3: Structure & Organization (30 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 3A. Logical flow | 0-10 | **10:** "Ideas progress coherently with clear transitions" / **0:** "Disorganized, hard to follow" |
| 3B. Section organization | 0-8 | **8:** "Clear, appropriately-sized sections with descriptive headings" / **0:** "No sections or illogical groupings" |
| 3C. Navigation aids | 0-7 | **7:** "TOC, headers, cross-refs enable easy navigation" / **0:** "No navigation aids" |
| 3D. Executive summary | 0-5 | **5:** "Effective standalone overview of key points" / **0:** "No executive summary" |

**Category 4: Writing Quality & Clarity (30 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 4A. Clarity of expression | 0-10 | **10:** "Complex ideas explained clearly and concisely" / **0:** "Unclear, confusing prose" |
| 4B. Conciseness | 0-8 | **8:** "No unnecessary content, every sentence adds value" / **0:** "Excessive padding or repetition" |
| 4C. Grammar & mechanics | 0-7 | **7:** "Error-free writing" / **0:** "Frequent errors impede comprehension" |
| 4D. Audience appropriateness | 0-5 | **5:** "Perfectly calibrated for intended readers" / **0:** "Wrong level (too technical or too basic)" |

**Category 5: Citations & Evidence (20 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 5A. Citation completeness | 0-10 | **10:** "All claims properly supported with citations" / **0:** "Unsupported claims throughout" |
| 5B. Source quality | 0-6 | **6:** "Authoritative, peer-reviewed, current sources" / **0:** "Unreliable or inappropriate sources" |
| 5C. Citation format consistency | 0-4 | **4:** "Uniform citation style throughout" / **0:** "Inconsistent or missing formats" |

**Category 6: Formatting & Presentation (20 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 6A. Visual consistency | 0-8 | **8:** "Uniform formatting throughout (fonts, spacing, styles)" / **0:** "Inconsistent formatting" |
| 6B. Tables & figures quality | 0-7 | **7:** "Clear, properly labeled, referenced in text" / **0:** "Missing labels, unclear visuals" |
| 6C. Professional appearance | 0-5 | **5:** "Polished, publication-ready appearance" / **0:** "Unprofessional appearance" |

### Critical Barriers

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| 2A (Factual correctness) | Score ≤ 3 | Automatic "Major Revision Required" |
| 2B (Methodology) | Score ≤ 3 | Automatic "Major Revision Required" |
| 1A (Scope coverage) | Score ≤ 3 | Automatic "Needs Work" |

### Interpretation Bands

| Score | Rating | Meaning | Recommended Action |
|-------|--------|---------|-------------------|
| 85-100% | Excellent | Publication/submission ready | Approve as-is |
| 70-84% | Good | Minor revisions needed | Approve with minor edits |
| 55-69% | Acceptable | Moderate revisions required | Return for revision |
| 40-54% | Below Standard | Significant revisions needed | Return with detailed feedback |
| 25-39% | Poor | Major rewrite required | Reject, provide guidance |
| 0-24% | Unacceptable | Fundamental issues | Reject, restart |

### Bias Review Findings

**Content Bias:** Criteria are domain-neutral; customize anchor examples for specific document types.
**Structural Bias:** "Executive summary" criterion may disadvantage informal documents where summaries aren't expected.
**Mitigation:** Mark criteria as N/A when document type doesn't require specific elements.

---

## Template: code-review

**Purpose:** Evaluate code quality, maintainability, security, and production-readiness.

**Total Points:** 150
**Categories:** 6

### Alignment Statement

**This rubric measures:** Code quality, correctness, security, and maintainability for software development contributions.

**Typically aligned with:**
- Team/organization coding standards
- Security best practices (OWASP)
- Performance benchmarks
- Testing requirements

### Category Structure

| # | Category | Points | Weight | Criteria | Justification |
|---|----------|--------|--------|----------|---------------|
| 1 | Functionality & Correctness | 40 | 27% | 4 | Code must work correctly |
| 2 | Code Quality & Readability | 30 | 20% | 4 | Maintainability over time |
| 3 | Security & Safety | 30 | 20% | 4 | Vulnerabilities create liability |
| 4 | Performance & Efficiency | 20 | 13% | 3 | User experience and cost |
| 5 | Testing & Coverage | 15 | 10% | 3 | Confidence in correctness |
| 6 | Documentation | 15 | 10% | 3 | Knowledge transfer |

### Criteria Details with Anchor Examples

**Category 1: Functionality & Correctness (40 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 1A. Requirements fulfilled | 0-15 | **15:** "All acceptance criteria met, demo-ready" / **0:** "Core functionality missing or broken" |
| 1B. Edge case handling | 0-10 | **10:** "All boundary conditions handled gracefully" / **0:** "Crashes on common edge cases" |
| 1C. Error handling | 0-10 | **10:** "Comprehensive error handling with informative messages" / **0:** "Unhandled exceptions crash the app" |
| 1D. Backwards compatibility | 0-5 | **5:** "No breaking changes to public APIs" / **0:** "Breaking changes without migration path" |

**Category 2: Code Quality & Readability (30 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 2A. Naming conventions | 0-8 | **8:** "Clear, consistent, self-documenting names" / **0:** "Cryptic single-letter variables, inconsistent style" |
| 2B. Code structure | 0-8 | **8:** "Well-organized, appropriate module/function boundaries" / **0:** "Monolithic functions, tangled dependencies" |
| 2C. Complexity management | 0-8 | **8:** "Appropriate abstraction, DRY principles applied" / **0:** "Copy-paste code, unnecessary complexity" |
| 2D. Style consistency | 0-6 | **6:** "Follows project conventions exactly" / **0:** "Ignores established patterns" |

**Category 3: Security & Safety (30 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 3A. Input validation | 0-10 | **10:** "All inputs validated/sanitized at boundaries" / **0:** "SQL injection or XSS vulnerabilities present" |
| 3B. Auth/authorization | 0-8 | **8:** "Correct access controls, no privilege escalation" / **0:** "Missing auth checks on sensitive operations" |
| 3C. Data protection | 0-7 | **7:** "Sensitive data encrypted, no secrets in code" / **0:** "Credentials hardcoded, PII exposed" |
| 3D. Dependency safety | 0-5 | **5:** "No known CVEs in dependencies" / **0:** "Critical vulnerabilities in dependencies" |

**Category 4: Performance & Efficiency (20 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 4A. Algorithm efficiency | 0-8 | **8:** "Optimal complexity for the problem" / **0:** "O(n³) when O(n) solution exists" |
| 4B. Resource usage | 0-7 | **7:** "Memory/CPU optimized, no leaks" / **0:** "Memory leaks or excessive resource consumption" |
| 4C. Scalability | 0-5 | **5:** "Handles 10x load without architecture changes" / **0:** "Falls over at modest scale" |

**Category 5: Testing & Coverage (15 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 5A. Test coverage | 0-6 | **6:** "Critical paths covered, >80% coverage" / **0:** "No tests for new code" |
| 5B. Test quality | 0-5 | **5:** "Meaningful assertions, clear test names" / **0:** "Tests that always pass or test nothing" |
| 5C. Edge case tests | 0-4 | **4:** "Boundary conditions explicitly tested" / **0:** "Only happy path tested" |

**Category 6: Documentation (15 pts)**

| Criterion | Points | Anchor Examples |
|-----------|--------|-----------------|
| 6A. Code comments | 0-6 | **6:** "Complex logic explained, why not what" / **0:** "No comments on non-obvious code" |
| 6B. API documentation | 0-5 | **5:** "All public interfaces documented with examples" / **0:** "No API docs" |
| 6C. README/setup | 0-4 | **4:** "Easy to get started, clear instructions" / **0:** "No setup instructions" |

### Critical Barriers

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| 3A (Input validation) | Score ≤ 2 | Automatic block - security risk |
| 3B (Auth) | Score ≤ 2 | Automatic block - security risk |
| 3C (Data protection) | Score = 0 | Automatic block - secrets exposed |
| 1A (Requirements) | Score ≤ 3 | Automatic "Needs Work" |

### Interpretation Bands

| Score | Rating | Meaning | Recommended Action |
|-------|--------|---------|-------------------|
| 85-100% | Production Ready | Merge immediately | Approve |
| 70-84% | Approved with Minor Changes | Small fixes needed | Approve with comments |
| 55-69% | Needs Work | Address issues before merge | Request changes |
| 40-54% | Significant Issues | Substantial rework | Request major changes |
| 25-39% | Major Concerns | Architecture/approach issues | Reject, discuss approach |
| 0-24% | Reject | Fundamental problems | Close, start over |

### Special Rules

1. **Security Blocker:** Any security criterion <3 = automatic "Needs Work" max
2. **Test Requirement:** No tests for new code = max 70% overall
3. **Breaking Change Flag:** Breaking changes require explicit maintainer approval

### Bias Review Findings

**Content Bias:** Criteria assume modern development practices; may disadvantage legacy codebases.
**Structural Bias:** Documentation weight (10%) may seem low for public APIs vs. internal tools.
**Mitigation:** Adjust weights based on code type (library vs. application vs. script).

---

## Template: vendor-evaluation

**Purpose:** Assess vendor proposals, RFP responses, or supplier capabilities.

**Total Points:** 200
**Categories:** 6

### Alignment Statement

**This rubric measures:** Vendor capability, value, and risk profile for procurement decisions.

**Typically aligned with:**
- Procurement policies
- RFP requirements
- Organizational risk tolerance
- Budget constraints

### Category Structure

| # | Category | Points | Weight | Criteria | Justification |
|---|----------|--------|--------|----------|---------------|
| 1 | Technical Capability | 50 | 25% | 5 | Must be able to deliver |
| 2 | Cost & Value | 40 | 20% | 4 | Budget constraints are real |
| 3 | Experience & References | 40 | 20% | 4 | Track record predicts future |
| 4 | Implementation Approach | 30 | 15% | 4 | How they'll deliver matters |
| 5 | Support & Maintenance | 20 | 10% | 3 | Long-term relationship |
| 6 | Risk & Compliance | 20 | 10% | 3 | Protect the organization |

### Critical Barriers

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| 6A (Regulatory compliance) | Score ≤ 2 | Automatic disqualification |
| 1A (Solution fit) | Score ≤ 3 | Automatic "Not Recommended" |
| Any mandatory requirement | Unmet | Automatic disqualification |

### Interpretation Bands

| Score | Rating | Meaning | Recommended Action |
|-------|--------|---------|-------------------|
| 85-100% | Highly Recommended | Clear frontrunner | Select pending negotiations |
| 70-84% | Recommended | Strong candidate | Include in final round |
| 55-69% | Conditionally Recommended | Viable with conditions | Consider if top choices unavailable |
| 40-54% | Not Recommended | Significant concerns | Exclude from consideration |
| 25-39% | Strongly Not Recommended | Major deficiencies | Do not engage |
| 0-24% | Disqualified | Does not meet minimum | Remove from process |

### Special Rules

1. **Mandatory Requirements:** Any unmet mandatory = automatic disqualification
2. **Cost Normalization:** Normalize all costs to common baseline (e.g., 5-year TCO)
3. **Reference Verification:** Unverifiable references score 0
4. **Conflict Check:** Scorer must attest to no vendor relationship

---

## Template: risk-assessment

**Purpose:** Evaluate project, operational, or financial risks.

**Total Points:** 100
**Categories:** 5

### Alignment Statement

**This rubric measures:** Risk severity, likelihood, and manageability for organizational decision-making.

**Typically aligned with:**
- Enterprise risk management frameworks
- Project risk registers
- Insurance and compliance requirements

### Category Structure

| # | Category | Points | Weight | Criteria | Justification |
|---|----------|--------|--------|----------|---------------|
| 1 | Probability of Occurrence | 25 | 25% | 3 | Likelihood drives prioritization |
| 2 | Impact Severity | 25 | 25% | 4 | Consequences drive urgency |
| 3 | Mitigation Feasibility | 20 | 20% | 3 | Can we actually address it? |
| 4 | Detection Capability | 15 | 15% | 2 | Can we see it coming? |
| 5 | Control Effectiveness | 15 | 15% | 2 | Do current controls work? |

### Critical Barriers

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| 2A (Financial impact) | Score ≥ 7 (catastrophic) | Automatic escalation to executive level |
| 2C (Reputational impact) | Score ≥ 6 | Automatic escalation to communications team |

### Interpretation Bands (INVERTED - Higher = More Risk)

| Score | Rating | Meaning | Recommended Action |
|-------|--------|---------|-------------------|
| 85-100% | Critical Risk | Immediate action required | Executive escalation, stop activities |
| 70-84% | High Risk | Priority mitigation needed | Dedicated team, weekly monitoring |
| 55-69% | Medium Risk | Mitigation plan required | Document and implement controls |
| 40-54% | Low-Medium Risk | Monitor and plan | Quarterly review |
| 25-39% | Low Risk | Acceptable with monitoring | Annual review |
| 0-24% | Negligible Risk | No action needed | Archive assessment |

### Special Rules

1. **Inverted Scale:** Higher scores = higher risk (opposite of other templates)
2. **Impact Multiplier:** Catastrophic impact + any probability = Critical
3. **Control Credit:** Strong existing controls can reduce effective risk level

---

## Template: performance-review

**Purpose:** Evaluate employee or team performance.

**Total Points:** 100
**Categories:** 6

### Alignment Statement

**This rubric measures:** Individual contribution to organizational goals and professional standards.

**Typically aligned with:**
- Job descriptions and role expectations
- Organizational values and competencies
- Individual goal agreements
- Professional development plans

### Category Structure

| # | Category | Points | Weight | Criteria | Justification |
|---|----------|--------|--------|----------|---------------|
| 1 | Goal Achievement | 25 | 25% | 3 | Primary measure of contribution |
| 2 | Quality of Work | 20 | 20% | 3 | Output standards matter |
| 3 | Collaboration & Communication | 20 | 20% | 3 | Team effectiveness |
| 4 | Initiative & Problem-Solving | 15 | 15% | 2 | Growth and adaptability |
| 5 | Professional Development | 10 | 10% | 2 | Future potential |
| 6 | Attendance & Reliability | 10 | 10% | 2 | Basic expectations |

### Critical Barriers

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| 6A (Attendance) | Score ≤ 1 | Performance improvement plan regardless of overall |
| 6B (Dependability) | Score ≤ 1 | Performance improvement plan regardless of overall |
| Any criterion | Score = 0 | Requires specific action plan for that area |

### Interpretation Bands

| Score | Rating | Meaning | Recommended Action |
|-------|--------|---------|-------------------|
| 85-100% | Exceeds Expectations | Exceptional performance | Consider promotion, bonus, recognition |
| 70-84% | Meets Expectations+ | Strong performance | Positive feedback, development opportunities |
| 55-69% | Meets Expectations | Satisfactory performance | Continue current trajectory |
| 40-54% | Needs Improvement | Below expectations | Coaching and support plan |
| 25-39% | Unsatisfactory | Significant concerns | Performance improvement plan |
| 0-24% | Does Not Meet | Performance action required | Formal disciplinary process |

### Special Rules

1. **Goal Weighting:** Individual goals may have different weights; normalize before scoring
2. **Role Adjustment:** Criteria weights vary by role (e.g., IC vs. manager)
3. **Probationary Status:** New employees scored against onboarding milestones
4. **Self-Assessment:** Employee self-rating should be captured separately

### Bias Review Findings

**Content Bias:** "Initiative" criterion may disadvantage cultures that value consensus over individual action.
**Structural Bias:** "Attendance" may disadvantage employees with disabilities or caregiving responsibilities.
**Mitigation:** Review accommodations before scoring; adjust expectations for documented circumstances.

---

## Template: research-quality

**Purpose:** Evaluate research papers, methodologies, or academic work.

**Total Points:** 200
**Categories:** 6

### Alignment Statement

**This rubric measures:** Scientific rigor, contribution significance, and communication quality for research outputs.

**Typically aligned with:**
- Journal or conference standards
- Disciplinary norms
- Institutional research guidelines
- Funding agency requirements

### Category Structure

| # | Category | Points | Weight | Criteria | Justification |
|---|----------|--------|--------|----------|---------------|
| 1 | Research Design & Methodology | 50 | 25% | 5 | Foundation of validity |
| 2 | Literature Review & Context | 40 | 20% | 4 | Situates contribution |
| 3 | Data Analysis & Findings | 40 | 20% | 4 | Core scientific work |
| 4 | Conclusions & Implications | 30 | 15% | 3 | Value of contribution |
| 5 | Citation Quality & Integrity | 20 | 10% | 3 | Academic honesty |
| 6 | Presentation & Clarity | 20 | 10% | 3 | Communication of findings |

### Critical Barriers

| Criterion | Threshold | Consequence |
|-----------|-----------|-------------|
| 5A (Citation accuracy) | Score ≤ 2 | Automatic rejection - integrity concern |
| 5C (Attribution) | Score = 0 | Automatic rejection - plagiarism |
| 1B (Methodology appropriateness) | Score ≤ 3 | Automatic "Major Revision" max |

### Interpretation Bands

| Score | Rating | Meaning | Recommended Action |
|-------|--------|---------|-------------------|
| 85-100% | Publication Ready | Accept as-is or minor edits | Accept / Minor Revision |
| 70-84% | Minor Revisions | Small improvements needed | Minor Revision |
| 55-69% | Major Revisions | Significant work required | Major Revision |
| 40-54% | Revise & Resubmit | Substantial rework | Reject with resubmission option |
| 25-39% | Reject | Fundamental issues | Reject |
| 0-24% | Not Suitable | Wrong venue or approach | Desk reject |

### Special Rules

1. **Methodology Threshold:** Category 1 < 50% = max overall 69%
2. **Citation Integrity:** Any plagiarism = automatic rejection
3. **Scope Alignment:** Score relative to stated contribution, not absolute standards
4. **Blind Review:** Scorer should not know author identity

---

## Customization Guidelines

When customizing any template:

1. **Preserve Structure:** Keep the category→subcategory→criterion hierarchy
2. **Maintain Totals:** Ensure points sum to template total
3. **Keep Proportions:** Similar category weights unless justified with documented rationale
4. **Update Bands:** Adjust interpretation bands to match domain context
5. **Document Changes:** Note all customizations in version history
6. **Provide Anchor Examples:** Every criterion level needs a concrete example
7. **Review for Bias:** Re-run bias checklist after customization
8. **Re-Pilot:** Major customizations require new pilot testing

---

## Anchor Example Standards

**Purpose:** Anchor examples ensure consistent scoring by providing concrete illustrations of each score level.

### Requirements

1. **Specificity:** Examples must be concrete, not abstract
   - ❌ "Good documentation"
   - ✅ "README includes installation, configuration, and API examples with working code snippets"

2. **Realism:** Examples must be plausible for the domain
   - ❌ "Perfect score on every metric"
   - ✅ "All 5 required sections present with >2 pages each"

3. **Contrast:** Adjacent levels must be clearly distinguishable
   - ❌ "Good" vs "Very Good"
   - ✅ "Meets 3 of 5 requirements" vs "Meets 5 of 5 requirements"

4. **Completeness:** Every score level needs an example
   - Including the 0 level ("Not specified", "Missing", "None")

### Format

```markdown
| Score | Description | Anchor Example |
|-------|-------------|----------------|
| **10** | [Best case] | *[Concrete example]* |
| **8** | [Good case] | *[Concrete example]* |
| **6** | [Acceptable] | *[Concrete example]* |
| **4** | [Below standard] | *[Concrete example]* |
| **2** | [Poor] | *[Concrete example]* |
| **0** | [Absent/Failing] | *[Concrete example]* |
```

---

## Inter-Rater Reliability Benchmarks

| Domain | Expected Kappa | Expected % Agreement | Notes |
|--------|---------------|---------------------|-------|
| Regulatory Compliance | ≥0.85 | ≥90% | Objective criteria, explicit evidence |
| Document Quality | ≥0.75 | ≥80% | Some subjectivity in quality judgments |
| Code Review | ≥0.80 | ≥85% | Mix of objective and subjective |
| Vendor Evaluation | ≥0.70 | ≥75% | Business judgment involved |
| Risk Assessment | ≥0.65 | ≥70% | Inherently probabilistic |
| Performance Review | ≥0.60 | ≥70% | High subjectivity, calibrate carefully |
| Research Quality | ≥0.70 | ≥75% | Disciplinary norms vary |

**Actions when below threshold:**
1. Identify criteria with highest disagreement
2. Clarify criterion descriptions and anchor examples
3. Conduct calibration session with problematic items
4. Consider splitting ambiguous criteria
5. Re-test reliability before deployment
