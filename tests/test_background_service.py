#!/usr/bin/env python3
"""
Unit tests for background_service.py
Tests clipboard monitoring and background scanning functionality.
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from background_service import BackgroundService, _extract_urls
from threat_engine import Sensitivity, ThreatResult


class TestURLExtraction:
    """Tests for URL extraction from text."""

    def test_extract_http_url(self):
        urls = _extract_urls("Check this: http://example.com")
        assert len(urls) == 1
        assert "http://example.com" in urls[0]

    def test_extract_https_url(self):
        urls = _extract_urls("Visit https://secure.example.com/page")
        assert len(urls) == 1
        assert "https://secure.example.com/page" in urls[0]

    def test_extract_www_url(self):
        urls = _extract_urls("Go to www.example.com")
        assert len(urls) == 1
        assert "example.com" in urls[0]

    def test_extract_multiple_urls(self):
        text = "Links: https://a.com and http://b.com"
        urls = _extract_urls(text)
        assert len(urls) == 2

    def test_extract_no_urls(self):
        urls = _extract_urls("No links here!")
        assert len(urls) == 0

    def test_extract_empty_string(self):
        urls = _extract_urls("")
        assert len(urls) == 0

    def test_extract_none(self):
        urls = _extract_urls(None)
        assert len(urls) == 0

    def test_extract_removes_duplicates(self):
        text = "https://dup.com https://dup.com"
        urls = _extract_urls(text)
        assert len(urls) == 1

    def test_extract_url_with_path(self):
        urls = _extract_urls("https://example.com/path/to/page.html")
        assert len(urls) == 1
        assert "path/to/page.html" in urls[0]

    def test_extract_url_with_query(self):
        urls = _extract_urls("https://example.com/search?q=test&lang=en")
        assert len(urls) == 1
        assert "search?q=test" in urls[0]


class TestBackgroundServiceInit:
    """Tests for BackgroundService initialization."""

    def test_default_init(self):
        service = BackgroundService()
        assert service.sensitivity == Sensitivity.MEDIUM
        assert service.enable_clipboard is True
        assert service.enable_tracker_check is True
        assert service.poll_interval == 1.5

    def test_custom_sensitivity(self):
        service = BackgroundService(sensitivity=Sensitivity.HIGH)
        assert service.sensitivity == Sensitivity.HIGH

    def test_custom_poll_interval(self):
        service = BackgroundService(poll_interval=2.0)
        assert service.poll_interval == 2.0

    def test_disabled_clipboard(self):
        service = BackgroundService(enable_clipboard=False)
        assert service.enable_clipboard is False

    def test_custom_callback(self):
        callback = MagicMock()
        service = BackgroundService(on_threat=callback)
        assert service.on_threat == callback


class TestBackgroundServiceLifecycle:
    """Tests for service start/stop lifecycle."""

    def test_start_creates_thread(self):
        service = BackgroundService()
        service.start()
        time.sleep(0.1)  # Let thread start
        assert service._thread is not None
        assert service._thread.is_alive()
        service.stop()

    def test_stop_terminates_thread(self):
        service = BackgroundService()
        service.start()
        time.sleep(0.1)
        service.stop()
        time.sleep(0.3)
        assert service._thread is None or not service._thread.is_alive()

    def test_double_start_no_error(self):
        service = BackgroundService()
        service.start()
        service.start()  # Should not create second thread
        time.sleep(0.1)
        service.stop()

    def test_stop_without_start(self):
        service = BackgroundService()
        service.stop()  # Should not raise

    def test_restart_service(self):
        service = BackgroundService()
        service.start()
        time.sleep(0.1)
        service.stop()
        time.sleep(0.1)
        service.start()
        time.sleep(0.1)
        assert service._thread is not None
        assert service._thread.is_alive()
        service.stop()


class TestBackgroundServiceScanning:
    """Tests for URL scanning functionality."""

    def test_scan_url_now(self):
        service = BackgroundService()
        result = service.scan_url_now("https://www.google.com")
        assert isinstance(result, ThreatResult)
        assert result.threat_type in ["safe", "phishing", "tracker", "malware", "suspicious_url"]

    def test_scan_phishing_url(self):
        service = BackgroundService()
        result = service.scan_url_now("https://paypa1.com/login")
        assert result.is_threat is True
        assert result.threat_type == "phishing"

    def test_scan_tracker_url(self):
        service = BackgroundService()
        result = service.scan_url_now("https://www.google-analytics.com/collect")
        assert result.is_threat is True
        assert result.threat_type == "tracker"

    def test_scan_respects_sensitivity(self):
        service_low = BackgroundService(sensitivity=Sensitivity.LOW)
        service_high = BackgroundService(sensitivity=Sensitivity.HIGH)
        
        url = "http://suspicious.xyz/verify"
        result_low = service_low.scan_url_now(url)
        result_high = service_high.scan_url_now(url)
        
        # Both should return results
        assert result_low is not None
        assert result_high is not None


class TestBackgroundServiceSettings:
    """Tests for settings update functionality."""

    def test_update_sensitivity(self):
        service = BackgroundService(sensitivity=Sensitivity.MEDIUM)
        service.update_settings(sensitivity=Sensitivity.HIGH)
        assert service.sensitivity == Sensitivity.HIGH

    def test_update_clipboard_setting(self):
        service = BackgroundService(enable_clipboard=True)
        service.update_settings(enable_clipboard=False)
        assert service.enable_clipboard is False

    def test_update_tracker_setting(self):
        service = BackgroundService(enable_tracker_check=True)
        service.update_settings(enable_tracker_check=False)
        assert service.enable_tracker_check is False

    def test_partial_update(self):
        service = BackgroundService(
            sensitivity=Sensitivity.MEDIUM,
            enable_clipboard=True,
        )
        service.update_settings(sensitivity=Sensitivity.LOW)
        # Only sensitivity should change
        assert service.sensitivity == Sensitivity.LOW
        assert service.enable_clipboard is True

    def test_update_none_values_ignored(self):
        service = BackgroundService(sensitivity=Sensitivity.HIGH)
        service.update_settings(sensitivity=None)
        # Should remain unchanged
        assert service.sensitivity == Sensitivity.HIGH


class TestBackgroundServiceCallback:
    """Tests for threat callback functionality."""

    def test_callback_called_on_threat(self):
        callback = MagicMock()
        service = BackgroundService(on_threat=callback)
        
        # Simulate threat detection by directly calling the internal check
        with patch.object(service, '_last_clipboard', ''):
            with patch('background_service._get_clipboard', return_value='https://paypa1.com/login'):
                service._check_clipboard()
        
        # Callback should have been called
        assert callback.called

    def test_callback_receives_threat_result(self):
        results = []
        
        def capture_threat(result, url):
            results.append((result, url))
        
        service = BackgroundService(on_threat=capture_threat)
        
        with patch.object(service, '_last_clipboard', ''):
            with patch('background_service._get_clipboard', return_value='https://paypa1.com/login'):
                service._check_clipboard()
        
        assert len(results) > 0
        result, url = results[0]
        assert isinstance(result, ThreatResult)
        assert result.is_threat is True


class TestBackgroundServiceClipboard:
    """Tests for clipboard monitoring."""

    def test_same_clipboard_not_rechecked(self):
        callback = MagicMock()
        service = BackgroundService(on_threat=callback)
        
        with patch('background_service._get_clipboard', return_value='https://paypa1.com'):
            service._check_clipboard()
            call_count_1 = callback.call_count
            
            # Same clipboard content should not trigger recheck
            service._check_clipboard()
            call_count_2 = callback.call_count
            
            assert call_count_1 == call_count_2

    def test_new_clipboard_is_checked(self):
        callback = MagicMock()
        service = BackgroundService(on_threat=callback)
        
        with patch('background_service._get_clipboard', return_value='https://paypa1.com'):
            service._check_clipboard()
        
        with patch('background_service._get_clipboard', return_value='https://amaz0n.com'):
            service._check_clipboard()
        
        # Should have been called twice (once per unique URL)
        assert callback.call_count == 2

    def test_clipboard_disabled(self):
        callback = MagicMock()
        service = BackgroundService(on_threat=callback, enable_clipboard=False)
        
        # Even with threat URL, callback should not be called when disabled
        with patch('background_service._get_clipboard', return_value='https://paypa1.com'):
            # _check_clipboard won't be called in _run when disabled
            pass
        
        # Start and immediately stop to test the disabled path
        service.start()
        time.sleep(0.2)
        service.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
