---
name: preflight
description: Pre-push quality checks — secrets, docs, tests, gitignore, cleanup
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
- **FAIL** if no README, **WARN** if public functions lack docstrings, **PASS** otherwise

### 3. Test check

- Glob for test files (`*_test.go`, `test_*.py`, `*.test.js`, `*.test.ts`, `*.spec.*`)
- If tests exist, run the project's test command (`go test ./...`, `pytest`, `npm test`)
- Flag source files that have no corresponding test file
- **FAIL** if tests fail, **WARN** if untested source files exist, **PASS** if all tests pass

### 4. Gitignore check

- Check if `debug.log` is tracked (`git ls-files debug.log`)
- Check if `.env` is tracked (`git ls-files .env`)
- Check if common build artifacts are tracked (`node_modules/`, `dist/`, `__pycache__/`, `target/`)
- **FAIL** if any sensitive/build files are tracked, **PASS** otherwise

### 5. Cleanup scan

- Count `TODO`, `FIXME`, `HACK`, `XXX` comments in source files (exclude vendor/node_modules)
- Check for uncommitted changes (`git status --porcelain`)
- **WARN** if TODOs/FIXMEs exist or uncommitted changes remain, **PASS** otherwise

## Output Format

Print results in this exact format:

```
Preflight Results
=================
[PASS] Secrets — no hardcoded secrets found
[WARN] Docs — 2 public functions missing docstrings
[PASS] Tests — 12 tests passed
[FAIL] Gitignore — debug.log is tracked
[WARN] Cleanup — 3 TODOs, 1 FIXME remaining

Result: 2 pass, 2 warn, 1 fail
```

Use the actual counts and details from each check. Keep descriptions to one line each.
