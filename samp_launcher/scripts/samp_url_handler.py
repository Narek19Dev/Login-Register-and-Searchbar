#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

# Determine project root from this script location
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = PROJECT_ROOT / "launcher" / "config.json"


def read_config():
    default = {
        "wine_path": "/usr/bin/wine",
        "samp_exe_path": "",
    }
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return {**default, **data}
        except Exception:
            return default
    return default


def normalize_arg_to_ip_port(arg: str) -> str:
    # Accept either samp://ip:port or ip:port
    if arg.lower().startswith("samp://"):
        return arg.split("://", 1)[1]
    return arg


def main():
    if len(sys.argv) < 2:
        print("Usage: samp_url_handler.py samp://ip:port", file=sys.stderr)
        sys.exit(1)

    target = normalize_arg_to_ip_port(sys.argv[1])

    cfg = read_config()
    wine_path = cfg.get("wine_path") or "/usr/bin/wine"
    samp_exe_path = cfg.get("samp_exe_path") or ""

    if not samp_exe_path or not os.path.exists(samp_exe_path):
        print("samp_exe_path not set or not found in config.json", file=sys.stderr)
        sys.exit(2)

    cmd = [wine_path, samp_exe_path, target]
    try:
        subprocess.Popen(cmd)
    except Exception as exc:
        print(f"Failed to start SA:MP: {exc}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()