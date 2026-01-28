# 🛡️ Real-World Cyber Defense - Desktop Application

**The ultimate security tool for your PC and Linux**

Transform your computer into a fortress against digital threats. Cyber Defense is a lightweight, powerful desktop application that monitors threats in real-time, blocks phishing attacks, eliminates trackers, and protects your downloads.

---

## ✨ What's New: Desktop Edition

We've completely redesigned Cyber Defense from a Chrome extension into a **standalone desktop application**:

- 🖥️ **No Browser Dependency** - Works independently on Windows and Linux
- ⚡ **Lightweight & Fast** - Minimal resource usage, instant launch
- 🎯 **Always Protected** - Monitor threats whether your browser is open or not
- 🔌 **System-Wide** - Protects your entire computer, not just web browsing
- 🎨 **Beautiful Dashboard** - Intuitive GUI showing real-time threat status
- 📊 **Detailed Threat Log** - Track all security events
- 🔧 **Highly Customizable** - Enable/disable features as you like
- 🌳 **System Tray** - Minimize to tray, stay in background
- 🚀 **Auto-Start Option** - Run on boot automatically

---

## 🚀 Quick Start (Choose Your OS)

### ⚡ Windows (Easiest)

1. **Download & Run Installer:**
   ```bash
   download install-windows.bat
   double-click it
   ```

2. **Wait for installation** (auto-downloads Python + dependencies)

3. **Click "Cyber Defense" desktop shortcut**

4. **Done!** You're protected 🎉

**Installation takes 2-3 minutes** depending on internet speed.

---

### 🐧 Linux (Ubuntu/Debian/Fedora)

1. **Download installer:**
   ```bash
   wget https://github.com/DarkRX01/Real-World-Cyber-Defense/raw/main/install-linux.sh
   chmod +x install-linux.sh
   ```

2. **Run installer:**
   ```bash
   ./install-linux.sh
   ```

3. **Launch app:**
   ```bash
   cyber-defense
   # OR
   python3 -m cyber_defense.app_main
   ```

4. **Done!** You're protected 🎉

---

## 📋 System Requirements

| Requirement | Windows | Linux |
|-----------|---------|-------|
| **OS** | Windows 7+ | Ubuntu 18.04+ / Debian 9+ / Fedora 30+ / Arch |
| **RAM** | 512MB+ | 512MB+ |
| **Disk** | 500MB+ | 500MB+ |
| **Python** | 3.9+ (auto-installed) | 3.9+ (auto-installed) |
| **Browser** | Optional | Optional |

---

## 🛡️ Features

### 🔗 URL Scanning
- **Real-time analysis** of URLs you visit
- **Phishing detection** with AI-powered scoring
- **Homograph attack prevention** (prevents confusing lookalike domains)
- **Clipboard monitoring** - automatically scans URLs you copy
- **Suspicious pattern detection** - catches malicious URL tricks

**Example Protected Against:**
- `paypa1.com` (phishing PayPal) 
- `amaz0n.com` (phishing Amazon)
- `http://123.45.67.89/fake-login` (IP-based attacks)

### 🎣 Phishing Detection
- **Advanced scoring algorithm** (0-100% confidence)
- **Keyword analysis** - detects urgent/verify language
- **Domain reputation** - checks against known phishing domains
- **TLD analysis** - flags suspicious extensions (.xyz, .tk, etc.)
- **HTTPS verification** - warns about non-secure sites
- **Visual indicators** 🔴🟡🟢 for threat severity

### 🚫 Tracker Blocking
- **25+ known tracker domains** (Google Analytics, Facebook Pixel, etc.)
- **Auto-detection** of tracking URLs
- **Real-time notification** when trackers are blocked
- **Logging** of all blocked tracking attempts
- **Customizable** - enable/disable per tracker type

### 📥 Download Protection
- **File scanning** - analyzes downloaded files
- **Extension checking** - flags suspicious executables
- **File hash analysis** - matches against known malware
- **VirusTotal integration** (optional, with API key)
- **Size warnings** - alerts on unusually large files
- **Real-time monitoring** of Downloads folder

### 💻 System Security
- **Vulnerability detection** - finds weak system settings
- **Windows Defender status** - checks if enabled
- **Firewall monitoring** - ensures firewall is active
- **Permission checking** - detects insecure file permissions
- **Full system scan** - comprehensive security audit

### ⚙️ Customization
- **Threat Sensitivity:** Low 🟢 / Medium 🟡 / High 🔴 / Extreme ⚫
- **Feature Toggle:**
  - Enable/Disable phishing detection
  - Enable/Disable tracker blocking
  - Enable/Disable download scanning
  - Enable/Disable URL scanning
- **Background Service:** Optional background monitoring
- **Auto-Start:** Launch on system boot
- **Notifications:** Real-time security alerts
- **API Keys:** Optional (Google Safe Browsing, VirusTotal)

---

## 📊 Dashboard Explained

### Status Panel
```
🔒 Monitoring Active          ⏸️ Pause Monitoring
```
- **Green** = Active protection
- **Orange** = Paused
- **Red** = Error

### Statistics
```
🔴 Threats Detected: 42        🚫 Trackers Blocked: 156        🎣 Phishing Blocked: 8
```
- Real-time counters
- Resets on app restart (stored in logs)
- Click to see detailed threat log

### Tabs

1. **📊 Dashboard**
   - Status overview
   - Real-time statistics
   - Recent activity log
   - Quick action buttons

2. **🔴 Threats**
   - Detailed threat history
   - Threat type classification
   - Severity indicators
   - URLs/files affected
   - Time of detection

3. **🔧 Tools**
   - 🔗 URL Scanner - scan clipboard URL
   - 💻 System Scanner - full system scan
   - ⚠️ Vulnerability Checker - find weak points

---

## ⚙️ Settings & Customization

### How to Access Settings
1. Click **⚙️ Settings** button
2. Adjust any options
3. Click **💾 Save Settings**
4. Changes apply immediately

### Sensitivity Levels

| Level | What It Does | Use When |
|-------|------------|----------|
| 🟢 **Low** | Only blocks confirmed threats | You want minimal false positives |
| 🟡 **Medium** (Default) | Balanced detection | Normal browsing (recommended) |
| 🔴 **High** | Aggressive detection | Visiting risky sites |
| ⚫ **Extreme** | Maximum alerts | Security researcher mode |

### Feature Toggles

```
✅ Enable Phishing Detection       - Recommend: ON (default)
✅ Block Trackers                   - Recommend: ON (default)
✅ Scan Downloads                   - Recommend: ON (default)
✅ Scan URLs                        - Recommend: ON (default)
✅ Run in Background (System Tray) - Recommend: ON (optional)
✅ Auto-Start on Boot              - Recommend: OFF (set as needed)
✅ Enable Notifications            - Recommend: ON (default)
```

### Background Service

**What it does:**
- Continues monitoring even when app window is closed
- Shows icon in system tray
- Displays notifications for threats
- Can be paused/resumed from tray menu

**To enable:**
1. Open Settings
2. Check "Run in Background"
3. Save

**Access from tray:**
- Right-click system tray icon
- Select Show/Pause/Settings/Exit

---

## 🔧 Tools

### 🔗 URL Scanner
**Manually scan any URL:**
1. Copy URL to clipboard
2. Click **Tools** tab
3. Click **Scan URL from Clipboard**
4. Get instant threat analysis

**Output includes:**
- Phishing score (0-100%)
- Threat type (if detected)
- Specific indicators found
- Recommended action

### 💻 Full System Scan
**Comprehensive security audit:**
1. Click **Tools** tab
2. Click **Full System Scan**
3. Waits for scan to complete
4. Reports all threats found

**Scans:**
- Recently downloaded files
- Active processes
- System settings
- Installed applications

### ⚠️ Vulnerability Check
**Find security weaknesses:**
1. Click **Tools** tab
2. Click **Check for Vulnerabilities**
3. Get list of issues
4. Follow recommendations

**Checks:**
- Windows Defender status
- Firewall status
- File permissions
- System updates
- Password management

---

## 📝 Understanding Threat Types

### 🎣 Phishing
**What:** Fake website trying to steal credentials
**Indicators:**
- Urgent language ("act now", "verify account")
- Lookalike domains (`paypa1.com`)
- Missing HTTPS
- Suspicious subdomains

**What to do:** ❌ Don't click, close the tab

### 🚫 Tracker
**What:** Website tracking your behavior
**Indicators:**
- Analytics pixels
- Ad servers
- Data collection services

**What to do:** ✅ Already blocked, you're safe

### 📥 Suspicious File
**What:** Potentially harmful download
**Indicators:**
- Executable file (.exe, .dll, .scr)
- Suspicious size
- Unknown source

**What to do:** ❌ Delete the file, or scan with VirusTotal

### 🔗 Suspicious URL
**What:** URL with odd patterns
**Indicators:**
- IP address instead of domain
- Excessive encoding
- JavaScript protocol

**What to do:** ❌ Don't click, leave the site

### 🦠 Malware Detected
**What:** File matched malware database
**Indicators:**
- VirusTotal flagged file
- File hash in threat database

**What to do:** ❌ Delete immediately, run antivirus

---

## 🎨 Color Scheme

| Color | Meaning | Action |
|-------|---------|--------|
| 🟢 Green | Safe/Low threat | Continue normally |
| 🟡 Yellow | Warning/Medium threat | Be cautious |
| 🔴 Red | Danger/High threat | Take immediate action |
| ⚫ Black | Critical/Extreme threat | Stop and block |

---

## 🚀 Advanced Usage

### Using API Keys (Optional)

**Google Safe Browsing API:**
1. Go to https://console.developers.google.com
2. Create API key
3. Open Settings → Enter API key
4. Enhanced phishing detection

**VirusTotal API:**
1. Go to https://www.virustotal.com
2. Create free account
3. Get API key
4. Open Settings → Enter API key
5. File scans check global malware database

### Command Line Launch

```bash
# Windows
python -m cyber_defense.app_main

# Linux
python3 -m cyber_defense.app_main

# Run with specific settings
python3 -m cyber_defense.app_main --headless  # Background mode
```

### Accessing Logs

**Windows:**
```
C:\Users\[YourUsername]\.cyber-defense\logs\
```

**Linux:**
```
~/.cyber-defense/logs/
```

**View recent threats:**
```bash
cat ~/.cyber-defense/threat_log.json
```

### Uninstall

**Windows:**
1. Control Panel → Programs → Uninstall
2. Find "Cyber Defense"
3. Click Uninstall
4. Settings stored in `~\.cyber-defense\` (safe to delete)

**Linux:**
```bash
pip3 uninstall cyber-defense
rm -rf ~/.cyber-defense
rm ~/.local/share/applications/cyber-defense.desktop
sudo rm /usr/local/bin/cyber-defense
```

---

## ❓ FAQ

**Q: Will this slow down my computer?**
A: No! It uses <50MB RAM and minimal CPU. Lightweight by design.

**Q: Does it need internet?**
A: Optional. Basic phishing detection works offline. Enhanced features need internet.

**Q: What about privacy?**
A: 100% local. No data sent to servers. All logs stay on your computer.

**Q: Can it be customized?**
A: Yes! Settings, sensitivity levels, feature toggles - all customizable.

**Q: Does it work with antivirus software?**
A: Yes! Works alongside Windows Defender, Norton, McAfee, etc.

**Q: What if I find a bug?**
A: Report to: https://github.com/DarkRX01/Real-World-Cyber-Defense/issues

**Q: Is it free?**
A: 100% free and open source (MIT License)

**Q: Can I use it at work?**
A: Yes! Works on corporate networks. Settings are per-user.

---

## 📞 Support

**Documentation:**
- [Getting Started Guide](GETTING_STARTED.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Architecture Guide](ARCHITECTURE.md)

**Community:**
- GitHub Issues: https://github.com/DarkRX01/Real-World-Cyber-Defense/issues
- Discussions: https://github.com/DarkRX01/Real-World-Cyber-Defense/discussions

**Contributing:**
- See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 License

MIT License - Free to use, modify, distribute.
See [LICENSE](LICENSE) for details.

---

## 🎯 Version

**Current:** v2.0.0 (Desktop Edition)
**Released:** 2026-01-28

---

## 🙏 Thanks

Built with:
- Python 3
- PyQt5
- Security best practices
- Community feedback

---

**Stay safe. Stay protected. Cyber Defense has your back. 🛡️**
