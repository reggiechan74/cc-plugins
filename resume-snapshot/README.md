# resume-snapshot

<!-- badges-start -->
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-plugin-blueviolet)
<!-- badges-end -->

A Claude Code plugin that generates portfolio-ready repository snapshots for resume and job documentation. Run one command in any git repo to produce a polished markdown summary suitable for GitHub portfolio READMEs, job applications, and technical interviews.

## Installation

### From Marketplace
```
/plugin marketplace add reggiechan74/cc-plugins
/plugin install resume-snapshot@cc-plugins
```

### Local Development
```bash
claude --plugin-dir /path/to/resume-snapshot
```

## Usage

From inside any git repository:

```
/resume-snapshot
```

Writes `RESUME_SNAPSHOT.md` to the repo root by default.

### Options

- `--output FILE` — Write to a custom path instead of `RESUME_SNAPSHOT.md`.

```
/resume-snapshot --output ~/portfolio/my-project.md
```

## What It Captures

The command collects:

- Git metadata — commit count, contributors, tags, first/last commit dates, recent activity
- File statistics — language breakdown by extension
- Project structure — top-level layout and notable directories
- Detected stack — package managers, frameworks, test runners
- Documentation signals — README presence, license, CI configuration

It then synthesizes a portfolio-quality markdown document describing what the repository is, who built it, the tech stack, and the work done — written for non-technical recruiters as well as engineering reviewers.

## Output Format

The generated document includes:

- One-line project summary
- Role and contribution context
- Tech stack (languages, frameworks, tooling)
- Notable features or technical highlights
- Project scale (commits, contributors, age)
- Links and references

## License

MIT

## Support

Issues and contributions: https://github.com/reggiechan74/cc-plugins/issues
