#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HANDLER = PROJECT_ROOT / "scripts" / "samp_url_handler.py"
APPLICATIONS_DIR = Path.home() / ".local" / "share" / "applications"
DESKTOP_FILE = APPLICATIONS_DIR / "samp-url.desktop"

DESKTOP_CONTENT = f"""
[Desktop Entry]
Name=SA:MP URL Handler
Comment=Handle samp:// URLs and launch SA:MP via Wine
Exec=python3 {HANDLER} %u
Terminal=false
Type=Application
NoDisplay=true
MimeType=x-scheme-handler/samp;
""".strip() + "\n"


def write_desktop_file():
    APPLICATIONS_DIR.mkdir(parents=True, exist_ok=True)
    DESKTOP_FILE.write_text(DESKTOP_CONTENT, encoding="utf-8")


def register_mime():
    # Best-effort xdg registration
    try:
        subprocess.run(["xdg-mime", "default", DESKTOP_FILE.name, "x-scheme-handler/samp"], check=False)
        subprocess.run(["update-desktop-database", str(APPLICATIONS_DIR)], check=False)
        print("Registered samp:// protocol via xdg-mime")
    except Exception:
        print("Could not run xdg-mime; ensure it is installed or add entry to mimeapps.list manually")


def main():
    write_desktop_file()
    register_mime()
    print(f"Desktop entry written to: {DESKTOP_FILE}")
    print("If the protocol doesn't work immediately, log out and back in, or run:")
    print(f"  xdg-mime default {DESKTOP_FILE.name} x-scheme-handler/samp")


if __name__ == "__main__":
    main()