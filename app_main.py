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

APP_VERSION = "2.2.0"

from threat_engine import (
    ThreatResult,
    Sensitivity,
    scan_url,
    analyze_download,
    get_system_security_summary,
)
from background_service import BackgroundService


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
        "vpn_config_path": "",
        "vpn_kill_switch": False,
        "notif_cooldown_seconds": 25.0,
        "notif_batch_similar": True,
        "notif_mute_file": False,
        "notif_mute_network": False,
        "notif_mute_vpn": False,
        "notif_mute_behavioral": False,
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

    def __init__(self, config_path: str, connect: bool):
        super().__init__()
        self.config_path = config_path
        self.connect = connect

    def run(self):
        try:
            if self.connect:
                from vpn_client import connect_wireguard
                ok, msg = connect_wireguard(self.config_path)
            else:
                from vpn_client import disconnect_wireguard
                ok, msg = disconnect_wireguard(self.config_path)
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

        self._build_ui()
        self._setup_tray()
        self._setup_notification_manager()
        self._apply_settings()
        self._refresh_stats()
        self._start_monitoring()
        self._start_optional_services()
        self._start_status_timer()

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
    
    def _create_stat_number(self, value: str, color: str) -> QLabel:
        """Create a stat number label."""
        label = QLabel(value)
        label.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {color};
            background: transparent;
        """)
        return label
    
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Top bar with header and controls
        top_bar = QWidget()
        top_bar.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4f46e5, stop:0.35 #6366f1, stop:0.7 #818cf8, stop:1 #a5b4fc);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid rgba(255,255,255,0.12);
        """)
        top_layout = QHBoxLayout(top_bar)
        
        # Left side - Title and subtitle
        title_container = QWidget()
        title_container.setStyleSheet("background: transparent;")
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(4)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("🛡️ Cyber Defense")
        header.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            background: transparent;
            letter-spacing: 0.5px;
        """)
        title_layout.addWidget(header)
        
        subheader = QLabel("Real-time protection · Phishing · Trackers · File monitoring · VPN")
        subheader.setStyleSheet("""
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
        """)
        title_layout.addWidget(subheader)
        
        version_lbl = QLabel(f"v{APP_VERSION}")
        version_lbl.setStyleSheet("""
            font-size: 11px;
            color: rgba(255, 255, 255, 0.7);
            background: transparent;
        """)
        title_layout.addWidget(version_lbl)
        
        top_layout.addWidget(title_container)
        top_layout.addStretch()
        
        # Right side - Status badge
        status_badge = QWidget()
        status_badge.setStyleSheet("""
            background-color: rgba(74, 222, 128, 0.2);
            border: 1px solid rgba(74, 222, 128, 0.6);
            border-radius: 10px;
            padding: 10px 18px;
        """)
        status_badge_layout = QHBoxLayout(status_badge)
        status_badge_layout.setSpacing(8)
        
        status_icon = QLabel("✓")
        status_icon.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #4ade80;
            background: transparent;
        """)
        status_badge_layout.addWidget(status_icon)
        
        self.status_label = QLabel("ACTIVE")
        self.status_label.setStyleSheet("""
            font-size: 13px; 
            color: #4ade80; 
            font-weight: 700;
            background: transparent;
            letter-spacing: 1px;
        """)
        status_badge_layout.addWidget(self.status_label)
        
        top_layout.addWidget(status_badge)
        
        layout.addWidget(top_bar)

        # Stats cards with modern gradient design
        stats_container = QWidget()
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setSpacing(20)
        
        # Threats card - Red gradient
        threats_card = self._create_stat_card(
            icon="🔥",
            title="Threats Blocked",
            gradient="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #dc2626, stop:1 #991b1b)",
            glow="rgba(239, 68, 68, 0.3)"
        )
        self.lbl_threats = self._create_stat_number("0", "#ffffff")
        threats_card.layout().addWidget(self.lbl_threats)
        stats_layout.addWidget(threats_card)
        
        # Trackers card - Orange gradient
        trackers_card = self._create_stat_card(
            icon="🚨",
            title="Trackers Found",
            gradient="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f59e0b, stop:1 #d97706)",
            glow="rgba(245, 158, 11, 0.3)"
        )
        self.lbl_trackers = self._create_stat_number("0", "#ffffff")
        trackers_card.layout().addWidget(self.lbl_trackers)
        stats_layout.addWidget(trackers_card)
        
        # Phishing card - Cyan gradient
        phishing_card = self._create_stat_card(
            icon="🎯",
            title="Phishing Detected",
            gradient="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #06b6d4, stop:1 #0891b2)",
            glow="rgba(6, 182, 212, 0.3)"
        )
        self.lbl_phishing = self._create_stat_number("0", "#ffffff")
        phishing_card.layout().addWidget(self.lbl_phishing)
        stats_layout.addWidget(phishing_card)
        
        # Protection status card - green when active
        protection_card = self._create_stat_card(
            icon="🔒",
            title="Protection",
            gradient="qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #059669, stop:1 #047857)",
            glow="rgba(16, 185, 129, 0.3)"
        )
        self.lbl_protection = QLabel("ON")
        self.lbl_protection.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
            background: transparent;
        """)
        protection_card.layout().addWidget(self.lbl_protection)
        stats_layout.addWidget(protection_card)
        
        layout.addWidget(stats_container)

        # Tabs: Dashboard, Threats, Real-time, VPN, Settings
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._dashboard_tab(), "Dashboard")
        self.tabs.addTab(self._threats_tab(), "Threats")
        self.tabs.addTab(self._realtime_tab(), "Real-time")
        self.tabs.addTab(self._vpn_tab(), "VPN")
        self.tabs.addTab(self._settings_tab(), "Settings")
        layout.addWidget(self.tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.btn_pause = QPushButton("⏸ Pause")
        self.btn_pause.setMinimumWidth(120)
        self.btn_pause.clicked.connect(self._toggle_pause)
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setMinimumWidth(120)
        self.btn_settings.clicked.connect(lambda: self.tabs.setCurrentIndex(4))
        self.btn_close = QPushButton("Close")
        self.btn_close.setMinimumWidth(100)
        self.btn_close.clicked.connect(self.close)
        for b in (self.btn_pause, self.btn_settings, self.btn_close):
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

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
        self.btn_quick_scan.setToolTip("Scan Downloads folder in background")
        self.btn_quick_scan.clicked.connect(self._quick_scan_clicked)
        self.btn_full_scan = QPushButton("Full Scan")
        self.btn_full_scan.setToolTip("Scan user folders (may take a while)")
        self.btn_full_scan.clicked.connect(self._full_scan_clicked)
        self.btn_vpn_toggle = QPushButton("VPN: Connect")
        self.btn_vpn_toggle.setToolTip("Connect or disconnect VPN")
        self.btn_vpn_toggle.clicked.connect(self._dashboard_vpn_toggle)
        self.btn_realtime_toggle = QPushButton("Real-time: On")
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
                from vpn_client import is_vpn_connected
                if is_vpn_connected():
                    self._vpn_disconnect()
                else:
                    self._vpn_connect()
            except Exception:
                self._vpn_connect()
        else:
            self.tabs.setCurrentIndex(4)
            self._notif_mgr.notify("Cyber Defense", "Configure VPN in Settings first.", "vpn", "info")

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
        threats_header = QLabel("🔴 Threat history")
        threats_header.setStyleSheet("font-size: 14px; font-weight: 600; color: #94a3b8; margin-bottom: 4px;")
        layout.addWidget(threats_header)
        self.threat_table = QTableWidget(0, 5)
        self.threat_table.setHorizontalHeaderLabels(["Time", "Type", "Severity", "URL / Details", "Message"])
        self.threat_table.horizontalHeader().setStretchLastSection(True)
        self.threat_table.setAlternatingRowColors(True)
        self.threat_table.setMinimumHeight(280)
        layout.addWidget(self.threat_table)
        clear_btn = QPushButton("Clear log")
        clear_btn.setMaximumWidth(120)
        clear_btn.clicked.connect(self._clear_threat_log)
        layout.addWidget(clear_btn)
        return w

    def _realtime_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Monitored folders"))
        self.realtime_paths_text = QPlainTextEdit()
        self.realtime_paths_text.setReadOnly(True)
        self.realtime_paths_text.setMaximumHeight(100)
        self.realtime_paths_text.setPlaceholderText("Enable Real-time Protection in Settings. Monitored paths will appear here.")
        layout.addWidget(self.realtime_paths_text)
        layout.addWidget(QLabel("Recent file threats (last 20)"))
        self.realtime_events_table = QTableWidget(0, 4)
        self.realtime_events_table.setHorizontalHeaderLabels(["Time", "Path", "Type", "Message"])
        self.realtime_events_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.realtime_events_table)
        return w

    def _vpn_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("VPN status"))
        self.lbl_vpn_status = QLabel("Checking...")
        self.lbl_vpn_status.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(self.lbl_vpn_status)
        self.lbl_vpn_killswitch = QLabel("")
        layout.addWidget(self.lbl_vpn_killswitch)
        btn_row = QHBoxLayout()
        self.btn_vpn_connect = QPushButton("Connect")
        self.btn_vpn_connect.clicked.connect(self._vpn_connect)
        self.btn_vpn_disconnect = QPushButton("Disconnect")
        self.btn_vpn_disconnect.clicked.connect(self._vpn_disconnect)
        btn_row.addWidget(self.btn_vpn_connect)
        btn_row.addWidget(self.btn_vpn_disconnect)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addWidget(QLabel("Config path (from Settings):"))
        self.lbl_vpn_config = QLabel("")
        self.lbl_vpn_config.setWordWrap(True)
        layout.addWidget(self.lbl_vpn_config)
        layout.addStretch()
        return w

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
        self.cb_realtime_monitor = QCheckBox("Real-time file monitoring (Downloads/Desktop)")
        self.cb_realtime_monitor.setToolTip("Watch Downloads and Desktop for new files and scan them immediately.")
        self.cb_auto_updates = QCheckBox("Auto-update threat definitions every 2 hours")
        self.cb_auto_updates.setToolTip("Keep blocklists (ClamAV, URLhaus, PhishTank) up to date.")
        self.cb_behavioral_monitor = QCheckBox("Behavioral monitoring (suspicious process detection)")
        self.cb_behavioral_monitor.setToolTip("Watch for suspicious process patterns (e.g. encoded PowerShell). Optional; requires no extra deps.")
        self.cb_vpn = QCheckBox("VPN integration (WireGuard)")
        self.cb_vpn.setToolTip("Use WireGuard config for connect/disconnect from tray. Install WireGuard separately.")
        self.cb_vpn_kill_switch = QCheckBox("VPN kill-switch (alert when VPN drops)")
        self.cb_vpn_kill_switch.setToolTip("Show critical alert if VPN disconnects while enabled. No data sent; local-only.")
        self.vpn_config_edit = QLineEdit()
        self.vpn_config_edit.setPlaceholderText("Path to WireGuard .conf (e.g. C:\\Users\\You\\wg0.conf)")
        self.vpn_config_edit.setToolTip("Full path to your WireGuard configuration file.")

        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems(["Low", "Medium", "High", "Extreme"])
        self.sensitivity_combo.setToolTip("Medium is recommended. High/Extreme may flag more safe sites.")

        for c in (
            self.cb_clipboard, self.cb_tracker, self.cb_phishing, self.cb_download,
            self.cb_url_scan, self.cb_notifications, self.cb_start_minimized,
            self.cb_realtime_monitor, self.cb_auto_updates, self.cb_behavioral_monitor,
            self.cb_vpn, self.cb_vpn_kill_switch,
        ):
            layout.addWidget(c)
        layout.addWidget(QLabel("VPN config path (WireGuard):"))
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
        self.notif_cooldown_spin.setPlaceholderText("25")
        self.notif_cooldown_spin.setMaximumWidth(80)
        notif_layout.addWidget(self.notif_cooldown_spin)
        layout.addWidget(notif_grp)

        sys_grp = QGroupBox("System Security Check")
        sys_layout = QVBoxLayout(sys_grp)
        sys_btn = QPushButton("Run system security check")
        sys_btn.clicked.connect(self._run_system_scan)
        sys_layout.addWidget(sys_btn)
        self.sys_result = QPlainTextEdit()
        self.sys_result.setReadOnly(True)
        self.sys_result.setMaximumHeight(120)
        sys_layout.addWidget(self.sys_result)
        layout.addWidget(sys_grp)

        save_btn = QPushButton("Save settings")
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
            cooldown_seconds=float(self.settings.get("notif_cooldown_seconds", 25)),
            batch_similar=bool(self.settings.get("notif_batch_similar", True)),
            mute_file_threats=bool(self.settings.get("notif_mute_file", False)),
            mute_network_threats=bool(self.settings.get("notif_mute_network", False)),
            mute_vpn_status=bool(self.settings.get("notif_mute_vpn", False)),
            mute_behavioral=bool(self.settings.get("notif_mute_behavioral", False)),
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
        self.tabs.setCurrentIndex(4)

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
        self.cb_realtime_monitor.setChecked(bool(s.get("enable_realtime_monitor", False)))
        self.cb_auto_updates.setChecked(bool(s.get("enable_auto_updates", True)))
        self.cb_behavioral_monitor.setChecked(bool(s.get("enable_behavioral_monitor", False)))
        self.cb_vpn.setChecked(bool(s.get("enable_vpn", False)))
        self.cb_vpn_kill_switch.setChecked(bool(s.get("vpn_kill_switch", False)))
        self.vpn_config_edit.setText(s.get("vpn_config_path", "") or "")
        if hasattr(self, "cb_notif_mute_file"):
            self.cb_notif_mute_file.setChecked(bool(s.get("notif_mute_file", False)))
            self.cb_notif_mute_network.setChecked(bool(s.get("notif_mute_network", False)))
            self.cb_notif_mute_vpn.setChecked(bool(s.get("notif_mute_vpn", False)))
            self.cb_notif_mute_behavioral.setChecked(bool(s.get("notif_mute_behavioral", False)))
            self.cb_notif_batch.setChecked(bool(s.get("notif_batch_similar", True)))
            self.notif_cooldown_spin.setText(str(int(s.get("notif_cooldown_seconds", 25))))
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
        self.settings["enable_realtime_monitor"] = self.cb_realtime_monitor.isChecked()
        self.settings["enable_auto_updates"] = self.cb_auto_updates.isChecked()
        self.settings["enable_behavioral_monitor"] = self.cb_behavioral_monitor.isChecked()
        self.settings["enable_vpn"] = self.cb_vpn.isChecked()
        self.settings["vpn_kill_switch"] = self.cb_vpn_kill_switch.isChecked()
        self.settings["vpn_config_path"] = self.vpn_config_edit.text().strip()
        self.settings["sensitivity"] = self.sensitivity_combo.currentText().upper()
        if hasattr(self, "cb_notif_mute_file"):
            self.settings["notif_mute_file"] = self.cb_notif_mute_file.isChecked()
            self.settings["notif_mute_network"] = self.cb_notif_mute_network.isChecked()
            self.settings["notif_mute_vpn"] = self.cb_notif_mute_vpn.isChecked()
            self.settings["notif_mute_behavioral"] = self.cb_notif_mute_behavioral.isChecked()
            self.settings["notif_batch_similar"] = self.cb_notif_batch.isChecked()
            try:
                self.settings["notif_cooldown_seconds"] = float(self.notif_cooldown_spin.text() or "25")
            except ValueError:
                self.settings["notif_cooldown_seconds"] = 25.0
        save_settings(self.settings)
        if hasattr(self, "_notif_mgr"):
            from notification_manager import NotificationConfig
            self._notif_mgr.update_config(NotificationConfig(
                enabled=bool(self.settings.get("enable_notifications", True)),
                cooldown_seconds=float(self.settings.get("notif_cooldown_seconds", 25)),
                batch_similar=bool(self.settings.get("notif_batch_similar", True)),
                mute_file_threats=bool(self.settings.get("notif_mute_file", False)),
                mute_network_threats=bool(self.settings.get("notif_mute_network", False)),
                mute_vpn_status=bool(self.settings.get("notif_mute_vpn", False)),
                mute_behavioral=bool(self.settings.get("notif_mute_behavioral", False)),
            ))
        self._service.update_settings(
            sensitivity=sensitivity_from_string(self.settings["sensitivity"]),
            enable_clipboard=self.settings["enable_clipboard"],
            enable_tracker_check=self.settings["enable_tracker_check"],
        )
        if self.settings.get("enable_vpn", False) and self.settings.get("vpn_config_path", "").strip():
            try:
                from vpn_client import VPNClient
                if getattr(self, "_vpn_client", None):
                    self._vpn_client.stop()
                config_path = self.settings["vpn_config_path"].strip()
                kill_switch = bool(self.settings.get("vpn_kill_switch", False))
                self._vpn_client = VPNClient(
                    config_path=config_path,
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
        QMessageBox.information(self, "Settings", "Settings saved.")

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

        if self.settings.get("enable_vpn", False) and self.settings.get("vpn_config_path", "").strip():
            try:
                from vpn_client import VPNClient
                config_path = self.settings["vpn_config_path"].strip()
                kill_switch = bool(self.settings.get("vpn_kill_switch", False))
                self._vpn_client = VPNClient(
                    config_path=config_path,
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
                    from vpn_client import is_vpn_connected
                    self.btn_vpn_toggle.setText("VPN: Disconnect" if is_vpn_connected() else "VPN: Connect")
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
        ok, msg = self._vpn_client.connect()
        if hasattr(self, "_notif_mgr"):
            self._notif_mgr.notify("Cyber Defense – VPN", msg or "Connecting...", "vpn", "info" if ok else "warning")
        self._refresh_vpn_status()

    def _vpn_disconnect(self):
        if not getattr(self, "_vpn_client", None):
            if hasattr(self, "_notif_mgr"):
                self._notif_mgr.notify("Cyber Defense", "VPN not configured.", "vpn", "info")
            return
        ok, msg = self._vpn_client.disconnect()
        if hasattr(self, "_notif_mgr"):
            self._notif_mgr.notify("Cyber Defense – VPN", msg or "Disconnected.", "vpn", "info" if ok else "warning")
        self._refresh_vpn_status()

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
        # Optional: offer quarantine (quarantine module)
        if result.details.get("filepath") or path:
            try:
                from quarantine import quarantine_file
                q = quarantine_file(path, threat_type=result.threat_type, threat_message=result.message, copy_instead_of_move=True)
                if "error" not in q:
                    logger.info("Quarantined: %s", q.get("quarantine_path"))
            except Exception:
                pass

    def _on_behavioral_threat(self, result: ThreatResult):
        """Called when behavioral monitor detects a suspicious process."""
        if self._paused:
            return
        detail = result.details.get("name") or result.details.get("reason") or "suspicious process"
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
            self.status_label.setText("PAUSED")
            self.status_label.setStyleSheet("""
                font-size: 13px; 
                color: #fbbf24; 
                font-weight: 700;
                background: transparent;
                letter-spacing: 1px;
            """)
            # Update status badge parent background
            self.status_label.parent().setStyleSheet("""
                background-color: rgba(251, 191, 36, 0.15);
                border: 2px solid #fbbf24;
                border-radius: 12px;
                padding: 12px 20px;
            """)
            self.btn_pause.setText("▶ Resume")
        else:
            self._service.start()
            self.status_label.setText("ACTIVE")
            self.status_label.setStyleSheet("""
                font-size: 13px; 
                color: #4ade80; 
                font-weight: 700;
                background: transparent;
                letter-spacing: 1px;
            """)
            # Update status badge parent background
            self.status_label.parent().setStyleSheet("""
                background-color: rgba(74, 222, 128, 0.15);
                border: 2px solid #4ade80;
                border-radius: 12px;
                padding: 12px 20px;
            """)
            self.btn_pause.setText("⏸ Pause")
        if hasattr(self, "lbl_protection"):
            self.lbl_protection.setText("PAUSED" if self._paused else "ON")
        self._update_tray_icon()

    def _on_threat_detected(self, result: ThreatResult, url: str):
        if self._paused:
            return
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
        for e in reversed(self.threat_log[-200:]):
            row = t.rowCount()
            t.insertRow(row)
            t.setItem(row, 0, QTableWidgetItem(e.get("time", "")[:19]))
            t.setItem(row, 1, QTableWidgetItem(e.get("type", "")))
            t.setItem(row, 2, QTableWidgetItem(e.get("severity", "")))
            t.setItem(row, 3, QTableWidgetItem(e.get("url", "")[:80]))
            t.setItem(row, 4, QTableWidgetItem(e.get("message", "")[:60]))

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

    def _refresh_vpn_status(self):
        try:
            from vpn_client import is_vpn_connected
            connected = is_vpn_connected()
            self.lbl_vpn_status.setText("Connected" if connected else "Disconnected")
            self.lbl_vpn_status.setStyleSheet("color: #22c55e;" if connected else "color: #94a3b8;")
            cfg = self.settings.get("vpn_config_path", "") or "(not set)"
            self.lbl_vpn_config.setText(cfg[:80] + "..." if len(cfg) > 80 else cfg)
            kill = "Kill-switch: On" if self.settings.get("vpn_kill_switch") else "Kill-switch: Off"
            self.lbl_vpn_killswitch.setText(kill)
        except Exception:
            self.lbl_vpn_status.setText("Unknown")

    def _refresh_realtime_tab(self):
        try:
            if self.settings.get("enable_realtime_monitor") and getattr(self, "_realtime_monitor", None):
                paths = [str(p) for p in self._realtime_monitor.watch_paths]
                self.realtime_paths_text.setPlainText("\n".join(paths))
            else:
                self.realtime_paths_text.setPlainText("Real-time monitoring is off. Enable in Settings.")
            file_threats = [e for e in self.threat_log if e.get("type") in ("malware", "suspicious_file", "eicar_test", "ransomware_honeypot")]
            self.realtime_events_table.setRowCount(0)
            for e in list(reversed(file_threats))[:20]:
                row = self.realtime_events_table.rowCount()
                self.realtime_events_table.insertRow(row)
                self.realtime_events_table.setItem(row, 0, QTableWidgetItem(e.get("time", "")[:19]))
                self.realtime_events_table.setItem(row, 1, QTableWidgetItem((e.get("url", "") or "")[:60]))
                self.realtime_events_table.setItem(row, 2, QTableWidgetItem(e.get("type", "")))
                self.realtime_events_table.setItem(row, 3, QTableWidgetItem((e.get("message", "") or "")[:50]))
        except Exception:
            pass

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_threat_table()
        self._update_dashboard()
        self._refresh_vpn_status()
        self._refresh_realtime_tab()


def main():
    logger.info("Starting Cyber Defense v%s", APP_VERSION)
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Python: {sys.version}")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Cyber Defense")
    
    # Apply modern dark theme to entire application  
    try:
        app.setStyle("Fusion")
    except Exception as e:
        logger.warning(f"Could not set Fusion style: {e}")
        # Continue anyway with default style
    app.setStyleSheet("""
        * { font-family: 'Segoe UI Variable', 'Segoe UI', Arial, sans-serif; }

        /* Fluent-ish dark base */
        QMainWindow, QWidget { background-color: #0b0f14; color: #e5e7eb; }
        QLabel { color: #e5e7eb; background-color: transparent; }

        /* Buttons */
        QPushButton {
            background-color: #111827;
            color: #f9fafb;
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 10px;
            padding: 10px 16px;
            font-weight: 600;
            font-size: 10.5pt;
        }
        QPushButton:hover { border-color: rgba(99, 102, 241, 0.65); background-color: #0f172a; }
        QPushButton:pressed { background-color: #0b1220; }
        QPushButton:disabled { color: rgba(229, 231, 235, 0.35); }

        /* Inputs */
        QLineEdit, QPlainTextEdit, QTextEdit {
            background-color: #0f172a;
            color: #e5e7eb;
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 10px;
            padding: 10px;
            selection-background-color: rgba(99, 102, 241, 0.35);
        }
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus { border-color: #6366f1; }

        /* Combo */
        QComboBox {
            background-color: #0f172a;
            color: #e5e7eb;
            border: 1px solid rgba(148, 163, 184, 0.20);
            border-radius: 10px;
            padding: 8px;
            min-height: 28px;
        }
        QComboBox:hover { border-color: rgba(99, 102, 241, 0.65); }
        QComboBox::drop-down {
            border: none;
            background-color: rgba(148, 163, 184, 0.10);
            width: 28px;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #e2e8f0;
            margin-right: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #0f172a;
            color: #e5e7eb;
            border: 1px solid rgba(148, 163, 184, 0.18);
            selection-background-color: rgba(99, 102, 241, 0.35);
        }
        QCheckBox { color: #e5e7eb; spacing: 10px; background-color: transparent; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 5px;
            background-color: #0f172a;
        }
        QCheckBox::indicator:hover { border-color: #6366f1; }
        QCheckBox::indicator:checked {
            background-color: #6366f1;
            border-color: #6366f1;
            image: url(none);
        }
        QTabWidget::pane {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 12px;
            background-color: #0f172a;
            top: -1px;
        }
        QTabBar::tab {
            background-color: #0b0f14;
            color: rgba(229, 231, 235, 0.65);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-bottom: none;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            padding: 10px 18px;
            margin-right: 2px;
            font-weight: 600;
            min-width: 90px;
        }
        QTabBar::tab:selected {
            background-color: #0f172a;
            color: #a5b4fc;
            border-bottom: 1px solid #0f172a;
        }
        QTabBar::tab:hover:!selected { background-color: #0f172a; color: #e5e7eb; }
        QTableWidget {
            background-color: #0f172a;
            color: #e5e7eb;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 12px;
            gridline-color: rgba(148, 163, 184, 0.12);
            alternate-background-color: #0b0f14;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #2d3250;
        }
        QTableWidget::item:selected {
            background-color: #424769;
            color: #ffffff;
        }
        QTableWidget::item:hover { background-color: #334155; }
        QHeaderView::section {
            background-color: #0b0f14;
            color: rgba(229, 231, 235, 0.65);
            border: none;
            padding: 10px 12px;
            font-weight: 600;
            border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        }
        QHeaderView::section:hover { background-color: rgba(148, 163, 184, 0.08); }
        QGroupBox {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 12px;
            margin-top: 14px;
            padding: 16px 14px 14px 14px;
            font-weight: 600;
            color: #818cf8;
            background-color: transparent;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 8px;
            background-color: #0b0f14;
        }
        QProgressBar {
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 10px;
            text-align: center;
            background: #0f172a;
            color: rgba(229, 231, 235, 0.75);
            height: 18px;
        }
        QProgressBar::chunk {
            border-radius: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6366f1, stop:1 #a5b4fc);
        }
        QScrollBar:vertical {
            background-color: #1e293b;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background-color: #475569;
            border-radius: 5px;
            min-height: 28px;
        }
        QScrollBar::handle:vertical:hover { background-color: #64748b; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        QScrollBar:horizontal {
            background-color: #1e293b;
            height: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:horizontal {
            background-color: #475569;
            border-radius: 5px;
            min-width: 28px;
        }
        QScrollBar::handle:horizontal:hover { background-color: #64748b; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QMessageBox { background-color: #0b0f14; }
        QMessageBox QLabel { color: #e5e7eb; }
        QMessageBox QPushButton { min-width: 80px; }
    """)
    
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
