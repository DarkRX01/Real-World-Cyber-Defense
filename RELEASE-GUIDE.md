# 📦 Release Guide - How to Upload to GitHub

This guide shows you how to create a release on GitHub so users can easily download your app.

---

## GitHub Repo Description (one-time setup)

**Set the repo description** (Settings → General → Description) to:

> Desktop real-time threat scanner & privacy shield (Windows/Linux)

This replaces any "Chrome extension" wording and accurately describes the product.

---

## 🚀 Quick Steps

### 1. Create the Release Package

**Option A – Reproducible build (recommended):**
```bash
python build-safe-exe.py
# Output in dist/CyberDefense/; ZIP via build-signed.yml on tag push
```

**Option B – Manual package:**
```bash
python build-final.py
python package-for-release.py
```

This creates: `releases/CyberDefense-Windows-Portable.zip` (ready to upload!)

### 2. Go to GitHub Releases

1. Go to your repository: https://github.com/DarkRX01/Real-World-Cyber-Defense
2. Click on **"Releases"** (on the right side)
3. Click **"Create a new release"** (or "Draft a new release")

### 3. Create the Release

**Tag version:** `v2.0.0` (or your version number)

**Release title:** `Cyber Defense v2.0.0 - Modern Security Dashboard`

**Description:** (Copy this template)

```markdown
# 🛡️ Cyber Defense v2.0.0

A modern, colorful desktop security app for Windows with real-time threat detection!

## ✨ What's New

- 🎨 **Modern Colorful GUI** - Vibrant gradient cards (red, orange, cyan)
- 🔥 **Improved Threat Detection** - Enhanced phishing and tracker detection
- 💜 **Gradient Header** - Beautiful purple-pink gradient design
- ✓ **Better Window Management** - Auto-centers on screen, always visible
- 📊 **Large Bold Stats** - Easy-to-read 42px numbers
- 🌙 **Dark Theme** - Professional dark interface

## 📥 Download

Download the ZIP file below, extract it, and run `CyberDefense.exe`

⚠️ **IMPORTANT:** Extract the ENTIRE ZIP file, don't just copy the EXE!

## 🚀 Features

- Real-time threat detection
- Clipboard URL monitoring
- Tracker blocking
- Phishing detection
- Modern gradient interface
- System tray integration

## 💻 Requirements

- Windows 10 or later
- 100 MB free space

## 🐛 Troubleshooting

If you get a DLL error, make sure you extracted the entire ZIP file!
See the [README](https://github.com/DarkRX01/Real-World-Cyber-Defense#-troubleshooting) for more help.

---

**Full Changelog:** https://github.com/DarkRX01/Real-World-Cyber-Defense/blob/main/CHANGELOG.md
```

### 4. Upload the ZIP File

1. Scroll down to **"Attach binaries"**
2. Click **"Attach files by dragging & dropping, selecting or pasting them"**
3. Upload: `releases/CyberDefense-Windows-Portable.zip`
4. Wait for it to upload (36 MB, takes ~30 seconds)

### 5. Publish the Release

1. Check **"Set as the latest release"**
2. Click **"Publish release"**

Done! 🎉

## 📱 After Publishing

Users can now:

1. Go to: https://github.com/DarkRX01/Real-World-Cyber-Defense/releases
2. Click on the latest release
3. Download `CyberDefense-Windows-Portable.zip`
4. Extract and run!

## 🔄 Updating for New Releases

When you make updates:

```bash
# 1. Build new version (use build-safe-exe.py for reproducible builds)
python build-safe-exe.py

# 2. Tag and push for automated release: git tag v2.1.0 && git push origin v2.1.0
#    Or manually package: python package-for-release.py

# 3. Create new release on GitHub with new version number (v2.0.1, v2.1.0, etc.)

# 4. Upload the new ZIP file (or use artifacts from build-signed.yml)
# 5. Upload to VirusTotal and add link to release notes
```

## 📝 Version Numbering

- **Major:** `v2.0.0` → `v3.0.0` (big changes, new features)
- **Minor:** `v2.0.0` → `v2.1.0` (new features, improvements)
- **Patch:** `v2.0.0` → `v2.0.1` (bug fixes, small updates)

## ✅ Checklist Before Release

- [ ] App works locally (`python app_main.py`)
- [ ] Built executable works (`python build-safe-exe.py` or `python build-final.py`)
- [ ] Created release package (`python package-for-release.py` or via `build-signed.yml` on tag)
- [ ] Updated CHANGELOG.md with changes
- [ ] Updated version number in README.md
- [ ] Committed and pushed all changes to GitHub
- [ ] Created release on GitHub (or pushed version tag for automated build)
- [ ] Uploaded ZIP file
- [ ] **VirusTotal:** Upload `CyberDefense.exe` and release ZIP to [VirusTotal](https://www.virustotal.com/), add link to release notes (goal: 0 detections or heuristic-only)
- [ ] Published release
- [ ] Tested download link works

## 🎯 Pro Tips

1. **Screenshots:** Add screenshots of the app to the release description
2. **Changelog:** Always include what changed
3. **Testing:** Test the ZIP download before announcing
4. **VirusTotal:** Upload EXE and ZIP to VirusTotal, add the link to release notes. Goal: 0 detections (or only heuristic "suspicious behavior"). Builds trust and avoids "malware vibes."
5. **Social:** Share the release link on social media

## VirusTotal (Trust & Safety)

For every release:
1. Go to [virustotal.com](https://www.virustotal.com/)
2. Upload `CyberDefense.exe` and the release ZIP
3. Add the VirusTotal report URL to the release description
4. Aim for **0 detections** or only heuristic/suspicious flags. If many engines flag it, investigate before publishing.

That's it! Your app is now easy for anyone to download and use! 🚀
