#!/bin/bash
# One-time setup: makes a private Python environment in this folder and installs the image tool.
cd "$(dirname "$0")" || exit 1
echo "🏀 BBL Best & Worst — setup"
echo
if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys' >/dev/null 2>&1; then
  echo "Python isn't installed yet. A window should pop up offering to install Apple's developer tools —"
  echo "click Install, wait for it to finish, then double-click this Setup file again."
  xcode-select --install >/dev/null 2>&1
  read -n 1 -s -r -p "Press any key to close"; exit 1
fi
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
  echo "Your Python is too old (need 3.9+). Install the latest from https://www.python.org/downloads/macos/ and run Setup again."
  read -n 1 -s -r -p "Press any key to close"; exit 1
fi
set -e
echo "1/3 Creating the environment…"
python3 -m venv .venv
echo "2/3 Installing Playwright (draws the Top 10 image)…"
.venv/bin/pip install --quiet --upgrade pip playwright
echo "3/3 Downloading the headless browser it uses (about 150 MB, one time)…"
.venv/bin/python -m playwright install chromium
chmod +x "2 - BBL Tonight.command" 2>/dev/null || true
echo
echo "✅ Setup done. Next: install the roster bookmark (README step 3), then double-click '2 - BBL Tonight'."
read -n 1 -s -r -p "Press any key to close"
