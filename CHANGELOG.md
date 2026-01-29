# Changelog

All notable changes to the Real-World Cyber Defense project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive unit test suite with pytest
- Linux CI/CD workflow with GitHub Actions
- Modern Python packaging with pyproject.toml
- Development dependencies and linting configuration
- File-based logging for debugging

### Changed
- Updated documentation for desktop application
- Improved error handling throughout codebase

## [2.0.0] - 2026-01-29

### Added
- **Desktop Application** - Full PyQt5 GUI application for Windows and Linux
- **Real-time URL Scanning** - Automatic detection of malicious URLs
- **Phishing Detection** - Machine learning-powered phishing analysis
  - Lookalike domain detection (paypa1.com, amaz0n.com, etc.)
  - Suspicious TLD flagging (.xyz, .tk, etc.)
  - IP-based URL detection
  - Keyword-based urgency detection
- **Tracker Blocking** - Blocks 25+ known tracking domains
  - Google Analytics
  - Facebook Pixel
  - Hotjar
  - Mixpanel
  - And many more
- **Download Protection** - Scans files for dangerous extensions
  - Executable detection (.exe, .dll, .scr, etc.)
  - Script detection (.bat, .ps1, .vbs, etc.)
  - Large file warnings
- **System Security Checks** - Windows security status verification
  - Firewall status check
  - Windows Defender status check
  - Security recommendations
- **Clipboard Monitoring** - Automatic scanning of copied URLs
- **System Tray Integration** - Background monitoring with tray icon
- **Customizable Settings**
  - 4 sensitivity levels (Low, Medium, High, Extreme)
  - Feature toggles for each protection type
  - Notification preferences
- **Threat Logging** - Persistent threat history with export
- **Cross-Platform Support** - Windows 10/11 and major Linux distributions

### Technical
- Python 3.9+ support
- PyQt5-based modern GUI
- Background service architecture
- Local-only processing (no cloud dependencies)
- MIT License

## [1.0.0] - 2025-06-15

### Added
- Initial release as desktop security application
- Basic URL scanning functionality
- Simple phishing detection
- Tracker blocking (basic list)
- Windows support

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 2.0.0 | 2026-01-29 | Full desktop app, cross-platform, advanced detection |
| 1.0.0 | 2025-06-15 | Initial release |

---

## Upgrade Notes

### From 1.x to 2.0

Version 2.0 is a complete rewrite with a new GUI framework. To upgrade:

1. Uninstall the old version (if applicable)
2. Download the new release from GitHub
3. Run the installer or extract the portable version
4. Your settings will need to be reconfigured

### Fresh Install

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

---

## Security Advisories

No security vulnerabilities have been reported for this project.

If you discover a security issue, please report it privately via the process described in [SECURITY.md](SECURITY.md).

---

[Unreleased]: https://github.com/DarkRX01/Real-World-Cyber-Defense/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/DarkRX01/Real-World-Cyber-Defense/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/DarkRX01/Real-World-Cyber-Defense/releases/tag/v1.0.0
