---
name: create-from-template
description: Create new course from saved template
argument-hint: "[template-name] --variant [VariantName] [--location path]"
allowed-tools:
  - AskUserQuestion
  - Bash
  - Read
  - Write
  - Edit
---

# Create From Template Command

Generate new course by adapting a saved template.

## Prerequisites

- Template must exist in template directory
- User must specify variant focus

## Command Behavior

1. Verify template exists
2. Prompt for variant details (if not provided)
3. Copy template to new course directory
4. Replace parameterized values
5. Generate new dates/versions
6. Report created course with customization guidance

## Arguments

**Required:**
- `template-name`: Name of saved template

**Optional:**
- `--variant`: Variant name (e.g., "Commercial-Focus", "Residential")
- `--location`: Output directory (default from settings)

## Variant Customization

After creating from template:

1. **Update course positioning**:
   - Adjust target audience for variant
   - Refine value proposition
   - Update market differentiation

2. **Customize examples**:
   - Replace [EXAMPLE] placeholders with variant-specific examples
   - Update case studies
   - Adjust scenarios

3. **Adjust timing** (if needed):
   - Module duration may vary
   - Activity complexity may differ

4. **Refine objectives** (if needed):
   - May emphasize different aspects
   - Add/remove based on variant focus

## Output Structure

```
VariantName-YYYY-MM-DD/
├── 01-planning/
│   ├── course-positioning.md (updated with variant focus)
│   ├── course-description.md (from template, needs customization)
│   └── learning-objectives.md (from template)
├── 02-design/
│   ├── course-outline.md (from template)
│   └── lesson-plans.md (from template, examples need updating)
├── 03-assessment/
│   └── rubrics.md (from template)
└── 04-materials/
    └── README.md
```

## Completion Message

```
✓ Course created from template: [template-name]

New course: [location]/VariantName-YYYY-MM-DD/

**Template:** [template-name]
**Variant:** [VariantName]
**Customization needed:**

1. Update examples in lesson-plans.md (search for [EXAMPLE])
2. Refine course-positioning.md for variant audience
3. Customize case studies and scenarios
4. Review and adjust timing if needed

**Next steps:**
- Review all files for template placeholders
- Update course-description.md for variant
- Customize materials: /generate-artifacts
```

## Template List

If user doesn't know template names:
```
Available templates:

1. proptech-fundamentals
   - 2-day, professional level
   - 10 objectives (Apply/Analyze focus)
   - Real estate technology analysis

2. [other-template]
   - [details]

Use: /create-from-template [template-name] --variant [YourVariant]
```

---

Rapidly create course variants from proven templates, maintaining structure while allowing customization for specific audiences or contexts.
