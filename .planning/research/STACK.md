# Technology Stack

**Project:** Meta-Compiler for Domain-Specific Constrained Optimization Systems
**Researched:** 2026-03-09

## Recommended Stack

### Core Runtime: Python 3.12+

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python | 3.12+ | Runtime language | Required by OR-Tools, Z3, scipy. 3.12 is the sweet spot: all deps support it, good perf, stable. Avoid 3.13+ until OR-Tools confirms support. | HIGH |

**Rationale:** The entire optimization/verification ecosystem is Python-native. No TypeScript alternative exists for OR-Tools CP-SAT or Z3 bindings. The plugin's Python runtime (`meta_compiler/`) runs via subprocess from Claude Code slash commands.

---

### Solver Stack

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| ortools (CP-SAT) | 9.15.6755 | Primary solver: combinatorial/assignment optimization | Best-in-class for CP-SAT problems. Clean Python API via `CpModel`/`CpSolver`. Single `pip install ortools` with no system binaries. Directly maps from typed IR constraint representations. Active development (Jan 2026 release). | HIGH |
| scipy | 1.17.0 | LP relaxations, sensitivity analysis, numerical utilities | `scipy.optimize.linprog` with HiGHS backend for LP relaxations. `scipy.optimize.minimize` for continuous sensitivity sweeps. Already ubiquitous in Python environments. | HIGH |

**Do NOT use for MVP:**
- **Pyomo** -- Phase 2. Heavier dependency, requires separate solver binaries (GLPK/CBC/Gurobi). Adds complexity without benefit for CP-SAT-class problems.
- **PuLP** -- Redundant with OR-Tools for MILP. Less capable API. No CP-SAT support.
- **CVXPY** -- Phase 2. For convex continuous families only, which are out of MVP scope.
- **Gurobi/CPLEX** -- Commercial licenses. Not distributable in an open-source plugin.

---

### Verification and Proof Stack

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| z3-solver | 4.16.0.0 | SMT-based finite logical verification | Microsoft's Z3 is the standard SMT solver. Python bindings via `pip install z3-solver`. Handles: satisfiability checks, bounded model checking, finite-case verification, counterexample generation. Actively maintained (Feb 2026 release). | HIGH |
| LeanInteract | 0.x (2025) | Optional Lean 4 proof scaffold export | Python interface for Lean 4 REPL. Enables sending generated Lean code to a Lean server for type-checking. Phase 4-5 dependency only. | LOW |
| leanclient | 0.x (2025) | Optional Lean 4 language server wrapper | Alternative thin wrapper for Lean 4 LSP. Either this or LeanInteract; evaluate at Phase 5. | LOW |

**Do NOT use for MVP:**
- **CVC5** -- Z3 covers the same SMT space with better Python bindings and larger ecosystem. CVC5 is a Phase 2+ alternative if Z3 hits limitations.
- **Coq/Isabelle** -- Lean 4 is the proof assistant with the best Python interop story in 2025-2026. Coq's Python tooling is weaker. Isabelle has no meaningful Python bridge.

**Proof assistant strategy:** Z3 is the MVP verification layer (Phase 1). Lean 4 scaffolding is Phase 4-5. Generate `.lean` files with type signatures and proof obligations; users complete proofs in their Lean environment. Do not attempt to run Lean within the plugin runtime for MVP.

---

### DSL Parsing and Validation

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Pydantic | 2.12.5 | Schema validation, IR type system, model serialization | Industry standard for Python data validation. `BaseModel` subclasses define the IR node types. `model_validate()` for YAML-loaded dicts. Discriminated unions for constraint/objective type hierarchies. JSON Schema export for spec documentation. | HIGH |
| ruamel.yaml | 0.18.x | YAML parsing and round-trip editing | YAML 1.2 compliant (PyYAML only supports 1.1). Preserves comments during round-trip, critical for user-edited spec files. Stricter boolean handling avoids the PyYAML `Yes/No/On/Off` trap. | HIGH |

**Do NOT use:**
- **PyYAML** -- YAML 1.1 only. Silent boolean coercion bugs (`no` becomes `False`). No comment preservation. ruamel.yaml is strictly superior for a DSL parser.
- **jsonschema** -- Pydantic v2 subsumes jsonschema validation with better error messages, type coercion, and Python-native types. jsonschema adds a dependency for no benefit.
- **marshmallow** -- Legacy. Pydantic v2 is faster (Rust-backed core), has better type inference, and is the community standard for 2025+.
- **yaml2pydantic** -- Unnecessary indirection. Define Pydantic models directly in Python; they ARE the schema.

---

### IR Design and Graph Analysis

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python dataclasses + Pydantic | (stdlib + 2.12.5) | IR node definitions | Use Pydantic `BaseModel` for IR nodes that need validation (spec layer, constraint definitions). Use `@dataclass` for internal compiler nodes that need speed without validation overhead. Both serialize to dict/JSON trivially. | HIGH |
| NetworkX | 3.6.1 | Dependency graph analysis, cycle detection, structural validation | Needed for: circular dependency detection in derived expressions, acyclicity checks in reporting trees, constraint dependency ordering, graph-based structural validation. Mature, zero-dependency graph library. | HIGH |
| enum (stdlib) | -- | Epistemic status labels, constraint types, variable domains | `enum.Enum` subclasses for the 14 epistemic status labels, constraint hardness levels, variable domain types. Enforces closed vocabularies at the type level. | HIGH |

**IR architecture pattern:** The IR is a tree of Pydantic models (for serialization/validation) with a symbol table implemented as a flat `dict[str, SymbolEntry]`. Each IR node carries an `EpistemicStatus` enum. The IR serializes to YAML/JSON as the canonical artifact. All code generation reads from the serialized IR, never from in-memory compiler state.

---

### Code Generation

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Jinja2 | 3.1.6 | Template-based code generation | Generates: OR-Tools CP-SAT solver code, test suites, diagnostic harnesses, report markdown, Z3 verification scripts, Lean proof scaffolds. Template inheritance for domain-specific extensions. Compiled template caching for performance. | HIGH |

**Do NOT use:**
- **String concatenation / f-strings** -- Unmaintainable for multi-file code generation. No template inheritance. No escaping.
- **Mako** -- Less popular, less maintained, no meaningful advantage over Jinja2.
- **AST manipulation** -- Overkill. The generated code is formulaic solver boilerplate, not arbitrary Python transforms. Templates are cleaner.

---

### Testing and Quality

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| pytest | 9.0.2 | Test framework | Standard Python testing. Subtests merged into core in 9.0. Parametrize for constraint family coverage. Fixtures for IR factory methods. | HIGH |
| pytest-cov | 7.0.0 | Coverage reporting | Standard coverage plugin. | HIGH |

---

### Plugin Packaging (Claude Code)

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Claude Code plugin manifest | -- | Plugin registration | `.claude-plugin/plugin.json` with skills, commands, agents. Follows cc-plugins marketplace conventions. | HIGH |
| Markdown slash commands | -- | User-facing command surface | `/model:init`, `/model:compile`, etc. as `.md` files in `commands/` directory. Each command's markdown contains the prompt that invokes Claude with the Python runtime. | HIGH |
| subprocess (stdlib) | -- | Python runtime invocation | Slash commands invoke `python3 meta_compiler/cli.py <subcommand>` via subprocess. This is the seam between Claude (reasoning/formalization) and Python (execution/verification). | MEDIUM |
| pyproject.toml | -- | Python package metadata and dependency pinning | Modern Python packaging. `[project.dependencies]` pins all runtime deps. `pip install -e .` for development. | HIGH |

**Plugin architecture:** The plugin is a hybrid. The `.claude-plugin/` directory contains slash commands and skills (markdown). The `meta_compiler/` directory contains the Python package. Slash commands invoke Claude, which reasons about the spec and writes IR. Then Claude calls the Python runtime to compile, validate, solve, and verify. The IR (YAML files) is the interface contract.

**Dependency installation:** The plugin needs a setup step. A `/model:setup` command should run `pip install -e ./meta-compiler/meta_compiler` (or `pip install ortools scipy z3-solver ruamel.yaml pydantic networkx jinja2`) in the user's Python environment. This is a one-time cost.

---

## Full Dependency List

### Runtime Dependencies

```bash
pip install \
  ortools==9.15.6755 \
  scipy>=1.17.0 \
  z3-solver>=4.16.0.0 \
  pydantic>=2.12.5 \
  "ruamel.yaml>=0.18" \
  networkx>=3.6.1 \
  Jinja2>=3.1.6
```

### Development Dependencies

```bash
pip install -D \
  pytest>=9.0.2 \
  pytest-cov>=7.0.0 \
  ruff>=0.9.0 \
  mypy>=1.14.0
```

### Phase 2+ Dependencies (NOT for MVP)

```bash
# Phase 2: Additional solver backends
pip install pyomo cvxpy

# Phase 4-5: Proof assistant interop
pip install lean-interact  # or leanclient
```

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Solver | OR-Tools CP-SAT | Pyomo | Pyomo needs external solver binaries; CP-SAT is self-contained. Phase 2. |
| Solver | OR-Tools CP-SAT | PuLP | Weaker API, no CP-SAT support, redundant with OR-Tools MILP |
| YAML parser | ruamel.yaml | PyYAML | YAML 1.1 only, silent boolean bugs, no comment preservation |
| Validation | Pydantic v2 | marshmallow | Legacy, slower, weaker type system |
| Validation | Pydantic v2 | jsonschema | Pydantic subsumes it with better DX |
| SMT solver | Z3 | CVC5 | Z3 has better Python bindings, larger community. CVC5 is Phase 2 alternative |
| Proof assistant | Lean 4 | Coq | Lean 4 has better Python interop (LeanInteract), more active community in 2025-2026 |
| Proof assistant | Lean 4 | Isabelle | No Python bridge |
| Code gen | Jinja2 | Mako/string concat | Jinja2 is standard, has template inheritance, maintained |
| Graph lib | NetworkX | igraph | NetworkX is pure Python, lighter dep, sufficient for structural validation |

---

## Version Pinning Strategy

Pin **major.minor** for stability, allow patch updates:

```toml
[project]
requires-python = ">=3.12,<3.14"

[project.dependencies]
ortools = ">=9.15,<10"
scipy = ">=1.17,<2"
z3-solver = ">=4.16,<5"
pydantic = ">=2.12,<3"
"ruamel.yaml" = ">=0.18"
networkx = ">=3.6,<4"
Jinja2 = ">=3.1,<4"
```

---

## Sources

- [OR-Tools PyPI](https://pypi.org/project/ortools/) -- v9.15.6755, Jan 2026
- [OR-Tools CP-SAT docs](https://developers.google.com/optimization/cp/cp_solver)
- [CP-SAT Primer](https://d-krupke.github.io/cpsat-primer/) -- community guide
- [z3-solver PyPI](https://pypi.org/project/z3-solver/) -- v4.16.0.0, Feb 2026
- [Z3 GitHub](https://github.com/Z3Prover/z3)
- [Pydantic docs](https://docs.pydantic.dev/latest/) -- v2.12.5, Nov 2025
- [ruamel.yaml PyPI](https://pypi.org/project/ruamel.yaml/)
- [NetworkX PyPI](https://pypi.org/project/networkx/) -- v3.6.1, Dec 2025
- [SciPy linprog docs](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html) -- v1.17.0
- [Jinja2 PyPI](https://pypi.org/project/Jinja2/) -- v3.1.6, Mar 2025
- [pytest PyPI](https://pypi.org/project/pytest/) -- v9.0.2, Dec 2025
- [LeanInteract GitHub](https://github.com/augustepoiroux/LeanInteract) -- Python interface for Lean 4
- [leanclient PyPI](https://pypi.org/project/leanclient/) -- thin Lean 4 LSP wrapper
- [Claude Code plugin docs](https://code.claude.com/docs/en/discover-plugins)
- [Claude Code plugin README](https://github.com/anthropics/claude-code/blob/main/plugins/README.md)
