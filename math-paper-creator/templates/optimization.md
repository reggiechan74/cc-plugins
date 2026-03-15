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
