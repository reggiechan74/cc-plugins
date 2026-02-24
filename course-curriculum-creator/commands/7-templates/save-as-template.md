---
name: save-as-template
description: Save current course as reusable template
argument-hint: "[template-name]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
---

# Save As Template Command

Save current course structure as a reusable template for creating variants.

## Prerequisites

- Must be in complete course directory
- Should have at least objectives and outline

## Command Behavior

1. Validate course completeness
2. Prompt for template name (if not provided)
3. Copy course structure to template directory
4. Create template metadata
5. Confirm template saved

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `template_directory`: Where to store saved templates (default: `~/.claude/course-templates/`)

If settings file doesn't exist, use sensible defaults or prompt user.

## Template Storage

**Location:** From settings `template_directory` or default `~/.claude/course-templates/`

**Structure:**
```
~/.claude/course-templates/
└── template-name/
    ├── template-metadata.json
    ├── 01-planning/
    ├── 02-design/
    ├── 03-assessment/
    └── 04-materials/
```

## Template Metadata

```json
{
  "templateName": "template-name",
  "originalCourse": "CourseName-YYYY-MM-DD",
  "createdDate": "YYYY-MM-DD",
  "createdBy": "[instructor from settings]",
  "duration": "1-day or 2-day",
  "audienceLevel": "professional",
  "cognitiveDistribution": {
    "understand": 2,
    "apply": 4,
    "analyze": 2,
    "evaluate": 1,
    "create": 1
  },
  "moduleCount": 8,
  "description": "Brief template description",
  "keywords": ["PropTech", "Real Estate", "Analysis"]
}
```

## What Gets Saved

**Include:**
- Complete directory structure
- All curriculum files with content
- Assessment rubrics
- Lesson plans structure

**Parameterize:**
- Course title → [COURSE_TITLE]
- Specific examples → [EXAMPLE]
- Date references → [DATE]
- Instructor name → [INSTRUCTOR]

## Parameterization Rules

When saving a course as a template, apply these parameterization rules to make the template reusable:

### Automatic Replacements

These replacements are made automatically during template save:

| Original Value | Template Placeholder | Source |
|---------------|---------------------|--------|
| Course title | `{{COURSE_TITLE}}` | From course-positioning.md frontmatter `title` |
| Course dates | `{{DATE}}` | All date references in content |
| Instructor name | `{{INSTRUCTOR_NAME}}` | From settings `instructor_name` or frontmatter |
| Organization name | `{{ORGANIZATION}}` | From settings `organization` or frontmatter |
| Version number | `{{VERSION}}` | Reset to `0.1.0` in template |
| Status | `draft` | Always reset to draft |

### Domain-Specific Replacements (Prompted)

Prompt the user to identify these context-specific elements for parameterization:

- **Industry examples**: "Which examples are specific to this course's domain?" → Replace with `{{EXAMPLE: description}}`
- **Case studies**: "Which case studies should be swapped for different audiences?" → Replace with `{{CASE_STUDY: description}}`
- **Tool/software names**: "Which tools are specific to this offering?" → Replace with `{{TOOL: description}}`
- **Audience-specific references**: "Which references assume a particular audience?" → Replace with `{{AUDIENCE_REF: description}}`

### What NOT to Parameterize

Preserve these elements as-is (they represent pedagogical design decisions):
- Bloom's taxonomy action verbs in objectives
- Cognitive level distribution
- Module timing allocations and structure
- Assessment criteria and rubric descriptors
- Scaffolding sequence and progression
- Activity types and instructional strategies

### Template Manifest

When saving, also generate `template-manifest.md` alongside `template-metadata.json`:

```markdown
# Template Manifest: {{COURSE_TITLE}}

## Placeholders

| Placeholder | Type | Description | Example Value |
|-------------|------|-------------|---------------|
| `{{COURSE_TITLE}}` | automatic | Course title | "PropTech Fundamentals" |
| `{{DATE}}` | automatic | Current date | "2026-02-23" |
| `{{INSTRUCTOR_NAME}}` | automatic | Instructor name | "John Smith" |
| `{{ORGANIZATION}}` | automatic | Organization | "Acme Corp" |
| `{{VERSION}}` | automatic | Version number | "0.1.0" |
| `{{EXAMPLE: ...}}` | domain | Domain-specific example | varies |
| `{{CASE_STUDY: ...}}` | domain | Case study reference | varies |
| `{{TOOL: ...}}` | domain | Tool/software name | varies |

## Files Parameterized

- `01-planning/course-positioning.md` - [N] replacements
- `01-planning/learning-objectives.md` - [N] replacements
- [list all files with replacement counts]

## Customization Guide

When creating a course from this template:
1. All automatic placeholders are replaced during `/create-from-template`
2. Domain-specific placeholders ({{EXAMPLE}}, {{CASE_STUDY}}, etc.) require manual customization
3. Review all files for domain-specific references that weren't parameterized
```

## Usage Message

```
✓ Template saved: [template-name]

Location: ~/.claude/course-templates/template-name/

This template includes:
- [N] learning objectives ([distribution])
- [N] modules
- Assessment rubrics
- Lesson plan structure
- [Other components]

Create course from this template:
  /create-from-template [template-name] --variant [YourVariant]

List all templates:
  ls ~/.claude/course-templates/
```

---

Save proven course structures as templates for rapid variant creation.
