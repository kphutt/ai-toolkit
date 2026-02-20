---
name: code-review
description: Review code for bugs, clarity, edge cases, and security issues
user-invocable: true
allowed-tools: [Read, Grep, Glob, Bash]
argument-hint: "<file-path, PR number, or 'staged'>"
---

Review code for issues that actually matter. Skip style nits.

## Determine What to Review

Based on the argument:
- **File path** — Read and review that file
- **PR number** — Run `gh pr diff <number>` to get the diff
- **"staged"** or no argument — Run `git diff --cached` to review staged changes
- **Directory** — Glob for source files and review each

## Review Checklist

For each file or diff, check:

1. **Bugs** — anything that would break at runtime or produce wrong results
2. **Edge cases** — null/empty inputs, off-by-one, concurrency, large data
3. **Security** — injection, hardcoded secrets, auth gaps, path traversal
4. **Clarity** — could another dev understand this in 30 seconds? Flag confusing names or logic

## Output Format

For each issue found:

```
### [severity] file:line — short description

**Problem:** What's wrong and why it matters.
**Fix:**
<code suggestion>
```

Severity levels: `BUG`, `EDGE CASE`, `SECURITY`, `CLARITY`

If the code looks clean, say so in one sentence — don't manufacture issues.

End with a one-line summary: "N issues found (X bugs, Y edge cases, ...)" or "Looks good."
