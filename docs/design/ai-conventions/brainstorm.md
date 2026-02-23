# Portable AI Development Conventions

Turn lessons learned from AI-assisted development into a template of CLAUDE.md conventions that gets seeded into every new project. Same pattern as `prompts/project-docs.md` — a reusable template, not project-specific docs.

**Two things, not one:**
- ai-toolkit's own CLAUDE.md → covers toolkit-specific conventions (how skills work, hook format, etc.). Already exists.
- `prompts/ai-conventions.md` → a TEMPLATE of universal AI workflow conventions that `/bootstrap` seeds into OTHER projects' CLAUDE.md files. This is the new thing.

**The problem with a standalone "playbook":** It's passive. Someone has to remember to read it. What we actually want is rules that are ACTIVE — they live in each project's CLAUDE.md, so Claude follows them automatically. The template is the mechanism: `/bootstrap` asks "include AI workflow conventions?" and seeds them from `prompts/ai-conventions.md`.

**Implementation:** Create `prompts/ai-conventions.md`. Update `skills/bootstrap/SKILL.md` to add a new step: "Step 5: AI workflow conventions" that offers to include conventions from the template. Add a section to the ai-toolkit README noting the template exists.

## Conventions (each with problem/solution/rule)

### Planning conventions

**Enumerate all affected files upfront**
- Problem: Fixing things one-at-a-time led to inconsistencies — updated README but not CLAUDE.md, deleted files but left their doc references.
- Solution: Before touching anything, list every file that references the thing you're changing. Cross-reference the full list.
- CLAUDE.md rule: `Before any multi-file change, list ALL files that reference the changed components. Update them all in the same commit.`

**Write the plan, not the code**
- Problem: Asking AI to "clean up this repo" produces scattered, incomplete changes.
- Solution: Invest in a detailed plan — every file, every change, specific line numbers. Then execute mechanically.
- CLAUDE.md rule: `For non-trivial tasks, write a plan listing every file to modify and the specific changes before writing code.`

**Use plan mode for anything non-trivial**
- Problem: Jumping straight to implementation wastes effort when requirements are ambiguous or multiple approaches exist.
- Solution: Enter plan mode. Explore the codebase first. Present the approach for approval.
- CLAUDE.md rule: `Use plan mode for tasks that touch more than 2-3 files or have multiple valid approaches.`

### Verification conventions

**Every bulk operation needs a verification pass**
- Problem: `git rm -rf` deleted tracked files but left `__pycache__/` behind. Hard links became orphaned regular files.
- Solution: After every batch operation, run explicit verification. Every tool has edge cases in its cleanup behavior.
- CLAUDE.md rule: `After bulk delete/rename/refactor, verify for leftover artifacts (empty dirs, stale links, __pycache__).`

**Two passes beat one thorough pass**
- Problem: First verification missed the leftover directory.
- Solution: Run a "double check" — a second review with fresh eyes catches things the first pass normalized away.
- CLAUDE.md rule: `After completing a task, do a second-pass review checking for things the first pass missed.`

**Run tests before AND after**
- Problem: Changes that look correct can break invariants that aren't obvious.
- Solution: Run the test suite before making changes (baseline) and after (verification).
- CLAUDE.md rule: `Run tests before AND after making changes. Add tests for the specific things you changed.`

### Architecture conventions

**Eliminate unnecessary language boundaries**
- Problem: Bash hooks calling `python -c` for JSON parsing. setup.sh wrapping setup.py. Three languages touching one operation.
- Solution: Pick one language. Write everything in it. Remove wrappers. Every boundary doubles debug complexity.
- CLAUDE.md rule: `One language per operation — don't shell out to another language for parsing or formatting.`

**Search before you build**
- Problem: You hand-roll a solution, spend hours getting it right, then discover an existing library that does it better.
- Solution: Before building anything non-trivial, spend 5 minutes searching for existing solutions.
- CLAUDE.md rule: `Before building anything: search for existing solutions first ("[language] library for [thing]").`

**Dead features are invisible until you look**
- Problem: --detach mode existed in setup.py for months. Nobody used it. 50 lines of dead code path.
- Solution: Periodically audit: for each feature, is it used? Documented? Tested? If zero on all three, delete it.
- CLAUDE.md rule: `Periodically audit features: used? documented? tested? If none, delete.`

**Docs are code — they rot the same way**
- Problem: README referenced agents/, MCP servers, --detach, bash setup — all stale after cleanup.
- Solution: Treat doc updates as part of every code change. When deleting a feature, grep every .md file.
- CLAUDE.md rule: `When deleting or renaming a feature, grep every .md file for references. Update them all.`

### Process conventions

**Migration testing catches transition bugs**
- Problem: Converting bash hooks to Python meant old settings.json entries needed to coexist with new ones.
- Solution: Test the migration path explicitly: uninstall old → install new → verify. Test the transition, not just the end state.
- CLAUDE.md rule: `When changing formats/locations, test the migration path (old → new → verify), not just the end state.`

**Parallel independent tasks, sequential dependent ones**
- Problem: Running checks one-at-a-time is slow. Running dependent steps in parallel produces issues.
- Solution: Identify independent vs dependent tasks. Parallelize independent ones.
- CLAUDE.md rule: `Run independent tasks in parallel (e.g., two test suites). Run dependent tasks sequentially (e.g., delete then verify).`

### Prompting conventions

**Specificity beats length**
- Problem: Long, vague instructions produce generic results. "Make the code better" wastes a turn.
- Solution: Be specific about WHAT and WHERE. "Remove do_detach at line 404" beats "simplify setup.py."
- CLAUDE.md rule: `Be specific: file paths, line numbers, function names. Not "improve the code."`

**Tell the AI what NOT to do**
- Problem: AI adds docstrings, type hints, error handling, and refactoring you didn't ask for.
- Solution: Explicitly constrain scope.
- CLAUDE.md rule: `Only change what's requested. Don't add comments, docstrings, or refactoring to unchanged code.`

## Format in target project's CLAUDE.md

When `/bootstrap` seeds these into a project, they appear as concise one-line rules:

```markdown
## AI Workflow Conventions

- Before multi-file changes, list all files that reference the changed component. Update them all together.
- For non-trivial tasks, write a plan listing every file to modify before writing code.
- After bulk delete/rename/refactor, verify for leftover artifacts (empty dirs, stale links, __pycache__).
- One language per operation — don't shell out to another language for parsing or formatting.
- Before building anything: search for existing solutions first.
- When deleting a feature, grep every .md file for references.
- Be specific: file paths, line numbers, function names. Not "improve the code."
- Only change what's requested. Don't add comments, docstrings, or refactoring to unchanged code.
```

The full problem/solution context lives in `prompts/ai-conventions.md` in the toolkit repo. The CLAUDE.md in each project just gets the concise rules.

## Open questions
- Should `/bootstrap` auto-include these conventions, or ask "Include AI workflow conventions?" as an opt-in step?
- Should there be a skill that AUDITS a project's CLAUDE.md against these conventions (checks for missing rules)?
- As new conventions are learned, should there be a way to propagate updates to projects that already have the old set?
