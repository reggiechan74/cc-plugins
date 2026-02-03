# Reggie Chan's Claude Code Plugins

A marketplace of Claude Code plugins for enhanced development workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add reggiechan74/cc-plugins
```

## Available Plugins

### rubric-creator

Professional-grade rubric creation skill with validity, reliability, and fairness controls for Claude Code.

**Install:**
```bash
/plugin install rubric-creator@reggiechan74
```

**Features:**
- Three creation modes: Interactive, Template, and Example-Based
- 7 pre-built domain templates (regulatory-compliance, document-quality, code-review, vendor-evaluation, risk-assessment, performance-review, research-quality)
- Professional controls: anchor examples, critical barriers, inter-rater reliability protocol
- Optional companion materials: pilot testing worksheet and scorer calibration pack

**Commands:**
- `/rubric-creator --interactive` - Guided 6-phase questionnaire with validity/alignment foundation
- `/rubric-creator --template [domain]` - Generate from pre-built domain templates
- `/rubric-creator --from-example [file]` - Analyze existing rubric and create variant

---

### spinnerverbs

Generate and apply themed spinner verbs for Claude Code status messages.

**Install:**
```bash
/plugin install spinnerverbs@reggiechan74
```

**Features:**
- Pre-built themes: Star Trek, Game of Thrones, Mandalorian
- Custom theme generation from any description
- Style modifiers: `--parody` (AI/coding humor) and `--cynic` (pessimistic twist)
- Flexible scoping: local, project, or user-level

**Commands:**
- `/spinnerverbs:create [theme]` - Generate custom themed spinner verbs
- `/spinnerverbs:apply [template]` - Apply a pre-built theme (startrek, gameofthrones, mandalorian)

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
