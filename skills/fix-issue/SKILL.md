---
name: fix-issue
description: Read a GitHub issue, find relevant code, implement fix, write tests
user_invocable: true
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
argument-hint: "<issue-number>"
---

End-to-end workflow: read a GitHub issue, understand the problem, implement a fix, write tests, verify.

## Steps

1. **Read the issue**
   - Run `gh issue view <number>` to get the full issue
   - Identify: what's broken, reproduction steps, expected behavior
   - If the issue is a feature request, identify acceptance criteria

2. **Find relevant code**
   - Use Grep/Glob to locate the code mentioned in the issue
   - Read the relevant files to understand current behavior
   - Identify the root cause (for bugs) or insertion point (for features)

3. **Plan the fix**
   - Describe the change in 2-3 sentences before writing code
   - If the fix is non-trivial, outline it to the user and ask for confirmation

4. **Write tests first**
   - Write a failing test that reproduces the bug or validates the feature
   - Run the test suite to confirm the test fails for the right reason
   - Match existing test patterns in the project (framework, file location, naming)

5. **Implement the fix**
   - Make the minimum change needed to fix the issue
   - Run the test suite to confirm the fix works
   - Run the full test suite to check for regressions

6. **Report**
   - Summarize what was changed and why
   - List all modified files
   - Suggest a commit message

## Rules

- Never push or create PRs automatically — only local changes
- If you can't reproduce or understand the issue, say so and ask for help
- If the fix requires changes outside the repo (dependencies, infrastructure), flag it
