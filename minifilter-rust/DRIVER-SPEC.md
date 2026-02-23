# Minifilter Driver Specification (Intended)

**Status:** The minifilter in this repo is a **stub only**. Production Cyber Defense runs **user-mode only** ([ARCHITECTURE.md](../ARCHITECTURE.md)). This document describes the **intended** specification for a future kernel minifilter, for documentation, HLK/certification, or replacement by safer alternatives.

---

## 1. Purpose

- **If implemented:** Intercept file I/O in kernel to allow scan-before-write (e.g. block ransomware writes before they hit disk).
- **If not implemented:** Use **FileSystemWatcher + ETW** (user-mode) for monitoring; no kernel driver required.

---

## 2. IRP Operations (Planned)

| IRP / callback   | Role |
|------------------|------|
| **PreCreate**    | Optional: notify user-mode on new file create for early path checks. |
| **PreWrite**     | Primary: buffer/file path sent to user-mode service; if threat, complete with status that blocks the write. |
| **PostCreate**   | Optional: log only. |
| **PostWrite**    | Optional: log only. |

No other IRPs required for the minimal “scan before write” design. No raw volume or disk access.

---

## 3. Filter Altitude

- **Planned altitude:** Use a **Microsoft-assigned minifilter altitude** from the [Altitude Request](https://learn.microsoft.com/en-us/windows-hardware/drivers/ifs/allocated-altitudes) range for antivirus/security filters (e.g. 320000–329999 or as assigned).
- **Exact value:** To be set at implementation time and documented in this file and in the driver INF.

---

## 4. User-Mode Communication

- **Method:** Device control (IOCTL) or named pipe to the Cyber Defense user-mode service (Python/C#).
- **Flow:** Driver sends buffer/path in PreWrite → user-mode scans (YARA/hash/etc.) → responds allow/block → driver completes IRP accordingly.
- **No kernel-side scanning:** All signature/heuristic logic stays in user-mode to reduce driver attack surface and simplify certification.

---

## 5. Reproducible Build

- Build with **deterministic** toolchain (fixed Rust/WDK versions, no timestamps in binary).
- Produce **single .sys + .inf**; no unsigned or test-signed drivers in release.

---

## 6. Certification & Signing

- **Kernel driver:** Must be **signed** (EV or Microsoft-compliant Authenticode). Unsigned minifilter + “bypass SmartScreen” instructions = unacceptable.
- **HLK:** If the driver is shipped, it must pass **Windows Hardware Lab Kit (HLK)** and Windows Hardware Certification, or be **removed** from the product.
- **Alternative:** Prefer **no kernel driver** and rely on **FileSystemWatcher + ETW** for monitoring if certification is not realistic.

---

## 7. References

- [minifilter-rust/README.md](README.md) – WDK, wdk-rs, build outline.
- [ARCHITECTURE.md](../ARCHITECTURE.md) – Current user-mode-only design.
- [ROADMAP.md](../ROADMAP.md) – Driver hardening checklist.

---

*Last updated: February 2026*
