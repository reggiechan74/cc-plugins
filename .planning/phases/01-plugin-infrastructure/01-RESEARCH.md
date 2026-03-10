# Phase 1: Plugin Infrastructure - Research

**Researched:** 2026-03-09
**Domain:** Claude Code plugin scaffolding, Python runtime setup, cc-plugins conventions
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Installer strategy:**
- Use `uv` as the primary installer for `model:setup` -- faster, more reliable dependency resolution
- Fall back to `pip` if `uv` is not found on the system -- no hard uv requirement
- Never fail with "install uv first" -- always offer a working path

**Virtual environment location:**
- Prefer `${CLAUDE_PLUGIN_ROOT}/.venv` -- write there if `$CLAUDE_PLUGIN_ROOT` is writable
- Fall back to `~/.claude/meta-compiler/.venv` if plugin root is not writable (expected for cached installs)
- The venv must be fully self-contained and not pollute the user's system Python

**model:setup idempotency:**
- If all dependencies are already installed, skip and report "already installed" per dep
- Report which deps were already present vs newly installed in the run summary
- Re-running model:setup must be safe and fast

### Claude's Discretion
- Exact error message wording for pip fallback trigger
- Progress display format during install (spinner vs. streaming output)
- model:doctor output verbosity (terse pass/fail vs. version details) -- no strong user preference expressed, Claude should lean toward terse pass/fail with actionable fix hints on failure

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | User can run `model:setup` to install Python runtime dependencies (ortools, z3-solver, scipy, pydantic, jinja2) via uv or pip | uv/pip detection pattern, venv creation, idempotency check |
| INFRA-02 | User can run `model:doctor` to diagnose runtime environment, verify dependency versions, and surface missing or incompatible packages | importlib.metadata for version inspection, per-dep pass/fail reporting |
| INFRA-03 | Plugin follows cc-plugins two-step install conventions | plugin.json schema, confirmed from existing plugins in repo |
| INFRA-04 | Plugin README includes shields.io badges inside `<!-- badges-start -->` / `<!-- badges-end -->` markers | update-badges command pattern, badge format confirmed from repo |
</phase_requirements>

---

## Summary

Phase 1 scaffolds the `meta-compiler` plugin directory, implements `model:setup` and `model:doctor` as Claude Code command markdown files (backed by a Python script), and satisfies all cc-plugins conventions. No compiler or solver logic is needed yet -- the deliverable is a healthy plugin skeleton that users can install and confirm is working.

The plugin structure is well-understood from existing plugins in this repo. The only genuinely new ground is the Python runtime component: no other plugin here uses a venv-based setup command. The pattern is straightforward -- a shell-aware Python script handles uv/pip detection, venv creation, and idempotent dependency installation. The command markdown file invokes it via `Bash(python3:*)` or direct shell, passing `$CLAUDE_PLUGIN_ROOT` as the anchor.

The two-step install convention, plugin.json schema, badge format, and command file structure are all confirmed from existing repo code with HIGH confidence. The uv/pip fallback logic and venv writable-path detection are standard Python patterns with no surprising edge cases.

**Primary recommendation:** Implement `model:setup` as a standalone Python script at `meta-compiler/scripts/setup_runtime.py`, invoked by the command markdown. The script handles all installer detection, venv creation, and idempotency. This mirrors the `fetch_permits.py` pattern already established in `mississauga-permits`.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| uv | latest | Fast Python package installer and venv manager | Locked decision; faster than pip, better resolution |
| pip | stdlib | Fallback installer when uv absent | Always available with Python; ensures working path |
| venv | stdlib (Python 3.3+) | Virtual environment creation | No extra install; self-contained isolation |
| importlib.metadata | stdlib (Python 3.8+) | Version inspection in model:doctor | Zero deps; works for any installed package |

### Runtime Dependencies (Installed by model:setup)
| Library | Purpose | Install Name |
|---------|---------|--------------|
| ortools | CP-SAT solver (Phase 5+) | `ortools` |
| z3-solver | SMT verification (Phase 8+) | `z3-solver` |
| scipy | Sensitivity analysis (Phase 9+) | `scipy` |
| pydantic | YAML spec validation (Phase 2+) | `pydantic` |
| jinja2 | Template rendering (Phase 4+) | `jinja2` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| subprocess | stdlib | Run uv/pip from Python script | Inside setup_runtime.py |
| sys, os | stdlib | Path resolution, exit codes | Inside setup_runtime.py |
| shutil.which | stdlib | Detect uv on PATH | Installer detection |

**Installation (by model:setup itself):**
```bash
# uv path (preferred):
uv pip install --python "${VENV}/bin/python" ortools z3-solver scipy pydantic jinja2

# pip fallback:
"${VENV}/bin/python" -m pip install ortools z3-solver scipy pydantic jinja2
```

---

## Architecture Patterns

### Recommended Plugin Structure
```
meta-compiler/
├── .claude-plugin/
│   └── plugin.json              # name, version, description, author, keywords, license, commands
├── commands/
│   ├── model-setup.md           # model:setup command (invokes scripts/setup_runtime.py)
│   └── model-doctor.md          # model:doctor command (invokes scripts/doctor_runtime.py)
├── scripts/
│   ├── setup_runtime.py         # venv creation + idempotent dep install
│   └── doctor_runtime.py        # per-dep version check + pass/fail report
├── requirements.txt             # pinned deps for reproducibility (optional but good practice)
└── README.md                    # with <!-- badges-start --> / <!-- badges-end --> markers
```

### Pattern 1: Command Markdown Invokes Python Script
**What:** Command `.md` files use `allowed-tools: Bash(python3:*)` and pass `$CLAUDE_PLUGIN_ROOT` to a script.
**When to use:** Any command that needs real computation, not just LLM instructions.
**Example (from mississauga-permits):**
```markdown
---
description: Install Python runtime dependencies for meta-compiler
argument-hint: [--force]
allowed-tools: Bash(python3:*)
---

Run the setup script to install all required Python dependencies.

Execute:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/setup_runtime.py ${ARGUMENTS}
```

Report the output to the user. If errors occur, show the actionable fix hint from the script output.
```

### Pattern 2: uv/pip Detection and Venv Creation
**What:** Python script checks `shutil.which("uv")`, creates venv, installs deps.
**When to use:** model:setup exclusively.

```python
# Source: established Python stdlib pattern
import shutil, subprocess, sys, os
from pathlib import Path

def get_venv_path(plugin_root: str) -> Path:
    candidate = Path(plugin_root) / ".venv"
    # Test writability
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        test = candidate / ".write_test"
        test.touch(); test.unlink()
        return candidate
    except OSError:
        fallback = Path.home() / ".claude" / "meta-compiler" / ".venv"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback

def create_venv(venv_path: Path):
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

def install_deps(venv_path: Path, packages: list[str], use_uv: bool):
    python = str(venv_path / "bin" / "python")
    if use_uv:
        cmd = ["uv", "pip", "install", "--python", python] + packages
    else:
        cmd = [python, "-m", "pip", "install"] + packages
    subprocess.run(cmd, check=True)
```

### Pattern 3: Idempotency Check via importlib.metadata
**What:** Check installed version before installing; report "already installed" vs "newly installed".
**When to use:** model:setup, called on every dep before install attempt.

```python
# Source: Python stdlib importlib.metadata
from importlib.metadata import version, PackageNotFoundError

def check_installed(package: str) -> str | None:
    """Returns version string if installed, None if not."""
    try:
        return version(package)
    except PackageNotFoundError:
        return None
```

Note: `importlib.metadata` must be called with the venv's Python to check venv packages, not the system Python. Use `subprocess.run([venv_python, "-c", "import importlib.metadata; ..."])` or activate the venv before running.

### Pattern 4: plugin.json Schema
**What:** Minimal required fields confirmed from existing plugins.
**Example:**
```json
{
  "name": "meta-compiler",
  "version": "0.1.0",
  "description": "...",
  "author": { "name": "Reggie Chan" },
  "keywords": ["optimization", "compiler", "or-tools", "z3", "cp-sat"],
  "license": "MIT",
  "commands": ["./commands"]
}
```

### Pattern 5: model:doctor Pass/Fail Output
**What:** Terse per-dep check with version + actionable fix hint on failure.
**Recommended format (Claude's discretion -- terse):**
```
meta-compiler runtime health check
===================================
[PASS] python        3.13.7
[PASS] pydantic      2.6.1
[PASS] jinja2        3.1.4
[FAIL] ortools       NOT FOUND  →  run: model:setup
[FAIL] z3-solver     NOT FOUND  →  run: model:setup
[PASS] scipy         1.13.0

Result: 2 missing. Run `model:setup` to fix.
```

### Anti-Patterns to Avoid
- **Requiring uv:** Never exit with an error if uv is absent -- always fall back to pip. Locked decision.
- **System Python pollution:** Never install packages to system Python. Always create and use the venv.
- **Hardcoded venv path only:** The plugin cache is read-only on cached installs -- the writable fallback path is required by design.
- **Non-idempotent setup:** Running model:setup twice must be safe. Check before installing.
- **Badges without markers:** Per CLAUDE.md, badges MUST be inside `<!-- badges-start -->` / `<!-- badges-end -->` markers. Placing badges outside markers breaks the `/update-badges` command.
- **Wrong install instructions in README:** CLAUDE.md is explicit -- use the two-step marketplace install, never `claude plugin add /path/to/...`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Package version detection | Custom file parsing | `importlib.metadata.version()` | Handles editable installs, namespace packages, all edge cases |
| venv creation | Manual directory scaffolding | `python -m venv` | Stdlib, cross-platform, handles pip bootstrap |
| Package installation | Custom download logic | uv or pip | Dependency resolution is genuinely complex |
| PATH detection | Manual `$PATH` parsing | `shutil.which()` | Handles PATH edge cases, symlinks, OS differences |
| Write permission test | `os.access(path, os.W_OK)` | Try/except with actual write | `os.access` has known TOCTOU issues; try/except is authoritative |

**Key insight:** The Python packaging ecosystem has many edge cases. Use stdlib and established tools for all runtime management tasks.

---

## Common Pitfalls

### Pitfall 1: Checking Package Installation Against System Python
**What goes wrong:** `importlib.metadata.version("ortools")` in the setup script runs against the system Python, not the venv. Reports "NOT FOUND" even after successful venv install.
**Why it happens:** The setup script itself runs in system Python via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/...`. The venv Python is separate.
**How to avoid:** Use `subprocess.run([str(venv_python), "-c", "import importlib.metadata; print(importlib.metadata.version('ortools'))"])` to query the venv Python. Or run doctor.py directly from the venv Python.
**Warning signs:** model:doctor always reports FAIL even after successful model:setup.

### Pitfall 2: $CLAUDE_PLUGIN_ROOT Not Set in All Contexts
**What goes wrong:** Command markdown uses `${CLAUDE_PLUGIN_ROOT}` but it's empty or unset in some execution contexts, causing the script path to resolve incorrectly.
**Why it happens:** Plugin root injection may not happen in all Claude Code versions or invocation modes.
**How to avoid:** In the Python script, fallback to `Path(__file__).parent.parent` (the plugin root relative to the script's own location). The script knows where it is.
**Warning signs:** `python3 /scripts/setup_runtime.py` (leading slash with missing root).

### Pitfall 3: Venv Already Exists but is Broken
**What goes wrong:** `model:setup --force` is needed but not implemented. A partial venv from a failed previous run prevents clean reinstall.
**Why it happens:** `python -m venv` is a no-op if the directory exists. A broken venv silently persists.
**How to avoid:** Implement a `--force` flag that deletes and recreates the venv directory before installing.
**Warning signs:** model:doctor reports deps as present but importing them fails.

### Pitfall 4: uv pip vs uv venv Syntax
**What goes wrong:** `uv pip install` requires `--python` flag when not in an active venv context; omitting it installs to uv's default environment rather than the plugin venv.
**Why it happens:** uv has its own environment management separate from the standard venv.
**How to avoid:** Always pass `--python "${VENV}/bin/python"` when calling `uv pip install` from outside the venv.
**Warning signs:** Packages install without error but `model:doctor` still reports them missing.

### Pitfall 5: ortools Package Name vs Import Name
**What goes wrong:** The PyPI package is `ortools` but the import is `from ortools.sat.python import cp_model`. importlib.metadata key is `ortools`. These are consistent but worth noting.
**Why it happens:** Not a pitfall per se -- just verify the metadata key matches the install name.
**How to avoid:** Use `importlib.metadata.version("ortools")` for version check. The distribution name matches the install name.

---

## Code Examples

### Writable Path Detection
```python
# Source: Python stdlib try/except pattern (HIGH confidence)
from pathlib import Path

def get_venv_path(plugin_root: str) -> Path:
    candidate = Path(plugin_root) / ".venv"
    try:
        candidate.parent.mkdir(parents=True, exist_ok=True)
        probe = candidate.parent / ".write_probe"
        probe.touch()
        probe.unlink()
        return candidate
    except (OSError, PermissionError):
        fallback = Path.home() / ".claude" / "meta-compiler" / ".venv"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
```

### Idempotent Install Loop
```python
# Source: importlib.metadata stdlib (HIGH confidence)
import subprocess
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

PACKAGES = ["ortools", "z3-solver", "scipy", "pydantic", "jinja2"]

def check_in_venv(venv_python: Path, package: str) -> str | None:
    result = subprocess.run(
        [str(venv_python), "-c",
         f"import importlib.metadata; print(importlib.metadata.version('{package}'))"],
        capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None

def setup(venv_python: Path, use_uv: bool):
    already, to_install = [], []
    for pkg in PACKAGES:
        ver = check_in_venv(venv_python, pkg)
        if ver:
            already.append(f"{pkg}=={ver}")
        else:
            to_install.append(pkg)

    for pkg in already:
        print(f"[SKIP] {pkg} -- already installed")

    if to_install:
        print(f"[INSTALL] {', '.join(to_install)}")
        if use_uv:
            subprocess.run(["uv", "pip", "install", "--python", str(venv_python)] + to_install, check=True)
        else:
            subprocess.run([str(venv_python), "-m", "pip", "install"] + to_install, check=True)
```

### Badge Block Format (from repo conventions)
```markdown
# Meta-Compiler Plugin

<!-- badges-start -->
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/reggiechan74/cc-plugins/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-yellow)](https://www.python.org)
[![Claude Code Plugin](https://img.shields.io/badge/Claude_Code-plugin-blueviolet)](https://claude.ai/claude-code)
<!-- badges-end -->
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pip` only for package management | `uv` as primary, pip as fallback | 2023-2024 | uv is 10-100x faster for resolution; no behavior change for users |
| `pkg_resources` for version detection | `importlib.metadata` | Python 3.8+ | pkg_resources is deprecated; importlib.metadata is stdlib |
| Global Python installs | Per-project venv | Best practice since Python 3.3 | Isolation; no system pollution |

**Deprecated/outdated:**
- `pkg_resources.get_distribution()`: Replaced by `importlib.metadata.version()`. Do not use.
- `distutils`: Removed in Python 3.12. Do not use.

---

## Open Questions

1. **Does Claude Code guarantee `$CLAUDE_PLUGIN_ROOT` is set in all command execution contexts?**
   - What we know: `mississauga-permits` uses `${CLAUDE_PLUGIN_ROOT}/scripts/fetch_permits.py` and it works
   - What's unclear: Whether it's always set or only in marketplace-installed plugin contexts
   - Recommendation: Implement a `Path(__file__).parent.parent` fallback in setup_runtime.py as defensive measure

2. **Should model:setup emit a requirements.txt lockfile?**
   - What we know: No existing plugin in this repo does this; it is not required by CONTEXT.md
   - What's unclear: Whether Phase 2 will need reproducible builds
   - Recommendation: Defer to Phase 2; model:setup for Phase 1 is install-only

3. **z3-solver install time on CI/fresh systems**
   - What we know: z3-solver is a large binary package; install can take 1-3 minutes
   - What's unclear: Whether users will find this acceptable without a progress indicator
   - Recommendation: Stream pip/uv output live rather than buffering; addresses the CONTEXT.md "progress display" discretion item

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None detected -- no test infrastructure in repo |
| Config file | None -- Wave 0 must establish |
| Quick run command | `python3 -m pytest meta-compiler/tests/ -x -q` (once created) |
| Full suite command | `python3 -m pytest meta-compiler/tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | model:setup installs all 5 deps into venv | smoke | `python3 -m pytest meta-compiler/tests/test_setup.py -x` | Wave 0 |
| INFRA-01 | model:setup is idempotent (run twice = safe) | unit | `python3 -m pytest meta-compiler/tests/test_setup.py::test_idempotent -x` | Wave 0 |
| INFRA-01 | model:setup falls back to pip when uv absent | unit | `python3 -m pytest meta-compiler/tests/test_setup.py::test_pip_fallback -x` | Wave 0 |
| INFRA-01 | model:setup uses fallback venv path when plugin root not writable | unit | `python3 -m pytest meta-compiler/tests/test_setup.py::test_venv_fallback -x` | Wave 0 |
| INFRA-02 | model:doctor reports PASS for installed deps | unit | `python3 -m pytest meta-compiler/tests/test_doctor.py::test_pass -x` | Wave 0 |
| INFRA-02 | model:doctor reports FAIL with fix hint for missing deps | unit | `python3 -m pytest meta-compiler/tests/test_doctor.py::test_fail -x` | Wave 0 |
| INFRA-03 | plugin.json has required fields: name, version, commands | unit | `python3 -m pytest meta-compiler/tests/test_plugin_json.py -x` | Wave 0 |
| INFRA-04 | README has badge markers and minimum 3 badges | unit | `python3 -m pytest meta-compiler/tests/test_readme.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python3 -m pytest meta-compiler/tests/ -x -q`
- **Per wave merge:** `python3 -m pytest meta-compiler/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `meta-compiler/tests/__init__.py` -- package init
- [ ] `meta-compiler/tests/test_setup.py` -- covers INFRA-01
- [ ] `meta-compiler/tests/test_doctor.py` -- covers INFRA-02
- [ ] `meta-compiler/tests/test_plugin_json.py` -- covers INFRA-03
- [ ] `meta-compiler/tests/test_readme.py` -- covers INFRA-04
- [ ] Framework install: `pip install pytest` -- no pytest detected in repo

---

## Sources

### Primary (HIGH confidence)
- Repo: `/home/reggiechan/cc-plugins/mississauga-permits/` -- command markdown invoking Python scripts via `${CLAUDE_PLUGIN_ROOT}`
- Repo: `/home/reggiechan/cc-plugins/code-coherence/.claude-plugin/plugin.json` -- plugin.json schema
- Repo: `/home/reggiechan/cc-plugins/course-curriculum-creator/.claude-plugin/plugin.json` -- commands field pattern
- Repo: `/home/reggiechan/cc-plugins/.claude/commands/update-badges.md` -- badge marker spec, badge color reference
- Repo: `/home/reggiechan/cc-plugins/structured-english/README.md` -- canonical badge block example
- Repo: `/home/reggiechan/cc-plugins/CLAUDE.md` -- two-step install mandate, badge marker mandate
- Python stdlib docs: `importlib.metadata`, `venv`, `shutil.which`, `subprocess`

### Secondary (MEDIUM confidence)
- Repo: `/home/reggiechan/cc-plugins/google-workspace-mcp/` -- plugin with external runtime (Node.js); confirms `${CLAUDE_PLUGIN_ROOT}` pattern but Node, not Python
- uv documentation (knowledge): uv pip install `--python` flag for targeting specific Python executables

### Tertiary (LOW confidence)
- uv install time benchmarks: claimed 10-100x faster than pip for fresh installs; not independently verified against these specific packages on this platform

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all packages are stdlib or locked by CONTEXT.md; plugin.json schema confirmed from repo
- Architecture: HIGH -- command markdown + Python script pattern confirmed from mississauga-permits; venv pattern is standard Python
- Pitfalls: HIGH for venv/importlib pitfalls (reproducible from Python docs); MEDIUM for $CLAUDE_PLUGIN_ROOT edge cases (single source)

**Research date:** 2026-03-09
**Valid until:** Stable -- cc-plugins conventions and Python stdlib are not fast-moving. Re-check if Claude Code plugin system changes.
