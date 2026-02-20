#!/bin/bash
# Blocks writes to sensitive files (secrets, keys, credentials).
# Hook type: PreToolUse

# Only check tools that write files
if [[ "$CLAUDE_TOOL_NAME" != "Write" && "$CLAUDE_TOOL_NAME" != "Edit" ]]; then
  exit 0
fi

# Read tool input from stdin
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

BASENAME=$(basename "$FILE_PATH")

# Block patterns
case "$BASENAME" in
  .env|.env.*)
    echo "BLOCKED: Cannot write to environment file: $BASENAME"
    exit 2
    ;;
  *.pem|*.key)
    echo "BLOCKED: Cannot write to key/certificate file: $BASENAME"
    exit 2
    ;;
  credentials*|*credentials.json)
    echo "BLOCKED: Cannot write to credentials file: $BASENAME"
    exit 2
    ;;
esac

exit 0
