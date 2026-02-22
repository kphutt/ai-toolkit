#!/bin/bash
# Convenience wrapper — delegates to setup.py
exec python "$(dirname "$0")/setup.py" "$@" 2>/dev/null || exec python3 "$(dirname "$0")/setup.py" "$@"
