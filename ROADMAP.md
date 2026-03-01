# Roadmap

- **`/hygiene` — Codebase entropy scanner** — Mechanical scan for dead code, doc drift, orphaned artifacts. Periodic audit, not pre-push. See [brainstorm](docs/design/hygiene/brainstorm.md).

- **`/arch-review` — Architecture coherence review** — Top-down review for wrong boundaries, feature incoherence, pattern inconsistencies, tech stack misfits. The "bash calling python calling bash" detector. See [brainstorm](docs/design/arch-review/brainstorm.md).

- **`/landscape` — External research and industry comparison** — Web-search-based research skill. Answers questions `/arch-review` raises by checking standards, community practice, alternatives, and sustainability. See [brainstorm](docs/design/landscape/brainstorm.md).

- **`/project-success` — Project success factors review** — Evaluate what makes a project take off and stay useful. Not just what's missing but what's working, what could be stronger, and what separates projects that thrive from ones that stall. Onboarding experience, API clarity, documentation quality, test confidence, community readiness, architectural resilience. Relationship to other review skills TBD. See [brainstorm](docs/design/project-success/brainstorm.md).

- **Portable AI conventions** — Template of CLAUDE.md rules seeded into new projects via `/bootstrap`. Lessons from AI-assisted development turned into active rules, not a passive playbook. See [brainstorm](docs/design/ai-conventions/brainstorm.md).

- **AI workflow guide** — Human-readable reference for people learning to work effectively with AI coding assistants. Shareable with coworkers. Practical problem/solution format, grouped by topic. See [brainstorm](docs/design/ai-guide/brainstorm.md).

- **`/persona-review` — Expert persona design review** — Orchestrate 2-4 domain expert personas to critique a plan/design from orthogonal angles in parallel. Each persona runs as a separate agent with a prompt from prompt-lenses. Results are reconciled to identify conflicts and find synthesis. Emerged from text-adventure-v2 combat initiative planning where Pike (Go idiom), Muratori (performance), and Fowler (architecture) each caught issues the others missed.

- **`/decompose` — Initiative decomposition** — Break a large initiative into bite-sized phases. Each phase has clear scope boundaries (in/out), dependencies on prior phases, a "done when" condition, and decision gates between phases. Outputs a phased backlog document. Based on the decomposition philosophy from the combat initiative.

- **Forward-looking notes convention** — Bake into `/bootstrap` project templates. Every plan/design doc includes a "Forward-Looking Notes" section documenting decisions explicitly NOT made, with rationale for why they're safe to defer and what would trigger revisiting them.
