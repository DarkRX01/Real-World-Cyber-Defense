# Update Everything on GitHub

**Latest build:** The updated EXE (new GUI, v2.1.0) is in `releases/CyberDefense-Windows-Portable.zip`. A copy was also placed in your **Downloads** folder. Extract and run **Run Cyber Defense.bat** or **CyberDefense.exe**.

Follow these steps to push all changes to your GitHub repository.

---

## 1. Check status

From the **cyber-defense-extension** folder (or repo root if this project is the root):

```bash
cd "c:\Users\yamen.alkhoula.stude\Documents\Blue teaming\cyber-defense-extension"
git status
```

You should see all new and modified files listed.

---

## 2. Add all files

```bash
git add -A
```

Or add selectively:

```bash
git add .github/
git add app_main.py threat_engine.py background_service.py
git add detection/ realtime_monitor.py quarantine.py update_system.py
git add build-safe-exe.py packaging/
git add minifilter-rust/
git add README.md USER-GUIDE.md CHANGELOG.md
git add PRODUCTION-IMPROVEMENTS.md SIGNING-SELF-DEFENSE.md
git add tests/ pyproject.toml requirements.txt requirements-detection.txt
git add .gitignore GITHUB-UPDATE.md
git add GETTING_STARTED_DESKTOP.md TROUBLESHOOTING.md
# add any other changed docs
```

---

## 3. Commit

```bash
git commit -m "v2.1.0: Production improvements, UX, README & GitHub updates

- Detection: YARA, ML, behavioral monitoring (optional in Settings)
- Real-time file monitor (watchdog), quarantine, update system (2h)
- EICAR detection, CI build+EICAR scan, packaging (WiX/AppImage/DMG)
- Tray-first UX, tooltips, README-FIRST and launcher for EXE
- README and USER-GUIDE rewritten; GitHub issue/PR templates
- Changelog 2.1.0; minifilter-rust scaffold; SIGNING-SELF-DEFENSE"
```

---

## 4. Push to GitHub

**If you use `main`:**

```bash
git push origin main
```

**If you use `master`:**

```bash
git push origin master
```

**First time (set upstream):**

```bash
git push -u origin main
```

---

## 5. Optional: create a release

1. On GitHub: **Releases** → **Draft a new release**.
2. **Tag:** `v2.1.0` (create new tag).
3. **Title:** `v2.1.0 – New GUI, real-time protection, user-friendly EXE`.
4. **Description:** Copy from [CHANGELOG.md](CHANGELOG.md) section `[2.1.0]`.
5. Attach **releases/CyberDefense-Windows-Portable.zip** (already built; same zip is in your Downloads folder).
6. Publish release.

---

## 6. Optional: update repo description on GitHub

1. Open your repo on GitHub.
2. Click the **⚙️ (gear)** next to **About**.
3. Set **Description** to something like:  
   `Desktop security app: phishing & tracker detection, real-time file monitor, quarantine. Tray-first, user-friendly. Windows & Linux.`
4. Add **Topics** (e.g. `security`, `phishing-detection`, `malware`, `windows`, `python`, `pyqt5`).
5. Save.

---

## Checklist before pushing

- [ ] `pytest tests/` passes (or at least `tests/test_eicar.py` and `tests/test_threat_engine.py`)
- [ ] No secrets or API keys in committed files
- [ ] README and USER-GUIDE links are correct
- [ ] CHANGELOG and pyproject.toml version match (2.1.0)

---

**Repository:** https://github.com/DarkRX01/Real-World-Cyber-Defense
