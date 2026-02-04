# Research Foundation: "Team of Rivals" Architecture

Summary of the research paper by Vijayaraghavan et al. (2026) that provides the theoretical foundation for Code Coherence.

## Key Findings

### Single-Agent Limitations

**Baseline accuracy**: 60% on high-stakes tasks
**Primary failure mode**: Self-review is insufficient - the same reasoning that produced an error cannot reliably catch it
**Context contamination**: Raw data in LLM context causes hallucination and privacy risks

### Multi-Agent Architecture Results

**System accuracy**: 92.1% (67 percentage-point improvement)
**User-facing error rate**: 7.9% (vs 40% single-agent)
**Cost overhead**: +38.6% tokens
**Latency overhead**: +21.8% active time

### Three-Layer Critique System

| Layer | Scope | Catch Rate | Cumulative |
|-------|-------|------------|------------|
| L0: First Pass | Clean pass | 24.9% | 24.9% |
| L1: Inner Loop | Code + Chart | 87.8% | 90.8% |
| L2: Output | Quality validation | 14.6% | 92.1% |
| Residual | User rejected | 7.9% | - |

**Key insight**: Each layer catches errors the previous layer missed due to orthogonal failure modes

## Theoretical Foundations

### Swiss Cheese Model (Reason, 2000)

Multiple imperfect layers of defense achieve system reliability when holes are misaligned:
- Each layer has failure modes (holes)
- Holes don't align across layers
- Hazards cannot propagate through all layers simultaneously

**Application to AI**: Multiple critics with different specializations create defense-in-depth

### Shannon's Channel Capacity Theorem

Reliable communication over noisy channel achievable but at reduced bandwidth:
- Treat inter-agent communication as noisy channel
- Use redundancy (verbosity, retries) for reliability
- Accept throughput reduction for correctness guarantee

**Application to AI**: Retry loops and explicit verification trade speed for reliability

### Organizational Coherence

Coherence maintained by opposing forces holding outputs within acceptable zone:
- Planner pushes for completeness
- Executor pushes for pragmatic implementation
- Critic pushes for correctness and standards

**Result**: Conflicting incentives create boundaries preventing drift

## Architecture Components

### Specialized Agent Teams

- **Planners**: Generate execution strategies with pre-declared criteria
- **Executors**: Perform work with context isolation
- **Critics**: Validate outputs with veto authority
- **Experts**: Provide domain-specific guidance

### Remote Code Executor

Separation of reasoning from execution:
- Agents write code specifications
- Executor runs transformations remotely
- Only summaries return to agent context
- Prevents context contamination

### Hierarchical Veto Authority

- Critics can reject outputs entirely
- No self-certification allowed
- Failures trigger team-internal retry
- Persistent rejection escalates to user

## Evaluation Data

**Dataset**: 522 production sessions
**Domain**: Financial analysis (accounts payable reconciliation)
**Task complexity**: Multi-vendor invoice matching, PDF extraction, fuzzy matching

### Recovery Analysis

| Recovery Level | Sessions | Cost Overhead | Time Overhead |
|----------------|----------|---------------|---------------|
| Level 1 (1-2 retries) | 157 (40%) | 19.6% | 10.0% |
| Level 2 (3-5 retries) | 126 (32%) | 31.8% | 21.6% |
| Level 3 (6+ retries) | 109 (28%) | 48.1% | 27.4% |
| **Total** | **392** | **38.6%** | **21.8%** |

**Key finding**: 40% of recoveries happen within 1-2 iterations (efficient error correction)

### Error Types Caught

**Code Critique Inner Loop** (337 sessions):
- Missing required fields (invoice_number, date_of_issue, total_in_usd)
- Logic errors (wrong join conditions, incorrect aggregations)
- API misuse (incorrect parameters, missing error handling)

**Chart Critique** (7 sessions):
- Incorrect chart types
- Wrong axis configurations
- Misleading visualizations

**Output Critique** (7 sessions):
- Results violating pre-declared acceptance criteria
- Misalignment with user intent
- Format issues

### Comparison with Baselines

**Single-Agent** (10 trials):
- 60% accuracy on financial reconciliation
- High confidence in all outputs (no error signal)
- 1-2 minutes execution time

**Self-Verification** (5 trials):
- <60% accuracy (worse than no verification!)
- Model second-guesses correct answers
- 2-3 minutes execution time

**Multi-Agent (Code Coherence)** (20 trials):
- 90% accuracy
- Automatic error detection and retry
- 4.2 minutes execution time

## Implications for Practice

### When Overhead is Justified

**High-stakes domains**:
- Financial close (error propagates to regulatory filings)
- Security implementations (breach cost >> verification cost)
- Production deployments (downtime cost >> validation cost)

**Cost equation**: `overhead_cost < error_cost × error_probability_reduction`

### The 7% Residual Floor

Errors that escape all critics share characteristics:
- **Requirement ambiguity**: Correct implementation of misunderstood intent
- **Subjective preferences**: Technically valid but stylistically misaligned
- **Domain edge cases**: Context unavailable to any critic

**Interpretation**: 93% appears to be practical ceiling for automated systems

### Diminishing Returns

Fourth layer with equivalent effectiveness to L2 would:
- Reduce escape rate from 7.9% to 6.7%
- Save only 6 additional sessions
- Add latency and compute costs

**Optimal architecture**: Three critics across two layers

## Design Patterns

### Pre-Declared Acceptance Criteria

Define success before execution:
- Not emergent or subjective
- Explicit decision gates
- Mapped to critic veto authority

**Anti-pattern**: "Write good code and we'll see if it's acceptable"

### Context Isolation

Reasoning models never touch raw data:
- Agents write code specifications
- Executor runs against real data
- Only summaries return to context

**Benefits**:
- Working set >> context window
- No PII in LLM context
- Answers grounded in execution, not hallucination

### Hierarchical Veto

Decision-making follows strict hierarchy:
- Critics can reject (veto authority flows upward)
- Approvals escalate to next gate
- No horizontal consensus voting

**Anti-pattern**: Council-based voting where specialized critic can be outvoted

### Retry Without Replanning

Failed critique triggers internal retry:
- Team-internal improvement cycle
- User never sees intermediate failures
- Only approved outputs advance

**Efficiency**: Most errors corrected in 1-2 iterations

## References

Full paper: Vijayaraghavan, G., Jayachandran, P., Murthy, A., Govindan, S., & Subramanian, V. (2026). "If You Want Coherence, Orchestrate a Team of Rivals: Multi-Agent Models of Organizational Intelligence." arXiv:2601.14351 [cs.MA].

**Key citations**:
- Reason (2000): Swiss cheese model of system failures
- Shannon (1948): Channel capacity theorem
- Anthropic (2024): Building effective agents with sub-agent parallelization
