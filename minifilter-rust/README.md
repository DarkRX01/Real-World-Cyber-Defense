# Cyber Defense Minifilter (Rust)

**Status: scaffold only.** A real minifilter requires the Windows Driver Kit (WDK), kernel build environment, and signing.

## Why minifilter?

- **File-only scanning is too late.** Malware lives in memory, registry, boot sector. Ransomware encrypts before user-mode AV can read the file.
- **Kernel-level hooks** (minifilter on Windows, eBPF on Linux) intercept file/registry operations in real time and can block or quarantine before data is written.

## What you need

1. **Windows Driver Kit (WDK)** – [Download](https://learn.microsoft.com/en-us/windows-hardware/drivers/download-the-wdk)
2. **Rust** with kernel target (e.g. custom target for `x86_64-pc-windows-msvc` kernel)
3. **windows-driver / wdk crates** – [wdk-rs](https://github.com/microsoft/wdk-rs) or manual WDK bindings
4. **EV code signing certificate** – kernel drivers must be signed; use Sectigo/DigiCert (~$80–300/year)
5. **Test signing or HVCI-compatible signing** for development

## Implementation outline

- **Driver entry:** `DriverEntry` → register minifilter with `FltRegisterFilter`.
- **Callbacks:** PreCreate, PreWrite (and optionally PostCreate/PostWrite). In PreWrite, optionally copy buffer to non-paged memory and signal user-mode service to scan; if threat, return `FLT_PREOP_COMPLETE` with status that blocks the write.
- **User-mode service:** Your Python/C# service communicates with the driver (e.g. via device IOCTL or named pipe) to receive hashes/buffers and respond with allow/block.
- **Build:** Use WDK `msbuild` or `cargo` with a kernel target; produce `.sys` and `.inf`. Sign with `signtool`. Load with `fltmc load CyberDefense`.

## Linux: eBPF

On Linux, use eBPF programs (e.g. LSM hooks or tracepoint on file open/write) to achieve similar “see before write” behavior. No WDK; use libbpf or bcc.

## References

- [WDK minifilter sample](https://github.com/microsoft/Windows-driver-samples/tree/main/filesys/minifilter)
- [wdk-rs](https://github.com/microsoft/wdk-rs)
- “Windows Kernel Programming” (Pavel Yosifovich)
