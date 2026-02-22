#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python "$SCRIPT_DIR/setup.py" "$@" 2>/dev/null || python3 "$SCRIPT_DIR/setup.py" "$@"
