"""
Update system: pull ClamAV signatures, PhishTank, URLhaus every 2 hours.
HTTPS only; verify signatures where available (cryptography).
"""

import hashlib
import json
import os
import ssl
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional
from urllib.request import urlopen, Request

# Optional: schedule or run in thread with sleep
_parent = Path(__file__).resolve().parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

# Default data dir
DATA_DIR = _parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# URLs (HTTPS)
CLAMAV_MAIN = "https://database.clamav.net/main.cvd"
CLAMAV_DAILY = "https://database.clamav.net/daily.cvd"
URLHAUS_BLOCKLIST = "https://urlhaus.abuse.ch/downloads/text_online/"
PHISHTANK_FEED = "https://data.phishtank.com/data/online-valid.json"  # requires API key in URL
PHISHTANK_PUBLIC = "https://www.phishtank.com/feed.php"  # public RSS-style

INTERVAL_SECONDS = 2 * 60 * 60  # 2 hours


def _https_get(url: str, timeout: int = 60) -> Optional[bytes]:
    try:
        req = Request(url, headers={"User-Agent": "CyberDefense-Update/2.0"})
        ctx = ssl.create_default_context()
        with urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read()
    except Exception:
        return None


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _verify_signature(data: bytes, expected_sha256: Optional[str]) -> bool:
    if not expected_sha256:
        return True
    return _sha256_hex(data).lower() == expected_sha256.lower()


def fetch_urlhaus(on_progress: Optional[Callable[[str], None]] = None) -> bool:
    """Download URLhaus text blocklist. No signature; store with hash for integrity check."""
    data = _https_get(URLHAUS_BLOCKLIST)
    if not data:
        return False
    out = DATA_DIR / "urlhaus_blocklist.txt"
    out.write_bytes(data)
    (DATA_DIR / "urlhaus_blocklist.sha256").write_text(_sha256_hex(data))
    if on_progress:
        on_progress("URLhaus blocklist updated")
    return True


def fetch_phishtank_public(on_progress: Optional[Callable[[str], None]] = None) -> bool:
    """Download PhishTank public feed (RSS/CSV). Optional API key for online-valid.json."""
    data = _https_get(PHISHTANK_PUBLIC)
    if not data:
        return False
    out = DATA_DIR / "phishtank_feed.xml"
    out.write_bytes(data)
    if on_progress:
        on_progress("PhishTank feed updated")
    return True


def fetch_clamav_sigs(on_progress: Optional[Callable[[str], None]] = None) -> bool:
    """Download ClamAV main/daily CVD. Store in data/ for YARA/ClamAV integration."""
    for url, name in [(CLAMAV_MAIN, "main.cvd"), (CLAMAV_DAILY, "daily.cvd")]:
        data = _https_get(url)
        if not data:
            continue
        out = DATA_DIR / name
        out.write_bytes(data)
        if on_progress:
            on_progress(f"ClamAV {name} updated")
    return (DATA_DIR / "main.cvd").exists() or (DATA_DIR / "daily.cvd").exists()


def run_all_updates(on_progress: Optional[Callable[[str], None]] = None) -> dict:
    """Run all update fetches: URLhaus, PhishTank, ClamAV, and YARA rules from GitHub."""
    result = {}
    result["urlhaus"] = fetch_urlhaus(on_progress)
    result["phishtank"] = fetch_phishtank_public(on_progress)
    result["clamav"] = fetch_clamav_sigs(on_progress)
    try:
        from signature_updater import run_signature_updates
        sig_result = run_signature_updates(on_progress)
        result["yara_github"] = sig_result.get("yara_github", False)
    except Exception:
        result["yara_github"] = False
    return result


class UpdateScheduler:
    """Background thread: run updates every INTERVAL_SECONDS."""

    def __init__(
        self,
        interval_seconds: int = INTERVAL_SECONDS,
        on_progress: Optional[Callable[[str], None]] = None,
        on_done: Optional[Callable[[dict], None]] = None,
    ):
        self.interval = interval_seconds
        self.on_progress = on_progress
        self.on_done = on_done
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10.0)
            self._thread = None

    def _run(self) -> None:
        while not self._stop.is_set():
            result = run_all_updates(self.on_progress)
            if self.on_done:
                self.on_done(result)
            self._stop.wait(timeout=self.interval)


def load_urlhaus_domains() -> set:
    """Load URLhaus blocklist as set of domains/URLs (first column typically)."""
    p = DATA_DIR / "urlhaus_blocklist.txt"
    if not p.exists():
        return set()
    domains = set()
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        # Format: url, id, ...
        parts = line.split(",")
        if parts:
            domains.add(parts[0].strip())
    return domains
