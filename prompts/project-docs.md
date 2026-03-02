<!-- Reference copy: kphutt/.github/README.md — keep in sync -->

# Project docs convention

Standard documentation structure for all repositories. One system, every project.

## Structure

```
ROADMAP.md                              # root — prioritized big rocks
docs/
  decisions/
    0001-short-title.md                 # one decision per file
    0002-short-title.md
  design/
    {initiative}/
      brainstorm.md                     # required — exploration scratchpad
      backlog.md                        # optional — phased plan for larger work
      principles.md                     # optional — design laws for design-heavy features
```

## ROADMAP.md

The PM view. Prioritized list of what's next. This is the project-level backlog — no separate project-level backlog file. Items are big rocks (features, refactors, architectural changes). Mark completed items with ~~strikethrough~~ and checkmark. Initiative-level backlogs live in `docs/design/{initiative}/backlog.md` (see below).

## Decision records (`docs/decisions/`)

One file per decision, numbered sequentially (`0001`, `0002`, ...). Append-only — never edit after writing. If a decision is reversed, write a new record that supersedes it.

### Template

```markdown
# Short title (verb phrase)

## Status
Accepted | Superseded by 0042

## Context
What's the situation? What forces are at play? Value-neutral facts.

## Decision
What did we decide? "We will..." in active voice.

## Consequences
What follows from this — good, bad, and neutral.
```

### When to write one

- You chose between alternatives (language, library, architecture)
- You discovered something surprising that changed your approach
- You'd be annoyed if future-you had to re-derive the reasoning
- You wouldn't — skip it. Not every choice needs a record.

## Initiative brainstorms (`docs/design/{name}/brainstorm.md`)

Required for every initiative. Dump sub-tasks, open questions, half-baked ideas, trade-off analysis before building. Messy by design. When something settles, it graduates to a decision record in `docs/decisions/`.

## Initiative backlogs (`docs/design/{name}/backlog.md`)

Optional — use when an initiative has multiple phases that ship independently. Each phase has:

- **Goal** — one sentence, what the user gets
- **What's in scope** — bullet list of concrete deliverables
- **What's NOT in scope** — explicit boundaries (prevents scope creep)
- **Done when** — acceptance criteria

Mark completed phases with ~~strikethrough~~. A contributor should be able to pick up the next phase cold by reading the backlog without needing prior context.

## Initiative principles (`docs/design/{name}/principles.md`)

Optional — use for design-heavy features where multiple decisions share underlying rules. Immutable design laws that the team commits to (e.g., "No UI state in the database", "Every action is reversible"). Skip for small or incremental work.

## Lifecycle

```
ROADMAP.md item → brainstorm → decisions → code
```

## What NOT to do

- No project-level backlog file — the roadmap is the project backlog (initiative-level backlogs in `docs/design/` are encouraged for phased work)
- No decisions inside initiative folders — they're project-wide, not initiative-scoped
- No formal RFC process for solo/small team work — that's for collecting feedback from others
- No maintaining a decision index file — `ls docs/decisions/` is the index
