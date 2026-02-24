---
name: list-templates
description: List available course templates with details
argument-hint: "[--verbose]"
allowed-tools:
  - Bash
  - Read
  - Glob
---

# List Templates Command

Display available course templates from the template directory.

## Command Behavior

When user invokes `/list-templates`:

1. **Determine template directory:**
   - Read from settings `template_directory` in `.claude/course-curriculum-creator.local.md`
   - Default: `~/.claude/course-templates/`

2. **Scan for templates:**
   - List subdirectories in the template directory
   - Read `template-metadata.json` from each subdirectory
   - If metadata file is missing, note as "unregistered template"

3. **Display template list:**

**Standard output:**

```
Available Course Templates:

1. proptech-fundamentals
   Duration: 2-day | Modules: 8 | Level: professional
   "Two-day PropTech workshop for real estate professionals"

2. ai-basics-workshop
   Duration: 1-day | Modules: 5 | Level: beginner
   "Introduction to AI concepts for non-technical professionals"

[No templates found: Template directory is empty. Save a course as template using /save-as-template]
```

**Verbose output (with --verbose flag):**

```
Available Course Templates:

1. proptech-fundamentals
   Duration: 2-day | Modules: 8 | Level: professional
   "Two-day PropTech workshop for real estate professionals"

   Cognitive Distribution:
     Understand: 2 | Apply: 4 | Analyze: 2 | Evaluate: 1 | Create: 1

   Keywords: PropTech, Real Estate, Analysis, Technology
   Created: 2026-01-15 by Reggie Chan
   Template directory: ~/.claude/course-templates/proptech-fundamentals/

   Placeholders: 12 automatic, 8 domain-specific
   Files: 6 curriculum files + template-manifest.md

---

[Repeat for each template]
```

## Settings Integration

Read from `.claude/course-curriculum-creator.local.md` if exists:
- `template_directory`: Where to look for templates (default: `~/.claude/course-templates/`)

If settings file doesn't exist, use default template directory.

## Error Handling

**Template directory doesn't exist:**
- "No template directory found at [path]. Create templates using `/save-as-template` first."

**Empty template directory:**
- "No templates found. Save a course as a template using `/save-as-template`."

**Corrupted metadata:**
- Skip the template and note: "[template-name]: Unable to read metadata (template-metadata.json missing or corrupt)"

## Example Usage

**Standard:**
```
User: /list-templates
[Shows template names, duration, module count, level, description]
```

**Verbose:**
```
User: /list-templates --verbose
[Shows full details including cognitive distribution, keywords, dates, placeholder counts]
```

---

List available course templates to help instructors find and reuse proven curriculum structures.
