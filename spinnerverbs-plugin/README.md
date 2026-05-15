# Spinnerverbs Plugin

<!-- badges-start -->
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)
<!-- badges-end -->

Generate and apply themed spinner verbs for Claude Code status messages.

## Installation

```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install spinnerverbs@cc-plugins
```

## Features

- **Pre-built themes**: Star Trek, Game of Thrones, Mandalorian
- **Custom theme generation**: Create your own themed spinner verbs
- **Style modifiers**:
  - `--parody`: Adds Claude Code / AI / LLM parody references
  - `--cynic`: Adds pessimistic / world-weary / Murphy's Law twist
- **Flexible scoping**: Apply to current project, user-level, or local directory

## Commands

### `/spinnerverbs:create [theme] [options]`

Generate new themed spinner verbs from a description.

**Arguments:**
- `[theme]` - Theme description (e.g., "pirate", "chef", "corporate", or a detailed description)

**Options:**
- `--parody` - Add Claude Code / AI parody references
- `--cynic` - Add pessimistic / world-weary twist
- `--scope [local|project|user]` - Where to save (default: `user`)
- `--merge` - When using both `--parody` and `--cynic`, merge both variants
- `--combine` - When using both modifiers, create combined phrases with both styles

**Examples:**
```
/spinnerverbs:create pirate --parody
/spinnerverbs:create "real estate appraisal" --cynic
/spinnerverbs:create medieval --parody --cynic --merge
```

### `/spinnerverbs:apply [template-name] [options]`

Apply a pre-built theme template.

**Arguments:**
- `[template-name]` - One of: `startrek`, `gameofthrones`, `mandalorian`

**Options:**
- `--parody` - Use the parody variant
- `--cynic` - Use the cynic variant
- `--scope [local|project|user]` - Where to save (default: `user`)
- `--merge` - Merge base + selected variant(s)
- `--replace` - Replace with selected variant only (default)

**Examples:**
```
/spinnerverbs:apply startrek
/spinnerverbs:apply gameofthrones --cynic
/spinnerverbs:apply mandalorian --parody --cynic --merge
```

## Pre-built Themes

### Star Trek
Classic quotes from TOS, TNG, DS9, and Voyager with optional AI/coding parodies.

### Game of Thrones
Quotes from Westeros with optional cynical twists about the nature of software development.

### Mandalorian
This is the way... to customize your spinner verbs.

## Output Format

Writes to `settings.json` with the following structure:

```json
{
  "spinnerVerbs": {
    "mode": "replace",
    "verbs": [
      "Themed phrase 1",
      "Themed phrase 2",
      "..."
    ]
  }
}
```

## Installation

1. Clone or copy this plugin to your Claude Code plugins directory
2. Enable the plugin in Claude Code settings
3. Use `/spinnerverbs:apply` or `/spinnerverbs:create` to customize your spinner

## License

MIT
