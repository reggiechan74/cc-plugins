---
description: Assess whether a document would benefit from LLM-optimized HSF conversion
argument-hint: <path to markdown file>
allowed-tools: ["Read", "Write", "Edit", "Bash", "AskUserQuestion"]
---

# Assess Document for LLM-Facing HSF Conversion

Evaluate an existing markdown document against HSF v5 suitability criteria, specifically for producing a spec that an LLM agent will execute. Offer conversion if appropriate.

## Audience Context

LLM-facing specs prioritize compliance and token efficiency. The question is: would converting this document to HSF v5 make an LLM follow it more reliably?

## Workflow

### Step 1: Load the Skill

Use the `hsf` skill — it contains all the rules, formats, and validation requirements for HSF v5. Read it fully before proceeding. Also read the reference at `${CLAUDE_PLUGIN_ROOT}/skills/hsf/assets/reference.md`.

### Step 2: Read the Document

If the user provided a file path in the arguments, read it. Otherwise, ask the user:

- "Which markdown file should I assess?"

Read the full file content before proceeding.

### Step 3: Assess the Document

Analyze the content for signals that indicate whether HSF conversion would improve LLM compliance.

**Signals FOR conversion** (structure that LLMs need to follow reliably):

- If/then/else or when/then constructs — LLMs handle these better as @route tables or explicit prose conditionals
- Multi-step workflows — LLMs follow numbered phase-based instructions more reliably than embedded prose procedures
- Validation rules — explicit bold list items with MUST/SHOULD keywords produce better compliance than narrative descriptions
- Error handling scattered throughout — consolidating into a table prevents LLMs from missing error cases
- Configuration values repeated in multiple places — @config prevents LLMs from using stale values

**Signals FOR conversion** (LLM-specific benefits):

- The document will be loaded as a system prompt or skill for an LLM agent
- The document contains instructions that an LLM will execute autonomously
- The document has ambiguous language that an LLM might misinterpret ("handle appropriately", "relevant fields")

**Signals AGAINST conversion:**

- The document is purely narrative guidance for humans (README, style guide, explanation)
- The document is a simple linear checklist with no decisions or error handling
- The document will never be consumed by an LLM
- The document's value is in its narrative flow, not in its structural precision

### Step 4: Present the Assessment

Report your findings:

- **Verdict**: "Would benefit from LLM-facing HSF" or "Not a good fit"
- **Evidence**: Specific patterns found, with quotes or line references
- **If beneficial**: Suggest a tier and outline which HSF features would improve LLM compliance
- **If not beneficial**: Explain why and suggest what format suits it better

### Step 5: Offer Conversion

If the document would benefit from HSF, use `AskUserQuestion` to ask:

**Question 1** — Confirm conversion:

- "Would you like me to convert this document to LLM-facing HSF format?"
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

Convert using the `hsf` skill rules, optimizing for LLM execution. Save according to the user's choice.
