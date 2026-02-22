---
name: add-debug-logging
description: Add a --debug flag and structured file logging to the current project
origin: personal
user-invocable: true
allowed-tools: [Read, Write, Edit, Grep, Glob, Bash]
argument-hint: "[entry-point file]"
---

Add a `--debug` flag (or language equivalent) that writes structured diagnostic logs to a `debug.log` file. The log should be useful for tracing program behavior without a debugger.

## 1. Detect the Project

- If an argument is given, use that as the entry point.
- Otherwise, detect the language and find the entry point:
  - **Go**: `main.go` or file containing `func main()`
  - **Python**: `main.py`, `app.py`, `cli.py`, or file with `if __name__`
  - **JavaScript/TypeScript**: `index.js/ts`, `main.js/ts`, `app.js/ts`, or `"main"` in `package.json`
  - **Rust**: `src/main.rs`
- Read the entry point and any key modules to understand the program's structure before making changes.

### Multiple entry points

If the project has multiple independent entry points (e.g., standalone scripts, separate experiments each with their own `run.js` or `main.py`):

1. **Ask the user** which entry point(s) to instrument, or whether to do all of them.
2. **Create a shared debug utility module** (e.g., `debug_log.py`, `lib/debug.js`) that all entry points can import. The module should:
   - Export an `init(flag)` function that creates the logger + file only when the flag is set
   - Export a `log(tag, message)` function (or similar) so each script doesn't reimplement logging
3. **Add `--debug` to each entry point**, wiring it to the shared module.

This avoids duplicating logging boilerplate across N files while keeping each script independently runnable.

## 2. Add the Debug Flag

Add a command-line flag that enables debug logging. It must be **off by default** — normal runs produce no log file.

| Language | Pattern |
|----------|---------|
| Go | `flag.Bool("debug", ...)` — parse in `main()`, create `log.Logger` |
| Python | `argparse` add `--debug`, configure `logging` module with `FileHandler` |
| JS/TS | `process.argv.includes('--debug')`, write with `fs.appendFileSync` or a logger |
| Rust | `clap` or `std::env::args`, use `log` + `simplelog` or write directly |

## 3. Add Structured Log Lines

### Startup — log the initial state of the program

Log whatever is relevant to understand the starting conditions. Examples:
- Configuration values loaded
- Resources discovered (files, connections, rooms, routes, etc.)
- Environment info (relevant env vars, working directory)

Use a tag prefix like `[INIT]`, `[CONFIG]`, `[MAP]`, `[START]`, etc.

### Runtime — log each significant action

Every user command, API call, request, or major decision point should produce a log line. Always include context: what triggered it, what the result was, and any state change.

Format: `[TAG] key=value key=value ...` or `[TAG] descriptive message`

Standard tags to use where applicable:
- `[CMD]` — user command or input received
- `[RSP]` — response or output produced
- `[REQ]` / `[RES]` — outbound request / inbound response (APIs, HTTP)
- `[ERR]` — errors (always log these, even without --debug)
- `[STATE]` — significant state transitions
- `[SCORE]` / `[METRIC]` — numeric changes worth tracking

Include contextual fields that help correlate log lines:
- Timestamp (usually from the logger itself)
- Turn/sequence/request number
- Current context (room, route, user, etc.)

### Log file behavior
- **Fresh each run** — overwrite/truncate on startup (previous session's log isn't useful since context has changed)
- **File name**: `debug.log`
- **No log file created** when `--debug` is not passed

## 4. Update .gitignore

Add `debug.log` to `.gitignore` if not already present.

## 5. Verify

- Run the project's build command to confirm it compiles/parses.
- Run existing tests if present to confirm nothing broke.

## Output

Report what was added:
```
Debug logging added:
- Flag: --debug
- Log file: debug.log (created only when --debug is passed)
- Startup: [list what gets logged]
- Runtime: [list what gets logged]
- .gitignore updated
```
