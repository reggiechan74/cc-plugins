---
description: Assess whether a markdown document would benefit from SESF conversion
argument-hint: <path to markdown file>
allowed-tools: ["Read", "Bash", "AskUserQuestion"]
---

# Assess Document for SESF Conversion

Evaluate an existing markdown document against SESF v3 suitability criteria and offer conversion if appropriate. SESF v3 handles both declarative rules (BEHAVIOR) and step-by-step workflows (PROCEDURE).

## Workflow

### Step 1: Read the Document

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which markdown file should I assess?"

Read the full file content before proceeding.

### Step 2: Assess the Document

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

### Step 3: Present the Assessment

Report your findings clearly:

- **Verdict**: "Would benefit from SESF" or "Not a good fit for SESF"
- **Evidence**: Specific patterns found (or absent) in the document, with quotes or line references
- **If beneficial**: Suggest a tier (micro, standard, or complex) and recommend block types:
  - Which concerns map to BEHAVIOR blocks (declarative rules)?
  - Which concerns map to PROCEDURE blocks (ordered workflows)?
  - Are there reusable calculations (FUNCTION) or side-effect operations (ACTION)?
- **If not beneficial**: Explain what format suits the document better (prose, numbered list, outline, etc.) and why

### Step 4: Offer Conversion

If the document would benefit from SESF, use `AskUserQuestion` to ask:

- "Would you like me to convert this document to SESF format?"

If the user says yes, invoke the `structured-english` skill to perform the conversion, using the original document content as context for requirements gathering.
