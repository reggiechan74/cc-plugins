---
description: Review a markdown specification for ambiguity, contradiction, and inferred intent
argument-hint: <path to markdown spec file>
allowed-tools: ["Read", "Write", "Edit", "AskUserQuestion"]
---

# Assess Inferred Intent

Analyze a markdown specification file (slash command, SKILL.md, agent.md, or any structured spec) for areas of ambiguity, contradiction, or inferred intent. Present findings to the user for resolution, then apply the clarifications to the document.

## Workflow

### Step 1: Read the Document

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which markdown specification file should I review?"

Read the full file content before proceeding.

### Step 2: Analyze for Issues

Examine the document for three categories of problems:

**Ambiguity** — language or structure that could be interpreted multiple ways:

- Vague quantifiers ("some", "several", "a few", "many") without concrete values
- Undefined terms used without explanation or context
- Conditional logic with missing branches or unspecified default behavior
- Pronouns with unclear antecedents ("it should handle this" — what is "this"?)
- Scope boundaries that are not explicit ("related files", "similar items", "etc.")
- Instructions that assume context the reader may not have

**Contradiction** — statements that conflict with each other:

- Two rules that produce different outcomes for the same input
- A step that requires something a prior step explicitly forbids or omits
- Metadata (frontmatter fields, descriptions) that conflicts with the body content
- Conflicting defaults or fallback behaviors
- Ordering constraints that form impossible sequences

**Inferred Intent** — behavior that is implied but never stated:

- Steps that seem to assume a prerequisite not listed
- Error handling that is likely expected but not documented
- Edge cases where the spec is silent but real-world usage would encounter them
- Implicit ordering dependencies between steps that are not made explicit
- Assumptions about the environment, tools, or user state
- "Happy path only" workflows that omit failure scenarios

### Step 3: Present Findings

For each issue found, prepare a structured finding with:

- **Category**: Ambiguity, Contradiction, or Inferred Intent
- **Location**: The specific section, line, or passage where the issue occurs (quote the relevant text)
- **Problem**: What is unclear, conflicting, or assumed
- **Inferred intent**: Your best guess at what the author likely meant
- **Alternatives**: 1-2 other reasonable interpretations

If no issues are found, tell the user the spec looks clear and stop.

### Step 4: Resolve Issues with the User

Use `AskUserQuestion` to walk through the findings. Group related issues into a reasonable number of questions (aim for 1-4 questions per round to stay within tool limits). For each issue:

- Present the quoted passage and the problem
- Offer the inferred intent as the first option (labeled with "(Inferred)" at the end)
- List the alternative interpretations as additional options
- Allow the user to provide their own resolution via "Other"

Continue presenting rounds of questions until all issues are resolved.

### Step 5: Apply Clarifications

After all issues are resolved, revise the document to incorporate the user's decisions. Changes should:

- Replace ambiguous language with the user's chosen wording
- Resolve contradictions by keeping the user's preferred version
- Make inferred intent explicit in the document text
- Preserve the document's existing structure and formatting style
- Not introduce new content beyond what is needed to resolve the identified issues

### Step 6: Save the Result

Use `AskUserQuestion` to ask the user how to save:

- "How should I save the clarified specification?"
- Options:
  - "Overwrite the original file" — replace the source file in place
  - "Save as a new file" — write to `<original-name>-clarified.md` alongside the original
