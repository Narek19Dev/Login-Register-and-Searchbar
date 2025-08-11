import json
import os
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any, Dict

from cefpython3 import cefpython as cef
import requests

from .samp_connector import connect_via_samp_url_or_wine


APP_DIR = Path(__file__).resolve().parent.parent
LAUNCHER_DIR = APP_DIR / "launcher"
WEB_DIR = APP_DIR / "web"
CONFIG_PATH = LAUNCHER_DIR / "config.json"
ASSETS_DIR = APP_DIR / "assets"
SKINS_DIR = ASSETS_DIR / "skins"


DEFAULT_CONFIG: Dict[str, Any] = {
    "server_ip_port": "127.0.0.1:7777",
    "nickname": "Player",
    "password": "",
    "skin_download_url": "",
    "wine_path": "/usr/bin/wine",
    "samp_exe_path": ""
}


def ensure_dirs() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SKINS_DIR.mkdir(parents=True, exist_ok=True)
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


def download_skin_for_nickname(nickname: str, skin_download_url: str) -> str:
    ensure_dirs()
    if not skin_download_url:
        raise ValueError("skin_download_url not configured")
    url = skin_download_url.replace("{nickname}", nickname)
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    # Infer extension
    content_type = response.headers.get("content-type", "").lower()
    ext = ".png"
    if "jpeg" in content_type or "jpg" in content_type:
        ext = ".jpg"
    elif "webp" in content_type:
        ext = ".webp"

    target_path = SKINS_DIR / f"{nickname}{ext}"
    with open(target_path, "wb") as f:
        f.write(response.content)
    return str(target_path)


class BrowserBindings:
    def __init__(self):
        self._config_cache = load_config()

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
    def download_skin(self, nickname: str) -> Dict[str, Any]:
        try:
            skin_url = self._config_cache.get("skin_download_url", "")
            path = download_skin_for_nickname(nickname, skin_url)
            # Return file:// URL so the webview can preview
            return {"ok": True, "path": f"file://{path}"}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # Exposed to JS
    def connect(self, server_ip_port: str, nickname: str, password: str) -> Dict[str, Any]:
        try:
            wine_path = self._config_cache.get("wine_path", "")
            samp_exe_path = self._config_cache.get("samp_exe_path", "")
            connect_via_samp_url_or_wine(
                server_ip_port=server_ip_port,
                nickname=nickname,
                password=password,
                wine_path=wine_path,
                samp_exe_path=samp_exe_path,
            )
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


def main() -> None:
    sys.excepthook = cef.ExceptHook

    settings = {
        "persist_session_cookies": True,
        "context_menu": {
            "enabled": True,
        },
    }
    cef.Initialize(settings=settings)

    index_html = WEB_DIR / "index.html"
    if not index_html.exists():
        raise FileNotFoundError(f"Missing UI: {index_html}")

    bindings = cef.JavascriptBindings(bindToFrames=False, bindToPopups=True)
    bridge = BrowserBindings()
    # Expose as window.pyBridge in the renderer
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