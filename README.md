# Reggie Chan's Claude Code Plugins

[![Plugins](https://img.shields.io/badge/plugins-12-blue)](https://github.com/reggiechan74/cc-plugins)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude_Code-marketplace-blueviolet)](https://claude.ai/claude-code)
[![GitHub Stars](https://img.shields.io/github/stars/reggiechan74/cc-plugins?style=flat&color=yellow)](https://github.com/reggiechan74/cc-plugins/stargazers)

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
- Automatic verification gates via PreToolUse and PostToolUse hooks
- Per-project configuration with `.claude/code-coherence.local.md`

**Skills:**
- `/coherence-check` - Full multi-agent verification workflow
- `/plan-review` - Review execution plans with acceptance criteria
- `/audit-trail` - Bidirectional decision history with search
- `/acceptance-criteria` - Define and enforce success criteria
- `/swiss-cheese-validation` - Multi-layer error checking with independence verification

**Agents:**
- **Planner** - Creates execution DAGs with pre-declared acceptance criteria
- **Code Critic** - Validates syntax, logic, performance, style, complexity
- **Security Critic** - OWASP Top 10, data exposure, timing attacks, supply chain
- **Domain Critic** - Business logic validation (financial, healthcare, legal specializations)

---

### course-curriculum-creator

Create professional course curricula for 1-2 day workshops using backward design methodology and Bloom's taxonomy.

**Install:**
```bash
/plugin install course-curriculum-creator@cc-plugins
```

**Features:**
- Backward Design Framework: Start with learning outcomes, design assessments, then plan activities
- Bloom's Taxonomy Integration: Create measurable learning objectives at appropriate cognitive levels
- Rapid Course Creation: Generate complete curricula autonomously or step-by-step
- Modular Architecture: Create courses optimized for 1-2 day weekend workshops
- Professional Outputs: Course descriptions, outlines, lesson plans, rubrics, student materials
- Template System: Save and reuse course structures for variants and iterations

**Commands:**
- `/create-course` - Initialize new course project with directory structure
- `/generate-description` - Create student-facing course description
- `/generate-outline` - Generate module structure with timing
- `/generate-objectives` - Create Bloom's-aligned learning objectives
- `/generate-lesson-plans` - Generate detailed module-level lesson plans
- `/generate-rubrics` - Create 1-5 scale analytical assessment rubrics
- `/generate-artifacts` - Generate student handouts, instructor guides, etc.
- `/save-as-template` - Save course structure as reusable template
- `/create-from-template` - Create new course from existing template
- `/review-curriculum` - Validate curriculum quality and alignment

**Agents:**
- **Curriculum Architect** - Autonomous agent that designs complete curricula from high-level requirements
- **Quality Reviewer** - Validates alignment between outcomes, assessments, and activities

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
- Single-screen layout: 100vh no-scroll default for easy PDF/screenshot export
- Sample data generation: visualizations work immediately out of the box

---

### google-workspace-mcp

Gmail, Google Calendar, and Google Contacts MCP servers for Claude Code.

**Install:**
```bash
/plugin install google-workspace-mcp@cc-plugins
```

**Features:**
- 22 Gmail tools: send, draft, read, search, modify, delete emails; label management; filters; attachments; threads; contact lookup
- 6 Google Calendar tools: list calendars, list/create/get/update/delete events
- OAuth 2.0 authentication with GCP credentials
- Works with Gmail, Google Calendar, and Google People APIs

**Commands:**
- `/authenticate` - Run OAuth flow for Gmail and Calendar servers

---

### install-private-plugin

Configure git auth for installing Claude Code plugins from private GitHub repos. Guides PAT creation, Codespace secret storage, and git URL rewriting when `/plugin marketplace add` fails with 403 or HTTPS auth errors.

**Install:**
```bash
/plugin install install-private-plugin@cc-plugins
```

**Features:**
- Step-by-step guide for creating fine-grained GitHub PATs with minimal permissions
- Codespace secret storage and container rebuild workflow
- Git URL rewriting to inject PAT credentials transparently
- Access verification before attempting plugin install
- Works with any git-based private repo (GitHub, GitLab, Bitbucket)

**Commands:**
- `/install-private-plugin` - Show full prerequisites guide for PAT and secret setup
- `/install-private-plugin <github-repo-url> <env-var-name>` - Configure git auth and verify access

---

### kids-camp-planner

Plan and book kids' summer camps, March break programs, and PA day coverage with budget tracking, schedule optimization, and provider research for Ontario families.

**Install:**
```bash
/plugin install kids-camp-planner@cc-plugins
```

**Features:**
- Schedule Planning: Build gap-free day-by-day coverage from last day of school through fall, including March break and PA days
- Provider Research: Systematically discover and document camp providers with structured comparison files
- Budget Tracking: Calculate costs across children, providers, and days/weeks with discount optimization and tax recovery estimates
- Private School Support: Handle calendar mismatches between private schools and public board PA day/break schedules
- Email Drafting: Generate inquiry, registration, waitlist, special needs, and cancellation emails
- Pre-Saved Calendars: Ships with 12+ Ontario public school board calendars (TDSB, TCDSB, PDSB, DDSB, HDSB, YRDSB, and more) plus private schools (GIST, KCS)

**Skills:**
- **Setup** - Initialize research folder and family profile
- **Camp Planning** - Ontario camp evaluation knowledge and quality indicators
- **Budget Optimization** - Cost calculation, discount optimization, tax recovery
- **Plan Summer** - Day-by-day summer coverage scheduling
- **Plan March Break** - March break planning (handles 2-week private school breaks)
- **Plan PA Days** - PA day lookup and single-day coverage
- **Research Camps** - Provider discovery and documentation
- **Draft Email** - Email composition for camp communications
- **Add School Calendar** - Import school calendar from URL/PDF into reference data
- **Generate Annual Schedule** - Consolidate all periods into one annual view with markdown + xlsx output
- **Commute Matrix** - Automated commute calculation using Geoapify API

**Agents:**
- **Camp Researcher** - Autonomous web research creating provider files with daily and weekly rates
- **Schedule Optimizer** - Builds and refines day-level schedules across constraints

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
- Report-to-slides decomposition — convert markdown/PDF reports into presentation decks
- Version-safe output — never overwrites existing files

**Skills:**
- `nano-banana` - Image generation and editing via Gemini API
- `/deck-prompt` - Decompose reports into deck specification JSON

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
- Dark professional theme with refined typography
- GitHub Pages ready with included deploy workflow

**Commands:**
- `/report-to-web:generate <path>` - Parse a markdown report and generate a complete React site

**Agents:**
- **Site Builder** - Autonomous agent that parses reports and generates React projects

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
- Complexity hotspot detection: file sizes, function counts, nesting depth
- Evolution analysis: churn hotspots, commit cadence, refactoring maturity
- Import/dependency mapping with ASCII architecture diagrams
- Code quality evidence: test ratios, type safety, error handling patterns
- Professional portfolio-entry synthesis with technical architecture, skills, and business impact
- Honest, evidence-based output — only claims what the code supports

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
