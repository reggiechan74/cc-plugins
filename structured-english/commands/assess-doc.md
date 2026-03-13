---
description: Assess whether a markdown document would benefit from HSF conversion
argument-hint: <path to markdown file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Assess Document for HSF Conversion

Evaluate an existing markdown document against Hybrid Specification Format (HSF v5) suitability criteria and offer conversion if appropriate.

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for HSF v5 specifications. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md`.

### Step 2: Read the Document

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which markdown file should I assess?"

Read the full file content before proceeding.

### Step 3: Assess the Document

Analyze the content for signals that indicate whether HSF would add value.

**Signals FOR conversion** (rules with branching logic):

- If/then/else or when/then constructs
- Validation rules with different outcomes per case
- Decision trees or branching logic
- Routing or escalation logic (thresholds, tiers, priority levels)
- Business rules with numeric thresholds or eligibility criteria
- Classification with multiple categories and different handling
- Error handling with severity levels or different recovery paths

**Signals FOR conversion** (step-by-step workflows):

- Ordered steps that must happen in sequence
- Workflows with decisions, loops, or retries embedded in the steps
- Processes involving side effects (sending emails, writing files, calling APIs)
- Data pipelines (extract, transform, load)
- State machines or lifecycle transitions
- Onboarding flows, approval chains, or multi-stage processes
- Steps that reference outputs of prior steps

**Signals FOR structured notation** (HSF features that reduce boilerplate):

- Document has scattered configuration values (thresholds, limits, feature flags repeated in multiple places) → `@config` centralizes them
- Document has multi-branch conditional logic (3+ branches for the same decision point) → `@route` provides compact routing tables
- Document describes workflows with intermediate results (step outputs feed into later steps) → `$variable` threading names and passes results
- Document has many error cases (validation failures, edge cases, severity levels) → consolidated error table keeps them organized

**Signals AGAINST conversion** (purely narrative or trivial content):

- Narrative guidance or explanations with no actionable structure
- Role or personality descriptions
- README or documentation
- Style guides (preferences, not rules with error handling)
- Meeting agendas or outlines
- Simple linear checklists with no decisions, loops, or error handling

**Rule of thumb**: Ask two questions:
1. "Does the same input sometimes produce different outputs depending on conditions?" — if yes, structured rules help.
2. "Is there a step-by-step process with decisions, loops, or side effects?" — if yes, structured instructions help.

If neither applies, prose is simpler.

### Step 4: Present the Assessment

Report your findings clearly:

- **Verdict**: "Would benefit from HSF" or "Not a good fit for HSF"
- **Evidence**: Specific patterns found (or absent) in the document, with quotes or line references
- **If beneficial**: Suggest a tier (micro, standard, or complex) and recommend:
  - Which concerns map to rules sections?
  - Which concerns map to procedural instruction phases?
  - Are there @route candidates (3+ branch decisions)?
  - Are there @config candidates (3+ repeated config values)?
- **If not beneficial**: Explain what format suits the document better (prose, numbered list, outline, etc.) and why

### Step 5: Offer Conversion

If the document would benefit from HSF, use `AskUserQuestion` to ask three questions:

**Question 1** — Confirm conversion:

- "Would you like me to convert this document to HSF format?"
- Options:
  - "Yes, convert it" — proceed to output mode question
  - "No, keep as-is" — stop, do not convert

If the user declines, stop here.

**Question 2** — Output mode:

Detect whether the file is a Claude Code command or skill by checking for `allowed-tools` or `argument-hint` in its YAML frontmatter. If found, default-suggest "Self-contained".

- "How should the converted specification be structured?"
- Options:
  1. **Self-contained** (spec + executable in one file) — All content stays inline. This is the correct choice when the file is a Claude Code command or skill. *(Recommended if the file has `allowed-tools` or `argument-hint` frontmatter)*
  2. **Split into spec + executable** — Create a pure HSF v5 specification document and a separate executable. This is the correct choice when you want a clean separation between "what the system does" (spec) and "how to run it" (executable).

Store the user's choice as `$output_mode` ("self-contained" or "split").

**Question 3** — File handling:

- "How should I save the converted specification?"
- Options:
  - "Overwrite the original file" — replace the source file in place (original recoverable via git history)
  - "Save as a new file" — write to `<original-name>-hsf.md` alongside the original

After the user answers all questions, convert the document using the skill's HSF v5 rules, using the original document content as context for requirements gathering. Apply `$output_mode` to control whether content stays inline or is extracted to companion files. Write edge case examples only. Save the result according to the user's file handling choice.
