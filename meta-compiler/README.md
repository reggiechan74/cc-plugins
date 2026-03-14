# model

<!-- badges-start -->
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)
<!-- badges-end -->

Live validation for mathematical model documents (`.math.md`). Auto-validates on every edit, hard blocks on inconsistency.

## Installation

```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install model@cc-plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/model:check <file>` | Run validation pipeline against a `.math.md` document |
| `/model:status <file>` | Show symbol table, coverage, and orphan/phantom status |
| `/model:paper <file>` | Generate clean paper artifact (strips validation blocks) |
| `/model:report <file>` | Generate full validation report |
| `/model:compile <file>` | Produce all three artifacts (paper, codebase, report) |

## Live Validation

When installed, the plugin automatically validates `.math.md` files every time Claude writes or edits one. Validation errors are hard blocks — Claude must fix them before continuing.

The hook runs in **authoring mode**: symbol conflicts, undefined references, index mismatches, and dimensional errors are hard blocks. Orphan symbols produce warnings only (the symbol may be used in a later section).

Coverage gaps (math blocks without corresponding validation blocks) are reported as warnings.

## Requirements

Python 3.10+ with the `meta_compiler` package available on the Python path. The package is included in this plugin directory.
