"""
Behavioral monitoring: process creation, file writes, network calls.
Uses psutil; on Windows optionally pywin32 for ETW/WMI.
"""

import os
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

import psutil

import sys
_parent = Path(__file__).resolve().parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult

# Optional Windows hooks
try:
    import win32api  # pywin32
    import win32con
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


@dataclass
class ProcessEvent:
    pid: int
    ppid: int
    name: str
    exe: Optional[str]
    cmdline: Optional[List[str]]
    create_time: float


# Suspicious process patterns
SUSPICIOUS_NAMES = frozenset([
    "powershell.exe", "pwsh.exe", "cmd.exe", "wscript.exe", "cscript.exe",
    "mshta.exe", "rundll32.exe", "regsvr32.exe", "certutil.exe",
])
SUSPICIOUS_CMDLINE_PATTERNS = [
    "-enc", "-EncodedCommand", "Invoke-Expression", "IEX(", "eval(",
    "fromBase64String", "DownloadString", "DownloadFile", "WebClient",
    "bitsadmin", "mshta ", "javascript:", "vbscript:",
]


def _cmdline_str(cmdline: Optional[List[str]]) -> str:
    if not cmdline:
        return ""
    return " ".join(cmdline).lower()


def is_suspicious_process(proc: ProcessEvent) -> Optional[str]:
    """Returns reason string if suspicious else None."""
    name_lower = (proc.name or "").lower()
    cmd = _cmdline_str(proc.cmdline)
    if name_lower in SUSPICIOUS_NAMES and any(p in cmd for p in SUSPICIOUS_CMDLINE_PATTERNS):
        return "suspicious_lolbin_cmdline"
    if "encodedcommand" in cmd or "-enc " in cmd:
        return "encoded_powershell"
    if "downloadstring" in cmd or "downloadfile" in cmd:
        return "download_cmdline"
    return None


class BehavioralMonitor:
    """
    Watch process creation (and optionally file/network). Calls on_suspicious with ThreatResult.
    """

    def __init__(
        self,
        on_suspicious: Callable[[ThreatResult], None],
        poll_interval: float = 1.0,
        watch_children: bool = True,
    ):
        self.on_suspicious = on_suspicious
        self.poll_interval = poll_interval
        self.watch_children = watch_children
        self._seen_pids: Set[int] = set()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        with self._lock:
            self._seen_pids = {p.pid for p in psutil.process_iter(["pid"])}
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self._check_new_processes()
            except Exception:
                pass
            self._stop.wait(timeout=self.poll_interval)

    def _check_new_processes(self) -> None:
        current = set()
        for proc in psutil.process_iter(["pid", "ppid", "name", "exe", "cmdline", "create_time"]):
            try:
                info = proc.info
                pid = info.get("pid")
                if pid is None:
                    continue
                current.add(pid)
                with self._lock:
                    if pid in self._seen_pids:
                        continue
                    self._seen_pids.add(pid)

                event = ProcessEvent(
                    pid=pid,
                    ppid=info.get("ppid") or 0,
                    name=info.get("name") or "",
                    exe=info.get("exe"),
                    cmdline=info.get("cmdline"),
                    create_time=info.get("create_time") or 0,
                )
                reason = is_suspicious_process(event)
                if reason:
                    self.on_suspicious(ThreatResult(
                        is_threat=True,
                        threat_type="suspicious_behavior",
                        severity="high",
                        confidence=75,
                        message=f"Suspicious process: {reason} - {event.name}",
                        details={
                            "pid": event.pid,
                            "ppid": event.ppid,
                            "name": event.name,
                            "exe": event.exe,
                            "cmdline": event.cmdline[:5] if event.cmdline else None,
                            "reason": reason,
                        },
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        with self._lock:
            self._seen_pids = current


def get_network_connections_summary() -> List[dict]:
    """Return list of dicts with pid, status, laddr, raddr for active connections."""
    out = []
    for c in psutil.net_connections(kind="inet"):
        if c.status not in ("ESTABLISHED", "SYN_SENT", "SYN_RECV"):
            continue
        try:
            proc = psutil.Process(c.pid) if c.pid else None
            out.append({
                "pid": c.pid,
                "name": proc.name() if proc else None,
                "status": c.status,
                "laddr": f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else None,
                "raddr": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else None,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return out
