# Course Curriculum Creator

A Claude Code plugin for rapidly creating professional, pedagogically-sound curricula for 1-2 day intensive workshops and training programs.

## Overview

This plugin helps independent consultants, trainers, and instructional designers create comprehensive course materials using backward design methodology and Bloom's taxonomy. It generates structured curricula with learning objectives, lesson plans, assessment rubrics, and supporting materials—all in markdown format for easy version control and collaboration.

## Features

- **Backward Design Framework**: Start with learning outcomes, design assessments, then plan activities
- **Bloom's Taxonomy Integration**: Create measurable learning objectives at appropriate cognitive levels
- **Rapid Course Creation**: Generate complete curricula autonomously or step-by-step
- **Modular Architecture**: Create courses optimized for 1-2 day weekend workshops
- **Professional Outputs**: Course descriptions, outlines, lesson plans, rubrics, student materials
- **Template System**: Save and reuse course structures for variants and iterations
- **Cascade Invalidation**: Automatic staleness detection when source files change
- **Export Workflows**: Export as complete document, stakeholder summary, or student syllabus
- **Delivery Support**: Workshop preparation checklists and post-workshop feedback processing
- **Quality Gates**: Prerequisite validation hooks prevent generating files out of order
- **Incremental Updates**: Add, remove, or modify individual objectives and modules
- **Version Control Ready**: Semantic versioning with organized markdown files

## Installation

### From Marketplace
```bash
cc plugin install course-curriculum-creator
```

### Local Development
```bash
# Clone or copy plugin to your plugins directory
cp -r course-curriculum-creator ~/.claude/plugins/

# Enable in Claude Code
cc plugin enable course-curriculum-creator
```

## Quick Start

### Autonomous Course Creation
```
User: "Create a 2-day PropTech fundamentals workshop for real estate professionals"
```
The `curriculum-architect` agent will automatically generate a complete curriculum.

### Step-by-Step Course Creation
```bash
# 1. Initialize course project
/create-course "PropTech Fundamentals"

# 2. Generate core curriculum (backward design order)
/generate-objectives          # Stage 1: Desired results
/generate-rubrics             # Stage 2: Assessment evidence
/generate-outline             # Stage 3: Learning plan
/generate-lesson-plans        # Stage 3: Detailed activities
/generate-description         # Student-facing description

# 3. Create additional materials
/generate-artifacts --type handout
/generate-artifacts --type instructor-guide

# 4. Review and export
/review-curriculum
/export-curriculum --format full

# 5. Prepare for delivery
/generate-workshop-prep --date 2026-03-15
```

## Commands

| Command | Description |
|---------|-------------|
| `/create-course` | Initialize new course project with directory structure |
| `/generate-objectives` | Create Bloom's-aligned learning objectives |
| `/generate-rubrics` | Create 1-5 scale analytical assessment rubrics |
| `/generate-outline` | Generate module structure with timing |
| `/generate-lesson-plans` | Generate detailed module-level lesson plans |
| `/generate-description` | Create student-facing course description |
| `/generate-artifacts` | Generate student handouts, instructor guides, etc. |
| `/review-curriculum` | Validate curriculum quality and alignment |
| `/export-curriculum` | Export curriculum as combined document (full/summary/syllabus) |
| `/save-as-template` | Save course structure as reusable template |
| `/create-from-template` | Create new course from existing template |
| `/list-templates` | List available course templates with details |
| `/generate-workshop-prep` | Generate dated preparation checklist for delivery |
| `/process-workshop-feedback` | Analyze feedback and generate improvement report |

## Skills

### backward-design-methodology
Provides knowledge on Understanding by Design (UbD) framework for creating effective curricula:
- Stage 1: Identify desired results (learning outcomes)
- Stage 2: Determine acceptable evidence (assessments)
- Stage 3: Plan learning experiences (activities)

**Triggers**: "use backward design", "create curriculum using UbD", "design learning outcomes first"

### blooms-taxonomy
Guides creation of measurable learning objectives across cognitive levels:
- Six levels: Remember, Understand, Apply, Analyze, Evaluate, Create
- Action verb selection for each level
- Assessment type recommendations
- Scaffolding strategies for multi-day workshops

**Triggers**: "write learning objectives", "use Bloom's taxonomy", "create measurable outcomes"

## Agents

### curriculum-architect
Autonomous agent that designs complete course curricula from high-level requirements. Takes course topic, audience, and duration, then generates all core curriculum components following backward design principles.

**Triggers proactively** when user asks to create courses, or invoke manually for autonomous generation.

### quality-reviewer
Validates curriculum quality by checking:
- Alignment between outcomes, assessments, and activities
- Appropriate Bloom's taxonomy usage
- Realistic timing for 1-2 day format
- Assessment-objective correspondence
- Overall pedagogical soundness

Run automatically after generation or invoke with `/review-curriculum`.

## Configuration

Create `.claude/course-curriculum-creator.local.md` to customize defaults:

```yaml
---
# Instructor Information
instructor_name: "Your Name"
instructor_bio: "Your credentials and experience"
organization: "Your Organization"

# Course Defaults
default_duration: "2-day"
default_activity_format: "lab-heavy"  # lab-heavy, lecture-heavy, balanced
default_audience_level: "professional"  # beginner, intermediate, professional, expert

# Output Configuration
courses_directory: "~/courses"
version_strategy: "semantic"  # semantic or date-based

# Assessment Defaults
rubric_scale: "1-5"
rubric_type: "analytical"  # performance, analytical, holistic

# Templates
use_custom_templates: false
template_directory: "~/.claude/course-templates"
---
```

## Course Directory Structure

When you create a course, the following structure is generated:

```
CourseName-YYYY-MM-DD/
├── 01-planning/
│   ├── course-positioning.md      # Market fit, audience, value proposition
│   ├── course-description.md      # Student-facing description
│   └── learning-objectives.md     # Bloom's-aligned outcomes
├── 02-design/
│   ├── course-outline.md          # Module structure with timing
│   └── lesson-plans.md            # Detailed module plans
├── 03-assessment/
│   └── rubrics.md                 # 1-5 scale evaluation criteria
└── 04-materials/
    ├── student-handout.md
    ├── instructor-guide.md
    └── [other artifacts]
```

## Template System

Save successful courses as templates for reuse:

```bash
# Save as template
/save-as-template "PropTech-Fundamentals-2025-02-15"

# Create variant from template
/create-from-template PropTech-Fundamentals --variant "Commercial-Focus"
```

Templates preserve structure, objectives, and pedagogical approach while allowing customization for different audiences or contexts.

## Version Control

Courses use semantic versioning (v1.0.0, v1.1.0, v2.0.0):
- **Major**: Complete curriculum redesign
- **Minor**: New modules or significant content additions
- **Patch**: Small fixes, timing adjustments, clarity improvements

Update version in `course-positioning.md` frontmatter when making changes.

## Best Practices

1. **Start with outcomes**: Clearly define what students should achieve before designing content
2. **Align rigorously**: Ensure assessments measure objectives, and activities support both
3. **Scaffold appropriately**: Progress from lower to higher Bloom's levels across the workshop
4. **Time realistically**: Account for breaks, setup, troubleshooting in 1-2 day formats
5. **Review regularly**: Use quality-reviewer agent to validate alignment after changes
6. **Version deliberately**: Increment versions when making substantial changes
7. **Template strategically**: Save proven structures for course families

## Examples

See `examples/` directory for:
- `course-curriculum-creator.local.md` - Sample configuration file for customizing defaults

See `skills/` subdirectories for worked examples:
- `skills/blooms-taxonomy/examples/example-objectives-1day.md` - Complete 1-day workshop objective set
- `skills/blooms-taxonomy/examples/example-objectives-2day.md` - Complete 2-day workshop objective set
- `skills/backward-design-methodology/examples/example-backward-design-1day.md` - Full backward design walkthrough

## Contributing

Contributions welcome! Please:
1. Follow existing patterns for commands, agents, and skills
2. Include examples for new features
3. Update documentation
4. Test with real curriculum creation scenarios

## License

MIT

## Author

Created by Reggie Chan for Tenebrus Capital Corp training programs.

## Support

_GitHub repository and issue tracking coming soon._
