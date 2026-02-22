#!/usr/bin/env python3
"""Fast PyInstaller build for CyberDefense - optimized for speed."""
import subprocess
import sys
import os
from pathlib import Path

def build_exe():
    """Build standalone EXE with PyInstaller."""
    root = Path(__file__).parent
    
    # Fast build config
    icon_path = root / "icons" / "shield.ico"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Single EXE file
        "--windowed",  # No console window
        "--distpath", str(root / "dist"),
        "--workpath", str(root / "build"),
        "--specpath", str(root),
        "--name", "CyberDefense",
        # icon args will be inserted below if the file exists
        "--hidden-import=PyQt5",
        "--hidden-import=threat_engine",
        "--hidden-import=background_service",
        "--hidden-import=notification_manager",
        "--hidden-import=vpn_client",
        "--hidden-import=ransomware_shield",
        "--hidden-import=realtime_monitor",
        "--hidden-import=network_monitor",
        "--hidden-import=registry_monitor",
        "--hidden-import=process_injection_detector",
        "--hidden-import=rootkit_detector",
        "--hidden-import=advanced_ransomware_detector",
        "--hidden-import=advanced_behavioral_analysis",
        "--hidden-import=threat_detection_orchestrator",
        "--collect-all=yara",
        "--noconfirm",
        "--log-level=ERROR",
        str(root / "app_main.py")
    ]
    # Insert icon args only if the icon file exists to avoid PyInstaller errors
    if icon_path.exists():
        # inject after the --name argument (position 8)
        # find index of --name then insert ["--icon", str(icon_path)] after it
        try:
            name_idx = cmd.index("--name")
            insert_pos = name_idx + 2  # --name <value> so insert after value
            cmd[insert_pos:insert_pos] = ["--icon", str(icon_path)]
        except ValueError:
            # fallback: append
            cmd += ["--icon", str(icon_path)]
    
    print("🔨 Building EXE... (this takes 2-3 minutes)")
    print(f"Command: {' '.join(cmd[:5])} ...")
    
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    success = build_exe()
    if success:
        exe_path = Path(__file__).parent / "dist" / "CyberDefense.exe"
        if exe_path.exists():
            print(f"\n✅ EXE BUILT SUCCESSFULLY!")
            print(f"📁 Location: {exe_path}")
            print(f"📊 Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            print(f"\n🚀 You can run: {exe_path}")
        else:
            print("❌ Build succeeded but EXE not found")
            sys.exit(1)
    else:
        print("❌ Build failed")
        sys.exit(1)
