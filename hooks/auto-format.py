#!/usr/bin/env python3
"""Auto-format files after Write/Edit tool calls.

Hook type: PostToolUse (Write|Edit)

Runs the first available formatter by extension:
  .py  → black, ruff
  .js/.ts/.css/… → prettier
  .go  → gofmt
  .rs  → rustfmt

Best-effort: silently skips if no formatter is installed. Always exits 0.
"""

import json
import os
import shutil
import subprocess
import sys


FORMATTERS = {
    "py": [["black", "--quiet"], ["ruff", "format", "--quiet"]],
    "js": [["prettier", "--write", "--log-level", "error"]],
    "jsx": [["prettier", "--write", "--log-level", "error"]],
    "ts": [["prettier", "--write", "--log-level", "error"]],
    "tsx": [["prettier", "--write", "--log-level", "error"]],
    "json": [["prettier", "--write", "--log-level", "error"]],
    "css": [["prettier", "--write", "--log-level", "error"]],
    "md": [["prettier", "--write", "--log-level", "error"]],
    "yaml": [["prettier", "--write", "--log-level", "error"]],
    "yml": [["prettier", "--write", "--log-level", "error"]],
    "go": [["gofmt", "-w"]],
    "rs": [["rustfmt"]],
}


def main():
    tool = os.environ.get("CLAUDE_TOOL_NAME", "")
    if tool not in ("Write", "Edit"):
        return 0

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    file_path = data.get("file_path", "")
    if not file_path or not os.path.isfile(file_path):
        return 0

    ext = file_path.rsplit(".", 1)[-1] if "." in file_path else ""
    candidates = FORMATTERS.get(ext, [])

    for cmd_prefix in candidates:
        if shutil.which(cmd_prefix[0]):
            try:
                subprocess.run(cmd_prefix + [file_path],
                               capture_output=True, timeout=30)
            except (subprocess.TimeoutExpired, OSError):
                pass
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
