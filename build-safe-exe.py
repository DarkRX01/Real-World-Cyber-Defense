#!/usr/bin/env python3
"""
Build Antivirus-Friendly Windows EXE using PyInstaller
This configuration avoids common antivirus triggers
"""

import os
import sys
import subprocess
from pathlib import Path

def build_safe_windows_exe():
    """Build Windows executable that's less likely to trigger antivirus"""
    
    print("=" * 70)
    print("🛡️ Real-World Cyber Defense - Antivirus-Friendly EXE Builder")
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
    
    # Create safe PyInstaller spec file
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['app_main.py'],
    pathex=[],
    binaries=[],
    datas=[('icons/shield.svg', 'icons')] if os.path.exists(os.path.join('icons', 'shield.svg')) else [],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'test'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CyberDefense',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/icon.ico' if os.path.exists(os.path.join('icons', 'icon.ico')) else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CyberDefense'
)
'''
    
    # Write spec file
    with open('CyberDefense-safe.spec', 'w') as f:
        f.write(spec_content)
    
    # Create version info file
    version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(2,0,0,0),
    prodvers=(2,0,0,0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Cyber Defense Security'),
        StringStruct(u'FileDescription', u'Real-World Cyber Defense Tool'),
        StringStruct(u'FileVersion', u'2.0.0.0'),
        StringStruct(u'InternalName', u'CyberDefense'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
        StringStruct(u'OriginalFilename', u'CyberDefense.exe'),
        StringStruct(u'ProductName', u'Cyber Defense'),
        StringStruct(u'ProductVersion', u'2.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    
    # Build command with antivirus-friendly options
    print("\n🔨 Building Antivirus-Friendly Windows EXE...")
    print("-" * 70)
    
    build_cmd = [
        "pyinstaller",
        "--clean",                    # Clean build
        "--noconfirm",                # No confirmation prompts
        "--distpath", "./dist",       # Output directory
        "--workpath", "./build",      # Build directory
        "CyberDefense-safe.spec"
    ]
    
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
        print("🛡️ Antivirus-Friendly Features:")
        print("   ✓ No suspicious imports")
        print("   ✓ Proper version information")
        print("   ✓ Clean build configuration")
        print("   ✓ No UPX compression")
        print()
        print("🚀 Next Steps:")
        print("   1. Test the executable locally")
        print("   2. Upload to VirusTotal for analysis")
        print("   3. Submit to antivirus vendors if needed")
        print()
        
        # Create test script
        test_script = '''@echo off
echo Testing CyberDefense.exe...
echo.
echo If antivirus blocks this, you may need to:
echo 1. Add exception to your antivirus
echo 2. Run as administrator
echo 3. Submit to antivirus vendor for whitelisting
echo.
pause
start "" "dist\\CyberDefense\\CyberDefense.exe"
'''
        
        with open('test-exe.bat', 'w') as f:
            f.write(test_script)
            
        print("📝 Created test-exe.bat for testing")

        try:
            portable_dir = Path("dist/CyberDefense")
            portable_dir.mkdir(parents=True, exist_ok=True)

            launcher_path = portable_dir / "Run Cyber Defense.bat"
            launcher_content = """@echo off
setlocal
cd /d "%~dp0"
start "" "CyberDefense.exe"
endlocal
"""
            launcher_path.write_text(launcher_content, encoding="utf-8")

            readme_path = portable_dir / "README-FIRST.txt"
            readme_content = """Real-World Cyber Defense (Windows)

How to run:
1) Double-click: Run Cyber Defense.bat

If Windows SmartScreen shows a warning:
- Click: More info
- Click: Run anyway

If your antivirus blocks it:
- This can be a false positive for new unsigned apps.
- Add an exception for this folder or contact your AV vendor.
"""
            readme_path.write_text(readme_content, encoding="utf-8")
        except Exception:
            pass
        
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
    build_safe_windows_exe()
