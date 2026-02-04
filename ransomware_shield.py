"""
Ransomware shield: honeypot files in key dirs; if touched, quarantine and alert.
Monitor for mass file encryptions (many modifications in short time).
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import Callable, List, Optional, Set

_parent = Path(__file__).resolve().parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult

# Honeypot filename (hidden-ish); ransomware often encrypts everything
HONEYPOT_FILENAME = ".cyberdefense_honeypot"
HONEYPOT_CONTENT = b"CyberDefense honeypot - do not encrypt\n"
# Mass change: more than this many file events in this window = possible ransomware
MASS_CHANGE_THRESHOLD = 50
MASS_CHANGE_WINDOW_SECONDS = 10.0


def get_default_honeypot_dirs() -> List[Path]:
    """Dirs to place honeypots: Downloads, Desktop, Documents."""
    home = Path.home()
    if sys.platform == "win32":
        profile = os.environ.get("USERPROFILE", str(home))
        base = Path(profile)
    else:
        base = home
    dirs = []
    for name in ("Downloads", "Desktop", "Documents"):
        p = base / name
        if p.exists():
            dirs.append(p)
    return dirs


def ensure_honeypot_files() -> List[Path]:
    """Create honeypot files in key dirs. Return list of paths created/existing."""
    created = []
    for d in get_default_honeypot_dirs():
        hp = d / HONEYPOT_FILENAME
        try:
            if not hp.exists():
                hp.write_bytes(HONEYPOT_CONTENT)
            created.append(hp)
        except (OSError, IOError):
            pass
    return created


def get_honeypot_paths() -> Set[str]:
    """Return set of absolute paths that are honeypot files (for realtime monitor check)."""
    out = set()
    for d in get_default_honeypot_dirs():
        hp = d / HONEYPOT_FILENAME
        if hp.exists():
            out.add(str(hp.resolve()))
    return out


def is_honeypot_path(filepath: str) -> bool:
    """True if filepath is one of our honeypot files."""
    try:
        return Path(filepath).resolve() in {Path(p) for p in get_honeypot_paths()}
    except Exception:
        return False


def honeypot_threat_result(filepath: str) -> ThreatResult:
    """ThreatResult for honeypot touched (possible ransomware)."""
    return ThreatResult(
        is_threat=True,
        threat_type="ransomware_honeypot",
        severity="critical",
        confidence=95,
        message="Ransomware honeypot touched - possible mass encryption in progress",
        details={"filepath": filepath, "action": "quarantine_process_recommended"},
    )


class MassChangeDetector:
    """
    Tracks file change events; flags if count in recent window exceeds threshold
    (possible ransomware mass encryption).
    """

    def __init__(
        self,
        threshold: int = MASS_CHANGE_THRESHOLD,
        window_seconds: float = MASS_CHANGE_WINDOW_SECONDS,
        on_mass_change: Optional[Callable[[ThreatResult], None]] = None,
    ):
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.on_mass_change = on_mass_change or (lambda r: None)
        self._timestamps: List[float] = []
        self._lock = threading.Lock()

    def record_event(self, path: str = "") -> None:
        """Call when a file create/modify is observed."""
        with self._lock:
            now = time.monotonic()
            self._timestamps.append(now)
            cutoff = now - self.window_seconds
            self._timestamps = [t for t in self._timestamps if t > cutoff]
            if len(self._timestamps) >= self.threshold:
                self.on_mass_change(ThreatResult(
                    is_threat=True,
                    threat_type="mass_file_change",
                    severity="critical",
                    confidence=85,
                    message=f"Mass file change detected ({len(self._timestamps)} events in {self.window_seconds}s) - possible ransomware",
                    details={"count": len(self._timestamps), "window_sec": self.window_seconds},
                ))
                self._timestamps.clear()
