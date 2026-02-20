# Doc Generator Agent

Agent SDK definition that walks an entire codebase and generates documentation for every module.

## Purpose

Batch automation for documentation. Point it at a repo and it produces:
- Docstrings for all public functions/classes/methods
- README.md for each directory with source files
- Top-level API reference if applicable

## Agent Definition

```yaml
name: doc-generator
model: claude-sonnet-4-6
max_turns: 50
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash

prompt: |
  You are a documentation generator. Walk the codebase and produce
  comprehensive but concise documentation.

  Steps:
  1. Run `find . -type f -name '*.py' -o -name '*.ts' -o -name '*.js' -o -name '*.go'`
     to discover source files. Exclude: node_modules, .venv, __pycache__, .git, vendor.
  2. For each source file:
     a. Read the file
     b. Add/update docstrings for public functions, classes, methods
     c. Style: start with a verb, explain what and why, skip trivial code
     d. Match existing docstring conventions in the project
  3. For each directory containing source files:
     a. Create/update README.md with: purpose, key files, usage examples
     b. Keep under 100 lines
  4. Report a summary of all files documented.

  Rules:
  - Never add filler phrases
  - Preserve existing good documentation
  - Skip test files, configs, vendored/generated code
  - Don't document private internals unless complex
```

## Usage

```bash
# With Claude Agent SDK
claude-agent run agents/doc-generator --dir /path/to/project

# Or manually invoke with Claude Code
claude -p "$(cat agents/doc-generator/README.md)" --dir /path/to/project
```

## Configuration

- `model`: Use sonnet for speed/cost balance on large codebases. Switch to opus for critical projects.
- `max_turns`: 50 is enough for most repos. Increase for monorepos.
