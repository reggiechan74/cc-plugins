---
name: site-generation
description: This skill should be used when the user asks to "generate a website from a report",
  "convert markdown to React site", "create presentation website", "build interactive site
  from research", "turn my report into a website", "make my research interactive",
  "parse report for web", "scaffold Vite React project", "deploy to GitHub Pages",
  or needs guidance on markdown parsing strategy, component composition, interactive element
  detection, or static site generation from research documents.
version: 2.0.0
---

# Research Report to Interactive Website Generation

Generate interactive React presentation websites from markdown research reports using Tailwind CSS v4 + shadcn/ui. Parse report structure into tabbed sections with interactive components, deploy as static sites to GitHub Pages.

## Markdown Parsing Strategy

Parse research report markdown into a structured site architecture:

### Structure Mapping

- **H1 heading** becomes the site title and appears in the browser tab and hero area
- **H2 headings** become top-level tabs in the tabbed navigation
- **H3 headings** become sections within each tab, rendered as scroll-anchored blocks
- **H4+ headings** become subsection headers within their parent section
- **Executive Summary** (if present) becomes a hero callout on the Overview tab
- **Table of Contents** is replaced by the tab navigation — do not render the original TOC
- **References/Endnotes sections** become the Sources tab with CitationCard components
- **Research Methodology** merges into the Sources tab as a collapsible section

### Content Type Detection

Map markdown elements to React components:

| Markdown Pattern | React Component | Detection Rule |
|---|---|---|
| `> blockquote` with legal/official text | `StyledBlockquote` | Contains legislation references, "section", "Act" |
| Tables with comparison data | `ComparisonTable` | 3+ columns, row headers describe same attributes |
| Tables with numerical data | `DataTable` or `Calculator` | Contains `$`, `%`, numerical values |
| Footnote references `[^N]` | `CitationCard` | Inline superscript links to endnotes |
| Bullet/numbered lists | `AnimatedList` | Standard list rendering with reveal animations |
| Bold markers `[VERIFIED]` etc. | `Badge` (shadcn) | Inline badge before content |
| `<!-- interactive: TYPE -->` | Corresponding component | Explicit user marker |
| Formula patterns `X = A × B` | `Calculator` | Mathematical expressions with variables |

### Interactive Element Detection

Auto-detect interactive opportunities using these patterns:

**Calculator candidates:**
- Lines containing `=` with variable names on both sides
- Phrases: "calculated as", "formula", "equals", "multiplied by"
- Tables with a "Total" or "Amount" row that sums other rows
- Percentage-based calculations

**Scenario candidates:**
- "What if" language, conditional phrases
- Ranges of values ("between X and Y")
- Comparison of outcomes under different assumptions
- Sensitivity analysis or variable adjustments

**Timeline candidates:**
- Year references in sequence (2016, 2017, 2020...)
- Date-based tables with status columns
- Process descriptions with sequential steps and dates
- Legislative history with bill numbers and years

**Comparison candidates:**
- Tables with 3+ columns where first column has shared attributes
- "versus", "compared to", "differs from" language
- Side-by-side descriptions of different approaches or entities

### Explicit Markers

Support HTML comment markers for user control:
```html
<!-- interactive: calculator -->
<!-- interactive: timeline -->
<!-- interactive: scenario -->
<!-- interactive: comparison -->
<!-- interactive: chart -->
```

Place markers immediately before the content block they apply to. Markers override AI detection.

## Vite + React Project Scaffold

### Project Configuration

Use Vite with React + Tailwind CSS v4 + shadcn/ui for fast builds and GitHub Pages compatibility.

**Key config files:**
- `vite.config.js` — Set `base` to `/<repo-name>/` for GitHub Pages, `resolve.alias` for `@/`, `manualChunks` for code splitting
- `postcss.config.js` — `@tailwindcss/postcss` plugin
- `jsconfig.json` — `@/` path alias to `./src/*`
- `components.json` — shadcn config: `tsx: false`, style `new-york`, `rsc: false`

**Package dependencies:**
- `react`, `react-dom` — Core framework
- `react-markdown` with `remark-gfm` — Render markdown content within components
- `framer-motion` — Animations for tab transitions and content reveals
- `lucide-react` — Icons (search, external link, chevron, etc.)
- `fuse.js` — Lightweight fuzzy search for Knowledge Vault
- `tailwindcss`, `@tailwindcss/postcss`, `postcss` — Tailwind CSS v4
- `clsx`, `tailwind-merge`, `class-variance-authority` — Utility class composition
- `radix-ui` — Headless UI primitives for shadcn components
- `shadcn` — CLI for installing UI components

**After scaffolding, install shadcn UI components:**
```bash
npx shadcn@latest add card input label table badge accordion collapsible slider button separator
```

### GitHub Pages Deployment

Include `.github/workflows/deploy.yml` for automated deployment:
- Trigger on push to main branch
- Install dependencies, build, deploy to gh-pages
- Use `actions/deploy-pages@v4` for deployment

Also include an `npm run deploy` script using `gh-pages` package as an alternative.

## Component Composition

### Tab Architecture

Each H2 section becomes a tab. Standard tab structure:

1. **Overview** — Executive summary hero + key highlights from the report
2. **[Content Tabs]** — One per major H2 section, containing rendered sections with interactive elements
3. **Knowledge Vault** — Full searchable report content (uses shadcn Accordion)
4. **Sources** — Citations, references, external links (uses shadcn Collapsible + Badge)

### Page Component Pattern

Each tab page follows this pattern:
```
TabPage
├── SectionRenderer (for each H3)
│   ├── Heading with gradient accent line
│   ├── Content (rendered markdown via ReactMarkdown)
│   └── InteractiveElement (if detected)
│       ├── Calculator (Card, Input, Label, Separator)
│       ├── ComparisonTable (Table, Button)
│       ├── TimelineView (Badge)
│       ├── ScenarioSlider (Card, Label, Separator)
│       └── CitationCard (Collapsible, Badge)
```

### Data Flow

Parse report into `reportData.js` structured as:
```
reportData.meta → Site title, date, author
reportData.tabs[] → Tab definitions with sections
reportData.tabs[].sections[] → Section content with optional interactive configs
reportData.citations[] → All footnotes/endnotes with URLs
reportData.externalLinks[] → Deduplicated external URLs with labels
```

Interactive configurations go in `interactiveConfig.js`:
```
interactives[] → Array of interactive element definitions
  .type → calculator | comparison | timeline | scenario
  .tabId → Which tab contains this element
  .sectionId → Which section within the tab
  .config → Type-specific configuration (formula, inputs, data, etc.)
```

## Vercel Agent Skills Integration

After scaffolding the project, install Vercel's agent skills for React code quality:

```bash
npx -y skills add vercel-labs/agent-skills --skill react-best-practices --skill web-design-guidelines --skill composition-patterns -y
```

Read the installed SKILL.md files and apply their rules when generating components:
- **react-best-practices**: 40+ optimization rules — memoization, key stability, bundle splitting, data fetching
- **web-design-guidelines**: 100+ rules — accessibility (ARIA, keyboard nav, color contrast), performance, responsive design
- **composition-patterns**: Component architecture — compound components, state lifting, render delegation

These skills complement the bundled component templates by ensuring the generated code follows production-grade React patterns.

## Build and Deployment

After generating all files:

1. Run `npm install` to install dependencies
2. Run `npm run build` to verify production build succeeds
3. Fix any build errors
4. Provide deployment instructions for GitHub Pages

For detailed component API documentation, see `${CLAUDE_PLUGIN_ROOT}/skills/site-generation/references/component-api.md`.
For a worked example of report parsing, see `${CLAUDE_PLUGIN_ROOT}/skills/site-generation/references/parsing-example.md`.
For starter React component templates, see `${CLAUDE_PLUGIN_ROOT}/templates/src/components/`.
For theme/registry selection, see `${CLAUDE_PLUGIN_ROOT}/skills/design-system/references/registry-guide.md`.
