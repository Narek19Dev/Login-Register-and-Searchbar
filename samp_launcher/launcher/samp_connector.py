import os
import shutil
import subprocess
from typing import Optional


def _try_open_samp_url(server_ip_port: str) -> bool:
    url = f"samp://{server_ip_port}"
    # Try xdg-open first (Linux)
    xdg = shutil.which("xdg-open")
    if xdg:
        try:
            subprocess.run([xdg, url], check=False)
            return True
        except Exception:
            pass

    # Try generic webbrowser
    try:
        import webbrowser
        opened = webbrowser.open(url)
        if opened:
            return True
    except Exception:
        pass

    return False


def _try_wine_launch(wine_path: str, samp_exe_path: str, server_ip_port: str) -> bool:
    if not wine_path or not samp_exe_path:
        return False
    if not os.path.exists(samp_exe_path):
        return False

    cmd = [wine_path, samp_exe_path, server_ip_port]
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def connect_via_samp_url_or_wine(
    server_ip_port: str,
    nickname: str,
    password: str,
    wine_path: Optional[str] = None,
    samp_exe_path: Optional[str] = None,
) -> None:
    # 1) Attempt the registered samp:// protocol
    if _try_open_samp_url(server_ip_port):
        return

    # 2) Fallback: Wine + samp.exe
    if wine_path and samp_exe_path and _try_wine_launch(wine_path, samp_exe_path, server_ip_port):
        return

    raise RuntimeError(
        "Unable to open SA:MP. Ensure the samp:// protocol is registered or configure Wine and samp.exe paths."
    )