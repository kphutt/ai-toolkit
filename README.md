# AI Toolkit

Skills, hooks, and prompts that extend Claude Code. Installed via symlinks — `git pull` updates everything.

## Skills

Invoked via `/skillname` in Claude Code.

- `/bootstrap` — Interactive new-project setup (debug logging, docs, gitignore, CLAUDE.md)
- `/preflight` — Pre-push quality checks (secrets, docs, tests, gitignore, cleanup, security)
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

setup.py only manages its own links — never touches files it didn't create. Dry-run by default.

```bash
python setup.py                        # preview
python setup.py --apply                # install
python setup.py --uninstall --apply    # clean removal
```

## License

[MIT](LICENSE)
