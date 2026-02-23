# Cyber Defense – Roadmap to Trust, Quality & Adoption

This roadmap organizes improvements into **must-haves** (trust & safety), **feature depth**, **usability**, **community**, and **path to 10/10**. Items are actionable and linked to existing docs where relevant.

---

## 1. Core Trust & Safety (without these → stays dangerous garbage)

### 1.1 Proper code signing
- [ ] **EV certificate or at minimum Microsoft Authenticode** on every released `.exe` (and driver if shipped).
- [ ] Unsigned kernel minifilter + “bypass SmartScreen” instructions = instant malware vibes → **never document bypass steps**.
- **Refs:** [SIGNING-SELF-DEFENSE.md](SIGNING-SELF-DEFENSE.md), [REPRODUCIBLE-BUILDS.md](REPRODUCIBLE-BUILDS.md), `.github/workflows/build-signed.yml` (secrets: `CODE_SIGNING_CERT`, `CODE_SIGNING_PASSWORD`).

### 1.2 Driver hardening & validation
The Rust minifilter (`minifilter-rust/`) must be:
- [ ] **Fully documented:** IRP operations hooked, exact filter altitude, communication method to user-mode. See [minifilter-rust/README.md](minifilter-rust/README.md) and [minifilter-rust/DRIVER-SPEC.md](minifilter-rust/DRIVER-SPEC.md).
- [ ] **Built reproducibly** (deterministic build from tag).
- [ ] **Either:** removed, **or** submitted for Microsoft HLK / Windows Hardware Certification.
- [ ] **Or:** replaced with safer alternatives (FileSystemWatcher + ETW for most monitoring) if certification isn’t realistic. Current production is user-mode only ([ARCHITECTURE.md](ARCHITECTURE.md)).

### 1.3 No “click More info → Run anyway” guidance
- [ ] **Stop telling users to disable Defender/SmartScreen.** Remove any “click More info → Run anyway” from README, TROUBLESHOOTING, SMARTSCREEN-WARNING.
- [ ] **Publish official VirusTotal links** for every release ZIP/EXE.
- [ ] **Goal:** 0 detections or only “suspicious behavior” from heuristics on VirusTotal.

### 1.4 Reproducible builds
- [ ] **GitHub Actions CI** that produces the **exact same binaries** from a source tag.
- [ ] Provide **build logs + SHA256** (and SHA512) of artifacts in each release. Already partially done in `build-signed.yml` and [REPRODUCIBLE-BUILDS.md](REPRODUCIBLE-BUILDS.md); verify and document in release notes.

---

## 2. Feature Quality & Depth

### 2.1 Real effectiveness proof
- [ ] **Upload EICAR, Eicar-like, ransom-sim, AMSI test samples, process-injection PoCs** → show detection + logs + quarantine in **video/GIF**.
- [ ] **Benchmark vs Windows Defender, Malwarebytes, ESET** on standard AV test sets (e.g. AV-Comparatives, MRG Effitas).
- **Refs:** [DETECTION-EFFECTIVENESS.md](DETECTION-EFFECTIVENESS.md), [THREAT-MODEL.md](THREAT-MODEL.md).

### 2.2 Low false positive rate
- [ ] **User whitelist**, **learning mode**, **sensitivity sliders**, **ignore-list per folder/process.**
- [ ] Behavioral engine: avoid overzealous defaults; make sensitivity and scope configurable.

### 2.3 VPN actually works & is optional
- [ ] **Full WireGuard-Go integration**, config import/export.
- [ ] **Proper kill-switch** (Windows Filtering Platform / WFP callout), leak protection tests.
- [ ] **Split-tunnel support.**

### 2.4 YARA & signatures meaningful
- [ ] Not just “download rules from GitHub.” **Curate/maintain a small high-quality set** + allow **custom rules folder**.
- [ ] If claiming ClamAV: **integrate ClamAV engine properly.**

### 2.5 Behavioral engine maturity
- [ ] Replace toy anomaly detection with **real ML/statistical baselining**: process parent–child trees, CPU/memory/network histograms, **ETW consumer** for sysmon-like events.

### 2.6 Rootkit / injection detection
- [ ] **Either drop the claim or implement properly:** e.g. DKOM detection via SSDT hooks scan, handle table checks, ETW tampering detection. Document limitations in [THREAT-MODEL.md](THREAT-MODEL.md) and [LIMITATIONS.md](LIMITATIONS.md).

---

## 3. Usability & Polish

### 3.1 Screenshots + video demos
- [ ] **Zero visuals = zero trust.** Record **3–5 min demo:** e.g. phishing link in clipboard detected, ransomware sim encryption blocked, VPN connect/kill-switch test.
- [ ] Add screenshots to README and docs.

### 3.2 Clean UI
- [ ] Modernize PyQt dark theme: **QDarkStyle or Fluent-style**, responsive layout.
- [ ] **Real-time graphs:** file scan progress, CPU usage, detections timeline.

### 3.3 Installer + auto-update without sketchy self-defense
- [ ] **Proper MSI installer (signed).** See `packaging/build-msi.ps1`.
- [ ] **Silent update channel** via GitHub Releases API (no “run bat as admin every time”).

### 3.4 Configuration & transparency
- [ ] **GUI settings** for every risky feature: enable/disable minifilter (if used), behavioral monitoring level, monitored folders, VPN auto-connect.

---

## 4. Community & Adoption

### 4.1 Fix repo description
- [ ] **Stop calling it a “Chrome extension”.** Use: **“Desktop real-time threat scanner & privacy shield (Windows/Linux)”.** Update GitHub repo description and README first line/tagline.

### 4.2 Get eyes on it
- [ ] Post on **r/privacy, r/cybersecurity, r/opensource**, Wilders Security, MalwareTips.
- [ ] Encourage **source builds + code review.**

### 4.3 Tests & coverage
- [ ] Expand **tests/** to **unit + integration** for detection logic (pytest + mocking ETW/FileSystemWatcher).
- **Refs:** [TESTING_GUIDE.md](TESTING_GUIDE.md), `tests/`.

### 4.4 Documentation cleanup
- [ ] **Merge 50+ redundant .md files** into clear sections: **Features, Architecture, Threat Model, Limitations, FAQ.**
- [ ] Single **LIMITATIONS.md** (short “what we cannot catch”) + pointer to [THREAT-MODEL.md](THREAT-MODEL.md) for full detail.

### 4.5 Threat model & limitations
- [ ] **Honest statement** of what it cannot catch: kernel rootkits (unless driver is certified and active), fileless malware, LOLBins, etc. Already covered in [THREAT-MODEL.md](THREAT-MODEL.md); surface in README and [LIMITATIONS.md](LIMITATIONS.md).

---

## 5. Realistic Path to 10/10

- [ ] **Independent security audit** (even informal by known researchers).
- [ ] **500+ stars + active contributors** (marketing + proven detections).
- [ ] **Packaging:** winget / Chocolatey / Scoop (signed packages).
- [ ] **Enterprise:** centralized logging, SIEM export, multi-user support.
- [ ] **Cross-platform parity:** Linux version actually usable, not “from source lol”.

---

## Quick reference – existing docs

| Topic              | Document |
|--------------------|----------|
| Architecture       | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Threat model       | [THREAT-MODEL.md](THREAT-MODEL.md) |
| Limitations        | [LIMITATIONS.md](LIMITATIONS.md) (to consolidate) |
| Signing            | [SIGNING-SELF-DEFENSE.md](SIGNING-SELF-DEFENSE.md), [REPRODUCIBLE-BUILDS.md](REPRODUCIBLE-BUILDS.md) |
| SmartScreen        | [SMARTSCREEN-WARNING.md](SMARTSCREEN-WARNING.md) |
| Minifilter         | [minifilter-rust/README.md](minifilter-rust/README.md), [minifilter-rust/DRIVER-SPEC.md](minifilter-rust/DRIVER-SPEC.md) |
| Detection          | [DETECTION-EFFECTIVENESS.md](DETECTION-EFFECTIVENESS.md), [CORE-DETECTION-OVERHAUL.md](CORE-DETECTION-OVERHAUL.md) |
| Build & release    | [RELEASE-GUIDE.md](RELEASE-GUIDE.md), [build/README.md](build/README.md) |

---

*Last updated: February 2026*
