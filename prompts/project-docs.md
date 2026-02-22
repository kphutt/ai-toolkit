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
      brainstorm.md                     # optional scratchpad per initiative
```

## ROADMAP.md

The PM view. Prioritized list of what's next. This *is* the backlog — no separate backlog file. Items are big rocks (features, refactors, architectural changes). Mark completed items with ~~strikethrough~~ and checkmark.

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

Optional. Create when an initiative needs design exploration before building. Dump sub-tasks, open questions, half-baked ideas, trade-off analysis. Messy by design. When something settles, it graduates to a decision record in `docs/decisions/`.

## Lifecycle

```
ROADMAP.md item → (optional) brainstorm → decisions → code
```

## What NOT to do

- No separate backlog file — the roadmap is the backlog
- No decisions inside initiative folders — they're project-wide, not initiative-scoped
- No formal RFC process for solo/small team work — that's for collecting feedback from others
- No maintaining a decision index file — `ls docs/decisions/` is the index
