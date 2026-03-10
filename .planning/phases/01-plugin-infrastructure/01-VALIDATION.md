---
phase: 1
slug: plugin-infrastructure
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Wave 0 installs) |
| **Config file** | none — Wave 0 establishes |
| **Quick run command** | `python3 -m pytest meta-compiler/tests/ -x -q` |
| **Full suite command** | `python3 -m pytest meta-compiler/tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest meta-compiler/tests/ -x -q`
- **After every plan wave:** Run `python3 -m pytest meta-compiler/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 0 | INFRA-01 | unit | `python3 -m pytest meta-compiler/tests/test_setup.py -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 0 | INFRA-01 | unit | `python3 -m pytest meta-compiler/tests/test_setup.py::test_idempotent -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 0 | INFRA-01 | unit | `python3 -m pytest meta-compiler/tests/test_setup.py::test_pip_fallback -x` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01 | 0 | INFRA-01 | unit | `python3 -m pytest meta-compiler/tests/test_setup.py::test_venv_fallback -x` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 0 | INFRA-02 | unit | `python3 -m pytest meta-compiler/tests/test_doctor.py::test_pass -x` | ❌ W0 | ⬜ pending |
| 1-02-02 | 02 | 0 | INFRA-02 | unit | `python3 -m pytest meta-compiler/tests/test_doctor.py::test_fail -x` | ❌ W0 | ⬜ pending |
| 1-03-01 | 03 | 1 | INFRA-03 | unit | `python3 -m pytest meta-compiler/tests/test_plugin_json.py -x` | ❌ W0 | ⬜ pending |
| 1-04-01 | 04 | 1 | INFRA-04 | unit | `python3 -m pytest meta-compiler/tests/test_readme.py -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `meta-compiler/tests/__init__.py` — package init
- [ ] `meta-compiler/tests/test_setup.py` — stubs for INFRA-01 (setup, idempotent, pip_fallback, venv_fallback)
- [ ] `meta-compiler/tests/test_doctor.py` — stubs for INFRA-02 (pass, fail with hint)
- [ ] `meta-compiler/tests/test_plugin_json.py` — stubs for INFRA-03 (required fields)
- [ ] `meta-compiler/tests/test_readme.py` — stubs for INFRA-04 (badge markers, min 3 badges)
- [ ] `pip install pytest` — no pytest detected in repo

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Two-step marketplace install works end-to-end | INFRA-03 | Requires live Claude Code runtime | Run `/plugin marketplace add reggiechan74/cc-plugins` then `/plugin install meta-compiler@cc-plugins` and confirm listed |
| `model:setup` installs real venv with working imports | INFRA-01 | Smoke test requires actual Python subprocess execution | Run `model:setup`, then verify `import torch` in venv Python works |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
