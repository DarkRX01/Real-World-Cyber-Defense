"""
NotificationManager: Smart notification system with debouncing, batching, cooldown, and queue flushing.

Why this exists:
- Prevent tray popup spam (cooldowns + batching)
- Avoid Qt event-loop overload / self-kill when many events occur (queue + limited flush rate)
- Centralize severity and per-category mute logic
"""

import time
from dataclasses import dataclass, field
from typing import Callable, Optional, Deque
from collections import deque

# Severity maps to QSystemTrayIcon.MessageIcon
INFO = "info"
WARNING = "warning"
CRITICAL = "critical"


@dataclass
class NotificationConfig:
    """User-configurable notification settings."""
    enabled: bool = True
    cooldown_seconds: float = 25.0
    batch_similar: bool = True
    mute_file_threats: bool = False
    mute_network_threats: bool = False
    mute_vpn_status: bool = False
    mute_behavioral: bool = False


@dataclass
class PendingNotification:
    title: str
    message: str
    category: str  # "file", "network", "vpn", "behavioral", "update", "other"
    severity: str
    count: int = 1
    timestamp: float = field(default_factory=time.monotonic)


class NotificationManager:
    """
    Central notification manager. Debounces and batches alerts.
    Call notify() instead of tray.showMessage(); this manager decides when to actually show.
    """

    def __init__(
        self,
        show_fn: Callable[[str, str, int, int], None],
        config: Optional[NotificationConfig] = None,
    ):
        """
        show_fn(title, message, icon_int, msecs) - e.g. tray.showMessage(title, msg, icon_enum, msecs)
        """
        self._show_fn = show_fn
        self._config = config or NotificationConfig()
        self._last_shown: dict[str, float] = {}
        # Pending (batched) notifications waiting for cooldown expiry
        self._pending: dict[str, PendingNotification] = {}
        # Queue to prevent event-loop overload. Flushed via QTimer in the GUI every N seconds.
        self._queue: Deque[PendingNotification] = deque(maxlen=500)

    def update_config(self, config: NotificationConfig) -> None:
        self._config = config

    def _is_muted(self, category: str) -> bool:
        if not self._config.enabled:
            return True
        if category == "file" and self._config.mute_file_threats:
            return True
        if category in ("network", "phishing", "tracker") and self._config.mute_network_threats:
            return True
        if category == "vpn" and self._config.mute_vpn_status:
            return True
        if category == "behavioral" and self._config.mute_behavioral:
            return True
        return False

    def _in_cooldown(self, category: str) -> bool:
        last = self._last_shown.get(category, 0)
        return (time.monotonic() - last) < self._config.cooldown_seconds

    def _map_severity(self, severity: str) -> int:
        """Map to QSystemTrayIcon.MessageIcon (0=Info, 1=Warning, 2=Critical)."""
        if severity == CRITICAL:
            return 2
        if severity == WARNING:
            return 1
        return 0

    def _do_show(self, n: PendingNotification) -> None:
        """Actually show the notification. icon: 0=Info, 1=Warning, 2=Critical for QSystemTrayIcon."""
        if self._is_muted(n.category):
            return
        title = n.title
        msg = n.message
        if n.count > 1 and self._config.batch_similar:
            msg = f"{msg} ({n.count} similar)"
        icon = self._map_severity(n.severity)
        msecs = 8000 if n.severity == CRITICAL else 5000
        try:
            self._show_fn(title, msg, icon, msecs)
        except Exception:
            pass
        self._last_shown[n.category] = time.monotonic()

    def enqueue(
        self,
        title: str,
        message: str,
        category: str = "other",
        severity: str = WARNING,
    ) -> None:
        """
        Enqueue a notification request. This does NOT immediately show popups.
        Call flush_queue() periodically from a QTimer (e.g. every 5s).
        """
        if self._is_muted(category):
            return
        self._queue.append(PendingNotification(title=title, message=message, category=category, severity=severity))

    def notify(
        self,
        title: str,
        message: str,
        category: str = "other",
        severity: str = WARNING,
    ) -> None:
        """Backward-compatible API: enqueue instead of immediate show (safer under load)."""
        self.enqueue(title=title, message=message, category=category, severity=severity)

    def flush_queue(self, max_to_show: int = 3) -> None:
        """
        Flush queued notifications with cooldown + batching + max rate.
        Call this from GUI QTimer (e.g. every 5 seconds).
        """
        shown = 0
        # First, try to release any pending batched notifications whose cooldown expired
        for key, n in list(self._pending.items()):
            if shown >= max_to_show:
                break
            if not self._is_muted(n.category) and not self._in_cooldown(n.category):
                self._do_show(n)
                del self._pending[key]
                shown += 1

        # Then, consume from queue (batch/cooldown)
        while self._queue and shown < max_to_show:
            n = self._queue.popleft()
            if self._is_muted(n.category):
                continue
            key = f"{n.category}:{n.title}"
            if self._config.batch_similar:
                if key in self._pending:
                    self._pending[key].count += 1
                    self._pending[key].timestamp = time.monotonic()
                    continue
                if self._in_cooldown(n.category):
                    self._pending[key] = n
                    continue
                self._do_show(n)
                shown += 1
                continue
            # no batching
            if self._in_cooldown(n.category):
                self._pending[key] = n
                continue
            self._do_show(n)
            shown += 1
