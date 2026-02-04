# Upload the EXE to GitHub Releases

Use this guide to publish **Cyber Defense v2.2.0** (or the current build) to GitHub Releases so users can download the Windows portable ZIP.

---

## 1. Build and package (already done)

- **EXE:** `dist\CyberDefense\CyberDefense.exe`
- **Release ZIP:** `releases\CyberDefense-Windows-Portable.zip`  
  (Contains the whole `CyberDefense` folder: exe, Run Cyber Defense.bat, README-FIRST.txt, _internal.)

If you need to rebuild:

```powershell
cd "c:\Users\yamen.alkhoula.stude\Documents\Blue teaming\cyber-defense-extension"
python build-safe-exe.py
# Then create the zip:
Compress-Archive -Path "dist\CyberDefense" -DestinationPath "releases\CyberDefense-Windows-Portable.zip" -CompressionLevel Optimal
```

---

## 2. Push code and tag (optional but recommended)

```bash
cd "c:\Users\yamen.alkhoula.stude\Documents\Blue teaming\cyber-defense-extension"
git add -A
git commit -m "v2.2.0: GUI refresh, Protection card, version badge, release package"
git tag v2.2.0
git push origin main
git push origin v2.2.0
```

(Use your branch name instead of `main` if different.)

---

## 3. Create the release on GitHub

1. Open your repo: **https://github.com/DarkRX01/Real-World-Cyber-Defense** (or your fork).
2. Click **Releases** → **Draft a new release** (or **Create a new release**).
3. **Choose a tag:**  
   - Either select the existing tag **v2.2.0**, or  
   - Type **v2.2.0** and click **Create new tag: v2.2.0 on publish**.
4. **Release title:**  
   `v2.2.0 – GUI refresh, Protection card, Core Detection & VPN`
5. **Description:**  
   Copy the **v2.2.0** section from [CHANGELOG.md](CHANGELOG.md) (or the summary below).
6. **Attach the ZIP:**  
   - Drag and drop **`releases\CyberDefense-Windows-Portable.zip`** into the “Attach binaries” area, or  
   - Click “Choose files” and select that ZIP.
7. Click **Publish release**.

---

## 4. Suggested release description (v2.2.0)

```markdown
## What's new in v2.2.0

- **GUI refresh:** Version in window title and header, 4th stat card (Protection ON/PAUSED), Dashboard quick action to Tools, Threat history header, cleaner tab styling.
- **Core Detection Overhaul:** Real-time monitoring (Downloads, Desktop, Temp, user dirs), file hashes, YARA from GitHub, PE heuristics, ransomware honeypots, behavioral CPU spike detection.
- **VPN:** WireGuard connect/disconnect from tray; optional kill-switch alert when VPN drops.
- **Build:** Windows portable ZIP includes CyberDefense.exe, Run Cyber Defense.bat, README-FIRST.txt.

## Download

- **Windows (portable):** Download `CyberDefense-Windows-Portable.zip` below, extract, then run **CyberDefense.exe** or **Run Cyber Defense.bat** from the `CyberDefense` folder. Keep all files in the same folder.

## Requirements

- Windows 10/11 (64-bit).
- No install needed; extract and run.
```

---

## 5. After publishing

- The release will appear under **Releases** and the ZIP will be the main download.
- Update the repo **About** section if you want (description, topics).
- Optional: Pin the latest release or add a “Download” link in the README that points to the latest release asset.
