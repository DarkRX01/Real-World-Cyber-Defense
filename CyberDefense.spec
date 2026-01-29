# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None
current_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['app_main.py', 'threat_engine.py', 'background_service.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'pyperclip'],
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
    icon='icons/icon.ico' if os.path.exists('icons/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CyberDefense',
)
