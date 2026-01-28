#!/usr/bin/env python3
"""
Background service for Real-World Cyber Defense.
Monitors clipboard for URLs and runs threat scans. Runs in a separate thread.
"""

import re
import threading
from typing import Callable, Optional
from urllib.parse import urlparse

from threat_engine import scan_url, Sensitivity, ThreatResult


# Basic URL pattern
URL_PATTERN = re.compile(
    r"https?://[^\s<>\"']+|(?:www\.)[^\s<>\"']+",
    re.IGNORECASE,
)


def _extract_urls(text: str) -> list:
    if not text or not isinstance(text, str):
        return []
    urls = []
    for m in URL_PATTERN.finditer(text):
        u = m.group(0).strip()
        if not u.startswith(("http://", "https://")):
            u = "https://" + u
        try:
            urlparse(u)
            urls.append(u)
        except Exception:
            pass
    return list(dict.fromkeys(urls))


def _get_clipboard() -> str:
    try:
        import pyperclip
        return (pyperclip.paste() or "").strip()
    except Exception:
        return ""


class BackgroundService:
    """
    Clipboard monitor and lightweight background scanner.
    Call start() to begin monitoring; stop() to stop.
    """

    def __init__(
        self,
        on_threat: Optional[Callable[[ThreatResult, str], None]] = None,
        sensitivity: Sensitivity = Sensitivity.MEDIUM,
        enable_clipboard: bool = True,
        enable_tracker_check: bool = True,
        poll_interval: float = 1.5,
    ):
        self.on_threat = on_threat or (lambda r, u: None)
        self.sensitivity = sensitivity
        self.enable_clipboard = enable_clipboard
        self.enable_tracker_check = enable_tracker_check
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_clipboard = ""

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                if self.enable_clipboard:
                    self._check_clipboard()
            except Exception:
                pass
            self._stop.wait(timeout=self.poll_interval)

    def _check_clipboard(self) -> None:
        raw = _get_clipboard()
        if not raw or raw == self._last_clipboard:
            return
        self._last_clipboard = raw
        urls = _extract_urls(raw)
        for url in urls:
            result = scan_url(url, self.sensitivity)
            if result.is_threat:
                self.on_threat(result, url)

    def scan_url_now(self, url: str) -> ThreatResult:
        """Synchronous scan for use from UI."""
        return scan_url(url, self.sensitivity)

    def update_settings(
        self,
        sensitivity: Optional[Sensitivity] = None,
        enable_clipboard: Optional[bool] = None,
        enable_tracker_check: Optional[bool] = None,
    ) -> None:
        if sensitivity is not None:
            self.sensitivity = sensitivity
        if enable_clipboard is not None:
            self.enable_clipboard = enable_clipboard
        if enable_tracker_check is not None:
            self.enable_tracker_check = enable_tracker_check
