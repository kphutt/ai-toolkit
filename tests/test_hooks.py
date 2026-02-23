#!/usr/bin/env python3
"""Tests for Python hooks.

Each test invokes the hook as a subprocess with the appropriate
environment variables and stdin, then checks exit code and output.
Run: python tests/test_hooks.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
PYTHON = sys.executable


def run_hook(hook_name: str, tool_name: str, stdin_data: dict,
             env_extra: "dict | None" = None) -> subprocess.CompletedProcess:
    """Run a hook script with the given tool name and stdin JSON."""
    env = os.environ.copy()
    env["CLAUDE_TOOL_NAME"] = tool_name
    env["CLAUDE_SESSION_ID"] = "test-session"
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [PYTHON, str(HOOKS_DIR / hook_name)],
        input=json.dumps(stdin_data),
        capture_output=True, text=True, env=env,
    )


# ---- protect-files.py ----

class TestProtectFiles(unittest.TestCase):

    def test_blocks_env_file(self):
        r = run_hook("protect-files.py", "Write", {"file_path": "/app/.env"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("BLOCKED", r.stdout)

    def test_blocks_env_variant(self):
        r = run_hook("protect-files.py", "Edit", {"file_path": "/app/.env.production"})
        self.assertEqual(r.returncode, 2)

    def test_blocks_pem_file(self):
        r = run_hook("protect-files.py", "Write", {"file_path": "/keys/server.pem"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("BLOCKED", r.stdout)

    def test_blocks_key_file(self):
        r = run_hook("protect-files.py", "Edit", {"file_path": "/keys/private.key"})
        self.assertEqual(r.returncode, 2)

    def test_allows_normal_file(self):
        r = run_hook("protect-files.py", "Write", {"file_path": "/app/main.py"})
        self.assertEqual(r.returncode, 0)

    def test_ignores_non_write_tool(self):
        r = run_hook("protect-files.py", "Bash", {"file_path": "/app/.env"})
        self.assertEqual(r.returncode, 0)


# ---- pre-commit.py ----

class TestPreCommit(unittest.TestCase):

    def test_blocks_git_push(self):
        r = run_hook("pre-commit.py", "Bash", {"command": "git push origin main"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("preflight", r.stderr.lower())

    def test_blocks_no_verify(self):
        r = run_hook("pre-commit.py", "Bash", {"command": "git commit --no-verify -m 'skip'"})
        self.assertEqual(r.returncode, 2)
        self.assertIn("--no-verify", r.stderr)

    def test_allows_git_status(self):
        r = run_hook("pre-commit.py", "Bash", {"command": "git status"})
        self.assertEqual(r.returncode, 0)

    def test_ignores_non_bash_tool(self):
        r = run_hook("pre-commit.py", "Write", {"command": "git push"})
        self.assertEqual(r.returncode, 0)


# ---- log-tool-use.py ----

class TestLogToolUse(unittest.TestCase):

    def test_appends_log_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_file = Path(tmp) / ".claude" / "tool-use.log"
            log_file.parent.mkdir(parents=True)
            # Override HOME so the hook writes to our temp dir
            env = os.environ.copy()
            env["CLAUDE_TOOL_NAME"] = "Read"
            env["CLAUDE_SESSION_ID"] = "test-sess-123"
            env["HOME"] = tmp
            env["USERPROFILE"] = tmp
            subprocess.run(
                [PYTHON, str(HOOKS_DIR / "log-tool-use.py")],
                input="{}", capture_output=True, text=True, env=env,
            )
            self.assertTrue(log_file.exists(), "Log file not created")
            content = log_file.read_text()
            self.assertIn("test-sess-123", content)
            self.assertIn("Read", content)
            self.assertIn("|", content)


# ---- auto-format.py ----

class TestAutoFormat(unittest.TestCase):

    def test_exits_zero_for_unknown_extension(self):
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as f:
            f.write(b"content")
            path = f.name
        try:
            r = run_hook("auto-format.py", "Write", {"file_path": path})
            self.assertEqual(r.returncode, 0)
        finally:
            os.unlink(path)

    def test_ignores_non_write_tool(self):
        r = run_hook("auto-format.py", "Bash", {"file_path": "/app/main.py"})
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
