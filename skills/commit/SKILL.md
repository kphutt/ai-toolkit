---
name: commit
description: Generate a commit message from staged changes and commit
origin: community
user-invocable: true
allowed-tools: [Bash]
---

Generate a well-crafted commit message and create the commit.

## Steps

1. Run `git diff --cached --stat` to see what files changed
2. Run `git diff --cached` to read the actual changes
3. Run `git log --oneline -10` to see recent commit message style
4. Draft a commit message following the project's conventions:
   - If the project uses conventional commits (feat:, fix:, etc.), match that
   - Otherwise, use imperative mood ("Add feature" not "Added feature")
   - First line under 72 characters
   - Add a blank line then body if the change needs explanation
   - Focus on **why**, not what (the diff shows what)
5. Show the drafted message to the user and ask for approval
6. If approved, run `git commit -m "<message>"`

## Rules

- Never commit without showing the message first
- Never use `--no-verify` or skip hooks
- If nothing is staged, tell the user and suggest what to stage
- If the diff is trivial (typo, formatting), keep the message to one line
