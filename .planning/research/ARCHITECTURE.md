# Architecture Patterns

**Domain:** Meta-compiler for constrained optimization systems (Claude Code plugin)
**Researched:** 2026-03-09

## Recommended Architecture

### High-Level: Hybrid Claude + Python Runtime

```
User <--> Claude Code slash commands (markdown)
              |
              v
         Claude (reasoning layer)
              |  writes/reads
              v
         IR files (YAML/JSON) <-- canonical seam
              |
              v
         Python runtime (meta_compiler/)
         |         |           |           |
         v         v           v           v
      Compiler  Validator   Solver     Verifier
      (IR->code) (structural) (OR-Tools) (Z3)
              |
              v
         Generated artifacts (Python code, reports, proof scaffolds)
```

Claude owns: spec understanding, formalization, IR authoring, report interpretation.
Python owns: compilation, validation, solving, verification, code generation.
IR (YAML) is the interface contract between the two.

### Component Boundaries

| Component | Responsibility | Communicates With | Technology |
|-----------|---------------|-------------------|------------|
| Slash commands | User-facing command surface | Claude reasoning | Markdown files in `commands/` |
| Skills/Agents | Claude prompt templates for formalization | Slash commands, IR files | Markdown files in `skills/`, `agents/` |
| Spec parser | Load YAML spec, validate against Pydantic schema | IR compiler | ruamel.yaml + Pydantic |
| IR compiler | Normalize spec into typed IR with symbol table | Spec parser, all downstream | Pydantic models, dataclasses |
| Structural validator | Check IR well-formedness | IR compiler | NetworkX (graph analysis), Pydantic |
| Code generator | Emit executable solver code from IR | IR, Jinja2 templates | Jinja2 |
| Solver runner | Execute generated code, extract solutions | Code generator | OR-Tools, scipy |
| Z3 verifier | Finite logical verification, counterexample search | IR | z3-solver |
| Report builder | Generate markdown reports from IR + solve results | All upstream | Jinja2 |
| Domain registry | Load domain templates, extend schema | Spec parser, IR compiler | YAML files + Pydantic |

### Data Flow

```
1. User invokes /model:init --> Claude creates spec template from domain
2. User fills spec YAML
3. /model:compile --> Claude validates intent, calls Python:
   a. Parser loads YAML, validates against Pydantic schema
   b. Compiler normalizes into IR (symbol table, constraint registry, etc.)
   c. Validator checks structural well-formedness
   d. Code generator emits OR-Tools CP-SAT Python file
   e. Returns: IR file + generated code + validation report
4. /model:solve --> Python runs generated solver code
   a. Returns: solution summary, objective values, assignments
5. /model:verify --> Python runs Z3 checks
   a. Returns: verification results with epistemic status labels
6. /model:report --> Python generates full technical report
```

## Patterns to Follow

### Pattern 1: IR as Single Source of Truth

**What:** All generated artifacts (code, reports, proof scaffolds) are derived from the serialized IR, never from in-memory compiler state or the original spec.

**When:** Always. This is the fundamental architectural invariant.

**Why:** Prevents implementation drift (Risk 5). If the generated code disagrees with the IR, the code is wrong. If the report disagrees with the IR, the report is wrong.

**Example:**
```python
# IR node definition
class ConstraintDef(BaseModel):
    name: str
    hardness: ConstraintHardness  # enum: hard, soft, derived, optional, policy
    expression: str
    index_sets: list[str]
    epistemic_status: EpistemicStatus
    provenance: str  # where this constraint came from

# Code generation reads from serialized IR
def generate_cpsat_constraint(constraint: ConstraintDef, symbols: SymbolTable) -> str:
    template = env.get_template(f"constraints/{constraint.hardness.value}.py.j2")
    return template.render(constraint=constraint, symbols=symbols)
```

### Pattern 2: Discriminated Unions for IR Node Types

**What:** Use Pydantic discriminated unions for polymorphic IR nodes (different variable types, constraint families, objective structures).

**When:** Any IR node that has subtypes with different fields.

**Example:**
```python
from pydantic import BaseModel, Discriminator, Tag
from typing import Annotated, Literal, Union

class BinaryVariable(BaseModel):
    kind: Literal["binary"] = "binary"
    name: str
    index_sets: list[str]

class IntegerVariable(BaseModel):
    kind: Literal["integer"] = "integer"
    name: str
    index_sets: list[str]
    lower_bound: int
    upper_bound: int

class ContinuousVariable(BaseModel):
    kind: Literal["continuous"] = "continuous"
    name: str
    index_sets: list[str]
    lower_bound: float
    upper_bound: float

DecisionVariable = Annotated[
    Union[BinaryVariable, IntegerVariable, ContinuousVariable],
    Discriminator("kind")
]
```

### Pattern 3: Registry Pattern for Extensibility

**What:** Constraints, objectives, and domain extensions register themselves into typed registries rather than being hardcoded.

**When:** Any extensible collection: constraint families, objective templates, domain modules, backend targets.

**Example:**
```python
class ConstraintRegistry:
    def __init__(self):
        self._constraints: dict[str, ConstraintDef] = {}

    def register(self, constraint: ConstraintDef) -> None:
        if constraint.name in self._constraints:
            raise DuplicateSymbolError(constraint.name)
        self._constraints[constraint.name] = constraint

    def get(self, name: str) -> ConstraintDef:
        if name not in self._constraints:
            raise UndefinedSymbolError(name)
        return self._constraints[name]

    def all(self) -> list[ConstraintDef]:
        return list(self._constraints.values())
```

### Pattern 4: Validation as Pipeline, Not Afterthought

**What:** Structural validation is a distinct compiler pass that runs after IR construction but before code generation. It produces a typed list of diagnostics (errors, warnings, info).

**When:** Always. Validation is a first-class feature per design brief section 15.

**Example:**
```python
@dataclass
class Diagnostic:
    severity: Literal["error", "warning", "info"]
    code: str  # e.g. "UNDEF_SYMBOL", "CIRCULAR_DEP"
    message: str
    location: str  # IR path, e.g. "constraints.capacity_limit"

class ValidationResult(BaseModel):
    diagnostics: list[Diagnostic]
    is_valid: bool  # True if no errors (warnings OK)

def validate_ir(ir: IntermediateRepresentation) -> ValidationResult:
    diagnostics = []
    diagnostics.extend(check_undefined_symbols(ir))
    diagnostics.extend(check_circular_dependencies(ir))
    diagnostics.extend(check_index_compatibility(ir))
    diagnostics.extend(check_impossible_bounds(ir))
    # ... more checks
    return ValidationResult(
        diagnostics=diagnostics,
        is_valid=not any(d.severity == "error" for d in diagnostics)
    )
```

### Pattern 5: Epistemic Status as Type-Level Concern

**What:** Every IR node that makes a claim carries an `EpistemicStatus` enum. This is enforced at the Pydantic model level, not as optional metadata.

**When:** All parameters, constraints, objectives, verification results, and report claims.

```python
class EpistemicStatus(str, Enum):
    DEFINITION = "definition"
    ASSUMPTION = "assumption"
    AXIOM = "axiom"
    INPUT_ESTIMATE = "input_estimate"
    POLICY_CONSTRAINT = "policy_constraint"
    DERIVED = "derived_expression"
    SOFT_PREFERENCE = "soft_preference"
    HARD_REQUIREMENT = "hard_requirement"
    HEURISTIC = "heuristic"
    SOLVER_RESULT = "solver_result"
    NUMERICAL_CHECK = "numerical_check"
    FINITE_VERIFICATION = "finite_case_verification"
    CONJECTURE = "conjecture"
    MACHINE_CHECKED = "machine_checked_theorem"
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Spec-to-Code Without IR

**What:** Generating solver code directly from the YAML spec, bypassing the IR.
**Why bad:** No normalization, no symbol table, no validation pass, no single source of truth. Guarantees implementation drift.
**Instead:** Always compile spec -> IR -> validate IR -> generate from IR.

### Anti-Pattern 2: Claude as Solver

**What:** Having Claude reason about optimization solutions instead of generating and running solver code.
**Why bad:** LLM "optimization" is pattern matching, not mathematical optimization. Results are unreliable and unverifiable.
**Instead:** Claude writes the model; the Python runtime solves it. Clear separation.

### Anti-Pattern 3: Monolithic Code Generation

**What:** One giant template that generates the entire solver file.
**Why bad:** Unmaintainable. Cannot extend with new constraint families or backends.
**Instead:** Composable templates: one per constraint family, one per objective type, one for the solver harness, assembled by the code generator.

### Anti-Pattern 4: Implicit Epistemic Status

**What:** Generating reports where solver results, assumptions, and verified claims are presented without status labels.
**Why bad:** Users conflate "the solver found this" with "this is proven." Core risk per design brief section 7.
**Instead:** Every claim in every report carries its status. No exceptions.

### Anti-Pattern 5: Dynamic Domain Loading Without Schema

**What:** Loading domain YAML templates without validating them against a domain schema.
**Why bad:** Domain templates become another source of "natural language soup" (Risk 1).
**Instead:** Domain templates must also pass Pydantic validation. Domain ontology has a schema.

## Directory Structure

```
meta-compiler/
  .claude-plugin/
    plugin.json           # Plugin manifest
  commands/               # Slash commands (markdown)
    model-init.md
    model-compile.md
    model-check.md
    model-solve.md
    model-verify.md
    model-stress.md
    model-report.md
    model-setup.md
  skills/                 # Claude skills for formalization
    spec-writer.md
    ir-reviewer.md
  agents/                 # Multi-step agents
    full-pipeline.md
  meta_compiler/          # Python package
    __init__.py
    cli.py                # CLI entry point (subprocess target)
    core/
      __init__.py
      ir.py               # IR Pydantic models
      parser.py           # YAML spec -> dict
      normalizer.py       # dict -> IR
      symbol_table.py     # Symbol registry
      type_system.py      # Variable domains, index sets
      validator.py        # Structural validation
      epistemic.py        # EpistemicStatus enum and utilities
    backends/
      __init__.py
      cpsat.py            # IR -> OR-Tools CP-SAT code
      z3_verifier.py      # IR -> Z3 verification scripts
    codegen/
      __init__.py
      generator.py        # Template orchestration
      templates/          # Jinja2 templates
        cpsat/
          solver.py.j2
          constraints/
          objectives/
        z3/
          verifier.py.j2
        reports/
          technical.md.j2
          notation.md.j2
    domains/
      __init__.py
      registry.py         # Domain template loader
      allocation/         # Generic allocation domain
        ontology.yaml
        constraints.yaml
        objectives.yaml
    runtime/
      __init__.py
      solver_runner.py    # Execute generated solver code
      stress_runner.py    # Sensitivity/perturbation
      report_builder.py   # Assemble reports
    tests/
      __init__.py
      test_parser.py
      test_ir.py
      test_validator.py
      test_cpsat.py
      test_z3.py
      conftest.py         # Shared fixtures
  pyproject.toml          # Python package config
  README.md
```

## Scalability Considerations

| Concern | Small models (< 100 vars) | Medium models (< 10K vars) | Large models (> 100K vars) |
|---------|--------------------------|---------------------------|---------------------------|
| IR compilation | Instant | < 1 second | May need lazy symbol table loading |
| Structural validation | Instant | NetworkX handles fine | Graph algorithms may need optimization |
| CP-SAT solve | < 1 second | Seconds to minutes | Minutes to hours; need timeout config |
| Z3 verification | < 1 second | Seconds | May hit decidability limits; scope verification targets |
| Code generation | Instant | Instant | Template rendering is fast regardless |

The MVP targets small-to-medium models. Large model optimization is Phase 3+.

## Sources

- Design brief sections 11 (core architecture), 12 (IR), 21 (repository structure)
- PROJECT.md architecture decision: "Hybrid model"
- [Pydantic discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/)
- [NetworkX graph algorithms](https://networkx.org/documentation/stable/reference/index.html)
- [Jinja2 template inheritance](https://jinja.palletsprojects.com/en/stable/intro/)
