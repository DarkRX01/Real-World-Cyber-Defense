# ⚠️ WINDOWS SMARTSCREEN WARNING - What It Means

When you download CyberDefense.exe, you might see this message:

```
"Windows Defender SmartScreen prevented an unrecognized app from starting"
```

## Why This Happens

**Root Cause:**
- CyberDefense.exe is **unsigned** (no digital code signature)
- Windows SmartScreen requires code signatures to build reputation
- New applications without signatures trigger this warning (even legitimate ones)

**This is not a reflection on the security of Cyber Defense**, but rather Windows' defense against unsigned binaries in general.

---

## Your Options

**We do not recommend bypassing SmartScreen** (e.g. “More info” → “Run anyway”). That trains users to ignore security prompts. Prefer the options below.

### ✅ **Recommended: Build From Source**

The safest option is to build the app yourself from source code:

```bash
git clone https://github.com/DarkRX01/Real-World-Cyber-Defense.git
cd Real-World-Cyber-Defense/cyber-defense-extension
pip install -r requirements.txt
python app_main.py
```

**Why this is best:**
- You run code you can read and verify
- No binary from the internet
- Full transparency
- Build it your way

### 📋 **Alternative: Add Exception to Windows Defender**

If you trust the project and want to run the EXE:

1. Add an exception in Windows Defender:
   - Windows Settings → Privacy & Security → Virus & threat protection
   - Manage settings → Add exclusions
   - Choose the CyberDefense folder

2. Then run the EXE

**Note:** This is a local decision you make based on your risk assessment.

### ℹ️ **Technical: Future Solution**

Cyber Defense plans to:
- Acquire an EV code signing certificate
- Sign all released binaries
- Submit to Microsoft SmartScreen for reputation building
- Provide signed MSI installers

---

## Transparency & Verification

**Open Source for Verification:**
- ✅ Full source code on GitHub: https://github.com/DarkRX01/Real-World-Cyber-Defense
- ✅ You can review every line of code
- ✅ MIT License (completely transparent)
- ✅ No hidden code or telemetry
- ✅ Built from clean Python + standard libraries

**How Windows SmartScreen Works:**

Windows shows warnings for:
- Unsigned applications (lack of code signature)
- New applications (no reputation history)
- Any software from publishers unknown to Microsoft

**This is a safety feature**, not necessarily a reflection on the app itself.

---

## Code Signing Roadmap

Cyber Defense is committed to becoming trustworthy through:

1. **Code Signing** – EV certificate acquisition + signtool signing
2. **Reputation Building** – Microsoft SmartScreen submission
3. **Signed Packages** – MSI installers with valid signatures
4. **Transparency** – Full release notes + SHA256 checksums; **publish VirusTotal links** for each release (goal: 0 detections or heuristic-only).
5. **Security Audits** – Independent code review (future)

---

## Summary

- **Unsigned status is honest** - No pretense of security we haven't earned
- **Build from source** - The safest option (full code transparency)
- **Add exception locally** - If you audit the code and trust it
- **Wait for signing** - Once EV certificate is acquired
- **Either way** - Run Cyber Defense **alongside** Windows Defender for comprehensive protection
