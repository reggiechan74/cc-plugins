---
# Instructor Information
instructor_name: "Reggie Chan"
instructor_bio: "PGCV certified real estate professional with 10+ years experience in infrastructure consulting and PropTech innovation"
organization: "Tenebrus Capital Corp"

# Course Defaults
default_duration: "2-day"
default_activity_format: "lab-heavy"  # Options: lab-heavy, lecture-heavy, balanced
default_audience_level: "professional"  # Options: beginner, intermediate, professional, expert

# Output Configuration
courses_directory: "~/courses"
version_strategy: "semantic"  # Options: semantic, date-based

# Assessment Defaults
rubric_scale: "1-5"  # Options: 1-4, 1-5, letter-grades, pass-fail
rubric_type: "analytical"  # Options: performance, analytical, holistic

# Templates
use_custom_templates: false
template_directory: "~/.claude/course-templates"
---

# Course Curriculum Creator Configuration

This file configures default settings for the Course Curriculum Creator plugin.

## Configuration Instructions

1. Copy this file to: `.claude/course-curriculum-creator.local.md`
2. Update the YAML frontmatter with your preferences
3. Save the file (it's git-ignored by default)

## Field Descriptions

### Instructor Information
- **instructor_name**: Your name as it appears on course materials
- **instructor_bio**: Brief credentials/experience statement for instructor guides
- **organization**: Your company/institution name for branding

### Course Defaults
- **default_duration**: Default workshop length ("1-day" or "2-day")
- **default_activity_format**:
  - `lab-heavy`: Emphasis on hands-on exercises (70% practice, 30% instruction)
  - `lecture-heavy`: Emphasis on instruction (70% instruction, 30% practice)
  - `balanced`: Equal mix (50% instruction, 50% practice)
- **default_audience_level**: Target expertise level affects complexity and prerequisites

### Output Configuration
- **courses_directory**: Where to create course projects (absolute or ~ path)
- **version_strategy**:
  - `semantic`: Use v1.0.0 versioning
  - `date-based`: Use YYYY-MM-DD versioning

### Assessment Defaults
- **rubric_scale**: Scoring scale for assessment rubrics
- **rubric_type**:
  - `performance`: For skills/task completion
  - `analytical`: Multi-criteria evaluation
  - `holistic`: Overall quality assessment

### Templates
- **use_custom_templates**: Enable custom template system
- **template_directory**: Where to store/load course templates

## Notes

- All settings are optional; plugin uses sensible defaults if not specified
- Settings can be overridden per-command using arguments
- Update this file anytime; changes apply to new courses immediately
