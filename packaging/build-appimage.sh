#!/bin/bash
# Build AppImage for Linux. Requires: python3, pip, appimage-builder or linuxdeploy
# Run from repo root: ./packaging/build-appimage.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

# Optional: create venv and install
python3 -m venv .venv-appimage 2>/dev/null || true
source .venv-appimage/bin/activate 2>/dev/null || true
pip install -r requirements.txt PyInstaller

# Build onefile or onedir
python -m PyInstaller --onefile --name CyberDefense --windowed app_main.py 2>/dev/null || true
# If using linuxdeploy
# download linuxdeploy-x86_64.AppImage and run:
# ./linuxdeploy-x86_64.AppImage --executable=dist/CyberDefense --appdir=AppDir --output appimage
echo "AppImage build: add linuxdeploy step; output in dist/"
