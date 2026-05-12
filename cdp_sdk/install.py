#!/usr/bin/env python3
"""
cdp-browse installer — auto-detect and install skill to AI agents.

Usage:
    pipx run cdp-browse                        # auto-detect all agents
    pipx run cdp-browse --agent claude          # Claude Code only
    pipx run cdp-browse --agent codex           # Codex only
    pipx run cdp-browse --agent all             # all agents
    pipx run cdp-browse --uninstall             # remove
"""

import argparse
import shutil
import subprocess
import sys
from importlib.resources import files as pkg_files
from pathlib import Path

SKILL_NAME = "cdp-browse"
PKG_DIR = Path(str(pkg_files("cdp_sdk")))  # actual installed package directory

EXCLUDE_FILES = {
    "install.py", "__pycache__",
}

AGENT_CONFIG = {
    "codex": {
        "dirs": [
            Path.home() / ".agents" / "skills",   # unified path (CLI + App)
            Path.home() / ".codex" / "skills",     # legacy CLI path
        ],
        "commands": ["codex"],
        "label": "Codex",
    },
    "claude": {
        "dirs": [
            Path.home() / ".claude" / "skills",
        ],
        "commands": ["claude"],
        "label": "Claude Code",
    },
    "opencode": {
        "dirs": [
            Path.home() / ".opencode" / "skills",
        ],
        "commands": ["opencode"],
        "label": "OpenCode",
    },
}


def copy_recursive(src: Path, dest: Path):
    if not dest.exists():
        dest.mkdir(parents=True, exist_ok=True)
    for entry in src.iterdir():
        if entry.name in EXCLUDE_FILES:
            continue
        target = dest / entry.name
        if entry.is_dir():
            copy_recursive(entry, target)
        else:
            shutil.copy2(entry, target)


def command_exists(cmd: str) -> bool:
    try:
        subprocess.run(["which", cmd], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def detect_agents() -> list[str]:
    detected = []
    for key, cfg in AGENT_CONFIG.items():
        if any(command_exists(cmd) for cmd in cfg["commands"]):
            detected.append(key)
            continue
        if any(d.parent.exists() for d in cfg["dirs"]):
            detected.append(key)
    return detected


def install_to(agent_key: str) -> bool:
    cfg = AGENT_CONFIG.get(agent_key)
    if not cfg:
        print(f"  Unknown agent: {agent_key}")
        return False

    installed = False
    for dir_path in cfg["dirs"]:
        dest = dir_path / SKILL_NAME
        try:
            copy_recursive(PKG_DIR, dest)
            print(f"  ✓ {cfg['label']} → {dest}")
            installed = True
        except Exception as e:
            print(f"  ✗ {cfg['label']} failed ({dest}): {e}")

    if not installed:
        print(f"  ✗ {cfg['label']}: no writable skill directory found")
    return installed


def uninstall_from(agent_key: str) -> int:
    cfg = AGENT_CONFIG.get(agent_key)
    if not cfg:
        return 0

    removed = 0
    for dir_path in cfg["dirs"]:
        dest = dir_path / SKILL_NAME
        if dest.exists():
            shutil.rmtree(dest)
            print(f"  ✓ Removed from {cfg['label']} ({dest})")
            removed += 1
    return removed


def main():
    parser = argparse.ArgumentParser(
        description="cdp-browse — browser automation skill installer",
        usage="pipx run cdp-browse [--agent {claude,codex,all}] [--uninstall]",
    )
    parser.add_argument("--agent", choices=["claude", "codex", "opencode", "all"],
                        help="Target agent (default: auto-detect)")
    parser.add_argument("--uninstall", action="store_true", help="Remove skill from all agents")
    args = parser.parse_args()

    if args.uninstall:
        print("\nUninstalling cdp-browse...\n")
        total = sum(uninstall_from(k) for k in AGENT_CONFIG)
        if total == 0:
            print("  (not installed anywhere)")
        print()
        return

    # determine targets
    if args.agent == "all":
        targets = list(AGENT_CONFIG.keys())
    elif args.agent:
        targets = [args.agent]
    else:
        detected = detect_agents()
        targets = detected if detected else list(AGENT_CONFIG.keys())

    print(f"\nInstalling cdp-browse skill...\n")
    success = sum(1 for key in targets if install_to(key))

    print("\n  Note: The skill uses 'uvx --from cdp-browse python' to run code,")
    print("  so no separate pip install is needed.\n")

    if success == 0:
        print("\nNo agents installed. Install Codex, Claude Code, or OpenCode first.\n")
        sys.exit(1)

    print(f"\nDone! Give your agent a URL to browse.\n")


if __name__ == "__main__":
    main()
