import json
import os
import sys
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from cefpython3 import cefpython as cef
import requests

from .samp_connector import run_samp_exe_with_wine


APP_DIR = Path(__file__).resolve().parent.parent
LAUNCHER_DIR = APP_DIR / "launcher"
WEB_DIR = APP_DIR / "web"
CONFIG_PATH = LAUNCHER_DIR / "config.json"
ASSETS_DIR = APP_DIR / "assets"
SBORKA_DIR = ASSETS_DIR / "sborka"
DOWNLOADS_DIR = ASSETS_DIR / "downloads"

# Hardcoded server IP:Port per user requirement
TARGET_SERVER = "46.174.48.235:7777"

DEFAULT_CONFIG: Dict[str, Any] = {
    "nickname": "Player",
    "sborka_url": "",  # Direct link to your sborka .zip or .7z file
    "wine_path": "/usr/bin/wine",
    "samp_relative_path": "samp.exe"  # relative inside sborka folder
}


def ensure_dirs() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SBORKA_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    LAUNCHER_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    ensure_dirs()
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    ensure_dirs()
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


class BrowserBindings:
    def __init__(self):
        self._config_cache = load_config()
        self._progress = 0
        self._status = ""

    # Exposed to JS
    def get_config(self) -> Dict[str, Any]:
        return self._config_cache

    # Exposed to JS
    def save_config(self, config_json: str) -> Dict[str, Any]:
        try:
            data = json.loads(config_json)
            self._config_cache = {**DEFAULT_CONFIG, **data}
            save_config(self._config_cache)
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # Exposed to JS
    def get_progress(self) -> Dict[str, Any]:
        return {"progress": self._progress, "status": self._status}

    # Internal helper
    def _set_progress(self, pct: int, status: Optional[str] = None) -> None:
        self._progress = max(0, min(100, int(pct)))
        if status is not None:
            self._status = status

    # Exposed to JS
    def download_sborka(self) -> Dict[str, Any]:
        url = self._config_cache.get("sborka_url", "").strip()
        if not url:
            return {"ok": False, "error": "Set sborka_url in settings"}

        def worker():
            try:
                self._set_progress(0, "Starting download…")
                local_name = url.split("/")[-1] or "sborka.zip"
                target_path = DOWNLOADS_DIR / local_name

                with requests.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    total = int(r.headers.get("content-length", 0))
                    downloaded = 0
                    chunk = 1024 * 256
                    with open(target_path, "wb") as f:
                        for part in r.iter_content(chunk_size=chunk):
                            if not part:
                                continue
                            f.write(part)
                            downloaded += len(part)
                            if total:
                                pct = int(downloaded * 100 / total)
                                self._set_progress(pct, f"Downloading… {pct}%")
                self._set_progress(100, "Download complete. Extracting…")

                # Extract
                ext = local_name.lower()
                SBORKA_DIR.mkdir(parents=True, exist_ok=True)
                if ext.endswith(".zip"):
                    import zipfile
                    with zipfile.ZipFile(target_path, 'r') as zf:
                        zf.extractall(SBORKA_DIR)
                elif ext.endswith(".7z") or ext.endswith(".rar"):
                    # Try patool if available
                    try:
                        import patoolib  # type: ignore
                        patoolib.extract_archive(str(target_path), outdir=str(SBORKA_DIR))
                    except Exception as e:
                        self._set_progress(100, "Extraction failed: install patool + backend (7z/unrar)")
                        return
                else:
                    self._set_progress(100, "Unknown archive format; place files manually in assets/sborka")
                    return

                self._set_progress(100, "Ready. You can launch now.")
            except Exception as exc:
                self._set_progress(0, f"Error: {exc}")

        threading.Thread(target=worker, daemon=True).start()
        return {"ok": True}

    # Exposed to JS
    def launch(self, nickname: str) -> Dict[str, Any]:
        try:
            samp_rel = self._config_cache.get("samp_relative_path", "samp.exe")
            samp_path = SBORKA_DIR / samp_rel
            run_samp_exe_with_wine(
                samp_exe_path=str(samp_path),
                server_ip_port=TARGET_SERVER,
                wine_path=self._config_cache.get("wine_path", None),
            )
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


def main() -> None:
    sys.excepthook = cef.ExceptHook

    settings = {
        "persist_session_cookies": True,
        "context_menu": {"enabled": False},
    }
    cef.Initialize(settings=settings)

    index_html = WEB_DIR / "index.html"
    if not index_html.exists():
        raise FileNotFoundError(f"Missing UI: {index_html}")

    bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=True)
    bridge = BrowserBindings()
    bindings.SetObject("pyBridge", bridge)

    window_info = cef.WindowInfo()
    window_info.caption = "SA:MP Python Launcher"

    browser = cef.CreateBrowserSync(
        url=f"file://{index_html}",
        window_title="SA:MP Python Launcher",
        window_info=window_info,
    )
    browser.SetJavascriptBindings(bindings)

    cef.MessageLoop()
    cef.Shutdown()


if __name__ == "__main__":
    main()