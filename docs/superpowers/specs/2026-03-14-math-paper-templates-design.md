# Math Paper Templates and Structural Checklist

**Date:** 2026-03-14
**Status:** Approved
**Scope:** math-paper-creator plugin — template files + author command update

## Problem

The `author` command creates math papers section by section but has no guidance on what a well-structured paper looks like. Users must know the right sections, order, and symbol progression themselves. There's no way to detect structural gaps (e.g., variables declared but never constrained) until the user manually reviews.

## Solution

Add 10 paper-type templates and 1 universal structural checklist as data files in `math-paper-creator/templates/`. Update the `author` command to present template selection at initialization and consult the checklist throughout authoring.

## Templates

### File Structure

```
math-paper-creator/
  templates/
    _checklist.md              # universal structural checklist
    optimization.md            # LP, IP, MIP, convex, network flow
    statistical.md             # regression, time series, Bayesian inference
    game-theoretic.md          # Nash equilibrium, mechanism design, auctions
    simulation.md              # Monte Carlo, agent-based, discrete-event
    decision-analysis.md       # decision trees, utility theory, MCDA
    financial-pricing.md       # derivatives pricing, stochastic calculus, term structure
    actuarial.md               # life tables, loss distributions, reserving
    econometric.md             # structural models, GMM, panel data, IV
    queueing.md                # M/M/1, networks, scheduling
    graph-network.md           # centrality, flow, matching, clustering
```

### Template Format

Each template is a Markdown file with YAML frontmatter and a section outline:

```markdown
---
name: <display name>
description: <one-line description>
keywords: [<searchable terms>]
---

# {title}

## Outline

### <Section Heading>
<Brief description of what goes in this section.>
**Symbols:** <symbol types typically introduced: Set, Parameter, Variable, Expression, Constraint, Objective, or "none">

### <Section Heading> (optional)
<Brief description.>
**Symbols:** <types>
```

Sections marked `(optional)` can be skipped without triggering checklist warnings. The `(optional)` marker may NOT be applied to Introduction or Conclusion — these are always required (see checklist). The `{title}` placeholder is replaced by the user's paper title.

Templates support `## Part` headings for multi-layer papers:

```markdown
## Part I: <Part Name>

### <Section>
...

## Part II: <Part Name>

### <Section>
...
```

### Example Template (Optimization)

```markdown
---
name: Constrained Optimization
description: Linear, integer, and mixed-integer programming models
keywords: [LP, IP, MIP, convex, network flow, assignment]
---

# {title}

## Outline

### Introduction
Purpose, motivation, and problem context. Frames the domain and explains
why a formal optimization model is needed.
**Symbols:** none

### Sets and Indices
Define the index sets over which the model operates (e.g., employees,
project types, time periods). These are the dimensions of the problem.
**Symbols:** Set

### Parameters
Exogenous inputs, coefficients, and given data. Everything the model
takes as given rather than choosing.
**Symbols:** Parameter

### Decision Variables
What the optimizer controls. Define the allocation, assignment, or
scheduling variables with their domains and bounds.
**Symbols:** Variable

### Derived Expressions
Computed quantities that simplify constraint and objective formulation.
Aggregations, ratios, weighted sums built from parameters and variables.
**Symbols:** Expression

### Constraints
Feasibility conditions the solution must satisfy. Capacity limits, demand
coverage, fairness bounds, logical requirements.
**Symbols:** Constraint

### Objective Function
What is being maximized or minimized. The single scalar that drives the
optimization.
**Symbols:** Objective

### Solution Properties (optional)
Dual interpretation, sensitivity analysis, special structure (totally
unimodular, network flow decomposition).
**Symbols:** Expression, Parameter

### Computational Notes (optional)
Solver considerations, relaxations, heuristic approximations, practical
implementation guidance.
**Symbols:** none

### Conclusion
Summary of the model, key assumptions, limitations, and potential
extensions.
**Symbols:** none
```

### Template List

| Template | Covers | Typical Use Cases |
|----------|--------|-------------------|
| optimization | LP, IP, MIP, convex, network flow | Workforce allocation, supply chain, portfolio construction |
| statistical | Regression, time series, Bayesian inference | Factor models, forecasting, causal inference |
| game-theoretic | Nash equilibrium, mechanism design, auctions | Market design, voting systems, contract theory |
| simulation | Monte Carlo, agent-based, discrete-event | Risk simulation, operational modeling, epidemic spread |
| decision-analysis | Decision trees, utility theory, MCDA | Capital budgeting, real options, scoring frameworks |
| financial-pricing | Derivatives pricing, stochastic calculus, term structure | Black-Scholes, interest rate models, credit risk |
| actuarial | Life tables, loss distributions, reserving | Insurance pricing, pension valuation, ruin theory |
| econometric | Structural models, GMM, panel data, IV | Labor economics, demand estimation, policy evaluation |
| queueing | M/M/1, networks, scheduling | Call centers, hospital flow, manufacturing lines |
| graph-network | Centrality, flow, matching, clustering | Social networks, transportation, assignment problems |

### "Other" Option

When no preset fits, the user selects "Other." The `author` command runs a discovery conversation:

1. What is the paper about?
2. What are the major parts or layers?
3. What mathematical structures are involved?

From the answers, Claude generates a custom outline on the fly, borrowing section patterns from whichever templates are relevant. The custom outline follows the same format (headings, descriptions, symbol types, optional markers, Part groupings). This is a best-effort feature — the quality of the generated outline depends on Claude's reasoning about the domain. The 10 preset templates are the primary value delivery; "Other" extends coverage to non-standard paper types.

## Universal Structural Checklist

File: `templates/_checklist.md`

The checklist is structural, not section-based. It checks completeness regardless of paper type.

**Evaluation mechanism:** The checklist is prompt-based. The `author` command reads `_checklist.md` and the current `.model.md` file, then reasons about whether each item is satisfied by examining the validate blocks and document structure. No compiler code changes are needed — Claude applies the rules by reading the file.

### Required (warnings at completion)

- At least one Set declared
- At least one Parameter declared with index referencing a declared Set
- At least one computable output (Expression, Constraint, or Objective)
- Every Variable referenced in at least one Constraint or Expression
- Every section with `$$...$$` display math also has a validate block in that section (one validate block per section, not per math block)
- Introduction section exists
- Conclusion section exists

### Advisories (informational, not blocking)

- Variables declared but no Objective — is this a scoring/classification model rather than optimization?
- Constraints declared but no Variables — are these validation rules on Parameters?
- More than 20 symbols with no Part/section grouping — consider organizing into parts
- Parameters with no units specified — intentional or missing?
- Sets declared but never used as an index — orphan sets

## Author Command Integration

### Template Selection (new Step 1.5, between initialization and opening section)

Template selection is inserted into the `author` command between the existing Step 1 (Initialize) and Step 2 (Opening section). It does not replace either step. The flow becomes:

1. **Step 1: Initialize** — create or resume the `.model.md` file (unchanged)
2. **Step 1.5: Template selection** (new) — present templates, select or generate outline
3. **Step 2: Opening section** — write the Introduction (unchanged, but now guided by the template)
4. **Step 3: Authoring loop** — section-by-section authoring (unchanged, but augmented with outline suggestions)

After creating or resuming the `.model.md` file, the `author` command:

1. Presents the 10 templates + "Other" as a numbered list with descriptions
2. User selects one
3. If preset: show the full outline, let the user reorder/remove/add sections before starting
4. If "Other": run discovery conversation, generate custom outline, present for approval
5. Store the selected template name and working outline in the `.model.md` frontmatter:
   ```yaml
   ---
   title: Workforce Optimization Model
   date: 2026-03-14
   template: optimization        # or "custom" for Other
   outline:                       # working section list
     - Introduction
     - Sets and Indices
     - Parameters
     - Decision Variables
     - Derived Expressions
     - Constraints
     - Objective Function
     - Conclusion
   ---
   ```

**Resume behavior:** When resuming an existing `.model.md`, the `author` command reads the `template` and `outline` fields from frontmatter. It compares the outline against sections already written in the document to determine which sections remain. If no template/outline fields exist (pre-template file), the command offers to select a template or continue without one.

### Outline as Orientation, Not Constraint

The outline is shown upfront for orientation. During authoring, the user can:
- Follow the outline in order
- Skip ahead or go back
- Add sections not in the outline
- Deviate freely — the outline is a guide, not a constraint

### Checklist Consultation

The `author` command consults the checklist at two points. This **augments** the existing symbol-based suggestion behavior (Step 3.6 in `author.md`), not replaces it. When the user asks "what's next?", the command:

1. Checks the outline for the next unwritten section (template-based suggestion)
2. Checks the structural checklist for gaps (checklist-based warning)
3. Reviews the symbol registry for missing dependencies (existing behavior, unchanged)

All three are combined into a single suggestion.

**At completion** — before offering to compile, the command runs the full checklist against the document and shows the status. Required items that fail produce warnings. Advisories are shown as informational notes.

## What Does NOT Change

- The compiler (`meta_compiler` Python package) — no code changes
- The `.model.md` file format — templates add optional frontmatter fields but don't change the block syntax
- The `onboard`, `check`, `compile`, `paper`, `report`, `status` commands — unchanged
- The validation pipeline — templates are consumed only by the `author` command

## Implementation Scope

1. Create 10 template files with section outlines appropriate to each paper type
2. Create `_checklist.md` with the structural checklist
3. Update `author.md` to add Step 1.5 (template selection), outline persistence in frontmatter, and checklist consultation between sections and at completion
