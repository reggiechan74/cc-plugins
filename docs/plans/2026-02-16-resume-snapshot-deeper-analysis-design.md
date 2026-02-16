# Resume Snapshot: Deeper Analysis Enhancement

**Date:** 2026-02-16
**Plugin:** resume-snapshot
**Scope:** Single-command enhancement (no new files beyond `resume-snapshot.md`)

## Problem

The current resume-snapshot command collects solid repository metadata but produces a surface-level portfolio entry. It lacks:

- **Code quality evidence** — no test ratios, type safety signals, or error handling analysis
- **Complexity insight** — no identification of where complexity lives or whether it's justified
- **Architecture visualization** — no diagram showing module relationships
- **Evolution narrative** — no analysis of development cadence, churn hotspots, or refactoring maturity

## Approach: Two-Pass Architecture

Split analysis into raw data collection (bash commands) and intelligent reasoning (Claude synthesis). This plays to Claude's strengths — pattern recognition, narrative synthesis, contextual reasoning — while keeping the plugin self-contained.

## Design

### Phase 1 Additions: New Data Collection Steps

Three new bash blocks appended after the existing 1e.

#### 1f. Complexity Hotspots

Identify the largest and most complex source files:

- Top 15 source files by line count (excluding generated/vendor directories)
- Function/method count per file (grep for `def`/`function`/`func`/`fn` patterns, language-aware)
- Max indentation depth per file (proxy for nesting complexity)

#### 1g. Evolution Analysis

Git history signals for development narrative:

- Top 15 most-changed files by commit count (churn hotspots)
- Files with highest add+delete churn (refactoring indicators)
- Commit frequency by month (development cadence timeline)
- Recent vs old code ratio (files modified in last 90 days vs total)

#### 1h. Import/Dependency Mapping

Raw material for pattern detection and architecture diagram:

- All import/require/use/include statements with source file paths
- Language-aware grep covering Python, JS/TS, Go, Rust, Java, Ruby, C/C++
- Limited to first 200 results to avoid overwhelming context

### New Phase 2.5: Analyze Codebase Intelligence

Inserted between Phase 2 (Read Key Files) and Phase 3 (Synthesize). This is an explicit instruction block — Claude reasons over everything collected so far with no new tool calls.

Produces four internal analyses that feed into Phase 3:

#### 1. Complexity Assessment

From file size rankings + function counts + nesting depth:

- The 3-5 most complex modules and what makes them complex
- Whether complexity is concentrated or distributed
- Complexity-to-test correlation (are the most complex files also the most tested?)

#### 2. Design Pattern Detection

From import graphs + directory structure + naming conventions:

- Architectural patterns (MVC, layered, plugin-based, pipeline, event-driven, etc.)
- Code organization strategy (by feature, by layer, by domain)
- Abstraction quality signals (deep vs shallow modules, interface patterns)

#### 3. Evolution Narrative

From churn data + commit cadence + file age:

- Development phases (initial build, rapid iteration, stabilization, maintenance)
- Refactoring maturity (high churn on old files = active refactoring)
- Hot spots that may indicate technical debt vs active development

#### 4. Architecture Diagram

From import mapping + directory tree:

- ASCII box-and-arrow diagram showing major modules and their relationships
- Direction of dependencies (which modules depend on which)
- External integration points marked separately

### Phase 3 Changes: Expanded Output Template

Keep all 5 existing sections. Add 3 new sections after "Technical Sophistication":

#### New: Code Quality Evidence

```markdown
**Code Quality Evidence**:
- **Test Coverage**: <test-to-source file ratio, test framework(s) used, what's tested vs untested>
- **Type Safety**: <type annotations/TypeScript usage, strictness level>
- **Error Handling**: <patterns observed, consistency, coverage of failure paths>
- **Complexity Profile**: <where complexity lives, whether it's justified, complexity-to-test correlation>
```

#### New: Architecture

```markdown
**Architecture**:
\```
  +------------+     +------------+
  | Module A   |---->| Module B   |
  +------------+     +-----+------+
                           |
                      +----v------+
                      | Module C  |---> [External API]
                      +-----------+
\```
<1-2 sentence caption explaining the key architectural insight>
```

#### New: Codebase Evolution

```markdown
**Codebase Evolution**:
- **Timeline**: <first commit> -> <last commit> (<duration>)
- **Development Phases**: <narrative, e.g., "rapid prototyping Jan-Mar, stabilization Apr-May">
- **Churn Hotspots**: <top 3 most-changed files and what that signals>
- **Refactoring Maturity**: <evidence of intentional cleanup vs accumulating debt>
```

#### Tweak: Development Approach

Cross-references the Evolution section rather than duplicating timeline/cadence data. Focuses on methodology signals (solo vs collaborative, AI-assisted, branching strategy) that aren't covered by Evolution.

### Unchanged

- Phase 1 steps 1a-1e (git metadata, file stats, directory tree, LOC, infrastructure)
- Phase 2 (Read Key Files)
- Phase 4 (Write Output)
- `--output` argument handling
- Synthesis rules (honesty, specificity, status/license/emoji heuristics)
- Plugin structure (single command, no agents/skills/hooks)

## Complete Phase Map

```
Phase 1: Collect Repository Metadata
  1a. Git metadata              (unchanged)
  1b. File statistics            (unchanged)
  1c. Directory tree             (unchanged)
  1d. Lines of code by language  (unchanged)
  1e. Infrastructure/tooling     (unchanged)
  1f. Complexity hotspots        (NEW)
  1g. Evolution analysis         (NEW)
  1h. Import/dependency mapping  (NEW)

Phase 2: Read Key Files           (unchanged)

Phase 2.5: Analyze Codebase Intelligence  (NEW)
  -> Complexity assessment
  -> Design pattern detection
  -> Evolution narrative
  -> ASCII architecture diagram

Phase 3: Synthesize Portfolio Entry
  - Header (repo name, emoji, status, license, commits)
  - Description                  (unchanged)
  - Technical Architecture       (unchanged)
  - Technical Sophistication     (unchanged)
  - Code Quality Evidence        (NEW)
  - Architecture (ASCII diagram) (NEW)
  - Codebase Evolution           (NEW)
  - Skills Demonstrated          (unchanged)
  - Business Impact              (unchanged)
  - Development Approach         (tweaked)

Phase 4: Write Output             (unchanged)
```
