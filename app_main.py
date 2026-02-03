#!/usr/bin/env python3
"""
Real-World Cyber Defense - Desktop Application
Main entry point and PyQt5 GUI.
"""

import json
import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
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
)

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
        "enable_realtime_monitor": False,
        "enable_auto_updates": True,
        "enable_behavioral_monitor": False,
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


class CyberDefenseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing Cyber Defense application")
        self.setWindowTitle("Cyber Defense - Real-World Security")
        self.setMinimumSize(900, 650)
        self.resize(1000, 700)
        
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

        self._service = BackgroundService(
            on_threat=self._on_threat_detected,
            sensitivity=sensitivity_from_string(self.settings.get("sensitivity", "MEDIUM")),
            enable_clipboard=bool(self.settings.get("enable_clipboard", True)),
            enable_tracker_check=bool(self.settings.get("enable_tracker_check", True)),
        )

        self._build_ui()
        self._setup_tray()
        self._apply_settings()
        self._refresh_stats()
        self._start_monitoring()
        self._start_optional_services()

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
                                       stop:0 #6366f1, stop:0.5 #8b5cf6, stop:1 #d946ef);
            border-radius: 16px;
            padding: 24px;
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
            font-size: 32px; 
            font-weight: bold; 
            color: #ffffff;
            background: transparent;
        """)
        title_layout.addWidget(header)
        
        subheader = QLabel("Real-time threat detection & security monitoring")
        subheader.setStyleSheet("""
            font-size: 13px; 
            color: rgba(255, 255, 255, 0.85);
            background: transparent;
        """)
        title_layout.addWidget(subheader)
        
        top_layout.addWidget(title_container)
        top_layout.addStretch()
        
        # Right side - Status badge
        status_badge = QWidget()
        status_badge.setStyleSheet("""
            background-color: rgba(74, 222, 128, 0.15);
            border: 2px solid #4ade80;
            border-radius: 12px;
            padding: 12px 20px;
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
        
        layout.addWidget(stats_container)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._dashboard_tab(), "📊 Dashboard")
        self.tabs.addTab(self._threats_tab(), "🔴 Threats")
        self.tabs.addTab(self._tools_tab(), "🔧 Tools")
        self.tabs.addTab(self._settings_tab(), "⚙️ Settings")
        layout.addWidget(self.tabs)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_pause = QPushButton("⏸️ Pause")
        self.btn_pause.clicked.connect(self._toggle_pause)
        self.btn_settings = QPushButton("⚙️ Settings")
        self.btn_settings.clicked.connect(lambda: self.tabs.setCurrentIndex(3))
        self.btn_close = QPushButton("❌ Close")
        self.btn_close.clicked.connect(self.close)
        for b in (self.btn_pause, self.btn_settings, self.btn_close):
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _dashboard_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Overview"))
        self.dashboard_text = QPlainTextEdit()
        self.dashboard_text.setReadOnly(True)
        self.dashboard_text.setPlaceholderText(
            "Copy a URL and paste it somewhere — we'll scan it automatically.\n\n"
            "Or go to Tools → Scan URL to check a link manually.\n\n"
            "Threats and activity will appear here and in the Threats tab."
        )
        self.dashboard_text.setToolTip("Recent activity and threat summary. Copy URLs to trigger automatic scanning.")
        layout.addWidget(self.dashboard_text)
        return w

    def _threats_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        self.threat_table = QTableWidget(0, 5)
        self.threat_table.setHorizontalHeaderLabels(["Time", "Type", "Severity", "URL / Details", "Message"])
        self.threat_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.threat_table)
        clear_btn = QPushButton("Clear log")
        clear_btn.clicked.connect(self._clear_threat_log)
        layout.addWidget(clear_btn)
        return w

    def _tools_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        # URL Scanner
        gb = QGroupBox("🔗 URL Scanner")
        gb.setToolTip("Paste any link here to check if it's safe (phishing, tracker, or malware).")
        fl = QFormLayout(gb)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste a URL here (e.g. https://example.com)")
        self.url_input.setToolTip("Paste the full URL you want to check.")
        fl.addRow("URL:", self.url_input)
        scan_btn = QPushButton("Scan URL")
        scan_btn.setToolTip("Check the URL for threats.")
        scan_btn.clicked.connect(self._scan_url_clicked)
        fl.addRow("", scan_btn)
        self.scan_result = QPlainTextEdit()
        self.scan_result.setReadOnly(True)
        self.scan_result.setPlaceholderText("Result will appear here after you click Scan URL.")
        fl.addRow(self.scan_result)
        layout.addWidget(gb)

        # System Scan
        gb2 = QGroupBox("💻 System Security Check")
        gb2.setToolTip("Quick check: firewall and Windows Defender status.")
        vl = QVBoxLayout(gb2)
        sys_btn = QPushButton("Run system security check")
        sys_btn.setToolTip("Check if Windows Firewall and Defender are enabled.")
        sys_btn.clicked.connect(self._run_system_scan)
        vl.addWidget(sys_btn)
        self.sys_result = QPlainTextEdit()
        self.sys_result.setReadOnly(True)
        self.sys_result.setPlaceholderText("Result will appear here after you run the check.")
        vl.addWidget(self.sys_result)
        layout.addWidget(gb2)

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

        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems(["Low", "Medium", "High", "Extreme"])
        self.sensitivity_combo.setToolTip("Medium is recommended. High/Extreme may flag more safe sites.")

        for c in (
            self.cb_clipboard, self.cb_tracker, self.cb_phishing, self.cb_download,
            self.cb_url_scan, self.cb_notifications, self.cb_start_minimized,
            self.cb_realtime_monitor, self.cb_auto_updates, self.cb_behavioral_monitor,
        ):
            layout.addWidget(c)
        layout.addWidget(QLabel("Sensitivity:"))
        layout.addWidget(self.sensitivity_combo)

        save_btn = QPushButton("Save settings")
        save_btn.setToolTip("Apply and save your preferences.")
        save_btn.clicked.connect(self._save_settings_clicked)
        layout.addWidget(save_btn)
        layout.addStretch()
        return w

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("Cyber Defense — Double-click to open, right-click for menu")
        try:
            icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)
            self.tray.setIcon(icon)
        except Exception:
            pass
        menu = QMenu()
        show_a = menu.addAction("Show")
        show_a.triggered.connect(self.show_normal)
        menu.addSeparator()
        pause_a = menu.addAction("Pause")
        pause_a.triggered.connect(self._toggle_pause)
        settings_a = menu.addAction("Settings")
        settings_a.triggered.connect(self._open_settings)
        menu.addSeparator()
        exit_a = menu.addAction("Exit")
        exit_a.triggered.connect(self._quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

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
        self.settings["sensitivity"] = self.sensitivity_combo.currentText().upper()
        save_settings(self.settings)
        self._service.update_settings(
            sensitivity=sensitivity_from_string(self.settings["sensitivity"]),
            enable_clipboard=self.settings["enable_clipboard"],
            enable_tracker_check=self.settings["enable_tracker_check"],
        )
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
                import os
                from realtime_monitor import RealtimeFileMonitor
                watch_paths = [
                    os.path.expanduser("~/Downloads"),
                    os.path.expanduser("~/Desktop"),
                ]
                if os.environ.get("USERPROFILE"):
                    watch_paths.append(os.path.join(os.environ["USERPROFILE"], "Downloads"))
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

    def _on_file_threat(self, result: ThreatResult, path: str):
        """Called when real-time monitor detects a file threat; notify and optionally quarantine."""
        if self._paused:
            return
        entry = {
            "time": datetime.now().isoformat(),
            "type": result.threat_type,
            "severity": result.severity,
            "url": path,
            "message": result.message,
            "confidence": result.confidence,
        }
        self.threat_log.append(entry)
        self._stats["threats"] += 1
        save_threat_log(self.threat_log)
        self._refresh_stats()
        self._refresh_threat_table()
        self._update_dashboard()
        if self.settings.get("enable_notifications", True):
            self.tray.showMessage(
                "Cyber Defense",
                f"File threat: {result.message[:60]}",
                QSystemTrayIcon.Warning,
                5000,
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
        if self.settings.get("enable_notifications", True):
            self.tray.showMessage(
                "Cyber Defense",
                f"Behavior: {result.message[:60]}",
                QSystemTrayIcon.Warning,
                5000,
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
            self.btn_pause.setText("▶️ Resume")
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
            self.btn_pause.setText("⏸️ Pause")

    def _on_threat_detected(self, result: ThreatResult, url: str):
        if self._paused:
            return
        logger.info(f"Threat detected: {result.threat_type} - {url[:50]}... (confidence: {result.confidence}%)")
        entry = {
            "time": datetime.now().isoformat(),
            "type": result.threat_type,
            "severity": result.severity,
            "url": url,
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
        if self.settings.get("enable_notifications", True):
            self.tray.showMessage(
                "Cyber Defense",
                f"{result.threat_type.upper()}: {result.message[:80]}...",
                QSystemTrayIcon.Warning,
                3000,
            )

    def _refresh_stats(self):
        self.lbl_threats.setText(str(self._stats['threats']))
        self.lbl_trackers.setText(str(self._stats['trackers']))
        self.lbl_phishing.setText(str(self._stats['phishing']))

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

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh_threat_table()
        self._update_dashboard()


def main():
    logger.info("Starting Cyber Defense v2.0.0")
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
        * {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QMainWindow, QWidget {
            background-color: #1a1d2e;
            color: #e0e6f0;
        }
        QLabel {
            color: #e0e6f0;
            background-color: transparent;
        }
        QPushButton {
            background-color: #2d3250;
            color: #ffffff;
            border: 2px solid #424769;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 10pt;
        }
        QPushButton:hover {
            background-color: #424769;
            border-color: #676f9d;
        }
        QPushButton:pressed {
            background-color: #676f9d;
        }
        QLineEdit, QPlainTextEdit, QTextEdit {
            background-color: #252842;
            color: #e0e6f0;
            border: 2px solid #424769;
            border-radius: 6px;
            padding: 8px;
            selection-background-color: #424769;
        }
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {
            border-color: #7c83fd;
        }
        QComboBox {
            background-color: #252842;
            color: #e0e6f0;
            border: 2px solid #424769;
            border-radius: 6px;
            padding: 6px;
            min-height: 25px;
        }
        QComboBox:hover {
            border-color: #7c83fd;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #424769;
            width: 30px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #e0e6f0;
            margin-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #252842;
            color: #e0e6f0;
            border: 2px solid #424769;
            selection-background-color: #424769;
        }
        QCheckBox {
            color: #e0e6f0;
            spacing: 8px;
            background-color: transparent;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #424769;
            border-radius: 4px;
            background-color: #252842;
        }
        QCheckBox::indicator:hover {
            border-color: #7c83fd;
        }
        QCheckBox::indicator:checked {
            background-color: #7c83fd;
            border-color: #7c83fd;
            image: url(none);
        }
        QTabWidget::pane {
            border: 2px solid #424769;
            border-radius: 8px;
            background-color: #252842;
            top: -2px;
        }
        QTabBar::tab {
            background-color: #2d3250;
            color: #a0a8c0;
            border: 2px solid #424769;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 10px 20px;
            margin-right: 4px;
            font-weight: 600;
            min-width: 80px;
        }
        QTabBar::tab:selected {
            background-color: #252842;
            color: #7c83fd;
            border-bottom: 2px solid #252842;
        }
        QTabBar::tab:hover:!selected {
            background-color: #424769;
            color: #e0e6f0;
        }
        QTableWidget {
            background-color: #252842;
            color: #e0e6f0;
            border: 2px solid #424769;
            border-radius: 6px;
            gridline-color: #424769;
            alternate-background-color: #2d3250;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #2d3250;
        }
        QTableWidget::item:selected {
            background-color: #424769;
            color: #ffffff;
        }
        QTableWidget::item:hover {
            background-color: #2d3250;
        }
        QHeaderView::section {
            background-color: #2d3250;
            color: #a0a8c0;
            border: none;
            padding: 10px;
            font-weight: 700;
            border-bottom: 2px solid #424769;
        }
        QHeaderView::section:hover {
            background-color: #424769;
        }
        QGroupBox {
            border: 2px solid #424769;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 16px;
            font-weight: 600;
            color: #7c83fd;
            background-color: transparent;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
            background-color: #1a1d2e;
        }
        QScrollBar:vertical {
            background-color: #252842;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #424769;
            border-radius: 6px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #676f9d;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar:horizontal {
            background-color: #252842;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #424769;
            border-radius: 6px;
            min-width: 30px;
        }
        QScrollBar::handle:horizontal:hover {
            background-color: #676f9d;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QMessageBox {
            background-color: #1a1d2e;
        }
        QMessageBox QLabel {
            color: #e0e6f0;
        }
        QMessageBox QPushButton {
            min-width: 80px;
        }
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
