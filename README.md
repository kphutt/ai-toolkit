# AI Toolkit

Personal toolkit for Claude Code extensibility — reusable skills, hooks, MCP servers, agents, and prompt templates.

## What's Inside

| Directory | Contents |
|-----------|----------|
| `skills/` | 10 invocable skills — bootstrap, preflight, debug logging, code review, TDD, and more |
| `hooks/` | 6 event-driven scripts — pre-commit safety, auto-formatting, file protection, tool-use logging |
| `mcp-servers/` | 2 FastMCP servers — project context (git status, TODOs, branch info) and a reference example |
| `agents/` | 2 Agent SDK definitions — doc generator and file summarizer |
| `prompts/` | Reusable prompt templates for common workflows |

## Skills

Invoked via `/skillname` in Claude Code.

### Personal

Built for this toolkit — opinionated workflows for CLI/TUI projects:

- `/bootstrap` — Interactive new-project setup (debug logging, docs, gitignore, CLAUDE.md)
- `/preflight` — Pre-push quality checks (secrets, docs, tests, gitignore, cleanup)
- `/add-debug-logging` — Add a `--debug` flag and structured file logging

### Community

Generic reusable skills:

- `/code-review` — Review code for bugs, clarity, edge cases, and security
- `/commit` — Generate a commit message from staged changes and commit
- `/doc-gen` — Generate or update documentation for files or directories
- `/fix-issue` — Read a GitHub issue, implement a fix, write tests
- `/security-review` — Security-focused audit with severity ratings
- `/tdd` — Strict red-green-refactor test-driven development
- `/compliment` — Find something genuinely well-done in the codebase

## Hooks

Run automatically in response to Claude Code events:

- **pre-commit.sh** — Blocks commits with staged secrets (.env, .key, .pem), debug.log, or --no-verify
- **auto-format.sh** — Formats files after Write/Edit (black, prettier, gofmt, rustfmt)
- **protect-files.sh** — Blocks writes to .env, .pem, .key, and credentials files
- **log-tool-use.sh** — Logs all tool calls to `~/.claude/tool-use.log`
- **reinject-context.sh** — Re-injects CLAUDE.md reminders before context compaction
- **notify.sh** — Desktop notification when Claude needs attention

## Settings Template

`settings/user-settings.json` is a portable Claude Code permissions template covering git, gh, Go, Python, npm, and other routine commands. Copy it to `~/.claude/settings.json` on any machine:

```bash
cp settings/user-settings.json ~/.claude/settings.json
```

Destructive commands (`rm -rf`, `git push --force`, `git reset --hard`, `git clean`) are intentionally excluded so they still prompt for confirmation.

## Getting Started

See [CLAUDE.md](CLAUDE.md) for conventions, file formats, and how to add new components.

## License

[MIT](LICENSE)
