# 🛡️ Cyber Defense - Real-World Security

A modern desktop application for learning about threat detection and security monitoring on Windows.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Educational-yellow)

## ⚠️ Important Disclaimer

**This is an educational/demonstration project, NOT production-grade security software.**

- ❌ No kernel-level protection
- ❌ No real-time file system monitoring
- ❌ Basic detection (won't catch packed/encrypted malware)
- ❌ Not a replacement for Windows Defender or real antivirus

**For real security:** Use Windows Defender + Malwarebytes + regular updates + backups.

**See [SECURITY-ROADMAP.md](SECURITY-ROADMAP.md) for honest limitations and what real AV requires.**

## ✨ Features

- 🔥 **Real-time Threat Detection** - Automatically detect and block threats
- 🚨 **Tracker Blocking** - Block known tracking domains and scripts
- 🎯 **Phishing Detection** - Identify suspicious URLs and phishing attempts
- 📋 **Clipboard Monitoring** - Scan URLs copied to your clipboard
- 🎨 **Modern GUI** - Beautiful, colorful dashboard with gradient cards
- 🌙 **Dark Theme** - Easy on the eyes with a professional dark interface
- 💾 **System Tray** - Runs quietly in the background
- 📊 **Statistics Dashboard** - Track threats, trackers, and phishing attempts

## 📥 Download & Installation

### Option 1: Download Pre-built Release (Easiest)

1. Go to [Releases](../../releases)
2. Download **`CyberDefense-Windows-Portable.zip`**
3. Extract the **entire ZIP file** to a folder
4. Run `CyberDefense.exe` from the extracted folder

> ⚠️ **IMPORTANT:** Do NOT move just the `.exe` file! Keep all files together.

### Option 2: Build from Source

```bash
# Clone the repository
git clone https://github.com/DarkRX01/Real-World-Cyber-Defense.git
cd Real-World-Cyber-Defense

# Install dependencies
pip install -r requirements.txt

# Run from source
python app_main.py

# OR build executable
python build-final.py
```

## 🚀 Quick Start

1. **First Run**
   - Double-click `CyberDefense.exe`
   - If Windows SmartScreen appears, click "More info" → "Run anyway"
   - The app will appear with a modern gradient interface

2. **Using the App**
   - The app monitors your clipboard automatically
   - Copy any URL and it will be scanned
   - Threats are shown in the dashboard with color-coded cards
   - Click the system tray icon to show/hide the window

3. **Settings**
   - Go to the **Settings** tab
   - Adjust sensitivity: Low, Medium, High, or Extreme
   - Enable/disable specific features
   - Click "Save settings" to apply

## 🎨 Interface Preview

The app features a modern, colorful design:

- **🔥 Red Gradient Card** - Threats Blocked
- **🚨 Orange Gradient Card** - Trackers Found  
- **🎯 Cyan Gradient Card** - Phishing Detected
- **💜 Purple Gradient Header** - Main navigation
- **✓ Green Status Badge** - Active monitoring indicator

## 🛠️ For Developers

### Project Structure

```
cyber-defense-extension/
├── app_main.py              # Main application entry point
├── threat_engine.py         # Threat detection logic
├── background_service.py    # Background monitoring service
├── build-final.py          # Build script for creating EXE
├── package-for-release.py  # Create distributable ZIP
├── requirements.txt        # Python dependencies
├── CyberDefense.spec       # PyInstaller configuration
└── tests/                  # Unit tests
```

### Build Commands

```bash
# Test dependencies
python test-dependencies.py

# Build production executable
python build-final.py

# Create release package
python package-for-release.py
```

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_threat_engine.py
```

## 📋 Requirements

- **OS:** Windows 10 or later
- **RAM:** 100 MB minimum
- **Disk:** 150 MB free space
- **Python:** 3.11+ (for building from source)

## 🔒 Security & Privacy

- ✅ **Local Processing** - All threat detection runs locally
- ✅ **No Data Collection** - We don't collect or transmit your data
- ✅ **Open Source** - Full source code available for review
- ✅ **Transparent** - All detection logic is visible in the code

## 🐛 Troubleshooting

### App doesn't start

1. Make sure you extracted the **entire ZIP**, not just the EXE
2. Check if antivirus is blocking it (add exception)
3. Try running as administrator
4. Check logs at: `%APPDATA%\.cyber-defense\logs\`

### DLL Extraction Error

If you see "Failed to extract PyQt5\Qt5\bin\opengl32sw.dll":
- You downloaded only the EXE file
- Download the full ZIP package from Releases
- Extract everything and run from the folder

### Antivirus False Positive

Some antivirus software may flag the app as suspicious (common for unsigned apps):
- This is a false positive
- The app is open source - you can review the code
- Add an exception in your antivirus settings

## 📖 Documentation

- **User Guide:** [GETTING_STARTED_DEMO.md](GETTING_STARTED_DEMO.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Security:** [SECURITY.md](SECURITY.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with PyQt5 for the modern GUI
- Uses local threat detection algorithms
- Designed for real-world security scenarios

## 📧 Support

- **Issues:** [GitHub Issues](../../issues)
- **Email:** [Create an issue for support]
- **Discussions:** [GitHub Discussions](../../discussions)

---

**Made with ❤️ for cybersecurity education and protection**

⭐ If you find this useful, please star the repo!
