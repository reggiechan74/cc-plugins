# d3-visualizations

A Claude Code plugin that provides comprehensive D3.js v7 knowledge for quickly creating any kind of data visualization.

## Features

- **All D3 chart types**: bar, line, area, scatter, pie, histogram, treemap, sunburst, force-directed, Sankey, chord, choropleth, and more
- **173 gallery templates**: configuration files covering every example from the Observable D3 Gallery
- **Three output formats**: standalone HTML, HTML + separate JS, React components
- **Two workflows**: direct implementation (fast) and creative mode (design philosophy + implementation)
- **Discovery interview**: 3-round, 12-question process to understand requirements before building
- **Clean professional style**: NYT/FT-inspired defaults with muted colors, clean axes, good typography
- **Single-screen layout**: 100vh no-scroll default for easy PDF/screenshot export
- **Sample data generation**: visualizations work immediately out of the box

## Installation

```bash
claude --plugin-dir /path/to/d3-visualizations
```

## Usage

The `d3js` skill activates automatically when you mention D3, charts, or data visualization. Examples:

- "Create a D3 bar chart showing quarterly revenue"
- "Make a force-directed graph of this network data"
- "Build a choropleth map of US states"
- "Create a scatter plot as a React component"
- "Create an artistic data visualization" (triggers creative mode)

## Structure

```
skills/d3js/
├── SKILL.md                          # Core workflow and best practices
├── references/
│   ├── chart-patterns.md             # Bar, line, area, scatter, pie, histogram, box, heatmap
│   ├── hierarchy-network-patterns.md # Treemap, sunburst, force, Sankey, chord, dendrogram
│   ├── geographic-patterns.md        # Choropleth, projections, GeoJSON/TopoJSON
│   ├── animation-interaction.md      # Transitions, zoom, brush, drag, tooltips, responsive
│   └── d3-api-quick-reference.md     # D3 v7 module-by-module API reference
├── examples/
│   ├── standalone.html               # Self-contained HTML bar chart
│   ├── separate-js/                  # Modular HTML + JS line chart
│   └── react-component.tsx           # React + TypeScript scatter plot
└── templates/
    ├── boilerplate.html              # Quick-start HTML template
    └── gallery/                      # 173 template configs from Observable D3 Gallery
        ├── index.json                # Master index and schema
        ├── animation.json            # 23 animated visualizations
        ├── interaction.json          # 9 interactive patterns
        ├── analysis.json             # 14 analytical charts
        ├── hierarchies.json          # 14 hierarchy layouts
        ├── networks.json             # 11 network diagrams
        ├── bars.json                 # 14 bar chart variants
        ├── lines.json                # 15 line chart types
        ├── areas.json                # 11 area chart types
        ├── dots.json                 # 11 dot/scatter types
        ├── radial.json               # 5 radial charts
        ├── annotation.json           # 8 annotation techniques
        ├── maps.json                 # 22 geographic visualizations
        ├── essays.json               # 4 explanatory visualizations
        └── fun.json                  # 12 creative/artistic visualizations
```
