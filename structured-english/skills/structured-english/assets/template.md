# SESF v4 Templates

Fill-in-the-blank starting points for each specification tier. Copy the template that matches your complexity, replace `[bracketed placeholders]` with your values, and delete any optional sections you do not need. Each tier includes both BEHAVIOR and PROCEDURE templates -- use whichever block type fits your problem, or combine them in the same spec.

**What is new in v4:**

- YAML frontmatter (optional, for tooling integration)
- Notation section (required for Standard/Complex tiers)
- @config block for centralized parameters
- @route decision tables inside BEHAVIOR blocks (3+ branches)
- $variable threading in PROCEDURE steps
- Compact ERRORS: table (5 mandatory columns)
- Compact EXAMPLES: one-line format

---

## Micro Tier Template

> **Choosing a block type:** Use BEHAVIOR for declarative rules (conditions lead to outcomes). Use PROCEDURE for ordered steps (do this, then this). A spec can use either or both.

### BEHAVIOR (Micro)

```
---
name: [skill-name]
description: "[one-line description]"
---

# [Specification Name]

Meta: Version X.X.X | Date: YYYY-MM-DD | Domain: [context] | Status: [draft | active | deprecated] | Tier: micro

Purpose
[One or two sentences describing what this specification accomplishes.]

Inputs
* [name]: [type] - [description] - required

Outputs
* [name]: [type] - [description]

Behaviors

BEHAVIOR [behavior_name]: [Brief description of this behavior]

  RULE [rule_name]:
    WHEN [condition]
    THEN [action]
    ELSE [alternative action]

  RULE [constraint_rule_name]:
    [subject] MUST [requirement]

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | [error_name] | [condition] | [critical/warning/info] | [recovery action] | "[user-facing message]" |

  EXAMPLES:
    [success_case]: [input description] → [expected outcome]
    [failure_case]: [input description] → [expected error outcome]

Constraints
* [optional constraint statement]
```

**Alternatives for Micro tier:**

- Traditional ERROR blocks may be used instead of the compact ERRORS: table:
  ```
  ERROR [error_name]:
    WHEN [condition that triggers this error]
    SEVERITY [critical | warning | info]
    ACTION [what to do when this error occurs]
    MESSAGE "[user-facing error message]"
  ```

- Traditional EXAMPLE blocks may be used instead of compact EXAMPLES:
  ```
  EXAMPLE [example_name]:
    INPUT: [concrete input value or object]
    EXPECTED: [concrete expected output]
  ```

### PROCEDURE (Micro)

```
---
name: [skill-name]
description: "[one-line description]"
---

# [Specification Name]

Meta: Version X.X.X | Date: YYYY-MM-DD | Domain: [context] | Status: [draft | active | deprecated] | Tier: micro

Purpose
[One or two sentences describing what this specification accomplishes.]

Inputs
* [name]: [type] - [description] - required

Outputs
* [name]: [type] - [description]

Procedures

PROCEDURE [procedure_name]: [Brief description of what this procedure does]

  STEP [step_name] → $[output_var]
    [natural English action] → $[output_var]

  STEP [another_step]:
    [natural English action using $output_var from prior step]

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | [error_name] | [condition] | [critical/warning/info] | [recovery action] | "[user-facing message]" |

  EXAMPLES:
    [success_case]: [input description] → [expected outcome]
    [failure_case]: [input description] → [expected error outcome]

Constraints
* [optional constraint statement]
```

**Notes for Micro tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- Inputs and Outputs are optional at micro tier. Include them when the spec has clear data boundaries.
- $variable threading on STEP declarations is optional. Omit `→ $var` if steps have no meaningful outputs to pass forward.
- Notation section is not required at micro tier. Include an abbreviated form only if hybrid symbols ($, @, →) appear and readers may need a glossary.
- @config and @route are not recommended at micro tier (too small to benefit).

---

## Standard Tier Template

> **Choosing a block type:** Use BEHAVIOR for declarative rules (conditions lead to outcomes). Use PROCEDURE for ordered steps (do this, then this). A spec can use either or both.

```
---
name: [skill-name]
description: "[one-line description]"
allowed-tools: [tool1, tool2]
---

# [Specification Name]

Meta
* Version: X.X.X
* Date: YYYY-MM-DD
* Domain: [context area]
* Status: [draft | active | deprecated]
* Tier: standard

Notation
* $ — references a variable or config value
* @ — marks a structured block (@config, @route)
* → — means "produces", "routes to", or "yields"
* MUST/SHOULD/MAY/CAN — requirement strength keywords

Purpose
[Two to three sentences describing what this specification accomplishes and why it exists.]

Scope
* IN SCOPE: [what this specification covers]
* OUT OF SCOPE: [what this explicitly does not cover]

Inputs
* [input_name]: [type] - [description] - [required | optional]
* [input_name]: [type] - [description] - [required | optional, default: value]

Outputs
* [output_name]: [type] - [description]

@config
  [key]: [value]
  [key]: [value]

Types

[TypeName] {
  [field_name]: [type], [required | optional]
  [field_name]: [type], [default: value]
  [field_name]: enum [[option1, option2, option3]], [required]
}

Functions

FUNCTION [function_name]([parameter1], [parameter2]):
  [logic as simple statements]
  IF [condition] THEN
    [action]
  ELSE
    [alternative action]
  RETURNS [output]

ACTION [action_name]([parameter1], [parameter2]):
  [natural English actions with side effects]
  RETURNS [output]

Behaviors

BEHAVIOR [behavior_name]: [Brief description of what this behavior does]

  @route [table_name] [first_match_wins]
    [condition_1]  → [outcome_1]
    [condition_2]  → [outcome_2]
    [condition_3]  → [outcome_3]
    *              → [default_outcome]

  RULE [constraint_name]:
    [subject] MUST [binary constraint]

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | [error_name] | [condition] | [critical/warning/info] | [recovery action] | "[user-facing message]" |

  EXAMPLES:
    [success_case]: [input description] → [expected outcome]
    [failure_case]: [input description] → [expected error outcome]

Procedures

PROCEDURE [procedure_name]: [Brief description of what this procedure does]

  STEP [step_name] → $[output_var]
    [action description] → $[output_var]

  STEP [another_step]:
    [action using $output_var from prior step]

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | [error_name] | [condition] | [critical/warning/info] | [recovery action] | "[user-facing message]" |

  EXAMPLES:
    [success_case]: [input description] → [expected outcome]
    [failure_case]: [input description] → [expected error outcome]

Constraints
* [constraint statement using MUST/SHOULD/MAY]

Dependencies
* [external system or resource this specification relies on]
```

**Alternatives for Standard tier:**

- Traditional ERROR blocks may be used instead of the compact ERRORS: table:
  ```
  ERROR [error_name]:
    WHEN [condition]
    SEVERITY [critical | warning | info]
    ACTION [what to do]
    MESSAGE "[user-facing message]"
  ```

- Traditional EXAMPLE blocks may be used instead of compact EXAMPLES:
  ```
  EXAMPLE [example_name]:
    INPUT: { [concrete input data] }
    EXPECTED: { [concrete expected output] }
    NOTES: [clarification if needed]
  ```

- Mixed usage is allowed: a block can have both compact and traditional ERROR/EXAMPLE entries.

**Notes for Standard tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- @config is optional. Omit it if the spec has no configurable parameters.
- @route is for 3+ branch conditionals inside BEHAVIOR blocks. For binary conditions, use WHEN/THEN/ELSE rules.
- $variable threading on STEP declarations is optional. Omit `→ $var` when steps have no meaningful outputs.
- Types and Functions sections are required. Use `-- none` stubs if the spec has no type definitions or functions:
  ```
  Types
  -- none: all data structures are inline within behavior and procedure blocks

  Functions
  -- none: all logic is expressed directly in behavior rules and procedure steps
  ```

---

## Complex Tier Template

> **Choosing a block type:** Use BEHAVIOR for declarative rules (conditions lead to outcomes). Use PROCEDURE for ordered steps (do this, then this). A spec can use either or both.

```
---
name: [skill-name]
description: "[one-line description]"
allowed-tools: [tool1, tool2]
---

# [Specification Name]

Meta
* Version: X.X.X
* Date: YYYY-MM-DD
* Domain: [context area]
* Status: [draft | active | deprecated]
* Tier: complex

Notation
* $ — references a variable or config value
* @ — marks a structured block (@config, @route)
* → — means "produces", "routes to", or "yields"
* MUST/SHOULD/MAY/CAN — requirement strength keywords

Purpose
[Two to three sentences describing what this specification accomplishes and why it exists.]

Audience
* AI agents: [implementation guidance for literal interpretation]
* Human readers: [context or rationale for understanding this specification]

Scope
* IN SCOPE: [what this specification covers]
* OUT OF SCOPE: [what this explicitly does not cover]

Inputs
* [input_name]: [type] - [description] - [required | optional]

Outputs
* [output_name]: [type] - [description]

@config
  [key]: [value]
  [key]: [value]
  [nested_group]:
    [key]: [value]

Types

[TypeName] {
  [field_name]: [type], [required | optional]
  [field_name]: enum [[option1, option2]], [required]
}

Functions

FUNCTION [function_name]([parameter1]):
  [logic as simple statements]
  RETURNS [output]

ACTION [action_name]([parameter1]):
  [natural English actions with side effects]
  RETURNS [output]

Behaviors

BEHAVIOR [behavior_name]: [Brief description of what this behavior does]

  @route [table_name] [first_match_wins]
    [condition_1]  → [outcome_1]
    [condition_2]  → [outcome_2]
    [condition_3]  → [outcome_3]
    *              → [default_outcome]

  RULE [rule_name]:
    WHEN [condition]
    THEN [action]
    ELSE [alternative action]
    PRIORITY 1

  RULE [constraint_name]:
    [subject] MUST [binary constraint]
    PRIORITY 2

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | [error_name] | [condition] | [critical/warning/info] | [recovery action] | "[user-facing message]" |

  EXAMPLES:
    [success_case]: [input description] → [expected outcome]
    [failure_case]: [input description] → [expected error outcome]

  State/Flow
    [state_name] -> [next_state]: WHEN [transition condition]
    [state_name] -> [terminal_state]: WHEN [completion condition]

  Audience notes
    * AI agents: [implementation guidance for literal interpretation]
    * Human readers: [context or rationale for this behavior]


BEHAVIOR [second_behavior_name]: [Brief description]

  RULE [rule_name]:
    WHEN [condition]
    THEN [action]
    PRIORITY 1

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | [error_name] | [condition] | [critical/warning/info] | [recovery action] | "[user-facing message]" |

  EXAMPLES:
    [success_case]: [input description] → [expected outcome]
    [edge_case]: [input testing overlap with first behavior] → [output showing precedence resolution]

Procedures

PROCEDURE [procedure_name]: [Brief description of what this procedure does]

  STEP [step_name] → $[output_var]
    [action description] → $[output_var]

  STEP [another_step]:
    [action using $output_var from prior step]

  STEP [final_step]:
    [natural English action or actions]

  ERRORS:
  | name | when | severity | action | message |
  |------|------|----------|--------|---------|
  | [error_name] | [condition] | [critical/warning/info] | [recovery action] | "[user-facing message]" |

  EXAMPLES:
    [success_case]: [input description] → [expected outcome]
    [failure_case]: [input description] → [expected error outcome]

  State/Flow
    [state_name] -> [next_state]: WHEN [transition condition]
    [state_name] -> [terminal_state]: WHEN [completion condition]

  Audience notes
    * AI agents: [implementation guidance for literal interpretation]
    * Human readers: [context or rationale for this procedure]

Precedence

PRECEDENCE:
  1. [rule_name] (from BEHAVIOR [behavior_name])
  2. [rule_name] (from BEHAVIOR [second_behavior_name])

Constraints
* [constraint statement using MUST/SHOULD/MAY]

Dependencies
* [external system or resource this specification relies on]

Changelog
* [version]: [YYYY-MM-DD] - [changes]
```

**Alternatives for Complex tier:**

- Traditional ERROR blocks may be used instead of the compact ERRORS: table:
  ```
  ERROR [error_name]:
    WHEN [condition]
    SEVERITY [critical | warning | info]
    ACTION [what to do]
    MESSAGE "[user-facing message]"
  ```

- Traditional EXAMPLE blocks may be used instead of compact EXAMPLES:
  ```
  EXAMPLE [example_name]:
    INPUT: { [concrete input data] }
    EXPECTED: { [concrete expected output] }
    NOTES: [explain which behavior/rule takes priority and why]
  ```

- Mixed usage is allowed: a block can have both compact and traditional ERROR/EXAMPLE entries.

**Notes for Complex tier:**

- YAML frontmatter is optional. Omit the `---` block if your tooling does not need it.
- Audience section at the top level is optional. Per-block Audience notes subsections are also optional.
- State/Flow subsections are optional within BEHAVIOR and PROCEDURE blocks. Include them when the block manages state transitions.
- PRECEDENCE is required at Complex tier when rules from different behaviors can match the same input. If no overlapping conditions exist, include a stub: `PRECEDENCE: -- none: no overlapping conditions between behaviors`.
- @config, @route, and $variable threading follow the same rules as Standard tier.
- PRIORITY tags on individual rules within a BEHAVIOR MUST NOT contradict the global PRECEDENCE block.
