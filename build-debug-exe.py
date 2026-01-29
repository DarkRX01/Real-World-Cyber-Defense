#!/usr/bin/env python3
"""
Build DEBUG Windows EXE with console output
This version will show error messages if the app crashes
"""

import os
import sys
import subprocess
from pathlib import Path

def build_debug_exe():
    """Build Windows executable with console for debugging"""
    
    print("=" * 70)
    print("🐛 Real-World Cyber Defense - DEBUG EXE Builder")
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
    
    # Build command with CONSOLE enabled for debugging
    print("\n🔨 Building DEBUG Windows EXE (with console)...")
    print("-" * 70)
    
    build_cmd = [
        "pyinstaller",
        "--onefile",                           # Single executable file
        "--console",                           # SHOW CONSOLE for debugging
        "--name", "CyberDefense-DEBUG",        # Debug version name
        "--distpath", "./dist",                # Output directory
        "--workpath", "./build",               # Build directory
        "--specpath", ".",                     # Spec file location
        "--noconfirm",                         # No confirmation prompts
        "--clean",                             # Clean build
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtWidgets",
        "--hidden-import", "pyperclip",
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
    exe_path = Path("dist/CyberDefense-DEBUG.exe")
    if exe_path.exists():
        print("✅ DEBUG BUILD SUCCESSFUL!")
        print()
        print(f"📁 Location: {exe_path.absolute()}")
        print(f"📊 Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
        print()
        print("🐛 This DEBUG version will:")
        print("   ✓ Show a console window with error messages")
        print("   ✓ Display what went wrong if the app crashes")
        print("   ✓ Help diagnose missing dependencies")
        print()
        print("🚀 Run the exe and check the console for any errors!")
        print()
    else:
        print("❌ BUILD FAILED")
        print("Check error messages above")
        sys.exit(1)

if __name__ == "__main__":
    build_debug_exe()
