"""
NotificationManager: Smart notification system with debouncing, batching, and cooldown.
Prevents spam; user-configurable per category. Use this instead of calling tray.showMessage directly.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Optional

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
        show_fn: Callable[[str, str, str, int], None],
        config: Optional[NotificationConfig] = None,
    ):
        """
        show_fn(tile, message, severity, msecs) - e.g. tray.showMessage(title, msg, icon, msecs)
        """
        self._show_fn = show_fn
        self._config = config or NotificationConfig()
        self._last_shown: dict[str, float] = {}
        self._pending: dict[str, PendingNotification] = {}
        self._batch_timer: Optional[object] = None  # QTimer if we use it; for now we flush on next notify

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
        self._pending.pop(f"{n.category}:{n.title}", None)

    def notify(
        self,
        title: str,
        message: str,
        category: str = "other",
        severity: str = WARNING,
    ) -> None:
        """
        Request a notification. May be debounced, batched, or suppressed.
        category: "file", "network", "phishing", "tracker", "vpn", "behavioral", "update", "other"
        severity: "info", "warning", "critical"
        """
        if self._is_muted(category):
            return

        key = f"{category}:{title}"
        now = time.monotonic()

        if self._config.batch_similar:
            if key in self._pending:
                self._pending[key].count += 1
                self._pending[key].timestamp = now
                # If we're in cooldown, the batched one will show when cooldown expires
                if not self._in_cooldown(category):
                    self._do_show(self._pending[key])
                    del self._pending[key]
                return
            else:
                n = PendingNotification(title=title, message=message, category=category, severity=severity)
                if self._in_cooldown(category):
                    self._pending[key] = n
                    return
                self._do_show(n)
                return

        if self._in_cooldown(category):
            self._pending[key] = PendingNotification(
                title=title, message=message, category=category, severity=severity
            )
            return

        self._do_show(PendingNotification(title=title, message=message, category=category, severity=severity))

    def flush_pending(self) -> None:
        """Show any pending batched notifications (e.g. on cooldown expiry)."""
        for key, n in list(self._pending.items()):
            if not self._is_muted(n.category) and not self._in_cooldown(n.category):
                self._do_show(n)
                del self._pending[key]
