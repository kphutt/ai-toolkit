# AI Toolkit

Personal toolkit for Claude Code extensibility — reusable skills, hooks, MCP servers, agents, and prompt templates.

## What's Inside

| Directory | Contents |
|-----------|----------|
| `skills/` | 7 invocable skills — code review, commit, doc generation, TDD, security review, issue fixing |
| `hooks/` | 5 event-driven scripts — auto-formatting, file protection, tool-use logging, context re-injection |
| `mcp-servers/` | 2 FastMCP servers — project context (git status, TODOs, branch info) and a reference example |
| `agents/` | 2 Agent SDK definitions — doc generator and file summarizer |
| `prompts/` | Reusable prompt templates for common workflows |

## Skills

Invoked via `/skillname` in Claude Code:

- `/code-review` — Review code for bugs, clarity, edge cases, and security
- `/commit` — Generate a commit message from staged changes and commit
- `/doc-gen` — Generate or update documentation for files or directories
- `/fix-issue` — Read a GitHub issue, implement a fix, write tests
- `/security-review` — Security-focused audit with severity ratings
- `/tdd` — Strict red-green-refactor test-driven development
- `/compliment` — Find something genuinely well-done in the codebase

## Hooks

Run automatically in response to Claude Code events:

- **auto-format.sh** — Formats files after Write/Edit (black, prettier, gofmt, rustfmt)
- **protect-files.sh** — Blocks writes to .env, .pem, .key, and credentials files
- **log-tool-use.sh** — Logs all tool calls to `~/.claude/tool-use.log`
- **reinject-context.sh** — Re-injects CLAUDE.md reminders before context compaction
- **notify.sh** — Desktop notification when Claude needs attention

## Getting Started

See [CLAUDE.md](CLAUDE.md) for conventions, file formats, and how to add new components.

## License

[MIT](LICENSE)
