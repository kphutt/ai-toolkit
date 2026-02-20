#!/bin/bash
# Logs every Claude Code tool call to a file.
# Hook type: PostToolUse
# Handy for reviewing what Claude actually did in a session.

LOG_FILE="${HOME}/.claude/tool-use.log"
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
SESSION_ID="${CLAUDE_SESSION_ID:-no-session}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "${TIMESTAMP} | ${SESSION_ID} | ${TOOL_NAME}" >> "${LOG_FILE}"
