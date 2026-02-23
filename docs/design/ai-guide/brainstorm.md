# AI Workflow Guide — Human-Readable Reference

A shareable document for people learning to work effectively with AI coding assistants. Practical guidance organized by topic, written in problem/solution format from real experience.

**What this is:** A reference doc for humans — not CLAUDE.md rules (that's the [ai-conventions](../ai-conventions/brainstorm.md) initiative). Not a tutorial for a specific tool. Not a decision log (those go in docs/decisions/).

**Key difference from ai-conventions:** The ai-conventions initiative produces terse rules like `"Before multi-file changes, list all files that reference the changed component."` This guide explains the *why* and *how* in human-friendly prose: "When we deleted the MCP servers directory, we updated README but forgot to check CLAUDE.md, ROADMAP.md, and environment.md — all of which still referenced it. The fix took a second pass to catch everything. Now we always grep all .md files before finishing a multi-file change."

**Audience:** Developers who are starting to use AI coding tools (or want to get better). Should be useful whether they use Claude Code, Copilot, Cursor, or any AI assistant.

## Content Areas

### 1. Planning & scoping
How to write good prompts for AI. When to use plan mode. How to break big tasks into phases. Why specificity matters more than length.

Real examples from this session:
- "Implement the following plan: [detailed 6-section plan]" worked perfectly — every file, every change, specific actions
- "Clean up this repo" would have produced scattered, incomplete changes
- Plan mode for the post-cleanup design session: explored → designed → got approval → will execute
- Breaking the cleanup into lettered sections (A-F) with explicit file lists prevented missed updates

### 2. Verification patterns
Why every bulk operation needs a verification pass. The "double check" pattern. Why tests before AND after.

Real examples from this session:
- `git rm -rf mcp-servers/` removed tracked files but left `__pycache__/` behind — had to manually clean up
- Deleting .sh hook source files left hard links in `~/.claude/hooks/` as orphaned regular files
- First verification pass said "all clean" — second pass ("double check everything") found the leftover directory
- Running all 18 setup.py tests + all 13 hook tests after changes caught nothing broken, confirming correctness

### 3. Architecture decisions
How to spot unnecessary language boundaries. When hand-rolling is justified vs when to use a library. How dead features accumulate invisibly.

Real examples from this session:
- Bash hooks calling `python -c` for JSON parsing: 3 languages (bash → python → JSON) for a one-language job
- `setup.sh` wrapping `setup.py`: the bash wrapper added nothing but a second failure mode
- `--detach` mode in setup.py: 50 lines of code, zero users, never documented properly — classic dead feature
- `/commit` skill duplicated Claude Code's built-in commit functionality — superseded feature

### 4. Working with AI effectively
Tell it what NOT to do. Constrain scope explicitly. How to use plan mode for non-trivial work. When to break context and start fresh. How to review AI output (don't just trust it).

Patterns that work:
- "Double check everything" as an explicit second-pass instruction
- Specific file-level plans with line numbers
- "Don't add docstrings, don't refactor surrounding code, just change X"
- Plan mode for anything touching >3 files
- Asking AI to think longer ("keep thinking, 30+ minutes if needed") for design work

Patterns that don't work:
- Vague instructions ("make it better", "clean things up")
- Trusting first-pass verification without a second check
- Assuming AI remembers constraints from earlier in the conversation
- Long conversations without context breaks (compaction loses nuance)

### 5. Common pitfalls
Things that go wrong repeatedly and how to avoid them.

- "I asked for X and got X plus a bunch of unrequested changes" → constrain scope explicitly
- "The AI said it was done but left artifacts behind" → always verify with a second pass
- "Long prompts produced worse results than short specific ones" → specificity > length
- "I deleted files but docs still reference them" → grep all .md files as part of every deletion
- "The migration worked in testing but broke on the real machine" → test the transition path, not just the end state
- "I hand-rolled something that already existed as a library" → search before building
- "A feature existed for months with zero users" → periodic audit: used? documented? tested?

## Format
- Grouped by topic, not dated
- Each entry: problem description (what happened), lesson (what we learned), practical advice (what to do next time)
- Written for humans to skim and share — not terse rules, but not walls of text either
- Real examples from actual sessions make it concrete, not abstract

## Implementation Options
- A standalone markdown file in the toolkit repo (e.g., `prompts/ai-workflow-guide.md`)
- Could be generated/updated by a skill that interviews you after a session (retrospective skill — `/retro`?)
- Could be a template that `/bootstrap` offers to include in new projects alongside the CLAUDE.md conventions
- Could live on a personal blog or wiki for broader sharing

## Open Questions
- Where does it live? `prompts/` (like other templates), `docs/` (like other docs), or root (like README)?
- Should there be a `/retro` skill that walks through a post-session review and appends to the guide?
- How does it stay current as lessons are learned in future sessions?
- Should it be one file or split by topic (one file per content area)?
- How much should it reference specific tools (Claude Code) vs. be tool-agnostic?
