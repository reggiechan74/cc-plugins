---
description: Assess whether a document would benefit from human-readable SESF conversion
argument-hint: <path to markdown file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Assess Document for Human-Facing SESF Conversion

Evaluate an existing markdown document against SESF v4.1 suitability criteria, specifically for producing a spec that humans will read, review, and maintain. Offer conversion if appropriate.

## Audience Context

Human-facing specs prioritize comprehension and maintainability. The question is: would converting this document to SESF v4.1 with formal BEHAVIOR/PROCEDURE blocks make it easier for humans to understand, review, and modify?

## Workflow

### Step 1: Load the Skill

Use the `sesf` skill — it contains all the rules, formats, and validation requirements for SESF v4.1. Read it fully before proceeding. Also read:

- The format reference at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/reference.md`
- The authoring guide at `${CLAUDE_PLUGIN_ROOT}/skills/sesf/assets/authoring-guide.md`

### Step 2: Read the Document

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which markdown file should I assess?"

Read the full file content before proceeding.

### Step 3: Assess the Document

Analyze the content for signals that indicate whether SESF structure would help human readers.

**Signals FOR conversion** (structural complexity humans struggle with in prose):

- Branching logic buried in paragraphs — humans scan WHEN/THEN blocks faster than nested prose conditionals
- Implicit rule groupings with no visual separation — BEHAVIOR blocks create scannable chapters
- Ordered workflows with no clear step boundaries — PROCEDURE/STEP blocks make sequence explicit
- Rules scattered across sections with no categorization — BEHAVIOR blocks group by concern
- Error handling mentioned in passing — consolidated error table makes all failure modes visible
- Configuration values hard-coded in multiple places — @config centralizes them

**Signals FOR conversion** (human-specific benefits):

- The document is a team reference that multiple people consult
- The document needs to survive personnel changes
- The document is reviewed in PRs and needs to be diffable section by section
- Stakeholders with different expertise read different sections (PMs read BEHAVIORs, engineers read PROCEDUREs)
- The document will be maintained over time — formal blocks make it obvious where to add/remove rules

**Signals AGAINST conversion:**

- The document is a personal note or scratchpad
- The document is purely narrative (explanation, tutorial, opinion)
- The document has no actionable structure — describes concepts, not rules or procedures
- The document is already well-structured with clear BEHAVIOR/PROCEDURE blocks

### Step 4: Present the Assessment

Report your findings:

- **Verdict**: "Would benefit from human-facing SESF" or "Not a good fit"
- **Evidence**: Specific patterns found, with quotes or line references
- **If beneficial**: Suggest a tier. Walk through the thinking steps:
  - Which content maps to BEHAVIOR blocks (declarative rules)?
  - Which content maps to PROCEDURE blocks (ordered steps)?
  - Where are the decision points — WHEN/THEN or @route?
  - What are the failure modes for the error table?
- **If not beneficial**: Explain why and suggest what format suits it better

### Step 5: Offer Conversion

If the document would benefit from SESF, use `AskUserQuestion` to ask:

**Question 1** — Confirm conversion:

- "Would you like me to convert this document to human-readable SESF format?"
- Options:
  - "Yes, convert it" — proceed
  - "No, keep as-is" — stop

If the user declines, stop here.

**Question 2** — Output mode:

Detect whether the file is a Claude Code command or skill by checking for `allowed-tools` or `argument-hint` in its YAML frontmatter. If found, default-suggest "Self-contained".

- "How should the converted specification be structured?"
- Options:
  1. **Self-contained** (spec + executable in one file) *(Recommended if the file has `allowed-tools` or `argument-hint` frontmatter)*
  2. **Split into spec + executable**

**Question 3** — File handling:

- "How should I save the converted specification?"
- Options:
  - "Overwrite the original file"
  - "Save as a new file"

Convert using the `sesf` skill rules, producing SESF v4.1 with formal BEHAVIOR/PROCEDURE blocks. Save according to the user's choice.
