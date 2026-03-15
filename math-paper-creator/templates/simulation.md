---
name: Simulation Model
description: Monte Carlo, agent-based, and discrete-event simulation
keywords: [Monte Carlo, agent-based, discrete-event, stochastic, simulation, sampling]
---

# {title}

## Outline

### Introduction
System being simulated, why analytical solutions are insufficient,
and what the simulation aims to reveal.
**Symbols:** none

### System Description
Components, entities, and the environment. Define the index sets
representing agents, resources, or event types.
**Symbols:** Set

### State Variables
Quantities that describe the system state at any point in time.
Initial conditions and domains.
**Symbols:** Variable, Parameter

### Transition Rules
How the state evolves — transition probabilities, agent decision
rules, event-processing logic. The dynamics of the simulation.
**Symbols:** Expression, Constraint

### Input Distributions
Stochastic inputs driving the simulation — arrival rates, service
times, random shocks. Distribution families and parameters.
**Symbols:** Parameter

### Output Metrics
What is measured from simulation runs. Summary statistics, performance
indicators, and how they are computed from state trajectories.
**Symbols:** Expression, Objective

### Convergence Analysis (optional)
Number of replications, warm-up period, confidence interval
construction, variance reduction techniques.
**Symbols:** Parameter, Expression

### Conclusion
Summary of simulation design, key findings, limitations, and
sensitivity to input assumptions.
**Symbols:** none
