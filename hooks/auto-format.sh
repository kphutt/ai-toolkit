#!/bin/bash
# Auto-format files after Write/Edit tool calls.
# Hook type: PostToolUse
# Runs the appropriate formatter based on file extension.

# Only run after Write or Edit
if [[ "$CLAUDE_TOOL_NAME" != "Write" && "$CLAUDE_TOOL_NAME" != "Edit" ]]; then
  exit 0
fi

# Extract file path from tool input (stdin)
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]]; then
  exit 0
fi

EXTENSION="${FILE_PATH##*.}"

case "$EXTENSION" in
  py)
    if command -v black &>/dev/null; then
      black --quiet "$FILE_PATH" 2>/dev/null
    elif command -v ruff &>/dev/null; then
      ruff format --quiet "$FILE_PATH" 2>/dev/null
    fi
    ;;
  js|jsx|ts|tsx|json|css|md|yaml|yml)
    if command -v prettier &>/dev/null; then
      prettier --write --log-level error "$FILE_PATH" 2>/dev/null
    fi
    ;;
  go)
    if command -v gofmt &>/dev/null; then
      gofmt -w "$FILE_PATH" 2>/dev/null
    fi
    ;;
  rs)
    if command -v rustfmt &>/dev/null; then
      rustfmt "$FILE_PATH" 2>/dev/null
    fi
    ;;
esac

# Always succeed — formatting is best-effort, never block the tool
exit 0
