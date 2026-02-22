---
name: security-review
description: Review code for security vulnerabilities with severity ratings and fixes
origin: community
user-invocable: true
allowed-tools: [Read, Grep, Glob, Bash]
argument-hint: "<file-path, directory, or 'staged'>"
---

Security-focused code review. Check for vulnerabilities, rate severity, suggest fixes.

## Determine What to Review

Based on the argument:
- **File path** — Read and review that file
- **Directory** — Glob for source files and review each
- **"staged"** or no argument — Run `git diff --cached` to review staged changes

## Security Checklist

### Injection
- SQL injection (string concatenation in queries, missing parameterization)
- Command injection (unsanitized input in shell commands, subprocess)
- XSS (unescaped user input in HTML/templates)
- Path traversal (user input in file paths without sanitization)
- Template injection (user input in template strings)

### Secrets & Auth
- Hardcoded secrets, API keys, passwords, tokens
- Weak or missing authentication checks
- Missing authorization (accessing resources without permission check)
- Insecure session handling
- Overly permissive CORS

### Data Handling
- Sensitive data in logs (passwords, tokens, PII)
- Missing input validation at system boundaries
- Insecure deserialization
- Missing rate limiting on auth endpoints

### Dependencies
- Run `npm audit` / `pip audit` / `cargo audit` if applicable
- Flag known vulnerable dependency versions

## Output Format

For each issue found:

```
### [SEVERITY] file:line — short description

**Vulnerability:** What the issue is and how it could be exploited.
**Impact:** What an attacker could achieve.
**Fix:**
<code suggestion>
```

Severity levels:
- `CRITICAL` — Exploitable now, data loss or RCE possible
- `HIGH` — Exploitable with some effort, significant impact
- `MEDIUM` — Requires specific conditions, moderate impact
- `LOW` — Minor issue, defense-in-depth concern

End with a summary: "N issues found (X critical, Y high, ...)" or "No security issues found."
