#!/bin/bash
# Build DMG for macOS. Requires: python3, pyinstaller, create-dmg or hdiutil
# Run on macOS from repo root: ./packaging/build-dmg.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

pip install -r requirements.txt PyInstaller
pyinstaller --onefile --name CyberDefense --windowed app_main.py || true
# create-dmg --volname "Cyber Defense" dist/CyberDefense.dmg dist/
echo "DMG: use create-dmg or hdiutil to wrap dist/CyberDefense"
