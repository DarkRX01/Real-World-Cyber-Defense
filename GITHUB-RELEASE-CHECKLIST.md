# GitHub Release Checklist

Use this checklist to prepare your extension for GitHub release.

---

## ✅ Pre-Release Checklist

### Code & Functionality
- [ ] All features working without errors
- [ ] No console errors (F12)
- [ ] Tested with and without API key
- [ ] Settings persist correctly
- [ ] Extension loads unpacked successfully
- [ ] No hardcoded secrets or API keys

### Documentation
- [ ] README.md is complete and accurate
- [ ] FREE-GITHUB-INSTALL.md created (easy instructions)
- [ ] CONTRIBUTING.md complete
- [ ] SECURITY.md in place
- [ ] DEVELOPMENT.md helpful for developers
- [ ] All links in docs work
- [ ] CODE_OF_CONDUCT.md present

### GitHub Setup
- [ ] Repository created and public
- [ ] Repo description updated
- [ ] Website link added (GitHub pages or docs)
- [ ] Topics/tags added (chrome, security, privacy, etc.)
- [ ] LICENSE file present (MIT)
- [ ] .gitignore configured (if needed)

### Files Ready
- [ ] manifest.json validated
- [ ] All source files present:
  - [ ] src/background/background.js
  - [ ] src/popup/popup.html, popup.js, popup.css
  - [ ] src/options/options.html, options.js, options.css
  - [ ] src/utils/constants.js, helpers.js
- [ ] Icons present (icons/shield.svg)
- [ ] No sensitive files committed

---

## 📦 Creating Release on GitHub

### Step 1: Create Zip File
```powershell
# From Windows PowerShell in extension directory
Compress-Archive -Path manifest.json, src, icons -DestinationPath cyber-defense-extension-v1.0.0.zip
```

### Step 2: Go to GitHub Releases
```
1. Go to: https://github.com/YOUR_USERNAME/cyber-defense-extension
2. Click "Releases" (right sidebar)
3. Click "Create a new release"
```

### Step 3: Fill in Release Info
```
Tag: v1.0.0
Title: Cyber Defense Extension v1.0.0

Description:
## Real-World Cyber Defense v1.0.0 🎉

### What's New
- Real-time URL scanning with Google Safe Browsing API
- Privacy tracker detection (25+ domains)
- Download security analysis
- Ephemeral threat logging
- User-friendly settings interface

### Installation
See [FREE-GITHUB-INSTALL.md](FREE-GITHUB-INSTALL.md) for easy setup!

**No payment required. Completely free.** ✅

### Features
- 🔍 Real-time threat detection
- 🛡️ Privacy tracker blocking
- ⬇️ Download security
- 📋 Threat logging
- ⚙️ Easy configuration

### Links
- 📖 [Installation Guide](FREE-GITHUB-INSTALL.md)
- 📚 [Full Documentation](README.md)
- 🤝 [Contributing](CONTRIBUTING.md)
- 🔐 [Security Policy](SECURITY.md)
```

### Step 4: Upload Files
```
1. Drag & drop cyber-defense-extension-v1.0.0.zip
2. GitHub will upload it
```

### Step 5: Publish Release
```
1. Click "Publish release"
2. Done! 🎉
```

---

## 🎯 Release URL

After publishing, your release will be at:
```
https://github.com/YOUR_USERNAME/cyber-defense-extension/releases/tag/v1.0.0
```

Users download from:
```
https://github.com/YOUR_USERNAME/cyber-defense-extension/releases
```

---

## 📢 After Release

### Tell People!
- [ ] Share on Twitter/X
- [ ] Share on Reddit (r/ChromeExtensions, r/cybersecurity)
- [ ] Share in developer communities
- [ ] Add to extension lists
- [ ] GitHub show off your project

### Keep It Updated
- [ ] Watch for issues reported
- [ ] Fix bugs quickly
- [ ] Create new releases for updates
- [ ] Maintain documentation

---

## 🔄 Future Releases

For each new version:

### Update Version
```json
// manifest.json
"version": "1.1.0"
```

### Update CHANGELOG
```markdown
## v1.1.0 - [Date]
- Feature: Added X
- Fix: Bug with Y
- Docs: Improved Z
```

### Create Release
```
1. Create new zip: cyber-defense-extension-v1.1.0.zip
2. Go to Releases → Create new release
3. Tag: v1.1.0
4. Upload zip
5. Publish
```

---

## ✨ Pro Tips

1. **Use semantic versioning**: v1.0.0, v1.1.0, v2.0.0
2. **Keep CHANGELOG updated**: Users want to know what changed
3. **Write clear release notes**: Help users understand updates
4. **Test before releasing**: No broken releases!
5. **Respond to issues**: Users appreciate engagement
6. **Share updates**: Tell people about new versions

---

## 🎉 You're Ready!

Your extension is ready for public release on GitHub!

**Complete & publish your first release today.** 🚀
