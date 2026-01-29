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
    print("=" * 70)
    print("📦 Cyber Defense - Release Packager")
    print("=" * 70)
    print()
    
    # Check if dist folder exists
    dist_dir = Path("dist/CyberDefense")
    if not dist_dir.exists():
        print("❌ dist/CyberDefense not found!")
        print("   Please run 'python build-final.py' first")
        return
    
    # Create releases folder
    releases_dir = Path("releases")
    releases_dir.mkdir(exist_ok=True)
    
    # Create ZIP filename
    zip_name = "CyberDefense-Windows-Portable.zip"
    zip_path = releases_dir / zip_name
    
    # Remove old zip if exists
    if zip_path.exists():
        zip_path.unlink()
    
    print(f"📦 Creating {zip_name}...")
    print()
    
    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from dist/CyberDefense
        for file_path in dist_dir.rglob('*'):
            if file_path.is_file():
                arcname = f"CyberDefense/{file_path.relative_to(dist_dir)}"
                zipf.write(file_path, arcname)
                print(f"  ✓ Added: {arcname}")
        
        # Add README
        readme_content = """Cyber Defense - Windows Portable Edition
==========================================

INSTALLATION:
-------------
1. Extract this entire ZIP file to a folder of your choice
2. Go into the CyberDefense folder
3. Run "CyberDefense.exe"

IMPORTANT:
----------
⚠️  DO NOT move CyberDefense.exe out of its folder!
⚠️  Keep all files together in the same folder

The application needs all the DLL files and dependencies
that are included in this folder.

FIRST RUN:
----------
If Windows SmartScreen shows a warning:
  1. Click "More info"
  2. Click "Run anyway"

If your antivirus blocks it:
  - This is a false positive (common for new unsigned apps)
  - Add an exception for the CyberDefense folder

FEATURES:
---------
✓ Real-time threat detection
✓ Clipboard URL monitoring
✓ Tracker blocking
✓ Phishing detection
✓ Modern GUI dashboard
✓ System tray integration

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
- 100 MB free disk space
- Internet connection (optional, for updates)

For support and updates:
https://github.com/DarkRX01/Real-World-Cyber-Defense
"""
        
        # Write README inside the ZIP
        readme_path = releases_dir / "README.txt"
        readme_path.write_text(readme_content, encoding="utf-8")
        zipf.write(readme_path, "README.txt")
        readme_path.unlink()  # Delete temp file
        print(f"  ✓ Added: README.txt")
    
    print()
    print("=" * 70)
    print("✅ PACKAGE CREATED SUCCESSFULLY!")
    print()
    print(f"📁 Location: {zip_path.absolute()}")
    print(f"📊 Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()
    print("📤 READY FOR DISTRIBUTION!")
    print()
    print("Next steps:")
    print("  1. Upload this ZIP to GitHub Releases")
    print("  2. Users download and extract the entire ZIP")
    print("  3. Run CyberDefense.exe from the extracted folder")
    print()

if __name__ == "__main__":
    create_release_package()
