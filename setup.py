#!/usr/bin/env python3
"""AI Toolkit setup — install/uninstall skills and hooks via links.

Never modifies or deletes files not created by us.
Dry-run by default. Use --apply to make changes.
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Debug logging — enabled only with --debug, writes to debug.log
# ---------------------------------------------------------------------------

log = logging.getLogger("ai-toolkit")


def _init_debug_logging():
    """Configure file logging to debug.log (truncated each run)."""
    handler = logging.FileHandler("debug.log", mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", datefmt="%H:%M:%S"))
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _resolve_home() -> Path:
    """Get home directory, handling MSYS/Git Bash paths on Windows."""
    home = os.environ.get("HOME", "")
    if sys.platform == "win32" and home.startswith("/"):
        try:
            r = subprocess.run(["cygpath", "-w", home], capture_output=True, text=True)
            if r.returncode == 0:
                return Path(r.stdout.strip())
        except FileNotFoundError:
            pass
    return Path(home) if home else Path.home()


TOOLKIT_DIR = Path(__file__).resolve().parent
MANIFEST = TOOLKIT_DIR / "environment.md"
TARGET_DIR = _resolve_home() / ".claude"
STATE_FILE = TARGET_DIR / ".ai-toolkit-managed.json"

# ---------------------------------------------------------------------------
# Platform — detect once at startup
# ---------------------------------------------------------------------------

STRATEGY = "symlink"  # or "windows" (junctions + hard links)


def _detect_strategy():
    global STRATEGY
    test_dir = TOOLKIT_DIR / f".setup-test-{os.getpid()}"
    try:
        test_dir.mkdir(parents=True, exist_ok=True)
        src = test_dir / "source"
        lnk = test_dir / "link"
        src.write_text("test")
        try:
            lnk.symlink_to(src)
            return  # symlinks work
        except OSError:
            pass
        if sys.platform == "win32":
            src_dir = test_dir / "srcdir"
            src_dir.mkdir()
            try:
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(test_dir / "jnc"), str(src_dir)],
                    capture_output=True, check=True,
                )
                STRATEGY = "windows"
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        print("ERROR: Neither symlinks nor junctions work.")
        print("On Windows, enable Developer Mode in Settings > For Developers.")
        sys.exit(1)
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# State file (JSON dict)
# ---------------------------------------------------------------------------

def _state_load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"entries": []}


def _state_save(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def _state_has(state: dict, target: str) -> bool:
    return any(e["target"] == target for e in state["entries"])


def _state_add(state: dict, link_type: str, target: str, source: str):
    if not _state_has(state, target):
        state["entries"].append({"type": link_type, "target": target, "source": source})


def _state_remove(state: dict, target: str):
    state["entries"] = [e for e in state["entries"] if e["target"] != target]


# ---------------------------------------------------------------------------
# Link operations
# ---------------------------------------------------------------------------

def _is_junction(target: Path) -> bool:
    """Detect Windows junctions that is_symlink() misses.

    Python's is_symlink() returns False for NTFS junctions, but os.readlink()
    successfully reads them — so we use that as the detection mechanism.
    """
    if sys.platform != "win32":
        return False
    try:
        if target.is_dir() and not target.is_symlink():
            os.readlink(target)
            return True
    except OSError:
        pass
    return False


def _is_link(target: Path) -> bool:
    return target.is_symlink() or _is_junction(target)


def create_link(source: Path, target: Path, is_dir: bool, state: dict):
    """Create a link from target → source, recording it in state."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if STRATEGY == "symlink":
        target.symlink_to(source, target_is_directory=is_dir)
        _state_add(state, "symlink", str(target), str(source))
    elif is_dir:
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            capture_output=True, check=True,
        )
        _state_add(state, "junction", str(target), str(source))
    else:
        os.link(str(source), str(target))
        _state_add(state, "hardlink", str(target), str(source))


def remove_link(target: Path):
    """Remove a link or regular file/dir. Handles Windows junction removal."""
    if _is_link(target):
        if target.is_dir():
            # Windows junctions must be removed with rmdir, not unlink
            try:
                os.rmdir(target)
            except OSError:
                subprocess.run(["cmd", "/c", "rmdir", str(target)],
                               capture_output=True, check=True)
        else:
            target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()


def is_managed(target: Path, state: dict) -> bool:
    """Return True if target is a toolkit-created link or recorded in state."""
    if _is_link(target):
        try:
            if str(TOOLKIT_DIR) in str(target.resolve()):
                return True
        except OSError:
            pass
    return _state_has(state, str(target))


# ---------------------------------------------------------------------------
# Manifest parser — single pass, also extracts settings.json hook block
# ---------------------------------------------------------------------------

def parse_manifest() -> tuple[list, list, dict]:
    """Return (skills, hooks, settings_hooks).

    skills/hooks: [(name, install_bool), ...]
    settings_hooks: the parsed JSON "hooks" dict from the ```json block, or {}
    """
    text = MANIFEST.read_text()
    skills, hooks = [], []
    settings_hooks = {}

    current_table = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("| Name") and "Install" in s:
            current_table = "skills"
            continue
        if s.startswith("| File") and "Event" in s:
            current_table = "hooks"
            continue
        if current_table and s.startswith("|---"):
            continue
        if current_table and s.startswith("|"):
            parts = [p.strip() for p in s.strip("|").split("|")]
            name = parts[0].strip()
            install = parts[1].strip().lower().startswith("yes")
            if current_table == "skills":
                skills.append((name, install))
            else:
                hooks.append((name, install))
        elif current_table and not s.startswith("|"):
            current_table = None

    m = re.search(r"```json\s*\n(.*?)```", text, re.DOTALL)
    if m:
        try:
            blob = json.loads(m.group(1))
            settings_hooks = blob.get("hooks", {})
        except json.JSONDecodeError:
            pass

    return skills, hooks, settings_hooks


# ---------------------------------------------------------------------------
# Settings.json merge
# ---------------------------------------------------------------------------

# Matches only toolkit-managed hook commands (both old bash and new python forms)
MANAGED_HOOK_RE = re.compile(r"^(bash|python3?) ~/\.claude/hooks/\S+\.(sh|py)$")


def _merge_settings(mode: str, expected_hooks: dict, dry_run: bool):
    settings_file = TARGET_DIR / "settings.json"
    if not settings_file.exists():
        print("  " + ("WARNING: settings.json not found — skipping" if mode == "install"
                       else "No settings.json — nothing to do"))
        return

    try:
        settings = json.loads(settings_file.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"  WARNING: could not parse settings.json — {e}")
        return

    changed = False
    if mode == "install":
        settings.setdefault("hooks", {})
        # Each event (PreToolUse, PostToolUse) maps to a list of entries,
        # where each entry has a "hooks" array of {type, command} objects.
        for event, entries in expected_hooks.items():
            settings["hooks"].setdefault(event, [])
            existing = {h.get("command", "") for e in settings["hooks"][event] for h in e.get("hooks", [])}
            for entry in entries:
                cmd = entry["hooks"][0]["command"]
                # On Windows, rewrite python3 → python (python3 may not exist)
                if sys.platform == "win32":
                    cmd = cmd.replace("python3 ", "python ")
                    entry = json.loads(json.dumps(entry).replace("python3 ", "python "))
                if cmd in existing:
                    print(f"  CURRENT: {event}:{cmd}")
                else:
                    changed = True
                    if dry_run:
                        print(f"  [dry-run] would add: {event}:{cmd}")
                    else:
                        settings["hooks"][event].append(entry)
                        print(f"  ADDED: {event}:{cmd}")
    else:  # uninstall
        if "hooks" not in settings:
            print("  No managed entries found")
            return
        for event in list(settings["hooks"]):
            kept = []
            for entry in settings["hooks"][event]:
                if any(MANAGED_HOOK_RE.match(h.get("command", "")) for h in entry.get("hooks", [])):
                    cmd = entry["hooks"][0]["command"]
                    changed = True
                    print(f"  {'[dry-run] would remove' if dry_run else 'REMOVED'}: {event}:{cmd}")
                else:
                    kept.append(entry)
            settings["hooks"][event] = kept
            if not kept:
                del settings["hooks"][event]
        if not settings.get("hooks"):
            settings.pop("hooks", None)
        if not changed:
            print("  No managed entries found")

    if changed and not dry_run:
        settings_file.write_text(json.dumps(settings, indent=2) + "\n")
        log.debug("[SETTINGS] wrote %s", settings_file)
        print("  settings.json updated")


# ---------------------------------------------------------------------------
# Safe link / safe remove
# ---------------------------------------------------------------------------

def safe_link(source: Path, target: Path, is_dir: bool, state: dict, dry_run: bool):
    """Create a link only if target is absent or already managed. Never touches local files."""
    name = target.name

    if _is_link(target):
        try:
            if str(TOOLKIT_DIR) in str(target.resolve()):
                log.debug("[LINK] current name=%s target=%s", name, target)
                print(f"  CURRENT: {name}")
                return
        except OSError:
            pass
        if dry_run:
            log.debug("[LINK] would-relink name=%s", name)
            print(f"  [dry-run] would re-link: {name}")
        else:
            remove_link(target)
            create_link(source, target, is_dir, state)
            log.debug("[LINK] relinked name=%s source=%s", name, source)
            print(f"  RE-LINKED: {name}")
        return

    # Regular file/dir not in state → LOCAL (not ours, don't touch)
    if (target.is_dir() if is_dir else target.is_file()) and not _state_has(state, str(target)):
        kind = "directory" if is_dir else "file"
        log.debug("[LINK] local name=%s kind=%s (not managed)", name, kind)
        print(f"  LOCAL: {name} (regular {kind} — not managed)")
        return

    # In state and exists → CURRENT (trust state file)
    if _state_has(state, str(target)) and target.exists():
        log.debug("[LINK] current name=%s (in state)", name)
        print(f"  CURRENT: {name}")
        return

    # Doesn't exist → create
    if dry_run:
        log.debug("[LINK] would-create name=%s source=%s", name, source)
        print(f"  [dry-run] would create: {name} -> {source}")
    else:
        create_link(source, target, is_dir, state)
        log.debug("[LINK] created name=%s source=%s", name, source)
        print(f"  CREATED: {name}")


def safe_remove(target: Path, state: dict, dry_run: bool) -> bool:
    """Remove target only if it was created by us. Returns True if removed."""
    if not is_managed(target, state):
        log.debug("[LINK] skip-remove name=%s (not managed)", target.name)
        print(f"  SKIP (not managed): {target.name}")
        return False
    if dry_run:
        log.debug("[LINK] would-remove name=%s", target.name)
        print(f"  [dry-run] would remove: {target.name}")
    else:
        remove_link(target)
        _state_remove(state, str(target))
        log.debug("[LINK] removed name=%s", target.name)
        print(f"  REMOVED: {target.name}")
    return True


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def do_install(skills, hooks, expected_hooks, state, dry_run):
    """Link skills and hooks into ~/.claude/ and merge settings.json entries."""
    print("Skills:")
    for name, install in skills:
        if not install:
            continue
        src, tgt = TOOLKIT_DIR / "skills" / name, TARGET_DIR / "skills" / name
        if not src.is_dir():
            print(f"  WARNING: source not found: {src}")
            continue
        safe_link(src, tgt, is_dir=True, state=state, dry_run=dry_run)
    print()

    print("Hooks:")
    for name, install in hooks:
        if not install:
            continue
        src, tgt = TOOLKIT_DIR / "hooks" / name, TARGET_DIR / "hooks" / name
        if not src.is_file():
            print(f"  WARNING: source not found: {src}")
            continue
        safe_link(src, tgt, is_dir=False, state=state, dry_run=dry_run)
    print()

    print("Settings.json:")
    _merge_settings("install", expected_hooks, dry_run)
    print()


def _iter_managed(subdir: str):
    """Yield entry paths in a target subdirectory."""
    d = TARGET_DIR / subdir
    if not d.is_dir():
        return
    for entry in sorted(d.iterdir()):
        yield entry


def do_uninstall(state, dry_run, expected_hooks):
    """Remove all toolkit-managed links and settings.json entries."""
    for label, subdir in [("Skills:", "skills"), ("Hooks:", "hooks")]:
        print(label)
        for entry in _iter_managed(subdir):
            safe_remove(entry, state, dry_run)
        print()

    print("Settings.json:")
    _merge_settings("uninstall", expected_hooks, dry_run)
    print()

    if not state["entries"] and not dry_run:
        STATE_FILE.unlink(missing_ok=True)
    if not dry_run:
        print(f"Uninstall complete. Source repo at {TOOLKIT_DIR} still exists.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Parse CLI args and run install or uninstall."""
    parser = argparse.ArgumentParser(description="AI Toolkit setup")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Make changes (default is dry-run)")
    parser.add_argument("--debug", action="store_true", help="Write debug.log with diagnostic trace")
    args = parser.parse_args()

    if args.debug:
        _init_debug_logging()

    dry_run = not args.apply

    log.debug("[INIT] toolkit=%s target=%s strategy=%s mode=%s",
              TOOLKIT_DIR, TARGET_DIR, STRATEGY, "uninstall" if args.uninstall else ("apply" if args.apply else "dry-run"))

    print(f"\nAI Toolkit Setup ({'dry run' if dry_run else 'apply'})")
    print("=" * 40)

    if not MANIFEST.exists():
        log.debug("[ERR] manifest not found: %s", MANIFEST)
        print(f"ERROR: Manifest not found: {MANIFEST}")
        sys.exit(1)

    if not TARGET_DIR.is_dir() and not dry_run:
        TARGET_DIR.mkdir(parents=True, exist_ok=True)

    _detect_strategy()
    log.debug("[INIT] strategy=%s platform=%s", STRATEGY, sys.platform)
    if STRATEGY == "windows":
        print("Note: Using junctions + hard links (symlinks not available).\n")

    skills, hooks, expected_hooks = parse_manifest()
    log.debug("[MANIFEST] skills=%d hooks=%d settings_hook_events=%d",
              len(skills), len(hooks), len(expected_hooks))
    state = _state_load()
    log.debug("[STATE] loaded entries=%d", len(state.get("entries", [])))

    if args.uninstall:
        do_uninstall(state, dry_run, expected_hooks)
    else:
        do_install(skills, hooks, expected_hooks, state, dry_run)

    if not dry_run:
        if state["entries"]:
            _state_save(state)
            log.debug("[STATE] saved entries=%d", len(state["entries"]))
        elif STATE_FILE.exists():
            STATE_FILE.unlink()
            log.debug("[STATE] removed empty state file")

    log.debug("[DONE] finished")
    print("Done.")


if __name__ == "__main__":
    main()
