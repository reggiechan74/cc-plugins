---
description: "Convert a mathematically dense document into a plain-English companion version with explanation callouts"
argument-hint: "<path to document> [output_path]"
allowed-tools: AskUserQuestion, Read, Write, Agent, Bash, Glob
model: sonnet
---

# Plain-English Companion Generator

**Purpose:** Take a mathematically dense, symbol-heavy, or conceptually difficult document and produce a companion version that adds plain-English explanation callouts after complex sections. The original text is preserved by default.

## Instructions

When this command is invoked:

### Step 1: Parse Arguments

- First argument (required): path to the source document
- Second argument (optional): output path. Default: `<source_name>_plain_english.md` in the same directory

If no file path is provided, use AskUserQuestion to request one.

### Step 2: Read and Analyze the Source Document

Read the source document. Perform a quick structural analysis:
- Count sections/headings
- Identify math-heavy sections (LaTeX `$...$`, `$$...$$`, Greek symbols, formal notation)
- Identify conceptually dense sections (formal definitions, domain-specific jargon, multi-layered abstractions)
- Estimate total complexity (light, moderate, heavy)

Report to the user:
```
Analyzed: <filename>
- <N> sections, <M> lines
- Math density: <light/moderate/heavy> (<count> formulas detected)
- Estimated output: ~<N> callout insertions
```

### Step 3: Interview the User

Use AskUserQuestion to ask the following questions **one at a time**. Each question should include the multiple-choice options and a brief note on trade-offs.

If at any point the user says "defaults", "defaults are fine", "just go", "skip", or similar — stop the interview and use defaults for all remaining questions.

**Question 1 — Audience:**
```
Who is the primary audience for the plain-English version?

A) Executives/decision-makers — focus on "so what?" and strategic implications
B) Practitioners/operators — focus on "how do I use this?" with concrete examples
C) Smart generalist (grade 12 level) — focus on intuition and everyday analogies
D) All of the above — layered callouts serving all three
E) Custom — describe your audience

(Default: C)
```

**Question 2 — Callout structure:**
```
How should the explanation boxes be structured?

A) Single callout per section — one cohesive "Plain English" explanation box
B) Tiered callouts — separate labeled boxes:
   💡 What This Means (intuition)
   🔧 How To Apply This (operational)
   ⚡ Why This Matters (executive)
C) Single callout with bolded lead-ins — one box with internal structure
   (In plain terms: / In practice: / The takeaway:)

Note: If you chose audience (D) above, option B works best to let each audience find their layer.
(Default: A, or B if audience is "all of the above")
```

**Question 3 — Original text handling:**
```
Should the original document text be preserved as-is?

A) Full preservation — original text stays verbatim, callouts inserted after sections
B) Simplified rewrite — original prose rewritten in simpler language, callouts only for math
C) Hybrid — keep math/formulas intact, simplify surrounding prose, callouts for the heavy math

(Default: A)
```

**Question 4 — Placement strategy:**
```
Should every section get explanation callouts, or only the dense ones?

A) All sections get callouts — consistent structure throughout
B) Adaptive — math-heavy and conceptually dense sections get full treatment;
   simpler sections get fewer or no callouts (I'll use my judgment)
C) Math only — callouts appear only where there are formulas or Greek symbols

(Default: B)
```

**Question 5 — Reading level:**
```
What reading level should the explanations target?

A) Grade 10 — very simple language, basic analogies
B) Grade 12 — accessible but not dumbed down, can handle some abstraction
C) Undergraduate — assumes comfort with basic math concepts, explains the hard parts
D) Custom — describe the level

(Default: B)
```

**Question 6 — Output format:**
```
What callout syntax should I use?

A) Obsidian-compatible callouts (> [!tip], > [!example], > [!important])
B) Plain blockquotes (> **💡 What This Means:** ...)
C) GitHub-compatible (blockquotes with bold headers — renders on GitHub)
D) HTML details/summary tags (collapsible sections)

(Default: A)
```

### Step 4: Build the Configuration

After the interview, assemble the configuration object from the user's answers. Apply defaults for any skipped questions. Summarize the configuration back to the user before proceeding:

```
Configuration:
- Audience: <answer>
- Callout structure: <answer>
- Original text: <preserved/simplified/hybrid>
- Placement: <all/adaptive/math-only>
- Reading level: <answer>
- Output format: <answer>
- Output file: <path>

Proceeding with generation...
```

### Step 5: Generate the Companion Document

Launch a general-purpose Agent to create the companion document. The agent prompt must include:

1. **The full source document content** (read it and pass it in)
2. **The user's configuration** from Step 4
3. **The callout format templates** based on the user's choices
4. **Writing guidelines per callout type:**
   - 💡 What This Means / Intuition: Use everyday analogies. "Think of it like..." Keep at the target reading level. Explain what the math is actually saying in human terms. 3-6 sentences.
   - 🔧 How To Apply This / Operational: Concrete guidance. "When scoring..." or "In practice, this means..." Give specific examples. 3-6 sentences.
   - ⚡ Why This Matters / Executive: Strategic implications. "This changes the conversation from..." Connect to business outcomes. 2-4 sentences.
5. **Placement rules** based on the user's adaptive/all/math-only choice
6. **Instruction to preserve all original text verbatim** (unless user chose simplified/hybrid)
7. **YAML frontmatter** for the output file including `companion_to:` referencing the source

The agent prompt must explicitly state:
- Write the COMPLETE file — do not truncate
- Every line of the original must appear (if preservation mode)
- Get today's date via `TZ='America/New_York' date '+%Y-%m-%d'` for the lastUpdated field

### Step 6: Verify and Report

After the agent completes:

1. Verify the output file exists and is non-empty
2. Count lines in original vs companion
3. Count callout insertions (grep for the callout syntax markers)
4. Compare section headings between original and companion to verify completeness
5. Report:

```
Complete.
- Source: <original_file> (<N> lines)
- Output: <output_file> (<M> lines)
- Callouts inserted: <count>
- Section headings: <match status>
```

## Callout Templates

### Obsidian Format (default)

**Tiered (audience = all):**
```markdown
> [!tip] 💡 What This Means
> <intuition-level explanation>

> [!example] 🔧 How To Apply This
> <operational guidance>

> [!important] ⚡ Why This Matters
> <executive-level implications>
```

**Single:**
```markdown
> [!note] 📖 Plain English
> <combined explanation at target reading level>
```

**Single with lead-ins:**
```markdown
> [!note] 📖 Plain English
> **In plain terms:** <intuition>
> **In practice:** <operational>
> **The takeaway:** <executive>
```

### Plain Blockquote Format

```markdown
> **💡 What This Means**
> <explanation>
```

### GitHub-Compatible Format

```markdown
> **💡 What This Means**
>
> <explanation>
```

### HTML Collapsible Format

```html
<details>
<summary>💡 What This Means</summary>
<p>explanation</p>
</details>
```

## Defaults Summary

| Setting | Default |
|---------|---------|
| Audience | Smart generalist (grade 12) |
| Callout structure | Single callout |
| Original text | Preserved verbatim |
| Placement | Adaptive |
| Reading level | Grade 12 |
| Output format | Obsidian callouts |

## Example Usage

```
/plain-english /path/to/math-heavy-paper.md
/plain-english /path/to/paper.md /path/to/output.md
```
