# Python SA:MP Launcher (CEF)

This is a minimal cross-platform launcher UI built in Python using CEF that helps you connect to a SA:MP server. It provides a Chromium-based UI, allows saving nickname and server details, optionally downloads a skin preview, and attempts to connect to SA:MP via the `samp://` URL or directly via Wine on Linux.

## Features
- CEF UI (Chromium Embedded Framework via `cefpython3`)
- Save and load launcher configuration (`config.json`)
- Optional skin preview download (placeholder logic you can wire to your server's API)
- Connect to SA:MP using `samp://ip:port` URL
- Linux Wine fallback: run `samp.exe` through Wine if the protocol is not registered

## Requirements
- Python 3.8+
- Linux: Desktop environment with X11/Wayland, GTK libs
- Wine (Linux) if you plan to launch the Windows SA:MP client
- A working GTA:SA + SA:MP installation (Windows or Wine prefix)

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `cefpython3` fails to install, ensure you have system dependencies (GTK, libX11, etc.) installed. See the `cefpython3` docs for your distro.

## Configure
Edit `launcher/config.json` after first run or use the UI fields. Example:

```json
{
  "server_ip_port": "127.0.0.1:7777",
  "nickname": "YourNick",
  "password": "",
  "skin_download_url": "https://example.com/skins/{nickname}.png",
  "wine_path": "/usr/bin/wine",
  "samp_exe_path": "/path/to/your/wine/prefix/drive_c/Program Files/San Andreas Multiplayer/samp.exe"
}
```

- `skin_download_url`: Optional; supports `{nickname}` placeholder.
- `wine_path`: Optional; used for Linux Wine fallback.
- `samp_exe_path`: Optional; path to your `samp.exe` in Wine prefix.

## Run
```bash
source .venv/bin/activate
python -m launcher.main
```

## Notes on Connecting to SA:MP
- The launcher first tries: `xdg-open "samp://<ip:port>"` (Linux). If you have the SA:MP protocol registered (e.g., via Wine/desktop integration), this should open the SA:MP client and connect.
- If that fails, the launcher optionally falls back to: `wine <samp_exe_path> <ip:port>`.
- Nickname/password handling depends on your SA:MP client setup. Most clients read nickname from `sa-mp.cfg`. You can set it within the client as usual.

### Linux: Register the samp:// protocol to wire the launcher to SA:MP
If `samp://` links don't open SA:MP, register a URL handler that launches Wine:

```bash
# 1) Set `wine_path` and `samp_exe_path` in `launcher/config.json` (run the app once to create it)
# 2) Register the protocol (writes `~/.local/share/applications/samp-url.desktop`)
python3 scripts/register_protocol_linux.py

# 3) Test it
xdg-open "samp://127.0.0.1:7777"
```

This creates a desktop entry pointing to `scripts/samp_url_handler.py` which reads your `launcher/config.json` and runs `wine <samp_exe_path> <ip:port>`.

## Skin Download
This project includes a placeholder skin download for preview only (PNG/JPG). If your server provides custom skins (DL), wire `skin_download_url` to your API/CDN and adapt logic in `launcher/main.py` if needed (DFF/TXD handling would be client-side and platform-specific).

## Development
- UI lives in `web/` and communicates with Python via CEF JavaScript bindings (`window.pyBridge.*`).
- Python sources are in `launcher/`.

## Troubleshooting
- If the UI window is blank or crashes, verify `cefpython3` installed correctly and system GTK/X11 dependencies are present.
- If the SA:MP protocol is not registered on Linux, prefer the Wine fallback by setting `wine_path` and `samp_exe_path`.
- Some desktop environments require `xdg-utils` for `xdg-open`.

## License
MIT