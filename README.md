# 🛡️ Cyber Defense – Real-World Security

A **user-friendly** desktop app for threat detection and security monitoring on Windows (and Linux from source). Protects you from phishing, trackers, and suspicious downloads with a simple tray icon and clear notifications.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
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

**Settings:** Sensitivity (Medium recommended), clipboard monitoring, notifications, “Start minimized to tray”, real-time file monitoring (Downloads/Desktop), and auto-update of threat definitions every 2 hours.

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔗 **URL & phishing detection** | Scans URLs and clipboard links for phishing and suspicious patterns. |
| 🚨 **Tracker blocking** | Detects known tracking/analytics domains. |
| 📋 **Clipboard monitoring** | Optional; scans URLs when you copy them. |
| 📁 **Real-time file monitoring** | Optional; watches Downloads/Desktop and scans new files. |
| 🔄 **Auto-updates** | Optional; updates blocklists (ClamAV, URLhaus, PhishTank) every 2 hours. |
| 🗂 **Quarantine** | Detected file threats can be moved to quarantine (restore later). |
| 🌙 **Tray-first** | Runs in the tray; Win10-style notifications; window only when you open it. |
| 🎨 **Dark UI** | Simple dashboard, threat log, tools, and settings. |

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [USER-GUIDE.md](USER-GUIDE.md) | Short user guide: running the EXE, main window, recommended settings. |
| **README-FIRST.txt** | In the release ZIP – how to run and what to do if Windows/AV blocks. |
| [GETTING_STARTED_DESKTOP.md](GETTING_STARTED_DESKTOP.md) | Full getting started and first-time setup. |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and fixes. |
| [PRODUCTION-IMPROVEMENTS.md](PRODUCTION-IMPROVEMENTS.md) | Technical improvements (YARA, ML, real-time, quarantine, etc.). |
| [SIGNING-SELF-DEFENSE.md](SIGNING-SELF-DEFENSE.md) | Code signing and running as a service. |

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

## ⚠️ Disclaimer

This is **educational / light security** software, not a full replacement for Windows Defender or a commercial antivirus.

- ✅ Good for: phishing/tracker awareness, URL checks, learning, extra layer.
- ❌ Not: kernel-level protection, certified antivirus, or guaranteed zero-day protection.

**For strong security:** Use Windows Defender (or your AV), keep the system updated, and use backups. See [SECURITY-ROADMAP.md](SECURITY-ROADMAP.md) for limitations and [PRODUCTION-IMPROVEMENTS.md](PRODUCTION-IMPROVEMENTS.md) for what’s implemented.

---

## 🐛 Troubleshooting

| Issue | What to try |
|-------|-------------|
| App doesn’t start | Extract the **entire** ZIP; run **Run Cyber Defense.bat** or **CyberDefense.exe** from that folder. |
| SmartScreen warning | Click “More info” → “Run anyway”. |
| Antivirus blocks it | Common for unsigned apps. Add an exception for the app folder or build from source. |
| “Where’s the window?” | App starts in the tray. **Double-click the tray icon** to open the window. |
| Logs | `%APPDATA%\.cyber-defense\logs\` (Windows). |

---

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
