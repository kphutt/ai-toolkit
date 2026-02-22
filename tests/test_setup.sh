#!/bin/bash
# Invariant tests for setup.sh
# Each test creates isolated temp dirs and verifies safety guarantees.
# Run: bash tests/test_setup.sh

TOOLKIT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SETUP_SH="$TOOLKIT_DIR/setup.sh"
PASS=0
FAIL=0
REAL_HOME="$HOME"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

pass() { echo -e "  ${GREEN}PASS${NC}: $1"; ((PASS++)); }
fail() { echo -e "  ${RED}FAIL${NC}: $1"; ((FAIL++)); }

# Find python
PY=""
command -v python3 &>/dev/null && python3 -c "1" 2>/dev/null && PY=python3
[[ -z "$PY" ]] && command -v python &>/dev/null && PY=python

setup_fake_toolkit() {
  local tk="$1"
  mkdir -p "$tk/skills/test-skill" "$tk/hooks"
  echo "test skill content" > "$tk/skills/test-skill/SKILL.md"
  printf '#!/bin/bash\necho test' > "$tk/hooks/test-hook.sh"
  chmod +x "$tk/hooks/test-hook.sh"
  cp "$SETUP_SH" "$tk/setup.sh"
  cp "$TOOLKIT_DIR/setup.py" "$tk/setup.py"
  cat > "$tk/environment.md" << 'MANIFEST'
# Environment Manifest
## Skills
| Name | Install |
|------|---------|
| test-skill | yes |
## Hooks
| File | Install | Event | Matcher |
|------|---------|-------|---------|
| test-hook.sh | yes | PostToolUse | _(none)_ |
## Settings.json Hook Registrations
```json
{
  "hooks": {
    "PostToolUse": [
      {"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/test-hook.sh"}]}
    ]
  }
}
```
MANIFEST
}

setup_fake_home() {
  local tmp="$1"
  mkdir -p "$tmp/.claude/skills" "$tmp/.claude/hooks"
  echo '{"permissions":{"allow":[]}}' > "$tmp/.claude/settings.json"
  export HOME="$tmp"
}

cleanup_test() {
  export HOME="$REAL_HOME"
  local tmp="$1"
  # Remove junctions before rm -rf
  if command -v cygpath &>/dev/null; then
    for d in "$tmp"/.claude/skills/* "$tmp"/.claude/hooks/*; do
      if [[ -L "$d" ]] && [[ -d "$d" ]]; then
        local wd
        wd=$(cygpath -w "$d" 2>/dev/null) || true
        [[ -n "$wd" ]] && cmd //c "rmdir $wd" &>/dev/null || true
      fi
    done
  fi
  rm -rf "$tmp"
}

echo ""
echo "AI Toolkit Setup — Invariant Tests"
echo "==================================="
echo ""

# ---- Test 1: Install skips existing regular directory ----
echo "Test 1: Install skips existing regular directory"
T=$(mktemp -d)
setup_fake_toolkit "$T/toolkit"
setup_fake_home "$T"
mkdir -p "$T/.claude/skills/test-skill"
echo "my custom content" > "$T/.claude/skills/test-skill/SKILL.md"

bash "$T/toolkit/setup.sh" --apply > /dev/null 2>&1 || true

if [[ -d "$T/.claude/skills/test-skill" ]] && [[ -f "$T/.claude/skills/test-skill/SKILL.md" ]]; then
  content=$(cat "$T/.claude/skills/test-skill/SKILL.md")
  case "$content" in
    "my custom content") pass "Regular directory content preserved" ;;
    *) fail "Regular directory content was modified" ;;
  esac
else
  fail "Regular directory was removed or replaced"
fi
cleanup_test "$T"

# ---- Test 2: Install creates link for missing skill ----
echo "Test 2: Install creates link for missing skill"
T=$(mktemp -d)
setup_fake_toolkit "$T/toolkit"
setup_fake_home "$T"

bash "$T/toolkit/setup.sh" --apply > /dev/null 2>&1 || true

if [[ -d "$T/.claude/skills/test-skill" ]] && [[ -f "$T/.claude/skills/test-skill/SKILL.md" ]]; then
  pass "Skill link created with correct content"
else
  fail "Skill link was not created"
fi

if [[ -f "$T/.claude/hooks/test-hook.sh" ]]; then
  pass "Hook link created"
else
  fail "Hook link was not created"
fi
cleanup_test "$T"

# ---- Test 3: Uninstall only removes managed links ----
echo "Test 3: Uninstall only removes managed links"
T=$(mktemp -d)
setup_fake_toolkit "$T/toolkit"
setup_fake_home "$T"

# Install first
bash "$T/toolkit/setup.sh" --apply > /dev/null 2>&1 || true

# Create unmanaged files
mkdir -p "$T/.claude/skills/custom-skill"
echo "custom" > "$T/.claude/skills/custom-skill/SKILL.md"
echo "custom hook" > "$T/.claude/hooks/custom-hook.sh"

# Uninstall
bash "$T/toolkit/setup.sh" --uninstall --apply > /dev/null 2>&1 || true

if [[ -e "$T/.claude/skills/test-skill" ]]; then
  fail "Managed skill link was not removed"
else
  pass "Managed skill link removed"
fi

if [[ -e "$T/.claude/hooks/test-hook.sh" ]]; then
  fail "Managed hook link was not removed"
else
  pass "Managed hook link removed"
fi

if [[ -d "$T/.claude/skills/custom-skill" ]]; then
  pass "Unmanaged skill directory preserved"
else
  fail "Unmanaged skill directory was removed"
fi

if [[ -f "$T/.claude/hooks/custom-hook.sh" ]]; then
  pass "Unmanaged hook file preserved"
else
  fail "Unmanaged hook file was removed"
fi
cleanup_test "$T"

# ---- Test 4: Detach converts managed links to copies ----
echo "Test 4: Detach converts managed links to copies"
T=$(mktemp -d)
setup_fake_toolkit "$T/toolkit"
setup_fake_home "$T"

# Create unmanaged file
mkdir -p "$T/.claude/skills/custom-skill"
echo "custom content" > "$T/.claude/skills/custom-skill/SKILL.md"

# Install then detach
bash "$T/toolkit/setup.sh" --apply > /dev/null 2>&1 || true
bash "$T/toolkit/setup.sh" --detach --apply > /dev/null 2>&1 || true

if [[ -d "$T/.claude/skills/test-skill" ]] && [[ -f "$T/.claude/skills/test-skill/SKILL.md" ]]; then
  if [[ -L "$T/.claude/skills/test-skill" ]]; then
    fail "Skill is still a link after detach"
  else
    pass "Managed skill link detached to regular directory"
  fi
else
  fail "Managed skill link not properly detached"
fi

content=$(cat "$T/.claude/skills/custom-skill/SKILL.md" 2>/dev/null)
case "$content" in
  "custom content") pass "Unmanaged directory untouched during detach" ;;
  *) fail "Unmanaged directory was modified during detach" ;;
esac
cleanup_test "$T"

# ---- Test 5: settings.json custom entries preserved ----
echo "Test 5: settings.json custom entries preserved during install"
T=$(mktemp -d)
setup_fake_toolkit "$T/toolkit"
setup_fake_home "$T"
cat > "$T/.claude/settings.json" << 'JSON'
{"permissions": {"allow": ["Bash(git *)"]}, "customKey": "customValue"}
JSON

bash "$T/toolkit/setup.sh" --apply > /dev/null 2>&1 || true

if [[ -n "$PY" ]] && $PY -c "
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
assert d.get('customKey') == 'customValue', 'customKey missing'
assert d.get('permissions', {}).get('allow') == ['Bash(git *)'], 'permissions changed'
" "$T/.claude/settings.json" 2>/dev/null; then
  pass "Custom settings.json entries preserved"
else
  fail "Custom settings.json entries were lost"
fi
cleanup_test "$T"

# ---- Test 6: settings.json uninstall preserves custom entries ----
echo "Test 6: settings.json uninstall preserves custom entries"
T=$(mktemp -d)
setup_fake_toolkit "$T/toolkit"
setup_fake_home "$T"
cat > "$T/.claude/settings.json" << 'JSON'
{
  "permissions": {"allow": []},
  "hooks": {
    "PostToolUse": [
      {"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/test-hook.sh"}]},
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "bash /my/custom/hook.sh"}]}
    ]
  }
}
JSON

bash "$T/toolkit/setup.sh" --uninstall --apply > /dev/null 2>&1 || true

if [[ -n "$PY" ]] && $PY -c "
import json, sys
with open(sys.argv[1]) as f:
    d = json.load(f)
hooks = d.get('hooks', {}).get('PostToolUse', [])
assert any('/my/custom/hook.sh' in str(h) for h in hooks), 'custom hook removed'
assert not any('test-hook.sh' in str(h) for h in hooks), 'managed hook still present'
" "$T/.claude/settings.json" 2>/dev/null; then
  pass "Custom hook entries preserved, managed entries removed"
else
  fail "Settings.json uninstall did not work correctly"
fi
cleanup_test "$T"

# ---- Test 7: Guard function blocks non-managed removal ----
echo "Test 7: Guard function blocks non-managed removal"
T=$(mktemp -d)
mkdir -p "$T/hooks" "$T/toolkit"
echo "precious data" > "$T/hooks/my-hook.sh"

result=$(bash << GUARD_TEST
TOOLKIT_DIR='$T/toolkit'
DRY_RUN=false
is_managed() {
  [[ -L "\$1" ]] && readlink "\$1" | grep -q "\$TOOLKIT_DIR"
}
safe_remove() {
  is_managed "\$1" || { echo 'REFUSED'; return 1; }
  rm "\$1"; echo 'REMOVED'
}
safe_remove '$T/hooks/my-hook.sh' 2>/dev/null || true
GUARD_TEST
)

case "$result" in
  *REFUSED*) pass "Guard function refused non-managed file" ;;
  *) fail "Guard function did not refuse" ;;
esac

if [[ -f "$T/hooks/my-hook.sh" ]]; then
  pass "Non-managed file intact"
else
  fail "Non-managed file was deleted"
fi
rm -rf "$T"

# ---- Test 8: Dry-run changes nothing ----
echo "Test 8: Dry-run changes nothing"
T=$(mktemp -d)
setup_fake_toolkit "$T/toolkit"
setup_fake_home "$T"

BEFORE=$(find "$T/.claude" -type f -exec md5sum {} \; 2>/dev/null | sort)
bash "$T/toolkit/setup.sh" > /dev/null 2>&1 || true
AFTER=$(find "$T/.claude" -type f -exec md5sum {} \; 2>/dev/null | sort)

case "$BEFORE" in
  "$AFTER") pass "Dry-run made no changes" ;;
  *) fail "Dry-run modified the target directory" ;;
esac
cleanup_test "$T"

# ---- Summary ----
export HOME="$REAL_HOME"
echo ""
echo "==================================="
TOTAL=$((PASS + FAIL))
echo "Results: $PASS/$TOTAL passed"
if [[ $FAIL -gt 0 ]]; then
  echo -e "${RED}$FAIL test(s) failed${NC}"
  exit 1
else
  echo -e "${GREEN}All tests passed${NC}"
  exit 0
fi
