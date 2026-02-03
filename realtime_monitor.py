"""
Event-driven real-time file monitoring.
Windows: ReadDirectoryChangesW (or watchdog); Linux: inotify via watchdog.
No polling — react on file create/modify immediately.
"""

import os
import sys
import threading
from pathlib import Path
from typing import Callable, List, Optional

# Parent for threat_engine
_parent = Path(__file__).resolve().parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult

# Prefer watchdog for cross-platform; Windows can use ReadDirectoryChangesW for lower latency
USE_WATCHDOG = True


def _scan_callback_default(path: str) -> Optional[ThreatResult]:
    """Default: use threat_engine comprehensive scan."""
    from threat_engine import scan_file_comprehensive, Sensitivity
    return scan_file_comprehensive(path, Sensitivity.MEDIUM)


class RealtimeFileMonitor:
    """
    Event-driven file monitor. On file create/modify, calls scan_callback(path).
    If scan_callback returns a ThreatResult with is_threat=True, on_threat(result, path) is called.
    """

    def __init__(
        self,
        watch_paths: List[str],
        on_threat: Callable[[ThreatResult, str], None],
        scan_callback: Optional[Callable[[str], Optional[ThreatResult]]] = None,
        extensions_to_watch: Optional[List[str]] = None,
    ):
        self.watch_paths = [Path(p).resolve() for p in watch_paths]
        self.on_threat = on_threat
        self.scan_callback = scan_callback or _scan_callback_default
        self.extensions_to_watch = (extensions_to_watch or [
            ".exe", ".dll", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".msi", ".com"
        ])
        self._observer = None
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def _should_scan(self, path: str) -> bool:
        p = Path(path)
        if not p.is_file():
            return False
        suf = p.suffix.lower()
        return suf in self.extensions_to_watch

    def _handle_event(self, path: str) -> None:
        if not self._should_scan(path):
            return
        try:
            result = self.scan_callback(path)
            if result and result.is_threat:
                self.on_threat(result, path)
        except Exception:
            pass

    def start(self) -> None:
        if USE_WATCHDOG:
            self._start_watchdog()
        else:
            self._start_polling_fallback()

    def _start_watchdog(self) -> None:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent
        except ImportError:
            self._start_polling_fallback()
            return

        class Handler(FileSystemEventHandler):
            def __init__(self, parent: RealtimeFileMonitor):
                self.parent = parent

            def on_created(self, event):
                if event.is_directory:
                    return
                self.parent._handle_event(event.src_path)

            def on_modified(self, event):
                if event.is_directory:
                    return
                self.parent._handle_event(event.src_path)

        self._observer = Observer()
        handler = Handler(self)
        for wp in self.watch_paths:
            if wp.exists():
                self._observer.schedule(handler, str(wp), recursive=True)
        self._observer.start()

    def _start_polling_fallback(self) -> None:
        """Fallback: poll every 2s for new files (worse than event-driven)."""
        self._stop.clear()
        seen: set = set()

        def poll():
            while not self._stop.is_set():
                for wp in self.watch_paths:
                    if not wp.exists():
                        continue
                    try:
                        for f in wp.rglob("*"):
                            if f.is_file() and f.suffix.lower() in self.extensions_to_watch:
                                key = (str(f), f.stat().st_mtime)
                                if key not in seen:
                                    seen.add(key)
                                    self._handle_event(str(f))
                    except (PermissionError, OSError):
                        pass
                self._stop.wait(timeout=2.0)

        self._thread = threading.Thread(target=poll, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._observer is not None:
            try:
                self._observer.stop()
                self._observer.join(timeout=5.0)
            except Exception:
                pass
            self._observer = None
        if self._thread is not None:
            self._thread.join(timeout=5.0)
            self._thread = None
