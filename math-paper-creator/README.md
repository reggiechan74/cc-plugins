# math-paper-creator

<!-- badges-start -->
![Version](https://img.shields.io/badge/version-0.5.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)
<!-- badges-end -->

A Claude Code plugin that turns mathematical papers into validated, executable models. You describe concepts in natural language — Claude formalizes them into rigorous mathematics with prose, LaTeX display math, and Python validation code, all in a single `.model.md` document. Every symbol is registered exactly once, every equation is tested against concrete data, and every section is validated before the next one begins.

## The Problem

Mathematical papers are written in LaTeX or Markdown, but the math is never tested. A typo in a subscript, an inconsistent variable name, or a constraint that contradicts an earlier definition — these errors are invisible until someone tries to implement the model. By then, the paper and the code have diverged, and reconciling them is expensive.

## The Solution

The meta-compiler embeds executable validation directly inside the paper. A `.model.md` file is a standard Markdown document with two additions:

- **`python:fixture` blocks** — small, realistic test scenarios (3-5 concrete set members with realistic parameter values)
- **`python:validate` blocks** — symbol registrations that declare sets, parameters, variables, expressions, constraints, and objectives using a Python API

When you run the checker, it executes the fixture data against the validation blocks and verifies:

- **No phantoms** — every referenced symbol is declared
- **No collisions** — every symbol name is unique across the entire document (sets, parameters, variables, expressions, constraints, and objectives share one namespace)
- **No index violations** — every indexed symbol references declared sets
- **No cycles** — no circular dependencies between expressions
- **Unit boundaries** — constraints don't mix incompatible units
- **Constraint satisfaction** — every constraint holds against the fixture data
- **Objective evaluation** — every objective produces a numeric value

If any check fails, the error is reported with the source line number. You fix it before moving on.

## Two Workflows

### Author a new paper (`/math-paper-creator:author`)

You describe a problem domain. Claude formalizes it section by section:

1. You provide a concept (vague or specific)
2. Claude writes a complete section: heading, prose, `$$...$$` display math, fixture data, validation code
3. Claude inserts it into the `.model.md` file and runs the checker
4. If the check fails, Claude fixes errors before presenting
5. You approve, request changes, or redirect
6. Next concept builds on the accumulated symbol registry

Each section is validated against all previous sections. A variable defined in section 1 can be referenced in section 5 — the checker ensures consistency across the entire document. A variable can only be defined once.

The author workflow includes template selection — choose a paper type to get a pre-defined section outline and structural checklist tailored to your problem domain.

### Review a paper (`/math-paper-creator:review`)

You have a draft paper (`.md`, `.model.md`, or `.pdf`) and want a mathematical coherence assessment before proceeding. Claude reviews it across five layers:

1. **Core model** — are the foundational definitions sound?
2. **Mathematical completeness** — are there gaps in the formalization?
3. **Internal consistency** — do definitions, constraints, and objectives align?
4. **Structure and organization** — does the paper flow logically?
5. **Prose and presentation** — is the exposition clear and precise?

Findings are saved to a `.review.md` file and can be discussed interactively. The author workflow is aware of review findings — if a review file exists, Claude consults it when writing new sections.

### Onboard an existing paper (`/math-paper-creator:onboard`)

You have a Markdown paper with `$$...$$` display math but no validation. Claude reads it section by section, proposes fixture + validate blocks for each, and inserts them after your approval. Same incremental validation — each section is checked before moving to the next.

## What You Get

When the paper is complete, `/math-paper-creator:compile` produces three artifacts:

| Artifact | What it is |
|----------|------------|
| **`paper.md`** | Clean publishable paper — all validation blocks stripped, only prose and math remain |
| **`runner.py`** | Standalone Python script with all fixture data and validation logic inlined — runs without the paper |
| **`report.txt`** | Validation report: symbol table, dependency graph, coverage metrics, test results |

The `runner.py` is immediately repeatable. You can run it in CI, share it with collaborators, or use it as the foundation for an implementation — the symbol registrations document every set, parameter, variable, expression, constraint, and objective in the model.

## Installation

```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install math-paper-creator@cc-plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/math-paper-creator:author [file]` | Author a new paper interactively — ideate, formalize, validate section-by-section |
| `/math-paper-creator:onboard <file>` | Convert an existing paper — wrap existing math with validation blocks |
| `/math-paper-creator:review [file]` | Review a draft paper for mathematical coherence — layered assessment with interactive discussion |
| `/math-paper-creator:check <file>` | Run validation pipeline against a `.model.md` document |
| `/math-paper-creator:status <file>` | Show symbol table, coverage, and orphan/phantom status |
| `/math-paper-creator:report <file>` | Generate full validation report |
| `/math-paper-creator:paper <file>` | Generate clean paper artifact (strips validation blocks) |
| `/math-paper-creator:compile <file>` | Produce all artifacts: clean paper, standalone runner, validation report |

## Templates

The author workflow offers 10 paper-type templates, each providing a pre-defined section outline and structural checklist:

| Template | Domain |
|----------|--------|
| Constrained Optimization | LP, IP, MIP, convex, network flow, assignment |
| Statistical Modeling | Regression, time series, Bayesian inference |
| Game-Theoretic Analysis | Nash equilibrium, mechanism design, auctions |
| Simulation Model | Monte Carlo, agent-based, discrete-event |
| Decision Analysis | Decision trees, utility theory, MCDA |
| Financial Pricing | Derivatives pricing, stochastic calculus, term structure |
| Actuarial Model | Life tables, loss distributions, reserving |
| Econometric Model | Structural models, GMM, panel data, IV |
| Queueing Model | M/M/1, networks, scheduling |
| Graph and Network Analysis | Centrality, flow, matching, clustering |

A universal structural checklist applies to all paper types, covering required and advisory items.

## Live Validation

When installed, the plugin automatically validates `.model.md` files every time Claude writes or edits one. Validation errors are hard blocks — Claude must fix them before continuing.

The hook runs in **authoring mode**: symbol conflicts, undefined references, index mismatches, and dimensional errors are hard blocks. Orphan symbols produce warnings only (the symbol may be used in a later section).

## The API

Every symbol is registered through a Python function call:

```python
from meta_compiler import Set, Parameter, Variable, Expression, Constraint, Objective, S, registry

Set("W", description="Set of workers")

Parameter("cap", index=["W"], domain="nonneg_real", units="hours",
          description="Capacity per worker")

Variable("x", index=["W", "T"], domain="continuous", bounds=(0, 1),
         units="hours", description="Hours assigned")

Expression("load",
           definition=lambda i: sum(x[i, t] for t in S("T")),
           index=["W"], units="hours",
           description="Total load per worker")

Constraint("cap_limit",
           expr=lambda i: sum(x[i, t] for t in S("T")) <= cap[i],
           over="W",
           description="Load cannot exceed capacity")

Objective("total_output",
          expr=lambda: sum(sum(x[i, t] for t in S("T")) for i in S("W")),
          sense="maximize",
          description="Maximize total productive hours")

registry.run_tests()
```

Constraints iterate over a single set via `over`. For multi-index constraints, iterate inner sets inside the lambda. Expression results cannot be indexed in constraint lambdas — inline the computation instead.

## Requirements

Python 3.10+ with the `meta_compiler` package available on the Python path. The package is included in this plugin directory.
