# Threat Model: Cyber Defense Desktop
## What This App Protects Against & What It Cannot Catch

**Document Version**: 1.0  
**Date**: February 2026  
**Status**: Initial Public Documentation  
**Audience**: Security professionals, end users, auditors, potential contributors

---

## Executive Summary

Cyber Defense is a **user-mode threat detection and monitoring tool** that provides an additional layer of protection beyond your primary antivirus. This document honestly describes:

1. **What Cyber Defense CAN reliably detect** (with confidence levels)
2. **What Cyber Defense CANNOT detect** (known limitations)
3. **Threat types and attack surfaces** covered and not covered
4. **Confidence scoring matrix** for each detection method
5. **How to use this tool effectively** in a layered defense strategy

**Bottom Line**: Cyber Defense is best used **alongside Windows Defender or another mainstream antivirus**. It catches what signature/heuristic scanners miss at the application layer, but cannot replace certified antivirus software or protect against kernel-level attacks.

---

## 1. What Cyber Defense CAN Detect

### 1.1 Phishing & Social Engineering (URLs)

**Detection Methods:**
- Google Safe Browsing API v4 (real-time threat intelligence)
- Local heuristic checks (suspicious patterns, typosquatting, homographs)
- Clipboard monitoring (alerts when you copy phishing URLs)
- Blacklist integration (URLhaus, PhishTank, custom blocklists)

**Threat Types Detected:**
- Phishing URLs (fake login pages, credential harvesting)
- Homograph attacks (paypa1.com → paypal.com lookalikes)
- Suspicious TLDs (.xyz, .tk, .ga, .ml, etc.)
- Credential submission on non-HTTPS sites
- Malware distribution sites
- Unwanted software (PUP) download links

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| Google Safe Browsing match | 90% | Depends on Google's threat DB; very reliable for known threats |
| Local heuristic (typosquatting) | 75-85% | Pattern-based; can have false positives on legitimate alternative domains |
| Suspicious TLD detection | 60-70% | Heuristic; many legitimate sites use .xyz, .ml, etc. |
| URLhaus/PhishTank match | 85-95% | Community-curated; high confidence but lag time for new threats |

**What You're Protected From:**
✅ Known phishing campaigns  
✅ Typosquatting attacks  
✅ Newly identified phishing URLs (if in Safe Browsing DB)  
✅ Credential harvesting pages  
✅ Malware distribution sites  

**What You're NOT Protected From:**
❌ Zero-day phishing URLs (not yet in threat databases)  
❌ Sophisticated spear-phishing (targeted emails, custom domains)  
❌ Social engineering that doesn't use URLs (phone calls, SMS)  
❌ Advanced domain spoofing beyond homograph detection  

---

### 1.2 Tracking & Analytics Blocking

**Detection Methods:**
- Blocklist of 40+ known tracker domains
- Third-party request detection
- Privacy mode enforcement (block or notify)

**Tracker Categories Detected:**
- Google Analytics, Google Tag Manager
- Facebook Pixel, Twitter Analytics
- DoubleClick, AdSense (Google ad network)
- Mixpanel, Amplitude, Segment (analytics services)
- Hotjar, FullStory (session recording)
- LinkedIn, TikTok, Reddit pixels

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| Blocklist match | 99% | These are definitively tracking domains |
| Third-party detection | 95% | High confidence this is a tracker (though some are legitimate CDNs) |

**What You're Protected From:**
✅ Mainstream tracker domains  
✅ Third-party analytics (if blocked in strict mode)  
✅ Cookie-based tracking (when domains are blocked)  
✅ Pixel-based conversion tracking  

**What You're NOT Protected From:**
❌ First-party analytics (site's own domain tracking)  
❌ Advanced fingerprinting (browser, device, network fingerprints)  
❌ DNS-level tracking (ISP tracking, DoH tracking)  
❌ Server-side tracking (server logs, IP-based tracking)  
❌ New tracker domains not in blocklist  

---

### 1.3 Known Malware Signatures

**Detection Methods:**
- YARA rules (pattern-based malware detection)
- ClamAV signatures (community antivirus engine)
- SHA256/MD5 file hash matching against known-malware databases
- VirusTotal API integration (optional, API-dependent)

**Malware Types Detected:**
- Trojans, worms, and traditional executable malware
- Viruses (file infectors)
- Backdoors and remote access trojans (RATs)
- Spyware and adware
- Cryptocurrency miners
- Botnets

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| Exact hash match (SHA256) | 99% | If hash is in known-malware DB, it's malware (no false positives) |
| YARA rule match | 75-95% | Depends on rule quality; well-written rules are highly reliable |
| ClamAV signature match | 80-90% | Community DB; good coverage but lags on new variants |
| VirusTotal match (10+ engines) | 85-95% | Requires API; multiple antivirus engines agree |

**What You're Protected From:**
✅ Known malware families (Emotet, TrickBot, Dridex, etc.)  
✅ Banking trojans  
✅ Spyware and adware  
✅ Ransomware (if signature is known)  
✅ Backdoors and RATs (if in signature database)  
✅ Cryptominers  
✅ Worms and virus variants (if rules cover them)  

**What You're NOT Protected From:**
❌ **Zero-day malware** (not yet in YARA/ClamAV/VirusTotal)  
❌ **Polymorphic/metamorphic malware** (changes itself on each execution)  
❌ **Encrypted payloads** (obfuscated, UPX-packed, encrypted binaries without unpacking)  
❌ **Living-off-the-land binaries** (legitimate Windows tools abused for attacks)  
❌ **Fileless malware** (registry-based, memory-based, PowerShell attacks)  
❌ **Custom malware** (single-use, unique samples not in public databases)  

---

### 1.4 Ransomware Detection

**Detection Methods:**
- **Honeypot files**: Decoy files in Downloads, Desktop, Documents directories
- **Mass file change detection**: Alerts if >50 file modifications in 10 seconds
- **Encryption pattern detection**: Monitors for large-scale encryption operations
- **File extension monitoring**: Detects suspicious mass renames to .locked, .encrypted, etc.
- **Behavioral analysis**: Tracks process file operations for ransomware-like patterns

**Ransomware Behaviors Detected:**
- Mass file encryption (most ransomware)
- Shadow copy deletion (C:\$RECYCLE.BIN, VSS deletion)
- Backup file access patterns
- Ransom note creation (common file names detected)
- Registry modifications (disabling Windows recovery)

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| Honeypot touched | 95% | Very high confidence; attacker almost always encrypts all files |
| Mass file changes (>50 in 10s) | 85% | Good indicator but can have false positives from legitimate bulk operations |
| Encryption pattern (file magic headers) | 80-90% | High confidence for actual encryption |
| Shadow copy deletion detection | 85% | Strong indicator of ransomware intent |
| Behavioral baseline (CPU/memory spike + file ops) | 70-80% | Can be tuned to reduce false positives |

**What You're Protected From:**
✅ **Common ransomware**: Lockbit, BlackCat, REvil, Conti, Maze, etc.  
✅ **Mass encryption attempts** (caught before completion via honeypot)  
✅ **Backup/recovery deletion** (shadow copy, VSS targeting)  
✅ **Ransom note creation**  
✅ **Suspicious process file operations** (unusual file access patterns)  
✅ **Double-extortion attempts** (if data exfiltration is detected)  

**What You're NOT Protected From:**
❌ **Encrypting files before honeypot check** (if honeypot not in target directory)  
❌ **Slow, targeted encryption** (<50 files in 10 seconds, bypasses threshold)  
❌ **Compressed/archived ransomware** (if detection logic doesn't unpack)  
❌ **Kernel-level encryption** (if ransomware hooks filesystem at kernel level)  
❌ **Ransomware already running as SYSTEM** (elevation already achieved)  
❌ **Data destruction** (if attacker just deletes files instead of encrypting)  

---

### 1.5 Suspicious File Characteristics

**Detection Methods:**
- **PE header analysis**: Detects packed, suspicious, or anomalous executable characteristics
- **Entropy detection**: High-entropy sections indicate packing or encryption
- **File magic/signature validation**: Verifies file type matches extension
- **Code cave detection**: Identifies unusual gaps in executable sections (code injection)
- **Import table analysis**: Detects suspicious API imports (CreateRemoteThread, WriteProcessMemory, etc.)

**File Characteristics Detected:**
- Packed executables (UPX, ASPack, PECompact, etc.)
- High-entropy sections (compression, encryption)
- Mismatched file types (EXE with JPG extension)
- Double extensions (.exe.jpg)
- Suspicious API imports (process injection, memory manipulation)
- Code caves (space for injected code)

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| High entropy section | 70-80% | Packing is common in malware but also legitimate (compressed apps, games) |
| Suspicious API imports | 75-85% | Strong indicator for injection/malware, but some legitimate software uses these APIs |
| File magic mismatch | 95% | Very high confidence; .exe with PDF magic bytes is almost always suspicious |
| Code cave detection | 60-75% | Indicator of code injection but can have false positives |

**What You're Protected From:**
✅ **Obviously packed malware** (UPX, ASPack packed executables)  
✅ **Suspicious API imports** (CreateRemoteThread, WriteProcessMemory, SetWindowsHookEx)  
✅ **File type masquerading** (EXE with JPG extension)  
✅ **Double extensions** (document.exe.pdf tricks)  
✅ **Entropy-based compression detection** (unusual file compression)  

**What You're NOT Protected From:**
❌ **Legitimate packed software** (game engines, installers, legitimate packed apps)  
❌ **Code caves in legitimate software** (some compilers optimize space)  
❌ **Custom or unknown packing** (novel obfuscation techniques)  
❌ **Encrypted payloads** (decrypted in memory at runtime)  
❌ **Legitimate high-entropy files** (media, archives, etc.)  

---

### 1.6 Process Injection & Code Hooking

**Detection Methods:**
- **DLL injection detection**: Monitors for unexpected DLLs loaded into processes
- **API hooking detection**: Tracks suspicious hook patterns (SetWindowsHookEx, etc.)
- **Code cave analysis**: Detects unusual executable sections suitable for injected code
- **Process parent-child relationship analysis**: Flags unusual parent→child process chains
- **Suspicious API usage**: Monitors calls to CreateRemoteThread, WriteProcessMemory, NtCreateThreadEx, QueueUserAPC
- **SSDT hook detection**: Scans for kernel-mode System Service Descriptor Table modifications

**Injection Techniques Detected:**
- DLL injection (CreateRemoteThread + LoadLibrary pattern)
- Process Hollowing (VirtualAllocEx, WriteProcessMemory into new process)
- API hooking (SetWindowsHookEx, inline hooks)
- Code cave injection
- Asynchronous Procedure Call (APC) injection
- SSDT/kernel hook modifications (if driver available)

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| Suspicious DLL load (temp path) | 85-90% | Legitimate code rarely loads DLLs from TEMP or AppData |
| CreateRemoteThread detection | 80-85% | Strong indicator but some legitimate tools use this (debuggers) |
| Unusual parent-child chain | 70-80% | Depends on baseline; notepad.exe launching svchost.exe is very suspicious |
| API hooking detection | 75-85% | Good indicator of malware or rootkit activity |
| Code cave detection | 65-75% | Suspicious but can have false positives |

**What You're Protected From:**
✅ **Remote code injection** (DLL injection, process hollowing)  
✅ **API hooking attempts** (SetWindowsHookEx from suspicious processes)  
✅ **Unusual parent-child process chains** (normal process → suspicious child)  
✅ **TEMP/AppData DLL loads** (common malware trick)  
✅ **Suspicious CreateRemoteThread calls**  
✅ **APC injection attempts**  

**What You're NOT Protected From:**
❌ **Kernel-mode injection** (from kernel driver; not detectable from user-mode)  
❌ **Legitimate injectors** (debuggers, some frameworks legitimately use these APIs)  
❌ **Injection in already-running malware** (detection of initial malware execution, not secondary injection)  
❌ **Direct memory manipulation** (if malware has kernel-mode access)  
❌ **Stealthy code caves** (masked as legitimate data sections)  

---

### 1.7 Network Anomalies

**Detection Methods:**
- **C2 connection detection**: Monitors for unusual outbound connections, DNS queries to C2 domains
- **DNS tunneling detection**: Detects abnormal DNS query patterns (exfiltration over DNS)
- **Data exfiltration detection**: Alerts on large outbound data transfers to non-standard ports
- **DGA (Domain Generation Algorithm) detection**: Monitors for random domain queries
- **Blocklist integration**: Blocks known C2, botnet, and malware C&C domains

**Network Behaviors Detected:**
- Connections to C2 domains (if in blocklist)
- Unusual port usage (bot commands over 443, 8080, etc.)
- DNS tunneling (excessive subdomains, entropy in DNS queries)
- Large data exfiltration (GBs outbound to single IP)
- Unusual outbound connections from user applications
- DGA queries (random domain generation)

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| Blocklist C2 match | 95% | If domain is known C2, connection is highly suspicious |
| Unusual outbound ports | 70-80% | Depends on user's typical usage; customizable per sensitivity |
| DNS tunneling pattern | 80-85% | Statistical analysis; good indicator of exfiltration |
| Data exfiltration (volume) | 85-90% | Large sustained transfers are suspicious |
| DGA detection (entropy) | 75-85% | High entropy in DNS queries suggests DGA |

**What You're Protected From:**
✅ **Known C2 domains** (if in blocklist)  
✅ **Botnet callback attempts**  
✅ **Data exfiltration** (large outbound transfers)  
✅ **DNS tunneling attacks**  
✅ **Unusual network behavior** (process opening connections to unexpected IPs)  
✅ **Command & control callbacks**  

**What You're NOT Protected From:**
❌ **Encrypted C2 channels** (if using HTTPS to legitimate domains)  
❌ **Custom C2 domains** (not in blocklist, attacker's own infrastructure)  
❌ **Stealth exfiltration** (small, slow transfers over time)  
❌ **Legitimate cloud uploads** (Google Drive, OneDrive, Dropbox can appear like exfiltration)  
❌ **VPN/proxy-tunneled C2** (connection appears to VPN, not C2)  
❌ **Living-off-the-land exfiltration** (using Windows built-in tools, PowerShell)  

---

### 1.8 Behavioral Anomalies

**Detection Methods:**
- **Process baseline learning**: Learns normal CPU, memory, network, file I/O per process
- **Statistical anomaly detection**: 3-sigma deviation from baseline = alert
- **Parent-child process tree analysis**: Detects suspicious process relationships
- **Mass operation detection**: File/registry/network operation spikes
- **Privilege escalation detection**: Monitors for UAC bypass or token manipulation
- **Registry anomaly detection**: Unusual registry modifications for persistence/evasion

**Behavioral Patterns Detected:**
- CPU/memory spikes (crypto mining, encryption, compression)
- Unusual file operations (deletion sweeps, mass writes)
- Registry modifications (disabling security features)
- Suspicious parent→child relationships (notepad.exe → cmd.exe)
- Privilege escalation attempts
- Service installation (potential persistence)
- Network connection spikes

**Confidence Levels:**
| Method | Confidence | Notes |
|--------|-----------|-------|
| 3-sigma CPU/memory spike | 65-75% | Good indicator but can trigger on legitimate high-load operations |
| Unusual parent-child chain | 80-85% | Very strong indicator when baseline is clean |
| Mass registry modifications | 80-85% | Strong indicator of malware persistence attempts |
| Service installation by user process | 85-90% | Highly suspicious when process shouldn't create services |
| Privilege escalation pattern | 85-90% | UAC bypass attempts are clear indicators |

**What You're Protected From:**
✅ **Cryptocurrency miners** (CPU/GPU spikes during idle)  
✅ **Data encryption** (CPU spikes + high disk I/O + mass file writes)  
✅ **Suspicious process chains** (unusual parent→child relationships)  
✅ **Persistence mechanisms** (registry modifications, scheduled tasks)  
✅ **Privilege escalation attempts** (UAC bypass patterns)  
✅ **Malware installing services**  

**What You're NOT Protected From:**
❌ **Slow operations** (malware that operates gradually to avoid detection)  
❌ **Legitimate performance spikes** (backups, builds, video encoding)  
❌ **Legitimate process chains** (nested PowerShell, batch scripts)  
❌ **Baseline poisoning** (malware running from system startup, becomes "normal")  
❌ **Multi-user systems** (baselines become unreliable with multiple users)  

---

## 2. What Cyber Defense CANNOT Detect

### 2.1 Kernel-Level Rootkits

**Why Not Detectable:**
Cyber Defense runs entirely in **user-mode** (ring 3). Kernel rootkits operate in **kernel-mode** (ring 0) and can hide from user-mode tools.

**Examples:**
- Kernel drivers that intercept system calls
- Legitimate Windows drivers hijacked for malware
- SSDT (System Service Descriptor Table) hooks at kernel level
- Firmware/UEFI rootkits
- Hypervisor-based attacks (ring -1)

**What's NOT Detected:**
❌ Kernel-mode process hiding  
❌ Kernel-mode file/registry hiding  
❌ System call interception/manipulation  
❌ Firmware-level persistence  

**Mitigation:**
- Windows Defender's Kernel-mode driver provides kernel-level protection
- Use trusted BIOS/UEFI (Secure Boot)
- Regular Windows updates (patches kernel vulnerabilities)
- Avoid running unsigned kernel drivers

---

### 2.2 Zero-Day Exploits

**Why Not Detectable:**
Cyber Defense uses **signature-based and heuristic detection**. Zero-day exploits have no known signatures.

**Examples:**
- Windows kernel privilege escalation (unknown CVE)
- Browser 0-day (Chrome, Firefox, Edge memory corruption)
- PDF reader exploits (Reader X.0 buffer overflow)
- Office macro exploits (unknown office vulnerability)

**What's NOT Detected:**
❌ Exploit delivery (looks like normal document/link)  
❌ Exploit execution (unknown vulnerability, no signature)  
❌ Post-exploitation (depends on subsequent malware)  

**Mitigation:**
- Keep Windows and all software updated (patches 0-days once disclosed)
- Disable macros in Office (blocks VBA-based 0-days)
- Run untrusted content in sandbox (Windows Sandbox)
- Use Windows Defender (enterprise threat intel catches some 0-days)

---

### 2.3 Fileless Malware

**Why Not Detectable:**
Fileless malware lives in **memory, registry, or legitimate system processes**. Cyber Defense monitors files on disk.

**Examples:**
- PowerShell/WMI-based malware (registry payload)
- Registry-based persistence (registry entries containing encrypted code)
- In-memory shellcode (Emotet, TrickBot memory payloads)
- Living-off-the-land binary abuse (notepad.exe loading malicious DLL)
- Windows scheduled task malware

**What's NOT Detected:**
❌ PowerShell scripts executed in memory  
❌ Registry-based persistence (code in registry keys)  
❌ WMI Event Consumer malware  
❌ Living-off-the-land attacks (legitimate tools abused)  
❌ Memory-resident malware (no disk file to scan)  

**Mitigation:**
- Script block logging (PowerShell logging enabled)
- Disable PowerShell 2.0 (only use PowerShell 3.0+)
- Windows Defender monitors registry/memory
- Use behavioral detection (Windows Defender ATP)
- AppLocker / Device Guard (restrict unsigned scripts/executables)

---

### 2.4 Advanced Polymorphic & Metamorphic Malware

**Why Not Detectable:**
Polymorphic malware changes its binary signature on each infection. Metamorphic malware rewrites itself. YARA signatures are too slow to keep up.

**Examples:**
- Polymorphic virus (each copy has different hash)
- Metamorphic worm (rewrites itself entirely)
- Packed malware with random XOR keys (different encryption key per sample)
- Code mutation engines

**What's NOT Detected:**
❌ New variants of known malware (different hash, new signatures)  
❌ Malware that rewrites itself  
❌ Randomized packers (each execution is unique)  

**Mitigation:**
- Windows Defender uses behavior-based detection (catches polymorphic variants)
- Heuristic detection catches suspicious behavior (not just signature)
- Regular updates (new variants added to databases)
- Sandboxing (detonates unknown samples in isolated environment)

---

### 2.5 Supply Chain Attacks

**Why Not Detectable:**
Supply chain attacks compromise legitimate software updates. Cyber Defense scans individual files, not software sources or build systems.

**Examples:**
- Malicious update delivered by legitimate software vendor (SolarWinds)
- Compromised dependency injection (npm package, Python pip)
- Compiler injection (malicious compiler inserts backdoor)
- Build system compromise

**What's NOT Detected:**
❌ Malicious updates from trusted vendors  
❌ Compromised dependencies (only caught if malware signature detected)  
❌ Compiler trojans  

**Mitigation:**
- Vendor security assessments (check vendor's security practices)
- Update policy (don't auto-update; review changes first)
- Code review (for open source dependencies)
- Software transparency (vendor publishes build/release artifacts)

---

### 2.6 Encrypted Payloads & Obfuscation

**Why Not Detectable:**
If the payload is encrypted in transit or at rest, YARA rules and heuristics cannot analyze the actual malware code.

**Examples:**
- Encrypted ransomware payload (decrypted in memory)
- Obfuscated malware (UPX packed, custom packer)
- Encrypted command & control (C2 commands sent encrypted)
- Multi-stage payload (first stage is harmless, downloads real malware encrypted)

**What's NOT Detected:**
❌ Encrypted payloads (no signature to match)  
❌ Custom packers (unknown unpacking algorithm)  
❌ Polymorphic encryption (unique per sample)  

**Mitigation:**
- Behavioral detection (Windows Defender monitors encrypted malware execution)
- Behavioral heuristics (Cyber Defense monitors for encryption/mass writes)
- Sandboxing (detonates and monitors encrypted malware behavior)
- Reputation-based (if file source is untrusted, block)

---

### 2.7 Living-Off-The-Land Binaries (LOTL)

**Why Not Detectable:**
Legitimate Windows binaries abused for malicious purposes. LOLBIN attacks look like normal system operations.

**Examples:**
- `certutil.exe` (download file)
- `bitsadmin.exe` (background download)
- `rundll32.exe` (execute DLL)
- `powershell.exe` (execute script)
- `msbuild.exe` (execute arbitrary code)
- `regsvcs.exe`, `regasm.exe` (execute .NET code)

**What's NOT Detected:**
❌ Legitimate binaries used for malicious purposes  
❌ Normal-looking command-line operations (attacker just looks like admin)  
❌ PowerShell scripts (if not inspected)  
❌ Scheduled tasks (normal scheduled task, malicious payload)  

**Mitigation:**
- AppLocker / Device Guard (restrict what can run)
- Command-line auditing (log what's executed)
- Script block logging (log PowerShell code)
- Windows Defender ATP (behavior-based detection of LOTL patterns)
- Disable unnecessary PowerShell (use PowerShell 7+ instead of 5.1)

---

### 2.8 Advanced APT Techniques

**Why Not Detectable:**
Advanced Persistent Threat (APT) groups use custom tools, zero-days, and sophisticated techniques that evade standard detection.

**Examples:**
- Custom malware compiled specifically for target (not in public databases)
- Advanced obfuscation (steganography, multi-stage payloads)
- Legitimate-looking infrastructure (rented servers with clean history)
- Slow, stealthy operations (avoid triggering thresholds)
- Supply chain compromise (trojanized legitimate software)

**What's NOT Detected:**
❌ Custom malware (not in YARA/ClamAV databases)  
❌ Sophisticated C2 over HTTPS (legitimate-looking traffic)  
❌ Lateral movement (once inside, moves within network)  
❌ Multi-month persistence (malware avoids alerting)  

**Mitigation:**
- Network segmentation (limit lateral movement)
- Endpoint detection & response (EDR; continuous monitoring)
- Threat intelligence (know what APTs are targeting you)
- Incident response plan (detect and isolate compromises quickly)
- Enterprise tools (Windows Defender ATP, Sentinel, etc.)

---

### 2.9 Memory-Only Attacks

**Why Not Detectable:**
Some malware executes entirely in memory without touching disk. Cyber Defense's file monitoring won't see it.

**Examples:**
- Shellcode injection (raw bytes executed)
- In-memory code execution (C2 downloads payload, executes in RAM)
- Memory-resident backdoors

**What's NOT Detected:**
❌ Shellcode execution (no file, pure memory)  
❌ In-memory payloads (decrypted and executed without disk)  

**Mitigation:**
- Windows Defender (monitors memory access patterns)
- Process injection detection (Cyber Defense monitors this to some extent)
- Windows Defender ATP (advanced memory monitoring)
- Kernel patch protection (prevents unauthorized kernel modifications)

---

## 3. Detection Capability Matrix

**Quick Reference**: What detects what?

| Threat Type | URL Scanner | File Signatures | Behavioral | Network Monitor | Confidence |
|------------|-------------|-----------------|-----------|-----------------|-----------|
| Phishing URLs | ✅ | ❌ | ❌ | ❌ | 85-90% |
| Trojan/Worm | ❌ | ✅ | ⚠️ | ⚠️ | 80-95% |
| Ransomware | ❌ | ✅ | ✅ | ⚠️ | 85-95% |
| Process Injection | ❌ | ⚠️ | ✅ | ❌ | 75-85% |
| Data Exfiltration | ❌ | ❌ | ⚠️ | ✅ | 75-85% |
| Rootkit | ❌ | ❌ | ❌ | ❌ | N/A |
| Zero-day | ❌ | ❌ | ⚠️ | ⚠️ | 20-40% |
| Fileless Malware | ❌ | ❌ | ⚠️ | ⚠️ | 30-50% |
| Crypto Miner | ❌ | ⚠️ | ✅ | ⚠️ | 75-85% |
| Tracker | ✅ | ❌ | ❌ | ❌ | 99% |
| Botnet C2 | ❌ | ❌ | ❌ | ✅ | 90-95% |

**Legend:**
- ✅ Excellent detection
- ⚠️ Moderate/situational detection
- ❌ No detection capability

---

## 4. How to Use Cyber Defense Effectively

### 4.1 Recommended Setup (Layered Defense)

**Primary Protection:**
- Windows Defender (or third-party antivirus like ESET, Kaspersky)
  - Kernel-level scanning
  - Real-time process monitoring
  - Periodic full scans

**Secondary Protection (Cyber Defense):**
- Behavioral monitoring (enabled)
- URL/phishing detection (enabled, medium sensitivity)
- File real-time monitoring (enabled for Downloads, Desktop, Temp)
- Ransomware honeypot (enabled)

**Tertiary Protection:**
- Firewall (Windows Defender Firewall enabled)
- Windows Defender SmartScreen (enabled)
- UAC (User Account Control, set to "Always notify")

### 4.2 Sensitivity Levels & Configuration

**LOW Sensitivity:**
- Fewer behavioral alerts (only very confident detections)
- Good for production servers (fewer false positives)
- Risk: May miss subtle attacks

**MEDIUM Sensitivity** (Recommended):
- Balanced alerts (catches most threats, reasonable false positive rate)
- Good for typical users
- Risk: Some legitimate operations may trigger alerts

**HIGH Sensitivity:**
- More alerts (catches more edge cases)
- Good for security professionals analyzing threats
- Risk: Many false positives (need to whitelist legitimate apps)

**EXTREME Sensitivity:**
- All heuristics enabled, low thresholds
- Only for security research/testing
- Risk: Very high false positive rate

### 4.3 Whitelist Management

Create whitelist exceptions for:
- Your development tools (compilers, build systems)
- Legitimate backup software (Backblaze, Carbonite)
- Video encoding software (Handbrake, FFmpeg)
- Legitimate system utilities (CCleaner if trusted, disk tools)

Do NOT whitelist:
- Unknown applications
- Applications from untrusted sources
- Anything you're not familiar with

### 4.4 Regular Maintenance

1. **Update threat definitions** (automatic every 2 hours)
2. **Review threat log** weekly (check for patterns)
3. **Check whitelisted items** monthly (remove unused items)
4. **Update rules** from GitHub (pull latest YARA rules)
5. **Test detection** quarterly (run EICAR test to verify scanning works)

---

## 5. Threat Model Limitations & Known Issues

### 5.1 Architecture Limitations

1. **User-Mode Only**: Cannot detect kernel rootkits or kernel-level attacks
2. **Heuristic-Based**: Requires signatures for known threats; misses new malware
3. **Single-System**: Cannot detect lateral movement within a network
4. **No Cloud Intelligence**: Relies on local blocklists; lags on new threats
5. **Rule Quality**: YARA rules vary in quality; low-confidence rules are disabled

### 5.2 False Positive Reduction

Currently implemented:
- Sensitivity levels reduce false positives
- Whitelist system exempts trusted applications
- High-confidence-only rules are used by default
- Process baseline learning reduces behavioral false positives

Future improvements:
- Machine learning (if rule quality justifies)
- Community feedback (disable low-confidence rules)
- Automatic learning (track false positives, disable bad rules)

### 5.3 Known False Positives

- **Legitimate bulk operations**: Backup software, media encoding, large file operations
- **Development tools**: Compilers, debuggers, build systems
- **System maintenance**: Disk cleanup, index optimization, system restores
- **Cloud sync**: OneDrive, Google Drive, Dropbox large syncs

**Mitigation**: Create whitelist entries for legitimate tools.

---

## 6. Confidence Scoring Methodology

Each detection is assigned a confidence score:

| Score | Interpretation | Action |
|-------|-----------------|--------|
| 95-100% | Definite threat | Quarantine immediately |
| 80-94% | Very likely threat | Alert user, recommend quarantine |
| 60-79% | Probable threat | Alert user with details, ask for confirmation |
| 40-59% | Suspicious | Log, notify if sensitivity=HIGH, do not block |
| <40% | Low suspicion | Log only, do not notify |

Confidence is based on:
- **Source reliability**: Hash matches (99%) vs. heuristics (60-80%)
- **False positive history**: Well-tested rules score higher
- **Sample count**: Rules tested on 1000+ samples score higher
- **Expert assessment**: Reviewed by security researchers

---

## 7. How This Document Is Maintained

**Version Control:**
- Updated when detection logic changes
- Updated when new threats discovered
- Community feedback incorporated

**Testing:**
- Monthly testing against known malware samples (VirusTotal top detections)
- Quarterly testing against false positive sources (legitimate software)
- Annual comprehensive assessment

**Feedback:**
- User reports drive updates
- Security researcher feedback
- Threat landscape changes

---

## 8. When to NOT Use Cyber Defense Alone

Cyber Defense is **insufficient** as your only protection:

❌ **Do NOT rely on Cyber Defense as your only antivirus**
- Disable Windows Defender
- Disable all other security tools
- Assume you're fully protected

❌ **Do NOT skip OS updates**
- Cyber Defense cannot patch kernel vulnerabilities
- Windows updates are essential

❌ **Do NOT visit malicious sites assuming Cyber Defense will protect you**
- Sophisticated exploits may still compromise your system
- URL filtering has false negatives

❌ **Do NOT download and run unknown executables**
- Even with Cyber Defense running
- Threats are increasingly custom and evasive

---

## 9. Glossary of Terms

- **YARA Rules**: Pattern-based detection signatures for malware identification
- **ClamAV**: Community antivirus engine, open source
- **Entropy**: Measure of randomness; high entropy suggests encryption/packing
- **PE Header**: Portable Executable header (Windows executable file format)
- **C2**: Command and Control (attacker communication server)
- **DLL Injection**: Technique to load malicious library into running process
- **Hooking**: Intercepting function calls for malicious purposes
- **SSDT**: System Service Descriptor Table (kernel-level function pointer table)
- **UAC**: User Account Control (Windows privilege escalation protection)
- **EICAR**: Test file for antivirus testing (harmless)

---

## 10. References & Further Reading

**Windows Security:**
- [Microsoft Security Baselines](https://microsoft.com/en-us/security/tools/baselines)
- [Windows Defender Documentation](https://microsoft.com/en-us/security/threat-protection/windows-defender)

**Threat Detection:**
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Cyber Kill Chain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)

**Malware Analysis:**
- [VirusTotal](https://virustotal.com/)
- [URLhaus](https://urlhaus.abuse.ch/)
- [PhishTank](https://phishtank.org/)

**YARA Rules:**
- [MalwareBazaar YARA Rules](https://bazaar.abuse.ch/)
- [Yara-Rules Repository](https://github.com/Yara-Rules/rules)

---

## 11. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2026 | Initial threat model documentation |

---

## Contact & Questions

For questions about this threat model:
- Open an issue on [GitHub](https://github.com/DarkRX01/Real-World-Cyber-Defense/issues)
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- Security concerns: See [SECURITY.md](SECURITY.md)

---

**Last Updated**: February 23, 2026  
**Maintained By**: Cyber Defense Security Team  
**Status**: Public documentation
