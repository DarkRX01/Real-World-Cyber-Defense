"""
Anomaly detection: baseline system behavior, alert on deviations.
Local-first (no cloud). Optional torch/ML later for baseline modeling.
"""

import sys
import threading
import time
from collections import deque
from pathlib import Path
from typing import Callable, Deque, Dict, Optional

_parent = Path(__file__).resolve().parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult

# Baseline: number of "events" (e.g. file creations) per minute
# Alert if current rate > baseline_multiplier * median of recent rates
BASELINE_WINDOW_MINUTES = 60
BASELINE_MULTIPLIER = 2.5


class SimpleAnomalyDetector:
    """
    Rolling window of event counts per minute. Flags if recent rate
    exceeds baseline_multiplier * median of historical rates.
    """

    def __init__(
        self,
        window_minutes: int = BASELINE_WINDOW_MINUTES,
        baseline_multiplier: float = BASELINE_MULTIPLIER,
        on_anomaly: Optional[Callable[[ThreatResult], None]] = None,
    ):
        self.window_minutes = window_minutes
        self.baseline_multiplier = baseline_multiplier
        self.on_anomaly = on_anomaly or (lambda r: None)
        self._events_per_minute: Deque[float] = deque(maxlen=window_minutes)
        self._current_minute_events = 0
        self._current_minute_start = time.monotonic()
        self._lock = threading.Lock()

    def record_event(self) -> None:
        """Call on each event (e.g. file create). Rolls to new minute as time passes."""
        with self._lock:
            now = time.monotonic()
            elapsed_min = (now - self._current_minute_start) / 60.0
            if elapsed_min >= 1.0:
                # Push previous minute's count
                self._events_per_minute.append(self._current_minute_events)
                self._current_minute_events = 0
                self._current_minute_start = now
            self._current_minute_events += 1
            if len(self._events_per_minute) < 5:
                return
            # Check anomaly: current rate vs median historical
            recent = list(self._events_per_minute)[-self.window_minutes:]
            recent.append(self._current_minute_events)
            recent.sort()
            median = recent[len(recent) // 2]
            current_rate = self._current_minute_events / max(elapsed_min, 0.016)
            if median > 0 and current_rate >= self.baseline_multiplier * median:
                self.on_anomaly(ThreatResult(
                    is_threat=True,
                    threat_type="anomaly",
                    severity="medium",
                    confidence=65,
                    message=f"Unusual file/event rate: {current_rate:.0f}/min (baseline ~{median})",
                    details={"current_rate": current_rate, "median_baseline": median},
                ))
