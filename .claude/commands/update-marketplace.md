---
description: Scan for plugins and update marketplace.json and README.md
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Update Marketplace

Scan the repository for plugins and update both the marketplace registry and documentation.

**Arguments received:** $ARGUMENTS

## Instructions

### Step 1: Scan for Plugins

Scan the root directory `/workspaces/claude-plugins/` for plugin directories. A valid plugin is identified by:

1. **Modern format**: A directory containing `.claude-plugin/plugin.json`
2. **Legacy format**: A directory containing `manifest.json` at root level

**Exclude these directories:**
- `.git`
- `.claude-plugin` (the root marketplace config)
- `.claude` (commands/skills directory)
- `node_modules`
- Any hidden directories (starting with `.`)

For each plugin found, extract:
- `name`: From plugin.json or manifest.json
- `version`: From plugin.json or manifest.json
- `description`: From plugin.json or manifest.json
- `source`: Relative path from root (e.g., `./spinnerverbs-plugin`)

### Step 2: Read Current State

Read the current marketplace.json from `/workspaces/claude-plugins/.claude-plugin/marketplace.json`.

Compare discovered plugins against existing entries to identify:
- **New plugins**: Not in marketplace.json
- **Updated plugins**: Version or description changed
- **Removed plugins**: In marketplace.json but directory no longer exists

### Step 3: Update marketplace.json

Update `/workspaces/claude-plugins/.claude-plugin/marketplace.json` with the complete list of discovered plugins.

Format:
```json
{
  "name": "cc-plugins",
  "owner": {
    "name": "Reggie Chan"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugin-directory",
      "description": "Plugin description from manifest",
      "version": "1.0.0"
    }
  ]
}
```

Sort plugins alphabetically by name.

### Step 4: Update README.md

Update `/workspaces/claude-plugins/README.md` to document all plugins.

For each plugin:
1. Read its README.md to extract features and commands
2. Look for `## Features` section for feature list
3. Look for `## Commands` or `## Usage` sections for commands

Generate README with this structure:

```markdown
# Reggie Chan's Claude Code Plugins

A marketplace of Claude Code plugins for enhanced development workflows.

## Installation

Add this marketplace to Claude Code:

\`\`\`bash
/plugin marketplace add reggiechan74/cc-plugins
\`\`\`

## Available Plugins

### plugin-name

Short description from manifest.

**Install:**
\`\`\`bash
/plugin install plugin-name@reggiechan74
\`\`\`

**Features:**
- Feature 1
- Feature 2

**Commands:**
- `/command1` - Description
- `/command2` - Description

---

[Repeat for each plugin, separated by ---]

## Usage

After adding the marketplace, you can browse and install plugins using:

\`\`\`bash
/plugin
\`\`\`

Or install directly by name as shown above.

## Contributing

Found an issue or have a suggestion? Please open an issue in the repository.

## License

Each plugin has its own license. See individual plugin directories for details.
```

### Step 5: Report Changes

After updating both files, report:
- Number of plugins found
- New plugins added
- Plugins removed
- Plugins updated (version/description changed)

## Example Output

```
Marketplace updated successfully!

Found 2 plugins:
  ✓ rubric-creator (v1.0.0) - NEW
  ✓ spinnerverbs (v1.0.0) - unchanged

Updated files:
  - .claude-plugin/marketplace.json
  - README.md
```

## Execution

Now execute the scan and update process following the steps above.
