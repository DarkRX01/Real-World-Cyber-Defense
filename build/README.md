Build artifacts and installer helper

Files:
- CyberDefense-installer.nsi  - NSIS script to produce a Windows installer (requires makensis)
- build_installer.bat        - Convenience batch to call makensis

**Primary distribution:** Use `python package-for-release.py` after `python build-safe-exe.py` to create `releases/CyberDefense-Windows-Portable.zip` and `CyberDefense-Windows.zip`. This is the recommended way to distribute.

How to produce an NSIS installer (Windows):
1. Ensure `dist\CyberDefense\` exists (run `python build-safe-exe.py`).
2. Note: The NSIS script expects `dist\CyberDefense.exe` (single file). For onedir builds, use the portable ZIP instead.
3. Install NSIS and ensure `makensis.exe` is in your PATH.
4. From project root, run: `build\build_installer.bat`

This produces `Cyber Defense-setup-3.0.0.exe` when successful.
