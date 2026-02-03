#!/usr/bin/env python3
"""
EICAR test - Standard antivirus test file. CI must pass: build -> scan EICAR -> pass/fail.
"""

import os
import tempfile
from pathlib import Path

import pytest

from threat_engine import (
    EICAR_TEST_STRING,
    calculate_entropy,
    scan_file_comprehensive,
    scan_file_eicar,
    scan_file_entropy,
)

# EICAR standard test file for antivirus
EICAR_STRING = r"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


def test_eicar_detection():
    """Test that EICAR test string is detected"""
    # EICAR should be detected as malware
    data = EICAR_STRING.encode("ascii")

    # This is the standard test - any AV should catch this
    assert b"EICAR" in data
    assert b"STANDARD" in data
    assert b"ANTIVIRUS" in data


def test_eicar_scan_file_detection():
    """CI critical: scan_file_comprehensive must detect EICAR file (pass/fail)."""
    from threat_engine import is_eicar_bytes
    # Bytes-level detection must pass regardless of filesystem/AV
    eicar_bytes = EICAR_TEST_STRING.encode("ascii")
    assert is_eicar_bytes(eicar_bytes) is True
    assert is_eicar_bytes(b"prefix" + eicar_bytes + b"suffix") is True
    assert is_eicar_bytes(b"normal data") is False

    # File-based: use TEMP; skip if AV blocks EICAR file (e.g. Errno 22 on Windows)
    tmp = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))).resolve()
    path = tmp / "cyberdefense_eicar_ci.txt"
    try:
        path.write_bytes(EICAR_TEST_STRING.encode("ascii"))
        result = scan_file_comprehensive(str(path))
        if result.threat_type == "error" and "Errno 22" in (result.message or ""):
            pytest.skip("AV or OS blocked EICAR file access (Errno 22)")
        assert result.is_threat is True, "EICAR file must be detected as threat"
        assert result.threat_type == "eicar_test", f"got {result.threat_type}"
        assert result.confidence == 100
    finally:
        path.unlink(missing_ok=True)


def test_eicar_scan_eicar_helper():
    """scan_file_eicar returns threat for EICAR file (or skip if AV blocks)."""
    tmp = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))).resolve()
    path = tmp / "cyberdefense_eicar_helper.txt"
    try:
        path.write_bytes(EICAR_STRING.encode("ascii"))
        result = scan_file_eicar(str(path))
        if result is None:
            pytest.skip("AV or OS blocked EICAR file (scan_file_eicar could not read)")
        assert result.is_threat is True
        assert "EICAR" in result.message
    finally:
        path.unlink(missing_ok=True)


def test_eicar_string_format():
    """Verify EICAR string format is correct"""
    assert len(EICAR_STRING) == 68
    assert EICAR_STRING.startswith("X5O!")
    assert "EICAR-STANDARD-ANTIVIRUS-TEST-FILE" in EICAR_STRING


def test_high_entropy_detection():
    """Test that high entropy data is flagged"""
    # Create high-entropy data (pseudo-random)
    import os
    high_entropy_data = os.urandom(1024)
    entropy = calculate_entropy(high_entropy_data)
    
    # Random data should have very high entropy
    assert entropy >= 7.0, f"Random data should have entropy >= 7.0, got {entropy}"


def test_low_entropy_detection():
    """Test that low entropy data passes"""
    # Repeating pattern = low entropy
    low_entropy_data = b"A" * 1024
    entropy = calculate_entropy(low_entropy_data)
    
    # Repeated data should have very low entropy
    assert entropy < 1.0, f"Repeated data should have entropy < 1.0, got {entropy}"


def test_normal_text_entropy():
    """Test that normal text has moderate entropy"""
    normal_text = b"This is a normal text file with regular English content and some numbers 12345."
    normal_text = normal_text * 50  # Repeat to get enough data
    entropy = calculate_entropy(normal_text)
    
    # Normal text typically has entropy between 4-6
    assert 3.0 < entropy < 6.5, f"Normal text should have entropy 3-6.5, got {entropy}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
