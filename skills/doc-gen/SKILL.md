---
name: doc-gen
description: Generate or update documentation for files or directories
origin: community
user-invocable: true
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
argument-hint: "<file-or-directory>"
---

Generate or update documentation for the given file or directory. Style: concise, no filler.

## Steps

1. **Identify targets**
   - If given a file: document that file
   - If given a directory: glob for source files, skip tests/configs/vendored code
   - If no argument: document the current working directory

2. **For each source file:**
   - Read the file
   - Add/update docstrings for all public functions, classes, and methods
   - Docstrings should explain **what** and **why**, not restate the code
   - Match the existing docstring style if one exists (Google, NumPy, JSDoc, etc.)
   - If no style exists: Python → Google style, JS/TS → JSDoc, Go → standard godoc

3. **For directories:**
   - Create or update a `README.md` in the directory
   - Include: purpose, key files, usage examples
   - Keep it under 100 lines

## Rules

- Never add filler phrases ("This function is used to...", "This module provides...")
- Start docstrings with a verb: "Parse...", "Return...", "Validate..."
- Skip trivial getters/setters and `__init__` that just assigns args
- Don't document private/internal functions unless they're complex
- Preserve existing documentation that's already good — only update what's missing or wrong
