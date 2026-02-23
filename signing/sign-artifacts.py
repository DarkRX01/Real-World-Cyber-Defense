#!/usr/bin/env python3
"""
Code signing and artifact verification script for CyberDefense releases.

This script handles:
1. Signing Windows executables with Authenticode certificate
2. Generating SHA256 checksums
3. Verifying signatures
4. Creating release artifacts with checksums

Certificate Setup:
- For production: Use EV (Extended Validation) code signing certificate
- For testing: Use self-signed certificate from Windows SDK or test certificate

Usage:
    python sign-artifacts.py --exe dist/CyberDefense.exe --cert path/to/cert.pfx --password "pfx_password"
    python sign-artifacts.py --verify dist/CyberDefense.exe
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class CodeSigner:
    """Handle code signing and artifact verification."""

    def __init__(self, cert_path: Optional[str] = None, cert_password: Optional[str] = None):
        """
        Initialize code signer.

        Args:
            cert_path: Path to certificate (.pfx or .p12 file)
            cert_password: Password for certificate file
        """
        self.cert_path = cert_path
        self.cert_password = cert_password
        self.signtool_path = self._find_signtool()

    def _find_signtool(self) -> Optional[str]:
        """Find signtool.exe in Windows SDK or Visual Studio."""
        possible_paths = [
            "C:\\Program Files (x86)\\Windows Kits\\10\\bin\\x64\\signtool.exe",
            "C:\\Program Files\\Windows Kits\\10\\bin\\x64\\signtool.exe",
            "C:\\Program Files (x86)\\Windows Kits\\11\\bin\\x64\\signtool.exe",
            "C:\\Program Files\\Windows Kits\\11\\bin\\x64\\signtool.exe",
        ]

        for path in possible_paths:
            if Path(path).exists():
                return path

        try:
            result = subprocess.run(
                ["where", "signtool.exe"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass

        return None

    def sign_executable(self, exe_path: str, timestamp_server: Optional[str] = None) -> bool:
        """
        Sign an executable with Authenticode certificate.

        Args:
            exe_path: Path to .exe file
            timestamp_server: Optional timestamp server URL

        Returns:
            True if signing succeeded, False otherwise
        """
        exe_path = Path(exe_path)

        if not exe_path.exists():
            print(f"❌ ERROR: Executable not found: {exe_path}")
            return False

        if not self.cert_path or not self.cert_password:
            print("⚠️  WARNING: No certificate provided. Signing skipped.")
            print("   For production: Provide EV certificate via --cert and --password")
            return True

        if not self.signtool_path:
            print("❌ ERROR: signtool.exe not found in Windows SDK")
            print("   Install Windows SDK: https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/")
            return False

        print(f"\n📝 Signing executable: {exe_path.name}")

        cmd = [
            self.signtool_path,
            "sign",
            "/f", self.cert_path,
            "/p", self.cert_password,
            "/v",
        ]

        if timestamp_server:
            cmd.extend(["/t", timestamp_server])
        else:
            print("   ⚠️  No timestamp server specified (signature may expire)")

        cmd.append(str(exe_path))

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"✅ Successfully signed: {exe_path.name}")
                return True
            else:
                print(f"❌ Signing failed:")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"❌ Error running signtool: {e}")
            return False

    def verify_signature(self, exe_path: str) -> bool:
        """
        Verify digital signature of executable.

        Args:
            exe_path: Path to .exe file

        Returns:
            True if signature is valid, False otherwise
        """
        exe_path = Path(exe_path)

        if not exe_path.exists():
            print(f"❌ ERROR: Executable not found: {exe_path}")
            return False

        if not self.signtool_path:
            print("⚠️  WARNING: signtool.exe not found. Cannot verify signature.")
            return False

        print(f"\n🔍 Verifying signature: {exe_path.name}")

        cmd = [
            self.signtool_path,
            "verify",
            "/v",
            "/pa",
            str(exe_path)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"✅ Signature is valid")
                if "SignTool Error" not in result.stderr:
                    return True
            print(result.stderr)
            return False
        except Exception as e:
            print(f"❌ Error verifying signature: {e}")
            return False

    def generate_checksum(self, file_path: str, algorithm: str = "sha256") -> str:
        """
        Generate hash checksum for a file.

        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, sha512, md5)

        Returns:
            Hex digest of file hash
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if algorithm not in ["sha256", "sha512", "md5"]:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        hash_obj = hashlib.new(algorithm)

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def create_checksums(self, exe_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Generate SHA256 and SHA512 checksums for executable.

        Args:
            exe_path: Path to .exe file
            output_dir: Directory to save checksums (if None, uses same dir as exe)

        Returns:
            Dictionary with hash algorithm keys and checksum values
        """
        exe_path = Path(exe_path)

        if not exe_path.exists():
            print(f"❌ ERROR: Executable not found: {exe_path}")
            return {}

        if output_dir is None:
            output_dir = exe_path.parent

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📊 Generating checksums for: {exe_path.name}")

        checksums = {}
        for algo in ["sha256", "sha512"]:
            try:
                hash_value = self.generate_checksum(str(exe_path), algo)
                checksums[algo] = hash_value

                checksum_file = output_dir / f"{exe_path.stem}.{algo}"
                checksum_file.write_text(f"{hash_value}  {exe_path.name}\n")
                print(f"  {algo.upper()}: {hash_value}")
                print(f"    Saved to: {checksum_file.name}")
            except Exception as e:
                print(f"  ❌ Error generating {algo}: {e}")

        return checksums

    def create_release_manifest(
        self,
        exe_path: str,
        output_file: str = "RELEASE-MANIFEST.json",
    ) -> bool:
        """
        Create release manifest with checksums and metadata.

        Args:
            exe_path: Path to .exe file
            output_file: Output JSON manifest file

        Returns:
            True if manifest created successfully
        """
        exe_path = Path(exe_path)

        if not exe_path.exists():
            print(f"❌ ERROR: Executable not found: {exe_path}")
            return False

        try:
            checksums = self.create_checksums(str(exe_path))

            manifest = {
                "version": self._get_version(),
                "release_date": datetime.utcnow().isoformat(),
                "executable": exe_path.name,
                "executable_size": exe_path.stat().st_size,
                "checksums": checksums,
                "signature_verified": self.verify_signature(str(exe_path)),
            }

            output_path = Path(output_file)
            with open(output_path, "w") as f:
                json.dump(manifest, f, indent=2)

            print(f"\n📋 Release manifest created: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating manifest: {e}")
            return False

    def _get_version(self) -> str:
        """Get version from version_info.txt or pyproject.toml."""
        version_file = Path("version_info.txt")
        if version_file.exists():
            return version_file.read_text().strip()

        pyproject = Path("pyproject.toml")
        if pyproject.exists():
            content = pyproject.read_text()
            for line in content.split('\n'):
                if line.startswith('version ='):
                    return line.split('"')[1]

        return "unknown"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Sign and verify CyberDefense release artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sign executable with certificate
  python sign-artifacts.py --exe dist/CyberDefense.exe --cert cert.pfx --password "pass123"
  
  # Verify signature only
  python sign-artifacts.py --verify dist/CyberDefense.exe
  
  # Generate checksums
  python sign-artifacts.py --checksums dist/CyberDefense.exe
  
  # Create complete release manifest
  python sign-artifacts.py --manifest dist/CyberDefense.exe
        """
    )

    parser.add_argument("--exe", help="Path to executable to sign")
    parser.add_argument("--cert", help="Path to code signing certificate (.pfx)")
    parser.add_argument("--password", help="Certificate password")
    parser.add_argument("--timestamp", help="Timestamp server URL (default: none)")
    parser.add_argument("--verify", action="store_true", help="Verify executable signature")
    parser.add_argument("--checksums", action="store_true", help="Generate checksums only")
    parser.add_argument("--manifest", action="store_true", help="Create release manifest")
    parser.add_argument("--output", default="RELEASE-MANIFEST.json", help="Output manifest file")

    args = parser.parse_args()

    if not args.exe:
        parser.print_help()
        return 1

    signer = CodeSigner(cert_path=args.cert, cert_password=args.password)

    if args.verify:
        if signer.verify_signature(args.exe):
            return 0
        return 1

    if args.checksums:
        checksums = signer.create_checksums(args.exe)
        if checksums:
            return 0
        return 1

    if args.manifest:
        if signer.create_release_manifest(args.exe, args.output):
            return 0
        return 1

    if args.cert and args.password:
        if signer.sign_executable(args.exe, timestamp_server=args.timestamp):
            signer.verify_signature(args.exe)
            signer.create_checksums(args.exe)
            return 0
        return 1

    print("❌ ERROR: No action specified. Use --verify, --checksums, --manifest, or provide --cert and --password")
    return 1


if __name__ == "__main__":
    sys.exit(main())
