# 🛡️ Real-World Cyber Defense - Desktop Application

> **The ultimate security tool for your Windows and Linux PC**  
> Protect against phishing, trackers, malware, and vulnerabilities.  
> **Completely FREE. Open Source. Always Local.**

![Status](https://img.shields.io/badge/status-production-brightgreen)
![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![OS](https://img.shields.io/badge/OS-Windows%2FLinux-brightgreen)

---

## 🎯 What Is It?

**Cyber Defense** is a lightweight desktop application that protects your entire computer from digital threats:

✅ **Real-time threat detection** - Monitors URLs and files  
✅ **Phishing protection** - Blocks deceptive websites  
✅ **Privacy tracker blocking** - Stops behavioral tracking  
✅ **Download protection** - Scans files for malware  
✅ **System vulnerability detection** - Finds weak security settings  
✅ **Completely free** - Open source, no subscriptions  
✅ **Private by default** - All scanning happens locally  
✅ **Works on Windows & Linux** - Unified protection  

---

## ⚡ Quick Start (30 Seconds)

### 🎯 Just Want to Download?
👉 **[Go to QUICK-START.md](QUICK-START.md)** for the super easy installation guide

### Choose Your Operating System:

#### 🪟 Windows
```bash
1. Download install-windows.bat
2. Double-click it
3. Wait 2 minutes
4. Done! Desktop shortcut created ✅
```

#### 🐧 Linux
```bash
./install-linux.sh
# Supports: Ubuntu, Debian, Fedora, Arch Linux
# Auto-detects your distro
```

**Installation takes 2-3 minutes.** Includes automatic dependency setup.

### 📖 New Here?
Start with **[SETUP.md](SETUP.md)** - Everything explained in simple terms

---

## 🚀 Features

### 🔗 Real-Time URL Scanning
Automatically analyzes every URL you visit:
- **Phishing detection** - Identifies fake login pages
- **Domain reputation** - Checks if site is known threat
- **Pattern analysis** - Detects suspicious URL tricks
- **Clipboard monitoring** - Scans URLs you copy automatically

**Protected against:**
- `paypa1.com` (fake PayPal)
- `amaz0n.com` (fake Amazon)
- IP-based phishing attacks
- Lookalike domains

### 🎣 Advanced Phishing Detection
Machine learning-powered analysis:
- **Keyword detection** - Finds urgent/verify language
- **Homograph attack prevention** - Blocks confusing lookalike domains
- **TLD analysis** - Flags suspicious extensions (.xyz, .tk, etc.)
- **HTTPS verification** - Warns about insecure sites
- **Confidence scoring** - Shows threat probability (0-100%)

### 🚫 Tracker Blocking
Stop companies from tracking your behavior:
- **25+ known trackers** - Google Analytics, Facebook Pixel, etc.
- **Real-time blocking** - Prevents tracking pixels from loading
- **Auto-detection** - Identifies new tracking services
- **Detailed logging** - See what trackers were blocked

### 📥 Download Protection
Scans files before they harm your computer:
- **Executable detection** - Flags suspicious .exe, .dll files
- **File hash analysis** - Matches against malware database
- **VirusTotal integration** - Optional cloud scanning
- **Size warnings** - Alerts on unusually large files

### 💻 System Security Checks
Identifies vulnerabilities:
- **Firewall status** - Ensures Windows Firewall is active
- **Antivirus status** - Checks if Windows Defender is enabled
- **Permission analysis** - Finds insecure file permissions
- **Update checking** - Recommends security patches

### ⚙️ Highly Customizable
Adjust for your needs:
- **4 sensitivity levels** (Low/Medium/High/Extreme)
- **Feature toggles** - Enable/disable protection types
- **Background service** - Optional silent monitoring
- **Auto-start option** - Launch on boot
- **Custom notifications** - Real-time threat alerts
- **Optional API keys** - Enhanced detection with external services

---

## 📊 Dashboard Overview

```
┌────────────────────────────────────────────┐
│  🛡️  CYBER DEFENSE DASHBOARD               │
├────────────────────────────────────────────┤
│                                            │
│  Statistics:                               │
│  🔴 Threats Detected: 42                   │
│  🚫 Trackers Blocked: 156                  │
│  🎣 Phishing Blocked: 8                    │
│                                            │
│  Status: 🔒 Monitoring Active              │
│                                            │
│  Tabs:                                     │
│  [📊 Dashboard] [🔴 Threats] [🔧 Tools]   │
│                                            │
│  Controls:                                 │
│  [⏸️ Pause] [⚙️ Settings] [❌ Close]      │
│                                            │
└────────────────────────────────────────────┘
```

---

## 🎯 How It Works

### 1. Continuous Protection
```
Background Monitoring
    ↓
[URL Detection] ← Every website you visit
[File Scanning] ← Every download
[Tracker Blocking] ← Tracking pixels
[System Checks] ← Security status
    ↓
Real-time Alerts & Logging
```

### 2. Zero Privacy Concerns
- ✅ All processing happens **locally** on your computer
- ✅ **No cloud uploads** unless you enable optional APIs
- ✅ **No data collection** or personal information tracking
- ✅ **Fully open source** - code auditable by security researchers

### 3. Easy Control
- **Enable/Disable** any feature anytime
- **Adjust sensitivity** for your comfort level
- **Pause monitoring** when needed
- **Review logs** of what was blocked

---

## 📥 Installation

### System Requirements

| Windows | Linux |
|---------|-------|
| Windows 7+ | Ubuntu 18.04+ |
| 512MB RAM | Debian 9+ |
| 500MB disk | Fedora 30+ |
| - | Arch Linux |

### Installation Steps

See [GETTING_STARTED_DESKTOP.md](GETTING_STARTED_DESKTOP.md) for detailed walkthrough.

**Quick version:**

**Windows:**
```
download install-windows.bat → double-click → wait → done
```

**Linux:**
```
wget install-linux.sh → chmod +x install-linux.sh → ./install-linux.sh → done
```

---

## ⚙️ Configuration

### Sensitivity Levels

| Level | For You | Default Features |
|-------|---------|------------------|
| 🟢 **Low** | Trusted sites only | Confirms phishing, blocks extreme threats |
| 🟡 **Medium** | Normal browsing | Balanced protection (RECOMMENDED) |
| 🔴 **High** | Risky/unknown sites | Aggressive detection, may flag safe sites |
| ⚫ **Extreme** | Security research | Maximum alerts, very strict filtering |

### Feature Toggle

```
✅ Phishing Detection      - Blocks fake login pages
✅ Tracker Blocking       - Stops behavioral tracking  
✅ Download Scanning      - Scans files for malware
✅ URL Scanning          - Monitors all web traffic
✅ Background Service    - Silent protection in tray
✅ Auto-Start           - Launch on boot (optional)
✅ Notifications        - Real-time threat alerts
```

### Example Settings

**For Normal Users:**
```
Sensitivity: Medium 🟡
All features: ON ✅
Background: ON ✅
Auto-start: OFF (optional)
Notifications: ON ✅
```

**For Security-Conscious:**
```
Sensitivity: High 🔴
All features: ON ✅
Background: ON ✅
Auto-start: ON ✅
Notifications: ON ✅
API Keys: Enabled
```

---

## 🔧 Tools

### 🔗 URL Scanner
Manually test any suspicious URL:
```
1. Copy URL to clipboard
2. Click Tools → Scan URL
3. Get instant analysis
```

### 💻 System Scan
Comprehensive security audit:
```
1. Click Tools → Full System Scan
2. Wait for completion
3. Review findings
```

### ⚠️ Vulnerability Check
Find security weaknesses:
```
1. Click Tools → Check Vulnerabilities
2. See potential issues
3. Follow recommendations
```

---

## 📋 Understanding Threats

### 🎣 Phishing (High Severity)
**What:** Website impersonating a trusted service to steal credentials

**Examples:**
- `paypa1.com` (fake PayPal)
- "Click here to verify your Amazon account"
- Urgent language demanding action

**What to do:** ❌ Don't click, close the tab

### 🚫 Tracker (Low Severity)
**What:** Analytics/tracking pixels collecting your behavior data

**Examples:**
- Google Analytics
- Facebook Pixel
- Hotjar session recording

**What to do:** ✅ Already blocked, you're safe

### 📥 Malware (High Severity)
**What:** Malicious software trying to infect your computer

**Examples:**
- Suspicious .exe files
- Files flagged by VirusTotal
- Executable with unusual size

**What to do:** ❌ Delete immediately

### 🔗 Suspicious URL (Medium Severity)
**What:** URL with unusual patterns suggesting attacks

**Examples:**
- IP addresses instead of domain names
- Excessive URL encoding
- JavaScript protocol handlers

**What to do:** ❌ Avoid clicking

---

## 🎓 Getting Help

### 📖 Documentation

| Document | Purpose |
|----------|---------|
| [README-DESKTOP.md](README-DESKTOP.md) | Complete feature guide |
| [GETTING_STARTED_DESKTOP.md](GETTING_STARTED_DESKTOP.md) | Installation & first-time setup |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Problem solving (20+ scenarios) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical design details |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute code |

### 🤝 Get Support

- **GitHub Issues:** https://github.com/DarkRX01/Real-World-Cyber-Defense/issues
- **Discussions:** https://github.com/DarkRX01/Real-World-Cyber-Defense/discussions
- **Check Troubleshooting:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### 🔧 System Tray Menu

Right-click system tray icon:
```
→ Show        - Open app window
→ Pause       - Pause monitoring
→ Settings    - Open settings
→ Exit        - Close app
```

---

## ❓ Frequently Asked Questions

**Q: Is it really free?**
A: Yes! 100% free and open source (MIT License). No ads, no subscriptions.

**Q: Will it slow my computer?**
A: No! Uses <50MB RAM and minimal CPU. Lightweight by design.

**Q: Can I trust it?**
A: Yes! Code is fully open source. Anyone can review it.  
   GitHub: https://github.com/DarkRX01/Real-World-Cyber-Defense

**Q: Does it work offline?**
A: Mostly! Basic phishing detection works offline. Enhanced features need internet.

**Q: What about privacy?**
A: 100% local. No data leaves your computer unless you enable optional APIs.

**Q: Can I customize it?**
A: Yes! Settings, sensitivity, feature toggles, all customizable.

**Q: Works with antivirus?**
A: Yes! Complements Windows Defender, Norton, McAfee, etc.

**Q: Can I uninstall it?**
A: Yes! Clean uninstall without leftover files.

---

## 🚀 Advanced Features

### Optional API Keys
For enhanced detection:

**Google Safe Browsing API:**
```
1. Go to https://console.cloud.google.com
2. Create API key
3. Add to app settings
→ Better phishing detection
```

**VirusTotal API:**
```
1. Go to https://www.virustotal.com
2. Create free account
3. Add API key to settings
→ File scans check global malware database
```

### Command Line Usage

```bash
# Launch normally
python3 -m cyber_defense.app_main

# Launch in background
python3 -m cyber_defense.app_main --headless

# Check status
cyber-defense --status
```

### Logs & Data

**Windows:**
```
C:\Users\[YourUsername]\.cyber-defense\
├── settings.json
├── threat_log.json
└── logs\
```

**Linux:**
```
~/.cyber-defense/
├── settings.json
├── threat_log.json
└── logs/
```

---

## 📈 Version History

### v2.0.0 - Desktop Edition (Current)
- ✨ Professional desktop application for Windows and Linux
- ✨ Cross-platform support (Windows & Linux)
- ✨ PyQt5 GUI with beautiful dashboard
- ✨ Real-time threat monitoring
- ✨ Customizable sensitivity levels
- ✨ System tray integration
- ✨ Advanced phishing detection
- ✨ Tracker blocking
- ✨ Download protection
- ✨ System vulnerability detection

### v1.0.0 - Initial Release
- Desktop security application release

---

## 🤝 Contributing

Want to help improve Cyber Defense?

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report bugs
- How to request features
- How to submit code improvements
- Development setup guide
- Testing procedures

---

## 📄 License

MIT License - Free to use, modify, and distribute.

See [LICENSE](LICENSE) for full details.

---

## 🛠️ Built With

- **Python 3** - Core application
- **PyQt5** - GUI framework
- **Requests** - HTTP requests
- **Pyperclip** - Clipboard access

---

## 🙏 Acknowledgments

Thanks to everyone who:
- Tested the application
- Reported issues
- Suggested improvements
- Contributed code
- Shared with others

---

## 📞 Contact & Social

- **GitHub:** https://github.com/DarkRX01/Real-World-Cyber-Defense
- **Issues:** Report bugs and request features
- **Discussions:** Community Q&A and feedback

---

## ⚡ Quick Links

| Link | Purpose |
|------|---------|
| [Getting Started](GETTING_STARTED_DESKTOP.md) | Installation guide |
| [Full Features](README-DESKTOP.md) | Complete feature list |
| [Troubleshooting](TROUBLESHOOTING.md) | Fix common issues |
| [Contributing](CONTRIBUTING.md) | How to contribute |
| [GitHub Releases](https://github.com/DarkRX01/Real-World-Cyber-Defense/releases) | Download latest version |

---

**Your computer. Your security. Your control. 🛡️**

---

### Made with ❤️ for cybersecurity and privacy

**Real-World Cyber Defense** - Because your security matters.
