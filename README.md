# Reggie Chan's Claude Code Plugins

<!-- badges-start -->
[![Plugins](https://img.shields.io/badge/plugins-13-blue)](https://github.com/reggiechan74/cc-plugins)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-marketplace-blueviolet)](https://claude.ai/claude-code)
[![GitHub Stars](https://img.shields.io/github/stars/reggiechan74/cc-plugins?style=flat&color=yellow)](https://github.com/reggiechan74/cc-plugins/stargazers)
<!-- badges-end -->

A marketplace of Claude Code plugins for enhanced development workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add reggiechan74/cc-plugins
```

## Available Plugins

### code-coherence

Multi-agent verification system implementing organizational intelligence for production-grade code reliability. Achieves 92%+ accuracy through team-of-rivals architecture with specialized critic agents.

**Install:**
```bash
/plugin install code-coherence@cc-plugins
```

**Features:**
- Multi-layer verification with independent critics implementing the Swiss cheese model
- Specialized critic agents: planner, code-critic, security-critic, domain-critic
- Domain specializations: financial, healthcare, legal
- Per-project configuration with `.claude/code-coherence.local.md`
- Hierarchical veto authority -- any critic can reject

**Commands:**
- `/coherence-check` - Full multi-agent verification workflow
- `/plan-review` - Review execution plans with acceptance criteria
- `/audit-trail` - Bidirectional decision history with search
- `/acceptance-criteria` - Define and enforce success criteria
- `/swiss-cheese-validation` - Multi-layer error checking with independence verification

---

### course-curriculum-creator

Create professional course curricula for 1-2 day workshops using backward design methodology and Bloom's taxonomy.

**Install:**
```bash
/plugin install course-curriculum-creator@cc-plugins
```

**Features:**
- Backward Design Framework with Bloom's Taxonomy integration
- Rapid course creation: autonomous or step-by-step
- Template system: save and reuse course structures
- Universal Design for Learning (UDL) compliance
- Virtual/hybrid delivery adaptation
- Kirkpatrick L1-L4 evaluation planning
- Course series design (101/201/301/401) with Bloom's band enforcement

**Commands:**
- `/create-course` - Initialize new course project with directory structure
- `/assess-needs` - Conduct a training needs assessment
- `/generate-objectives` - Create Bloom's-aligned learning objectives
- `/generate-rubrics` - Create 1-5 scale analytical assessment rubrics
- `/generate-outline` - Generate module structure with timing
- `/generate-lesson-plans` - Generate detailed module-level lesson plans
- `/generate-description` - Create student-facing course description
- `/generate-artifacts` - Generate student handouts, instructor guides, etc.
- `/generate-evaluation-plan` - Kirkpatrick L1-L4 evaluation plan
- `/generate-transfer-plan` - Post-workshop transfer plan
- `/generate-workshop-prep` - Dated preparation checklist for delivery
- `/process-workshop-feedback` - Analyze feedback and generate improvement report
- `/adapt-for-virtual` - Adapt curriculum for virtual or hybrid delivery
- `/generate-review-package` - Stakeholder/SME review package
- `/review-curriculum` - Validate curriculum quality and alignment
- `/export-curriculum` - Export as combined document
- `/design-series` - Design a leveled course series
- `/save-as-template` - Save course structure as reusable template
- `/create-from-template` - Create new course from existing template
- `/list-templates` - List available course templates

---

### d3-visualizations

D3.js visualization skill for quickly creating any kind of data visualization.

**Install:**
```bash
/plugin install d3-visualizations@cc-plugins
```

**Features:**
- All D3 chart types: bar, line, area, scatter, pie, histogram, treemap, sunburst, force-directed, Sankey, chord, choropleth, and more
- 173 gallery templates covering every example from the Observable D3 Gallery
- Three output formats: standalone HTML, HTML + separate JS, React components
- Two workflows: direct implementation (fast) and creative mode (design philosophy + implementation)
- Discovery interview: 3-round, 12-question process to understand requirements before building
- Clean professional style: NYT/FT-inspired defaults with muted colors, clean axes, good typography

---

### google-workspace-mcp

Gmail, Google Calendar, and Google Contacts MCP servers for Claude Code. Features OAuth auto-refresh, retry with backoff, read-only tool annotations, and optimized API batching.

**Install:**
```bash
/plugin install google-workspace-mcp@cc-plugins
```

**Features:**
- 22 Gmail tools: send, draft, read, search, modify, delete emails; label management; filters; attachments; threads; contact lookup
- 7 Google Calendar tools: list calendars, create/get/update/delete events, multi-calendar parallel queries
- OAuth auto-refresh with token persistence
- Retry with exponential backoff for transient failures
- In-memory caching with syncToken revalidation

**Commands:**
- `/authenticate` - Run OAuth flow for Gmail and Calendar servers

---

### kids-camp-planner

Plan and book kids' summer camps, March break programs, and PA day coverage with budget tracking, schedule optimization, and provider research for Ontario families.

**Install:**
```bash
/plugin install kids-camp-planner@cc-plugins
```

**Features:**
- Day-by-day scheduling as the primary unit with weekly summaries derived automatically
- Full-year coverage: summer, PA days, winter break, March break in one annual view
- Provider research with structured comparison files (daily and weekly rates)
- Budget tracking with discount optimization and tax recovery estimates
- Private school support: handle calendar mismatches with public board schedules
- Email drafting: inquiry, registration, waitlist, special needs, and cancellation emails
- Pre-saved calendars for 12+ Ontario public school boards plus private schools
- Commute matrix with Geoapify API integration

---

### mississauga-permits

Query Mississauga building permit data by address with filtering and summary stats.

**Install:**
```bash
/plugin install mississauga-permits@cc-plugins
```

**Features:**
- 20 municipal datasets: building permits, parcels, land use, transit, infrastructure, and more
- Text search with partial matching and address normalization
- Spatial queries by latitude/longitude
- Auto-discovered field metadata from ArcGIS FeatureServer
- Zero external dependencies (Python stdlib only)
- JSON output with summary statistics

**Commands:**
- `/fetch-permits <address>` - Building permit lookup with rich filtering (type, scope, ward, date range, construction value)
- `/fetch-mississauga [options]` - General-purpose query for any of 20 City of Mississauga datasets

---

### math-paper-creator

Author validated math papers interactively. Formalize concepts into prose, LaTeX math, and executable Python validation — each section checked before the next begins.

**Install:**
```bash
/plugin install math-paper-creator@cc-plugins
```

**Features:**
- Incremental section-by-section authoring with live validation
- Symbol registry: sets, parameters, variables, expressions, constraints, objectives
- Phantom detection, collision checking, index validation, cycle detection, unit boundaries
- Constraint satisfaction and objective evaluation against fixture data
- Compile to clean paper, standalone runner.py, and validation report
- Onboarding workflow for existing papers without validation

**Commands:**
- `/math-paper-creator:author [file]` - Author a new paper interactively with section-by-section validation
- `/math-paper-creator:onboard <file>` - Convert an existing paper by adding validation blocks
- `/math-paper-creator:check <file>` - Run validation pipeline against a .model.md document
- `/math-paper-creator:status <file>` - Show symbol table, coverage, and orphan/phantom status
- `/math-paper-creator:report <file>` - Generate full validation report
- `/math-paper-creator:paper <file>` - Generate clean paper artifact (strips validation blocks)
- `/math-paper-creator:compile <file>` - Produce all artifacts: clean paper, standalone runner, validation report

---

### nano-banana

AI image generation and presentation deck creation via Gemini API. 25 style presets, batch deck generation, and report-to-slides decomposition.

**Install:**
```bash
/plugin install nano-banana@cc-plugins
```

**Features:**
- 25 style presets across 6 categories: Technical, Business, Creative, UI/UX, Photography, Specialized
- Image editing with up to 14 reference images per call
- Batch deck generation from JSON specifications with resume support
- 5 presentation presets: consulting, workshop, pitch, creative, notebooklm
- Structured prompt schema with template assembly for presentation-quality slides
- Report-to-slides decomposition -- convert markdown/PDF reports into presentation decks
- Version-safe output -- never overwrites existing files

**Commands:**
- `/deck-prompt <path>` - Decompose reports into deck specification JSON

---

### report-to-web

Convert markdown research reports into interactive React presentation websites for GitHub Pages.

**Install:**
```bash
/plugin install report-to-web@cc-plugins
```

**Features:**
- Reusable generator for any structured markdown research report
- Tailwind CSS v4 + shadcn/ui with 8 built-in dark color themes
- Interactive elements: calculators, scenario sliders, comparison tables, timelines
- Knowledge vault with searchable full-text report content
- Dark professional theme with refined typography (DM Serif Display + IBM Plex Sans)
- GitHub Pages ready with included deploy workflow
- Auto-detects interactive opportunities from report content

**Commands:**
- `/report-to-web:generate <path>` - Parse a markdown report and generate a complete React site

---

### resume-snapshot

Generate portfolio-ready repository snapshots for resume and job documentation.

**Install:**
```bash
/plugin install resume-snapshot@cc-plugins
```

**Features:**
- Automated git metadata collection: commits, contributors, timeline, tags
- File statistics and lines-of-code analysis by language
- Infrastructure and tooling detection (CI/CD, Docker, linting, tests)
- Complexity hotspot detection and evolution analysis
- Import/dependency mapping with ASCII architecture diagrams
- Code quality evidence: test ratios, type safety, error handling patterns
- Professional portfolio-entry synthesis with technical architecture, skills, and business impact

**Commands:**
- `/resume-snapshot` - Generate a portfolio-quality markdown summary of the current repository
- `/resume-snapshot --output FILE` - Write snapshot to a custom file path

---

### rubric-creator

Professional-grade rubric creation skill with validity, reliability, and fairness controls for Claude Code.

**Install:**
```bash
/plugin install rubric-creator@cc-plugins
```

**Features:**
- Three creation modes: Interactive, Template, and Example-Based
- 7 pre-built domain templates (regulatory-compliance, document-quality, code-review, vendor-evaluation, risk-assessment, performance-review, research-quality)
- Anchor examples for every score level
- Critical barrier definitions with thresholds
- Inter-rater reliability protocol
- Bias review checklist and maintenance lifecycle schedule
- Optional companion materials: pilot testing worksheet and scorer calibration pack

**Commands:**
- `/rubric-creator --interactive` - Guided 6-phase questionnaire with validity/alignment foundation
- `/rubric-creator --template [domain]` - Generate from pre-built domain templates
- `/rubric-creator --from-example [file]` - Analyze existing rubric and create variant
- `/rubric-creator --with-pilot` - Generate pilot testing worksheet
- `/rubric-creator --with-calibration` - Generate scorer calibration pack

---

### spinnerverbs

Generate and apply themed spinner verbs for Claude Code status messages. Includes pre-built themes (Star Trek, Game of Thrones, Mandalorian) with optional humor and cynic modifiers.

**Install:**
```bash
/plugin install spinnerverbs@cc-plugins
```

**Features:**
- Pre-built themes: Star Trek, Game of Thrones, Mandalorian
- Custom theme generation from any description
- Style modifiers: `--parody` (Claude Code / AI / LLM references) and `--cynic` (pessimistic / world-weary twist)
- Flexible scoping: Apply to current project, user-level, or local directory

**Commands:**
- `/spinnerverbs:create [theme]` - Generate new themed spinner verbs from a description
- `/spinnerverbs:apply [template-name]` - Apply a pre-built theme template (startrek, gameofthrones, mandalorian)

---

### structured-english

Dual-audience specification format -- HSF v5 (prose instructions optimized for LLM execution) and SESF v4.1 (formal BEHAVIOR/PROCEDURE/RULE/STEP blocks optimized for human readers). Both share @route decision tables, @config parameters, $variable threading, consolidated error tables, and 3-tier scaling.

**Install:**
```bash
/plugin install structured-english@cc-plugins
```

**Features:**
- Two formats: HSF v5 (LLM-facing prose) and SESF v4.1 (human-facing formal blocks)
- Decision tables: `@route` compact notation for 3+ branch conditional logic
- Centralized config: `@config` blocks for thresholds, feature flags, and environment settings
- Variable threading: `$variable` for explicit data flow between phases
- Consolidated error tables: All errors in one scannable table (Error | Severity | Action)
- 3-tier scaling: Micro (20-80 lines), Standard (80-200 lines), Complex (200-400 lines)
- Structural validator with auto-format detection
- Cross-format conversion: author in SESF, convert to HSF for LLM execution

**Commands:**
- `/write-LLM-spec <domain>` - Write an LLM-facing specification (HSF v5)
- `/assess-LLM-doc <path>` - Evaluate whether a document would benefit from HSF conversion
- `/update-LLM-spec <path>` - Update an existing HSF spec
- `/write-human-spec <domain>` - Write a human-facing specification (SESF v4.1)
- `/assess-human-doc <path>` - Evaluate whether a document would benefit from SESF conversion
- `/update-human-spec <path>` - Update an existing SESF spec
- `/convert-human-to-llm <path>` - Convert SESF spec to HSF for LLM execution
- `/assess-inferred-intent <path>` - Review a spec for ambiguity, contradiction, and inferred intent

---

## Usage

After adding the marketplace, you can browse and install plugins using:

```bash
/plugin
```

Or install directly by name as shown above.

## Contributing

Found an issue or have a suggestion? Please open an issue in the repository.

## License

Each plugin has its own license. See individual plugin directories for details.
