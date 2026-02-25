---
name: preflight
description: Pre-push quality checks — secrets, docs, tests, gitignore, cleanup, doc freshness, security
origin: personal
user-invocable: true
allowed-tools: [Read, Grep, Glob, Bash]
---

On-demand quality checks before pushing or wrapping up a dev session. Run all checks and report results.

## Checks

Run each check and record the result as PASS, WARN, or FAIL.

### 1. Secrets scan

- Grep for patterns: `API_KEY\s*=\s*["']`, `SECRET\s*=\s*["']`, `TOKEN\s*=\s*["']`, `PASSWORD\s*=\s*["']`, `-----BEGIN .* KEY-----`
- Check if any `.env` files are staged (`git diff --cached --name-only | grep '\.env'`)
- **FAIL** if hardcoded secrets or staged `.env` found, **PASS** otherwise

### 2. Doc coverage

- Check that `README.md` exists and has more than 5 lines
- Detect language and check for missing docstrings on public functions:
  - Go: exported functions without a preceding `// FuncName` comment
  - Python: public functions/classes without docstrings
  - JS/TS: exported functions without JSDoc
- **Skip** test files: don't flag test methods (`test_*`), unittest overrides (`setUp`, `tearDown`), or test classes
- **FAIL** if no README, **WARN** if public functions lack docstrings, **PASS** otherwise

### 3. Test check

- Glob for test files (`*_test.go`, `test_*.py`, `*.test.js`, `*.test.ts`, `*.spec.*`)
- If tests exist, run the project's test command (`go test ./...`, `pytest`, `npm test`)
- Flag source files that have no corresponding test file
- **FAIL** if tests fail, **WARN** if untested source files exist, **PASS** if all tests pass

### 4. Git hygiene check

- Check if `.gitattributes` exists and contains `* text=auto`
- Check if `debug.log` is tracked (`git ls-files debug.log`)
- Check if `.env` is tracked (`git ls-files .env`)
- Check if common build artifacts are tracked (`node_modules/`, `dist/`, `__pycache__/`, `target/`)
- **FAIL** if any sensitive/build files are tracked, **WARN** if `.gitattributes` is missing or lacks `* text=auto`, **PASS** otherwise

### 5. Cleanup scan

- Count `TODO`, `FIXME`, `HACK`, `XXX` comments in source files (exclude vendor/node_modules)
- Check for uncommitted changes (`git status --porcelain`)
- **WARN** if TODOs/FIXMEs exist or uncommitted changes remain, **PASS** otherwise

### 6. Doc freshness

Cross-reference project documentation against the actual codebase.

**README.md accuracy:**
- Read README, identify claims about: directory structure, CLI commands/flags, dependencies, doc paths
- Cross-reference against reality (ls, manifest files, source code)
- **FAIL** if references don't match codebase

**CLAUDE.md accuracy:**
- Read CLAUDE.md, identify claims about: project structure, build/test commands, conventions, dependencies
- Cross-reference against reality (ls, manifest, source code)
- **FAIL** if described structure or commands don't match codebase

**ROADMAP.md staleness:**
- Must exist and be non-empty
- Count code-file commits since ROADMAP last modified: `git log --oneline --after="$(git log -1 --format=%aI -- ROADMAP.md)" -- '*.go' '*.py' '*.js' '*.ts'`
- **FAIL** if missing, **WARN** if 5+ code commits since last update

**Decision records (`docs/decisions/`):**
- Each file must have: `## Status`, `## Context`, `## Decision`, `## Consequences`
- Filenames must be `NNNN-short-title.md`, numbering sequential with no gaps
- **FAIL** if missing required sections, **WARN** if numbering gaps

**Initiative brainstorms (`docs/design/*/brainstorm.md`):**
- Read ROADMAP, identify active (non-struck-through) initiatives
- Each should have a `docs/design/{initiative}/brainstorm.md`
- **WARN** if `docs/design/` missing or active initiatives lack brainstorms

**Manifest drift (ai-toolkit only):**
- Only run this sub-check when the project root contains `environment.md` (i.e., preflight is running inside the ai-toolkit repo)
- Read `environment.md`, extract all skill names and hook filenames listed in the tables
- Glob for actual skill directories in `skills/` and hook files in `hooks/`
- **WARN** if any skill directory or hook file exists in source but is NOT listed in the manifest
- **WARN** if the manifest lists a skill or hook that doesn't exist in the source directory
- **PASS** if manifest matches source exactly

Overall result = worst severity across sub-checks.

### 7. Security scan

Quick automated scan for common dangerous patterns across the whole project. Not a full `/security-review` deep-dive.

**Injection patterns:**
- Grep for string concatenation in SQL queries (missing parameterization)
- Grep for unsanitized input in shell/subprocess calls (`os.system`, `exec`, `subprocess` with `shell=True`, backtick interpolation)
- Grep for unescaped user input in HTML templates
- Grep for user input in file paths without sanitization

**Unsafe function calls:**
- Language-aware grep for dangerous functions:
  - Python: `eval(`, `exec(`, `pickle.loads(`, `yaml.load(` (without SafeLoader), `subprocess.call(...shell=True`
  - Go: `exec.Command` with unsanitized input
  - JS/TS: `eval(`, `innerHTML =`, `dangerouslySetInnerHTML`, `new Function(`

**Dependency audit:**
- Run `npm audit --json` / `pip audit` / `go vuln check` if applicable
- **FAIL** if critical/high vulnerabilities, **WARN** if medium/low

**Severity:**
- **FAIL** if injection patterns or critical dependency vulns found
- **WARN** if unsafe function calls or medium dependency vulns found
- **PASS** if nothing detected

One-line summary with count, e.g.: `[WARN] Security — 2 unsafe eval() calls found`

## Output Format

```
Preflight Results
=================
[PASS] Secrets — no hardcoded secrets found
[WARN] Docs — 2 public functions missing docstrings
[FAIL] Git hygiene — debug.log is tracked
[WARN] Security — 2 unsafe eval() calls found

Result: 1 pass, 2 warn, 1 fail
```

One line per check. Use actual counts and details.
