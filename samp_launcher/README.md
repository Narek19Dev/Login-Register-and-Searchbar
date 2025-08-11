# Python SA:MP Launcher (CEF)

This is a minimal cross-platform launcher UI built in Python using CEF that downloads your sborka archive, shows download progress, extracts it locally, and launches `samp.exe` from the sborka folder via Wine on Linux. The server IP is hardcoded to `46.174.48.235:7777` and only a Nickname is required.

## Features
- CEF UI (Chromium Embedded Framework via `cefpython3`)
- Save and load launcher configuration (`config.json`)
- Download and extract your sborka (`.zip` supported; `.7z/.rar` via patool if available)
- Hardcoded server: `46.174.48.235:7777`
- Launch `samp.exe` from the sborka via Wine on Linux

## Requirements
- Python 3.8+
- Linux: Desktop environment with X11/Wayland, GTK libs
- Wine (Linux) to launch `samp.exe`. A GTA:SA + SA:MP inside your sborka is expected; the launcher runs whatever you package.

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
  "nickname": "YourNick",
  "sborka_url": "https://your-cdn/your-sborka.zip",
  "wine_path": "/usr/bin/wine",
  "samp_relative_path": "samp.exe"
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

## How it works
- Enter Nickname, Sborka URL, Wine path (Linux), and the relative location of `samp.exe` within your sborka.
- Click Download to fetch and extract the sborka to `assets/sborka/` with a progress bar.
- Click Launch to start `samp.exe` via Wine and auto-connect to `46.174.48.235:7777`.
- No password field; nickname only.

## Notes
- For `.7z`/`.rar` archives, install `patool` and a backend (`p7zip-full`/`unrar`).
- The launcher expects your sborka to include a working `samp.exe` and required game files.
- On Windows you could adapt to launch directly without Wine (not implemented here by default).

## Development
- UI lives in `web/` and communicates with Python via CEF JavaScript bindings (`window.pyBridge.*`).
- Python sources are in `launcher/`.

## Troubleshooting
- If the UI window is blank or crashes, verify `cefpython3` installed correctly and system GTK/X11 dependencies are present.
- If the SA:MP protocol is not registered on Linux, prefer the Wine fallback by setting `wine_path` and `samp_exe_path`.
- Some desktop environments require `xdg-utils` for `xdg-open`.

## License
MIT