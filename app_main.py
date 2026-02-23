#!/usr/bin/env python3
"""
Real-World Cyber Defense - Desktop Application
Main entry point and PyQt5 GUI.
"""

import os
import sys
from pathlib import Path

# Ensure the app root is on sys.path so threat_engine, background_service, etc. are always found.
# Fixes ModuleNotFoundError when running "python app_main.py" from another directory.
if getattr(sys, "frozen", False):
    _APP_ROOT = Path(sys.executable).resolve().parent
else:
    _APP_ROOT = Path(__file__).resolve().parent
if str(_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_APP_ROOT))
# When running as script (not frozen), run from app root so relative paths work.
if not getattr(sys, "frozen", False):
    os.chdir(_APP_ROOT)

import json
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStyle,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QScrollArea,
    QFrame,
)

APP_VERSION = "3.0.0"  # Major upgrade: quiet, clean, enterprise-grade

from threat_engine import (
    ThreatResult,
    Sensitivity,
    scan_url,
    analyze_download,
    get_system_security_summary,
)
from background_service import BackgroundService

# APP SELF-EXCLUSION - Don't flag ourselves as a threat
_APP_HASHES = set()  # Will be populated during init
_APP_PATHS = set()  # Whitelist our own paths

def _init_app_whitelist():
    """Initialize whitelist of this app to prevent self-detection."""
    global _APP_HASHES, _APP_PATHS
    try:
        import hashlib
        if getattr(sys, "frozen", False):
            exe_path = Path(sys.executable)
        else:
            exe_path = Path(__file__)
        
        _APP_PATHS.add(str(exe_path.resolve()))
        _APP_PATHS.add(str(_APP_ROOT))
        
        # Hash our executable
        try:
            from utils import safe_hash_file
            h = safe_hash_file(str(exe_path))
            if h:
                _APP_HASHES.add(h)
        except Exception:
            try:
                with open(exe_path, 'rb') as f:
                    _APP_HASHES.add(hashlib.sha256(f.read()).hexdigest())
            except Exception:
                pass
    except:
        pass


def _config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", os.path.expanduser("~")))
    else:
        base = Path.home()
    d = base / ".cyber-defense"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _logs_dir() -> Path:
    d = _config_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def setup_logging() -> logging.Logger:
    """Configure application logging with file rotation."""
    logger = logging.getLogger("CyberDefense")
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG level, rotating)
    try:
        log_file = _logs_dir() / "cyber-defense.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file logging: {e}")
    
    return logger


# Initialize logger
logger = setup_logging()


def _settings_path() -> Path:
    return _config_dir() / "settings.json"


def _threat_log_path() -> Path:
    return _config_dir() / "threat_log.json"


def load_settings() -> dict:
    p = _settings_path()
    if not p.exists():
        logger.debug("No settings file found, using defaults")
        return default_settings()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.debug("Settings loaded successfully")
        return {**default_settings(), **data}
    except Exception as e:
        logger.warning(f"Failed to load settings: {e}, using defaults")
        return default_settings()


def default_settings() -> dict:
    return {
        "sensitivity": "MEDIUM",
        "enable_clipboard": True,
        "enable_tracker_check": True,
        "enable_notifications": True,
        "enable_phishing": True,
        "enable_download_scan": True,
        "enable_url_scan": True,
        "start_minimized": True,
        "enable_realtime_monitor": True,
        "enable_auto_updates": True,
        "enable_behavioral_monitor": True,
        "enable_vpn": False,
        "vpn_provider": "none",  # 'none', 'mullvad', 'adguard', 'protonvpn', 'custom'
        "vpn_config_path": "",
        "vpn_kill_switch": False,
        "enable_autostart": False,  # Start with Windows
        # Notification / noise controls - QUIET BY DEFAULT
        "notif_cooldown_seconds": 120.0,  # 2 min cooldown for less spam
        "notif_batch_similar": True,
        "notif_mute_file": False,
        "notif_mute_network": True,  # Quiet network monitoring by default
        "notif_mute_vpn": True,  # Quiet VPN status by default
        "notif_mute_behavioral": True,  # Quiet behavior alerts by default
        "notif_min_severity": "critical",  # Only show CRITICAL alerts by default
        "show_only_threats": True,  # Don't show empty/benign scan results
    }


def save_settings(s: dict) -> None:
    try:
        with open(_settings_path(), "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
        logger.debug("Settings saved successfully")
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")


def load_threat_log() -> list:
    p = _threat_log_path()
    if not p.exists():
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_threat_log(log: list) -> None:
    # Keep last 500 entries
    log = log[-500:]
    try:
        with open(_threat_log_path(), "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save threat log: {e}")


def sensitivity_from_string(s: str) -> Sensitivity:
    m = {
        "LOW": Sensitivity.LOW,
        "MEDIUM": Sensitivity.MEDIUM,
        "HIGH": Sensitivity.HIGH,
        "EXTREME": Sensitivity.EXTREME,
    }
    return m.get(s.upper(), Sensitivity.MEDIUM)


# --- Worker threads for non-blocking UI ---

class ScanWorker(QObject):
    """Runs scan_file_comprehensive in background. Emits result or progress."""
    finished = pyqtSignal(object, str)
    progress = pyqtSignal(int, int)

    def __init__(self, paths: list, sensitivity: Sensitivity):
        super().__init__()
        self.paths = paths
        self.sensitivity = sensitivity

    def run(self):
        from threat_engine import scan_file_comprehensive
        total = len(self.paths)
        for i, p in enumerate(self.paths):
            try:
                r = scan_file_comprehensive(p, self.sensitivity)
                if r.is_threat:
                    self.finished.emit(r, p)
            except Exception:
                pass
            self.progress.emit(i + 1, total)


class FolderScanWorker(QObject):
    """Scans a folder recursively for files, then runs ScanWorker-style scan."""
    finished = pyqtSignal()
    threat_found = pyqtSignal(object, str)
    progress = pyqtSignal(int, int)

    def __init__(self, folder: str, extensions: list, sensitivity: Sensitivity):
        super().__init__()
        self.folder = folder
        self.extensions = extensions or [".exe", ".dll", ".bat", ".ps1", ".vbs", ".js", ".msi"]
        self.sensitivity = sensitivity

    def run(self):
        from pathlib import Path
        from threat_engine import scan_file_comprehensive
        folder = Path(self.folder)
        if not folder.exists():
            self.finished.emit()
            return
        files = []
        for ext in self.extensions:
            files.extend(folder.rglob(f"*{ext}"))
        files = [str(f) for f in files if f.is_file()][:500]
        total = len(files)
        for i, p in enumerate(files):
            try:
                r = scan_file_comprehensive(p, self.sensitivity)
                if r.is_threat:
                    self.threat_found.emit(r, p)
            except Exception:
                pass
            self.progress.emit(i + 1, total)
        self.finished.emit()


class VPNConnectWorker(QObject):
    """Runs VPN connect/disconnect in background."""
    finished = pyqtSignal(bool, str)

    def __init__(self, vpn_client_obj, connect: bool):
        super().__init__()
        self.vpn_client_obj = vpn_client_obj
        self.connect = connect

    def run(self):
        try:
            if not self.vpn_client_obj:
                self.finished.emit(False, "VPN is not configured.")
                return
            if self.connect:
                ok, msg = self.vpn_client_obj.connect()
            else:
                ok, msg = self.vpn_client_obj.disconnect()
            # After action, poll real status briefly so UI is accurate.
            try:
                deadline = time.monotonic() + (20.0 if self.connect else 10.0)
                while time.monotonic() < deadline:
                    connected = self.vpn_client_obj.is_connected()
                    if self.connect and connected:
                        ok = True
                        break
                    if (not self.connect) and (not connected):
                        ok = True
                        break
                    time.sleep(0.5)
            except Exception:
                pass
            self.finished.emit(ok, msg)
        except Exception as e:
            self.finished.emit(False, str(e))


def _make_tray_icon_pixmap(color: str, size: int = 32) -> QPixmap:
    """Create a simple colored circle icon for tray status (green/yellow/red)."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.NoPen)
    p.drawEllipse(2, 2, size - 4, size - 4)
    p.end()
    return pix


class CyberDefenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing Cyber Defense application")
        self.setWindowTitle(f"Cyber Defense v{APP_VERSION} — Real-World Security")
        self.setMinimumSize(920, 680)
        self.resize(1020, 720)
        
        # Force window to show on top and centered
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()

        self.settings = load_settings()
        self.threat_log: list = load_threat_log()
        _init_app_whitelist()  # Initialize app self-exclusion
        self._paused = False
        self._stats = {"threats": 0, "trackers": 0, "phishing": 0}
        self._update_scheduler = None
        self._realtime_monitor = None
        self._behavioral_monitor = None
        self._vpn_client = None

        self._service = BackgroundService(
            on_threat=self._on_threat_detected,
            sensitivity=sensitivity_from_string(self.settings.get("sensitivity", "MEDIUM")),
            enable_clipboard=bool(self.settings.get("enable_clipboard", True)),
            enable_tracker_check=bool(self.settings.get("enable_tracker_check", True)),
        )

        # Build UI; be defensive in case an older frozen EXE lacks the method.
        if hasattr(self, "_build_ui") and callable(getattr(self, "_build_ui")):
            try:
                self._build_ui()
            except Exception:
                # Fall through to minimal UI builder
                self._build_ui_fallback()
        else:
            self._build_ui_fallback()
        self._setup_tray()
        self._setup_notification_manager()
        self._apply_settings()
        self._refresh_stats()
        self._start_monitoring()
        self._start_optional_services()
        self._start_status_timer()

    def _build_ui(self):
        """Construct main window: stat cards + tab widget."""
        central = QWidget()
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(14)

        # Top statistics row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        # Protection card
        prot_frame = QFrame()
        prot_frame.setObjectName("StatCard")
        prot_layout = QVBoxLayout(prot_frame)
        prot_title = QLabel("Protection")
        prot_title.setObjectName("StatTitle")
        prot_layout.addWidget(prot_title)
        self.lbl_protection = QLabel("ON" if not getattr(self, "_paused", False) else "PAUSED")
        self.lbl_protection.setObjectName("ProtectionValue")
        prot_layout.addWidget(self.lbl_protection)
        prot_layout.addStretch()
        stats_row.addWidget(prot_frame)

        # Threats card
        t_frame = QFrame()
        t_frame.setObjectName("StatCard")
        t_layout = QVBoxLayout(t_frame)
        t_title = QLabel("Threats")
        t_title.setObjectName("StatTitle")
        t_layout.addWidget(t_title)
        self.lbl_threats = QLabel(str(self._stats.get("threats", 0)))
        self.lbl_threats.setObjectName("StatValue")
        t_layout.addWidget(self.lbl_threats)
        t_layout.addStretch()
        stats_row.addWidget(t_frame)

        # Trackers card
        tr_frame = QFrame()
        tr_frame.setObjectName("StatCard")
        tr_layout = QVBoxLayout(tr_frame)
        tr_title = QLabel("Trackers")
        tr_title.setObjectName("StatTitle")
        tr_layout.addWidget(tr_title)
        self.lbl_trackers = QLabel(str(self._stats.get("trackers", 0)))
        self.lbl_trackers.setObjectName("StatValue")
        tr_layout.addWidget(self.lbl_trackers)
        tr_layout.addStretch()
        stats_row.addWidget(tr_frame)

        # Phishing card
        ph_frame = QFrame()
        ph_frame.setObjectName("StatCard")
        ph_layout = QVBoxLayout(ph_frame)
        ph_title = QLabel("Phishing")
        ph_title.setObjectName("StatTitle")
        ph_layout.addWidget(ph_title)
        self.lbl_phishing = QLabel(str(self._stats.get("phishing", 0)))
        self.lbl_phishing.setObjectName("StatValue")
        ph_layout.addWidget(self.lbl_phishing)
        ph_layout.addStretch()
        stats_row.addWidget(ph_frame)

        stats_row.addStretch()
        main_layout.addLayout(stats_row)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._dashboard_tab(), "Dashboard")
        self.tabs.addTab(self._threats_tab(), "Threats")
        self.tabs.addTab(self._vpn_tab(), "VPN")
        self.tabs.addTab(self._settings_tab(), "Settings")
        main_layout.addWidget(self.tabs)

        self.setCentralWidget(central)

    def _create_stat_card(self, icon: str, title: str, gradient: str, glow: str) -> QWidget:
        """Create a modern stat card with gradient background."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background: {gradient};
                border-radius: 16px;
                padding: 20px;
            }}
        """)
        card.setMinimumWidth(180)
        card.setMinimumHeight(140)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)

        # Icon and title row
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            font-size: 28px;
            background: transparent;
        """)
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        card_layout.addLayout(header_layout)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        card_layout.addWidget(title_label)
        
        card_layout.addStretch()
        
        return card

    def _build_ui_fallback(self):
        """Lightweight fallback UI if the primary `_build_ui` is missing or fails.
        This ensures frozen binaries built from older sources still show a usable window.
        """
        try:
            central = QWidget()
            layout = QVBoxLayout(central)
            hdr = QLabel("Cyber Defense")
            hdr.setObjectName("SectionHeader")
            layout.addWidget(hdr)
            self.tabs = QTabWidget()
            # Attempt to add tabs if the methods exist
            try:
                self.tabs.addTab(self._dashboard_tab(), "Dashboard")
            except Exception:
                self.tabs.addTab(QWidget(), "Dashboard")
            try:
                self.tabs.addTab(self._threats_tab(), "Threats")
            except Exception:
                self.tabs.addTab(QWidget(), "Threats")
            try:
                self.tabs.addTab(self._vpn_tab(), "VPN")
            except Exception:
                self.tabs.addTab(QWidget(), "VPN")
            try:
                self.tabs.addTab(self._settings_tab(), "Settings")
            except Exception:
                self.tabs.addTab(QWidget(), "Settings")
            layout.addWidget(self.tabs)
            self.setCentralWidget(central)
        except Exception:
            # As a last resort, create a minimal empty window
            try:
                self.setCentralWidget(QWidget())
            except Exception:
                pass

    def _dashboard_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)
        overview_header = QLabel("Overview")
        overview_header.setStyleSheet("font-size: 14px; font-weight: 600; color: #94a3b8;")
        layout.addWidget(overview_header)
        self.dashboard_text = QPlainTextEdit()
        self.dashboard_text.setReadOnly(True)
        self.dashboard_text.setMinimumHeight(120)
        self.dashboard_text.setPlaceholderText(
            "Copy a URL to scan automatically. Threats appear here and in the Threats tab."
        )
        layout.addWidget(self.dashboard_text)
        quick_hl = QLabel("Quick actions")
        quick_hl.setStyleSheet("font-size: 13px; font-weight: 600; color: #94a3b8; margin-top: 8px;")
        layout.addWidget(quick_hl)
        btn_row = QHBoxLayout()
        self.btn_quick_scan = QPushButton("Quick Scan (Downloads)")
        self.btn_quick_scan.setObjectName("SuccessButton")
        self.btn_quick_scan.setToolTip("Scan Downloads folder in background")
        self.btn_quick_scan.clicked.connect(self._quick_scan_clicked)
        self.btn_full_scan = QPushButton("Full Scan")
        self.btn_full_scan.setObjectName("DangerButton")
        self.btn_full_scan.setToolTip("Scan user folders (may take a while)")
        self.btn_full_scan.clicked.connect(self._full_scan_clicked)
        self.btn_vpn_toggle = QPushButton("VPN: Connect")
        self.btn_vpn_toggle.setObjectName("DefaultButton")
        self.btn_vpn_toggle.setToolTip("Connect or disconnect VPN")
        self.btn_vpn_toggle.clicked.connect(self._dashboard_vpn_toggle)
        self.btn_realtime_toggle = QPushButton("Real-time: On")
        self.btn_realtime_toggle.setObjectName("DefaultButton")
        self.btn_realtime_toggle.setToolTip("Toggle real-time file monitoring")
        self.btn_realtime_toggle.clicked.connect(self._dashboard_realtime_toggle)
        for b in (self.btn_quick_scan, self.btn_full_scan, self.btn_vpn_toggle, self.btn_realtime_toggle):
            btn_row.addWidget(b)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        layout.addWidget(self.scan_progress)
        gb = QGroupBox("URL Scanner")
        fl = QFormLayout(gb)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste URL to scan")
        fl.addRow("URL:", self.url_input)
        scan_btn = QPushButton("Scan URL")
        scan_btn.setObjectName("SuccessButton")
        scan_btn.clicked.connect(self._scan_url_clicked)
        fl.addRow("", scan_btn)
        self.scan_result = QPlainTextEdit()
        self.scan_result.setReadOnly(True)
        self.scan_result.setMaximumHeight(100)
        fl.addRow(self.scan_result)
        layout.addWidget(gb)
        layout.addStretch()
        return w

    def _quick_scan_clicked(self):
        import os
        folder = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Downloads")
        self._run_folder_scan(folder)

    def _full_scan_clicked(self):
        folder = os.path.expanduser("~")
        self._run_folder_scan(folder)

    def _run_folder_scan(self, folder: str):
        self.scan_progress.setVisible(True)
        self.scan_progress.setRange(0, 0)
        self.btn_quick_scan.setEnabled(False)
        self.btn_full_scan.setEnabled(False)
        thread = QThread()
        worker = FolderScanWorker(folder, [".exe", ".dll", ".bat", ".ps1", ".vbs", ".js", ".msi"], sensitivity_from_string(self.settings.get("sensitivity", "MEDIUM")))
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.threat_found.connect(lambda r, p: self._on_scan_threat(r, p))
        worker.progress.connect(lambda cur, tot: self.scan_progress.setRange(0, tot) or self.scan_progress.setValue(cur))
        worker.finished.connect(lambda: (thread.quit(), self.scan_progress.setVisible(False), self.btn_quick_scan.setEnabled(True), self.btn_full_scan.setEnabled(True)))
        worker.finished.connect(thread.deleteLater)
        self._scan_thread = thread
        self._scan_worker = worker
        thread.start()

    def _on_scan_threat(self, result, path):
        # Check if this is the app itself (self-exclusion)
        from pathlib import Path
        import hashlib
        try:
            file_path = Path(path).resolve()
            # Skip if path matches whitelisted app paths
            if str(file_path) in _APP_PATHS or str(file_path.absolute()) in _APP_PATHS:
                logger.info(f"Skipping self-detection in scan: {path}")
                return
            
            # Skip if file hash matches whitelisted app hashes
            if path.endswith((".exe", ".dll")):
                try:
                    from utils import safe_hash_file
                    file_hash = safe_hash_file(path, max_bytes=10 * 1024 * 1024)
                    if file_hash and file_hash in _APP_HASHES:
                        logger.info(f"Skipping self-detection by hash in scan: {path}")
                        return
                except Exception:
                    try:
                        from utils import safe_hash_file
                        file_hash = safe_hash_file(path, max_bytes=10 * 1024 * 1024)
                        if file_hash and file_hash in _APP_HASHES:
                            logger.info(f"Skipping self-detection by hash in scan: {path}")
                            return
                    except Exception:
                        try:
                            with open(path, "rb") as f:
                                file_hash = hashlib.sha256(f.read()).hexdigest()
                                if file_hash in _APP_HASHES:
                                    logger.info(f"Skipping self-detection by hash in scan: {path}")
                                    return
                        except Exception:
                            pass
        except Exception as e:
            logger.debug(f"Error checking self-exclusion in scan: {e}")
        
        entry = {"time": datetime.now().isoformat(), "type": result.threat_type, "severity": result.severity, "url": path, "message": result.message, "confidence": result.confidence}
        self.threat_log.append(entry)
        self._stats["threats"] += 1
        save_threat_log(self.threat_log)
        self._refresh_stats()
        self._refresh_threat_table()
        self._update_dashboard()

    def _dashboard_vpn_toggle(self):
        if getattr(self, "_vpn_client", None):
            try:
                if self._vpn_client.is_connected():
                    self._vpn_disconnect()
                else:
                    self._vpn_connect()
            except Exception:
                self._vpn_connect()
        else:
            self.tabs.setCurrentIndex(3)
            if hasattr(self, "_notif_mgr"):
                self._notif_mgr.notify("Cyber Defense", "Enable VPN in Settings and choose provider (e.g. AdGuard DNS).", "vpn", "info")

    def _dashboard_realtime_toggle(self):
        self.settings["enable_realtime_monitor"] = not self.settings.get("enable_realtime_monitor", False)
        save_settings(self.settings)
        self._start_optional_services()
        self.btn_realtime_toggle.setText(f"Real-time: {'On' if self.settings['enable_realtime_monitor'] else 'Off'}")
        self.tray_realtime_a.setText(f"Real-time Protection: {'On' if self.settings['enable_realtime_monitor'] else 'Off'}")

    def _threats_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        threats_header = QLabel("Threat history")
        threats_header.setObjectName("SectionHeader")
        layout.addWidget(threats_header)

        self.threat_table = QTableWidget(0, 6)
        self.threat_table.setHorizontalHeaderLabels(["Time", "Severity", "Type", "Location", "Message", "Action"])
        self.threat_table.setAlternatingRowColors(True)
        self.threat_table.setSortingEnabled(True)
        self.threat_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.threat_table.setSelectionMode(QTableWidget.SingleSelection)
        self.threat_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.threat_table.setWordWrap(False)
        self.threat_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.threat_table.customContextMenuRequested.connect(self._threats_context_menu)
        try:
            header = self.threat_table.horizontalHeader()
            header.setStretchLastSection(False)
            header.setSectionResizeMode(0, header.ResizeToContents)  # time
            header.setSectionResizeMode(1, header.ResizeToContents)  # severity
            header.setSectionResizeMode(2, header.ResizeToContents)  # type
            header.setSectionResizeMode(3, header.Stretch)           # location
            header.setSectionResizeMode(4, header.Stretch)           # message
            header.setSectionResizeMode(5, header.ResizeToContents)  # action
        except Exception:
            pass
        # Use compact fixed row heights to avoid large empty gaps when few rows present
        try:
            self.threat_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
            self.threat_table.verticalHeader().setDefaultSectionSize(28)
        except Exception:
            pass
        self.threat_table.setMinimumHeight(240)
        layout.addWidget(self.threat_table)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        clear_btn = QPushButton("Clear log")
        clear_btn.setObjectName("WarningButton")
        clear_btn.setMaximumWidth(140)
        clear_btn.clicked.connect(self._clear_threat_log)
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)
        return w

    def _vpn_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(12)
        # VPN menu header
        vpn_header = QLabel("🔒 VPN & DNS Protection")
        vpn_header.setStyleSheet("font-size: 16px; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(vpn_header)
        layout.addWidget(QLabel("Status"))
        self.lbl_vpn_status = QLabel("Checking...")
        self.lbl_vpn_status.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(self.lbl_vpn_status)
        self.lbl_vpn_killswitch = QLabel("")
        layout.addWidget(self.lbl_vpn_killswitch)
        layout.addWidget(QLabel("Provider:"))
        self.lbl_vpn_provider = QLabel("")
        self.lbl_vpn_provider.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.lbl_vpn_provider)
        # Config picker (WireGuard) - dropdown of available configs
        config_row = QHBoxLayout()
        config_row.addWidget(QLabel("Config:"))
        self.vpn_config_combo = QComboBox()
        self.vpn_config_combo.setMinimumWidth(220)
        self.vpn_config_combo.setToolTip("Select WireGuard config or enter path in Settings")
        self._populate_vpn_config_combo()
        self.vpn_config_combo.currentIndexChanged.connect(self._on_vpn_config_selected)
        config_row.addWidget(self.vpn_config_combo)
        config_row.addStretch()
        layout.addLayout(config_row)
        # Connect/Disconnect buttons
        btn_row = QHBoxLayout()
        self.btn_vpn_connect = QPushButton("Connect")
        self.btn_vpn_connect.setObjectName("SuccessButton")
        self.btn_vpn_connect.clicked.connect(self._vpn_connect)
        self.btn_vpn_disconnect = QPushButton("Disconnect")
        self.btn_vpn_disconnect.setObjectName("WarningButton")
        self.btn_vpn_disconnect.clicked.connect(self._vpn_disconnect)
        btn_row.addWidget(self.btn_vpn_connect)
        btn_row.addWidget(self.btn_vpn_disconnect)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addWidget(QLabel("Config path (Settings):"))
        self.lbl_vpn_config = QLabel("")
        self.lbl_vpn_config.setWordWrap(True)
        self.lbl_vpn_config.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.lbl_vpn_config)
        layout.addWidget(QLabel("Tip: Enable VPN in Settings and choose provider. AdGuard DNS needs no config."))
        layout.addStretch()
        return w

    def _populate_vpn_config_combo(self):
        """Populate VPN config dropdown with WireGuard configs from default folder."""
        from vpn_client import get_available_wireguard_configs
        self.vpn_config_combo.blockSignals(True)
        self.vpn_config_combo.clear()
        self.vpn_config_combo.addItem("(Select or enter path in Settings)", "")
        configs = get_available_wireguard_configs()
        for name, path in configs:
            self.vpn_config_combo.addItem(name, path)
        self.vpn_config_combo.blockSignals(False)

    def _on_vpn_config_selected(self):
        """When user selects a config from dropdown, save to settings and update VPN client."""
        path = self.vpn_config_combo.currentData()
        if path:
            if hasattr(self, "vpn_config_edit"):
                self.vpn_config_edit.setText(path)
            self.settings["vpn_config_path"] = path
            save_settings(self.settings)
            if getattr(self, "_vpn_client", None) and self.settings.get("vpn_provider") != "adguard":
                self._vpn_client.set_config(path)

    def _settings_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        self.cb_clipboard = QCheckBox("Monitor clipboard for URLs")
        self.cb_clipboard.setToolTip("When you copy a link, we scan it automatically.")
        self.cb_tracker = QCheckBox("Tracker detection")
        self.cb_tracker.setToolTip("Warn about known tracking domains (e.g. analytics).")
        self.cb_phishing = QCheckBox("Phishing detection")
        self.cb_phishing.setToolTip("Detect fake login pages and scam URLs.")
        self.cb_download = QCheckBox("Download scanning")
        self.cb_download.setToolTip("Check downloaded files for dangerous types.")
        self.cb_url_scan = QCheckBox("URL scanning")
        self.cb_url_scan.setToolTip("Scan URLs for threats.")
        self.cb_notifications = QCheckBox("Show notifications for threats")
        self.cb_notifications.setToolTip("Show a popup when a threat is detected.")
        self.cb_start_minimized = QCheckBox("Start minimized to tray (recommended)")
        self.cb_start_minimized.setToolTip("Only show the tray icon on startup; double-click tray to open the window.")
        self.cb_autostart = QCheckBox("Start with Windows (autostart)")
        self.cb_autostart.setToolTip("Automatically launch Cyber Defense when Windows starts.")
        self.cb_realtime_monitor = QCheckBox("Real-time file monitoring (Downloads/Desktop)")
        self.cb_realtime_monitor.setToolTip("Watch Downloads and Desktop for new files and scan them immediately.")
        self.cb_auto_updates = QCheckBox("Auto-update threat definitions every 2 hours")
        self.cb_auto_updates.setToolTip("Keep blocklists (ClamAV, URLhaus, PhishTank) up to date.")
        self.cb_behavioral_monitor = QCheckBox("Behavioral monitoring (suspicious process detection)")
        self.cb_behavioral_monitor.setToolTip("Watch for suspicious process patterns (e.g. encoded PowerShell). Optional; requires no extra deps.")
        
        # VPN Provider Selection
        vpn_provider_layout = QHBoxLayout()
        vpn_provider_layout.addWidget(QLabel("VPN Provider:"))
        self.vpn_provider_combo = QComboBox()
        self.vpn_provider_combo.addItems([
            "None (disabled)",
            "AdGuard DNS",
            "Mullvad (open-source)",
            "ProtonVPN",
            "WireGuard (custom)",
            "OpenVPN (custom)"
        ])
        self.vpn_provider_combo.setToolTip("Select your preferred VPN provider or use custom WireGuard/OpenVPN config.")
        vpn_provider_layout.addWidget(self.vpn_provider_combo)
        vpn_provider_layout.addStretch()
        
        self.cb_vpn = QCheckBox("Enable VPN integration")
        self.cb_vpn.setToolTip("Use configured VPN for connect/disconnect from tray.")
        self.cb_vpn_kill_switch = QCheckBox("VPN kill-switch (alert when VPN drops)")
        self.cb_vpn_kill_switch.setToolTip("Show critical alert if VPN disconnects while enabled. No data sent; local-only.")
        self.vpn_config_edit = QLineEdit()
        self.vpn_config_edit.setPlaceholderText("Path to config file (e.g. C:\\Users\\You\\wireguard.conf)")
        self.vpn_config_edit.setToolTip("Full path to your VPN configuration file (for custom providers).")

        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems(["Low", "Medium", "High", "Extreme"])
        self.sensitivity_combo.setToolTip("Medium is recommended. High/Extreme may flag more safe sites.")

        for c in (
            self.cb_clipboard, self.cb_tracker, self.cb_phishing, self.cb_download,
            self.cb_url_scan, self.cb_notifications, self.cb_start_minimized,
            self.cb_autostart,
            self.cb_realtime_monitor, self.cb_auto_updates, self.cb_behavioral_monitor,
            self.cb_vpn, self.cb_vpn_kill_switch,
        ):
            layout.addWidget(c)
        layout.addLayout(vpn_provider_layout)
        layout.addWidget(QLabel("VPN config path (for custom providers):"))
        layout.addWidget(self.vpn_config_edit)
        layout.addWidget(QLabel("Sensitivity:"))
        layout.addWidget(self.sensitivity_combo)

        notif_grp = QGroupBox("Notification controls")
        notif_layout = QVBoxLayout(notif_grp)
        self.cb_notif_mute_file = QCheckBox("Mute file threat notifications")
        self.cb_notif_mute_network = QCheckBox("Mute network/phishing notifications")
        self.cb_notif_mute_vpn = QCheckBox("Mute VPN status notifications")
        self.cb_notif_mute_behavioral = QCheckBox("Mute behavioral alerts")
        self.cb_notif_batch = QCheckBox("Batch similar alerts")
        notif_layout.addWidget(self.cb_notif_mute_file)
        notif_layout.addWidget(self.cb_notif_mute_network)
        notif_layout.addWidget(self.cb_notif_mute_vpn)
        notif_layout.addWidget(self.cb_notif_mute_behavioral)
        notif_layout.addWidget(self.cb_notif_batch)
        notif_layout.addWidget(QLabel("Cooldown (seconds):"))
        self.notif_cooldown_spin = QLineEdit()
        self.notif_cooldown_spin.setPlaceholderText("60")
        self.notif_cooldown_spin.setMaximumWidth(80)
        notif_layout.addWidget(self.notif_cooldown_spin)
        notif_layout.addWidget(QLabel("Notify minimum severity:"))
        self.notif_min_sev_combo = QComboBox()
        self.notif_min_sev_combo.addItems(["Info", "Warning", "Critical"])
        self.notif_min_sev_combo.setToolTip(
            "Lower = noisier, higher = only important alerts. Default is Warning."
        )
        notif_layout.addWidget(self.notif_min_sev_combo)
        layout.addWidget(notif_grp)

        sys_grp = QGroupBox("System Security Check")
        sys_layout = QVBoxLayout(sys_grp)
        sys_btn = QPushButton("Run system security check")
        sys_btn.setObjectName("DefaultButton")
        sys_btn.clicked.connect(self._run_system_scan)
        sys_layout.addWidget(sys_btn)
        clean_btn = QPushButton("Run system cleaner (free space & temp)")
        clean_btn.setObjectName("WarningButton")
        clean_btn.clicked.connect(self._ask_run_system_cleaner)
        sys_layout.addWidget(clean_btn)
        self.sys_result = QPlainTextEdit()
        self.sys_result.setReadOnly(True)
        self.sys_result.setMaximumHeight(120)
        sys_layout.addWidget(self.sys_result)
        layout.addWidget(sys_grp)

        save_btn = QPushButton("Save settings")
        save_btn.setObjectName("SuccessButton")
        save_btn.setToolTip("Apply and save your preferences.")
        save_btn.clicked.connect(self._save_settings_clicked)
        layout.addWidget(save_btn)
        layout.addStretch()
        return w

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("Cyber Defense — Double-click to open, right-click for menu")
        self._update_tray_icon()
        menu = QMenu()
        show_a = menu.addAction("Show")
        show_a.triggered.connect(self.show_normal)
        menu.addAction("Dashboard").triggered.connect(lambda: (self.show_normal(), self.tabs.setCurrentIndex(0)))
        menu.addSeparator()
        self.tray_realtime_a = menu.addAction("Real-time Protection: On")
        self.tray_realtime_a.triggered.connect(self._tray_toggle_realtime)
        self.vpn_connect_a = menu.addAction("VPN: Connect")
        self.vpn_connect_a.triggered.connect(self._vpn_connect)
        self.vpn_disconnect_a = menu.addAction("VPN: Disconnect")
        self.vpn_disconnect_a.triggered.connect(self._vpn_disconnect)
        menu.addSeparator()
        pause_a = menu.addAction("Pause protection")
        pause_a.triggered.connect(self._toggle_pause)
        settings_a = menu.addAction("Settings")
        settings_a.triggered.connect(self._open_settings)
        menu.addSeparator()
        # Optional uninstaller entry – launches uninstall.py / uninstall.bat if present.
        uninstall_a = menu.addAction("Uninstall Cyber Defense…")
        uninstall_a.triggered.connect(self._launch_uninstaller)
        clean_a = menu.addAction("Run system cleaner")
        clean_a.triggered.connect(self._ask_run_system_cleaner)
        menu.addSeparator()
        exit_a = menu.addAction("Quit")
        exit_a.triggered.connect(self._quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _update_tray_icon(self):
        """Update tray icon based on protection status (green=protected, yellow=paused, red=threat)."""
        try:
            if self._paused:
                color = "#fbbf24"
            elif self._stats.get("threats", 0) > 0 and not self._paused:
                color = "#ef4444"
            else:
                color = "#22c55e"
            self.tray.setIcon(QIcon(_make_tray_icon_pixmap(color)))
        except Exception:
            try:
                self.tray.setIcon(QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation))
            except Exception:
                pass

    def _setup_notification_manager(self):
        from notification_manager import NotificationManager, NotificationConfig
        icon_map = [QSystemTrayIcon.Information, QSystemTrayIcon.Warning, QSystemTrayIcon.Critical]

        def show_fn(title, msg, icon_int, msecs):
            if self.tray.isVisible():
                self.tray.showMessage(title, msg, icon_map[min(icon_int, 2)], msecs)

        cfg = NotificationConfig(
            enabled=bool(self.settings.get("enable_notifications", True)),
            cooldown_seconds=float(self.settings.get("notif_cooldown_seconds", 60)),
            batch_similar=bool(self.settings.get("notif_batch_similar", True)),
            mute_file_threats=bool(self.settings.get("notif_mute_file", False)),
            mute_network_threats=bool(self.settings.get("notif_mute_network", False)),
            mute_vpn_status=bool(self.settings.get("notif_mute_vpn", False)),
            mute_behavioral=bool(self.settings.get("notif_mute_behavioral", False)),
            min_severity=(self.settings.get("notif_min_severity") or "warning"),
        )
        self._notif_mgr = NotificationManager(show_fn, cfg)

    def _start_status_timer(self):
        """Periodic timer: update tray icon, VPN status, flush pending notifications."""
        self._status_timer = QTimer(self)
        self._status_timer.timeout.connect(self._on_status_tick)
        self._status_timer.start(5000)

    def _on_status_tick(self):
        self._update_tray_icon()
        if hasattr(self, "_notif_mgr"):
            # Flush a few queued notifications to avoid event-loop overload
            try:
                self._notif_mgr.flush_queue(max_to_show=3)
            except Exception:
                pass
        try:
            if hasattr(self, "lbl_vpn_status") and self.lbl_vpn_status:
                self._refresh_vpn_status()
        except Exception:
            pass

    def _tray_toggle_realtime(self):
        self.settings["enable_realtime_monitor"] = not self.settings.get("enable_realtime_monitor", False)
        save_settings(self.settings)
        self._start_optional_services()
        self.tray_realtime_a.setText(f"Real-time Protection: {'On' if self.settings['enable_realtime_monitor'] else 'Off'}")


    def _tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_normal()

    def _open_settings(self):
        self.show_normal()
        self.tabs.setCurrentIndex(3)

    def _quit(self):
        logger.info("Shutting down Cyber Defense")
        self._service.stop()
        if getattr(self, "_update_scheduler", None):
            try:
                self._update_scheduler.stop()
            except Exception:
                pass
        if getattr(self, "_realtime_monitor", None):
            try:
                self._realtime_monitor.stop()
            except Exception:
                pass
        if getattr(self, "_behavioral_monitor", None):
            try:
                self._behavioral_monitor.stop()
            except Exception:
                pass
        if getattr(self, "_vpn_client", None):
            try:
                self._vpn_client.stop()
            except Exception:
                pass
        if getattr(self, "_status_timer", None):
            try:
                self._status_timer.stop()
            except Exception:
                pass
        save_settings(self.settings)
        save_threat_log(self.threat_log)
        QApplication.quit()

    def _launch_uninstaller(self):
        """Launch the bundled uninstaller (`uninstall.bat` or `uninstall.py`) if present."""
        try:
            from pathlib import Path
            import subprocess
            import sys
            from PyQt5.QtWidgets import QMessageBox

            app_root = Path(getattr(sys, "frozen", False) and sys.executable or __file__).resolve().parent
            bat = app_root / "uninstall.bat"
            py = app_root / "uninstall.py"

            if not bat.exists() and not py.exists():
                QMessageBox.information(self, "Uninstaller not found", "No uninstaller was found in the application folder.")
                return

            reply = QMessageBox.question(
                self,
                "Uninstall Cyber Defense",
                "This will run the uninstaller and attempt to remove application files. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

            # Prefer batch on Windows to get a visible console; otherwise run the Python script.
            if bat.exists():
                if sys.platform == "win32":
                    creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
                else:
                    creationflags = 0
                subprocess.Popen([str(bat)], shell=True, creationflags=creationflags)
            else:
                # Run the Python uninstaller in a new console so the user can see progress.
                exe = sys.executable or "python"
                if sys.platform == "win32":
                    creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
                else:
                    creationflags = 0
                subprocess.Popen([exe, str(py)], creationflags=creationflags)

            QMessageBox.information(self, "Uninstaller launched", "Uninstaller started. The app will now exit.")
            # Exit the application to allow the uninstaller to remove files.
            self._quit()
        except Exception as e:
            try:
                QMessageBox.critical(self, "Uninstall failed", f"Failed to launch uninstaller: {e}")
            except Exception:
                pass

    def closeEvent(self, event):
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        else:
            self._quit()
            event.accept()

    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _apply_settings(self):
        s = self.settings
        self.cb_clipboard.setChecked(bool(s.get("enable_clipboard", True)))
        self.cb_tracker.setChecked(bool(s.get("enable_tracker_check", True)))
        self.cb_phishing.setChecked(bool(s.get("enable_phishing", True)))
        self.cb_download.setChecked(bool(s.get("enable_download_scan", True)))
        self.cb_url_scan.setChecked(bool(s.get("enable_url_scan", True)))
        self.cb_notifications.setChecked(bool(s.get("enable_notifications", True)))
        self.cb_start_minimized.setChecked(bool(s.get("start_minimized", True)))
        self.cb_autostart.setChecked(bool(s.get("enable_autostart", False)))
        self.cb_realtime_monitor.setChecked(bool(s.get("enable_realtime_monitor", False)))
        self.cb_auto_updates.setChecked(bool(s.get("enable_auto_updates", True)))
        self.cb_behavioral_monitor.setChecked(bool(s.get("enable_behavioral_monitor", False)))
        self.cb_vpn.setChecked(bool(s.get("enable_vpn", False)))
        self.cb_vpn_kill_switch.setChecked(bool(s.get("vpn_kill_switch", False)))
        self.vpn_config_edit.setText(s.get("vpn_config_path", "") or "")
        
        # Set VPN provider combo
        provider_map = {
            "none": 0,
            "adguard": 1,
            "mullvad": 2,
            "protonvpn": 3,
            "wireguard": 4,
            "openvpn": 5,
        }
        provider = s.get("vpn_provider", "none").lower()
        self.vpn_provider_combo.setCurrentIndex(provider_map.get(provider, 0))
        
        if hasattr(self, "cb_notif_mute_file"):
            self.cb_notif_mute_file.setChecked(bool(s.get("notif_mute_file", False)))
            self.cb_notif_mute_network.setChecked(bool(s.get("notif_mute_network", True)))
            self.cb_notif_mute_vpn.setChecked(bool(s.get("notif_mute_vpn", True)))
            self.cb_notif_mute_behavioral.setChecked(bool(s.get("notif_mute_behavioral", True)))
            self.cb_notif_batch.setChecked(bool(s.get("notif_batch_similar", True)))
            self.notif_cooldown_spin.setText(str(int(s.get("notif_cooldown_seconds", 120))))
            # Map stored min severity to combo index
            min_sev = (s.get("notif_min_severity") or "critical").lower()
            idx = {"info": 0, "warning": 1, "critical": 2}.get(min_sev, 2)
            self.notif_min_sev_combo.setCurrentIndex(idx)
        sens = s.get("sensitivity", "MEDIUM").capitalize()
        idx = self.sensitivity_combo.findText(sens)
        if idx >= 0:
            self.sensitivity_combo.setCurrentIndex(idx)

    def _save_settings_clicked(self):
        self.settings["enable_clipboard"] = self.cb_clipboard.isChecked()
        self.settings["enable_tracker_check"] = self.cb_tracker.isChecked()
        self.settings["enable_phishing"] = self.cb_phishing.isChecked()
        self.settings["enable_download_scan"] = self.cb_download.isChecked()
        self.settings["enable_url_scan"] = self.cb_url_scan.isChecked()
        self.settings["enable_notifications"] = self.cb_notifications.isChecked()
        self.settings["start_minimized"] = self.cb_start_minimized.isChecked()
        self.settings["enable_autostart"] = self.cb_autostart.isChecked()
        self.settings["enable_realtime_monitor"] = self.cb_realtime_monitor.isChecked()
        self.settings["enable_auto_updates"] = self.cb_auto_updates.isChecked()
        self.settings["enable_behavioral_monitor"] = self.cb_behavioral_monitor.isChecked()
        self.settings["enable_vpn"] = self.cb_vpn.isChecked()
        self.settings["vpn_kill_switch"] = self.cb_vpn_kill_switch.isChecked()
        self.settings["vpn_config_path"] = self.vpn_config_edit.text().strip()
        self.settings["sensitivity"] = self.sensitivity_combo.currentText().upper()
        
        # Save VPN provider
        provider_map_rev = {
            0: "none", 1: "adguard", 2: "mullvad", 3: "protonvpn",
            4: "wireguard", 5: "openvpn"
        }
        self.settings["vpn_provider"] = provider_map_rev.get(self.vpn_provider_combo.currentIndex(), "none")
        
        if hasattr(self, "cb_notif_mute_file"):
            self.settings["notif_mute_file"] = self.cb_notif_mute_file.isChecked()
            self.settings["notif_mute_network"] = self.cb_notif_mute_network.isChecked()
            self.settings["notif_mute_vpn"] = self.cb_notif_mute_vpn.isChecked()
            self.settings["notif_mute_behavioral"] = self.cb_notif_mute_behavioral.isChecked()
            self.settings["notif_batch_similar"] = self.cb_notif_batch.isChecked()
            try:
                self.settings["notif_cooldown_seconds"] = float(self.notif_cooldown_spin.text() or "120")
            except ValueError:
                self.settings["notif_cooldown_seconds"] = 120.0
            # Persist minimum severity
            sev_map = {0: "info", 1: "warning", 2: "critical"}
            self.settings["notif_min_severity"] = sev_map.get(self.notif_min_sev_combo.currentIndex(), "critical")
        
        # Handle Windows autostart
        if sys.platform == "win32":
            self._set_windows_autostart(self.settings["enable_autostart"])
        
        save_settings(self.settings)
        if hasattr(self, "_notif_mgr"):
            from notification_manager import NotificationConfig
            self._notif_mgr.update_config(NotificationConfig(
                enabled=bool(self.settings.get("enable_notifications", True)),
                cooldown_seconds=float(self.settings.get("notif_cooldown_seconds", 60)),
                batch_similar=bool(self.settings.get("notif_batch_similar", True)),
                mute_file_threats=bool(self.settings.get("notif_mute_file", False)),
                mute_network_threats=bool(self.settings.get("notif_mute_network", False)),
                mute_vpn_status=bool(self.settings.get("notif_mute_vpn", False)),
                mute_behavioral=bool(self.settings.get("notif_mute_behavioral", False)),
                min_severity=(self.settings.get("notif_min_severity") or "warning"),
            ))
        self._service.update_settings(
            sensitivity=sensitivity_from_string(self.settings["sensitivity"]),
            enable_clipboard=self.settings["enable_clipboard"],
            enable_tracker_check=self.settings["enable_tracker_check"],
        )
        enable_vpn = self.settings.get("enable_vpn", False)
        provider = self.settings.get("vpn_provider", "none").lower()
        config_path = (self.settings.get("vpn_config_path") or "").strip()
        vpn_ready = enable_vpn and (provider == "adguard" or config_path)
        if vpn_ready:
            try:
                from vpn_client import VPNClient
                if getattr(self, "_vpn_client", None):
                    self._vpn_client.stop()
                kill_switch = bool(self.settings.get("vpn_kill_switch", False))
                self._vpn_client = VPNClient(
                    config_path=config_path,
                    provider=provider if provider != "none" else "wireguard",
                    kill_switch=kill_switch,
                    on_vpn_down=self._on_vpn_down,
                )
            except Exception as e:
                logger.debug("VPN client not started: %s", e)
                self._vpn_client = None
        else:
            if getattr(self, "_vpn_client", None):
                try:
                    self._vpn_client.stop()
                except Exception:
                    pass
                self._vpn_client = None
        self._refresh_vpn_status()
        if hasattr(self, "vpn_config_combo"):
            self._populate_vpn_config_combo()
        QMessageBox.information(self, "Settings", "Settings saved.")

    def _set_windows_autostart(self, enabled):
        """Enable or disable Windows autostart via registry."""
        try:
            import winreg
            from pathlib import Path
            
            app_exe = Path(sys.argv[0]).resolve()
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "CyberDefense"
            
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            
            with key:
                if enabled:
                    # Add autostart entry
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, str(app_exe))
                    logger.info("Added autostart registry entry for CyberDefense")
                else:
                    # Remove autostart entry
                    try:
                        winreg.DeleteValue(key, app_name)
                        logger.info("Removed autostart registry entry for CyberDefense")
                    except FileNotFoundError:
                        pass  # Entry doesn't exist, which is fine
        except Exception as e:
            logger.error("Failed to set Windows autostart: %s", e)

    def _start_monitoring(self):
        self._service.start()

    def _start_optional_services(self):
        """Start update scheduler and optional real-time file monitor (silent unless critical)."""
        if self.settings.get("enable_auto_updates", True):
            try:
                from update_system import UpdateScheduler
                self._update_scheduler = UpdateScheduler(
                    on_progress=lambda msg: logger.debug("Update: %s", msg),
                    on_done=lambda r: logger.info("Definitions updated: %s", r),
                )
                self._update_scheduler.start()
            except Exception as e:
                logger.debug("Update scheduler not started: %s", e)
                self._update_scheduler = None
        else:
            self._update_scheduler = None

        if self.settings.get("enable_realtime_monitor", False):
            try:
                from realtime_monitor import RealtimeFileMonitor, get_default_watch_paths
                from ransomware_shield import ensure_honeypot_files
                ensure_honeypot_files()
                watch_paths = get_default_watch_paths()
                self._realtime_monitor = RealtimeFileMonitor(
                    watch_paths=watch_paths,
                    on_threat=self._on_file_threat,
                )
                self._realtime_monitor.start()
            except Exception as e:
                logger.debug("Realtime monitor not started: %s", e)
                self._realtime_monitor = None
        else:
            self._realtime_monitor = None

        if self.settings.get("enable_behavioral_monitor", False):
            try:
                from detection.behavioral import BehavioralMonitor
                self._behavioral_monitor = BehavioralMonitor(
                    on_suspicious=lambda r: self._on_behavioral_threat(r),
                )
                self._behavioral_monitor.start()
            except Exception as e:
                logger.debug("Behavioral monitor not started: %s", e)
                self._behavioral_monitor = None
        else:
            self._behavioral_monitor = None

        enable_vpn = self.settings.get("enable_vpn", False)
        provider = self.settings.get("vpn_provider", "none").lower()
        config_path = (self.settings.get("vpn_config_path") or "").strip()
        vpn_ready = enable_vpn and (provider == "adguard" or config_path)
        if vpn_ready:
            try:
                from vpn_client import VPNClient
                kill_switch = bool(self.settings.get("vpn_kill_switch", False))
                self._vpn_client = VPNClient(
                    config_path=config_path,
                    provider=provider if provider != "none" else "wireguard",
                    kill_switch=kill_switch,
                    on_vpn_down=self._on_vpn_down,
                )
            except Exception as e:
                logger.debug("VPN client not started: %s", e)
                self._vpn_client = None
        else:
            self._vpn_client = None
        self._refresh_dashboard_buttons()

    def _refresh_dashboard_buttons(self):
        try:
            self.btn_realtime_toggle.setText(f"Real-time: {'On' if self.settings.get('enable_realtime_monitor') else 'Off'}")
            self.tray_realtime_a.setText(f"Real-time Protection: {'On' if self.settings.get('enable_realtime_monitor') else 'Off'}")
            if getattr(self, "_vpn_client", None):
                try:
                    connected = self._vpn_client.is_connected()
                    self.btn_vpn_toggle.setText("VPN: Disconnect" if connected else "VPN: Connect")
                except Exception:
                    self.btn_vpn_toggle.setText("VPN: Connect")
            else:
                self.btn_vpn_toggle.setText("VPN: Connect")
        except Exception:
            pass

    def _on_vpn_down(self):
        """Kill-switch: VPN dropped while expected on. Alert user (no telemetry)."""
        if self._paused:
            return
        if hasattr(self, "_notif_mgr"):
            self._notif_mgr.notify("Cyber Defense – VPN", "VPN connection dropped. Traffic may be exposed.", "vpn", "critical")

    def _vpn_connect(self):
        if not getattr(self, "_vpn_client", None):
            if hasattr(self, "_notif_mgr"):
                self._notif_mgr.notify("Cyber Defense", "Enable VPN in Settings and set config path first.", "vpn", "warning")
            return
        self._set_vpn_ui_busy(True, "Connecting…")
        thread = QThread()
        worker = VPNConnectWorker(self._vpn_client, True)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(lambda ok, msg: self._on_vpn_action_done(thread, worker, ok, msg))
        thread.start()

    def _vpn_disconnect(self):
        if not getattr(self, "_vpn_client", None):
            if hasattr(self, "_notif_mgr"):
                self._notif_mgr.notify("Cyber Defense", "VPN not configured.", "vpn", "info")
            return
        self._set_vpn_ui_busy(True, "Disconnecting…")
        thread = QThread()
        worker = VPNConnectWorker(self._vpn_client, False)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(lambda ok, msg: self._on_vpn_action_done(thread, worker, ok, msg))
        thread.start()

    def _set_vpn_ui_busy(self, busy: bool, status_text: str = "") -> None:
        try:
            if hasattr(self, "btn_vpn_connect"):
                self.btn_vpn_connect.setEnabled(not busy)
            if hasattr(self, "btn_vpn_disconnect"):
                self.btn_vpn_disconnect.setEnabled(not busy)
            if hasattr(self, "btn_vpn_toggle"):
                self.btn_vpn_toggle.setEnabled(not busy)
            if status_text and hasattr(self, "lbl_vpn_status"):
                self.lbl_vpn_status.setText(status_text)
        except Exception:
            pass

    def _on_vpn_action_done(self, thread: QThread, worker: QObject, ok: bool, msg: str) -> None:
        try:
            thread.quit()
            thread.wait(2000)
        except Exception:
            pass
        try:
            worker.deleteLater()
            thread.deleteLater()
        except Exception:
            pass
        self._set_vpn_ui_busy(False)
        self._refresh_vpn_status()
        self._refresh_dashboard_buttons()
        if hasattr(self, "_notif_mgr"):
            self._notif_mgr.notify(
                "Cyber Defense – VPN",
                msg or ("Connected" if ok else "VPN action failed"),
                "vpn",
                "info" if ok else "warning",
            )

    def _on_file_threat(self, result: ThreatResult, path: str):
        """Called when real-time monitor detects a file threat; notify and optionally quarantine."""
        if self._paused:
            return
        # Avoid "self-detection": never quarantine or spam-alert our own app files/folder.
        # This commonly happens when the app is run from Downloads/Temp and entropy heuristics flag packed DLLs.
        try:
            p = Path(path).resolve()
            app_root = Path(_APP_ROOT).resolve()
            if str(p).lower().startswith(str(app_root).lower()):
                logger.info("Self-file excluded from actions: %s", p)
                return
            # Also exclude PyInstaller internal bundle folders if user runs from extracted ZIP
            if any(part.lower() in ("cyberdefense", "_internal") for part in p.parts[-3:]) and p.name.lower().endswith((".dll", ".exe")):
                # If the file is inside a CyberDefense bundle folder, treat it as self
                # (prevents quarantining python dlls like pywintypes*.dll)
                bundle_hint = [x.lower() for x in p.parts]
                if "cyberdefense" in bundle_hint and "_internal" in bundle_hint:
                    logger.info("Self-bundle excluded from actions: %s", p)
                    return
        except Exception:
            pass
        # Limit in-memory log to 1000 (overload protection)
        if len(self.threat_log) > 1000:
            self.threat_log = self.threat_log[-900:]
        entry = {
            "time": datetime.now().isoformat(),
            "type": result.threat_type,
            "severity": result.severity,
            "url": path,  # location for UI
            "message": result.message,
            "confidence": result.confidence,
            "action": "",
        }
        self.threat_log.append(entry)
        self._stats["threats"] += 1
        save_threat_log(self.threat_log)
        self._refresh_stats()
        self._refresh_threat_table()
        self._update_dashboard()
        if hasattr(self, "_notif_mgr"):
            loc = path or result.details.get("filepath") or ""
            self._notif_mgr.notify(
                "Cyber Defense",
                f"File threat: {result.message[:60]} | {loc}",
                "file",
                "warning",
            )
        # Default action: quarantine (copy) to reduce risk; user can restore from the Threats context menu.
        if result.details.get("filepath") or path:
            try:
                from quarantine import quarantine_file
                q = quarantine_file(
                    path,
                    threat_type=result.threat_type,
                    threat_message=result.message,
                    copy_instead_of_move=True,
                )
                if "error" not in q:
                    entry["action"] = "Quarantined"
                    entry["quarantine_path"] = q.get("quarantine_path")
                    entry["quarantine_meta"] = q.get("metadata_path")
                    logger.info("Quarantined: %s", q.get("quarantine_path"))
                else:
                    entry["action"] = "Detected"
            except Exception:
                entry["action"] = "Detected"

    def _on_behavioral_threat(self, result: ThreatResult):
        """Called when behavioral monitor detects a suspicious process."""
        if self._paused:
            return
        # Ignore noise from core system processes and require multiple hits
        # within a short window to avoid spamming for transient blips.
        name = (result.details.get("name") or "").lower()
        SYSTEM_WHITELIST = {
            "system idle process",
            "system",
            "svchost.exe",
            "csrss.exe",
            "wininit.exe",
            "services.exe",
        }
        if name in SYSTEM_WHITELIST:
            return

        # Rate-limit behavioral alerts per process/reason
        now = time.monotonic()
        window_sec = 60.0
        required_hits = 3
        key = name or (result.details.get("reason") or "unknown")
        if not hasattr(self, "_behavioral_hits"):
            self._behavioral_hits = {}
        hit = self._behavioral_hits.get(key, {"count": 0, "first": now})
        if now - hit["first"] > window_sec:
            hit = {"count": 0, "first": now}
        hit["count"] += 1
        self._behavioral_hits[key] = hit
        if hit["count"] < required_hits:
            return

        detail = name or result.details.get("reason") or "suspicious process"
        if len(self.threat_log) > 1000:
            self.threat_log = self.threat_log[-900:]
        entry = {
            "time": datetime.now().isoformat(),
            "type": result.threat_type,
            "severity": result.severity,
            "url": f"Process: {detail}",
            "message": result.message,
            "confidence": result.confidence,
        }
        self.threat_log.append(entry)
        self._stats["threats"] += 1
        save_threat_log(self.threat_log)
        self._refresh_stats()
        self._refresh_threat_table()
        self._update_dashboard()
        if hasattr(self, "_notif_mgr"):
            self._notif_mgr.notify(
                "Cyber Defense",
                f"Behavior: {result.message[:60]} | Process: {detail}",
                "behavioral",
                "warning",
            )

    def _toggle_pause(self):
        self._paused = not self._paused
        if self._paused:
            self._service.stop()
        else:
            self._service.start()
        if hasattr(self, "lbl_protection"):
            self.lbl_protection.setText("PAUSED" if self._paused else "ON")
        self._update_tray_icon()

    def _on_threat_detected(self, result: ThreatResult, url: str):
        if self._paused:
            return
        
        # Check if this is the app itself (self-exclusion)
        from pathlib import Path
        import hashlib
        try:
            file_path = Path(url).resolve()
            # Skip if path matches whitelisted app paths
            if str(file_path) in _APP_PATHS or str(file_path.absolute()) in _APP_PATHS:
                logger.info(f"Skipping self-detection: {url}")
                return
            
            # Skip if file hash matches whitelisted app hashes
            if url.endswith((".exe", ".dll")):
                try:
                    with open(url, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        if file_hash in _APP_HASHES:
                            logger.info(f"Skipping self-detection by hash: {url}")
                            return
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Error checking self-exclusion: {e}")
        
        logger.info(f"Threat detected: {result.threat_type} - {url[:50]}... (confidence: {result.confidence}%)")
        if len(self.threat_log) > 1000:
            self.threat_log = self.threat_log[-900:]
        entry = {
            "time": datetime.now().isoformat(),
            "type": result.threat_type,
            "severity": result.severity,
            "url": url,  # location for UI
            "message": result.message,
            "confidence": result.confidence,
        }
        self.threat_log.append(entry)
        self._stats["threats"] += 1
        if result.threat_type == "tracker":
            self._stats["trackers"] += 1
        elif result.threat_type == "phishing":
            self._stats["phishing"] += 1
        save_threat_log(self.threat_log)
        self._refresh_stats()
        self._refresh_threat_table()
        self._update_dashboard()
        if hasattr(self, "_notif_mgr"):
            cat = "network" if result.threat_type in ("phishing", "tracker") else "other"
            self._notif_mgr.notify(
                "Cyber Defense",
                f"{result.threat_type.upper()}: {result.message[:80]} | {url}",
                cat,
                "warning",
            )

    def _refresh_stats(self):
        self.lbl_threats.setText(str(self._stats['threats']))
        self.lbl_trackers.setText(str(self._stats['trackers']))
        self.lbl_phishing.setText(str(self._stats['phishing']))
        if hasattr(self, "lbl_protection"):
            self.lbl_protection.setText("PAUSED" if self._paused else "ON")

    def _refresh_threat_table(self):
        t = self.threat_table
        t.setRowCount(0)
        
        # Filter threats based on show_only_threats setting
        show_only_threats = self.settings.get("show_only_threats", True)
        threats_to_show = []
        
        for e in reversed(self.threat_log[-400:]):
            # If show_only_threats is enabled, filter out low-severity/info entries
            if show_only_threats:
                severity = (e.get("severity", "") or "").lower()
                # Only show warning, high, critical
                if severity not in ["warning", "high", "critical"]:
                    continue
            threats_to_show.append(e)
        
        for e in threats_to_show:
            row = t.rowCount()
            t.insertRow(row)
            time_item = QTableWidgetItem(e.get("time", "")[:19])
            sev_item = QTableWidgetItem((e.get("severity", "") or "").upper())
            type_item = QTableWidgetItem(e.get("type", "") or "")
            loc = e.get("url", "") or ""
            msg = e.get("message", "") or ""
            loc_item = QTableWidgetItem(loc)
            msg_item = QTableWidgetItem(msg)
            action_item = QTableWidgetItem(e.get("action", "") or "")

            # Store full entry for context menu actions
            try:
                loc_item.setData(Qt.UserRole, dict(e))
            except Exception:
                pass

            t.setItem(row, 0, time_item)
            t.setItem(row, 1, sev_item)
            t.setItem(row, 2, type_item)
            t.setItem(row, 3, loc_item)
            t.setItem(row, 4, msg_item)
            t.setItem(row, 5, action_item)
            # Enforce compact row height to avoid large gaps
            try:
                default_h = t.verticalHeader().defaultSectionSize() or 28
                t.setRowHeight(row, default_h)
            except Exception:
                pass

    def _update_dashboard(self):
        lines = [
            f"Threats: {self._stats['threats']} | Trackers: {self._stats['trackers']} | Phishing: {self._stats['phishing']}",
            "",
            "Recent entries:",
        ]
        for e in list(reversed(self.threat_log))[:10]:
            lines.append(f"  [{e.get('type', '?')}] {e.get('message', '')[:60]}")
        self.dashboard_text.setPlainText("\n".join(lines))

    def _clear_threat_log(self):
        self.threat_log.clear()
        self._stats = {"threats": 0, "trackers": 0, "phishing": 0}
        save_threat_log(self.threat_log)
        self._refresh_stats()
        self._refresh_threat_table()
        self._update_dashboard()
        self.dashboard_text.clear()
        QMessageBox.information(self, "Threats", "Log cleared.")

    def _threats_context_menu(self, pos):
        """Right-click context menu for Threats table."""
        try:
            idx = self.threat_table.indexAt(pos)
            if not idx.isValid():
                return
            row = idx.row()
            loc_item = self.threat_table.item(row, 3)
            if not loc_item:
                return
            entry = loc_item.data(Qt.UserRole) or {}
            location = (entry.get("url") or "").strip()
            q_path = (entry.get("quarantine_path") or "").strip()

            menu = QMenu(self)
            act_open_folder = menu.addAction("Open folder")
            act_quarantine = menu.addAction("Quarantine (copy)")
            act_delete_file = menu.addAction("Delete file (permanently)")
            act_restore = menu.addAction("Restore from quarantine")
            act_ignore = menu.addAction("Ignore (mark)")
            menu.addSeparator()
            act_delete_q = menu.addAction("Delete from quarantine")
            act_run_cleaner = menu.addAction("Run system cleaner")

            # Enable/disable based on data
            act_open_folder.setEnabled(bool(location))
            act_quarantine.setEnabled(bool(location))
            act_delete_file.setEnabled(bool(location))
            act_restore.setEnabled(bool(q_path))
            act_delete_q.setEnabled(bool(q_path))

            chosen = menu.exec_(self.threat_table.viewport().mapToGlobal(pos))
            if not chosen:
                return

            if chosen == act_open_folder:
                self._open_location_folder(location)
            elif chosen == act_quarantine:
                self._quarantine_location(row, location, entry)
            elif chosen == act_delete_file:
                self._delete_threat_file(row, location, entry)
            elif chosen == act_restore:
                self._restore_quarantined(row, q_path, entry)
            elif chosen == act_delete_q:
                self._delete_quarantined(row, q_path, entry)
            elif chosen == act_run_cleaner:
                self._ask_run_system_cleaner()
            elif chosen == act_ignore:
                self._mark_threat_action(row, entry, "Ignored")
        except Exception:
            # Never let UI context menu crash the app
            return

    def _open_location_folder(self, location: str) -> None:
        try:
            p = Path(location)
            folder = p.parent if p.exists() else Path(location).parent
            if sys.platform == "win32":
                os.startfile(str(folder))  # type: ignore[attr-defined]
            else:
                import subprocess
                subprocess.run(["xdg-open", str(folder)], timeout=3)
        except Exception:
            pass

    def _delete_threat_file(self, row: int, location: str, entry: dict) -> None:
        """Permanently delete the threat file on disk (asks for confirmation)."""
        try:
            if not location:
                return
            p = Path(location)
            if not p.exists():
                QMessageBox.information(self, "Delete file", "File not found on disk.")
                return
            reply = QMessageBox.question(self, "Delete file",
                                         f"Permanently delete '{p.name}'? This cannot be undone.",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
            try:
                # Attempt secure delete if available: overwrite simple then delete
                try:
                    with open(p, "r+b") as fh:
                        sz = fh.seek(0, os.SEEK_END)
                        fh.seek(0)
                        fh.write(b"\x00" * max(1, min(4096, sz)))
                except Exception:
                    pass
                p.unlink()
                self._mark_threat_action(row, entry, "Deleted")
                QMessageBox.information(self, "Delete", "File deleted.")
            except Exception as e:
                QMessageBox.warning(self, "Delete", f"Failed to delete file: {e}")
        except Exception:
            pass

    def _quarantine_location(self, row: int, location: str, entry: dict) -> None:
        try:
            from quarantine import quarantine_file
            q = quarantine_file(
                location,
                threat_type=entry.get("type", "unknown"),
                threat_message=entry.get("message", ""),
                copy_instead_of_move=True,
            )
            if "error" in q:
                QMessageBox.warning(self, "Quarantine", f"Failed: {q.get('error')}")
                self._mark_threat_action(row, entry, "Detected")
                return
            entry["quarantine_path"] = q.get("quarantine_path")
            entry["quarantine_meta"] = q.get("metadata_path")
            self._mark_threat_action(row, entry, "Quarantined")
        except Exception as e:
            QMessageBox.warning(self, "Quarantine", f"Failed: {e}")

    def _restore_quarantined(self, row: int, q_path: str, entry: dict) -> None:
        try:
            from quarantine import restore_from_quarantine
            r = restore_from_quarantine(q_path)
            if not r.get("success"):
                QMessageBox.warning(self, "Restore", r.get("message", "Restore failed"))
                return
            self._mark_threat_action(row, entry, "Restored")
        except Exception as e:
            QMessageBox.warning(self, "Restore", f"Failed: {e}")

    def _delete_quarantined(self, row: int, q_path: str, entry: dict) -> None:
        try:
            from quarantine import delete_from_quarantine
            r = delete_from_quarantine(q_path, secure=False)
            if not r.get("success"):
                QMessageBox.warning(self, "Delete", r.get("message", "Delete failed"))
                return
            self._mark_threat_action(row, entry, "Deleted")
        except Exception as e:
            QMessageBox.warning(self, "Delete", f"Failed: {e}")

    def _mark_threat_action(self, row: int, entry: dict, action: str) -> None:
        """Update the threat entry and refresh UI."""
        entry["action"] = action
        # Update the matching entry in the in-memory log (by time+url+message)
        key = (entry.get("time"), entry.get("url"), entry.get("message"))
        for e in self.threat_log:
            if (e.get("time"), e.get("url"), e.get("message")) == key:
                e.update(entry)
                break
        save_threat_log(self.threat_log)
        self._refresh_threat_table()

    def _scan_url_clicked(self):
        url = (self.url_input.text() or "").strip()
        if not url:
            self.scan_result.setPlainText("Enter a URL first.")
            return
        sens = sensitivity_from_string(self.settings.get("sensitivity", "MEDIUM"))
        r = scan_url(url, sens)
        lines = [
            f"URL: {url}",
            f"Threat: {r.is_threat}",
            f"Type: {r.threat_type}",
            f"Severity: {r.severity}",
            f"Confidence: {r.confidence}%",
            f"Message: {r.message}",
        ]
        self.scan_result.setPlainText("\n".join(lines))
        if r.is_threat:
            self._on_threat_detected(r, url)

    def _run_system_scan(self):
        self.sys_result.setPlainText("Running system security check...")
        QApplication.processEvents()
        summary = get_system_security_summary()
        lines = ["System Security Summary", ""]
        lines.append(f"Firewall active: {summary.get('firewall_active')}")
        lines.append(f"Defender active: {summary.get('defender_active')}")
        lines.append("")
        for msg in summary.get("issues", []):
            lines.append(f"⚠️ {msg}")
        for msg in summary.get("recommendations", []):
            lines.append(f"💡 {msg}")
        self.sys_result.setPlainText("\n".join(lines))

    def _ask_run_system_cleaner(self):
        try:
            reply = QMessageBox.question(
                self,
                "Run System Cleaner",
                "This will run a system cleanup (delete temp files, clear SoftwareDistribution downloads, empty Recycle Bin). Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
            self._run_system_cleaner()
        except Exception:
            pass

    def _run_system_cleaner(self):
        """Locate and launch the bundled `tools\system_cleaner.bat` with elevation on Windows.
        If not on Windows, attempt to perform simple temp cleanup where possible.
        """
        try:
            script = _APP_ROOT / "tools" / "system_cleaner.bat"
            if sys.platform == "win32" and script.exists():
                try:
                    # Use ShellExecute to elevate
                    import ctypes
                    params = str(script)
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", str(script), None, None, 1)
                    QMessageBox.information(self, "Cleaner", "System cleaner launched (may require admin).")
                    return
                except Exception as e:
                    QMessageBox.warning(self, "Cleaner", f"Failed to launch cleaner: {e}")
                    return
            # Non-windows fallback: attempt to remove /tmp and user temp
            if script.exists() is False and sys.platform != "win32":
                try:
                    import shutil
                    t1 = Path(os.environ.get('TMP', '/tmp'))
                    if t1.exists():
                        shutil.rmtree(str(t1), ignore_errors=True)
                        t1.mkdir(parents=True, exist_ok=True)
                    QMessageBox.information(self, "Cleaner", "Temporary folders cleaned (best-effort).")
                    return
                except Exception as e:
                    QMessageBox.warning(self, "Cleaner", f"Failed to clean temp folders: {e}")
                    return
            QMessageBox.information(self, "Cleaner", "Cleaner script not found or unsupported platform.")
        except Exception as e:
            try:
                QMessageBox.warning(self, "Cleaner", f"Cleaner failed: {e}")
            except Exception:
                pass

    def _refresh_vpn_status(self):
        try:
            from vpn_client import is_vpn_or_dns_connected
            provider = self.settings.get("vpn_provider", "none").lower()
            provider_names = {"adguard": "AdGuard DNS", "wireguard": "WireGuard", "openvpn": "OpenVPN",
                             "mullvad": "Mullvad", "protonvpn": "ProtonVPN", "none": "None"}
            connected = is_vpn_or_dns_connected(provider) if provider != "none" else False
            self.lbl_vpn_status.setText("Connected" if connected else "Disconnected")
            self.lbl_vpn_status.setStyleSheet("color: #22c55e;" if connected else "color: #94a3b8;")
            if hasattr(self, "lbl_vpn_provider"):
                self.lbl_vpn_provider.setText(provider_names.get(provider, provider) + " (from Settings)")
            cfg = self.settings.get("vpn_config_path", "") or "(not set)" if provider != "adguard" else "N/A - AdGuard uses system DNS"
            self.lbl_vpn_config.setText(cfg[:80] + "..." if len(cfg) > 80 else cfg)
            kill = "Kill-switch: On" if self.settings.get("vpn_kill_switch") else "Kill-switch: Off"
            self.lbl_vpn_killswitch.setText(kill)
        except Exception:
            self.lbl_vpn_status.setText("Unknown")

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_threat_table()
        self._update_dashboard()
        self._refresh_vpn_status()


def main():
    logger.info("Starting Cyber Defense v%s", APP_VERSION)
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Python: {sys.version}")
    
    # Enable high-DPI scaling and high-DPI pixmaps for crisp UI on modern displays
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("Cyber Defense")
    try:
        from PyQt5.QtGui import QFont
        app.setFont(QFont("Segoe UI", 9))
    except Exception:
        pass

    # Load and set application icon (prefer valid PNG; fallback to SVG rendering).
    try:
        png_icon = _APP_ROOT / "icons" / "cyberdefense_logo_256.png"
        svg_icon = _APP_ROOT / "icons" / "cyberdefense_logo.svg"
        loaded = False
        if png_icon.exists():
            try:
                ic = QIcon(str(png_icon))
                if not ic.isNull():
                    app.setWindowIcon(ic)
                    loaded = True
            except Exception:
                loaded = False
        if (not loaded) and svg_icon.exists():
            try:
                # Render SVG to pixmap and use as icon (works when PNG is missing or corrupted)
                from PyQt5.QtSvg import QSvgRenderer
                renderer = QSvgRenderer(str(svg_icon))
                pix = QPixmap(256, 256)
                pix.fill(Qt.transparent)
                painter = QPainter(pix)
                renderer.render(painter)
                painter.end()
                app.setWindowIcon(QIcon(pix))
            except Exception:
                pass
    except Exception:
        pass
    
    # Try to load bundled QSS for a polished dark theme, fallback to inline
    try:
        qss_path = _APP_ROOT / "dark_theme.qss"
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        else:
            try:
                app.setStyle("Fusion")
            except Exception:
                pass
            app.setStyleSheet("""
                * { font-family: 'Segoe UI Variable', 'Segoe UI', Arial, sans-serif; }
                QMainWindow, QWidget { background-color: #0b0f14; color: #e5e7eb; }
                QLabel { color: #e5e7eb; background-color: transparent; }
            """)
    except Exception as e:
        logger.warning("Failed to load theme file: %s", e)
        try:
            app.setStyle("Fusion")
        except Exception:
            pass
    
    try:
        logger.info("Creating main window...")
        win = CyberDefenseApp()
        
        # Center the window on screen
        from PyQt5.QtWidgets import QDesktopWidget
        center = QDesktopWidget().availableGeometry().center()
        frame = win.frameGeometry()
        frame.moveCenter(center)
        win.move(frame.topLeft())
        
        # Tray-first: start minimized if setting (nobody wants a window popping up every ping)
        if win.settings.get("start_minimized", True):
            win.show()  # needed for tray to have a parent
            win.hide()
            logger.info("Application started in tray (start minimized)")
        else:
            win.show()
            win.raise_()
            win.activateWindow()
            logger.info("Application window shown")
        return app.exec_()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        # Show error dialog
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Error", f"Failed to start application:\n\n{str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
