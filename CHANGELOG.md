# Changelog

All notable changes to the Real-World Cyber Defense project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_No additional changes yet._

## [2.2.0] - 2026-02-04

### Added
- **GUI:** Version (v2.2.0) in window title and header; 4th stat card “Protection” (ON/PAUSED); Dashboard “Quick actions” with “Open Tools → Scan URL”; Threat tab “Threat history” header; cleaner Dashboard/Threats styling.
- **Core Detection Overhaul:** Real-time FS (Downloads, Desktop, Temp, user dirs), EICAR + hashlib hashes, YARA from GitHub, PE heuristics, ransomware honeypots, behavioral CPU spike detection, anomaly detector (see CORE-DETECTION-OVERHAUL.md).
- **VPN:** WireGuard connect/disconnect from tray; kill-switch alert when VPN drops; Settings: VPN config path and kill-switch.

### Changed
- Window size default 1020×720; minimum 920×680.
- Build and version_info: 2.2.0; ProductVersion/FileVersion 2.2.0.0.
- Release ZIP: `releases/CyberDefense-Windows-Portable.zip` (contains full CyberDefense folder for GitHub Releases).

## [2.1.0] - 2026-02-04

### Added

**Detection**
- **YARA engine** (`detection/yara_engine.py`) – File scanning with YARA; use rules from MalwareBazaar in `yara_rules/`. Wired into comprehensive file scan when `yara-python` and rules are present.
- **Static ML detector** (`detection/ml_detector.py`) – scikit-learn on entropy, file size, PE sections (optional `pefile`). Heuristic fallback when no model is trained.
- **Behavioral monitor** (`detection/behavioral.py`) – Process creation monitoring (psutil); flags suspicious LOLBins (e.g. encoded PowerShell). Optional in Settings: “Behavioral monitoring”.
- **EICAR detection** – Standard AV test string detection in `scan_file_eicar()` and `scan_file_comprehensive()`; `is_eicar_bytes()` for in-memory checks.

**Real-time & updates**
- **Event-driven file monitor** (`realtime_monitor.py`) – Watchdog-based; no polling. Watches Downloads/Desktop (optional in Settings). Scans new files immediately; optional quarantine.
- **Update system** (`update_system.py`) – Pull ClamAV, URLhaus, PhishTank every 2 hours over HTTPS. Optional in Settings: “Auto-update threat definitions”.
- **Quarantine** (`quarantine.py`) – Move threats to quarantine folder with metadata; restore and secure-delete support.

**UX & packaging**
- **Tray-first** – Start minimized to tray by default; double-click tray to open window. Tooltips on all main controls and settings.
- **User-friendly EXE** – Build produces `Run Cyber Defense.bat` and **README-FIRST.txt** in the release folder (how to run, first-time tips, SmartScreen/AV notes).
- **USER-GUIDE.md** – Short user guide for portable EXE and recommended settings.
- **README.md** – Rewritten for users: quick download/run, features table, docs links, troubleshooting table.

**CI & quality**
- **CI** (`.github/workflows/test.yml`) – EICAR tests (bytes + file when not blocked by AV), threat engine tests, coverage; **build-and-scan** job (build exe, verify EICAR); Linux tests.
- **Packaging** – WiX MSI (`packaging/wix/`, `build-msi.ps1`), AppImage and DMG scripts (`packaging/`).

**Docs & GitHub**
- **SIGNING-SELF-DEFENSE.md** – EV cert, signtool, SmartScreen, NSSM/systemd.
- **PRODUCTION-IMPROVEMENTS.md** – Summary of all production-grade additions.
- **Minifilter scaffold** (`minifilter-rust/`) – Rust stub and README for a future Windows minifilter.
- **GitHub** – Issue templates (bug, feature, question) and PR template updated for the desktop app.

### Changed
- Dashboard placeholder text explains copy-URL-to-scan and Tools → Scan URL.
- Settings: added “Start minimized to tray”, “Real-time file monitoring”, “Auto-update definitions”, “Behavioral monitoring”; all with tooltips.
- Tray tooltip: “Double-click to open, right-click for menu”.
- Comprehensive file scan optionally runs YARA when available.

## [2.0.0] - 2026-01-29

### Added
- **Desktop Application** - Full PyQt5 GUI application for Windows and Linux
- **Real-time URL Scanning** - Automatic detection of malicious URLs
- **Phishing Detection** - Machine learning-powered phishing analysis
  - Lookalike domain detection (paypa1.com, amaz0n.com, etc.)
  - Suspicious TLD flagging (.xyz, .tk, etc.)
  - IP-based URL detection
  - Keyword-based urgency detection
- **Tracker Blocking** - Blocks 25+ known tracking domains
  - Google Analytics
  - Facebook Pixel
  - Hotjar
  - Mixpanel
  - And many more
- **Download Protection** - Scans files for dangerous extensions
  - Executable detection (.exe, .dll, .scr, etc.)
  - Script detection (.bat, .ps1, .vbs, etc.)
  - Large file warnings
- **System Security Checks** - Windows security status verification
  - Firewall status check
  - Windows Defender status check
  - Security recommendations
- **Clipboard Monitoring** - Automatic scanning of copied URLs
- **System Tray Integration** - Background monitoring with tray icon
- **Customizable Settings**
  - 4 sensitivity levels (Low, Medium, High, Extreme)
  - Feature toggles for each protection type
  - Notification preferences
- **Threat Logging** - Persistent threat history with export
- **Cross-Platform Support** - Windows 10/11 and major Linux distributions

### Technical
- Python 3.9+ support
- PyQt5-based modern GUI
- Background service architecture
- Local-only processing (no cloud dependencies)
- MIT License

## [1.0.0] - 2025-06-15

### Added
- Initial release as desktop security application
- Basic URL scanning functionality
- Simple phishing detection
- Tracker blocking (basic list)
- Windows support

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 2.1.0 | 2026-02-04 | YARA/ML/behavioral detection, real-time monitor, quarantine, updates, tray-first UX, README & GitHub |
| 2.0.0 | 2026-01-29 | Full desktop app, cross-platform, advanced detection |
| 1.0.0 | 2025-06-15 | Initial release |

---

## Upgrade Notes

### From 1.x to 2.0

Version 2.0 is a complete rewrite with a new GUI framework. To upgrade:

1. Uninstall the old version (if applicable)
2. Download the new release from GitHub
3. Run the installer or extract the portable version
4. Your settings will need to be reconfigured

### Fresh Install

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

---

## Security Advisories

No security vulnerabilities have been reported for this project.

If you discover a security issue, please report it privately via the process described in [SECURITY.md](SECURITY.md).

---

[Unreleased]: https://github.com/DarkRX01/Real-World-Cyber-Defense/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/DarkRX01/Real-World-Cyber-Defense/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/DarkRX01/Real-World-Cyber-Defense/releases/tag/v1.0.0
