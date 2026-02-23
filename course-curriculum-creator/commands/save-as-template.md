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
