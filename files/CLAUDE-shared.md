# Shared Conventions

> This file is managed by ai-toolkit. It's symlinked from ~/dev/ai-toolkit/files/CLAUDE-shared.md.
> Edits here propagate via git — commit and push in ai-toolkit to sync across machines.

## Shorthand
- "y" means yes
- "check my repos" means: fetch all repos in ~/dev/, show ahead/behind origin,
  uncommitted changes, untracked files, and last commit date for each

## Cross-Project Notes
- All repos publish to GitHub under kphutt
- Writing repo is PRIVATE — never change visibility
- LinkedIn posts publish 2x/week, Tuesdays and Thursdays, 10am Pacific

## Maintenance
- If a session seems to be missing skills, hooks, or settings, suggest running /sync-env
- Proactively suggest /sync-env once at the start of longer sessions or when switching machines
- /sync-env runs setup.py to check and fix ai-toolkit symlinks — it's fast and non-destructive

## Project Dashboard

- The Active Projects table in `~/dev/kphutt/README.md` is the cross-project status dashboard.
- When wrapping up meaningful work on any project (feature complete, phase change, milestone hit),
  update the Phase and Next Action columns in README.md. Commit and push kphutt.
- When the user asks "where am I?" or "get up to speed", read kphutt/README.md first for a fast overview,
  then dig into specific repos as needed.
- Keep it concise — one line per project, current phase + next concrete action.

## Plan Mode Preferences
- In plan files, put stable content (context, file list) at the top and actively changing content
  (open questions, active discussion) at the bottom — so edits happen near where the user is reading
- Update the plan in place as you iterate — no changelog/log section, just keep the plan current
