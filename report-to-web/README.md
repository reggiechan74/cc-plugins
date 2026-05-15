# report-to-web

<!-- badges-start -->
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)
<!-- badges-end -->

Convert markdown research reports into interactive React presentation websites for GitHub Pages.

## Installation

### From Marketplace
```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install report-to-web@cc-plugins
```

### Local Development
Clone `reggiechan74/cc-plugins`, then from inside the clone:
```
/plugin marketplace add .
/plugin install report-to-web@cc-plugins
```

## Features

- **Reusable generator** — works with any structured markdown research report
- **Tailwind CSS v4 + shadcn/ui** — modern utility-first styling with swappable component registries
- **Theme presets** — 8 built-in dark color themes + community registry support
- **Interactive elements** — calculators, scenario sliders, comparison tables, timelines
- **Knowledge vault** — searchable full-text report content
- **Dark professional theme** — refined typography (DM Serif Display + IBM Plex Sans), amber accent system
- **GitHub Pages ready** — Vite build with included deploy workflow
- **Vercel agent skills** — integrates react-best-practices, web-design-guidelines, and composition-patterns

## Quick Start

```bash
/report-to-web:generate path/to/your-report.md
```

The command will:
1. Ask where to create the output project
2. Ask your preferred interactivity level (presentation, full-interactive, or both)
3. Ask your preferred visual style (Dark Professional, shadcn color presets, or community registry)
4. Parse the report structure and generate a complete React site

## Components

### Command
- `/report-to-web:generate` — Main entry point

### Skills
- **site-generation** — Markdown parsing strategy, component mapping, project scaffolding
- **design-system** — Dark professional theme tokens, typography, animation patterns

### Agent
- **site-builder** — Autonomous agent that parses reports and generates React projects

### Bundled React Components
- `TabbedLayout` — Tab navigation shell with animated transitions
- `Calculator` — Interactive formula calculator with live results
- `ComparisonTable` — Filterable side-by-side comparison
- `TimelineView` — Vertical timeline with expandable events
- `CitationCard` — Expandable reference cards with external links
- `KnowledgeVault` — Searchable full-text content browser
- `ScenarioSlider` — What-if scenario explorer with sliders
- `SectionRenderer` — Markdown renderer with scroll-triggered animations

## Interactivity Detection

The site-builder agent auto-detects interactive opportunities:

| Report Pattern | Component |
|---|---|
| Formulas (`Tax = CVA x Rate`) | Calculator |
| Comparison tables (3+ columns) | ComparisonTable |
| Chronological dates / timelines | TimelineView |
| What-if language / ranges | ScenarioSlider |
| Footnotes / endnotes | CitationCard |

You can also add explicit markers in your report:
```html
<!-- interactive: calculator -->
<!-- interactive: timeline -->
<!-- interactive: scenario -->
<!-- interactive: comparison -->
```

## Generated Site Structure

```
output-dir/
├── package.json
├── vite.config.js
├── postcss.config.js
├── jsconfig.json
├── components.json
├── index.html
├── .github/workflows/deploy.yml
├── src/
│   ├── main.jsx
│   ├── app.css
│   ├── App.jsx
│   ├── data/
│   │   ├── reportData.js
│   │   └── interactiveConfig.js
│   ├── themes/           (selected theme preset)
│   ├── theme/
│   │   └── motion.js     (framer-motion tokens)
│   ├── lib/
│   │   └── utils.js      (cn() utility)
│   ├── components/
│   │   ├── ui/           (installed by npx shadcn add)
│   │   └── *.jsx         (bundled custom components)
│   └── pages/            (generated per report)
```

## Prerequisites

- Node.js 18+
- npm

## License

MIT
