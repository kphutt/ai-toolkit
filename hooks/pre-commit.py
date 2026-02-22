#!/usr/bin/env python3
"""Block unsafe git operations: push without /preflight, --no-verify, staged secrets.

Hook type: PreToolUse (Bash)
"""

import json
import os
import sys


def main():
    tool = os.environ.get("CLAUDE_TOOL_NAME", "")
    if tool != "Bash":
        return 0

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    command = data.get("command", "")
    if not command:
        return 0

    if "git push" in command:
        print('{"decision":"block","reason":"Have you run /preflight? Run it before pushing, then retry."}',
              file=sys.stderr)
        return 2

    if "git commit" not in command:
        return 0

    if "--no-verify" in command:
        print('{"decision":"block","reason":"--no-verify is not allowed. Run hooks properly."}',
              file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
