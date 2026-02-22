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
| doc-gen | yes |
| fix-issue | yes |
| preflight | yes |
| security-review | yes |
| sync-env | yes |
| tdd | yes |

## Hooks

| File | Install | Event | Matcher |
|------|---------|-------|---------|
| auto-format.py | yes | PostToolUse | Write\|Edit |
| log-tool-use.py | yes | PostToolUse | _(none — all tools)_ |
| pre-commit.py | yes | PreToolUse | Bash |
| protect-files.py | yes | PreToolUse | Write\|Edit |

## Settings.json Hook Registrations

Sync adds these if missing. Never removes existing entries.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/protect-files.py"}]
      },
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/pre-commit.py"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/auto-format.py"}]
      },
      {
        "hooks": [{"type": "command", "command": "python3 ~/.claude/hooks/log-tool-use.py"}]
      }
    ]
  }
}
```

## Setup

New machine: `git clone <repo> ~/dev/ai-toolkit && python ~/dev/ai-toolkit/setup.py --apply`
Subsequent updates: `git pull` (symlinks pick up changes automatically)
Review state: `/sync-env` from Claude Code or `python setup.py` (dry-run)

To freeze copies instead of symlinks: `cp -r` the skill/hook directory, then `--uninstall`.
