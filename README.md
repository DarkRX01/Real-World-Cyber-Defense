# 🛡️ Cyber Defense – Real-World Security

**Desktop real-time threat scanner & privacy shield (Windows/Linux).** A user-friendly desktop app for threat detection and security monitoring. Protects you from phishing, trackers, and suspicious downloads with a simple tray icon and clear notifications.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Why use it?

- **Easy to run** – Download the ZIP, double-click **Run Cyber Defense.bat** or **CyberDefense.exe**. No installer required.
- **Stays out of your way** – Runs in the system tray by default; double-click the tray icon to open the window.
- **Clear and simple** – Dashboard, threat log, URL scanner, and settings in one place. Tooltips explain every option.
- **Privacy-first** – All scanning runs on your PC. No cloud, no data collection.

---

## 📥 Download & run (easiest)

### Windows – portable (no install)

1. Go to [Releases](https://github.com/DarkRX01/Real-World-Cyber-Defense/releases).
2. Download **`CyberDefense-Windows-Portable.zip`** (or the latest Windows build).
3. **Extract the whole ZIP** to a folder (e.g. `Desktop\CyberDefense`).
4. Double-click **`Run Cyber Defense.bat`** or **`CyberDefense.exe`**.

**First run:** The app starts in the tray (icon near the clock). **Double-click the tray icon** to open the window. See **README-FIRST.txt** in the folder for more.

> ⚠️ **Keep all files together** – Don’t move only the `.exe`. The app needs the other files in the same folder.

---

## 🚀 Quick start

| Step | What to do |
|------|------------|
| 1 | Run the app (tray icon appears). |
| 2 | Double-click tray icon → open main window. |
| 3 | Copy any URL – we scan it automatically when clipboard monitoring is on. |
| 4 | Or go to **Tools → URL Scanner**, paste a link, click **Scan URL**. |
| 5 | Check **Threats** tab for the log; **Settings** to turn features on/off. |

**Settings:** Sensitivity (Medium recommended), clipboard monitoring, notifications, “Start minimized to tray”, real-time file monitoring (Downloads/Desktop/Temp), behavioral monitoring, VPN (WireGuard config + kill-switch), and auto-update of threat definitions every 2 hours.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔗 **URL & phishing detection** | Scans URLs and clipboard links for phishing and suspicious patterns. |
| 🚨 **Tracker blocking** | Detects known tracking/analytics domains. |
| 📋 **Clipboard monitoring** | Optional; scans URLs when you copy them. |
| 📁 **Real-time file monitoring** | Optional; watches Downloads, Desktop, **Temp**, and user dirs 24/7. Hashes + YARA + PE heuristics + entropy heuristics. |
| 🛡 **Ransomware shield** | Honeypot files in key dirs; mass-encryption detection. |
| 🔄 **Auto-updates** | Optional; YARA from GitHub + ClamAV, URLhaus, PhishTank every 2 hours. |
| 🗂 **Quarantine** | Detected file threats can be moved to quarantine (restore later). |
| 🔒 **VPN & DNS** | AdGuard DNS (no config), WireGuard config picker, connect/disconnect from tray; kill-switch when VPN drops. |
| 🌙 **Tray-first** | Runs in the tray; Win10-style notifications; VPN Connect/Disconnect in menu. |
| 🎨 **Dark UI** | Simple dashboard, threat log, tools, and settings. |

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [USER-GUIDE.md](USER-GUIDE.md) | Short user guide: running the EXE, main window, recommended settings. |
| **README-FIRST.txt** | In the release ZIP – how to run and what to do if Windows/AV blocks. |
| [GETTING_STARTED_DESKTOP.md](GETTING_STARTED_DESKTOP.md) | Full getting started and first-time setup. |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and fixes. |
| [CORE-DETECTION-OVERHAUL.md](CORE-DETECTION-OVERHAUL.md) | Core detection: real-time FS, signatures, PE heuristics, ransomware shield, VPN. |
| [PRODUCTION-IMPROVEMENTS.md](PRODUCTION-IMPROVEMENTS.md) | Technical improvements (YARA, ML, real-time, quarantine, etc.). |
| [SIGNING-SELF-DEFENSE.md](SIGNING-SELF-DEFENSE.md) | Code signing and running as a service. |
| [ROADMAP.md](ROADMAP.md) | Prioritized roadmap: trust & safety, features, usability, community. |
| [THREAT-MODEL.md](THREAT-MODEL.md) | What we can and cannot detect; confidence levels. |
| [LIMITATIONS.md](LIMITATIONS.md) | Short summary of limitations; link to full threat model. |
| [INSTALLER-GUIDE.md](INSTALLER-GUIDE.md) | Installation options: portable ZIP, from source. |
| [ANTIVIRUS-FIXES.md](ANTIVIRUS-FIXES.md) | False positives, VirusTotal, vendor reporting. |
| [LAUNCH-CHECKLIST.md](LAUNCH-CHECKLIST.md) | Pre-release and launch checklist. |

---

## 🛠 Build from source

```bash
git clone https://github.com/DarkRX01/Real-World-Cyber-Defense.git
cd Real-World-Cyber-Defense/cyber-defense-extension

pip install -r requirements.txt

# Run directly
python app_main.py

# Build Windows EXE (output in dist/CyberDefense/)
python build-safe-exe.py
```

The built folder will include **Run Cyber Defense.bat** and **README-FIRST.txt** for end users.

---

## 🛡️ How it helps you

Cyber Defense is built to be **actually useful** as an extra layer of protection:

- **Real-time file monitoring** – Watches Downloads, Desktop, Temp, and user dirs 24/7; scans new files instantly (hashes, YARA, PE heuristics). Ransomware honeypots in key dirs.
- **URL & clipboard** – Catches phishing and suspicious links before you open them.
- **Behavioral monitoring** – Flags suspicious process behavior and anomalous CPU spikes (e.g. mining/encryption).
- **YARA + PE heuristics** – Auto-updating YARA rules from GitHub; packed-EXE and entropy-based detection.
- **Quarantine** – Moves threats to a safe folder instead of deleting; you can restore or remove later.
- **Auto-updating blocklists** – Pulls YARA (GitHub), ClamAV, URLhaus, PhishTank so definitions stay current.
- **VPN** – Optional WireGuard connect/disconnect from tray; kill-switch alerts when VPN drops (local-only; no telemetry).

**Best setup:** Run Cyber Defense **together with** Windows Defender (or your main AV). Defender handles certified antivirus + kernel-level protection; Cyber Defense adds real-time file/URL/behavior monitoring and quarantine from the application layer. See [PRODUCTION-IMPROVEMENTS.md](PRODUCTION-IMPROVEMENTS.md) for what's under the hood and [THREAT-MODEL.md](THREAT-MODEL.md) for honest limitations.

---

## 🐛 Troubleshooting

| Issue | What to try |
|-------|-------------|
| App doesn’t start | Extract the **entire** ZIP; run **Run Cyber Defense.bat** or **CyberDefense.exe** from that folder. |
| SmartScreen warning | We do **not** recommend bypassing SmartScreen. Prefer **building from source** or use a signed build when available. See [SMARTSCREEN-WARNING.md](SMARTSCREEN-WARNING.md). |
| Antivirus blocks it | Common for unsigned builds. Add an exception only if you trust the source, or **build from source**. |
| “Where’s the window?” | App starts in the tray. **Double-click the tray icon** to open the window. |
| Verify downloads | Use **SHA256 checksums** and **VirusTotal** links on the release page (goal: 0 detections). See [REPRODUCIBLE-BUILDS.md](REPRODUCIBLE-BUILDS.md). |
| Logs | `%APPDATA%\.cyber-defense\logs\` (Windows). |

## 📋 Requirements

- **Windows:** 10 or later (or run from source on Linux).
- **Portable build:** No install; ~150 MB disk, runs from the folder.
- **From source:** Python 3.9+ and dependencies in `requirements.txt`.

---

## 🤝 Contributing & support

- **Issues and ideas:** [GitHub Issues](https://github.com/DarkRX01/Real-World-Cyber-Defense/issues)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Security:** [SECURITY.md](SECURITY.md)

---

## 📜 License

MIT License – see [LICENSE](LICENSE).

---

**Made for easier, more transparent security on your PC.**  
If this project helps you, consider giving it a ⭐ on GitHub.
