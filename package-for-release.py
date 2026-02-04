#!/usr/bin/env python3
"""
Package Cyber Defense for distribution
Creates a ZIP file with all necessary files
"""

import zipfile
import os
from pathlib import Path
import shutil

def create_release_package():
    # NOTE: Keep console output ASCII-only (Windows cp1252-safe).
    print("=" * 70)
    print("Cyber Defense - Release Packager")
    print("=" * 70)
    print()
    
    # Check if dist folder exists
    dist_dir = Path("dist/CyberDefense")
    if not dist_dir.exists():
        print("ERROR: dist/CyberDefense not found!")
        print("   Please run 'python build-final.py' first")
        return
    
    # Create releases folder
    releases_dir = Path("releases")
    releases_dir.mkdir(exist_ok=True)
    
    # Create ZIP filename
    zip_name_portable = "CyberDefense-Windows-Portable.zip"
    zip_name_simple = "CyberDefense-Windows.zip"
    zip_path = releases_dir / zip_name_portable
    zip_path_simple = releases_dir / zip_name_simple
    
    # Remove old zip if exists
    if zip_path.exists():
        zip_path.unlink()
    
    print(f"Creating {zip_name_portable} ...")
    print()
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from dist/CyberDefense
        for file_path in dist_dir.rglob('*'):
            if file_path.is_file():
                arcname = f"CyberDefense/{file_path.relative_to(dist_dir)}"
                zipf.write(file_path, arcname)
                # Avoid noisy output (and unicode) for large zips
                pass
        
        # Add README directly via writestr (avoids temp file locks on Windows)
        readme_content = """Cyber Defense - Windows Portable Edition
==========================================

INSTALLATION:
-------------
1. Extract this entire ZIP file to a folder of your choice
2. Go into the CyberDefense folder
3. Run "CyberDefense.exe"

IMPORTANT:
----------
- DO NOT move CyberDefense.exe out of its folder.
- Keep all files together in the same folder (DLLs, etc.).

FIRST RUN:
----------
If Windows SmartScreen shows a warning:
  1. Click "More info"
  2. Click "Run anyway"

If your antivirus blocks it:
  - False positives are common for unsigned apps
  - Add an exception for the CyberDefense folder

FEATURES:
---------
- Real-time threat detection
- Clipboard URL monitoring
- Tracker blocking
- Phishing detection
- Modern GUI dashboard
- System tray integration

TROUBLESHOOTING:
----------------
If the app doesn't start:
  1. Make sure all files are extracted together
  2. Check if antivirus is blocking it
  3. Try running as administrator
  4. Check logs at: %APPDATA%\\.cyber-defense\\logs\\

SYSTEM REQUIREMENTS:
--------------------
- Windows 10 or later
- ~100 MB free disk space
- Internet connection (optional, for updates)

For support and updates:
https://github.com/DarkRX01/Real-World-Cyber-Defense
"""
        zipf.writestr("README.txt", readme_content)
        print("Added: README.txt")
    
    print()
    print("=" * 70)
    print("PACKAGE CREATED SUCCESSFULLY!")
    print()
    print(f"Location: {zip_path.absolute()}")
    print(f"Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    print("READY FOR DISTRIBUTION!")
    print()
    # Also provide a simpler alternate name for convenience
    try:
        if zip_path_simple.exists():
            zip_path_simple.unlink()
        shutil.copy2(zip_path, zip_path_simple)
        print(f"Also created: {zip_path_simple.name}")
    except Exception as e:
        print(f"WARNING: Could not create {zip_name_simple}: {e}")
    print()
    print("Next steps:")
    print("  1. Upload the ZIP to GitHub Releases")
    print("  2. Users download and extract the entire ZIP")
    print("  3. Run CyberDefense.exe from the extracted folder")
    print()

if __name__ == "__main__":
    create_release_package()
