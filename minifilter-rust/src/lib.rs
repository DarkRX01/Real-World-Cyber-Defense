//! Cyber Defense minifilter driver (stub).
//!
//! Real implementation requires Windows Driver Kit (WDK), wdk-rs, and kernel build.
//! See README.md.

/// Placeholder; real driver would register a minifilter and block malicious writes.
#[cfg(windows)]
pub fn stub() -> bool {
    true
}

#[cfg(not(windows))]
pub fn stub() -> bool {
    false
}
