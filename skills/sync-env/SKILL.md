---
name: sync-env
description: Sync skills, hooks, settings, and files from ai-toolkit
origin: personal
user-invocable: true
allowed-tools: [Read, Bash, Glob, Grep]
argument-hint: "[path-to-ai-toolkit]"
---

Sync the ai-toolkit environment to the local machine. This skill wraps setup.py —
all installation logic lives there.

## Algorithm

1. **Find toolkit.** Use the argument as the toolkit path, or default to `~/dev/ai-toolkit`.
   Verify `environment.md` and `setup.py` exist. If not found, print a clear error and stop.

2. **Run dry-run.** Execute: `python3 <toolkit>/setup.py`
   This shows the current state of all skills, hooks, settings, and files without changing anything.

3. **Show the report** to the user. Summarize: how many CURRENT, how many would be created/relinked,
   any LOCAL items (which are never touched).

4. **If everything is CURRENT**, print "All synced." and stop.

5. **If there are items to fix**, ask the user: "Apply fixes? This will create/update symlinks
   and add missing settings.json entries. LOCAL items are never touched."

6. **Apply.** Execute: `python3 <toolkit>/setup.py --apply`
   Show the output.

7. **Post-apply note:** "New skills take effect next session. Hook changes and file links are immediate."
