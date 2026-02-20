#!/bin/bash
# Re-outputs critical project reminders before context compaction.
# Hook type: PreCompact
# These reminders survive compaction so Claude retains key constraints.

# Check for CLAUDE.md in the current project
if [[ -f "CLAUDE.md" ]]; then
  echo "=== CRITICAL REMINDERS (from CLAUDE.md) ==="
  # Extract lines marked as critical (starting with "!!" or "IMPORTANT:")
  grep -iE '^\s*(!!|IMPORTANT:|CRITICAL:|NEVER |ALWAYS )' CLAUDE.md 2>/dev/null
  echo "=== END REMINDERS ==="
fi

# Always remind about safety
echo "REMINDER: Do not write to .env, *.pem, *.key, or credentials files."
echo "REMINDER: Never use --no-verify or --force without explicit user approval."

exit 0
