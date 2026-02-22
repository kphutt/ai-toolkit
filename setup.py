#!/usr/bin/env python3
"""AI Toolkit setup — install/uninstall/detach skills and hooks via symlinks.

On Windows without Developer Mode, uses junctions (dirs) + hard links (files).
Dry-run by default. Use --apply to make changes.

Same interface as the old setup.sh:
    python setup.py                        # dry-run
    python setup.py --apply                # install
    python setup.py --uninstall            # dry-run uninstall
    python setup.py --uninstall --apply    # uninstall
    python setup.py --detach --apply       # detach
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def _resolve_home() -> Path:
    """Get home directory, handling MSYS/Git Bash paths on Windows.

    Python's Path.home() on Windows uses USERPROFILE and ignores the HOME
    env var that Git Bash sets.  When tests (or users) override HOME, we
    need to respect it — and convert MSYS virtual paths like /tmp/... to
    real Windows paths via cygpath.
    """
    home = os.environ.get("HOME", "")
    if sys.platform == "win32" and home.startswith("/"):
        try:
            result = subprocess.run(
                ["cygpath", "-w", home], capture_output=True, text=True,
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except FileNotFoundError:
            pass
    if home:
        return Path(home)
    return Path.home()


TOOLKIT_DIR = Path(__file__).resolve().parent
MANIFEST = TOOLKIT_DIR / "environment.md"
TARGET_DIR = _resolve_home() / ".claude"
STATE_FILE = TARGET_DIR / ".ai-toolkit-managed.json"

# ---------------------------------------------------------------------------
# Platform / link strategy
# ---------------------------------------------------------------------------

STRATEGY = "symlink"  # or "windows" (junctions + hard links)


def _detect_strategy():
    """Try a real symlink. Fall back to junctions on Windows."""
    global STRATEGY
    test_dir = TOOLKIT_DIR / f".setup-test-{os.getpid()}"
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        src = test_dir / "source"
        lnk = test_dir / "link"
        src.write_text("test")
        try:
            lnk.symlink_to(src)
            if lnk.resolve() == src.resolve():
                return  # symlinks work
        except OSError:
            pass

        # Try junction (Windows without Developer Mode)
        if sys.platform == "win32":
            jnc = test_dir / "jnc"
            src_dir = test_dir / "srcdir"
            src_dir.mkdir(exist_ok=True)
            try:
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(jnc), str(src_dir)],
                    capture_output=True, check=True,
                )
                if jnc.exists():
                    STRATEGY = "windows"
                    # clean junction
                    subprocess.run(
                        ["cmd", "/c", "rmdir", str(jnc)],
                        capture_output=True,
                    )
                    return
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        print("ERROR: Neither symlinks nor junctions are supported.")
        print("On Windows, enable Developer Mode in Settings -> Privacy & Security -> For Developers.")
        sys.exit(1)
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# State file (JSON)
# ---------------------------------------------------------------------------

def _state_load() -> dict:
    """Load state file, return {"entries": [...]}."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"entries": []}


def _state_save(state: dict, dry_run: bool):
    if dry_run:
        return
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def _state_has(state: dict, target: str) -> bool:
    return any(e["target"] == target for e in state["entries"])


def _state_add(state: dict, link_type: str, target: str, source: str):
    if not _state_has(state, target):
        state["entries"].append({"type": link_type, "target": target, "source": source})


def _state_remove(state: dict, target: str):
    state["entries"] = [e for e in state["entries"] if e["target"] != target]


def _state_source(state: dict, target: str) -> str | None:
    for e in state["entries"]:
        if e["target"] == target:
            return e["source"]
    return None


def _state_cleanup(state: dict, dry_run: bool):
    """Remove state file if no entries remain."""
    if dry_run:
        return
    if not state["entries"]:
        STATE_FILE.unlink(missing_ok=True)
    else:
        _state_save(state, dry_run)


# ---------------------------------------------------------------------------
# Link operations — ONE place for all platform logic
# ---------------------------------------------------------------------------

def create_link(source: Path, target: Path, is_dir: bool, state: dict):
    """Create a link (symlink, junction, or hard link) and record in state."""
    if STRATEGY == "symlink":
        target.symlink_to(source, target_is_directory=is_dir)
        _state_add(state, "symlink", str(target), str(source))
    elif is_dir:
        # Junction
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            capture_output=True, check=True,
        )
        _state_add(state, "junction", str(target), str(source))
    else:
        # Hard link
        os.link(str(source), str(target))
        _state_add(state, "hardlink", str(target), str(source))


def _is_junction(target: Path) -> bool:
    """Detect Windows junctions (reparse points that is_symlink() misses)."""
    if sys.platform != "win32":
        return False
    try:
        # Junction: is_dir() True, is_symlink() may be False, but os.readlink works
        if target.is_dir() and not target.is_symlink():
            os.readlink(target)
            return True
    except OSError:
        pass
    return False


def remove_link(target: Path):
    """Remove a link (symlink, junction, hard link, or regular file)."""
    if target.is_symlink() or _is_junction(target):
        if target.is_dir():
            # Symlink-to-dir or junction — use os.rmdir (does not follow)
            try:
                os.rmdir(target)
            except OSError:
                # Fallback: cmd /c rmdir for junctions
                try:
                    subprocess.run(
                        ["cmd", "/c", "rmdir", str(target)],
                        capture_output=True, check=True,
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    target.unlink(missing_ok=True)
        else:
            target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()


def is_managed(target: Path, state: dict) -> bool:
    """Check if a path was created by us (symlink/junction into toolkit OR in state file)."""
    if target.is_symlink() or _is_junction(target):
        try:
            resolved = str(target.resolve())
            if str(TOOLKIT_DIR) in resolved:
                return True
        except OSError:
            pass
    return _state_has(state, str(target))


# ---------------------------------------------------------------------------
# Manifest parser
# ---------------------------------------------------------------------------

def parse_manifest() -> tuple[list[tuple[str, bool]], list[tuple[str, bool]]]:
    """Parse environment.md, return (skills, hooks) as [(name, install), ...]."""
    text = MANIFEST.read_text()
    skills = []
    hooks = []

    # Skills table
    in_skills = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Name") and "Install" in stripped:
            in_skills = True
            continue
        if in_skills and stripped.startswith("|---"):
            continue
        if in_skills and stripped.startswith("|"):
            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) >= 2:
                name = parts[0].strip()
                install = parts[1].strip().lower().startswith("yes")
                skills.append((name, install))
        elif in_skills and not stripped.startswith("|"):
            in_skills = False

    # Hooks table
    in_hooks = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("| File") and "Event" in stripped:
            in_hooks = True
            continue
        if in_hooks and stripped.startswith("|---"):
            continue
        if in_hooks and stripped.startswith("|"):
            parts = [p.strip() for p in stripped.strip("|").split("|")]
            if len(parts) >= 4:
                name = parts[0].strip()
                install = parts[1].strip().lower().startswith("yes")
                hooks.append((name, install))
        elif in_hooks and not stripped.startswith("|"):
            in_hooks = False

    return skills, hooks


# ---------------------------------------------------------------------------
# Settings.json merge
# ---------------------------------------------------------------------------

EXPECTED_HOOKS = {
    "PreToolUse": [
        {"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/protect-files.sh"}]},
        {"matcher": "Bash", "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/pre-commit.sh"}]},
    ],
    "PostToolUse": [
        {"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "bash ~/.claude/hooks/auto-format.sh"}]},
        {"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/log-tool-use.sh"}]},
    ],
}

MANAGED_HOOK_RE = re.compile(r"^bash ~/\.claude/hooks/\S+\.sh$")


def merge_settings(mode: str, dry_run: bool):
    """Merge or remove hook entries in settings.json.

    mode: "install" | "uninstall"
    """
    settings_file = TARGET_DIR / "settings.json"

    if mode == "install" and not settings_file.exists():
        print("  WARNING: settings.json not found — skipping settings merge")
        return
    if mode == "uninstall" and not settings_file.exists():
        print("  No settings.json found — nothing to do")
        return

    try:
        settings = json.loads(settings_file.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARNING: could not parse settings.json — {e}")
        return

    if mode == "install":
        _merge_install(settings, settings_file, dry_run)
    else:
        _merge_uninstall(settings, settings_file, dry_run)


def _merge_install(settings: dict, settings_file: Path, dry_run: bool):
    if "hooks" not in settings:
        settings["hooks"] = {}

    changed = False
    for event, entries in EXPECTED_HOOKS.items():
        if event not in settings["hooks"]:
            settings["hooks"][event] = []
        existing_commands = set()
        for entry in settings["hooks"][event]:
            for h in entry.get("hooks", []):
                existing_commands.add(h.get("command", ""))
        for entry in entries:
            cmd = entry["hooks"][0]["command"]
            if cmd not in existing_commands:
                if dry_run:
                    print(f"  [dry-run] would add: {event}:{cmd}")
                else:
                    settings["hooks"][event].append(entry)
                    print(f"  ADDED: {event}:{cmd}")
                changed = True
            else:
                print(f"  CURRENT: {event}:{cmd}")

    if changed and not dry_run:
        _write_settings(settings, settings_file)


def _merge_uninstall(settings: dict, settings_file: Path, dry_run: bool):
    if "hooks" not in settings:
        print("  No managed entries found")
        return

    changed = False
    for event in list(settings["hooks"].keys()):
        new_entries = []
        for entry in settings["hooks"][event]:
            is_ours = False
            for h in entry.get("hooks", []):
                if MANAGED_HOOK_RE.match(h.get("command", "")):
                    is_ours = True
                    break
            if is_ours:
                cmd = entry["hooks"][0]["command"]
                if dry_run:
                    print(f"  [dry-run] would remove: {event}:{cmd}")
                else:
                    print(f"  REMOVED: {event}:{cmd}")
                changed = True
            else:
                new_entries.append(entry)
        settings["hooks"][event] = new_entries
        if not settings["hooks"][event]:
            del settings["hooks"][event]

    if not settings.get("hooks"):
        settings.pop("hooks", None)

    if changed:
        if not dry_run:
            _write_settings(settings, settings_file)
    else:
        print("  No managed entries found")


def _write_settings(settings: dict, settings_file: Path):
    tmp = tempfile.NamedTemporaryFile(
        mode="w", dir=str(settings_file.parent),
        prefix="settings.json.", delete=False,
    )
    try:
        json.dump(settings, tmp, indent=2)
        tmp.write("\n")
        tmp.close()
        shutil.move(tmp.name, str(settings_file))
        print("  settings.json updated")
    except Exception:
        tmp.close()
        os.unlink(tmp.name)
        raise


# ---------------------------------------------------------------------------
# Safe link / safe remove
# ---------------------------------------------------------------------------

def safe_link(source: Path, target: Path, is_dir: bool, state: dict, dry_run: bool):
    """Create a link, respecting existing files and the safety invariant."""
    name = target.name

    is_link = target.is_symlink() or _is_junction(target)

    # Existing non-link regular entry, not in state → LOCAL
    if not is_link:
        if is_dir and target.is_dir() and not _state_has(state, str(target)):
            print(f"  LOCAL: {name} (regular directory — not managed)")
            return
        if not is_dir and target.is_file() and not _state_has(state, str(target)):
            print(f"  LOCAL: {name} (regular file — not managed)")
            return

    # Existing symlink/junction pointing into our toolkit → CURRENT
    if is_link:
        try:
            resolved = str(target.resolve())
            if str(TOOLKIT_DIR) in resolved:
                print(f"  CURRENT: {name}")
                return
        except OSError:
            pass
        # Link to wrong source — re-link
        if dry_run:
            print(f"  [dry-run] would re-link: {name} -> {source}")
        else:
            remove_link(target)
            create_link(source, target, is_dir, state)
            print(f"  RE-LINKED: {name}")
        return

    # Existing hard link in state → check inode match
    if _state_has(state, str(target)) and target.exists():
        if not is_dir:
            try:
                src_stat = source.stat()
                tgt_stat = target.stat()
                if src_stat.st_ino == tgt_stat.st_ino and src_stat.st_ino != 0:
                    print(f"  CURRENT: {name}")
                    return
            except OSError:
                pass
        else:
            print(f"  CURRENT: {name}")
            return
        # Inode mismatch — re-link
        if dry_run:
            print(f"  [dry-run] would re-link: {name} -> {source}")
        else:
            remove_link(target)
            _state_remove(state, str(target))
            create_link(source, target, is_dir, state)
            print(f"  RE-LINKED: {name}")
        return

    # Target doesn't exist — create
    if dry_run:
        print(f"  [dry-run] would create: {name} -> {source}")
    else:
        create_link(source, target, is_dir, state)
        print(f"  CREATED: {name}")


def safe_remove(target: Path, state: dict, dry_run: bool):
    """Remove a managed link. Refuses non-managed paths."""
    if not is_managed(target, state):
        print(f"  REFUSED: not managed by ai-toolkit: {target}")
        return False
    if dry_run:
        print(f"  [dry-run] would remove: {target.name}")
    else:
        remove_link(target)
        _state_remove(state, str(target))
        print(f"  REMOVED: {target.name}")
    return True


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def do_install(skills, hooks, state: dict, dry_run: bool):
    print("Skills:")
    for name, install in skills:
        if not install:
            continue
        source = TOOLKIT_DIR / "skills" / name
        target = TARGET_DIR / "skills" / name
        if not source.is_dir():
            print(f"  WARNING: source not found: {source}")
            continue
        safe_link(source, target, is_dir=True, state=state, dry_run=dry_run)
    print()

    print("Hooks:")
    for name, install in hooks:
        if not install:
            continue
        source = TOOLKIT_DIR / "hooks" / name
        target = TARGET_DIR / "hooks" / name
        if not source.is_file():
            print(f"  WARNING: source not found: {source}")
            continue
        # Ensure executable
        if not dry_run and not os.access(source, os.X_OK):
            source.chmod(source.stat().st_mode | 0o111)
        safe_link(source, target, is_dir=False, state=state, dry_run=dry_run)
    print()

    print("Settings.json:")
    merge_settings("install", dry_run)
    print()


def do_uninstall(state: dict, dry_run: bool):
    print("Skills:")
    skills_dir = TARGET_DIR / "skills"
    if skills_dir.is_dir():
        for entry in sorted(skills_dir.iterdir()):
            if is_managed(entry, state):
                safe_remove(entry, state, dry_run)
            else:
                print(f"  SKIP (not managed): {entry.name}")
    print()

    print("Hooks:")
    hooks_dir = TARGET_DIR / "hooks"
    if hooks_dir.is_dir():
        for entry in sorted(hooks_dir.iterdir()):
            if is_managed(entry, state):
                safe_remove(entry, state, dry_run)
            else:
                print(f"  SKIP (not managed): {entry.name}")
    print()

    print("Settings.json:")
    merge_settings("uninstall", dry_run)
    print()

    _state_cleanup(state, dry_run)

    if not dry_run:
        print(f"Uninstall complete. Source repo at {TOOLKIT_DIR} still exists — delete it manually if done with the toolkit.")


def do_detach(state: dict, dry_run: bool):
    print("Skills:")
    skills_dir = TARGET_DIR / "skills"
    if skills_dir.is_dir():
        for entry in sorted(skills_dir.iterdir()):
            if is_managed(entry, state):
                source = _find_source(entry, state)
                if not source or not Path(source).exists():
                    print(f"  WARNING: cannot find source for {entry.name} — skipping")
                    continue
                if dry_run:
                    print(f"  [dry-run] would detach: {entry.name}")
                else:
                    remove_link(entry)
                    shutil.copytree(source, str(entry))
                    _state_remove(state, str(entry))
                    print(f"  DETACHED: {entry.name} (now a regular copy)")
            else:
                print(f"  SKIP (not managed): {entry.name}")
    print()

    print("Hooks:")
    hooks_dir = TARGET_DIR / "hooks"
    if hooks_dir.is_dir():
        for entry in sorted(hooks_dir.iterdir()):
            if is_managed(entry, state):
                source = _find_source(entry, state)
                if not source or not Path(source).exists():
                    print(f"  WARNING: cannot find source for {entry.name} — skipping")
                    continue
                if dry_run:
                    print(f"  [dry-run] would detach: {entry.name}")
                else:
                    remove_link(entry)
                    shutil.copy2(source, str(entry))
                    _state_remove(state, str(entry))
                    print(f"  DETACHED: {entry.name} (now a regular copy)")
            else:
                print(f"  SKIP (not managed): {entry.name}")
    print()

    print("Settings.json: left as-is (hook registrations still work with regular files).")
    _state_cleanup(state, dry_run)

    if not dry_run:
        print()
        print("Detached. Skills and hooks are now regular files — no longer linked to the source repo.")
        print(f"Safe to remove {TOOLKIT_DIR}.")


def _find_source(target: Path, state: dict) -> str | None:
    """Resolve the original source for a managed target."""
    if target.is_symlink() or _is_junction(target):
        try:
            return str(target.resolve())
        except OSError:
            pass
    return _state_source(state, str(target))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AI Toolkit setup — install/uninstall/detach skills and hooks.",
        usage="python setup.py [--uninstall|--detach] [--apply]",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--uninstall", action="store_true", help="Remove managed links + settings.json entries")
    group.add_argument("--detach", action="store_true", help="Convert managed links to regular file copies")
    parser.add_argument("--apply", action="store_true", help="Actually make changes (default is dry-run)")
    args = parser.parse_args()

    mode = "detach" if args.detach else ("uninstall" if args.uninstall else "install")
    dry_run = not args.apply
    run_label = "dry run" if dry_run else "apply"

    # Banner
    print()
    print(f"AI Toolkit Setup ({run_label})")
    print("==========================")
    print("This script only manages what it creates (symlinks + settings entries).")
    print("It never modifies, overwrites, or deletes anything it didn't create.")
    print()
    print("Paths that may be changed:")
    print("  ~/.claude/skills/       links created/removed")
    print("  ~/.claude/hooks/        links created/removed")
    print("  ~/.claude/settings.json hook entries added (install) or removed (uninstall)")
    print()

    # Prerequisites
    if not MANIFEST.exists():
        print(f"ERROR: Manifest not found: {MANIFEST}")
        sys.exit(1)

    if not TARGET_DIR.is_dir():
        print("WARNING: ~/.claude/ does not exist. Creating it.")
        if not dry_run:
            TARGET_DIR.mkdir(parents=True, exist_ok=True)

    # Detect link strategy
    _detect_strategy()
    if STRATEGY == "windows":
        print("Note: Using junctions (dirs) + hard links (files) — symlinks not available.")
        print()

    # Ensure target directories
    for sub in ("skills", "hooks"):
        d = TARGET_DIR / sub
        if not d.is_dir():
            if dry_run:
                print(f"  [dry-run] would create directory: {d}")
            else:
                d.mkdir(parents=True, exist_ok=True)
                print(f"  created directory: {d}")

    # Parse manifest
    skills, hooks = parse_manifest()

    # Load state
    state = _state_load()

    # Execute
    if mode == "install":
        do_install(skills, hooks, state, dry_run)
    elif mode == "uninstall":
        do_uninstall(state, dry_run)
    elif mode == "detach":
        do_detach(state, dry_run)

    # Save state
    if not dry_run:
        _state_save(state, dry_run)

    print("Done.")


if __name__ == "__main__":
    main()
