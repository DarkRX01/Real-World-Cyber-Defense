# 🆘 Troubleshooting – Cyber Defense Desktop App

**Something not working? This guide will help you fix it.**

---

## ❌ App doesn't start

### Problem: Nothing happens when I double-click the EXE or .bat

**Solution:**
1. **Extract the entire ZIP** – Don't move only `CyberDefense.exe`. The app needs all files in the same folder.
2. **Run from the correct folder** – Use `Run Cyber Defense.bat` or `CyberDefense.exe` from the extracted folder.
3. **Check antivirus** – Some AVs quarantine unsigned executables. Add an exception for the CyberDefense folder, or **build from source** (safest).

---

## ❌ SmartScreen or Defender warning

### Problem: Windows says "Windows protected your PC" or "Unrecognized app"

**We do not recommend bypassing SmartScreen** (e.g. "More info" → "Run anyway"). That trains users to ignore security prompts.

**Safer options:**
1. **Build from source** – Clone the repo, run `python app_main.py`. You run code you can verify. See [README.md](README.md#-build-from-source).
2. **Wait for signed builds** – When we have code signing, releases will not trigger SmartScreen.
3. **Verify before running** – Check SHA256 checksums and VirusTotal links on the release page. See [SMARTSCREEN-WARNING.md](SMARTSCREEN-WARNING.md).

---

## ❌ Antivirus blocks the app

### Problem: My AV quarantines or blocks CyberDefense.exe

**Solution:**
- **Common for unsigned apps.** Add an exception for the CyberDefense folder only if you trust the source.
- **Best option:** Build from source. No binary from the internet.
- See [ANTIVIRUS-FIXES.md](ANTIVIRUS-FIXES.md) if it exists.

---

## ❌ "Where's the window?"

### Problem: I ran the app but don't see anything

**Solution:**
- The app **starts in the system tray** (near the clock). Look for the shield icon.
- **Double-click the tray icon** to open the main window.
- Or right-click the tray icon → **Show** / **Open**.

---

## ❌ Settings not saving

### Problem: My settings disappear after I close the app

**Solution:**
1. Make sure you click **Save** or **Apply** in Settings.
2. Check that `%APPDATA%\.cyber-defense\` is writable (no permission issues).
3. Run as normal user (not "Run as administrator" unless needed).

---

## ❌ No threats detected / scanning not working

### Problem: I expect a detection but nothing shows

**Solution:**
1. **Check Settings** – Real-time file monitoring, clipboard monitoring, and behavioral monitoring must be enabled.
2. **Monitored folders** – Default: Downloads, Desktop, Temp. Add more in Settings if needed.
3. **Sensitivity** – Try Medium or High. Low may miss some threats.
4. **Update definitions** – YARA/ClamAV/URLhaus update every 2 hours. Force update from Settings if available.

---

## ❌ VPN / WireGuard issues

### Problem: VPN won't connect or kill-switch doesn't work

**Solution:**
1. **WireGuard config** – Ensure you have a valid `.conf` file and selected it in Settings.
2. **Permissions** – WireGuard may need elevated rights on some systems.
3. **Kill-switch** – Currently alerts when VPN drops; full WFP-based kill-switch is planned. See [ROADMAP.md](ROADMAP.md).

---

## ❌ Logs and debugging

### Problem: I need to see what's happening

**Log location (Windows):**
```
%APPDATA%\.cyber-defense\logs\
```

**From source:**
- Run `python app_main.py` and check console output.
- Enable debug logging in Settings if available.

---

## ❌ Uninstalling

### Problem: How do I remove Cyber Defense?

**Solution:**
1. **Close the app** – Right-click tray icon → Exit.
2. **Delete the folder** – Remove the extracted CyberDefense folder.
3. **Optional:** Run `uninstall.bat` or `uninstall.py` if provided in the release.
4. **Clean config:** Delete `%APPDATA%\.cyber-defense\` if you want to remove all settings and logs.

---

## ✅ Still having problems?

1. **Check docs:** [README.md](README.md), [USER-GUIDE.md](USER-GUIDE.md), [THREAT-MODEL.md](THREAT-MODEL.md), [LIMITATIONS.md](LIMITATIONS.md)
2. **Open an issue:** [GitHub Issues](https://github.com/DarkRX01/Real-World-Cyber-Defense/issues)
3. **Describe your problem** – Include OS, version, what you tried, and any error messages.

---

*Cyber Defense Support* 🛡️
