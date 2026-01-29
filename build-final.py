#!/usr/bin/env python3
"""
Build Final Working Windows EXE
This script creates a working executable using the corrected spec file.
"""

import subprocess
import sys
from pathlib import Path

def build_final():
    print("=" * 70)
    print("✅ Real-World Cyber Defense - Final Working Build")
    print("=" * 70)
    print()
    
    # Check if spec file exists
    spec_file = Path("CyberDefense.spec")
    if not spec_file.exists():
        print("❌ CyberDefense.spec not found!")
        print("   This spec file is required for the build.")
        sys.exit(1)
    
    # Install requirements
    print("📥 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Build using spec file
    print("\n🔨 Building Windows EXE...")
    print("-" * 70)
    
    subprocess.run(["pyinstaller", "--clean", "--noconfirm", "CyberDefense.spec"], check=False)
    
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
        print("🚀 To run the app:")
        print(f"   Go to: dist\\CyberDefense\\")
        print(f"   Run: CyberDefense.exe")
        print()
        print("💡 The app will:")
        print("   ✓ Show a GUI window")
        print("   ✓ Add an icon to your system tray")
        print("   ✓ Monitor clipboard for malicious URLs")
        print("   ✓ Provide real-time threat detection")
        print()
    else:
        print("❌ BUILD FAILED")
        sys.exit(1)

if __name__ == "__main__":
    build_final()
