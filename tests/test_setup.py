#!/usr/bin/env python3
"""Invariant tests for setup.py.

Each test creates isolated temp dirs and verifies safety guarantees.
Run: python tests/test_setup.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLKIT_DIR = Path(__file__).resolve().parent.parent
SETUP_PY = TOOLKIT_DIR / "setup.py"

# Find a working python command
PYTHON = sys.executable


def make_toolkit(path: Path):
    """Create a fake toolkit with one skill and one hook."""
    (path / "skills" / "test-skill").mkdir(parents=True)
    (path / "skills" / "test-skill" / "SKILL.md").write_text("test skill content")
    (path / "hooks").mkdir(parents=True)
    (path / "hooks" / "test-hook.sh").write_text("#!/bin/bash\necho test")
    shutil.copy(str(SETUP_PY), str(path / "setup.py"))
    (path / "environment.md").write_text("""\
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
""")


def make_home(path: Path):
    """Create a fake ~/.claude with empty settings.json."""
    claude = path / ".claude"
    (claude / "skills").mkdir(parents=True)
    (claude / "hooks").mkdir(parents=True)
    (claude / "settings.json").write_text('{"permissions":{"allow":[]}}')


def run_setup(toolkit: Path, home: Path, *extra_args) -> subprocess.CompletedProcess:
    """Run setup.py with HOME pointing to the fake home."""
    env = os.environ.copy()
    env["HOME"] = str(home)
    # On Windows, also set USERPROFILE as fallback
    env["USERPROFILE"] = str(home)
    return subprocess.run(
        [PYTHON, str(toolkit / "setup.py"), *extra_args],
        capture_output=True, text=True, env=env,
    )


def cleanup_junctions(home: Path):
    """Remove junctions before rmtree (Windows needs this)."""
    claude = home / ".claude"
    for subdir in ("skills", "hooks"):
        d = claude / subdir
        if not d.is_dir():
            continue
        for entry in d.iterdir():
            if entry.is_symlink() or (entry.is_dir() and _looks_like_junction(entry)):
                try:
                    os.rmdir(entry)
                except OSError:
                    if sys.platform == "win32":
                        subprocess.run(["cmd", "/c", "rmdir", str(entry)],
                                       capture_output=True)


def _looks_like_junction(p: Path) -> bool:
    if sys.platform != "win32":
        return False
    try:
        os.readlink(p)
        return True
    except OSError:
        return False


class TestSetup(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.toolkit = self.tmp / "toolkit"
        self.toolkit.mkdir()
        make_toolkit(self.toolkit)
        make_home(self.tmp)

    def tearDown(self):
        cleanup_junctions(self.tmp)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def home_path(self, *parts):
        return self.tmp / ".claude" / Path(*parts)

    # -- Test 1: Install skips existing regular directory --

    def test_install_preserves_regular_directory(self):
        skill_dir = self.home_path("skills", "test-skill")
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text("my custom content")

        run_setup(self.toolkit, self.tmp, "--apply")

        self.assertTrue(skill_dir.is_dir())
        self.assertEqual((skill_dir / "SKILL.md").read_text(), "my custom content")

    # -- Test 2: Install creates links for missing skill and hook --

    def test_install_creates_links(self):
        run_setup(self.toolkit, self.tmp, "--apply")

        skill = self.home_path("skills", "test-skill")
        hook = self.home_path("hooks", "test-hook.sh")
        self.assertTrue(skill.is_dir(), "Skill link not created")
        self.assertTrue((skill / "SKILL.md").exists(), "Skill content not accessible")
        self.assertTrue(hook.exists(), "Hook link not created")

    # -- Test 3: Uninstall removes managed, preserves unmanaged --

    def test_uninstall_selective(self):
        run_setup(self.toolkit, self.tmp, "--apply")

        # Create unmanaged items
        custom_skill = self.home_path("skills", "custom-skill")
        custom_skill.mkdir(parents=True)
        (custom_skill / "SKILL.md").write_text("custom")
        custom_hook = self.home_path("hooks", "custom-hook.sh")
        custom_hook.write_text("custom hook")

        run_setup(self.toolkit, self.tmp, "--uninstall", "--apply")

        self.assertFalse(self.home_path("skills", "test-skill").exists(),
                         "Managed skill not removed")
        self.assertFalse(self.home_path("hooks", "test-hook.sh").exists(),
                         "Managed hook not removed")
        self.assertTrue(custom_skill.is_dir(), "Unmanaged skill removed")
        self.assertTrue(custom_hook.is_file(), "Unmanaged hook removed")

    # -- Test 4: Detach converts links to regular copies --

    def test_detach(self):
        # Create unmanaged item
        custom_skill = self.home_path("skills", "custom-skill")
        custom_skill.mkdir(parents=True)
        (custom_skill / "SKILL.md").write_text("custom content")

        run_setup(self.toolkit, self.tmp, "--apply")
        run_setup(self.toolkit, self.tmp, "--detach", "--apply")

        skill = self.home_path("skills", "test-skill")
        self.assertTrue(skill.is_dir(), "Skill missing after detach")
        self.assertTrue((skill / "SKILL.md").exists(), "Skill content missing after detach")
        self.assertFalse(skill.is_symlink(), "Skill still a symlink after detach")
        self.assertFalse(_looks_like_junction(skill), "Skill still a junction after detach")
        self.assertEqual((custom_skill / "SKILL.md").read_text(), "custom content")

    # -- Test 5: settings.json install preserves custom entries --

    def test_settings_install_preserves_custom(self):
        settings = self.home_path("settings.json")
        settings.write_text('{"permissions":{"allow":["Bash(git *)"]},"customKey":"customValue"}')

        run_setup(self.toolkit, self.tmp, "--apply")

        d = json.loads(settings.read_text())
        self.assertEqual(d["customKey"], "customValue")
        self.assertEqual(d["permissions"]["allow"], ["Bash(git *)"])

    # -- Test 6: settings.json uninstall preserves custom hooks --

    def test_settings_uninstall_preserves_custom_hooks(self):
        settings = self.home_path("settings.json")
        settings.write_text(json.dumps({
            "permissions": {"allow": []},
            "hooks": {
                "PostToolUse": [
                    {"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/test-hook.sh"}]},
                    {"matcher": "Bash", "hooks": [{"type": "command", "command": "bash /my/custom/hook.sh"}]},
                ]
            }
        }))

        run_setup(self.toolkit, self.tmp, "--uninstall", "--apply")

        d = json.loads(settings.read_text())
        hooks = d.get("hooks", {}).get("PostToolUse", [])
        commands = [h.get("command", "") for e in hooks for h in e.get("hooks", [])]
        self.assertIn("bash /my/custom/hook.sh", commands)
        self.assertNotIn("bash ~/.claude/hooks/test-hook.sh", commands)

    # -- Test 7: Non-managed files are never removed --

    def test_guard_refuses_non_managed(self):
        """Verify that uninstall doesn't remove files it didn't create."""
        precious = self.home_path("hooks", "precious.sh")
        precious.write_text("precious data")

        run_setup(self.toolkit, self.tmp, "--uninstall", "--apply")

        self.assertTrue(precious.is_file(), "Non-managed file was deleted")
        self.assertEqual(precious.read_text(), "precious data")

    # -- Test 8: Dry-run changes nothing --

    def test_dry_run_no_changes(self):
        claude = self.tmp / ".claude"
        before = {}
        for f in claude.rglob("*"):
            if f.is_file():
                before[str(f)] = f.read_bytes()

        run_setup(self.toolkit, self.tmp)  # no --apply

        after = {}
        for f in claude.rglob("*"):
            if f.is_file():
                after[str(f)] = f.read_bytes()

        self.assertEqual(before, after, "Dry-run modified files")


if __name__ == "__main__":
    unittest.main()
