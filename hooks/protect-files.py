#!/usr/bin/env python3
"""Block writes to sensitive files (secrets, keys, credentials).

Hook type: PreToolUse (Write|Edit)
"""

import json
import os
import sys


def main():
    """Block Write/Edit to .env, .pem, .key, and credentials files."""
    tool = os.environ.get("CLAUDE_TOOL_NAME", "")
    if tool not in ("Write", "Edit"):
        return 0

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    file_path = data.get("file_path", "")
    if not file_path:
        return 0

    basename = os.path.basename(file_path)

    if basename == ".env" or basename.startswith(".env."):
        print(f"BLOCKED: Cannot write to environment file: {basename}")
        return 2
    if basename.endswith((".pem", ".key")):
        print(f"BLOCKED: Cannot write to key/certificate file: {basename}")
        return 2
    if basename.startswith("credentials") or basename.endswith("credentials.json"):
        print(f"BLOCKED: Cannot write to credentials file: {basename}")
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
