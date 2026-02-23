# Limitations – What Cyber Defense Cannot Catch

Short summary. For full detail see **[THREAT-MODEL.md](THREAT-MODEL.md)**.

---

## Honest list: what we cannot detect

| Category | Why not |
|----------|--------|
| **Kernel rootkits** | App is user-mode only. Kernel drivers (including the optional minifilter) are stub/not certified. No ring-0 visibility. |
| **Fileless malware** | No disk file to scan; registry/memory/WMI/PowerShell-based attacks need OS/EDR-level visibility. |
| **Living-off-the-land (LOLBins)** | Legitimate Windows binaries (PowerShell, certutil, etc.) abused; behavior may look like normal admin activity. |
| **Zero-day exploits** | No signature yet; heuristics only catch some. |
| **Custom / polymorphic malware** | New or mutating samples not in YARA/ClamAV/hash DBs. |
| **Encrypted payloads** | Until decrypted or executed, content is opaque to scanners. |
| **Supply chain attacks** | Malicious updates from trusted vendors; we scan files, not build pipelines or vendor trust. |
| **Lateral movement** | Single-host monitoring; no network-wide visibility. |

---

## What we can detect (with caveats)

- **Phishing URLs** – When in blocklists or matching heuristics (not zero-day phishing).
- **Known malware** – YARA, ClamAV, hash matching; quality depends on rule set and updates.
- **Ransomware behavior** – Honeypots, mass file changes, encryption patterns (user-mode visibility only).
- **Process injection / suspicious APIs** – User-mode hooks and heuristics; kernel-level injection not visible.
- **C2 / exfiltration** – When domains or patterns are in blocklists or heuristics.

See [THREAT-MODEL.md](THREAT-MODEL.md) for confidence levels and detection matrix.

---

## Documentation cleanup

Many `.md` files exist in this repo. Target structure:

- **Features** – What it does (README + USER-GUIDE).
- **Architecture** – [ARCHITECTURE.md](ARCHITECTURE.md).
- **Threat model** – [THREAT-MODEL.md](THREAT-MODEL.md).
- **Limitations** – This file + THREAT-MODEL.
- **FAQ** – Single merged FAQ (to be created from existing docs).

See [ROADMAP.md](ROADMAP.md) for the full documentation cleanup checklist.

---

*Last updated: February 2026*
