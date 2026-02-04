"""
Signature database expansion: auto-updating YARA and ClamAV-style defs.
Pulls YARA rules from GitHub (VirusTotal-style), ClamAV daily, and supports
community-submitted sigs via repo or URL.
"""

import io
import os
import sys
import zipfile
import threading
from pathlib import Path
from typing import Callable, Optional
from urllib.request import urlopen, Request

_parent = Path(__file__).resolve().parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

# Default dirs
YARA_RULES_DIR = _parent / "yara_rules"
DATA_DIR = _parent / "data"
DATA_DIR.mkdir(exist_ok=True)
YARA_RULES_DIR.mkdir(exist_ok=True)

# YARA rule sources (open, no auth)
YARA_GITHUB_ZIP = "https://github.com/Yara-Rules/rules/archive/refs/heads/master.zip"
MALWAREBAZAAR_YARA = "https://bazaar.abuse.ch/export/#yara"  # manual export; we use GitHub for auto
CLAMAV_DAILY = "https://database.clamav.net/daily.cvd"
CLAMAV_MAIN = "https://database.clamav.net/main.cvd"


def _https_get(url: str, timeout: int = 120) -> Optional[bytes]:
    try:
        req = Request(url, headers={"User-Agent": "CyberDefense-SignatureUpdater/2.0"})
        with urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception:
        return None


def fetch_yara_rules_github(
    zip_url: str = YARA_GITHUB_ZIP,
    extract_to: Optional[Path] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> bool:
    """
    Download YARA rules from GitHub (e.g. Yara-Rules/rules) and extract to yara_rules/.
    VirusTotal-style rule set; update daily.
    """
    extract_to = extract_to or YARA_RULES_DIR
    data = _https_get(zip_url)
    if not data:
        if on_progress:
            on_progress("YARA GitHub fetch failed")
        return False
    try:
        with zipfile.ZipFile(io.BytesIO(data), "r") as z:
            # Extract only .yar / .yara files into a flat or structured dir
            community = extract_to / "community"
            community.mkdir(parents=True, exist_ok=True)
            count = 0
            for name in z.namelist():
                if name.endswith((".yar", ".yara")) and not name.startswith("__"):
                    try:
                        content = z.read(name)
                        # Safe filename
                        base = Path(name).name
                        out = community / base
                        out.write_bytes(content)
                        count += 1
                    except Exception:
                        continue
        if on_progress:
            on_progress(f"YARA rules updated: {count} files in {community}")
        return count > 0
    except Exception as e:
        if on_progress:
            on_progress(f"YARA extract error: {e}")
        return False


def fetch_clamav_daily(
    on_progress: Optional[Callable[[str], None]] = None,
) -> bool:
    """Pull ClamAV daily.cvd into data/ for ClamAV-style scanning (or future engine)."""
    data = _https_get(CLAMAV_DAILY)
    if not data:
        if on_progress:
            on_progress("ClamAV daily fetch failed")
        return False
    out = DATA_DIR / "daily.cvd"
    out.write_bytes(data)
    if on_progress:
        on_progress("ClamAV daily.cvd updated")
    return True


def fetch_clamav_main(
    on_progress: Optional[Callable[[str], None]] = None,
) -> bool:
    """Pull ClamAV main.cvd into data/."""
    data = _https_get(CLAMAV_MAIN)
    if not data:
        if on_progress:
            on_progress("ClamAV main fetch failed")
        return False
    out = DATA_DIR / "main.cvd"
    out.write_bytes(data)
    if on_progress:
        on_progress("ClamAV main.cvd updated")
    return True


def run_signature_updates(on_progress: Optional[Callable[[str], None]] = None) -> dict:
    """
    Run all signature updates: YARA from GitHub, ClamAV daily/main.
    Returns dict with success flags. Run daily (e.g. from UpdateScheduler).
    """
    result = {}
    result["yara_github"] = fetch_yara_rules_github(on_progress=on_progress)
    result["clamav_daily"] = fetch_clamav_daily(on_progress=on_progress)
    result["clamav_main"] = fetch_clamav_main(on_progress=on_progress)
    return result


class SignatureUpdateScheduler:
    """Background thread: run signature updates every 24 hours."""

    def __init__(
        self,
        interval_seconds: int = 24 * 60 * 60,
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
            self._thread.join(timeout=15.0)
            self._thread = None

    def _run(self) -> None:
        while not self._stop.is_set():
            result = run_signature_updates(self.on_progress)
            if self.on_done:
                self.on_done(result)
            self._stop.wait(timeout=self.interval)
