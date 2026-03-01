# SESF v2 Templates

Fill-in-the-blank starting points for each specification tier. Copy the template that matches your complexity, replace `[bracketed placeholders]` with your values, and delete any optional sections you do not need.

---

## Micro Tier Template

```
# [Specification Name]

Meta
* Version: [1.0.0] | Date: [YYYY-MM-DD] | Domain: [context] | Status: [draft] | Tier: micro

Purpose
[One sentence describing what this specification accomplishes]

BEHAVIOR [behavior_name]: [Brief description of this behavior]

  RULE [rule_name]:
    [condition or constraint statement using MUST/SHOULD/MAY]

  RULE [conditional_rule_name]:
    WHEN [condition]
    THEN [action]
    ELSE [alternative action]

  ERROR [error_name]:
    WHEN [condition that triggers this error]
    SEVERITY [critical | warning | info]
    ACTION [what to do when this error occurs]
    MESSAGE "[user-facing error message]"

  EXAMPLE [success_case]:
    INPUT: [concrete input value or object]
    EXPECTED: [concrete expected output]

  EXAMPLE [failure_case]:
    INPUT: [concrete input that triggers the error above]
    EXPECTED: [error output or rejection result]

Constraints
* [constraint statement]
```

---

## Standard Tier Template

```
# [Specification Name]

Meta
* Version: [1.0.0]
* Date: [YYYY-MM-DD]
* Domain: [context area]
* Status: [draft | active | deprecated]
* Tier: standard

Purpose
[One to three sentences describing what this specification accomplishes and why it exists.]

Scope
* IN SCOPE: [what this specification covers]
* OUT OF SCOPE: [what this explicitly does not cover]

Inputs
* [input_name]: [type] - [description] - [required | optional]
* [input_name]: [type] - [description] - [required | optional, default: value]

Outputs
* [output_name]: [type] - [description]

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

Behaviors

BEHAVIOR [behavior_name]: [Brief description of what this behavior does]

  RULE [rule_name]:
    WHEN [condition]
    THEN [action]
    ELSE [alternative action]

  RULE [simple_rule_name]:
    [field] MUST [satisfy constraint]

  ERROR [error_name]:
    WHEN [condition]
    SEVERITY [critical | warning | info]
    ACTION [what to do]
    MESSAGE "[user-facing message]"

  EXAMPLE [success_case]:
    INPUT: { [concrete input data] }
    EXPECTED: { [concrete expected output] }
    NOTES: [clarification if needed]

  EXAMPLE [failure_case]:
    INPUT: { [concrete input that triggers error] }
    EXPECTED: { [error output] }

Constraints
* [constraint statement using MUST/SHOULD/MAY]

Dependencies
* [external system or resource this specification relies on]
```

---

## Complex Tier Template

```
# [Specification Name]

Meta
* Version: [1.0.0]
* Date: [YYYY-MM-DD]
* Domain: [context area]
* Status: [draft | active | deprecated]
* Tier: complex

Purpose
[One to three sentences describing what this specification accomplishes and why it exists.]

Scope
* IN SCOPE: [what this specification covers]
* OUT OF SCOPE: [what this explicitly does not cover]

Inputs
* [input_name]: [type] - [description] - [required | optional]

Outputs
* [output_name]: [type] - [description]

Types

[TypeName] {
  [field_name]: [type], [required | optional]
  [field_name]: enum [[option1, option2]], [required]
}

Functions

FUNCTION [function_name]([parameter1]):
  [logic as simple statements]
  RETURNS [output]

Behaviors

BEHAVIOR [behavior_name]: [Brief description of what this behavior does]

  RULE [rule_name]:
    WHEN [condition]
    THEN [action]
    ELSE [alternative action]
    PRIORITY 1

  RULE [simple_rule_name]:
    [field] MUST [satisfy constraint]
    PRIORITY 2

  ERROR [error_name]:
    WHEN [condition]
    SEVERITY [critical | warning | info]
    ACTION [what to do]
    MESSAGE "[user-facing message]"

  EXAMPLE [success_case]:
    INPUT: { [concrete input data] }
    EXPECTED: { [concrete expected output] }

  EXAMPLE [failure_case]:
    INPUT: { [concrete input that triggers error] }
    EXPECTED: { [error output] }

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

  ERROR [error_name]:
    WHEN [condition]
    SEVERITY [critical | warning | info]
    ACTION [what to do]
    MESSAGE "[user-facing message]"

  EXAMPLE [success_case]:
    INPUT: { [concrete input] }
    EXPECTED: { [concrete output] }

  EXAMPLE [edge_case]:
    INPUT: { [input that tests overlap with first behavior] }
    EXPECTED: { [output showing precedence resolution] }
    NOTES: [explain which behavior/rule takes priority and why]

Precedence

PRECEDENCE:
  1. [rule_name] (from BEHAVIOR [behavior_name])
  2. [rule_name] (from BEHAVIOR [second_behavior_name])

Constraints
* [constraint statement using MUST/SHOULD/MAY]

Dependencies
* [external system or resource this specification relies on]

Changelog
* [version]: [date] - [changes]
```
