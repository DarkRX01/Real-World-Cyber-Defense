# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['PyQt5', 'threat_engine', 'background_service', 'notification_manager', 'vpn_client', 'ransomware_shield', 'realtime_monitor', 'network_monitor', 'registry_monitor', 'process_injection_detector', 'rootkit_detector', 'advanced_ransomware_detector', 'advanced_behavioral_analysis', 'threat_detection_orchestrator']
tmp_ret = collect_all('yara')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\yamen.alkhoula.stude\\Documents\\Blue teaming\\cyber-defense-extension\\app_main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CyberDefense',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
