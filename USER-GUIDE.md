# Cyber Defense – User Guide

Short guide for using the **portable EXE** or the app from source.

---

## Running the app (Windows portable)

1. **Download** the latest `CyberDefense-Windows-Portable.zip` from [Releases](https://github.com/DarkRX01/Real-World-Cyber-Defense/releases).
2. **Extract** the entire ZIP to a folder (e.g. `Desktop\CyberDefense`). Do not move only the EXE.
3. **Run** by double-clicking:
   - **Run Cyber Defense.bat** (recommended), or  
   - **CyberDefense.exe**
4. The app starts in the **system tray** (icon near the clock). There is no window at first.
5. **Double-click the tray icon** to open the main window.

See **README-FIRST.txt** in the extracted folder for first-run tips and what to do if Windows or your antivirus blocks the app.

---

## Main window

- **Dashboard** – Overview and recent activity. Copy URLs to trigger automatic scanning (if clipboard monitoring is on).
- **Threats** – Full list of detected threats. You can clear the log.
- **Tools** – **URL Scanner** (paste a link, click Scan URL) and **System Security Check** (firewall / Defender status).
- **Settings** – Sensitivity, clipboard monitoring, notifications, start minimized, real-time file monitoring, auto-updates. Click **Save settings** to apply.

Use the **tray icon**: right-click for **Show**, **Pause**, **Settings**, **Exit**. Double-click to open the window.

---

## Recommended settings (first time)

- **Sensitivity:** Medium  
- **Start minimized to tray:** On (so the app doesn’t open a window on every startup)  
- **Show notifications for threats:** On  
- **Auto-update definitions every 2 hours:** On  

Save after changing.

---

## If something goes wrong

- **App doesn’t start** – Extract the full ZIP and run from that folder. Don’t run only the EXE from another location.
- **SmartScreen warning** – Choose “More info” → “Run anyway”.
- **Antivirus blocks it** – Add an exception for the app folder or build from source (see README).
- **Logs** – Windows: `%APPDATA%\.cyber-defense\logs\`  
- More: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) and [GETTING_STARTED_DESKTOP.md](GETTING_STARTED_DESKTOP.md).

---

**Repository:** [GitHub – Real-World-Cyber-Defense](https://github.com/DarkRX01/Real-World-Cyber-Defense)
