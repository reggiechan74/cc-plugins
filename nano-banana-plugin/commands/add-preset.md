---
description: "Add a custom image generation preset to nano-banana. Use /nano-banana:add-preset [slug] --category [name] --aspect [ratio] --size [tier]"
allowed-tools: ["Read", "Edit", "AskUserQuestion"]
arguments:
  - name: "slug"
    description: "Preset slug (lowercase, hyphens only, e.g. 'chalk-drawing')"
  - name: "category"
    description: "Category: Technical | Business | Creative | UI/UX | Photography | Specialized"
  - name: "aspect"
    description: "Default aspect ratio, e.g. 1:1, 16:9, 3:4 (default: 1:1)"
  - name: "size"
    description: "Default resolution tier: 512px | 1K | 2K | 4K (default: 2K)"
---

# Add Custom Preset

Add a new image generation preset to nano-banana, updating `config.json`, `presets.md`, and `SKILL.md`.

**Arguments received:** $ARGUMENTS

## File Paths

All paths are relative to `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/`:
- Config: `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/config.json`
- Presets reference: `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/references/presets.md`
- Skill reference: `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/SKILL.md`

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- **slug** — the preset identifier (e.g. `chalk-drawing`)
- **--category** — one of: `Technical`, `Business`, `Creative`, `UI/UX`, `Photography`, `Specialized`
- **--aspect** — default aspect ratio (default: `1:1`)
- **--size** — default resolution tier (default: `2K`)

Valid aspect ratios: `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`
Valid sizes: `512px`, `1K`, `2K`, `4K`
Valid categories: `Technical`, `Business`, `Creative`, `UI/UX`, `Photography`, `Specialized`

## Step 2: Gather Missing Information

Read `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/config.json` to check whether a preset with this slug already exists. If it does, inform the user and stop.

For any missing required fields, use AskUserQuestion to collect them one at a time:

1. If **slug** is missing or invalid (contains spaces or uppercase): ask for a valid slug.
2. If **category** is missing or invalid: ask the user to choose from the six valid categories.
3. Always ask for the **prompt prefix** — the core style instruction prepended to every prompt. Tell the user:
   - It should describe medium, style, lighting, quality anchors, and exclusions
   - It must end with a space and a period+space: `". "`
   - Aim for 30–60 words
   - Example: `"Chalk illustration on dark blackboard: soft chalk texture with visible dust marks, limited warm color palette, bold outlines with rough edges, slightly imperfect hand-drawn feel, educational diagram quality. "`
4. Always ask for a **When to Use** description (1–2 sentences describing ideal use cases).
5. Always ask for **Tips** (1–2 sentences of prompt engineering advice specific to this style).

## Step 3: Preview and Confirm

Show the user a preview of all collected values:

```
Slug:          {slug}
Category:      {category}
Aspect:        {aspect}
Size:          {size}
Prompt Prefix: {prompt_prefix}
When to Use:   {when_to_use}
Tips:          {tips}
```

Ask the user to confirm:
- ✅ Add this preset
- ✏️ Edit a field
- ❌ Cancel

If the user wants to edit a field, ask which field and re-collect it, then show the preview again.

## Step 4: Update config.json

Read `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/config.json`.

Add the new preset entry inside the `"presets"` object, after the last existing entry in the same category (or at the end if the category has no existing entries). The entry format:

```json
"{slug}": {
  "category": "{category}",
  "prompt_prefix": "{prompt_prefix}",
  "default_aspect": "{aspect}",
  "default_size": "{size}"
}
```

Ensure the preceding entry has a trailing comma before inserting.

## Step 5: Update presets.md

Read `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/references/presets.md`.

Insert a new preset section at the correct location:
- Find the `### {category}` heading section
- Add the new entry before the next `###` heading (or before `## Customization Guide` if it's the last section)
- Use this exact format:

```markdown
---

#### {slug}

- **Slug:** `{slug}`
- **Default Aspect:** {aspect}
- **Default Size:** {size}
- **Prompt Prefix:** "{prompt_prefix}"
- **When to Use:** {when_to_use}
- **Tips:** {tips}
```

## Step 6: Update SKILL.md

Read `$CLAUDE_PLUGIN_ROOT/skills/nano-banana/SKILL.md`.

Find the **Preset Quick-Reference** table (the table with columns `Category | Slug | Aspect | Size`). Add a new row at the end of the correct category group:

```
| {category} | `{slug}` | {aspect} | {size} |
```

Also update the preset count in the `## Purpose` section if it references a specific number (e.g. "25 style presets" → "26 style presets").

## Step 7: Confirm Success

Report:
- The slug and category of the new preset
- Confirmation that all three files were updated
- Example usage: `python3 $BASE_DIR/scripts/nano_banana.py --prompt "your prompt" --preset {slug}`
