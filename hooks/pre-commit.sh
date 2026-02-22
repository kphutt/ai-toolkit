#!/bin/bash
# Block commits that include secrets, debug logs, or --no-verify bypass
# Hook type: PreToolUse

# Only act on Bash tool calls
if [[ "$CLAUDE_TOOL_NAME" != "Bash" ]]; then
  exit 0
fi

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.command // empty')

# Only check git commit commands
if ! echo "$COMMAND" | grep -q 'git commit'; then
  exit 0
fi

# Block --no-verify flag
if echo "$COMMAND" | grep -q '\-\-no-verify'; then
  echo '{"decision":"block","reason":"--no-verify is not allowed. Run hooks properly."}' >&2
  exit 2
fi

# Check for staged .env files
STAGED_ENV=$(git diff --cached --name-only 2>/dev/null | grep -E '\.env($|\.)')
if [[ -n "$STAGED_ENV" ]]; then
  echo '{"decision":"block","reason":"Blocked: .env file is staged — remove it with git reset HEAD '"$STAGED_ENV"'"}' >&2
  exit 2
fi

# Check for staged key/pem files
STAGED_KEYS=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(key|pem)$')
if [[ -n "$STAGED_KEYS" ]]; then
  echo '{"decision":"block","reason":"Blocked: secret key file staged — '"$STAGED_KEYS"'"}' >&2
  exit 2
fi

# Check if debug.log is staged
STAGED_DEBUG=$(git diff --cached --name-only 2>/dev/null | grep -E '^debug\.log$')
if [[ -n "$STAGED_DEBUG" ]]; then
  echo '{"decision":"block","reason":"Blocked: debug.log is staged — add it to .gitignore"}' >&2
  exit 2
fi

exit 0
