---
name: d3js
description: This skill should be used when the user asks to "create a D3 visualization", "make a D3 chart", "build a d3js graph", "create a bar chart with D3", "make a scatter plot", "build a treemap", "create a force-directed graph", "make a choropleth map", "create a Sankey diagram", "build a sunburst chart", "make a line chart", "create a histogram", "build a heatmap", or mentions D3.js, d3js, data visualization with D3, or any specific chart type. Covers D3.js v7 with three output formats and optional creative/artistic mode.
version: 0.1.0
---

Create any D3.js data visualization quickly and correctly using D3 v7. This skill supports two workflows: direct implementation (default) for fast, professional output, and creative mode for artistic, philosophy-driven visualizations. Three output formats are available: standalone HTML, HTML + separate JS, and React components.

## Default Configuration

These defaults apply to every visualization unless the user explicitly overrides them. The assumption is that the user will PDF, screenshot, or otherwise export the result for insertion into another document.

### Layout: Single Screen, No Scrolling

Every visualization MUST fit entirely within a single browser viewport (100vh) with no scrolling required. This is non-negotiable.

Implementation rules:
- Set `html, body { height: 100vh; overflow: hidden; }` on standalone HTML output
- Use `body { display: flex; flex-direction: column; }` with `flex: 1` on the chart container to fill available space
- Use compact padding (`0.5rem–0.75rem`), gaps (`0.5rem`), and font sizes
- SVGs fill their containers via CSS (`width: 100%; height: 100%`) rather than fixed pixel dimensions
- Titles and labels use small but readable sizes (0.7–0.85rem for titles, 10–11px for axis text)
- When multiple charts share a page (dashboards), use CSS Grid with fractional rows (`1.2fr 1fr`) and `min-height: 0` on flex children to prevent overflow

### Sizing: Responsive viewBox, Not Fixed Pixels

- Always use `viewBox` on SVGs — never set fixed `width`/`height` attributes
- Do not set inline `style("height", "auto")` on SVGs — let CSS control sizing
- Set `preserveAspectRatio="xMidYMid meet"` on charts that need to maintain proportions (donut, pie, radial layouts)

### Visual Style: Clean and Professional

- **Color palette**: Muted, purposeful colors from `d3.schemeTableau10` or curated palettes. No rainbow, no random RGB.
- **Typography**: System font stack (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`). No external font loads.
- **Background**: Light gray page (`#f0f2f5`), white chart panels with subtle box shadow
- **Axes**: Light gray gridlines (`#f3f4f6`), gray tick labels (`#6b7280`), no heavy borders
- **Margins**: Generous enough for labels but not wasteful. Verify long labels (like "Natural Gas") are not truncated.

### Data: Always Working

- When no data is provided, generate realistic inline mock data — the visualization must render immediately with no placeholders
- Use seeded or deterministic data when reproducibility matters

### Export-Friendly

- White/light backgrounds (no dark themes) for clean PDF/image export
- Avoid relying on hover-only information for understanding the chart — labels and values should be visible by default where space permits
- Avoid animations that obscure the final state — if animating, ensure the end state is the complete visualization

## Workflow Selection

**Direct mode** (default): Proceed to the discovery interview, then implement.

**Creative mode**: Activate when the user says "artistic", "creative", "manifesto", or "generative". Run the discovery interview, then follow the full Design Philosophy Creation process before implementing.

---

## Discovery Interview (REQUIRED)

Before writing any code, use the AskUserQuestion tool to interview the user. This step is mandatory — never skip it, even if the initial request seems detailed.

Run the interview in **three rounds** to avoid overwhelming the user.

### Round 1: Purpose & Data

Ask these questions using AskUserQuestion (all four in a single call):

1. **"What is the goal of this visualization?"** (header: "Goal")
   - Options: "Explain a trend", "Compare categories", "Show relationships/connections", "Show geographic distribution", + Other
   - This determines chart type recommendations

2. **"Who is the audience?"** (header: "Audience")
   - Options: "Executive / leadership", "Technical team", "General public / blog", "Personal / exploratory"
   - This determines complexity level, labeling density, and terminology

3. **"Do you have a dataset, or should I generate sample data?"** (header: "Data")
   - Options: "I have a file (CSV, JSON, etc.)", "I have data I'll paste in", "Generate realistic sample data"
   - If they have a file, ask for the path in a follow-up

4. **"What output format do you need?"** (header: "Format")
   - Options: "Standalone HTML (Recommended)", "HTML + separate JS files", "React component"

### Round 2: Style & Specifics

After the user answers Round 1, ask these questions using AskUserQuestion:

1. **"Do you have brand colors or a specific color scheme?"** (header: "Colors")
   - Options: "Use clean defaults (Recommended)", "I have brand colors (I'll provide hex codes)", "Specific palette (e.g. blues, warm tones)", "Colorblind-safe palette"

2. **"What chart type do you have in mind?"** (header: "Chart type")
   - Tailor options based on the Round 1 "Goal" answer:
     - If "Explain a trend": "Line chart", "Area chart", "Stacked area", "Bar chart over time"
     - If "Compare categories": "Bar chart", "Grouped/stacked bar", "Dot plot", "Radar chart"
     - If "Show relationships": "Force-directed graph", "Sankey diagram", "Chord diagram", "Network/arc diagram"
     - If "Show geographic": "Choropleth map", "Bubble map", "Spike map", "Hex bin map"
     - Always include Other for custom requests

3. **"Any specific features you need?"** (header: "Features", multiSelect: true)
   - Options: "Tooltips on hover", "Animated transitions", "Interactive filtering/brush", "Print/export optimized (static labels, no hover-only info)"

4. **"Where should I save the output file(s)?"** (header: "Output path")
   - Options: "Current directory", "I'll specify a path"

### Round 3: Context & Polish

After Round 2, ask these final questions using AskUserQuestion:

1. **"What should the chart title/headline be?"** (header: "Title")
   - Options: "I'll provide a title", "Generate one from the data", "No title needed"

2. **"Where will this visualization be used?"** (header: "Destination")
   - Options: "Presentation slide", "Written report / document", "Blog post or webpage", "Standalone file / exploration"
   - This affects information density: slides need less text and larger elements; reports can be denser

3. **"What is the single key takeaway the viewer should get?"** (header: "Takeaway")
   - Options: "I'll describe it", "Let the data speak for itself"
   - If they describe it, use this to guide annotation placement, color emphasis, and subtitle text

4. **"Any specific data points, events, or benchmarks to highlight?"** (header: "Annotations")
   - Options: "No annotations needed", "Yes, I'll describe what to call out"
   - Examples: "Q3 2023 was a turning point", "Target line at $50M", "Highlight top 3 categories"

### After the Interview

Summarize the gathered requirements back to the user in a brief confirmation before starting implementation. Example:

> Building a **stacked area chart** showing revenue trends over time, for an **executive audience**. Using **your CSV at ./data/revenue.csv**. Brand colors: **#1a3a5c, #e07b39, #2d8659**. Standalone HTML saved to **./charts/revenue-trend.html**. Features: tooltips, animated load, print-optimized.

Then proceed to implementation.

## Implementation Workflow

With interview answers in hand, follow these steps:

### 1. Choose Output Format

**Standalone HTML** (default): Single self-contained `.html` file with D3 v7 loaded via CDN. Opens directly in any browser.

**HTML + separate JS**: An `index.html` file and a `chart.js` module. Cleaner code organization for larger visualizations. Requires a local server (`python -m http.server`) due to ES module imports.

**React component**: A `.tsx` component using `useRef` and `useEffect` to integrate D3 with React. For projects already using React.

Refer to `examples/` for working templates of each format.

### 2. Implement the Visualization

Apply any user-specified brand colors, audience-appropriate labeling, and data source from the interview. If the user provided brand hex codes, use those instead of the default palette.

**Always use D3 v7** via ES module CDN:
```html
<script type="module">
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
</script>
```

**Follow the default visual style** — clean and professional (NYT/FT-inspired):
- Muted, purposeful color palettes (avoid rainbow or random colors)
- Clean axes with readable tick labels and axis titles
- Good typography: system font stack or a clean sans-serif
- Adequate margins: `{top: 40, right: 30, bottom: 50, left: 60}` as a starting point
- Subtle gridlines if they aid readability
- Tooltips for data point details
- Responsive SVG using `viewBox`

**Sample data**: When the user has no data, generate realistic inline mock data so the visualization works immediately. Use `d3.range()`, arrays of objects, or embedded JSON. Never leave data as a placeholder.

### 3. Code Structure

Every D3 visualization follows this pattern:

```javascript
// 1. Dimensions and margins
const margin = {top: 40, right: 30, bottom: 50, left: 60};
const width = 800 - margin.left - margin.right;
const height = 500 - margin.top - margin.bottom;

// 2. Create SVG container
const svg = d3.select("#chart")
  .append("svg")
  .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
  .append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);

// 3. Scales
// 4. Axes
// 5. Data binding and rendering
// 6. Labels, legends, tooltips
// 7. Transitions and interactivity
```

### 4. Loading External Data

When the user provides a data file, use D3's fetch utilities inside the `<script type="module">` block:

```javascript
// CSV → array of objects (values are strings by default — coerce numbers)
const data = await d3.csv("data.csv", d => ({
  category: d.category,
  value: +d.value,        // coerce to number
  date: new Date(d.date)  // parse dates
}));

// JSON → parsed object/array
const data = await d3.json("data.json");

// TSV
const data = await d3.tsv("data.tsv", d3.autoType);
```

**Important:** Loading external files via `d3.csv()` / `d3.json()` requires HTTP — it will fail when opening the HTML directly from the filesystem (`file://` protocol) due to CORS restrictions. Tell the user to serve the file locally:

```bash
python -m http.server 8000
# then open http://localhost:8000/chart.html
```

For standalone HTML that must open without a server, embed data inline as a JavaScript array instead of loading from a file.

### 5. Chart-Type Specific Patterns

For detailed patterns organized by chart type, consult the reference files:
- **`references/chart-patterns.md`** — Bar, line, area, scatter, pie/donut, histogram, box plot, ridgeline, heatmap
- **`references/hierarchy-network-patterns.md`** — Treemap, sunburst, circle packing, force-directed graph, Sankey, chord diagram, dendrogram
- **`references/geographic-patterns.md`** — Choropleth, world/state maps, projections, GeoJSON/TopoJSON handling
- **`references/animation-interaction.md`** — Transitions, zoom, brush, drag, tooltips, responsive resize

### 6. Quality Checklist

Before delivering any visualization, verify:
- [ ] Axes have readable labels and titles
- [ ] Color palette is purposeful and accessible (colorblind-safe when possible)
- [ ] Tooltips show relevant data on hover
- [ ] SVG uses `viewBox` for responsive sizing
- [ ] Margins provide breathing room for labels
- [ ] Legend present when multiple series/categories exist
- [ ] Sample data is realistic if user provided none
- [ ] Code is clean, well-commented, and idiomatic D3 v7
- [ ] SVG has `role="img"` and `aria-label` describing the visualization
- [ ] SVG contains a `<title>` element for screen readers
- [ ] Color palette is distinguishable for colorblind viewers (`d3.schemeTableau10` is a safe default; for maximum accessibility use Okabe-Ito or `d3.schemeObservable10`)

### 7. Common Pitfalls

**Null / missing data:** Always filter or coerce before binding to scales. Null values cause NaN in scale output, which renders invisible or broken elements.
```javascript
const clean = data.filter(d => d.value != null && !isNaN(d.value));
```

**CDN availability:** The default CDN (`cdn.jsdelivr.net`) is reliable but not infallible. If building for offline or restricted environments, note this in the output and suggest downloading D3 locally:
```html
<!-- Fallback: download d3.min.js and serve locally -->
<script type="module">
import * as d3 from "./d3.min.js";
</script>
```

**Overflowing 100vh:** When content exceeds the viewport despite the single-screen constraint:
1. Reduce margins (`top: 20, bottom: 30` instead of 40/50)
2. Use smaller font sizes (10px axis labels, 0.7rem titles)
3. For dashboards with many panels, use CSS Grid `minmax(0, 1fr)` to let panels shrink
4. If the data truly requires more space (50+ bar categories), acknowledge the override and switch to scrollable layout with a comment explaining why

**Date parsing:** D3 v7's `d3.csv()` returns all values as strings. Always parse dates explicitly:
```javascript
const parseDate = d3.timeParse("%Y-%m-%d");
const data = await d3.csv("data.csv", d => ({ ...d, date: parseDate(d.date) }));
```

---

## Creative Mode Workflow

When the user requests artistic or creative visualization, follow this two-phase process inspired by generative art practices.

### Phase 1: Data Visualization Philosophy Creation

Create a DATA VISUALIZATION PHILOSOPHY — an aesthetic movement for how data should be expressed visually through D3.js. Output as a `.md` file.

**Name the movement** (1-2 words): "Luminous Data" / "Structural Narratives" / "Chromatic Flows"

**Articulate the philosophy** (4-6 paragraphs) expressing how data manifests through:
- Form, geometry, and spatial encoding
- Color systems and chromatic meaning
- Motion, transition, and temporal storytelling
- Scale relationships and visual hierarchy
- Interactivity as dialogue between viewer and data

**Critical guidelines:**
- **Emphasize craftsmanship repeatedly**: The philosophy MUST stress that the final visualization should appear meticulously crafted, refined through countless iterations by a master of data aesthetics. Repeat phrases like "painstaking attention to detail," "the product of deep visual expertise."
- **Leave creative space**: Be specific about the aesthetic direction but concise enough to allow interpretive implementation choices at an extremely high level of craftsmanship.
- **Data as material**: Unlike pure generative art, data visualization philosophy treats data as the raw material — the algorithm serves the data's story, not the other way around.

**Philosophy examples:**

**"Luminous Data"**: Data as light — values encoded as luminance, density as glow, relationships as light interference. Visualization emerges from darkness, data points illuminating structure. Transitions are dawn and dusk. Interaction reveals hidden constellations. The result of painstaking calibration where every opacity and blend mode was refined by a master.

**"Structural Narratives"**: Data as architecture — values become load-bearing beams, categories are floors, time is the corridor. Visualization reads like a building section drawing. Precise, technical, yet deeply human. Every line weight chosen with architectural rigor.

### Phase 2: Express Through D3.js

With the philosophy established, implement the visualization using D3.js, letting the philosophy guide every design decision — scales, color choices, transition easing, layout algorithm, interaction model. Follow all technical requirements from the Implementation Workflow above, but let the philosophy override default style choices.

---

## D3 API Quick Reference

For a comprehensive module-by-module reference of D3 v7 APIs, consult **`references/d3-api-quick-reference.md`**. Key modules:

| Module | Purpose |
|--------|---------|
| d3-selection | DOM manipulation, data joins |
| d3-scale | Map data to visual values (linear, band, ordinal, time, log) |
| d3-axis | Generate axes from scales |
| d3-shape | Lines, areas, arcs, pies, curves, symbols |
| d3-hierarchy | Treemaps, trees, pack, partition, stratify |
| d3-force | Force-directed layouts |
| d3-geo | Map projections and geographic paths |
| d3-transition | Animated transitions |
| d3-zoom | Pan and zoom behavior |
| d3-brush | Rectangular selection |
| d3-fetch | Load CSV, JSON, TSV data |
| d3-scale-chromatic | Color schemes (categorical, sequential, diverging) |

---

## Resources

### Reference Files

Consult these for detailed, chart-specific implementation patterns:
- **`references/chart-patterns.md`** — Standard chart types (bar, line, area, scatter, pie, histogram, box plot, heatmap, ridgeline)
- **`references/hierarchy-network-patterns.md`** — Hierarchical and network visualizations (treemap, sunburst, circle packing, force-directed, Sankey, chord, dendrogram)
- **`references/geographic-patterns.md`** — Geographic visualizations (choropleth, projections, TopoJSON, GeoJSON)
- **`references/animation-interaction.md`** — Transitions, zoom, brush, drag, tooltips, responsive design
- **`references/d3-api-quick-reference.md`** — D3 v7 module-by-module API reference

### Example Files

Working templates for each output format in `examples/`:
- **`examples/standalone.html`** — Self-contained HTML with inline D3 bar chart
- **`examples/separate-js/index.html`** + **`examples/separate-js/chart.js`** — Modular HTML + JS approach
- **`examples/react-component.tsx`** — React component with D3 integration

> **Note:** Example files use a scrollable layout with padding for readability as teaching samples. Production output should follow the `templates/boilerplate.html` pattern (100vh, `overflow: hidden`, flex layout) per the Default Configuration above.

### Template Files

- **`templates/boilerplate.html`** — Minimal HTML boilerplate with D3 v7 CDN, responsive SVG, and standard margin convention. Use as a starting point for standalone HTML visualizations.

### Demo

- **`../../demo.html`** — Complete multi-chart interactive dashboard (energy production) demonstrating linked brush filtering, animated transitions, interactive legend toggle, and donut arc tweens in a single 100vh viewport.

### Gallery Templates

The `templates/gallery/` directory contains **174 template configurations** based on the [Observable D3 Gallery](https://observablehq.com/@d3/gallery), organized by category. Each config specifies the chart type, D3 modules, data shape, scales, key patterns, and implementation notes needed to reproduce that visualization.

- **`templates/gallery/index.json`** — Master index of all categories and schema
- **`templates/gallery/animation.json`** — 23 animated visualizations (bar chart race, animated treemap, zoomable sunburst, etc.)
- **`templates/gallery/interaction.json`** — 9 interactive patterns (brushable scatterplot, pannable chart, versor dragging, etc.)
- **`templates/gallery/analysis.json`** — 14 analytical charts (histogram, box plot, KDE, hexbin, contours, etc.)
- **`templates/gallery/hierarchies.json`** — 14 hierarchy layouts (treemap, circle packing, sunburst, icicle, dendrogram, etc.)
- **`templates/gallery/networks.json`** — 11 network diagrams (force-directed, Sankey, chord, arc diagram, edge bundling, etc.)
- **`templates/gallery/bars.json`** — 14 bar chart variants (stacked, grouped, diverging, Marimekko, calendar, etc.)
- **`templates/gallery/lines.json`** — 15 line chart types (multi-line, candlestick, parallel coordinates, slope chart, etc.)
- **`templates/gallery/areas.json`** — 11 area chart types (stacked, streamgraph, ridgeline, horizon, difference, etc.)
- **`templates/gallery/dots.json`** — 11 dot/scatter types (scatterplot, beeswarm, bubble map, spike map, SPLOM, etc.)
- **`templates/gallery/radial.json`** — 6 radial charts (pie, donut, radial area, radial stacked bar, radar/spider)
- **`templates/gallery/annotation.json`** — 8 annotation techniques (tooltips, inline labels, Voronoi labels, styled axes, etc.)
- **`templates/gallery/maps.json`** — 22 geographic visualizations (choropleth, projections, tiles, vector fields, star map, etc.)
- **`templates/gallery/essays.json`** — 4 explanatory/educational visualizations
- **`templates/gallery/fun.json`** — 12 creative/artistic visualizations (polar clock, word cloud, Voronoi stippling, etc.)

When a user requests a specific chart type, consult the relevant gallery config to get the exact D3 modules, scale types, data shape, and key implementation patterns needed.
