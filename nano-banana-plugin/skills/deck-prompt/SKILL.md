---
name: deck-prompt
description: This skill should be used when the user asks to "create a presentation", "make a deck", "generate slides", "deck prompt", "report to slides", "convert report to presentation", or mentions creating visual slide decks from markdown or PDF content.
user-invokable: true
argument-hint: report_path --preset name --slides count
---

## Purpose

Decompose a markdown or PDF report into a structured deck specification JSON file that the nano-banana `--deck` mode can consume to generate presentation slide images. Claude reads the source document, understands its structure and content, selects appropriate slide types, writes structured slide fields (heading, visual metaphor, labels, text panel) conforming to a strict schema, and outputs a complete deck spec ready for image generation.

## Path Resolution

When this skill is loaded, Claude Code displays a "Base directory for this skill:" header. Use that absolute path to resolve file paths in all commands below. In the examples, `$BASE_DIR` represents this path. The sibling nano-banana skill lives at `$BASE_DIR/../nano-banana`.

## Workflow

### Step 1: Read the Source Report

Use the Read tool to load the full content of the report file. Supported formats:

- **Markdown (.md):** Read directly.
- **PDF (.pdf):** Read using the PDF reader (specify `pages` for large documents).

Parse the document structure: title, abstract/summary, section headings, body content, tables, statistics, quotes, conclusions, and recommendations.

### Step 2: Load the Presentation Config

Read the presentation config JSON to understand available slide types, prompt prefixes, and brand identity:

```
$BASE_DIR/../nano-banana/presets/presentations/{preset}.json
```

**Available presets:**

| Preset | Style | Color Palette |
|--------|-------|---------------|
| `consulting` (default) | McKinsey/BCG professional | Deep navy, white, coral, light gray |
| `workshop` | Educational, warm, accessible | Warm teal, soft amber, cream, charcoal |
| `pitch` | Startup/VC, bold, high-contrast | Pure black, electric blue, white, neon green |
| `creative` | Portfolio/agency, editorial | Warm cream, matte black, terracotta, sage green |
| `notebooklm` | Architectural engineering, blueprint-inspired | Engineering cream, blueprint navy, copper, teal, steel blue |

If the user does not specify a preset, default to `consulting`.

**What to extract from the config:**
- `global_prompt_prefix` -- prepended to every slide prompt by nano-banana
- `slide_types` -- per-type `prompt_prefix` values (also prepended automatically)
- `default_aspect`, `default_size`, `default_model` -- inherited defaults

You do NOT need to include the global or type prompt prefixes in your slide fields. Nano-banana assembles the full prompt automatically from the structured fields.

### Step 3: Decompose the Report into Slides

Map report sections to slide types using these rules:

| Report Element | Slide Type | When to Use |
|----------------|------------|-------------|
| Report title, author, date, abstract | `title` | Always the first slide. One per deck. |
| Major section headings (H1/H2) | `section-divider` | Use to introduce each major section of the report. |
| Body paragraphs, findings, analysis, explanations | `content` | Core information slides. One key message per slide. |
| Tables, statistics, quantitative data, metrics, charts | `data-chart` | Whenever the source has numbers, comparisons, or trends. |
| Notable quotes, callouts, testimonials, key statements | `quote` | Direct quotes or standout statements worth highlighting. |
| Conclusions, recommendations, next steps, contact info | `closing` | Always the last slide. One per deck. |

**Slide count guidance:**
- If `--slides <count>` is specified, target that number.
- If not specified, use the report length as a guide: roughly 1 slide per major point, typically 6-12 slides for a standard report.
- Every deck must have exactly one `title` slide (first) and one `closing` slide (last).
- Use `section-divider` slides to create visual breaks between major topics; do not use them for every minor heading.

### Step 5: Write Structured Slide Fields

For each slide, write four structured fields: `heading`, `visual`, `labels`, and `text_panel`. Follow these authoring rules strictly.

**Rule 1: Every slide starts with a physical metaphor.** Before writing any field, answer: "What concrete object or scene would a viewer see?" The `visual` field must describe something you could build with your hands or photograph. Not "two columns comparing X and Y" but "a 1D number line dissolving into a 3D coordinate space."

**Rule 2: The `visual` field is the hero -- 60% of the slide area.** Describe the object, its materials, its spatial arrangement. Use engineering/architectural vocabulary: isometric, cross-section, exploded view, dimension lines, blueprint grid. ~30 words max.

**Rule 3: Labels are short annotations ON the visual.** Each label is 1-4 words. They go on or next to the visual element they describe. Think engineering drawing callouts. Array of strings, not sentences.

**Rule 4: `text_panel` is max 2 sentences (~40 words).** This is the "so what" at the bottom. If you can't say it in 2 sentences, the slide is trying to do too much -- split it.

**Rule 5: `heading` is the claim, not the topic (~8 words).** Not "Market Analysis" but "Transportation Leads at $4.2B." The heading states what the viewer should conclude.

**Rule 6: One metaphor per slide, one insight per slide.** If you're describing two different visuals, it's two slides.

**Metaphor mapping table:**

| Report Element | Think About | Example Metaphor |
|---|---|---|
| Core equation/formula | Physical components multiplying | Colored blocks with x operators between them |
| Comparison (A vs B) | Contrasting objects | Split panel: solid cube vs cracked cube |
| Taxonomy/categories | Grid of distinct objects | 4x2 grid of isometric icon cards |
| Process/flow | Connected mechanism | Interlocking gears, conveyor belt |
| Constraints/limitations | Physical barriers | Locked panel vs. open control board |
| Time dynamics | Diverging curves | Exponential growth curve vs decay curve |
| Key quote/principle | Architectural frame | Minimal frame with centered bold statement |

**Good example (structured):**

```json
{
  "slide_number": 3,
  "slide_type": "content",
  "heading": "Deconstructing Human Impact",
  "visual": "four isometric 3D blocks in a row connected by large multiplication signs: blue block (Direct Effect), copper block (Leverage Effect), green block (Time Effect), equals dark block (Organizational Output), with engineering dimension arrows",
  "labels": ["Direct Effect", "Leverage Effect", "Time Effect", "Organizational Output"],
  "text_panel": "Employee impact is not merely additive. It is additive (Ai, Di), multiplicative (Li), and exponential (Ci, Fi).",
  "style_overrides": {}
}
```

**Bad example (old freeform -- DO NOT USE):**

```json
{
  "slide_number": 3,
  "slide_type": "content",
  "layout": "split-horizontal",
  "prompt": "Top half heading 'What Conventional Labels Miss'. Two columns: Left column labeled 'Standard View' showing linear spectrum from Subtractor to Adder to Multiplier..."
}
```

### Step 6: Write the Deck Spec JSON

Write the complete JSON file to:

```
output/nano-banana/decks/{auto_name}.json
```

**Auto-naming convention:** `YYYY-MM-DD_{title_slug}.json` where `title_slug` is the deck title in lowercase with spaces replaced by underscores, truncated to 40 characters. Example: `2026-02-27_infrastructure_ai_market_analysis.json`

### Step 7: Report and Offer Generation

After writing the deck spec:

1. Report the absolute file path of the deck spec.
2. Summarize the deck: total slides, breakdown by type, preset used.
3. Offer to run nano-banana to generate the slide images:

```bash
python3 $BASE_DIR/../nano-banana/scripts/nano_banana.py --deck path/to/deck_spec.json
```

If the user wants to regenerate specific slides (e.g., after prompt edits), use `--force`:

```bash
python3 $BASE_DIR/../nano-banana/scripts/nano_banana.py --deck path/to/deck_spec.json --force
```

## Deck Spec JSON Schema

The deck spec is the contract between this skill and nano-banana's `--deck` mode. Every deck spec must conform to this structure:

```json
{
  "title": "string",
  "presentation_config": "string -- consulting | workshop | pitch | creative | notebooklm",
  "total_slides": "integer",
  "output_dir": "string",
  "slides": [
    {
      "slide_number": "integer -- 1-indexed",
      "slide_type": "string -- title | section-divider | content | data-chart | quote | closing",
      "heading": "string -- Bold title text, ~8 words, states the claim",
      "visual": "string -- Dominant physical metaphor, ~30 words, concrete object/scene",
      "labels": "array of strings -- Short annotations on the visual, 1-4 words each. Optional.",
      "text_panel": "string -- Explanatory text, max 2 sentences. Optional.",
      "reference_image": "string -- Path to style reference image. Optional, null if unused.",
      "style_overrides": "object -- Optional: { aspect, size, model }"
    }
  ]
}
```

**Required fields:** `title`, `presentation_config`, `total_slides`, `output_dir`, `slides`
**Required per-slide fields:** `slide_number`, `slide_type`, `heading`, `visual`
**Optional per-slide fields:** `labels` (defaults to `[]`), `text_panel` (defaults to `""`), `reference_image` (defaults to `null`), `style_overrides` (defaults to `{}`)

**Backward compatibility:** The old `prompt` and `layout` fields still work but should NOT be used in new deck specs.

**`output_dir` convention:** Use `output/nano-banana/decks/YYYY-MM-DD_{title_slug}` for relative paths. Nano-banana resolves relative paths from the current working directory (project root).

## Slide Types Reference

| Type | Purpose | Typical Count |
|------|---------|---------------|
| `title` | Opening slide with deck title, subtitle, author | Exactly 1 (first) |
| `section-divider` | Visual break introducing a major section | 1-4 per deck |
| `content` | Core information: findings, analysis, explanations | 2-6 per deck |
| `data-chart` | Quantitative data: charts, tables, metrics | 1-3 per deck |
| `quote` | Notable quotes, callouts, key statements | 0-2 per deck |
| `closing` | Conclusions, recommendations, next steps, contact | Exactly 1 (last) |

## Example Deck Spec

A 6-slide consulting deck generated from a hypothetical market analysis report:

```json
{
  "title": "Canadian Infrastructure AI Opportunity",
  "presentation_config": "consulting",
  "total_slides": 6,
  "output_dir": "output/nano-banana/decks/2026-02-27_canadian_infrastructure_ai",
  "slides": [
    {
      "slide_number": 1,
      "slide_type": "title",
      "heading": "Canadian Infrastructure AI Opportunity",
      "visual": "subtle circuit-board pattern fading into cityscape silhouette with blueprint grid lines",
      "labels": [],
      "text_panel": "Market Analysis Q1 2026 | Tenebrus Capital",
      "style_overrides": {}
    },
    {
      "slide_number": 2,
      "slide_type": "section-divider",
      "heading": "Market Landscape",
      "visual": "abstract visualization of interconnected infrastructure nodes -- roads, bridges, power lines rendered as glowing isometric network graph",
      "labels": [],
      "text_panel": "Understanding the $4.2B Canadian infrastructure AI market",
      "style_overrides": {}
    },
    {
      "slide_number": 3,
      "slide_type": "data-chart",
      "heading": "Transportation Leads at $1.8B",
      "visual": "bar chart showing four vertical bars of decreasing height, with the tallest bar highlighted in coral accent",
      "labels": ["Transportation $1.8B", "Energy $1.4B", "Water $0.6B", "Telecom $0.4B"],
      "text_panel": "42% CAGR since 2023. Transportation sector alone exceeds combined water and telecom spending.",
      "style_overrides": {}
    },
    {
      "slide_number": 4,
      "slide_type": "content",
      "heading": "Three Forces Driving Convergence",
      "visual": "three overlapping translucent circles forming a Venn diagram, each containing a distinct isometric icon: government building, digital twin cube, AI chip",
      "labels": ["Federal $14B bill", "Municipal digital twin mandates", "60% private AI adoption"],
      "text_panel": "Federal infrastructure spending, municipal digital twin mandates, and private sector AI adoption are converging to create a structural opportunity.",
      "style_overrides": {}
    },
    {
      "slide_number": 5,
      "slide_type": "quote",
      "heading": "By 2028, 75% of Canadian infrastructure inspections will involve AI-assisted analysis",
      "visual": "subtle geometric pattern of intersecting lines forming an abstract bridge structure",
      "labels": [],
      "text_panel": "-- Canadian Infrastructure Report Card 2025",
      "style_overrides": {}
    },
    {
      "slide_number": 6,
      "slide_type": "closing",
      "heading": "Recommendations & Next Steps",
      "visual": "three ascending platforms connected by arrows, each containing an isometric icon: target, handshake, calendar",
      "labels": ["Target transportation vertical", "Build municipal pilot", "Secure partnerships by Q3"],
      "text_panel": "Contact: reggie@tenebruscapital.com | Tenebrus Capital Corp",
      "style_overrides": {}
    }
  ]
}
```

## Argument Handling

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<report_path>` | Yes | -- | Path to the source markdown or PDF report |
| `--preset <name>` | No | `consulting` | Presentation config to use: `consulting`, `workshop`, `pitch`, `creative`, `notebooklm` |
| `--slides <count>` | No | auto | Target number of slides; if omitted, derive from report length |

## Error Handling

- If the report file does not exist or cannot be read, inform the user and stop.
- If the requested preset does not have a matching config file, list available presets and ask the user to choose.
- If the report is too short to fill the requested slide count, inform the user and suggest a lower count.
- If the report has no clear structure (no headings, no sections), do your best to decompose by paragraph and inform the user that results may vary.
