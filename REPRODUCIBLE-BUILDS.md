# Reproducible Builds & Code Signing

This document explains how CyberDefense ensures build reproducibility and implements code signing for released binaries.

## Overview

**Reproducible builds** mean that building CyberDefense from the same source code and environment will produce bit-for-bit identical binaries. This allows users and security researchers to independently verify that released executables match the published source code.

**Code signing** adds a digital signature to the executable, verifying the publisher's identity and integrity of the binary.

## Build Environment & Requirements

### Official Build Environment
- **OS**: Windows 10/11 with latest updates
- **Python**: 3.11.x (exact version specified below)
- **SDK**: Windows SDK 10.0.22621 or later
- **Tools**:
  - PyInstaller 6.0.0 or later
  - Git (for version control)

### Reproducibility Pinning

All dependencies must be pinned to exact versions in `requirements.txt`:

```
PyQt5==5.15.9
requests==2.31.0
pyperclip==1.8.2
psutil==5.9.5
watchdog==3.0.0
pytest-cov==4.0.0
```

### Python Version Verification

Verify your Python version before building:
```powershell
python --version
# Expected: Python 3.11.x
```

### PyInstaller Version

Reproducible builds require consistent PyInstaller behavior:
```powershell
pip install pyinstaller==6.0.0
```

## Building from Source

### Prerequisites
1. Clone the repository:
   ```bash
   git clone https://github.com/DarkRX01/Real-World-Cyber-Defense.git
   cd cyber-defense-extension
   ```

2. Create a clean Python environment:
   ```powershell
   python -m venv build-env
   .\build-env\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   pip install pyinstaller==6.0.0
   ```

### Building the Executable

Use the provided build script with deterministic settings:

```powershell
python build-safe-exe.py
```

This script is configured for reproducibility:
- Deterministic timestamps (from git commit time when available)
- No UPX compression (adds non-determinism)
- No external data bundling
- Consistent spec file settings

### Build Output

The executable is created at:
```
dist/CyberDefense/CyberDefense.exe
```

## Verifying Your Build

### Step 1: Calculate Checksums

After building, generate checksums:

```powershell
# SHA256 (primary verification method)
certutil -hashfile dist/CyberDefense/CyberDefense.exe SHA256

# SHA512 (additional verification)
certutil -hashfile dist/CyberDefense/CyberDefense.exe SHA512
```

### Step 2: Compare with Published Checksums

Download the release artifacts from GitHub:
1. Go to https://github.com/DarkRX01/Real-World-Cyber-Defense/releases
2. Find your version tag (e.g., `v2.1.0`)
3. Download `RELEASE-MANIFEST.json` or `CyberDefense.exe.sha256`

Compare your checksums:
```powershell
# View published checksum
Get-Content CyberDefense.exe.sha256

# Your calculated checksum should match exactly
```

### Step 3: Verify Signature (Signed Releases Only)

For signed releases, verify the digital signature:

```powershell
# Check signature details
Get-AuthenticodeSignature dist/CyberDefense/CyberDefense.exe | Format-List

# Expected output includes:
# - SignerCertificate with valid issuer
# - Status: Valid (or UnknownError on first run if certificate not trusted)
```

## Code Signing

### For Users (Verifying Signatures)

Released executables are signed with an Authenticode certificate. Windows SmartScreen and signature verification tools can confirm:

```powershell
# Verify signature via PowerShell
$sig = Get-AuthenticodeSignature "CyberDefense.exe"
if ($sig.Status -eq "Valid") {
    Write-Host "✅ Signature is valid"
    Write-Host "Signed by: $($sig.SignerCertificate.Subject)"
}
```

### For Developers (Signing Releases)

#### Setting Up Code Signing

1. **Obtain a certificate**:
   - For production: EV (Extended Validation) code signing certificate from a trusted CA
   - For testing: Self-signed certificate or Windows SDK test certificate

2. **Store certificate securely**:
   - Export as `.pfx` file with strong password
   - For GitHub Actions: Add as repository secrets (see below)

#### GitHub Actions Setup

To enable automatic code signing on releases:

1. **Add repository secrets**:
   - Go to Settings → Secrets and variables → Actions
   - Add `CODE_SIGNING_CERT`: Base64-encoded `.pfx` file
   - Add `CODE_SIGNING_PASSWORD`: Certificate password

2. **Encode certificate**:
   ```powershell
   $certBytes = Get-Content "path/to/cert.pfx" -Encoding Byte
   $certBase64 = [Convert]::ToBase64String($certBytes)
   # Copy $certBase64 to repository secret
   ```

3. **Trigger signing**:
   - Push a git tag: `git tag v2.1.0 && git push origin v2.1.0`
   - GitHub Actions workflow `build-signed.yml` will automatically:
     - Build the executable
     - Sign it with the certificate
     - Verify the signature
     - Generate checksums
     - Create a GitHub Release with all artifacts

#### Manual Signing

For local signing or testing:

```powershell
# Sign an executable
python signing/sign-artifacts.py --exe dist/CyberDefense/CyberDefense.exe `
  --cert path/to/cert.pfx --password "your_password"

# Verify signature
python signing/sign-artifacts.py --verify dist/CyberDefense/CyberDefense.exe

# Generate checksums only
python signing/sign-artifacts.py --checksums dist/CyberDefense/CyberDefense.exe

# Create release manifest
python signing/sign-artifacts.py --manifest dist/CyberDefense/CyberDefense.exe
```

## Release Workflow

### Automated Release Process

When a tag is pushed:

1. GitHub Actions triggers `build-signed.yml` workflow
2. Builds executable with deterministic settings
3. Generates SHA256 and SHA512 checksums
4. Signs executable (if certificate available)
5. Verifies signature
6. Creates `RELEASE-MANIFEST.json` with metadata
7. Packages everything into a ZIP file
8. Creates GitHub Release with all artifacts
9. Stores artifacts for 90 days

### Release Artifacts

Each release includes:
- `CyberDefense.exe` - Main executable
- `CyberDefense.exe.sha256` - SHA256 checksum
- `CyberDefense.exe.sha512` - SHA512 checksum
- `RELEASE-MANIFEST.json` - Complete build metadata
- `CyberDefense-VERSION-Windows.zip` - Portable distribution

### Release Manifest Format

`RELEASE-MANIFEST.json` contains:
```json
{
  "version": "2.1.0",
  "release_date": "2026-02-23T12:34:56.789000",
  "executable": "CyberDefense.exe",
  "executable_size": 38456789,
  "checksums": {
    "sha256": "abc123...",
    "sha512": "def456..."
  },
  "signature_verified": true
}
```

## Troubleshooting

### Checksums Don't Match

1. **Verify Python version**: Must be exactly 3.11.x
   ```powershell
   python --version
   ```

2. **Verify dependencies**: Reinstall exact versions
   ```powershell
   pip install -r requirements.txt --force-reinstall
   ```

3. **Clean build directory**:
   ```powershell
   Remove-Item -Recurse -Force build/
   Remove-Item -Recurse -Force dist/
   python build-safe-exe.py
   ```

4. **Check for modifications**: Ensure no files were modified after git checkout
   ```powershell
   git status
   ```

### Signature Verification Fails

1. **Verify signtool.exe exists**:
   ```powershell
   where signtool.exe
   ```
   If not found, install Windows SDK

2. **Check certificate validity**:
   ```powershell
   certutil -repairstore My "Certificate Thumbprint"
   ```

3. **Verify certificate isn't expired**:
   - Check Windows SDK certificate store
   - Re-import test certificates if needed

### SmartScreen Still Warns

Initial releases may trigger SmartScreen warnings even if signed:

1. **SmartScreen reputation building**: Microsoft monitors downloads and signatures to build reputation
2. **Request official review**: File for SmartScreen review at https://www.microsoft.com/en-us/wdsi/filesubmission
3. **User reassurance**:
   - Publish checksums and signatures
   - Provide GitHub links to verified source code
   - Explain signature verification steps

## Security Considerations

1. **Never distribute unsigned binaries from official releases**
2. **Always use HTTPS** for downloads
3. **Publish checksums** on multiple channels (GitHub, website, forum)
4. **Rotate certificates** as needed (especially test certificates)
5. **Keep secrets secure**: Never commit `.pfx` files or passwords to Git
6. **Automate signing**: Use CI/CD to prevent manual errors

## Resources

- [Microsoft Authenticode Documentation](https://docs.microsoft.com/en-us/windows/win32/seccrypto/authenticode)
- [PyInstaller Reproducible Builds](https://pyinstaller.org/en/stable/advanced-topics.html#building-reproducible-packages)
- [Reproducible Builds Project](https://reproducible-builds.org/)
- [Windows Defender SmartScreen](https://docs.microsoft.com/en-us/windows/security/threat-protection/microsoft-defender-smartscreen/microsoft-defender-smartscreen-overview)

## Version History

- **v2.1.0** (2026-02-23): Initial reproducible builds documentation
