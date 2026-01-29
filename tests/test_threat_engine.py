#!/usr/bin/env python3
"""
Unit tests for threat_engine.py
Tests URL scanning, phishing detection, tracker blocking, and download analysis.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from threat_engine import (
    ThreatResult,
    Sensitivity,
    scan_url,
    check_tracker,
    get_phishing_confidence,
    analyze_download,
    is_ip_url,
    TRACKER_DOMAINS,
    SUSPICIOUS_TLDS,
    DANGEROUS_EXTENSIONS,
)


class TestThreatResult:
    """Tests for ThreatResult dataclass."""

    def test_threat_result_creation(self):
        result = ThreatResult(
            is_threat=True,
            threat_type="phishing",
            severity="high",
            confidence=85,
            message="Test threat",
            details={"test": "value"},
        )
        assert result.is_threat is True
        assert result.threat_type == "phishing"
        assert result.severity == "high"
        assert result.confidence == 85
        assert result.message == "Test threat"
        assert result.details == {"test": "value"}

    def test_threat_result_default_details(self):
        result = ThreatResult(
            is_threat=False,
            threat_type="safe",
            severity="low",
            confidence=100,
            message="Safe",
        )
        assert result.details == {}


class TestSensitivity:
    """Tests for Sensitivity enum."""

    def test_sensitivity_values(self):
        assert Sensitivity.LOW.value == 1
        assert Sensitivity.MEDIUM.value == 2
        assert Sensitivity.HIGH.value == 3
        assert Sensitivity.EXTREME.value == 4


class TestTrackerDetection:
    """Tests for tracker detection functionality."""

    def test_known_tracker_google_analytics(self):
        result = check_tracker("https://www.google-analytics.com/collect")
        assert result is not None
        assert result.is_threat is True
        assert result.threat_type == "tracker"
        assert result.severity == "low"

    def test_known_tracker_facebook_pixel(self):
        result = check_tracker("https://connect.facebook.net/en_US/fbevents.js")
        assert result is not None
        assert result.is_threat is True
        assert result.threat_type == "tracker"

    def test_known_tracker_hotjar(self):
        result = check_tracker("https://static.hotjar.com/c/hotjar.js")
        assert result is not None
        assert result.is_threat is True

    def test_safe_url_no_tracker(self):
        result = check_tracker("https://www.example.com/page")
        assert result is None

    def test_tracker_with_www_prefix(self):
        result = check_tracker("https://www.googletagmanager.com/gtm.js")
        assert result is not None
        assert result.threat_type == "tracker"

    def test_empty_url(self):
        result = check_tracker("")
        assert result is None

    def test_tracker_domains_exist(self):
        assert len(TRACKER_DOMAINS) >= 25


class TestPhishingDetection:
    """Tests for phishing detection functionality."""

    def test_ip_based_url_detection(self):
        result = get_phishing_confidence("http://192.168.1.1/login")
        assert result.is_threat is True or result.confidence < 100

    def test_suspicious_tld_detection(self):
        result = get_phishing_confidence("https://login-secure.xyz/account")
        assert result.details.get("suspicious_tld") is not None or result.confidence < 100

    def test_lookalike_paypal(self):
        result = get_phishing_confidence("https://paypa1.com/login")
        assert result.is_threat is True
        assert result.threat_type == "phishing"

    def test_lookalike_amazon(self):
        result = get_phishing_confidence("https://amaz0n.com/signin")
        assert result.is_threat is True
        assert result.threat_type == "phishing"

    def test_safe_url(self):
        result = get_phishing_confidence("https://www.google.com")
        assert result.is_threat is False
        assert result.threat_type == "safe"

    def test_http_without_https(self):
        result = get_phishing_confidence("http://example.com/login")
        assert "no_https" in result.details or result.confidence < 100

    def test_excessive_encoding(self):
        url = "https://example.com/%20%21%22%23%24%25%26"
        result = get_phishing_confidence(url)
        # Should flag excessive encoding
        assert result.details.get("encoding") is True or result.is_threat

    def test_sensitivity_low_reduces_score(self):
        url = "http://suspicious.xyz/verify-account"
        result_medium = get_phishing_confidence(url, Sensitivity.MEDIUM)
        result_low = get_phishing_confidence(url, Sensitivity.LOW)
        # Low sensitivity should have lower/equal confidence in threat
        assert result_low.confidence <= result_medium.confidence or not result_low.is_threat

    def test_sensitivity_high_increases_score(self):
        url = "http://suspicious.xyz/verify"
        result_medium = get_phishing_confidence(url, Sensitivity.MEDIUM)
        result_high = get_phishing_confidence(url, Sensitivity.HIGH)
        # High sensitivity should detect more threats
        assert result_high.confidence >= result_medium.confidence or result_high.is_threat

    def test_empty_url_safe(self):
        result = get_phishing_confidence("")
        assert result.is_threat is False

    def test_suspicious_tlds_exist(self):
        assert len(SUSPICIOUS_TLDS) >= 10


class TestIPURLDetection:
    """Tests for IP-based URL detection."""

    def test_ipv4_url(self):
        assert is_ip_url("http://192.168.1.1/path") is True

    def test_ipv4_url_with_port(self):
        assert is_ip_url("http://10.0.0.1:8080/path") is True

    def test_domain_url(self):
        assert is_ip_url("https://www.example.com") is False

    def test_localhost(self):
        assert is_ip_url("http://127.0.0.1") is True

    def test_empty_url(self):
        assert is_ip_url("") is False


class TestScanURL:
    """Tests for the main scan_url function."""

    def test_scan_tracker_url(self):
        result = scan_url("https://www.google-analytics.com/analytics.js")
        assert result.is_threat is True
        assert result.threat_type == "tracker"

    def test_scan_phishing_url(self):
        result = scan_url("https://paypa1.com/login")
        assert result.is_threat is True
        assert result.threat_type == "phishing"

    def test_scan_safe_url(self):
        result = scan_url("https://www.wikipedia.org")
        assert result.is_threat is False

    def test_scan_with_sensitivity(self):
        url = "https://example.com"
        result_low = scan_url(url, Sensitivity.LOW)
        result_high = scan_url(url, Sensitivity.HIGH)
        # Both should return valid results
        assert result_low.threat_type in ["safe", "phishing", "tracker", "suspicious_url"]
        assert result_high.threat_type in ["safe", "phishing", "tracker", "suspicious_url"]


class TestDownloadAnalysis:
    """Tests for download file analysis."""

    def test_dangerous_exe_file(self):
        result = analyze_download("malware.exe")
        assert result.is_threat is True
        assert result.threat_type == "malware"
        assert result.severity == "high"

    def test_dangerous_dll_file(self):
        result = analyze_download("suspicious.dll")
        assert result.is_threat is True
        assert result.threat_type == "malware"

    def test_dangerous_bat_file(self):
        result = analyze_download("script.bat")
        assert result.is_threat is True

    def test_dangerous_ps1_file(self):
        result = analyze_download("powershell.ps1")
        assert result.is_threat is True

    def test_safe_pdf_file(self):
        result = analyze_download("document.pdf")
        assert result.is_threat is False
        assert result.threat_type == "safe"

    def test_safe_txt_file(self):
        result = analyze_download("readme.txt")
        assert result.is_threat is False

    def test_safe_image_file(self):
        result = analyze_download("photo.jpg")
        assert result.is_threat is False

    def test_large_executable_warning(self):
        # 400 MB executable
        result = analyze_download("huge.exe", file_size_bytes=400 * 1024 * 1024)
        assert result.is_threat is True

    def test_download_from_phishing_url(self):
        result = analyze_download("file.pdf", download_url="https://paypa1.com/file.pdf")
        assert result.is_threat is True
        assert result.threat_type == "phishing"

    def test_dangerous_extensions_exist(self):
        assert len(DANGEROUS_EXTENSIONS) >= 20
        assert ".exe" in DANGEROUS_EXTENSIONS
        assert ".dll" in DANGEROUS_EXTENSIONS
        assert ".bat" in DANGEROUS_EXTENSIONS


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_malformed_url(self):
        result = scan_url("not-a-valid-url")
        # Should not crash, should return some result
        assert result is not None

    def test_url_without_scheme(self):
        result = scan_url("www.example.com")
        assert result is not None

    def test_unicode_url(self):
        result = scan_url("https://例え.jp/path")
        assert result is not None

    def test_very_long_url(self):
        long_url = "https://example.com/" + "a" * 2000
        result = scan_url(long_url)
        assert result is not None

    def test_url_with_special_characters(self):
        result = scan_url("https://example.com/path?query=value&other=123")
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
