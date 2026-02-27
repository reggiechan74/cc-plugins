---
name: deck-prompt
description: This skill should be used when the user asks to "create a presentation", "make a deck", "generate slides", "deck prompt", "report to slides", "convert report to presentation", or mentions creating visual slide decks from markdown or PDF content.
user-invokable: true
argument-hint: report_path --preset name --slides count
---

## Purpose

Decompose a markdown or PDF report into a structured deck specification JSON file that the nano-banana `--deck` mode can consume to generate presentation slide images. Claude reads the source document, understands its structure and content, selects appropriate slide types and layouts, writes concise visual prompts for each slide, and outputs a complete deck spec ready for image generation.

## Workflow

### Step 1: Read the Source Report

Use the Read tool to load the full content of the report file. Supported formats:

- **Markdown (.md):** Read directly.
- **PDF (.pdf):** Read using the PDF reader (specify `pages` for large documents).

Parse the document structure: title, abstract/summary, section headings, body content, tables, statistics, quotes, conclusions, and recommendations.

### Step 2: Load the Presentation Config

Read the presentation config JSON to understand available slide types, layouts, prompt prefixes, and brand identity:

```
$CLAUDE_PLUGIN_ROOT/skills/nano-banana/presets/presentations/{preset}.json
```

**Available presets:**

| Preset | Style | Color Palette |
|--------|-------|---------------|
| `consulting` (default) | McKinsey/BCG professional | Deep navy, white, coral, light gray |
| `workshop` | Educational, warm, accessible | Warm teal, soft amber, cream, charcoal |
| `pitch` | Startup/VC, bold, high-contrast | Pure black, electric blue, white, neon green |
| `creative` | Portfolio/agency, editorial | Warm cream, matte black, terracotta, sage green |

If the user does not specify a preset, default to `consulting`.

**What to extract from the config:**
- `global_prompt_prefix` -- prepended to every slide prompt by nano-banana
- `slide_types` -- per-type `prompt_prefix` values (also prepended automatically)
- `layouts` -- available layout options for this preset
- `default_aspect`, `default_size`, `default_model` -- inherited defaults

You do NOT need to include the global or type prompt prefixes in your slide prompts. Nano-banana assembles the full prompt automatically using this order:

```
global_prompt_prefix + slide_type.prompt_prefix + "Layout: {layout}. " + slide.prompt
```

Your `slide.prompt` field only needs the slide-specific content description.

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

### Step 4: Select Layouts for Each Slide

Choose a layout from the config's `layouts` array for each slide. Available layouts and their best use:

| Layout | Description | Best For |
|--------|-------------|----------|
| `centered-statement` | Text centered vertically and horizontally | Title slides, quotes, section dividers with short text, bold single statements |
| `left-visual-right-text` | Image/visual on left, text content on right | Content slides with supporting imagery, section dividers with topic visuals |
| `full-bleed-image` | Image fills the entire slide area | Data charts, hero visuals, dramatic photography, creative title slides |
| `split-horizontal` | Top and bottom halves divided | Before/after comparisons, two related points, complementary content |
| `grid-2x2` | Four equal quadrants | Comparing four items, SWOT-style analysis, multiple metrics |
| `grid-3-column` | Three equal columns | Three-point arguments, process steps, category comparisons |

Each slide type has a `default_layout` in the config. Use the default unless a different layout better serves the specific content of that slide.

### Step 5: Write Slide Prompts

**Prompt writing rules:**

1. **Maximum ~50 words per prompt.** Be concise and specific. Every word must earn its place.
2. **Lead with the visual description.** Describe what the viewer sees first, then the text content.
3. **Include key data verbatim.** If the source has a specific number, percentage, dollar amount, or date, include it exactly as stated. Do not paraphrase data.
4. **One key message per slide.** Do not cram multiple concepts into a single prompt.
5. **Do not repeat the type/layout/brand prefixes.** Nano-banana prepends those automatically. Your prompt is only the slide-specific content.
6. **Use concrete nouns and action verbs.** "Bar chart showing Q3 revenue growth from $2.1M to $3.4M" beats "chart about revenue."
7. **Specify text content in single quotes.** For any text that should appear on the slide, wrap it in single quotes so the model treats it as literal text to render.

**Good prompt examples:**
- `"'Infrastructure AI Market Analysis' subtitle 'Prepared for Acme Corp' with abstract city skyline silhouette"`
- `"Bar chart comparing five regional markets, Toronto leads at $4.2B, Vancouver second at $2.8B, coral highlight on Toronto bar"`
- `"'The convergence of AI and infrastructure creates a $50B opportunity by 2030' -- Industry Report 2025"`

**Bad prompt examples (avoid these):**
- `"A nice title slide with the report name"` -- too vague, no actual content
- `"Professional consulting slide showing the data from section 3 about the market"` -- no specific data, references source instead of extracting
- `"Deep navy background with white sans-serif text showing..."` -- repeating brand/style instructions that the prefix already handles

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
python3 $CLAUDE_PLUGIN_ROOT/skills/nano-banana/scripts/nano_banana.py --deck path/to/deck_spec.json
```

If the user wants to regenerate specific slides (e.g., after prompt edits), use `--force`:

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/nano-banana/scripts/nano_banana.py --deck path/to/deck_spec.json --force
```

## Deck Spec JSON Schema

The deck spec is the contract between this skill and nano-banana's `--deck` mode. Every deck spec must conform to this structure:

```json
{
  "title": "string -- Deck title, displayed in logs and used for output directory naming",
  "presentation_config": "string -- Preset name: consulting | workshop | pitch | creative",
  "total_slides": "integer -- Total number of slides in the deck",
  "output_dir": "string -- Relative path (from project root) or absolute path for generated images",
  "slides": [
    {
      "slide_number": "integer -- 1-indexed position in the deck",
      "slide_type": "string -- One of: title | section-divider | content | data-chart | quote | closing",
      "layout": "string -- One of: centered-statement | left-visual-right-text | full-bleed-image | split-horizontal | grid-2x2 | grid-3-column",
      "prompt": "string -- Slide-specific prompt (~50 words max). Do NOT include global/type prefixes.",
      "style_overrides": "object -- Optional overrides: { aspect, size, model }. Empty {} to use config defaults."
    }
  ]
}
```

**Required fields:** `title`, `presentation_config`, `total_slides`, `output_dir`, `slides`
**Required per-slide fields:** `slide_number`, `slide_type`, `layout`, `prompt`
**Optional per-slide fields:** `style_overrides` (defaults to `{}`)

**`output_dir` convention:** Use `output/nano-banana/decks/YYYY-MM-DD_{title_slug}` for relative paths. Nano-banana resolves relative paths from the current working directory (project root).

## Slide Types Reference

| Type | Purpose | Typical Count | Default Layout |
|------|---------|---------------|----------------|
| `title` | Opening slide with deck title, subtitle, author | Exactly 1 (first) | `centered-statement` |
| `section-divider` | Visual break introducing a major section | 1-4 per deck | `left-visual-right-text` |
| `content` | Core information: findings, analysis, explanations | 2-6 per deck | `left-visual-right-text` |
| `data-chart` | Quantitative data: charts, tables, metrics | 1-3 per deck | `full-bleed-image` |
| `quote` | Notable quotes, callouts, key statements | 0-2 per deck | `centered-statement` |
| `closing` | Conclusions, recommendations, next steps, contact | Exactly 1 (last) | `centered-statement` |

## Layouts Reference

| Layout | Composition | Best Paired With |
|--------|-------------|------------------|
| `centered-statement` | Text centered vertically and horizontally with generous whitespace | `title`, `quote`, `closing`, `section-divider` |
| `left-visual-right-text` | Visual element on left ~40%, text content on right ~60% | `content`, `section-divider` |
| `full-bleed-image` | Image fills entire slide; text overlaid or integrated | `data-chart`, `creative title`, hero visuals |
| `split-horizontal` | Top half and bottom half divided by a horizontal rule or whitespace | Before/after, two complementary points |
| `grid-2x2` | Four equal quadrants | SWOT analysis, four-metric dashboards, comparisons |
| `grid-3-column` | Three equal vertical columns | Three-step processes, triple comparisons, category breakdowns |

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
      "layout": "centered-statement",
      "prompt": "'Canadian Infrastructure AI Opportunity' subtitle 'Market Analysis Q1 2026' with subtle circuit-board pattern fading into cityscape silhouette",
      "style_overrides": {}
    },
    {
      "slide_number": 2,
      "slide_type": "section-divider",
      "layout": "left-visual-right-text",
      "prompt": "'Market Landscape' with abstract visualization of interconnected infrastructure nodes rendered as glowing network graph",
      "style_overrides": {}
    },
    {
      "slide_number": 3,
      "slide_type": "data-chart",
      "layout": "full-bleed-image",
      "prompt": "Bar chart showing Canadian infrastructure AI spending by sector: Transportation $1.8B, Energy $1.4B, Water $0.6B, Telecom $0.4B. Coral highlight on Transportation bar. Annotation: '42% CAGR since 2023'",
      "style_overrides": {}
    },
    {
      "slide_number": 4,
      "slide_type": "content",
      "layout": "left-visual-right-text",
      "prompt": "Heading: 'Three Convergence Drivers'. Visual of overlapping circles. Points: '1. Federal infrastructure bill ($14B allocated)' '2. Municipal digital twin mandates' '3. Private sector AI adoption reaching 60%'",
      "style_overrides": {}
    },
    {
      "slide_number": 5,
      "slide_type": "quote",
      "layout": "centered-statement",
      "prompt": "'By 2028, 75% of Canadian infrastructure inspections will involve AI-assisted analysis' -- Canadian Infrastructure Report Card 2025",
      "style_overrides": {}
    },
    {
      "slide_number": 6,
      "slide_type": "closing",
      "layout": "centered-statement",
      "prompt": "'Recommendations & Next Steps'. Three action items: 'Target transportation vertical first' 'Build municipal pilot program' 'Secure strategic partnerships by Q3'",
      "style_overrides": {}
    }
  ]
}
```

## Argument Handling

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<report_path>` | Yes | -- | Path to the source markdown or PDF report |
| `--preset <name>` | No | `consulting` | Presentation config to use: `consulting`, `workshop`, `pitch`, `creative` |
| `--slides <count>` | No | auto | Target number of slides; if omitted, derive from report length |

## Error Handling

- If the report file does not exist or cannot be read, inform the user and stop.
- If the requested preset does not have a matching config file, list available presets and ask the user to choose.
- If the report is too short to fill the requested slide count, inform the user and suggest a lower count.
- If the report has no clear structure (no headings, no sections), do your best to decompose by paragraph and inform the user that results may vary.
