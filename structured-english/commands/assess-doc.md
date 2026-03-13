---
description: Assess whether a markdown document would benefit from SESF conversion
argument-hint: <path to markdown file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Assess Document for SESF Conversion

Evaluate an existing markdown document against SESF v4 suitability criteria and offer conversion if appropriate. SESF v4 handles both declarative rules (BEHAVIOR) and step-by-step workflows (PROCEDURE).

## Workflow

### Step 1: Load the Skill

Use the `structured-english` skill — it contains all the rules, formats, and validation requirements for SESF v4 specifications. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/structured-english/assets/reference.md`.

### Step 2: Read the Document

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which markdown file should I assess?"

Read the full file content before proceeding.

### Step 3: Assess the Document

Analyze the content for signals that indicate whether SESF would add value.

**Signals FOR declarative SESF** (BEHAVIOR blocks — conditional logic that branches):

- If/then/else or when/then constructs
- Validation rules with different outcomes per case
- Decision trees or branching logic
- Routing or escalation logic (thresholds, tiers, priority levels)
- Business rules with numeric thresholds or eligibility criteria
- Classification with multiple categories and different handling
- Error handling with severity levels or different recovery paths

**Signals FOR procedural SESF** (PROCEDURE blocks — step-by-step workflows):

- Ordered steps that must happen in sequence
- Workflows with decisions, loops, or retries embedded in the steps
- Processes involving side effects (sending emails, writing files, calling APIs)
- Data pipelines (extract, transform, load)
- State machines or lifecycle transitions
- Onboarding flows, approval chains, or multi-stage processes
- Steps that reference outputs of prior steps

**Signals FOR hybrid elements** (v4 features that reduce boilerplate):

- Document has scattered configuration values (thresholds, limits, feature flags repeated in multiple places) → `@config` centralizes them in one block
- Document has multi-branch conditional logic (3+ branches for the same decision point) → `@route` provides compact routing tables instead of nested IF/ELSE IF
- Document describes workflows with intermediate results (step outputs feed into later steps) → `$variable` threading names and passes results between PROCEDURE steps
- Document has many error cases (validation failures, edge cases, severity levels) → compact `ERRORS` table format keeps them organized without verbose prose

**Signals AGAINST conversion** (purely narrative or trivial content):

- Narrative guidance or explanations with no actionable structure
- Role or personality descriptions
- README or documentation
- Style guides (preferences, not rules with error handling)
- Meeting agendas or outlines
- Simple linear checklists with no decisions, loops, or error handling

**Rule of thumb**: Ask two questions:
1. "Does the same input sometimes produce different outputs depending on conditions?" — if yes, BEHAVIOR blocks help.
2. "Is there a step-by-step process with decisions, loops, or side effects?" — if yes, PROCEDURE blocks help.

If neither applies, prose is simpler.

### Step 4: Present the Assessment

Report your findings clearly:

- **Verdict**: "Would benefit from SESF" or "Not a good fit for SESF"
- **Evidence**: Specific patterns found (or absent) in the document, with quotes or line references
- **If beneficial**: Suggest a tier (micro, standard, or complex) and recommend block types:
  - Which concerns map to BEHAVIOR blocks (declarative rules)?
  - Which concerns map to PROCEDURE blocks (ordered workflows)?
  - Are there reusable calculations (FUNCTION) or side-effect operations (ACTION)?
- **If not beneficial**: Explain what format suits the document better (prose, numbered list, outline, etc.) and why

### Step 5: Offer Conversion

If the document would benefit from SESF, use `AskUserQuestion` to ask three questions:

**Question 1** — Confirm conversion:

- "Would you like me to convert this document to SESF format?"
- Options:
  - "Yes, convert it" — proceed to output mode question
  - "No, keep as-is" — stop, do not convert

If the user declines, stop here.

**Question 2** — Output mode:

Detect whether the file is a Claude Code command or skill by checking for `allowed-tools` or `argument-hint` in its YAML frontmatter. If found, default-suggest "Self-contained".

- "How should the converted specification be structured?"
- Options:
  1. **Self-contained** (spec + executable in one file) — All content (agent prompts, examples, operational instructions) stays inline. This is the correct choice when the file is a Claude Code command or skill. *(Recommended if the file has `allowed-tools` or `argument-hint` frontmatter)*
  2. **Split into spec + executable** — Create a pure SESF v4 specification document and a separate executable. This is the correct choice when you want a clean separation between "what the system does" (spec) and "how to run it" (executable).

Store the user's choice as `$output_mode` ("self-contained" or "split").

**Question 3** — File handling:

- "How should I save the converted specification?"
- Options:
  - "Overwrite the original file" — replace the source file in place (original recoverable via git history)
  - "Save as a new file" — write to `<original-name>-sesf.md` alongside the original

After the user answers all questions, convert the document using the skill's v4 rules, using the original document content as context for requirements gathering. Apply `$output_mode` to control whether content stays inline or is extracted to companion files. Write edge case examples only — boundary conditions, error paths, and non-obvious behavior. Save the result according to the user's file handling choice.
