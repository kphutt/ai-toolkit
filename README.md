# AI Toolkit

Personal toolkit for Claude Code extensibility — reusable skills, hooks, MCP servers, agents, and prompt templates.

## What's Inside

| Directory | Contents |
|-----------|----------|
| `skills/` | 11 invocable skills — bootstrap, preflight, sync-env, debug logging, code review, TDD, and more |
| `hooks/` | 6 event-driven scripts — pre-commit safety, auto-formatting, file protection, tool-use logging |
| `mcp-servers/` | 2 FastMCP servers — project context (git status, TODOs, branch info) and a reference example |
| `agents/` | 2 Agent SDK definitions — doc generator and file summarizer |
| `prompts/` | Reusable prompt templates for common workflows |

## Skills

Invoked via `/skillname` in Claude Code.

### Personal

- `/bootstrap` — Interactive new-project setup (debug logging, docs, gitignore, CLAUDE.md)
- `/preflight` — Pre-push quality checks (secrets, docs, tests, gitignore, cleanup, manifest drift)
- `/add-debug-logging` — Add a `--debug` flag and structured file logging
- `/sync-env` — Sync skills, hooks, and settings from ai-toolkit to ~/.claude

### Community

- `/code-review` — Review code for bugs, clarity, edge cases, and security
- `/doc-gen` — Generate or update documentation for files or directories
- `/fix-issue` — Read a GitHub issue, implement a fix, write tests
- `/security-review` — Security-focused audit with severity ratings
- `/tdd` — Strict red-green-refactor test-driven development
- `/compliment` — Find something genuinely well-done in the codebase

## Hooks

- **pre-commit.sh** — Blocks commits with staged secrets or --no-verify; reminds to run /preflight before push
- **auto-format.sh** — Formats files after Write/Edit (black, prettier, gofmt, rustfmt)
- **protect-files.sh** — Blocks writes to .env, .pem, .key, and credentials files
- **log-tool-use.sh** — Logs all tool calls to `~/.claude/tool-use.log`

## Setup

```bash
git clone <repo> ~/dev/ai-toolkit
bash ~/dev/ai-toolkit/setup.sh           # preview — changes nothing
bash ~/dev/ai-toolkit/setup.sh --apply   # install symlinks + settings.json entries
```

Subsequent updates: `git pull` (symlinks pick up changes automatically).

See `environment.md` for what gets installed and why certain components are excluded.

## Safety Invariant

**setup.py never modifies, overwrites, or deletes anything it didn't create.** It only manages its own links and settings.json entries. Dry-run by default (preview only, changes nothing).

```bash
bash setup.sh                        # preview — changes nothing (wrapper calls setup.py)
bash setup.sh --apply                # install (create links)
bash setup.sh --detach --apply       # freeze current version as regular files
bash setup.sh --uninstall --apply    # clean removal (links + settings entries)
```

Already deleted the repo? Clean up dangling symlinks:
```bash
find ~/.claude/skills ~/.claude/hooks -maxdepth 1 -type l ! -exec test -e {} \; -delete
```

## License

[MIT](LICENSE)
