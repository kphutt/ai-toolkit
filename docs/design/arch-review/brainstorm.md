# /arch-review — Architecture Coherence Review

Step-back holistic review. Finds problems no single-file review catches: wrong abstraction boundaries, feature incoherence, pattern inconsistencies, tech stack misfits. This is the "bash calling python calling bash" detector.

**Not code-review** (bottom-up: "is this function correct?"). Arch-review is top-down: "should this function exist? Is it in the right place?"

**Implementation:** Create `skills/arch-review/SKILL.md`. Frontmatter: `name: arch-review`, `description: Review architecture for unnecessary boundaries, incoherence, and pattern inconsistencies`, `origin: personal`, `user-invocable: true`, `allowed-tools: [Read, Grep, Glob, Bash]`, `argument-hint: "[directory]"`. Add to `environment.md` and `README.md`.

## Review Areas

### 1. Boundary analysis
- Map files by language. Find every place one language invokes another (subprocess, exec, shell-out, FFI)
- For each boundary: is it necessary? Could the caller do this natively?
- Flag boundaries that exist because of history rather than necessity
- This is the check that would have caught bash hooks calling `python -c` for JSON parsing
- Look for: subprocess.run calling scripts in a different language, shell=True with inline scripts, os.system calls, backtick interpolation

### 2. Tech stack fit
- For each major component, ask: is the language/tool the right one for this job?
- Look at what the code actually DOES vs what the language is good at — e.g., "bash for JSON parsing" is a mismatch; "Python for symlink management" is fine
- Check for tools/libraries being used in unusual ways (fighting the framework)
- Check for hand-rolled solutions where a standard library or well-known package exists
- This check identifies QUESTIONS ("is bash right for hooks?") — `/landscape` answers them with external research

### 3. Feature coherence
- Inventory features from manifests, entry points, docs
- For each: fully implemented? Documented? Tested? Actually used?
- Identify half-implemented features (code exists but no docs, or docs but partial code, or config references something that doesn't work end-to-end)
- Identify superseded features (two things doing roughly the same job, one newer than the other)
- Check: does every documented feature actually work? Does every working feature have documentation?

### 4. Convention consistency
- Sample the project's patterns: naming conventions, error handling style, config loading mechanism, logging approach, test organization
- Find deviations from the majority pattern
- Flag only significant deviations — not style nits (those are for formatters)
- Example: if 8/10 modules use logging.getLogger(__name__) but 2 use print(), flag the 2
- Example: if most config comes from env vars but one module reads a JSON file, flag it

### 5. Abstraction assessment
- Find wrapper functions that add no value (just forward to another function with the same args)
- Find the same logic pattern repeated 3+ times without abstraction
- Find abstractions with only one implementation (premature generalization)
- Find "god modules" that everything imports from
- Find modules that import things they don't use

## Output format

More narrative than `/hygiene`. Each finding includes an assessment explaining WHY it's a problem (or why it's actually fine — false positive explanations build trust).

```
Architecture Review
===================

## Boundary Analysis

### [BOUNDARY] bash → python in hooks/
All 4 hooks are .sh files that invoke `python -c` for JSON parsing.
Assessment: Unnecessary boundary. Hooks should be native Python —
the project is Python-based, JSON parsing is a stdlib one-liner, and
the bash wrapper adds nothing but a second failure mode.
Action: Convert all hooks to Python, eliminate bash dependency.

## Feature Coherence

### [SUPERSEDED] /commit skill overlaps with Claude Code built-in
Both create structured git commits. The skill adds no unique formatting
or workflow that the built-in doesn't provide.
Assessment: Dead feature. Delete skill and remove from manifest.

## Convention Consistency

### [OK] log-tool-use.py doesn't parse stdin (others do)
protect-files.py, pre-commit.py, and auto-format.py all parse stdin JSON.
log-tool-use.py only reads env vars.
Assessment: Legitimate divergence — log-tool-use.py doesn't need stdin
data (it only logs tool name and session from env vars). Not a problem.

## Summary: 1 boundary issue, 1 superseded feature, 1 OK (no action)
```

---

## When to run what

| Trigger | Skills | Why |
|---------|--------|-----|
| After a major refactor | `/hygiene` → `/arch-review` | Debris check + coherence check |
| Starting a new initiative | `/arch-review` → `/landscape` | Current state + industry context |
| Monthly maintenance | `/hygiene` | Entropy check — catch drift before it accumulates |
| Choosing tech/approach | `/landscape` | Research before committing to an approach |
| After `/landscape` surfaces concerns | `/arch-review` | Re-evaluate local architecture with new external context |
| Something feels wrong but you can't name it | `/arch-review` | Top-down sniff test |

## Meta: Is this the right thing to build?

The feedback loop these tools create:
1. `/hygiene` finds mechanical problems (dead code, drift) → produces a report
2. `/arch-review` finds structural problems (boundaries, incoherence, tech fit) → produces an assessment
3. `/landscape` researches external context (standards, alternatives, community) → produces a research report
4. The user enters plan mode to turn findings into a plan
5. Claude executes the plan
6. Portable conventions ensure the same mistakes don't recur in new projects

What this does NOT solve (and whether it matters):
- **Cross-session learning**: Claude forgets between sessions. Memory helps but is limited. Anthropic will build better persistence. → Not our problem.
- **Proactive detection**: These skills run on-demand, not continuously. Hooks catch some issues reactively, but a "code health monitor" doesn't exist. → Wait for better tools.
- **Multi-tool portability**: Skills are Claude Code-specific in format but the instructions are English. Trivial to adapt frontmatter for other tools.

What if we're wrong? The cost is ~4 SKILL.md files and 1 template. Easy to delete. Skills are auto-discovered, so unused ones don't affect anything. Low-risk experiment.

The real test: after building these, run `/hygiene` and `/arch-review` on the ai-toolkit itself. If they find problems we missed, they're valuable. `/landscape` should validate our whole approach against the industry.
