# Cyber Defense – Project Checklist

A complete checklist of everything in this project. Use for releases, audits, or onboarding.

---

## Core Application

- [ ] **app_main.py** – Main GUI (PyQt5), dashboard, tabs, tray, settings
- [ ] **threat_engine.py** – URL/phishing/tracker detection, file scanning, hashes, entropy, YARA/PE heuristics
- [ ] **background_service.py** – Clipboard monitoring, URL scanning in background
- [ ] **realtime_monitor.py** – Watchdog-based file monitoring (Downloads, Temp, user dirs)
- [ ] **quarantine.py** – Move threats to quarantine, restore, secure delete
- [ ] **update_system.py** – ClamAV, URLhaus, PhishTank, YARA updates (2h interval)

---

## Detection Modules

- [ ] **detection/yara_engine.py** – YARA rule scanning
- [ ] **detection/behavioral.py** – Process monitoring, suspicious cmdlines, CPU spike detection
- [ ] **detection/ml_detector.py** – ML classifier (scikit-learn), PE features, entropy
- [ ] **detection/heuristic_pe.py** – PE packed EXE detection (pefile, entropy)
- [ ] **signature_updater.py** – YARA from GitHub, ClamAV daily/main fetch

---

## Protection Features

- [ ] **ransomware_shield.py** – Honeypot files, mass-change detector
- [ ] **anomaly_detector.py** – Simple baseline, event-rate anomaly
- [ ] **vpn_client.py** – WireGuard connect/disconnect, kill-switch

---

## Build & Packaging

- [ ] **build-safe-exe.py** – PyInstaller build (antivirus-friendly)
- [ ] **build-windows-exe.bat** – Windows build script
- [ ] **package-for-release.py** – Create release ZIP
- [ ] **version_info.txt** – Windows EXE version metadata
- [ ] **releases/CyberDefense-Windows-Portable.zip** – Windows portable release

---

## Packaging (Advanced)

- [ ] **packaging/build-msi.ps1** – WiX MSI installer
- [ ] **packaging/build-appimage.sh** – Linux AppImage
- [ ] **packaging/build-dmg.sh** – macOS DMG
- [ ] **packaging/wix/CyberDefense.wxs** – WiX installer config
- [ ] **cyber-defense-installer.nsi** – NSIS installer
- [ ] **minifilter-rust/** – Rust minifilter stub (future kernel-level)

---

## Tests

- [ ] **tests/test_threat_engine.py** – Threat engine unit tests
- [ ] **tests/test_background_service.py** – Background service tests
- [ ] **tests/conftest.py** – Pytest fixtures

---

## CI/CD

- [ ] **.github/workflows/test.yml** – Tests + optional build smoke-check
- [ ] **.github/workflows/linux-build.yml** – Linux build
- [ ] **.github/workflows/windows-build.yml** – Windows build
- [ ] **.github/ISSUE_TEMPLATE/** – Bug, feature, question templates
- [ ] **.github/PULL_REQUEST_TEMPLATE/** – PR template

---

## Documentation

- [ ] **README.md** – Main readme, features, download, build
- [ ] **USER-GUIDE.md** – User guide
- [ ] **CHANGELOG.md** – Version history
- [ ] **CORE-DETECTION-OVERHAUL.md** – Core detection + VPN summary
- [ ] **PRODUCTION-IMPROVEMENTS.md** – Production-grade improvements
- [ ] **SECURITY-ROADMAP.md** – Future security roadmap
- [ ] **SIGNING-SELF-DEFENSE.md** – Code signing, EV cert
- [ ] **RELEASE-UPLOAD.md** – How to upload to GitHub Releases
- [ ] **GITHUB-UPDATE.md** – Git push, commit, release steps
- [ ] **TROUBLESHOOTING.md** – Common issues
- [ ] **GETTING_STARTED_DESKTOP.md** – Getting started
- [ ] **CONTRIBUTING.md** – Contribution guidelines
- [ ] **ARCHITECTURE.md** – Architecture overview
- [ ] **TESTING_GUIDE.md** – Testing guide

---

## Features (User-Facing)

- [ ] URL & phishing detection
- [ ] Tracker blocking (25+ domains)
- [ ] Clipboard monitoring
- [ ] Real-time file monitoring (Downloads, Desktop, Temp, user dirs)
- [ ] File hashing (SHA256)
- [ ] YARA rule scanning
- [ ] PE heuristics (packed EXE)
- [ ] Behavioral monitoring (suspicious processes, CPU spikes)
- [ ] Ransomware honeypots
- [ ] Mass-change detection
- [ ] Anomaly detection (event rate)
- [ ] Quarantine (move, restore, delete)
- [ ] Auto-updates (YARA, ClamAV, URLhaus, PhishTank)
- [ ] VPN (WireGuard connect/disconnect, kill-switch)
- [ ] System tray (minimize, pause, VPN, settings)
- [ ] Dark UI (dashboard, threats, tools, settings)
- [ ] Threat log (persistent, export)
- [ ] System security check (firewall, Defender)

---

## Dependencies

- [ ] **requirements.txt** – PyQt5, requests, pyperclip, psutil, watchdog
- [ ] **requirements-detection.txt** – yara-python, pefile, scikit-learn, pywin32
- [ ] **requirements-dev.txt** – pytest-cov, dev tools
- [ ] **pyproject.toml** – Project config, pytest

---

## Icons & Assets

- [ ] **icons/shield.svg** – Shield icon
- [ ] **icons/icon.ico** – Windows icon (if generated)
- [ ] **icons/generate-ico.py** – Icon generator

---

## Install Scripts

- [ ] **install-windows.bat** – Windows install
- [ ] **install-windows-silent.bat** – Silent Windows install
- [ ] **install-linux.sh** – Linux install
- [ ] **install.ps1** – PowerShell install
- [ ] **setup.bat** – Setup script

---

## Release Checklist (before publishing)

- [ ] `pytest tests/` passes
- [ ] `python build-safe-exe.py` succeeds
- [ ] `releases/CyberDefense-Windows-Portable.zip` created
- [ ] CHANGELOG [X.X.X] section updated
- [ ] README version badge updated
- [ ] Git tag created (e.g. v2.2.0)
- [ ] GitHub Release created with ZIP attached
