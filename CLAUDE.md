# AI Toolkit — Conventions

Personal toolkit for Claude Code extensibility: skills, hooks, MCP servers, agents, and prompts.

## Repository Structure

```
skills/          # Invocable skills for Claude Code
hooks/           # Shell scripts triggered by Claude Code events
mcp-servers/     # FastMCP servers exposing tools to Claude
agents/          # Agent SDK definitions for batch automation
prompts/         # Reusable prompt templates
```

## Skills

Every skill is a **directory** with a `SKILL.md` entry point:

```
skills/my-skill/
  SKILL.md        # entry point (required)
  examples/       # optional reference material
```

### SKILL.md Format

```markdown
---
name: my-skill
description: One-line description of what this skill does
user_invocable: true
allowed-tools: [Read, Grep, Glob, Bash]
argument-hint: "<file-or-path>"
---

Instructions for Claude when the skill is invoked.
```

Required frontmatter fields: `name`, `description`
Common optional fields: `user_invocable`, `allowed-tools`, `argument-hint`

### Writing Good Skills

- Be specific about what Claude should do, not how to think
- List concrete steps, not vague goals
- Specify output format if it matters
- Use `allowed-tools` to limit scope when appropriate

## Hooks

Shell scripts in `hooks/`. Each script must:

1. Be executable (`chmod +x`)
2. Have a comment on line 3 indicating the event type:
   ```bash
   #!/bin/bash
   # Description of what this hook does
   # Hook type: PreToolUse | PostToolUse | PreCompact | Notification
   ```
3. Use correct exit codes:
   - `0` — success, proceed normally
   - `2` — block the action (PreToolUse only)

### Hook Events

| Event | Trigger | Can Block? |
|-------|---------|------------|
| PreToolUse | Before a tool runs | Yes (exit 2) |
| PostToolUse | After a tool runs | No |
| PreCompact | Before context compaction | No |
| Notification | When Claude wants user attention | No |

### Environment Variables Available in Hooks

- `CLAUDE_TOOL_NAME` — name of the tool being called
- `CLAUDE_TOOL_INPUT` — JSON of tool parameters (stdin)
- `CLAUDE_SESSION_ID` — current session identifier

## MCP Servers

Built with Python [FastMCP](https://github.com/jlowin/fastmcp). Pattern:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("server-name")

@mcp.tool()
def my_tool(param: str) -> str:
    """Docstring becomes the tool description."""
    return result

if __name__ == "__main__":
    mcp.run()
```

Register servers in `.claude/settings.json` under `mcpServers`.

## Agents

Agent definitions live in `agents/<name>/`. Each has a `README.md` describing purpose, prompt, and usage. Agents are designed for batch/automated use via the Claude Agent SDK.

## Project Docs Convention

All repos follow the standard in [prompts/project-docs.md](prompts/project-docs.md): `ROADMAP.md` for big rocks, `docs/decisions/` for decision records, `docs/design/{initiative}/brainstorm.md` for optional design exploration.

## Style

- Keep instructions concise — no filler, no motivation speeches
- Prefer concrete examples over abstract descriptions
- Test hooks manually before committing: `echo '{}' | ./hooks/my-hook.sh`
