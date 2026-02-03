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
- Multi-agent verification with 92%+ reliability (vs 60% single-agent baseline)
- Team of Rivals architecture with specialized critic agents
- Swiss cheese model for multi-layer error checking
- Hierarchical veto authority (any critic can reject)
- Automatic verification gates via PreToolUse/PostToolUse hooks
- Per-project configuration via `.claude/code-coherence.local.md`

**Commands:**
- `/coherence-check` - Full multi-agent verification workflow
- `/plan-review` - Review execution plans with acceptance criteria
- `/audit-trail` - Bidirectional decision history with search
- `/acceptance-criteria` - Define and enforce success criteria

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
- Professional controls: anchor examples, critical barriers, inter-rater reliability
- Confidence flagging (high/medium/low)
- Bias review checklist
- Optional companion materials (pilot testing worksheet, scorer calibration pack)

**Commands:**
- `/rubric-creator --interactive` - Guided 6-phase questionnaire
- `/rubric-creator --template [domain]` - Generate from pre-built templates
- `/rubric-creator --from-example [file]` - Create variant from existing rubric

---

### spinnerverbs

Generate and apply themed spinner verbs for Claude Code status messages. Includes pre-built themes (Star Trek, Game of Thrones, Mandalorian) with optional humor and cynic modifiers.

**Install:**
```bash
/plugin install spinnerverbs@reggiechan74
```

**Features:**
- Pre-built themes: Star Trek, Game of Thrones, Mandalorian
- Custom theme generation from descriptions
- Style modifiers: `--parody` (AI/LLM references), `--cynic` (pessimistic twist)
- Flexible scoping: project, user, or local directory

**Commands:**
- `/spinnerverbs:create [theme]` - Generate new themed spinner verbs
- `/spinnerverbs:apply [template-name]` - Apply a pre-built theme template

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
