#!/usr/bin/env python3
"""
Build FIXED Windows EXE - Solves PyQt5 DLL extraction issues
Uses --onedir instead of --onefile to avoid DLL extraction failures
"""

import os
import sys
import subprocess
from pathlib import Path

def build_fixed_exe():
    """Build Windows executable that avoids DLL extraction issues"""
    
    print("=" * 70)
    print("🔧 Real-World Cyber Defense - FIXED EXE Builder")
    print("=" * 70)
    print()
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Install requirements
    print("📥 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Build command - USE --onedir instead of --onefile to avoid DLL issues
    print("\n🔨 Building FIXED Windows EXE...")
    print("-" * 70)
    print()
    print("ℹ️  Using --onedir mode to avoid PyQt5 DLL extraction issues")
    print()
    
    build_cmd = [
        "pyinstaller",
        "--onedir",                            # Directory mode (not single file)
        "--windowed",                          # No console window
        "--name", "CyberDefense",              # Output name
        "--distpath", "./dist",                # Output directory
        "--workpath", "./build",               # Build directory
        "--specpath", ".",                     # Spec file location
        "--noconfirm",                         # No confirmation prompts
        "--clean",                             # Clean build
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "pyperclip",
        "--hidden-import", "threat_engine",    # Include local module
        "--hidden-import", "background_service", # Include local module
        "app_main.py"
    ]
    
    # Add icon if available
    icon_path = Path("icons/icon.ico")
    if icon_path.exists():
        build_cmd.extend(["--icon", str(icon_path)])
    
    subprocess.run(build_cmd, check=False)
    
    print("-" * 70)
    print()
    
    # Check if build was successful
    exe_path = Path("dist/CyberDefense/CyberDefense.exe")
    if exe_path.exists():
        print("✅ BUILD SUCCESSFUL!")
        print()
        print(f"📁 Location: {exe_path.absolute()}")
        print(f"📊 Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
        print()
        print("📦 This version includes:")
        print("   ✓ Main executable: CyberDefense.exe")
        print("   ✓ All required DLLs in the same folder")
        print("   ✓ No DLL extraction issues")
        print()
        print("🚀 To run the app:")
        print(f"   Navigate to: dist\\CyberDefense\\")
        print(f"   Run: CyberDefense.exe")
        print()
        
        # Create launcher script in dist folder
        try:
            dist_dir = exe_path.parent
            
            # Create a convenient launcher
            launcher_path = dist_dir / "Run Cyber Defense.bat"
            launcher_content = """@echo off
setlocal
cd /d "%~dp0"
start "" "CyberDefense.exe"
endlocal
"""
            launcher_path.write_text(launcher_content, encoding="utf-8")
            print(f"✅ Created launcher: {launcher_path.name}")
            
            # Create README
            readme_path = dist_dir / "README.txt"
            readme_content = """Real-World Cyber Defense - Windows Application
==============================================

HOW TO RUN:
-----------
Option 1: Double-click "Run Cyber Defense.bat"
Option 2: Double-click "CyberDefense.exe"

IMPORTANT:
----------
- Keep all files in this folder together (don't move just the .exe)
- The app needs the DLL files that are in this folder

If Windows SmartScreen shows a warning:
- Click "More info"
- Click "Run anyway"

If your antivirus blocks it:
- This can be a false positive for unsigned apps
- Add an exception for this folder in your antivirus settings

TROUBLESHOOTING:
----------------
If the app doesn't start:
1. Check if antivirus is blocking it
2. Run as administrator (right-click > Run as administrator)
3. Check the logs at: %APPDATA%\\.cyber-defense\\logs\\

For support, check the GitHub repository.
"""
            readme_path.write_text(readme_content, encoding="utf-8")
            print(f"✅ Created README: {readme_path.name}")
            print()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not create helper files: {e}")
            print()
        
        print("✨ The app is ready to use!")
        print()
        
    else:
        print("❌ BUILD FAILED")
        print("Check error messages above")
        sys.exit(1)

if __name__ == "__main__":
    build_fixed_exe()
