"""
MCP server exposing project context: recent changes, open TODOs.
Gives Claude quick project health info without manual git/grep commands.

Run: pip install mcp && python server.py
"""

import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-context")


def _run(cmd: list[str], cwd: str | None = None) -> str:
    """Run a shell command and return stdout, or an error message."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10, cwd=cwd
        )
        return result.stdout.strip() or result.stderr.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "Command timed out after 10s"
    except FileNotFoundError:
        return f"Command not found: {cmd[0]}"


@mcp.tool()
def recent_changes(count: int = 20) -> str:
    """Show recent git commits with stats. Defaults to last 20."""
    log = _run(["git", "log", f"--oneline", f"-{count}", "--stat"])
    return log


@mcp.tool()
def open_todos() -> str:
    """Find all TODO, FIXME, and HACK comments in the codebase."""
    results = []
    for pattern in ["TODO", "FIXME", "HACK"]:
        output = _run(
            ["grep", "-rn", "--include=*.py", "--include=*.ts", "--include=*.js",
             "--include=*.go", "--include=*.rs", "--include=*.sh", "--include=*.md",
             pattern, "."]
        )
        if output and "Command not found" not in output:
            results.append(f"=== {pattern} ===\n{output}")
    return "\n\n".join(results) if results else "No TODOs, FIXMEs, or HACKs found."


@mcp.tool()
def changed_files() -> str:
    """Show files with uncommitted changes (staged and unstaged)."""
    return _run(["git", "status", "--short"])


@mcp.tool()
def branch_info() -> str:
    """Show current branch, tracking info, and ahead/behind status."""
    branch = _run(["git", "branch", "-vv"])
    return branch


if __name__ == "__main__":
    mcp.run()
