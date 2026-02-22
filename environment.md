# Environment Manifest

Source repo: ~/dev/ai-toolkit
Install target: ~/.claude
Install method: symlinks (source files are never copied — changes via git pull take effect immediately)

## Skills

| Name | Install |
|------|---------|
| add-debug-logging | yes |
| bootstrap | yes |
| code-review | yes |
| compliment | yes |
| doc-gen | yes |
| fix-issue | yes |
| preflight | yes |
| security-review | yes |
| sync-env | yes |
| tdd | yes |
| commit | no — redundant with Claude Code built-in |

## Hooks

| File | Install | Event | Matcher |
|------|---------|-------|---------|
| auto-format.sh | yes | PostToolUse | Write\|Edit |
| log-tool-use.sh | yes | PostToolUse | _(none — all tools)_ |
| pre-commit.sh | yes | PreToolUse | Bash |
| protect-files.sh | yes | PreToolUse | Write\|Edit |
| notify.sh | no — macOS only | | |
| reinject-context.sh | no — unsupported event | | |

## Settings.json Hook Registrations

Sync adds these if missing. Never removes existing entries.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/protect-files.sh"}]
      },
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/pre-commit.sh"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/auto-format.sh"}]
      },
      {
        "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/log-tool-use.sh"}]
      }
    ]
  }
}
```

## Setup

New machine: `git clone <repo> ~/dev/ai-toolkit && bash ~/dev/ai-toolkit/setup.sh --apply`
Subsequent updates: `git pull` (symlinks pick up changes automatically)
Review state: `/sync-env` from Claude Code or `bash setup.sh` (dry-run)

Already deleted the repo? Clean up dangling symlinks:
```bash
find ~/.claude/skills ~/.claude/hooks -maxdepth 1 -type l ! -exec test -e {} \; -print -delete
```

## Not Installed

| Component | Reason |
|-----------|--------|
| skills/commit | Redundant with Claude Code built-in |
| hooks/notify.sh | macOS only (osascript) |
| hooks/reinject-context.sh | Uses unsupported PreCompact event |
| mcp-servers/* | Tutorial demo only |
| agents/* | For Agent SDK batch use, not CLI sessions |
