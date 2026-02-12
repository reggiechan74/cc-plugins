---
description: Convert a markdown research report into an interactive React presentation website
argument-hint: <path-to-report.md>
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "AskUserQuestion", "Task"]
---

# Generate Interactive Presentation Website from Research Report

Convert a markdown research report into a fully interactive, dark-themed React presentation website with Tailwind CSS + shadcn/ui, optimized for GitHub Pages hosting.

## Workflow

### Step 1: Validate Input

Read the provided markdown report file path. If no path was provided in the arguments, ask the user:
- "What is the path to your research report (.md file)?"

Verify the file exists and is a markdown file. Read its full contents.

### Step 2: Ask User Preferences

Use AskUserQuestion to ask three questions:

1. **Output directory**: "Where should I create the React project?" with options:
   - A sensible default based on the report filename (e.g., `./report-name-site/`)
   - Next to the report file
   - Custom path

2. **Interactivity level**: "What level of interactivity do you want?" with options:
   - **Presentation-focused**: Animated scroll-based presentation with data visualizations, smooth transitions between tabs, auto-playing highlights. Minimal user input required.
   - **Full interactive**: Calculators for formulas, what-if scenario sliders, interactive comparison tables, expandable case law cards, searchable knowledge vault. Maximum user engagement.
   - **Both**: Full interactive components PLUS presentation mode toggle that auto-advances through content with animations.

3. **Visual style**: "Which visual style?" with options:
   - **Dark Professional** (default) — Refined gold/teal/indigo accents on deep space backgrounds. Bloomberg Terminal meets The Economist.
   - **shadcn Blue** — Cool blue + cyan accents. Clean, corporate, trustworthy feel.
   - **shadcn Green** — Fresh green + teal accents. Natural, growth-oriented energy.
   - **shadcn Orange** — Warm orange + amber accents. Bold, energetic, attention-grabbing.
   - **shadcn Red** — Strong red + orange accents. Urgent, powerful, high-contrast.
   - **shadcn Rose** — Elegant rose + pink accents. Soft warmth with modern sophistication.
   - **shadcn Violet** — Rich violet + indigo accents. Creative, premium, distinctive.
   - **shadcn Yellow** — Vibrant yellow + amber accents. Optimistic, high-visibility, editorial.
   - **Community Registry** — Browse the shadcn themes gallery at https://ui.shadcn.com/themes and the community registry directory at https://ui.shadcn.com/registry to find a style you like (e.g., `@neobrutalism`, `@retroui`, `@magicui`, `@animata`). Provide the registry name when prompted.

### Step 3: Analyze the Report

Parse the markdown report to identify:

1. **Structure**: Headings hierarchy (H1 = title, H2 = major tabs, H3 = sub-sections)
2. **Interactive candidates**: Look for these patterns:
   - **Formulas/calculations**: Lines with `=`, mathematical expressions, "calculated as", "formula" — these become Calculator components
   - **Comparison tables**: Tables with 3+ columns comparing items — these become ComparisonTable components
   - **Timelines**: Chronological data, dates, "timeline", status progressions — these become TimelineView components
   - **Citations/references**: Footnotes `[^N]`, endnotes, URLs, case law references — these become CitationCard components
   - **Data tables**: Any markdown table with numerical data — these can become interactive charts
   - **Explicit markers**: Look for `<!-- interactive: calculator|timeline|scenario|comparison -->` HTML comments

3. **Metadata**: Title, date, author, executive summary
4. **External links**: All URLs, especially legislation, court cases, official sources
5. **Knowledge vault content**: The full report body for the searchable reference section

### Step 4: Scaffold the Vite + React Project

Create the project using the bundled templates from `${CLAUDE_PLUGIN_ROOT}/templates/`:

1. Copy the base project files (package.json, vite.config.js, index.html, postcss.config.js, jsconfig.json, components.json)
2. Copy the component library from `${CLAUDE_PLUGIN_ROOT}/templates/src/components/`
3. Copy `${CLAUDE_PLUGIN_ROOT}/templates/src/app.css` and `${CLAUDE_PLUGIN_ROOT}/templates/src/theme/motion.js`
4. Copy `${CLAUDE_PLUGIN_ROOT}/templates/src/lib/utils.js`
5. Update `vite.config.js` with the correct `base` path for GitHub Pages (e.g., `/<repo-name>/`)

### Step 4b: Install UI Components and Apply Theme

After scaffolding, install shadcn UI components and apply the selected visual style:

**Install shadcn components:**

For default or built-in presets:
```bash
cd <output-dir>
npx shadcn@latest add card input label table badge accordion collapsible slider button separator
```

For community registries (e.g., `@neobrutalism`):
```bash
cd <output-dir>
npx shadcn@latest add @neobrutalism/card @neobrutalism/input @neobrutalism/label @neobrutalism/table @neobrutalism/badge @neobrutalism/accordion @neobrutalism/collapsible @neobrutalism/slider @neobrutalism/button @neobrutalism/separator
```

If a community registry doesn't have a needed component, fall back to the default shadcn version for that component.

**Apply theme preset:**

- **Dark Professional**: Import `${CLAUDE_PLUGIN_ROOT}/templates/src/themes/dark-professional.css` after app.css in main.jsx (no-op — default tokens already in app.css)
- **Built-in color presets**: Copy the appropriate theme file from `${CLAUDE_PLUGIN_ROOT}/templates/src/themes/<color>.css` to `src/themes/<color>.css`, then import it after app.css in main.jsx
- **Community registries**: Use the registry's built-in styling — import dark-professional.css as a fallback

### Step 4c: Install Vercel Agent Skills

After installing components, add Vercel's agent skills for React best practices:

```bash
cd <output-dir>
npx -y skills add vercel-labs/agent-skills --skill react-best-practices --skill web-design-guidelines --skill composition-patterns -y
```

This installs three skill sets that guide code generation:
- **react-best-practices**: 40+ React/Next.js optimization rules from Vercel Engineering
- **web-design-guidelines**: 100+ accessibility, performance, and UX best practice rules
- **composition-patterns**: React compound components, state lifting, and internal composition patterns

Read the installed SKILL.md files (typically in `.claude/skills/` or `.skills/`) and apply their guidelines when generating React components in the subsequent steps. Specifically:
- Follow React rendering optimization patterns (memoization, key stability, etc.)
- Apply accessibility rules from web-design-guidelines to all interactive components
- Use composition patterns for complex components like TabbedLayout and KnowledgeVault

### Step 5: Generate Content-Specific Files

Based on the report analysis, create:

1. **`src/data/reportData.js`** — Parsed report content structured as:
   ```js
   export const reportData = {
     meta: { title, date, author, query },
     tabs: [
       { id, label, sections: [{ heading, content, interactive: [] }] }
     ],
     citations: [...],
     externalLinks: [...]
   }
   ```

2. **`src/data/interactiveConfig.js`** — Configuration for interactive elements:
   ```js
   export const interactives = [
     { type: 'calculator', tabId, config: { formula, inputs, labels } },
     { type: 'comparison', tabId, config: { headers, rows, highlights } },
     { type: 'timeline', tabId, config: { events } },
     { type: 'scenario', tabId, config: { variables, formula, description } }
   ]
   ```

3. **`src/App.jsx`** — Wire up TabbedLayout with the report data, importing all needed components

4. **`src/pages/`** — One component per tab, composing the bundled components with report data

### Step 6: Build and Verify

Run these commands in sequence:
```bash
cd <output-dir>
npm install
npm run build
```

If build succeeds, inform the user the site is ready. If it fails, fix the errors.

### Step 7: Provide Deployment Instructions

Tell the user:

1. **Local preview**: `cd <output-dir> && npm run dev`
2. **GitHub Pages deployment**:
   - Push to a GitHub repo
   - In repo Settings > Pages, set source to "GitHub Actions"
   - The included `.github/workflows/deploy.yml` handles the rest
   - Or use `gh-pages` branch: `npm run deploy`

## Important Guidelines

- Use the `frontend-design` skill for design decisions — the site MUST use the selected theme from the Tailwind + shadcn design system
- Every tab should have meaningful content — never leave placeholder text
- All external links must open in new tabs (`target="_blank" rel="noopener"`)
- The Knowledge Vault tab should contain the full report text, searchable
- Ensure the site is fully responsive (mobile, tablet, desktop)
- Use Tailwind utility classes for all styling — no inline `style={}` objects for layout/color/spacing
- Include proper `<title>` and meta tags from report metadata
- Components import from `@/components/ui/...` — these resolve after `npx shadcn add` runs
- Import `cn` from `@/lib/utils` for conditional class merging
- Import framer-motion tokens from `../theme/motion` (not `tokens.js`)
