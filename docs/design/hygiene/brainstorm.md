# /hygiene — Codebase Entropy Scanner

Mechanical scan that finds dead code, doc drift, convention violations, and accumulated entropy. Produces a structured report with specific actions. Local-first, multi-lens, language-agnostic. Fast, run-it-often (weekly, after cleanups).

**Not preflight** (pre-push gate for secrets/tests). Not code-review (per-file bug hunting). Hygiene is a periodic audit: "has entropy accumulated?"

**Implementation:** Create `skills/hygiene/SKILL.md`. Frontmatter: `name: hygiene`, `description: Scan for dead code, doc drift, convention violations, and accumulated entropy`, `origin: personal`, `user-invocable: true`, `allowed-tools: [Read, Grep, Glob, Bash]`, `argument-hint: "[directory]"`. Add to `environment.md` skills table, `README.md` skills list.

## The 12 Lenses

| # | Lens | What it catches |
|---|------|----------------|
| 1 | Dead code | Unreferenced files, unused functions, orphan imports |
| 2 | Doc drift | Claims in docs that don't match reality |
| 3 | Dead dependencies | Declared but never imported packages |
| 4 | Orphaned artifacts | Build debris, stale symlinks, leftover dirs |
| 5 | Convention violations | Established patterns not followed |
| 6 | Stale planning | Roadmap items going nowhere, aged TODOs |
| 7 | Gitignore gaps | Files that should be ignored but aren't |
| 8 | Broken references | Internal links, file paths, URLs pointing to nothing |
| 9 | Consistency drift | Line endings, formatting, naming pattern deviations |
| 10 | Reducible complexity | Dead indirection, duplicate code, over-long functions, deep nesting |
| 11 | Test health | Skipped tests, empty test files, coverage decay signals |
| 12 | Churn hotspots | High-complexity files that change frequently — maintenance magnets |

---

### 1. Dead code
**Description:** Files, functions, or imports that nothing references. Entropy accumulates as features get removed but their support code stays behind.

**Detection:**
- Glob all source files; for each, grep the rest of the codebase for imports/references
- Check if file is an entry point (main, CLI, hook, skill) or listed in a manifest
- For functions: grep for the function name outside its own file
- Delegate to native tools when available: `vulture` (Python), `knip` (JS/TS), `go vet` (Go) — use their output as high-confidence signals, fall back to grep-based heuristics for languages without tooling

**Severity:**
- `DEAD` — zero references anywhere
- `MAYBE` — only referenced in one place (could be over-abstraction)

**Example finding:** `src/old_handler.py` — entire file unreferenced. Not imported, not an entry point, not in any manifest.

**Action format:** `Action: Delete file.` or `Action: Confirm if awaiting use or dead.`

---

### 2. Doc drift
**Description:** Concrete claims in documentation that no longer match reality. Goes deeper than preflight's doc-freshness check — line-level references, not just "does the file exist."

**Detection:**
- Parse README.md, CLAUDE.md, ROADMAP.md, environment.md for concrete claims: directory names, CLI commands/flags, file paths, feature descriptions
- Cross-reference each claim against reality (Glob for dirs, Grep for references, Read for content)
- Check that code examples in docs actually work / reference real APIs
- Check install/setup instructions — do the listed commands still work? Do referenced scripts exist?
- Check README badges (CI status, coverage, version) — do the badge URLs still resolve? Do they point to the right branch?

**Severity:**
- `DRIFT` — claim is provably wrong (path doesn't exist, flag was removed)
- `STALE` — claim is outdated but not technically wrong (version number, count)

**Example finding:** README.md:15 says "See agents/ for autonomous workflows" but `agents/` directory does not exist.

**Action format:** `Action: Remove reference from README.` or `Action: Update claim to match current state.`

---

### 3. Dead dependencies
**Description:** Packages declared in a manifest but never imported or used in source code. Adds install weight, audit surface, and confusion.

**Detection:**
- Read package manifest (package.json / requirements.txt / go.mod / Cargo.toml)
- Grep for actual import/usage of each dependency in source files
- Exclude: dev/build tools (webpack, vite, pytest), type-only packages (@types/*), runtime-implicit deps
- Prefer native tools when available: `go mod tidy -diff` (Go), `deptry` (Python), `knip` (JS/TS) — these understand dynamic imports, aliases, and framework conventions that grep misses
- Fall back to grep-based heuristics for languages without native tooling

**Severity:**
- `DEAD` — declared, never imported anywhere
- `MAYBE` — imported only in commented-out code or dead files

**Example finding:** `package.json` declares `lodash` but no source file imports it.

**Action format:** `Action: Remove from package.json and run install.`

---

### 4. Orphaned artifacts
**Description:** Build debris, untracked directories, stale symlinks, and leftover files that should have been cleaned up. Classic example: `git rm -rf` removes tracked files but leaves untracked subdirs behind.

**Detection:**
- Find `__pycache__/`, `.pyc`, `node_modules/` in unexpected locations, empty directories
- `git ls-files --others --exclude-standard` for untracked files that look like build output
- Check for stale symlinks/junctions whose targets no longer exist
- Stale config leftovers: `docker-compose.override.yml`, `.env.local`, `*.bak`, `*.orig` — local experiment debris that never got cleaned up
- Large binary files committed to git (images, zips, compiled binaries) — `git ls-files` + check file sizes
- Leftover merge/rebase artifacts: `.orig` files from conflict resolution

**Severity:**
- `ORPHAN` — clearly leftover, safe to delete
- `CHECK` — untracked but might be intentional (local config, scratch files)

**Example finding:** `mcp-servers/__pycache__/` — left behind after `git rm -rf mcp-servers/`. Contains .pyc files.

**Action format:** `Action: Delete directory, add __pycache__/ to .gitignore if missing.`

---

### 5. Convention violations
**Description:** The project has established patterns (docstrings on public functions, decision records in `docs/decisions/`, manifest entries for every skill). This lens catches places where the pattern exists but isn't followed.

**Detection:**
- If CLAUDE.md declares conventions, check each one mechanically:
  - "Every skill has a SKILL.md" → Glob `skills/*/SKILL.md`, compare against `skills/*/`
  - "Decision records in docs/decisions/" → check the directory exists, files follow `NNNN-short-title.md` naming
- If project uses docstrings: grep for public function defs missing docstrings
- If environment.md is a manifest: compare declared items against actual files (superset of old "manifest drift" check)
- Repo hygiene basics: LICENSE file present? CONTRIBUTING guide if it's an open-source project? .editorconfig or format config?
- Release hygiene: any git tags? If project has a version in package manifest, does a matching tag exist?

**Severity:**
- `VIOLATION` — convention clearly documented, clearly not followed
- `GAP` — convention implied but not explicitly documented (suggest documenting it)

**Example finding:** 8 public functions in `hooks/format_code.py` and `hooks/preflight_check.py` missing docstrings. Project convention (CLAUDE.md) says public functions should have docstrings.

**Action format:** `Action: Add docstrings to listed functions.` or `Action: Add missing entry to environment.md manifest.`

---

### 6. Stale planning
**Description:** Roadmap items, TODOs, and FIXMEs that have gone stale. "Next" items that are actually blocked or speculative. Planning docs that reference completed or abandoned work.

**Detection:**
- Read ROADMAP.md: check "Next" items — are they actually actionable or stuck?
- Grep for `TODO`, `FIXME`, `HACK`, `XXX` across codebase — check age via `git log` on those lines
- Check brainstorm files in `docs/design/` — do they reference initiatives that shipped or were abandoned?

**Severity:**
- `STALE` — item has been in "Next" for multiple cycles with no progress
- `AGED` — TODO/FIXME older than a configurable threshold (default: 90 days)

**Example finding:** ROADMAP.md lists 3 items under "Next" that are blocked or speculative: `/mcp-registry`, `hook: auto-commit`, `prompt: project-docs improvements`. None have active brainstorms or recent commits.

**Action format:** `Action: Move to "Later" or remove from roadmap.` or `Action: Resolve or remove TODO at file:line.`

---

### 7. Gitignore gaps
**Description:** Files showing up in `git status` that shouldn't be tracked, or common patterns missing from `.gitignore`. Causes noise in every status/diff and risks committing local-only files.

**Detection:**
- `git status --porcelain` — look for untracked files that match known ignore patterns (log files, dist dirs, IDE configs, local settings)
- Check `.gitignore` against a baseline of common patterns for the project's languages/tools:
  - Python: `__pycache__/`, `*.pyc`, `.venv/`, `dist/`
  - Node: `node_modules/`, `dist/`, `.env`
  - General: `*.log`, `debug.log`, `.DS_Store`, `Thumbs.db`
- Check for `.claude/settings.local.json` and similar local config files

**Severity:**
- `MISSING` — common pattern not in .gitignore and matching files exist
- `NOISE` — untracked file showing in status that looks like it should be ignored

**Example finding:** `.gitignore` missing entries for `debug.log` and `dist/`. Untracked `.claude/settings.local.json` appears in every `git status`.

**Action format:** `Action: Add pattern to .gitignore.` or `Action: Add to .gitignore and git rm --cached if already tracked.`

---

### 8. Broken references
**Description:** Internal links, file paths, and anchors that point to nothing. Docs link to files that moved; brainstorms reference initiatives that don't exist yet; code comments cite removed functions.

**Detection:**
- In markdown files: extract `[text](path)` links, check if target exists
- In markdown files: extract `[text](#anchor)` links, check if heading exists
- In brainstorm/design docs: check references to other design docs or files
- In code comments: extract file paths and function references, verify they exist
- CI/CD badge URLs in README — do they point to the right repo/branch? Do the linked services still exist?
- Build scripts and Makefiles: do referenced commands, paths, and scripts still exist?

**Severity:**
- `BROKEN` — target definitely doesn't exist
- `SUSPECT` — target exists but content doesn't match what the reference implies

**Example finding:** `docs/design/hygiene/brainstorm.md` links to `docs/design/mcp-registry/brainstorm.md` which doesn't exist.

**Action format:** `Action: Fix link target or remove broken reference.`

---

### 9. Consistency drift
**Description:** Mixed conventions within the same codebase — line endings, indentation styles, naming patterns, file organization. Often invisible until it causes real problems (CRLF diffs, merge conflicts, linter disagreements).

**Detection:**
- Check line endings: `git ls-files | xargs file` or `git diff --check` for mixed CRLF/LF
- Check for `.editorconfig` or format config — if present, verify files comply
- Compare naming patterns within directories (camelCase vs snake_case files, inconsistent prefixes)
- Look for mixed indentation (tabs vs spaces) in same-language files
- Check for leftover merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) — surprisingly common in repos
- Check for BOM markers in files that shouldn't have them

**Severity:**
- `INCONSISTENT` — mixed conventions in same directory or file type
- `WARN` — no enforced standard exists (suggest adding one)

**Example finding:** CRLF line endings in 12 files while rest of repo uses LF. Causes warnings on every commit.

**Action format:** `Action: Normalize line endings to LF and add .gitattributes rule.` or `Action: Add .editorconfig with project standard.`

---

### 10. Reducible complexity
**Description:** Code that can be simplified without changing behavior. Covers two categories: **dead indirection** (abstractions that don't earn their keep) and **structural bloat** (duplication, over-long functions, deep nesting). Both are mechanically detectable and signal that entropy has accumulated.

**Detection — dead indirection:**
- Find functions/classes called from exactly one place — are they earning the indirection?
- Find config files/constants that hold only default values never overridden
- Find wrapper functions that just forward to another function with no transformation
- Find abstract base classes or interfaces with exactly one implementation

**Detection — structural bloat:**
- Find functions over a size threshold (e.g., >50 lines) — candidates for extraction
- Find files over a size threshold (e.g., >300 lines) — candidates for splitting
- Find duplicate or near-duplicate code blocks across files (identical logic, different variable names)
- Find deeply nested conditionals (>3 levels) — candidates for early returns or extraction
- Find repeated patterns that could be a shared utility (3+ occurrences of same structure)

**Severity:**
- `REDUNDANT` — wrapper/abstraction adds no value, can be inlined
- `DUPLICATE` — same logic appears in multiple places, should be consolidated
- `OVERSIZE` — function or file exceeds size threshold, should be split
- `REVIEW` — might be intentional, but worth a look

**Example findings:**
- `helpers/run_command.py` wraps `subprocess.run()` with identical arguments, called from one place. Adds a file and an import for no behavioral difference.
- `hooks/preflight_check.py:check_secrets()` and `hooks/format_code.py:scan_patterns()` contain nearly identical grep-and-report loops — 20 lines duplicated with different variable names.
- `setup.py` is 400 lines with a `main()` function spanning 120 lines.

**Action format:** `Action: Inline function at callsite and delete helper.` or `Action: Extract shared logic into utility.` or `Action: Split function into smaller units.`

---

### 11. Test health
**Description:** Tests that have gone stale, been disabled, or were never real tests. `.skip` and `.only` markers left behind, test files with no assertions, test functions that pass trivially. These accumulate silently because the test suite still "passes."

**Detection:**
- Grep for `.skip`, `.only`, `@pytest.mark.skip`, `@unittest.skip`, `t.Skip()` — disabled tests left in place
- Find test files with no `assert`, `expect`, or equivalent — tests that test nothing
- Find test functions that are empty or contain only setup/logging
- Compare test file names against source files — source files with no corresponding test (if project convention requires tests)

**Severity:**
- `SKIPPED` — test explicitly disabled, no linked issue explaining why
- `EMPTY` — test file or function with no assertions
- `UNCOVERED` — source file has no corresponding test file (when convention expects one)

**Example finding:** `tests/test_setup.py:test_idempotent()` contains `@pytest.mark.skip("flaky")` with no issue link. Has been skipped for 6 months.

**Action format:** `Action: Fix and unskip, or delete if test is obsolete.` or `Action: Add assertions to empty test.`

---

### 12. Churn hotspots
**Description:** Files that are both complex and frequently changed are maintenance magnets — every change risks breaking something, every reviewer has to re-understand tangled logic. This is CodeScene's core insight: complexity alone doesn't matter; complexity *times* churn rate does.

**Detection:**
- `git log --format=format: --name-only --since="90 days"` — count commits per file
- For high-churn files (top 10% by commit count), estimate complexity: line count, function count, nesting depth
- Flag files where churn AND complexity both exceed thresholds
- Also flag files touched by many different authors (knowledge distribution risk)

**Severity:**
- `HOTSPOT` — high churn + high complexity, top priority for refactoring
- `WATCH` — high churn but moderate complexity, or high complexity but low churn

**Example finding:** `setup.py` — 45 commits in 90 days, 400 lines, 8 functions, deepest nesting 4 levels. Touched by 3 contributors.

**Action format:** `Action: Prioritize splitting/simplifying — high churn amplifies complexity cost.` or `Action: Add to watch list for next refactor cycle.`

---

## Execution Model

How the scan runs — not just what it checks but how it stays fast, scopes intelligently, and delegates work.

### Scan modes

Three modes control scope. The goal: make the common case fast so people actually run it.

| Mode | Scope | Use case |
|------|-------|----------|
| `--full` | Entire repo, all 12 lenses | Weekly audit, post-cleanup verification |
| `--changed` | Only files changed since a ref (default: last commit) | After a work session — "did I leave entropy behind?" |
| `--staged` | Only staged files | Pre-commit spot check |

`--changed` should be the default. Full scans are the deliberate choice, not the default. Supports `--since=<commit|tag|branch>` for comparing against arbitrary baselines.

For `--changed` mode: report only NEW findings. Pre-existing findings appear as dimmed/noted context, not as action items. This is SonarQube's "Clean as You Code" insight: focus on not making things worse.

### Native tool delegation

The LLM is the reasoning engine, not the parser. For lenses where language-specific tools exist, delegate the heavy lifting to them and feed their output to the LLM for cross-referencing, explanation, and formatting.

**Strategy:** Check if tool is available (`which vulture`, `which knip`, etc.). If yes, run it and ingest output. If no, fall back to grep/glob heuristics. Never hard-depend on any external tool.

| Language | Dead code | Dead deps | Formatting |
|----------|-----------|-----------|------------|
| Python | `vulture` | `deptry` | `black --check` |
| JS/TS | `knip` | `knip` | `prettier --check` |
| Go | `go vet`, `deadcode` | `go mod tidy -diff` | `gofmt -l` |
| Rust | `cargo udeps` | `cargo udeps` | `cargo fmt --check` |
| Any | grep heuristics | manifest vs import grep | `.editorconfig` check |

This keeps the skill language-agnostic (always works) while being language-aware (better results when native tools are present). The LLM focuses on the lenses no static tool can handle: doc drift, stale planning, convention violations, broken references.

### Performance target

Under 60 seconds for `--changed` on a typical repo. Under 5 minutes for `--full`. If it's slow, people won't run it. Parallelize independent lenses where possible.

---

## Report Intelligence

What makes the report a killer feature — not just a list of findings, but a tool that thinks.

### Delta tracking

Each scan writes a `.hygiene-snapshot.json` to the project root (gitignored). On subsequent runs, the report shows:

```
Hygiene Report — 2024-03-15
============================
Since last scan (2024-03-08): +3 new findings, -2 resolved, 1 worsened

Trajectory: ▲ degrading (net +1)
```

Per-lens trajectory: `Dead code: stable | Doc drift: ▲ degrading | Stale planning: ▼ improving`

**Entropy velocity** = `(new_findings - resolved_findings) / days_elapsed`. Positive = accumulating debt. Negative = paying it down. This single number tells you if you're winning or losing.

### Confidence scoring

Every finding gets a confidence level. This directly addresses the #1 reason devs abandon analysis tools: false positives.

| Confidence | Meaning | Display |
|------------|---------|---------|
| **High** | Mechanically certain (file doesn't exist, link is broken, pattern is missing) | Shown by default |
| **Medium** | Strong signal but ambiguous (function appears unused but could be dynamically called) | Shown by default, marked |
| **Low** | Heuristic guess (might be dead code, might be a public API) | Hidden unless `--all` flag |

Default output shows high + medium confidence only. `--all` shows everything. This is the Datadog/ZeroFalse insight: use the LLM as a judge to filter its own findings.

### Fix tiers

Not all findings need the same response. Three tiers based on confidence and reversibility:

| Tier | When | What happens |
|------|------|-------------|
| **Auto-fixable** | Deterministic, safe, reversible | Report includes the exact command. E.g., `Action: git rm --cached .env.local && echo '.env.local' >> .gitignore` |
| **Suggest with diff** | High confidence but changes code | Report shows a preview of the change. E.g., updated docstring, normalized line endings |
| **Explain only** | Uncertain or judgment-required | Natural language explanation of the finding and why it matters. E.g., "This function appears unused, but it's exported — verify before deleting" |

The key insight from OpenRewrite: deterministic fixes earn trust. If the tool gets the easy stuff right every time, people trust it for the harder stuff.

### Natural language explanations

Every finding gets a "why it matters" line — not just "unused export detected" but context-aware reasoning:

> `helpers/tax_calculator.py:calculate_old_rate()` — last called in commit `abc123` (6 months ago) when the tax module was refactored to `calculate_rate_v2()`. Appears to be dead code from the old calculation system. The only test referencing it (`test_tax.py:12`) is also skipped.

This addresses the #2 complaint about analysis tools (ICSE 2013 research): "tools don't give enough information to assess what the problem is." The LLM has the context to explain *why*, not just *what*.

### Hygiene score

A single 0-100 number summarizing overall project health. Weighted by severity and confidence:

- High-confidence critical findings (DEAD, BROKEN, VIOLATION) drag the score down fast
- Low-confidence or advisory findings (MAYBE, REVIEW, WATCH) have minimal impact
- Score trends over time matter more than the absolute number

The score appears in the report header: `Hygiene Score: 74/100 (▼ down from 78)`. Not a letter grade — numbers feel precise and less judgmental. The real value is the trend: "am I making this repo better or worse?"

---

## Landscape & Positioning

Research into existing tools confirms this space is fragmented. Many tools cover 1-2 lenses; none does a multi-lens project scan.

### Closest existing tools

| Tool | Covers | Limitation |
|------|--------|------------|
| **Knip** (knip.dev) | Dead code, dead deps, unused exports | JS/TS only |
| **Vulture** | Dead code (functions, imports, variables) | Python only |
| **deptry** | Dead/missing dependencies | Python only |
| **dependency-cruiser** | Circular deps, orphan modules, layer violations | JS/TS only |
| **Lychee** (lychee.cli.rs) | Broken links in markdown/HTML | Links only — doesn't check if docs *match code* |
| **todocheck** | TODOs referencing closed/missing issues | Only issue-linked TODOs, no age awareness |
| **Repolinter** (TODO Group) | Repo structure rules (README exists, LICENSE, etc.) | Archived/dead project |
| **Danger JS** (danger.systems) | CI-time PR checks (configurable) | Framework, not batteries-included; requires CI |
| **CodeScene** (codescene.com) | Hotspots, code health biomarkers, knowledge silos | Commercial SaaS |
| **SonarQube** | Bugs, smells, duplication, coverage | High false-positive rate, heavy infrastructure |
| **Semgrep** (semgrep.dev) | Custom pattern-based rules across languages | Powerful but you write all the rules yourself |

### What big companies do

- **Meta (SCARF):** Graph-based dead code elimination. Auto-generates deletion PRs daily. 100M+ lines removed over 5 years. Key insight: automate *deletion*, not just detection.
- **Google (Tricorder):** Plugin-based analysis platform, ~50K changes/day. Obsessive about low false-positive rates. Runs at code-review time, not as a separate scan.
- **Common pattern:** Integration at review time, automated remediation (actual PRs, not just reports), graph-based analysis across the full dependency tree.

### Gaps /hygiene fills

1. **Multi-lens single-pass scanning.** No tool covers more than 2-3 lenses. One command, 12 checks.
2. **Doc-code drift detection.** Lychee checks if links *resolve*. Nothing checks if docs *match code* (e.g., docs reference `parseConfig()` but it was renamed to `loadConfig()`). LLM-powered analysis can do this naturally.
3. **Stale TODO age awareness.** todocheck only handles issue-linked TODOs. Nothing uses `git blame` to find TODOs sitting for 90+ days.
4. **Convention enforcement without CI.** Danger JS requires CI infrastructure. /hygiene runs locally, zero setup.
5. **Language-agnostic dead code signals.** Knip = JS only, Vulture = Python only. An LLM approach provides heuristic dead code signals across any language.
6. **Repo shape validation.** Repolinter is dead. "Does this repo match our declared conventions?" is unsolved for custom project structures.
7. **Config/manifest hygiene.** Almost nothing checks if build scripts reference existing files, or if env var references match `.env.example`.

### Design principles (informed by industry)

- **Low false-positive rate above all.** Google's Tricorder team learned this through multiple failed attempts. A noisy tool gets ignored. Severity tiers (`DEAD` vs `MAYBE`, `VIOLATION` vs `GAP`) help — surface high-confidence findings first.
- **Actionable output, not just reports.** Meta's SCARF generates deletion PRs, not dashboards. Each finding should have a concrete `Action:` line that could become a commit.
- **Local-first, no infrastructure.** Unlike SonarQube/CodeScene/Danger, /hygiene runs in the terminal with zero setup. The LLM *is* the analysis engine.
- **Periodic audit, not a gate.** Preflight is the gate (pre-push). Hygiene is the audit ("has entropy accumulated since last time?"). Different cadence, different tolerance for depth.

## Output format

Structured enough to become a cleanup plan. Each finding has: category tag, confidence, exact location, evidence, why it matters, concrete action line.

```
Hygiene Report — 2024-03-15
============================
Hygiene Score: 68/100 (▼ down from 74)
Since last scan (2024-03-08): +3 new, -1 resolved, 1 worsened
Trajectory: ▲ degrading (net +2)

Lens status: Dead code: stable | Doc drift: ▲ new | Convention: stable
             Stale planning: stable | Gitignore: stable | Complexity: ▲ new

## Dead Code (2 findings)

### [DEAD] [high] src/old_handler.py — entire file unreferenced
Not imported by any file. Not an entry point. Not in any manifest.
Why: This file was likely part of the v1 handler system replaced in commit def456 (4 months ago).
     The test file test_old_handler.py was deleted but the source file was missed.
Action: Delete file.

### [MAYBE] [medium] src/helpers.py:12 — validate_email() only referenced by tests
Only caller is test_helpers.py:8. No production usage.
Why: Could be awaiting use in a planned feature, or dead code left after the auth refactor.
Action: Confirm if awaiting use or dead.

## Doc Drift (2 findings) — ▲ 1 new since last scan

### [DRIFT] [high] README.md:15 — references "agents/" directory
README says: "See agents/ for autonomous workflows"
Reality: agents/ directory does not exist.
Why: The agents/ directory was removed in commit abc123 when MCP servers replaced direct agents.
Action: Remove reference from README.

### [DRIFT] [high] README.md:8 — install instructions reference setup.sh ← NEW
README says: "Run ./setup.sh to install"
Reality: setup.sh was renamed to setup.py 3 months ago.
Why: Anyone cloning this repo will hit a broken first step.
Action: Update README install instructions to reference setup.py.

## Convention Violations (1 finding)

### [VIOLATION] [high] hooks/format_code.py — 3 public functions missing docstrings
Functions: format_file(), check_formatter(), get_language()
Project convention (CLAUDE.md) requires docstrings on public functions.
Why: These functions were added in a batch commit that skipped the convention.
Action: Add docstrings to listed functions.

## Stale Planning (1 finding)

### [STALE] [medium] ROADMAP.md:18 — "/mcp-registry" in Next with no activity
Listed under "Next" but no brainstorm, no recent commits, no open design doc.
Why: Has been in "Next" since initial roadmap creation. No evidence of active work.
Action: Move to "Later" or remove from roadmap.

## Gitignore Gaps (1 finding)

### [MISSING] [high] .gitignore — no entry for debug.log
debug.log is a common log file pattern. No .gitignore rule covers it.
Action: `echo 'debug.log' >> .gitignore`

## Reducible Complexity (1 finding) — ▲ new since last scan

### [DUPLICATE] [medium] hooks/preflight_check.py:45 + hooks/format_code.py:30 — near-identical grep loops
Both functions iterate over patterns, grep for matches, and format results. ~20 lines duplicated.
Why: Both hooks were written independently. The pattern emerged after the second hook was added.
Action: Extract shared grep-and-report logic into utility.

## Summary
Findings: 8 total (5 high, 3 medium, 0 low)
By lens: 2 dead code, 2 doc drift, 0 dead deps, 0 orphans, 1 convention,
         1 stale planning, 1 gitignore gap, 0 broken refs, 0 consistency,
         1 complexity, 0 test health, 0 hotspots
Auto-fixable: 1 | Suggest with diff: 3 | Explain only: 4
```
