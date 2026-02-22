---
name: bootstrap
description: Interactive new-project setup — debug logging, docs structure, gitignore, CLAUDE.md
origin: personal
user-invocable: true
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, Skill]
---

Walk through project setup steps interactively. For each step, ask whether to run or skip.

## 1. Detect Project Type

Before starting, identify the project:

- **Go**: `go.mod`, `*.go` files
- **Python**: `pyproject.toml`, `setup.py`, `requirements.txt`, `*.py` files
- **JavaScript/TypeScript**: `package.json`, `*.js`/`*.ts` files
- **Rust**: `Cargo.toml`, `*.rs` files

Read the entry point or manifest to understand the project's name and structure. Print what you detected.

## 2. Interactive Steps

For each step below, ask the user: **"Run [step name]? (yes/skip)"**. If they skip, move to the next step.

### Step 1: Debug logging

Invoke the `/add-debug-logging` skill to add a `--debug` flag and structured file logging.

### Step 2: Project docs structure

Follow the convention from `prompts/project-docs.md`:

- Create `ROADMAP.md` with an empty template:
  ```markdown
  # Roadmap

  <!-- Prioritized big rocks. This is the backlog. -->
  ```
- Create `docs/decisions/` directory (empty)
- Create `docs/design/` directory (empty)

### Step 3: Gitignore essentials

Create or augment `.gitignore` with:

- **Always include**: `.env`, `*.pem`, `*.key`, `debug.log`, `.DS_Store`, `Thumbs.db`
- **Language-specific** (based on detection):
  - Go: binary name (from `go.mod` module), `vendor/`
  - Python: `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `*.egg-info/`
  - JS/TS: `node_modules/`, `dist/`, `.next/`, `coverage/`
  - Rust: `target/`

If `.gitignore` already exists, append only missing patterns — don't duplicate.

### Step 4: CLAUDE.md scaffold

Create a starter `CLAUDE.md` with:

```markdown
# {Project Name} — Conventions

## Structure

{detected directory layout — top-level dirs only}

## Conventions

<!-- Add project-specific conventions here -->

## Docs

This project follows the [project-docs convention](https://github.com/{user}/{repo}/blob/main/docs/): `ROADMAP.md` for big rocks, `docs/decisions/` for decision records.
```

Fill in project name from the manifest file. If `CLAUDE.md` already exists, skip and tell the user.

## 3. Summary

After all steps, print a summary:

```
Bootstrap complete
==================
[DONE] Debug logging — --debug flag added
[SKIP] Project docs — skipped by user
[DONE] Gitignore — .gitignore created with Python patterns
[DONE] CLAUDE.md — scaffold created
```
