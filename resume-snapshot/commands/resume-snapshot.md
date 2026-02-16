---
description: Generate a portfolio-ready repository snapshot for resume/job documentation
argument-hint: "--output FILE"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
---

Generate a professional portfolio-quality summary of the current git repository. The output is a markdown document suitable for GitHub portfolio READMEs, job applications, and technical interviews.

**Parse arguments from:** `$ARGUMENTS`

If `--output` is specified, use that file path. Otherwise write to `RESUME_SNAPSHOT.md` in the repository root.

---

## Phase 1: Collect Repository Metadata

Run ALL of the following bash commands. Capture every output — you will need it all for synthesis.

**1a. Git metadata:**

```bash
echo "@@REPO_ROOT@@" && basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" && \
echo "@@REMOTE_URL@@" && git remote get-url origin 2>/dev/null || echo "no-remote" && \
echo "@@DEFAULT_BRANCH@@" && git branch --show-current 2>/dev/null && \
echo "@@TOTAL_COMMITS@@" && git rev-list --count HEAD 2>/dev/null && \
echo "@@FIRST_COMMIT@@" && git log --reverse --format='%ai' 2>/dev/null | head -1 && \
echo "@@LAST_COMMIT@@" && git log -1 --format='%ai' 2>/dev/null && \
echo "@@TAGS@@" && git tag --sort=-v:refname 2>/dev/null | head -5 && \
echo "@@CONTRIBUTORS@@" && git shortlog -sn --no-merges 2>/dev/null | head -10 && \
echo "@@RECENT_COMMITS@@" && git log --oneline -25 2>/dev/null
```

**1b. File statistics (by extension):**

```bash
echo "@@EXT_COUNTS@@" && \
find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/target/*' -not -path '*/.next/*' -not -path '*/.cache/*' -not -path '*/cache/*' -not -name '*.pyc' | grep '\.' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -25 && \
echo "@@TOTAL_FILES@@" && \
find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/__pycache__/*' | wc -l
```

**1c. Directory tree:**

```bash
tree -L 3 -I 'node_modules|.git|__pycache__|.venv|venv|dist|build|target|.next|.cache|cache|*.pyc' --dirsfirst 2>/dev/null || find . -type d -not -path '*/.git/*' -maxdepth 3 | sort
```

**1d. Lines of code by language** (use whichever is available):

```bash
scc --no-cocomo --no-complexity -s code 2>/dev/null || \
(echo "@@LOC_FALLBACK@@" && \
for ext in py js ts tsx jsx go rs java rb cpp c cs swift kt sh sql md json yaml yml toml; do
  count=$(find . -name "*.$ext" -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -exec cat {} + 2>/dev/null | wc -l)
  [ "$count" -gt 0 ] && echo "  .$ext: $count lines"
done)
```

**1e. Infrastructure and tooling detection:**

```bash
echo "@@CI_CD@@" && ls -1 .github/workflows/*.yml .github/workflows/*.yaml 2>/dev/null; \
echo "@@INFRA@@" && ls -1 Makefile Dockerfile docker-compose.yml docker-compose.yaml Jenkinsfile .gitlab-ci.yml .travis.yml .circleci/config.yml Procfile Vagrantfile 2>/dev/null; \
echo "@@QUALITY@@" && ls -1 .eslintrc* .prettierrc* tsconfig.json jest.config.* vitest.config.* pytest.ini setup.cfg tox.ini .flake8 mypy.ini .pre-commit-config.yaml biome.json 2>/dev/null; \
echo "@@LICENSE@@" && ls -1 LICENSE* LICENCE* license* licence* 2>/dev/null && head -3 LICENSE* LICENCE* 2>/dev/null; \
echo "@@TESTS@@" && find . -type f \( -name '*test*' -o -name '*spec*' -o -name '*_test.*' \) -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/__pycache__/*' -not -name '*.pyc' 2>/dev/null | head -20 && \
echo "TEST_COUNT:" && find . -type f \( -name '*test*' -o -name '*spec*' -o -name '*_test.*' \) -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/__pycache__/*' -not -name '*.pyc' 2>/dev/null | wc -l
```

**1f. Complexity hotspots:**

```bash
echo "@@TOP_FILES_BY_SIZE@@" && \
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.rb' -o -name '*.cpp' -o -name '*.c' \) \
  -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/target/*' -not -path '*/.next/*' \
  -exec wc -l {} + 2>/dev/null | sort -rn | head -16 && \
echo "@@FUNCTION_COUNTS@@" && \
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.rb' \) \
  -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/dist/*' -not -path '*/build/*' \
  -exec sh -c 'count=$(grep -cE "^\s*(def |function |const \w+ = |async function |func |fn |public |private |protected )" "$1" 2>/dev/null); [ "$count" -gt 0 ] && echo "  $count $1"' _ {} \; 2>/dev/null | sort -rn | head -15 && \
echo "@@DEEP_NESTING@@" && \
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.go' -o -name '*.rs' -o -name '*.java' \) \
  -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/dist/*' \
  -exec sh -c 'max=$(awk "{ match(\$0, /^[[:space:]]*/); len=RLENGTH; if(len>max) max=len } END { print max+0 }" "$1" 2>/dev/null); [ "$max" -gt 16 ] && echo "  depth:$max $1"' _ {} \; 2>/dev/null | sort -t: -k2 -rn | head -10
```

---

## Phase 2: Read Key Files

Use the **Read** tool to read each of these (skip any that don't exist):

1. **README** — `README.md`, `README.rst`, or `README.txt` (whichever exists)
2. **Primary dependency manifest** — read the FIRST one found:
   - `package.json`
   - `requirements.txt`
   - `pyproject.toml`
   - `Cargo.toml`
   - `go.mod`
   - `Gemfile`
   - `pom.xml`
   - `build.gradle` / `build.gradle.kts`
   - `mix.exs`
3. **Changelog** — `CHANGELOG.md` or `CHANGES.md` (first 80 lines only)
4. **Config/manifest files** that reveal architecture — e.g., `plugin.json`, `tsconfig.json`, `Dockerfile`, CI workflow files

Use **Glob** to find the 5 largest source code files (by common extensions: `.py`, `.js`, `.ts`, `.go`, `.rs`, `.java`, `.rb`, `.cpp`, `.c`). Read the first 60 lines of each to understand architectural patterns and coding style.

---

## Phase 3: Synthesize Portfolio Entry

Using ALL collected data, generate a portfolio entry in this **exact structure**:

```markdown
### [repo-name](github-url) <emoji>
**Status**: <status> | **License**: <license> | **Commits**: <count>

<1-2 paragraph description of what the project does and why it matters.
Be specific about the problem it solves and who benefits.>

**Technical Architecture**:
- **<Pattern Name>**: <specific details with numbers where possible>
- **<Pattern Name>**: <specific details>
- ...continue as warranted by project complexity

**Technical Sophistication**:
- **<N> <Language> <files/scripts>**: <total KB/LOC> across <module descriptions>
- **<Notable technical achievement>**: <specifics>
- **<Integration points>**: <external systems, APIs, protocols>
- **<Quality indicators>**: <testing, CI/CD, types, linting, etc.>
- **Production Features**: <config management, logging, error handling, caching, etc.>

**Skills Demonstrated**:
- <Skill 1> (<qualifier: beginner/intermediate/advanced — based on code evidence>)
- <Skill 2>
- ...only list skills with EVIDENCE in the codebase

**Business Impact**:
- <Concrete value delivered or problem solved>
- <Scale/performance characteristics if observable>
- <Cost savings, time savings, or efficiency gains — infer conservatively>
- <Target users or use cases>

**Development Approach**:
<1 paragraph synthesizing: development timeline (from first/last commit dates),
iteration cadence (from commit density), solo vs. collaborative (from contributors),
development methodology signals (from commit messages, branching, CI/CD), and
any AI-assisted development indicators (from commit messages or tooling).>
```

### Synthesis Rules

**Be honest — only claim what the code evidence supports:**
- Do NOT inflate metrics or capabilities
- Do NOT fabricate business impact numbers that aren't in the README
- If a section has insufficient data, say so briefly rather than guessing

**Be specific — numbers beat adjectives:**
- "20 Python scripts, 12K LOC across 5 modules" > "multiple scripts"
- "Queries 406 API endpoints across 50 municipalities" > "queries many APIs"
- "4-phase pipeline: text → spatial → provincial → scoring" > "multi-step pipeline"

**Status detection heuristics:**
- Version tags present (v1.x+) → "Production (vX.Y.Z)"
- Version tags present (v0.x) → "Beta (v0.X.Y)"
- CI/CD configured + tests → "Active Development"
- No tags, no CI → "Prototype" or "In Development"
- README mentions "WIP" or "experimental" → "Experimental"

**License detection:**
- Read from LICENSE file header, `package.json` license field, or `pyproject.toml` license field
- If no license found → "Unlicensed"

**Emoji selection** — pick ONE that best represents the project:
- 🏆 Production/polished project
- 🚀 Active/growing project
- 🔧 Developer tool / utility
- 🗺️ Data/GIS/mapping project
- 🤖 AI/ML project
- 📊 Analytics/data science
- 🌐 Web application
- 📦 Library/package
- 🔒 Security tool
- 🧪 Experimental/research

**Skills qualification:**
- "advanced" — deep usage: custom implementations, complex patterns, performance tuning
- "intermediate" — solid usage: multiple modules, proper patterns, error handling
- "beginner" — basic usage: simple scripts, standard patterns, minimal complexity

---

## Phase 4: Write Output

Write the synthesized portfolio entry to the output file using the **Write** tool.

After writing, display a brief summary to the user:
- Output file path and size
- Key stats: commits, primary language, file count
- Any sections where data was limited and manual review is recommended
