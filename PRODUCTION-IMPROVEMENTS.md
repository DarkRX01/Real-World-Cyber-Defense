# Production Improvements Implemented

This document summarizes the fixes and additions made to address the production-grade security critique.

## 1. Detection (beyond hashes/regex)

- **YARA** (`detection/yara_engine.py`): Scan files with YARA; use rules from MalwareBazaar (place `.yar` files in `yara_rules/`). Optional dependency: `pip install yara-python`.
- **Static ML** (`detection/ml_detector.py`): scikit-learn on entropy, file size, PE sections (via `pefile`). Heuristic fallback if no trained model; optional `data/ml_model.pkl` for a real classifier. Install: `pip install -r requirements-detection.txt`.
- **Behavioral** (`detection/behavioral.py`): Process creation monitoring with psutil; flags suspicious LOLBins (PowerShell `-EncodedCommand`, `DownloadString`, etc.). Optional pywin32 on Windows.

## 2. Real-time (event-driven)

- **`realtime_monitor.py`**: Event-driven file monitoring via **watchdog** (inotify on Linux, ReadDirectoryChangesW-style on Windows). On file create/modify in watched dirs (e.g. Downloads, Desktop), runs a scan immediately; on threat, calls `on_threat` and optionally quarantines.
- **App**: Settings “Real-time file monitoring” and “Auto-update definitions every 2 hours”; background service uses the above (no 5‑minute polling for file events).

## 3. Quarantine (no blind delete)

- **`quarantine.py`**: Move/copy threats to `%PROGRAMDATA%\.cyber-defense\quarantine` (or `~/.cyber-defense/quarantine` on Linux) with metadata (original path, threat type, time, SHA256 prefix). Restore via `restore_from_quarantine()`; optional secure wipe in `delete_from_quarantine(..., secure=True)`. VSS shadow copy is documented for rollback (requires admin).

## 4. Update system

- **`update_system.py`**: Every 2 hours (configurable): pull **ClamAV** (main/daily CVD), **URLhaus** blocklist, **PhishTank** public feed over HTTPS. Stores under `data/` with SHA256 for URLhaus. Start/stop via `UpdateScheduler`; used by the app when “Auto-update definitions” is enabled.

## 5. Tray-first UI

- **Start minimized**: Setting “Start minimized to tray (no window popup)” (default ON). No main window on startup; only tray icon and Win10-style notifications for critical threats.
- **Settings**: “Real-time file monitoring”, “Auto-update definitions every 2 hours” added in Settings tab.

## 6. CI (tests + build smoke-check)

- **`.github/workflows/test.yml`**:
  - Run threat engine tests and full test suite with coverage.
  - Optional build smoke-check job on Windows.
  - Linux job: same tests on Ubuntu.

## 7. Packaging

- **MSI (WiX)**: `packaging/wix/CyberDefense.wxs` and `packaging/build-msi.ps1`. Install WiX Toolset and run the script from repo root.
- **AppImage**: `packaging/build-appimage.sh` (stub; add linuxdeploy step).
- **DMG**: `packaging/build-dmg.sh` (stub for macOS).

## 8. Signing & self-defense

- **`SIGNING-SELF-DEFENSE.md`**: EV code signing (~$80–300/year), `signtool` usage, SmartScreen submission; NSSM (Windows) and systemd (Linux) for running as a service so malware can’t easily kill the process.

## 9. Kernel/driver (scaffold only)

- **`minifilter-rust/`**: Rust crate stub for a Windows minifilter. Real implementation requires WDK, wdk-rs, kernel build, and EV signing. See `minifilter-rust/README.md`.

## Optional dependencies

- **Full detection stack**: `pip install -r requirements-detection.txt` (yara-python, pefile, scikit-learn, pywin32 on Windows).
- **Watchdog** is already in `requirements.txt` for real-time file monitoring.

## Notes

- **Malware samples in CI**: Do not ship or scan real malware samples in CI. Keep CI focused on unit/integration tests and safe fixtures.
- **EV cert**: Until you have an EV cert and sign builds, Defender/SmartScreen may still flag the app; document exclusions and see `ANTIVIRUS-FIXES.md` and `SIGNING-SELF-DEFENSE.md`.
