# AI Toolkit

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Skills, hooks, and prompts that extend Claude Code. Installed via symlinks — `git pull` updates everything.

## Why This Exists

LLM-assisted development increases entropy without guardrails. Models will push to main, overwrite protected files, skip tests, and commit secrets — not maliciously, but because nothing stops them. This toolkit is a local control layer: declarative skills define what the AI can do, hooks enforce what it can't.

## Design Principles

- **No push without preflight** — `pre-commit.py` blocks `git push` unless `/preflight` has run
- **Sensitive files are write-protected** — `protect-files.py` blocks `.env`, `.pem`, `.key`, and credential files
- **Every tool call is logged** — `log-tool-use.py` appends timestamp, session, and tool name to `~/.claude/tool-use.log`
- **Dry-run by default** — `setup.py` previews all changes; `--apply` required to execute
- **Non-invasive** — setup.py only manages its own symlinks, never touches files it didn't create

## Skills

Invoked via `/skillname` in Claude Code.

- `/bootstrap` — Interactive new-project setup (debug logging, docs, git hygiene, CLAUDE.md)
- `/preflight` — Pre-push quality checks (secrets, docs, tests, git hygiene, cleanup, security)
- `/add-debug-logging` — Add a `--debug` flag and structured file logging
- `/sync-env` — Sync skills, hooks, and settings from ai-toolkit to ~/.claude
- `/code-review` — Review code for bugs, clarity, edge cases, and security
- `/doc-gen` — Generate or update documentation for files or directories
- `/fix-issue` — Read a GitHub issue, implement a fix, write tests
- `/security-review` — Security-focused audit with severity ratings
- `/tdd` — Strict red-green-refactor test-driven development

## Hooks

- **protect-files.py** — Blocks writes to .env, .pem, .key, and credentials files
- **pre-commit.py** — Blocks git push without /preflight; blocks --no-verify
- **auto-format.py** — Formats files after Write/Edit (gofmt, black, prettier, rustfmt)
- **log-tool-use.py** — Logs all tool calls to `~/.claude/tool-use.log`

## Setup

```bash
git clone <repo> ~/dev/ai-toolkit
python ~/dev/ai-toolkit/setup.py           # preview — changes nothing
python ~/dev/ai-toolkit/setup.py --apply   # install symlinks + settings.json entries
```

Subsequent updates: `git pull` (symlinks pick up changes automatically).

```bash
python setup.py                        # preview
python setup.py --apply                # install
python setup.py --uninstall --apply    # clean removal
```

## License

[MIT](LICENSE)
