---
description: Assess whether a markdown document would benefit from SESF conversion
argument-hint: <path to markdown file>
allowed-tools: ["Read", "Bash", "AskUserQuestion"]
---

# Assess Document for SESF Conversion

Evaluate an existing markdown document against SESF suitability criteria and offer conversion if appropriate.

## Workflow

### Step 1: Read the Document

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which markdown file should I assess?"

Read the full file content before proceeding.

### Step 2: Assess the Document

Analyze the content for signals that indicate whether SESF would add value.

**Signals FOR conversion** (conditional logic that branches differently based on inputs):

- If/then/else or when/then constructs
- Validation rules with different outcomes per case
- Decision trees or branching logic
- Routing or escalation logic (thresholds, tiers, priority levels)
- State machines or lifecycle transitions
- Business rules with numeric thresholds or eligibility criteria
- Classification with multiple categories and different handling
- Error handling with severity levels or different recovery paths

**Signals AGAINST conversion** (sequential, linear, or narrative content):

- Step-by-step instructions with no branching
- Linear checklists
- Narrative guidance or explanations
- Role or personality descriptions
- README or documentation
- Style guides (preferences, not rules with error handling)
- Meeting agendas or outlines

**Rule of thumb**: "Does the same input sometimes produce different outputs depending on conditions?" If yes, SESF helps. If the process is the same every time, prose is simpler.

### Step 3: Present the Assessment

Report your findings clearly:

- **Verdict**: "Would benefit from SESF" or "Not a good fit for SESF"
- **Evidence**: Specific patterns found (or absent) in the document, with quotes or line references
- **If beneficial**: Suggest a tier (micro, standard, or complex) and list the behaviors you identified
- **If not beneficial**: Explain what format suits the document better (prose, numbered list, outline, etc.) and why

### Step 4: Offer Conversion

If the document would benefit from SESF, use `AskUserQuestion` to ask:

- "Would you like me to convert this document to SESF format?"

If the user says yes, invoke the `structured-english` skill to perform the conversion, using the original document content as context for requirements gathering.
