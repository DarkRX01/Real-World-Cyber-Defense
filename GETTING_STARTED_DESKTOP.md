# 🚀 Getting Started with Cyber Defense (Desktop Edition)

Welcome to **Real-World Cyber Defense**, your new desktop security guardian!

This guide will take you through setup in **5 minutes or less**.

---

## 📥 Installation

### 🪟 Windows Users

**Step 1:** Download installer
```
Click: install-windows.bat
```

**Step 2:** Double-click the file
- Windows might ask "Do you want to run this file?" → Click **Yes**

**Step 3:** Wait for completion
- Automatically downloads Python (if needed)
- Installs security libraries
- Creates desktop shortcut
- Takes 2-3 minutes depending on internet speed

**Step 4:** Verify installation
- Look for "Cyber Defense" shortcut on Desktop
- You'll see the completion message

### 🐧 Linux Users

**Step 1:** Download installer
```bash
wget https://github.com/DarkRX01/Real-World-Cyber-Defense/raw/main/install-linux.sh
chmod +x install-linux.sh
```

**Step 2:** Run the installer
```bash
./install-linux.sh
```

**Step 3:** Answer prompts
- Install system packages: Press `y` for yes
- Auto-start on boot: Your choice (optional)

**Step 4:** Verify installation
- See "✅ INSTALLATION COMPLETE!" message
- Find "Cyber Defense" in Applications menu

---

## 🎯 First Launch

### Launch the App

**Windows:**
1. Double-click "Cyber Defense" on Desktop
2. Or open Start → Search "Cyber Defense" → Click it

**Linux:**
1. Click Applications → Search "Cyber Defense"
2. Or open terminal, type: `cyber-defense`

### What You'll See

```
┌──────────────────────────────────────────┐
│  🛡️ CYBER DEFENSE DASHBOARD              │
├──────────────────────────────────────────┤
│                                          │
│  🔴 Threats Detected: 0                  │
│  🚫 Trackers Blocked: 0                  │
│  🎣 Phishing Blocked: 0                  │
│                                          │
│  🔒 Monitoring Active    ⏸️ Pause        │
│                                          │
│  📋 Recent Activity      [Dashboard]    │
│                          [Threats]      │
│                          [Tools]        │
│                          [⚙️ Settings]  │
└──────────────────────────────────────────┘
```

---

## ⚙️ First-Time Setup (2 minutes)

### Step 1: Open Settings
1. Click **⚙️ Settings** button
2. You'll see the settings dialog

### Step 2: Configure Basic Settings
```
Threat Sensitivity: 🟡 Medium (RECOMMENDED)

Features:
  ✓ Enable Phishing Detection     [✅ Keep ON]
  ✓ Block Trackers               [✅ Keep ON]
  ✓ Scan Downloads               [✅ Keep ON]
  ✓ Scan URLs                    [✅ Keep ON]
  ✓ Run in Background            [✅ Keep ON]
  ✓ Auto-Start on Boot           [❌ Keep OFF for now]
  ✓ Enable Notifications         [✅ Keep ON]
```

### Step 3: Save Settings
1. Click **💾 Save Settings**
2. See ✅ "Settings saved successfully!"

---

## 🎓 How It Works

### Real-Time Monitoring
The app continuously watches for threats:

```
Your Computer
    ↓
[URL you visit] → Scanned for phishing
    ↓
[Files you download] → Scanned for malware
    ↓
[Tracking pixels] → Detected and blocked
    ↓
Dashboard shows results in real-time
```

### What Gets Protected
- ✅ All URLs you visit
- ✅ Files you download
- ✅ Tracking attempts
- ✅ Phishing attempts
- ✅ System vulnerabilities

### Privacy Promise
- 🔒 All scanning happens locally
- 🔒 No data leaves your computer
- 🔒 No cloud uploads
- 🔒 No data collection
- 🔒 100% private

---

## 📊 Understanding the Dashboard

### Status Indicators

| Icon | Meaning | Action |
|------|---------|--------|
| 🟢 | Safe/Normal | Continue normally |
| 🟡 | Warning | Be careful |
| 🔴 | Danger | Take action |
| ⚫ | Critical | Stop immediately |

### The Three Tabs

#### 📊 Dashboard (Main View)
- Real-time threat count
- Total trackers blocked
- Total phishing prevented
- Recent activity log
- Quick actions

**Example Activity:**
```
Time       Type        Status      Details
11:42:23   Phishing    🛡️ Blocked  paypa1.com - Lookalike
11:42:15   Tracker     🛡️ Blocked  google-analytics.com
11:42:08   URL Safe    ✅ OK      www.reddit.com
```

#### 🔴 Threats (Detailed Log)
- Every threat ever detected
- Full URL/file information
- Threat type
- Severity level
- When it occurred

#### 🔧 Tools (Manual Checks)
- **Scan URL** - Test any URL
- **System Scan** - Check whole computer
- **Vulnerability Check** - Find weak points

---

## 🎮 Basic Operations

### Pause Monitoring
When you need to temporarily allow something:

1. Click **⏸️ Pause Monitoring**
2. Status changes to orange
3. Click **▶️ Resume** to restart

### Scan a Suspicious URL
1. Copy the URL to clipboard
2. Click **Tools** tab
3. Click **Scan URL from Clipboard**
4. Get instant result

### Clear Threat Log
1. Click **🔴 Threats** tab
2. Click **🗑️ Clear Log**
3. Log resets (stats still kept)

### Check System Health
1. Click **Tools** tab
2. Click **Full System Scan**
3. Waits for scan completion
4. Shows findings

---

## 🔐 Customization Guide

### Adjusting Sensitivity

**Choose the right level for you:**

```
🟢 LOW SENSITIVITY
├─ Only blocks confirmed malware
├─ Very few false positives
└─ Use: Trusted websites only

🟡 MEDIUM SENSITIVITY (DEFAULT)
├─ Balanced approach
├─ Catches most real threats
├─ Few false positives
└─ Use: Normal browsing

🔴 HIGH SENSITIVITY
├─ Aggressive detection
├─ May warn about safe sites
└─ Use: Visiting risky/unknown sites

⚫ EXTREME SENSITIVITY
├─ Maximum alerts
├─ Very strict filtering
└─ Use: Security research
```

### Enabling/Disabling Features

**Phishing Detection:**
- ✅ ON: Blocks phishing websites
- ❌ OFF: Only warns about downloads

**Tracker Blocking:**
- ✅ ON: Blocks all tracking pixels
- ❌ OFF: Allows tracking (not recommended)

**Download Scanning:**
- ✅ ON: Checks downloaded files
- ❌ OFF: No file protection

**URL Scanning:**
- ✅ ON: Monitors all URLs
- ❌ OFF: No URL protection

**Background Service:**
- ✅ ON: Runs in system tray
- ❌ OFF: Only works when window open

**Auto-Start:**
- ✅ ON: Launches on system boot
- ❌ OFF: Manual launch only

**Notifications:**
- ✅ ON: Popup alerts for threats
- ❌ OFF: Silent operation

---

## 🆘 Troubleshooting

### App Won't Start

**Windows:**
```
Error: "Python not found"
→ Download Python from python.org
→ Run installer with Admin rights
→ Try installing again
```

**Linux:**
```
Error: "PyQt5 not found"
→ Run: pip3 install PyQt5
→ Then: cyber-defense
```

### Threat Log Empty

```
Is this your first day?
→ This is normal! Log builds over time
→ Visit a few websites to populate
→ Check will add entries as threats found
```

### Settings Not Saving

```
Error: "Settings save failed"
→ Check folder permissions
→ On Linux: chmod 755 ~/.cyber-defense
→ Restart the app
→ Try again
```

### High CPU Usage

```
Is your system scanning?
→ Click Tools → Full System Scan
→ This takes a few minutes
→ Let it finish
→ CPU usage returns to normal
```

### Notifications Not Working

**Windows:**
- Check: Settings → System → Notifications
- Ensure "Do not disturb" is OFF

**Linux:**
- Install: `sudo apt install notification-daemon`
- Check: Settings → Notifications is enabled in app

---

## 🚀 Next Steps

### Beginner Level
1. ✅ Install the app (done!)
2. ✅ Configure settings (done!)
3. Browse normally - app protects in background
4. Check threat log occasionally

### Intermediate Level
5. Enable auto-start on boot
6. Add API keys for enhanced detection
7. Adjust sensitivity based on your needs
8. Review logs weekly

### Advanced Level
9. Check vulnerability scan results
10. Study threat patterns in log
11. Contribute improvements
12. Share with others

---

## 📖 Full Documentation

For more detailed information:

| Guide | Contents |
|-------|----------|
| [README.md](README.md) | Features, download, quick start |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Problem solving (20+ scenarios) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical design and how it works |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute code |

---

## ❓ Common Questions

**Q: Is it really free?**
A: Yes! 100% free, open source (MIT License)

**Q: Will it slow my computer?**
A: No! Uses <50MB RAM, minimal CPU (unless scanning)

**Q: Can I trust it?**
A: Yes! Code is open source - anyone can review it
   GitHub: https://github.com/DarkRX01/Real-World-Cyber-Defense

**Q: Does it need internet?**
A: Not always. Basic protection works offline.
   Enhanced features (API lookups) need internet.

**Q: Can I uninstall it?**
A: Yes, easily. Everything you install can be removed cleanly.

**Q: Is my data safe?**
A: Yes! All processing happens on your computer.
   No data sent to servers (unless you enable optional APIs).

---

## 🎉 You're Ready!

**Congratulations!** Your computer is now protected by Cyber Defense.

### Quick Recap
- ✅ App installed
- ✅ Settings configured  
- ✅ Monitoring active
- ✅ Dashboard ready
- ✅ You're protected!

### What to Do Now
1. Use your computer normally
2. App protects in background automatically
3. Check Dashboard occasionally to see what was blocked
4. Adjust settings as needed
5. Enjoy peace of mind!

---

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**Have questions?** Open an issue: https://github.com/DarkRX01/Real-World-Cyber-Defense/issues

**Want to contribute?** See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Stay safe. Stay protected. Cyber Defense has your back. 🛡️**
