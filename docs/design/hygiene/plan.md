# /hygiene — Implementation Plan

## Context

The ROADMAP's top item is `/hygiene` — a periodic codebase entropy scanner. A detailed brainstorm exists at `docs/design/hygiene/brainstorm.md` with 12 lenses, execution model, delta tracking, and report intelligence. This plan scopes a practical V1 that ships as a single SKILL.md, following existing skill patterns.

**Key distinction from preflight:** Preflight is a pre-push gate (binary pass/fail, fast). Hygiene is a periodic audit (rich findings, deeper analysis, run weekly or after cleanups).

## V1 Scope

### 9 lenses (ordered by impact)

| # | Lens | Why it hurts |
|---|------|-------------|
| 1 | Doc drift | Most dangerous — people make decisions based on docs. Wrong docs cause wrong decisions. |
| 2 | Dead code | Most common — every search, every AI context window, every new contributor wastes time on irrelevant code. |
| 3 | Test health | Silent — the safety net has holes nobody knows about until something breaks. |
| 4 | Stale planning | Misleading — the roadmap and TODOs describe a different project than what exists. |
| 5 | Duplicate logic | Multiplier — two implementations of the same thing diverge over time. Fix a bug in one, the other still has it. |
| 6 | Convention violations | Erosion — the project had standards, and they're slowly being ignored. |
| 7 | Broken references | Navigation — you can't follow the trail. Links and paths point to nothing. |
| 8 | Dead dependencies | Hidden — packages you don't need, or packages you use but don't declare. Weight and risk for nothing. |
| 9 | Orphaned artifacts | Visible — build debris, stale files, leftover cruft. Makes the project feel neglected. |

### 3 lenses deferred to V2

| # | Lens | Why defer |
|---|------|-----------|
| - | Gitignore gaps | Preflight covers this well already |
| - | Consistency drift | High false-positive risk without tooling |
| - | Churn hotspots | Valuable but is refactoring prioritization, not entropy detection |

### V1 features

- **Scan modes:** `--full` (default) and `--changed` (files since last commit)
- **Confidence:** High and medium only (no low-confidence findings)
- **Tags:** Per-lens tags that are specific and self-explanatory (DEAD, MAYBE, DRIFT, STALE, ORPHAN, BROKEN, SKIPPED, etc.). No meta-categories — the tags themselves communicate what the problem is and imply the remedy. Summary counts by tag. (We considered grouping findings into broader entropy categories — "dead weight" for things to remove, "drift" for things out of sync, "erosion" for things that degraded — but decided against it. The per-finding tags already communicate clearly, and adding a meta-layer doesn't change what you do about a finding. The action line handles that.)
- **Action lines:** Every finding gets a concrete "Action:" step
- **Summary:** Counts by tag across all lenses (e.g., "14 findings — 3 DEAD, 2 DRIFT, 2 STALE, 2 BROKEN, 2 ORPHAN, 1 SKIPPED, 1 AGED, 1 VIOLATION")

### Additions from landscape research

Ideas discovered during research that strengthen V1:

**Commented-out code detection** (lens 1) — from flake8-eradicate, deadcode (DC12). Unused functions and commented-out code are both dead code but for different reasons. An unused function was real code nothing calls anymore. A commented-out block is code someone explicitly disabled but didn't delete, usually hedging ("I might need this later"). Both accumulate entropy.

**Unlisted/phantom dependencies** (lens 3) — from Knip's `unlisted` check. Dead deps (declared but unused) is half the picture. The inverse: imports that work because a transitive dependency provides them, but aren't declared in the manifest. Update a parent package and the phantom dep disappears. Same manifest-vs-imports comparison, just in reverse.

**Issue-tracker cross-reference** (lens 6) — from todocheck. The brainstorm uses git-blame age (>90 days) as a stale-TODO heuristic. But if a TODO says `TODO(#123)` and issue #123 is closed, that's certainty, not a heuristic — the highest-confidence signal for stale planning. Only fires when TODOs have issue references, so zero false positives.

**`deadcode` as Python native tool** (lens 1) — newer than vulture (EuroPython 2024), handles global scope analysis, detects 13 dead code categories, and has `--fix --dry` preview. Adding alongside vulture — whichever is installed gets used.

**Lychee delegation** (lens 7) — Lychee (3.3k stars, Rust) already checks markdown links perfectly: anchor checking, redirect handling, caching. Delegate when installed, fall back to manual link extraction when not.

**.env/.env.example drift** (lens 5) — from env-check. Many projects use `.env.example` as a contract for required env vars. If someone adds a var to code but not to `.env.example`, onboarding breaks silently. Quick key comparison, fits under convention violations.

### Deferred features (V2+)

- Delta tracking (`.hygiene-snapshot.json`)
- Hygiene score (0-100)
- Fix tiers (auto-fixable / suggest with diff / explain only)
- `--staged` mode
- Entropy velocity tracking
- `--all` flag for low-confidence findings
- Temporal coupling detection (files that always change together — CodeScene's insight)
- Circular dependency detection (dependency-cruiser, madge)
- SARIF output format for GitHub Security tab integration

## Files to create/modify

### 1. Create `skills/hygiene/SKILL.md` (~220 lines)

Structure:

```
---
name: hygiene
description: Scan for dead code, doc drift, convention violations, and accumulated entropy
origin: personal
user-invocable: true
allowed-tools: [Read, Grep, Glob, Bash]
argument-hint: "[--changed | --full | directory]"
---
```

**Opening** (~3 lines): What this skill does, how it differs from preflight.

**Scan scope section** (~15 lines):
- `--full` (default): entire repo, all 8 lenses
- `--changed`: only files changed since last commit (`git diff --name-only HEAD~1`)
- Directory argument: scan that directory only
- Detect language from manifests/file extensions
- Check for native tools (`which vulture`, `which knip`, `which deptry`)

**8 lens sections** (~20 lines each, ~160 total):

Each lens follows this template:
```markdown
### N. Lens Name
**What to find:** One sentence.
**Detection:**
- Concrete step 1 (Glob/Grep/Bash)
- Concrete step 2
- Native tool: if <tool> available, run <command>
**Tags:**
- TAG1 — meaning (high confidence)
- TAG2 — meaning (medium confidence)
**Skip when:** <conditions>
```

Lens-specific detection logic:

1. **Dead code**: Glob source files, grep for references in other files. Check if file is entry point or in manifest. Also check for commented-out code blocks (function bodies, import groups). Native: `vulture` or `deadcode` (Python), `knip` (JS/TS). Tags: DEAD, MAYBE.

2. **Doc drift**: Read README/CLAUDE.md/ROADMAP.md/environment.md. Extract concrete claims (paths, commands, flags, feature descriptions). Cross-reference each against reality. Tags: DRIFT, STALE.

3. **Dead dependencies**: Read package manifest. Grep for imports of each dependency. Exclude dev tools and type packages. Also check the inverse: imports of packages not declared in the manifest (phantom/unlisted deps). Native: `deptry` (Python), `knip` (JS/TS), `go mod tidy -diff`. Tags: DEAD, UNLISTED, MAYBE.

4. **Orphaned artifacts**: Find `__pycache__/` in wrong places, `.pyc` files, empty dirs, stale symlinks. `git ls-files --others --exclude-standard` for untracked build output. Check for `.bak`, `.orig` files. Tags: ORPHAN, CHECK.

5. **Duplicate logic**: Filter-then-compare, not exhaustive. First, group candidates by shape (similar line count, parameter count, return type), by name (similar function names like `parse_config`/`load_config`/`read_config`), or by purpose (same directory, same data types). Then compare only the top 20-30 most suspicious pairs. Native: `jscpd` (copy-paste), `pylint --duplicate-code`. The LLM adds value by catching logic duplication that looks different syntactically. Tags: DUPLICATE, SIMILAR.

6. **Convention violations**: Read CLAUDE.md, extract declared conventions. Check each mechanically. Check manifest against actual files. Check missing docstrings per project convention. If `.env.example` exists, verify it stays in sync with documented env vars. Tags: VIOLATION, GAP.

7. **Stale planning**: Read ROADMAP, check each item for recent commits/brainstorms. Grep TODOs/FIXMEs, check age via `git log -1 --format=%ai` on lines containing them. Flag TODOs older than 90 days. If TODOs reference issue numbers (e.g., `TODO(#123)`), check if the issue is closed via `gh issue view`. Tags: STALE, AGED.

8. **Broken references**: Extract `[text](path)` and `[text](#anchor)` links from .md files. Check if file targets exist. Check if anchor targets (headings) exist. Native: delegate to `lychee` if installed. Tags: BROKEN, SUSPECT.

9. **Test health**: Grep for skip markers (`@pytest.mark.skip`, `.skip(`, `t.Skip()`). Find test files with no `assert`/`expect`/`self.assert`. Find empty test functions. Tags: SKIPPED, EMPTY.

**Output format section** (~25 lines):

Show condensed example output:
```
Hygiene Report — 2024-03-15 (full scan)
========================================

## Doc Drift (2 findings)

### [DRIFT] [high] README.md:15 — references nonexistent directory
README says: "See agents/ for autonomous workflows"
Reality: agents/ directory does not exist.
Why: Removed when MCP servers replaced direct agents.
Action: Remove reference from README.

### [STALE] [medium] CLAUDE.md:42 — version number outdated
Claims v2.1, package.json shows v3.0.
Action: Update version in CLAUDE.md.

## Dead Code (1 finding)

### [DEAD] [high] src/old_handler.py — entire file unreferenced
Not imported by any file. Not an entry point. Not in any manifest.
Action: Delete file.

## Stale Planning (1 finding)

### [AGED] [medium] src/auth.py:88 — TODO older than 90 days
`TODO: switch to OAuth2` — last modified 2023-11-02 (4 months ago).
Action: Resolve or remove.

Summary: 4 findings (2 DRIFT, 1 DEAD, 1 AGED) across 3 lenses
```

**Rules section** (~8 lines):
- Show only high and medium confidence findings
- Omit lenses with zero findings from the report
- If the entire scan is clean, say so in one sentence
- For `--changed` mode, only report findings in changed files
- Prefer native tool output over grep heuristics when available
- Never suggest deleting files without evidence they are unreferenced

### 2. Edit `environment.md` (line 16)

Add one row to the Skills table (alphabetical order, between `fix-issue` and `preflight`):

```
| hygiene | yes |
```

### 3. Edit `README.md` (line 10)

Add one line to the skills list (after `/preflight`, since they're related):

```
- `/hygiene` — Periodic entropy scan (dead code, doc drift, convention violations, stale planning)
```

### 4. Add `.hygiene-snapshot.json` to `.gitignore`

Even though delta tracking is V2, add the pattern now so it's ready. Append under the `# Build / logs` section:

```
.hygiene-snapshot.json
```

## Verification

1. Run `python3 setup.py` (dry-run) — verify hygiene skill appears in output
2. Run `python3 tests/test_setup.py` — all 9 tests pass
3. Run `python3 tests/test_hooks.py` — all 13 tests pass
4. Invoke `/hygiene` against the ai-toolkit repo itself to test
5. Invoke `/hygiene --changed` to test the changed-files mode
6. Run `/preflight` to confirm no new warnings
