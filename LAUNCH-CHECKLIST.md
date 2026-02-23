# 🚀 Launch Checklist – Cyber Defense

Use this checklist before announcing a release or going live.

---

## Pre-Release (Before Tagging)

- [ ] **Build passes** – `python build-safe-exe.py` completes successfully
- [ ] **Tests pass** – `pytest tests/` (or `make test`)
- [ ] **ZIPs created** – `python package-for-release.py` produces:
  - `releases/CyberDefense-Windows-Portable.zip`
  - `releases/CyberDefense-Windows.zip`
- [ ] **CHANGELOG updated** – Version and changes documented
- [ ] **Version bumped** – In `pyproject.toml`, `version_info.txt`, README badge

---

## Release (Tag Push or Manual)

- [ ] **Create release** – Tag (e.g. `v3.0.0`) or manual GitHub Release
- [ ] **Attach artifacts** – ZIP files, SHA256/SHA512 checksums
- [ ] **VirusTotal** – Upload EXE and ZIP, add report link to release notes (goal: 0 detections)
- [ ] **Release notes** – What's new, download instructions, verification steps

---

## Post-Release

- [ ] **GitHub repo description** – Set to: "Desktop real-time threat scanner & privacy shield (Windows/Linux)"
- [ ] **Test download** – Download ZIP from release page, extract, run
- [ ] **Share** – r/privacy, r/cybersecurity, r/opensource (when ready)

---

## Trust & Safety (Ongoing)

- [ ] **No bypass instructions** – Never tell users "More info → Run anyway"
- [ ] **Code signing** – When cert available, add to `build-signed.yml` secrets
- [ ] **VirusTotal** – Report false positives to Elastic, Jiangmin, Zillya, etc.

---

*Quick ref: [RELEASE-GUIDE.md](RELEASE-GUIDE.md) | [ROADMAP.md](ROADMAP.md)*
