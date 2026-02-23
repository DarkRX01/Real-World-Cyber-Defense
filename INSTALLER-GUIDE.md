# 🚀 Installation Guide – Cyber Defense Desktop App

This guide shows how to install the **Cyber Defense** desktop security app on Windows or Linux.

---

## 📦 What You Need

- **Windows 10/11** or **Linux** (Ubuntu, Debian, Fedora, Arch)
- **5 minutes** of your time
- For portable: Download the ZIP from [Releases](https://github.com/DarkRX01/Real-World-Cyber-Defense/releases)

---

## Option 1: Windows – Portable (Easiest) 🪟

### Step 1: Download

1. Go to [Releases](https://github.com/DarkRX01/Real-World-Cyber-Defense/releases)
2. Download **`CyberDefense-Windows-Portable.zip`** (or `CyberDefense-Windows.zip`)

### Step 2: Extract & Run

1. **Extract the entire ZIP** to a folder (e.g. `Desktop\CyberDefense`)
2. Double-click **`Run Cyber Defense.bat`** or **`CyberDefense.exe`**
3. The app starts in the **system tray** (icon near the clock)
4. **Double-click the tray icon** to open the main window

### Step 3: First Run

- See **README-FIRST.txt** in the extracted folder for tips
- If Windows or antivirus blocks it: See [SMARTSCREEN-WARNING.md](SMARTSCREEN-WARNING.md) and [ANTIVIRUS-FIXES.md](ANTIVIRUS-FIXES.md)

---

## Option 2: Windows – From Source

```bash
git clone https://github.com/DarkRX01/Real-World-Cyber-Defense.git
cd Real-World-Cyber-Defense/cyber-defense-extension
pip install -r requirements.txt
python app_main.py
```

To build your own EXE: `python build-safe-exe.py`

---

## Option 3: Linux – From Source 🐧

```bash
git clone https://github.com/DarkRX01/Real-World-Cyber-Defense.git
cd Real-World-Cyber-Defense/cyber-defense-extension
pip install -r requirements.txt
python app_main.py
```

---

## 📚 What's Next?

1. **Quick Start**: [USER-GUIDE.md](USER-GUIDE.md) or [GETTING_STARTED_DESKTOP.md](GETTING_STARTED_DESKTOP.md)
2. **Settings**: Open the app → Settings tab
3. **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## ❓ Questions?

- **Installation help**: [USER-GUIDE.md](USER-GUIDE.md)
- **Having issues**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Bug reports**: https://github.com/DarkRX01/Real-World-Cyber-Defense/issues

---

**Enjoy your safer computing!** 🛡️
