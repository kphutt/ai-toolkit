#!/bin/bash
# macOS desktop notification when Claude finishes or needs attention.
# Hook type: Notification
# Requires macOS (uses osascript). Silent no-op on other platforms.

# Only run on macOS
if [[ "$(uname)" != "Darwin" ]]; then
  exit 0
fi

MESSAGE="${1:-Claude Code needs your attention}"

osascript -e "display notification \"$MESSAGE\" with title \"Claude Code\"" 2>/dev/null

exit 0
