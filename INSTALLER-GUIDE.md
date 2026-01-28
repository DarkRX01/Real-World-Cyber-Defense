# 🚀 Easy Installation Guide

Welcome! This guide shows you 3 ways to install the **Real-World Cyber Defense Extension**. Pick the easiest one for your computer!

---

## 📦 What You Need

- **Google Chrome** (or Chromium/Edge)
- **The ZIP file** from GitHub releases
- **5 minutes** of your time

---

## Option 1: Windows (EASIEST) 🪟

### Step 1: Get the Setup File

1. Download `cyber-defense-extension-v1.0.0.zip` from:
   - 👉 https://github.com/DarkRX01/Real-World-Cyber-Defense/releases

2. Download `setup.bat` from the same GitHub page

3. Put both files in the **same folder** on your computer

### Step 2: Run the Installer

1. **Double-click** `setup.bat`
   - It might ask: "Do you want to run this file?" → Click **Yes**

2. The setup wizard will:
   - ✓ Check for Chrome
   - ✓ Create a folder for the extension
   - ✓ Extract the files
   - ✓ Show you what to do next

3. **Follow the on-screen instructions**
   - You'll see step-by-step directions
   - It will show you exactly what folder to select in Chrome

### Step 3: Load in Chrome

1. Open **Google Chrome**

2. Go to: **chrome://extensions/**

3. Turn **ON** "Developer mode" (toggle at top-right)

4. Click **"Load unpacked"**

5. Select the folder the setup created

6. **Done!** 🎉 Your extension is now active!

---

## Option 2: Linux (EASY) 🐧

### Step 1: Get the Files

1. Download `cyber-defense-extension-v1.0.0.zip` from:
   - 👉 https://github.com/DarkRX01/Real-World-Cyber-Defense/releases

2. Download `setup.sh` from GitHub

3. Put both files in the **same folder**

### Step 2: Make Setup Script Executable

Open your terminal and run:

```bash
chmod +x setup.sh
```

### Step 3: Run the Installer

In your terminal, run:

```bash
./setup.sh
```

The script will:
- ✓ Check for Chrome/Chromium
- ✓ Create installation folder: `~/.config/cyber-defense-extension`
- ✓ Extract the extension files
- ✓ Show you next steps

### Step 4: Load in Chrome

1. Open **Google Chrome** or **Chromium**

2. Go to: **chrome://extensions/**

3. Turn **ON** "Developer mode" (top-right corner)

4. Click **"Load unpacked"**

5. Navigate to: `~/.config/cyber-defense-extension`

6. Select the folder

7. **Done!** 🎉 Extension is active!

---

## Option 3: Manual Install (ALL PLATFORMS) 📖

### If the setup scripts don't work, do this manually:

### Step 1: Extract the ZIP

1. Download `cyber-defense-extension-v1.0.0.zip`

2. Right-click → **Extract All** (Windows)
   - Or use any zip tool (7-Zip, WinRAR, etc.)

3. You'll have a folder with:
   - `manifest.json`
   - `src/` folder
   - `icons/` folder
   - And more...

### Step 2: Open Chrome Extensions

1. Open **Google Chrome**

2. Type this in the address bar:
   ```
   chrome://extensions/
   ```

3. Press **Enter**

### Step 3: Enable Developer Mode

1. Look at the **top-right** of the page

2. Find the toggle that says **"Developer mode"**

3. Click it to turn it **ON** (it will turn blue)

### Step 4: Load the Extension

1. Click the button that says **"Load unpacked"**

2. A folder selection window will open

3. Navigate to where you extracted the ZIP

4. Select the **folder** (not a file inside it)

5. Click **"Select Folder"** or **"Open"**

### Step 5: Done! 🎉

- The extension is now installed!
- You should see it in your Chrome extensions list
- The shield icon will appear in your toolbar

---

## ✅ Verify Installation

After installation, you should see:

- ✓ The extension appears in your Chrome extensions list
- ✓ A shield icon (🛡️) in your toolbar
- ✓ Click the icon to see threat reports

---

## 🆘 Troubleshooting

### "Extension can't be loaded"
- Make sure you selected the **folder**, not a file
- The folder must contain `manifest.json`

### "Chrome not found"
- Install Chrome from: https://www.google.com/chrome/
- Or use Chromium/Edge (they work too)

### "ZIP extraction failed"
- Try a different ZIP tool
- Make sure the file isn't corrupted
- Download again from GitHub

### Setup script won't run (Windows)
- Right-click → "Run as Administrator"
- Or use Option 3 (Manual Install)

### Setup script won't run (Linux)
- Make sure you ran: `chmod +x setup.sh`
- Run from terminal: `./setup.sh`

### Still having issues?
- 📖 Read: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- 🐛 Report bug: https://github.com/DarkRX01/Real-World-Cyber-Defense/issues
- 💬 Ask question: https://github.com/DarkRX01/Real-World-Cyber-Defense/discussions

---

## 📚 What's Next?

After installation:

1. **Quick Start**: Read [FIRST-TIME-USERS.md](./FIRST-TIME-USERS.md)
2. **Settings**: Click extension icon → Options
3. **Add Your API Key**: (Optional) For advanced scanning
4. **Report Issues**: Use GitHub Issues if something breaks

---

## ❓ Questions?

- **Installation help**: [FIRST-TIME-USERS.md](./FIRST-TIME-USERS.md)
- **Having issues**: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Bug reports**: https://github.com/DarkRX01/Real-World-Cyber-Defense/issues
- **Questions**: https://github.com/DarkRX01/Real-World-Cyber-Defense/discussions

---

## 🎉 You're Ready!

The extension is now protecting you! It scans URLs, detects trackers, and checks downloads automatically.

**Enjoy your safer browsing!** 🛡️
