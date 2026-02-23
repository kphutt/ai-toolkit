# /hygiene — Codebase Entropy Scanner

Mechanical scan that finds dead code, doc drift, orphaned artifacts. Produces a structured report with specific actions. Fast, run-it-often (weekly, after cleanups).

**Not preflight** (pre-push gate for secrets/tests). Not code-review (per-file bug hunting). Hygiene is a periodic audit: "has entropy accumulated?"

**Implementation:** Create `skills/hygiene/SKILL.md`. Frontmatter: `name: hygiene`, `description: Scan for dead code, doc drift, orphaned artifacts, and simplification opportunities`, `origin: personal`, `user-invocable: true`, `allowed-tools: [Read, Grep, Glob, Bash]`, `argument-hint: "[directory]"`. Add to `environment.md` skills table, `README.md` skills list.

## Checks

### 1. Dead files
- Glob all source files
- For each: is it imported by another file? Is it an entry point? Is it in a manifest?
- Report orphaned files that are neither imported, entry points, nor manifest-listed
- Exclude: test files (they reference production, not vice versa), root configs (.gitignore, LICENSE, etc.)
- Severity: DEAD if zero references, MAYBE if only referenced in one place (could be over-abstraction)

### 2. Doc drift
- Parse README.md, CLAUDE.md, ROADMAP.md for concrete claims: directory names, CLI commands/flags, file paths, feature descriptions, URL references
- Cross-reference each claim against reality (Glob for dirs, Grep for references, Read for content)
- Report stale claims with file:line and what reality shows
- Go deeper than preflight's doc-freshness check (line-level references, not just "does README exist")
- Example: README says "See agents/ for autonomous workflows" but agents/ directory does not exist → DRIFT

### 3. Dead dependencies
- Read package manifest (package.json / requirements.txt / go.mod / Cargo.toml)
- Grep for actual import/usage of each dependency in source files
- Report declared-but-never-imported dependencies
- Exclude: dev/build tools (webpack, vite, pytest, etc.), type-only packages (@types/*), runtime-implicit deps

### 4. Orphaned artifacts
- Find `__pycache__/`, `.pyc`, leftover build dirs, empty directories
- `git ls-files --others --exclude-standard` for untracked files that look like they should be gitignored
- Check for stale links (symlinks/junctions whose targets no longer exist)
- This catches the exact `mcp-servers/__pycache__` problem from the bash→Python cleanup — git rm -rf removes tracked files but leaves untracked subdirs behind

### 5. Manifest drift (when applicable)
- If `environment.md` exists: compare declared skills/hooks against actual `skills/` and `hooks/` dirs
- Report files that exist but aren't declared, or declared but don't exist
- Note: preflight has a version of this check scoped to pre-push. Hygiene's version is standalone.

## Output format

Structured enough to become a cleanup plan. Each finding has: category tag, exact location, evidence, concrete action line.

```
Hygiene Report
==============

## Dead Files (2 findings)

### [DEAD] src/old_handler.py — entire file unreferenced
Not imported by any file. Not an entry point. Not in any manifest.
Action: Delete file.

### [MAYBE] src/helpers.py:12 — validate_email() only referenced by tests
Only caller is test_helpers.py:8. No production usage.
Action: Confirm if awaiting use or dead.

## Doc Drift (1 finding)

### [DRIFT] README.md:15 — references "agents/" directory
README says: "See agents/ for autonomous workflows"
Reality: agents/ directory does not exist.
Action: Remove reference from README.

## Orphaned Artifacts (1 finding)

### [ORPHAN] mcp-servers/__pycache__/ — untracked directory
Left behind after git rm -rf mcp-servers/. Contains .pyc files.
Action: Delete directory, add __pycache__/ to .gitignore if missing.

## Summary: 2 dead files, 1 doc drift, 1 orphan, 0 dead deps
```
