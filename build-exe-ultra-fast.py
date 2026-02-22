#!/usr/bin/env python3
"""Ultra-fast PyInstaller build - 30-60 seconds."""
import subprocess
import sys
import os
from pathlib import Path
import time

def build_exe():
    """Minimal fast build."""
    root = Path(__file__).parent
    start = time.time()
    
    # ULTRA-FAST: Only essential imports
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--distpath", str(root / "dist"),
        "--buildpath", str(root / "build_temp"),
        "--specpath", str(root),
        "--name", "CyberDefense",
        "--noconfirm",
        "--log-level=CRITICAL",
        "--noupx",  # Skip compression for speed
        "--strip",  # Remove debug symbols
        str(root / "app_main.py")
    ]
    
    print("⚡ ULTRA-FAST BUILD MODE (30-60 secs)")
    print("=" * 50)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start
    
    if result.returncode == 0:
        exe_path = root / "dist" / "CyberDefense.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / 1024 / 1024
            print(f"\n✅ BUILD COMPLETE IN {elapsed:.0f} seconds!")
            print(f"📁 {exe_path}")
            print(f"💾 Size: {size_mb:.1f} MB\n")
            return True
    
    print(f"\n❌ Build failed (after {elapsed:.0f}s)")
    print("STDERR:", result.stderr[:500])
    return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
