# Claude Code Plugin Marketplace

This repo is a Claude Code plugin marketplace owned by Reggie Chan (`reggiechan74/cc-plugins`).

## Plugin README Standards

### Install section

Every plugin README must include an `## Installation` section with two subsections:

**From Marketplace** — the primary, end-user form. Required, must be exact:

```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install <plugin-name>@cc-plugins
```

**Local Development** — for contributors testing from a clone of this repo. Required, must be exact:

```
/plugin marketplace add .
/plugin install <plugin-name>@cc-plugins
```

(Run after cloning `reggiechan74/cc-plugins` and `cd`-ing into the clone. The `.` registers the local checkout as a marketplace under the same `cc-plugins` name, so the install command is identical to production.)

Do not use `claude plugin add /path/to/...`, `claude --plugin-dir`, `cp -r`, `ln -s`, or any other ad-hoc form. Consistency across plugins matters more than per-plugin preference.

### Badges

Every plugin README must include shields.io badges inside `<!-- badges-start -->` / `<!-- badges-end -->` markers, placed immediately after the `# ` heading. Use `/update-badges` to generate them. At minimum, include version, license, and Claude Code plugin badges.

### plugin.json metadata

Every `.claude-plugin/plugin.json` must include: `name`, `version`, `description`, `author.name` (`Reggie Chan`), `license` (`MIT`), `repository` (`https://github.com/reggiechan74/cc-plugins`), and `homepage` (`https://github.com/reggiechan74/cc-plugins/tree/main/<plugin-dir>`).

### Skill frontmatter

SKILL.md files must not include a `version:` field — it is undocumented in the Claude Code skill spec and silently ignored.
