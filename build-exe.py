#!/usr/bin/env python3
"""
Build Windows EXE using PyInstaller
Run this script to create cyber-defense.exe
"""

import os
import sys
import subprocess
from pathlib import Path

def build_windows_exe():
    """Build Windows executable using PyInstaller"""
    
    print("=" * 60)
    print("🛡️ Real-World Cyber Defense - Windows EXE Builder")
    print("=" * 60)
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
    
    # Build command
    print("\n🔨 Building Windows EXE...")
    print("-" * 60)
    
    build_cmd = [
        "pyinstaller",
        "--onefile",                           # Single executable file
        "--windowed",                          # No console window
        "--name", "CyberDefense",             # Output name
        "--distpath", "./dist",               # Output directory
        "--workpath", "./build",              # Build directory
        "--specpath", ".",                    # Spec file location
        "--noconfirm",                        # No confirmation prompts
        "--clean",                            # Clean build
        "app_main.py"
    ]
    
    subprocess.run(build_cmd, check=False)
    
    print("-" * 60)
    print()
    
    # Check if build was successful
    exe_path = Path("dist/CyberDefense.exe")
    if exe_path.exists():
        print("✅ BUILD SUCCESSFUL!")
        print()
        print(f"📁 Location: {exe_path.absolute()}")
        print(f"📊 Size: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
        print()
        print("🚀 You can now:")
        print("   1. Run: CyberDefense.exe")
        print("   2. Share with others")
        print("   3. Create installer with NSIS")
        print()
    else:
        print("❌ BUILD FAILED")
        print("Check error messages above")
        print()
        print("💡 Troubleshooting:")
        print("   1. Ensure PyQt5 is installed: pip install PyQt5")
        print("   2. Ensure app_main.py is in the same directory")
        print("   3. Check for syntax errors in Python files")
        sys.exit(1)

if __name__ == "__main__":
    build_windows_exe()
