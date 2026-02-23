# /landscape — External Research and Industry Comparison

External research skill. Answers the questions that `/arch-review` raises by searching the web, GitHub, and official docs. Compares your approach against industry patterns, formal standards, and community practice. Slow by nature — requires web searching.

**Why separate from arch-review:** Web research is slow (minutes, not seconds), noisy (lots of irrelevant results to filter), and requires different tools (WebSearch, WebFetch). Mixing it into arch-review would make a fast local analysis take 10x longer. Run arch-review first to identify questions, then landscape to answer them.

**Implementation:** Create `skills/landscape/SKILL.md`. Frontmatter: `name: landscape`, `description: Research how the industry solves the same problems — standards, tools, community patterns`, `origin: personal`, `user-invocable: true`, `allowed-tools: [Read, Grep, Glob, Bash, WebSearch, WebFetch]`, `argument-hint: "<topic-or-component>"`. Add to `environment.md` and `README.md`.

## Research Phases (sequential — each builds on the last)

The order matters. You can't evaluate alternatives without knowing the standards. You can't judge sustainability without knowing the community. Each phase uses what was learned in previous phases to refine its searches. This is inherently iterative — early findings reshape later questions.

### Phase 1. Official standards and specs (do this FIRST)
- What does the tool/framework officially support? Read the docs before anything else.
- For Claude Code: hook specs, skill format, settings.json schema, supported events, what's stable vs experimental
- For libraries/frameworks: official schemas, RFCs, documented best practices from the authors
- Key question: "What is the GROUND TRUTH of what's possible?"
- This phase establishes the foundation. Everything after this references what you learn here.
- Example: "Are PreToolUse/PostToolUse the only hook events? What format does SKILL.md officially support? What's documented vs undocumented?"

### Phase 2. Community practice (what do people actually do?)
- NOW that you know the official capabilities, search for how people actually use them
- Search GitHub for repos solving the same problem — look at structure, conventions, install patterns
- Search for blog posts, tutorials, discussions about the same tools
- Key question: "Given what's officially supported (Phase 1), what's the established convention?"
- Adjust searches based on Phase 1 findings — if you discovered a feature you didn't know about, search for how others use it
- Example: "Now that we know the hook spec, how do other Claude Code users structure their hooks? Is anyone using features we're not?"

### Phase 3. Alternative approaches (completely different paradigms)
- NOW that you know what exists (Phase 1) and how people use it (Phase 2), look for different paradigms
- Not "use library X instead of Y" but "should this be a hook at all, or should it be an MCP server? A CLAUDE.md rule? A git hook?"
- Look at adjacent ecosystems that solve the same underlying problem differently
- Key question: "Is there a fundamentally better approach that Phase 1-2 didn't surface because I was looking within the current paradigm?"
- Example: "VS Code extensions, pre-commit framework, GitHub Actions — how do THEY handle file protection and pre-push checks? Is their approach better?"

### Phase 4. Tool and library landscape — "someone must have solved this"
- NOW that you know the right paradigm (Phase 3), evaluate the specific tools
- For EVERY hand-rolled component: search for existing solutions FIRST. Someone probably has solved this. Check PyPI, npm, crates.io, Go modules, GitHub.
- Evaluate existing solutions honestly: is the existing solution better, worse, or differently scoped? Would adopting it simplify your code or add a dependency you don't want?
- For dependencies you already use: are they maintained? Are there better alternatives?
- For the language: is it the right one for this component?
- Key question: "Am I building something that already exists? If so, is my version justified or am I wasting effort?"
- Example: "We hand-rolled 450 lines of cross-platform symlink management. Is there a Python library for this? If so, is it mature enough to trust, or is hand-rolling it the right call for our constraints?"

### Phase 5. Sustainability (will this still work?)
- NOW that you've evaluated the whole stack, assess its longevity
- Check changelogs, deprecation notices, API stability promises, roadmaps
- Check community health: recent commits, issue response time, contributor count
- Key question: "Given everything we've learned, is this built on stable ground?"
- Example: "Claude Code's hook system — is it marked stable? Are there deprecation warnings? What does the roadmap say about skills/hooks?"

### Phase 6. Existential check — should this exist at all?
- This is the LAST phase because you need ALL the context from Phases 1-5 to answer it honestly
- Given what you now know about standards, community, alternatives, tools, and sustainability: does this component justify its existence?
- Is the complexity proportional to the value? Count: lines of code, files maintained, cognitive overhead. Compare against the alternative of NOT having it.
- Is the problem you're solving the RIGHT problem? Now that you've seen the full landscape, would solving a different problem be higher-leverage?
- Key question: "If I deleted this entirely and did the simplest possible thing instead, what would I actually lose?"
- Example: "We have 450-line setup.py with state tracking and manifest parsing. The community mostly just symlinks manually. Is the installer worth maintaining, or should we simplify to a 20-line script?"

## Output format

Research report with sources. Each finding: source (URL or search terms used), what was found, relevance assessment with reasoning.

```
Landscape Report: [topic] (Feb 2026)
=====================================

## Standards & Specs

### Claude Code hook format
Source: [Anthropic docs URL]
Finding: Hook events are PreToolUse, PostToolUse, Notification, and
Stop. We're using the first two correctly. Stop event could be useful
for session-end cleanup (we're not using it).
Relevance: HIGH — we may be missing a useful event.

## Community Practice

### Other Claude Code toolkits
Source: [GitHub search results]
Finding: 3 public repos found with Claude Code skill collections.
Most use flat SKILL.md files (same as us). None use a setup.py
installer — they just tell users to symlink manually.
Relevance: MEDIUM — our installer is more sophisticated than the
norm, which is either a feature or over-engineering.

## Alternative Approaches

### Protect-files via settings.json deny rules
Finding: Claude Code supports `deny: ["Write(.env)"]` rules in
settings.json. This could replace protect-files.py entirely.
Trade-off: Deny rules are simpler but less flexible (can't match
patterns like "credentials*"). Hook gives better error messages.
Relevance: HIGH — worth evaluating whether the hook adds enough
value over built-in deny rules.

## Summary
- 1 HIGH finding: investigate Stop hook event
- 1 HIGH finding: evaluate deny rules vs protect-files hook
- 1 MEDIUM finding: our installer is unusually sophisticated
```

## Time-sensitivity

Landscape findings are snapshots, not permanent truths. The industry moves fast — what's standard today may be deprecated in 6 months. The output should:
- Include the date of the research at the top of the report
- Flag findings that are likely time-sensitive (e.g., "Claude Code hooks are in beta" — this will change)
- Recommend a re-run cadence based on how fast the relevant space is moving
- Note: if a previous landscape report exists (from a prior session), compare against it — "last time we checked, X was the standard. Now Y has emerged."

This means `/landscape` is re-runnable by design. Running it today vs. 6 months from now should produce meaningfully different findings as the ecosystem evolves.
