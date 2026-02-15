# Reggie Chan's Claude Code Plugins

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
/plugin install code-coherence@reggiechan74
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
/plugin install course-curriculum-creator@reggiechan74
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

### install-private-plugin

Configure git auth for installing Claude Code plugins from private GitHub repos. Guides PAT creation, Codespace secret storage, and git URL rewriting when `/plugin marketplace add` fails with 403 or HTTPS auth errors.

**Install:**
```bash
/plugin install install-private-plugin@reggiechan74
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
/plugin install kids-camp-planner@reggiechan74
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
/plugin install mississauga-permits@reggiechan74
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

### report-to-web

Convert markdown research reports into interactive React presentation websites for GitHub Pages.

**Install:**
```bash
/plugin install report-to-web@reggiechan74
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

### rubric-creator

Professional-grade rubric creation skill with validity, reliability, and fairness controls for Claude Code.

**Install:**
```bash
/plugin install rubric-creator@reggiechan74
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
/plugin install spinnerverbs@reggiechan74
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
