#!/usr/bin/env python3
"""Log every Claude Code tool call to a file.

Hook type: PostToolUse (all tools)
"""

import os
import sys
from datetime import datetime
from pathlib import Path


def main():
    log_file = Path.home() / ".claude" / "tool-use.log"
    tool = os.environ.get("CLAUDE_TOOL_NAME", "unknown")
    session = os.environ.get("CLAUDE_SESSION_ID", "no-session")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} | {session} | {tool}\n")
    except OSError:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
