# Rubric Creator Plugin for Claude Code

Professional-grade rubric creation skill with validity, reliability, and fairness controls.

## Features

- **Three Creation Modes:**
  - **Interactive** (`--interactive`): Guided 6-phase questionnaire with validity/alignment foundation
  - **Template** (`--template [domain]`): Generate from 7 pre-built domain templates
  - **Example-Based** (`--from-example [file]`): Analyze existing rubric and create variant

- **Professional Controls:**
  - Anchor examples for every score level
  - Critical barrier definitions with thresholds
  - Inter-rater reliability protocol
  - Confidence flagging (high/medium/low)
  - Bias review checklist
  - Maintenance lifecycle schedule

- **Optional Companion Materials:**
  - `--with-pilot`: Generate pilot testing worksheet
  - `--with-calibration`: Generate scorer calibration pack

## Installation

### Option 1: Copy to .claude/skills/

```bash
# From your project root
cp -r rubric-creator .claude/skills/
```

### Option 2: Symlink (for development)

```bash
ln -s /path/to/rubric-creator .claude/skills/rubric-creator
```

## Available Templates

| Template | Domain | Total Points |
|----------|--------|--------------|
| `regulatory-compliance` | Bylaws, regulations, policies | 250 |
| `document-quality` | Reports, proposals, technical docs | 200 |
| `code-review` | Software quality assessment | 150 |
| `vendor-evaluation` | RFP/proposal scoring | 200 |
| `risk-assessment` | Project/operational risk | 100 |
| `performance-review` | Employee/team performance | 100 |
| `research-quality` | Academic/research papers | 200 |

## Usage Examples

```bash
# Interactive mode - full professional package
/rubric-creator --interactive --with-pilot --with-calibration

# Generate from template with pilot worksheet
/rubric-creator --template regulatory-compliance --output zoning_rubric.md --with-pilot

# Create variant from existing rubric
/rubric-creator --from-example existing_rubric.md --output new_domain_rubric.md
```

## Generated Rubric Structure

Every rubric includes:

1. **Alignment Statement** - Construct definition and validation method
2. **Scoring Instructions** - Level rules, boundary handling, evidence requirements
3. **Inter-Rater Reliability Protocol** - Calibration and disagreement resolution
4. **Critical Barrier Definitions** - Hard stops with consequences
5. **Categories with Criteria** - Weighted sections with anchor examples
6. **Score Interpretation Bands** - Rating thresholds with recommended actions
7. **Bias Review Findings** - Content, structural, and scorer bias mitigations
8. **Version History** - Change tracking and maintenance schedule

## File Structure

```
rubric-creator/
├── manifest.json              # Plugin metadata
├── README.md                  # This file
├── SKILL.md                   # Main skill definition
├── templates/
│   └── templates-library.md   # 7 domain templates with anchor examples
└── rules/
    ├── pilot-testing.md       # Pilot testing worksheet template
    └── calibration-pack.md    # Scorer calibration pack template
```

## Requirements

- Claude Code v1.0.0 or higher
- No external dependencies

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions welcome! Please ensure:
1. Templates include anchor examples for all score levels
2. Bias review is conducted on new templates
3. Inter-rater reliability benchmarks are documented
