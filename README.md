# Ingenarte AutoClicker

**Cross-platform GUI + CLI automation toolkit built in Python**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)  
_Mac / Windows • Image-based clicking • JSON workflows • Modern CustomTkinter GUI_

---

## Overview

Ingenarte AutoClicker lets you **record, edit and replay** complex interaction flows:

- **Mouse & keyboard events** recorded with millisecond precision.
- **Image recognition** (MSS + OpenCV) to click dynamic screen elements.
- **Excel integration** – read inputs and write results to `.xlsx` files.
- **JSON workflows** – steps are saved and reused via portable `.json` files.
- **Headless CLI** (`sudo IngenarteAutoClicker /path/flow.json`) for server or pipeline use.
- **Modern GUI** written with CustomTkinter for non-technical users.

The project targets **macOS (Darwin 13+) and Windows 10+**. Linux is expected to work but is not part of the official test matrix.

---

## Quick Start (macOS)

1. **Grant permissions once**

   - Go to **System Settings ➜ Privacy & Security ➜ Accessibility** and **Screen Recording**, then enable **Terminal** (or iTerm, Warp, etc.).

2. **Run with elevated privileges** (required by Apple to dispatch synthetic input):

   ```bash
# Grant execution permission
chmod +x /path/to/IngenarteAutoClicker

# Then run it with elevated privileges
sudo /path/to/IngenarteAutoClicker

   # Run a stored workflow headless
   sudo IngenarteAutoClicker /absolute/path/to/flow.json
   ```

> **ℹ️ Note:** `sudo` is mandatory on macOS because the Accessibility API rejects unprivileged processes.

---

## Download pre-built binaries

| OS / Arch                     | Binary                                                                                                                | SHA-256                                                            |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Windows x64                   | [IngenarteAutoClicker.exe](https://github.com/Ingenarte/Ingenarte_AutoClicker/raw/main/dist/IngenarteAutoClicker.exe) | `5d86c48616f39942235ac4e4040ca64b2bca2302da06d8a12d905312786c3ffa` |
| macOS (Universal) / Linux x64 | [IngenarteAutoClicker](https://github.com/Ingenarte/Ingenarte_AutoClicker/raw/main/dist/IngenarteAutoClicker)         | `262b120482c37272e49e8919d4000453a081d7774ca0f4356de096b3b27e7bab` |

_Binaries in `dist/` are built from the latest Git tag and are signed & notarized where the platform allows._

---

## Running from source

```bash
git clone git@github.com:Ingenarte/Ingenarte_AutoClicker.git
cd Ingenarte_AutoClicker

# Isolate dependencies
python -m venv .venv && source .venv/bin/activate

# Install core + platform extras
pip install -r requirements.txt

# Launch the GUI
python main.py
```

### Build your own executables

```bash

Windows PS

pyinstaller main.py `
  --name IngenarteAutoClicker `
  --onefile `
  --icon "public\ingenarte_icon_ico.ico" `
  --add-data "public\ingenarte_icon.png;public" `
  --add-data "public\ingenarte_icon_ico.ico;public" `
  --add-data "modals;modals"

MacOs

rm -rf build IngenarteAutoClicker.spec
pyinstaller main.py \
   --name IngenarteAutoClicker \
   --onefile \
   --osx-bundle-identifier com.ingenarte.autoclicker \
   --add-data "public:public" \
   --add-data "modals:modals" \
   --hidden-import pynput \
   --hidden-import pynput.keyboard \
   --hidden-import pynput.mouse \
   --hidden-import pyautogui \
   --icon public/ingenarte_icon_ico.ico


```

---

## Core dependencies

| Purpose          | Library                      |
| ---------------- | ---------------------------- |
| GUI              | **CustomTkinter (ctk)**      |
| Input automation | **PyAutoGUI**, **pynput**    |
| Screen capture   | **mss**, **Pillow**          |
| Image search     | **opencv-python**, **numpy** |
| Data I/O         | **openpyxl**                 |
| Packaging        | **PyInstaller**              |

_See `requirements.txt` for exact, locked versions._

---

## CLI reference

| Flag          | Description                | Default |
| ------------- | -------------------------- | ------- |
| `<json-file>` | Execute the given workflow | —       |

---

## TODO – Full refactor roadmap

- Split core / GUI into `ingenarte/core` and `ingenarte/ui` sub-packages.
- Replace global state with dependency injection (`@dataclass` configs).
- Add full type annotations and enable `mypy --strict`.
- Extract Spanish-only strings into `i18n/` (gettext `.po`).
- Create a plug-in API so third-party steps can be dropped in.
- GitHub Actions: lint, test, build, sign & publish on each tag.
- ≥ 80 % code-coverage gate to `main`.
- Document the public Python API with MkDocs + Material theme.
- Optional: Wayland support on modern Linux desktops.

---

## Support / Questions

Open an issue on GitHub

---

## License

© 2025 Ingenarte.  
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).  
The license will be included officially with the first stable release tag.

---
