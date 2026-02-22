---
name: sync-env
description: Sync skills, hooks, and settings from ai-toolkit to ~/.claude
origin: personal
user-invocable: true
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
argument-hint: "[path-to-ai-toolkit]"
---

Sync the ai-toolkit environment manifest to `~/.claude/`. Check the state of all skills, hooks, and settings.json registrations, show a report, and offer to fix any issues.

## Algorithm

1. **Find manifest.** Use the argument as the toolkit path, or default to `~/dev/ai-toolkit`. Read `environment.md` from that path. If not found, print a clear error and stop.

2. **Ensure target directories exist.** Create `~/.claude/skills/` and `~/.claude/hooks/` if missing.

3. **Check each skill** (where Install = yes in the manifest):
   - Target doesn't exist → **MISSING**
   - Target is a symlink to the correct source → **CURRENT**
   - Target is a symlink to wrong source → **RELINK** (stale symlink)
   - Target is a regular file/directory → **LOCAL** (not managed, won't touch)

4. **Check each hook** (where Install = yes):
   - Same logic as skills.

5. **Check settings.json registrations:**
   - Read `~/.claude/settings.json`
   - For each hook registration in the manifest's "Settings.json Hook Registrations" section:
     - Present in settings.json → **CURRENT**
     - Missing → **MISSING**

6. **Show report** in this format:
   ```
   Environment Sync Report
   =======================
   Source: ~/dev/ai-toolkit

   Skills:
     CURRENT  add-debug-logging -> ~/dev/ai-toolkit/skills/add-debug-logging
     CURRENT  bootstrap -> ~/dev/ai-toolkit/skills/bootstrap
     MISSING  sync-env
     LOCAL    preflight (regular file — not managed)

   Hooks:
     CURRENT  auto-format.sh -> ~/dev/ai-toolkit/hooks/auto-format.sh
     MISSING  pre-commit.sh

   Settings.json:
     CURRENT  PreToolUse: bash ~/.claude/hooks/protect-files.sh
     MISSING  PostToolUse: bash ~/.claude/hooks/log-tool-use.sh

   Summary: 8 current, 2 missing, 1 local
   ```

7. **If everything is CURRENT**, print "All synced." and stop.

8. **If there are MISSING or RELINK items**, ask the user: "Apply fixes? This will create/update symlinks and add missing settings.json entries. LOCAL items are never touched."

9. **Apply fixes** (only after user confirms):
   - For MISSING skills/hooks: create symlinks from `~/.claude/<type>/<name>` → `<toolkit>/<type>/<name>`
   - For RELINK: remove old symlink, create new one
   - For settings.json MISSING entries: read the current file, add the missing hook registrations (merge — never remove existing entries), write back with atomic temp-file + rename
   - Never touch LOCAL items

10. **Post-apply note:** "New skills take effect next session. Hook changes are immediate."
