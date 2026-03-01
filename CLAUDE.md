# Claude Code Plugin Marketplace

This repo is a Claude Code plugin marketplace owned by Reggie Chan (`reggiechan74/cc-plugins`).

## Plugin README Standards

Every plugin README must include the correct two-step install instructions:

```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install <plugin-name>@cc-plugins
```

Do not use `claude plugin add /path/to/...` or other local-only install methods in READMEs.

Every plugin README must include shields.io badges inside `<!-- badges-start -->` / `<!-- badges-end -->` markers, placed immediately after the `# ` heading. Use `/update-badges` to generate them. At minimum, include version, license, and Claude Code plugin badges.
