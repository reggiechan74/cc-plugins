---
description: "Review a draft math paper for mathematical coherence — layered assessment with interactive discussion"
argument-hint: "<path-to-file.md or .model.md or .pdf>"
allowed-tools: ["Bash", "Read", "Write", "Edit", "Glob"]
arguments:
  - name: "file"
    description: "Path to a .md, .model.md, or .pdf file to review"
---

# Review a Math Paper

Perform a layered mathematical coherence assessment of a draft paper. Walk through five review layers with the user, resolve every finding through discussion, and produce a findings file that can be fed to `/math-paper-creator:author` in a fresh session.

## Step 1: Locate and load the file

**If a path is given:**

1. Check the file extension:
   - `.md` or `.model.md` — read the file directly.
   - `.pdf` — convert to markdown first (see PDF Handling below).
2. If the file does not exist, tell the user and stop.

**If no path is given:**

1. Search with Glob for `**/*.md` and `**/*.pdf` (excluding `*.model.md` files).
2. If matches are found, show at most 20 and ask the user which one to review.
3. If more than 20 matches exist, tell the user and ask for a path directly.
4. If no matches are found, tell the user and stop.

### PDF Handling

When the input is a PDF:

1. Read the PDF using the Read tool's PDF support. For PDFs over 10 pages, read in chunks using the `pages` parameter (e.g., pages 1-10, then 11-20).
2. Convert the content to a markdown file: `<original-basename>.md` in the same directory as the PDF.
3. Present the converted markdown to the user: "Does this conversion look reasonable? Any sections garbled or missing?"
4. Wait for the user to confirm before proceeding. If they flag issues, fix and re-present.
5. Proceed with the review against the markdown file.

## Step 2: Check for existing review

Check if a `<basename>.review.md` file already exists in the same directory as the input file.

**If it exists:** Read the frontmatter. If `status: in_progress`, offer to resume:
> "I found an existing review for this file (currently at Layer [N], Finding [M]). Want to resume from where we left off, or start a fresh review?"

If the user wants to resume, load the findings file and continue from `current_layer` / `current_finding`. If they want a fresh review, proceed to Step 3 (the old findings file will be overwritten at the end).

**If it does not exist:** Proceed to Step 3.

## Step 3: Initialize the findings file

Create `<original-basename>.review.md` in the same directory as the input file with initial frontmatter:

```yaml
---
source: <input filename>
status: in_progress
current_layer: 1
current_finding: 0
template: null
outline: []
---
```

Write this file immediately. It will be updated as the review progresses.

## Step 4: Layered review

Run five review layers in order. For each layer:

1. **Re-read the document** (or relevant sections) to ground the assessment in the actual text, not accumulated conversation context.
2. **Assess** against the layer's criteria (see layer definitions below).
3. **Present findings** one at a time. For each finding, show:
   - A severity tag: `[FATAL]`, `[GAP]`, `[INCONSISTENCY]`, `[WEAK]`, or `[MINOR]`
   - What was found, with specific references to sections, equations, or line numbers
   - Why it matters for the model's coherence
4. **Discuss each finding** with the user. Ask:
   - "Want to discuss this further?"
   - "Acknowledged — moving on?"
   - "Do you disagree with this assessment?"

   During discussion, ask follow-up questions to understand the user's intent: "What did you actually mean this section to express?" or "Should this be a constraint or just an observation?" Capture these clarifications — the findings file needs the user's thinking, not just Claude's critique, so that `/author` can use it as context.
5. **Resolve each finding** before moving to the next. Every finding must reach one of these outcomes:
   - **Resolved with decision** — the user states what should be done. Capture the decision and the user's reasoning/intent behind it.
   - **Resolved by removal** — the user decides this content doesn't belong. Capture what's being cut and why.
   - **Resolved by deferral to domain expert** — the user cannot resolve this now. **Pause the review.** Update the findings file with progress (`current_layer`, `current_finding`), tell the user they can resume later with the same command, and stop.

**The user may NOT say "we'll figure it out later", "let's skip this", or "not sure, move on."** If the user attempts to defer without committing to the domain-expert pause, explain: "Unresolved findings propagate into the model as ambiguity that compounds in later sections. If you can't resolve this now, we can pause the review and you can come back when you have the answer. But I can't move past it."

6. **After resolving all findings in a layer**, update the findings file: increment `current_layer`, reset `current_finding` to 0, and append the layer's findings to the file body.

### If no findings in a layer

If a layer has no findings (the paper is clean on that dimension), say so and move to the next layer. This is fine — not every paper has issues at every level.

### Layer 1: Core Model Identification

Re-read the document. Answer these questions:

- What is this paper trying to model?
- What is the decision being made? (What does the decision-maker control?)
- What is being optimized, predicted, or evaluated?
- Is there a clear, formal problem statement?

Present findings for anything missing, unclear, or contradictory. Common findings:
- No formal objective function
- Multiple disconnected models with no stated relationship
- The paper describes a process but never defines what is being decided or optimized
- The "model" is actually a simulation with no analytical framework

**After resolving all Layer 1 findings:** Read the template files from `${CLAUDE_PLUGIN_ROOT}/templates/` (optimization, statistical, game-theoretic, simulation, decision-analysis, financial-pricing, actuarial, econometric, queueing, graph-network). Identify which best fits the model, or "custom" if none fit. Present the recommendation to the user. Update the findings file frontmatter with `template: <name>`.

**Early termination:** If Layer 1 reveals there is no identifiable core model (the paper is too vague or scattered), surface this:
> "I cannot identify a coherent core model in this paper. It may be better to start fresh with `/math-paper-creator:author` rather than trying to review what's here. Want to continue the review anyway, or stop here?"

If the user wants to stop, write what was learned to the findings file with `status: complete` and a summary explaining why the review ended early.

### Layer 2: Mathematical Completeness

Re-read the document. For every mathematical concept mentioned, check:

- Is it formally defined (equation, not just prose)?
- Are all symbols introduced before use?
- Are domains, indices, and units specified?
- Are there concepts mentioned in prose that never get formalized?
- Are there equations stated but never developed (e.g., "solve numerically" with no method)?

Common findings:
- Parameter appears in an equation but is never defined in the model setup
- A concept is described in words but has no corresponding mathematical definition
- An equation is stated but key terms within it are undefined
- "We use standard technique X" without specifying which variant or how it applies

### Layer 3: Internal Consistency

Re-read the document. Check whether the pieces fit together:

- Do variables maintain consistent meaning, notation, and indices across sections?
- Do constraints reference the correct variables and sets?
- Are there circular dependencies?
- Do sub-models connect to each other?
- Are assumptions in one section contradicted in another?

For `.model.md` files: also check whether existing `python:validate` blocks are consistent with the model as understood from the Layer 1-2 discussion. If validate blocks register symbols that don't match the agreed-upon model, flag them.

Common findings:
- Two sections define the same concept differently
- A constraint references a variable with indices that don't match its definition
- The discrete model and continuous model use incompatible variable spaces
- An assumption (e.g., "parameters are constant") is violated later

### Layer 4: Structure and Organization

Re-read the document. Assess:

- Does the section flow make logical sense? (Sets before parameters, parameters before variables, etc.)
- Is executable code being used as a substitute for mathematical formalization?
- Is notation consistent throughout? (Same symbol always means the same thing)
- Would the paper benefit from Part groupings?
- Are there sections that try to do too much?

Common findings:
- Entire sections are Python code with no mathematical specification
- Notation switches between equivalent forms (K_i^n vs K_{i,n})
- A section defines sets, parameters, variables, AND constraints all at once
- The paper jumps from model definition to simulation results with no formal objective

### Layer 5: Prose and Presentation

Re-read the document. Assess:

- Are there placeholder or stub sections?
- Is the abstract/introduction accurate to what the paper actually delivers?
- Does the conclusion summarize what was actually shown?
- Is the writing clear and precise?
- Are claims supported by the formal model?

Common findings:
- Placeholder text: "(Using the expanded introduction from previous responses)"
- Conclusion is a single sentence
- Abstract promises features the paper doesn't deliver
- Prose makes claims not supported by the mathematical framework

## Step 5: Finalize findings

After all five layers are complete:

1. Update the findings file frontmatter: set `status: complete`.
2. Build the recommended section outline based on the identified template and all decisions made during the review. Update `outline` in frontmatter.
3. Write Part 1 (Summary) at the top of the findings file body:
   - One paragraph: what the paper is about (as understood after review)
   - Recommended template
   - Recommended section outline
   - Key decisions made during review (bulleted list)
   - What can be salvaged from the original vs. what needs to be built from scratch
4. Ensure Part 2 (Detailed Findings) contains all five layers' findings. Each finding entry must include:
   - The severity tag and finding description
   - The resolution (what was decided)
   - Relevant quotes or references from the original paper
   - User's stated intent where captured during discussion
5. Tell the user:
   > "Review complete. Findings saved to `<path>`. To build the model from this review, run `/math-paper-creator:author` in a fresh session and provide the review file as context."
