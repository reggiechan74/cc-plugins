# Phase 1: Plugin Infrastructure - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Scaffold the meta-compiler Claude Code plugin, implement `model:setup` and `model:doctor` commands, satisfy all cc-plugins conventions (two-step install, shields.io badges), and create the feature branch. Phase delivers a working plugin skeleton that users can install and confirm is healthy — no compiler or solver logic yet.

</domain>

<decisions>
## Implementation Decisions

### Installer strategy
- Use `uv` as the primary installer for `model:setup` — faster, more reliable dependency resolution
- Fall back to `pip` if `uv` is not found on the system — no hard uv requirement
- Never fail with "install uv first" — always offer a working path

### Virtual environment location
- Prefer `${CLAUDE_PLUGIN_ROOT}/.venv` — write there if `$CLAUDE_PLUGIN_ROOT` is writable
- Fall back to `~/.claude/meta-compiler/.venv` if plugin root is not writable (expected for cached installs)
- The venv must be fully self-contained and not pollute the user's system Python

### model:setup idempotency
- If all dependencies are already installed, skip and report "already installed" per dep
- Report which deps were already present vs newly installed in the run summary
- Re-running model:setup must be safe and fast

### Claude's Discretion
- Exact error message wording for pip fallback trigger
- Progress display format during install (spinner vs. streaming output)
- model:doctor output verbosity (terse pass/fail vs. version details) — no strong user preference expressed, Claude should lean toward terse pass/fail with actionable fix hints on failure

</decisions>

<specifics>
## Specific Ideas

- User confirmed awareness that the plugin cache is read-only — venv location must account for this by design
- Dependencies locked by PROJECT.md: ortools, z3-solver, scipy, pydantic, jinja2

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.claude-plugin/plugin.json` pattern: existing plugins use name, version, description, author, keywords, license, agents fields
- Badge pattern: existing READMEs use `<!-- badges-start -->` / `<!-- badges-end -->` markers (established by marketplace README)

### Established Patterns
- Two-step install: `/plugin marketplace add reggiechan74/cc-plugins` + `/plugin install <name>@cc-plugins` — non-negotiable per CLAUDE.md
- Plugin directory structure: `plugin-name/.claude-plugin/plugin.json` + commands/skills/agents subdirs (from code-coherence, course-curriculum-creator, etc.)
- No existing plugin in the repo has a Python runtime component — this is new ground

### Integration Points
- Plugin will live at `meta-compiler/` in the repo root
- Feature branch must be created before any implementation (per STATE.md blocker)

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-plugin-infrastructure*
*Context gathered: 2026-03-09*
