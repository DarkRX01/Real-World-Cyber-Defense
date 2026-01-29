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
        self.setMinimumSize(720, 520)
        self.resize(800, 600)

        self.settings = load_settings()
        self.threat_log: list = load_threat_log()
        self._paused = False
        self._stats = {"threats": 0, "trackers": 0, "phishing": 0}

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

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QLabel("🛡️ Cyber Defense Dashboard")
        header.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        layout.addWidget(header)

        # Status bar
        self.status_label = QLabel("🔒 Monitoring Active")
        self.status_label.setStyleSheet("font-size: 14px; color: #2d3748; padding: 4px 8px;")
        layout.addWidget(self.status_label)

        # Stats row
        stats = QWidget()
        stats_layout = QHBoxLayout(stats)
        self.lbl_threats = QLabel("🔴 Threats: 0")
        self.lbl_trackers = QLabel("🚫 Trackers: 0")
        self.lbl_phishing = QLabel("🎣 Phishing: 0")
        for w in (self.lbl_threats, self.lbl_trackers, self.lbl_phishing):
            w.setStyleSheet("font-size: 14px; padding: 8px;")
            stats_layout.addWidget(w)
        stats_layout.addStretch()
        layout.addWidget(stats)

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
        self.dashboard_text.setPlaceholderText("Summary and recent activity...")
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
        fl = QFormLayout(gb)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        fl.addRow("URL:", self.url_input)
        scan_btn = QPushButton("Scan URL")
        scan_btn.clicked.connect(self._scan_url_clicked)
        fl.addRow("", scan_btn)
        self.scan_result = QPlainTextEdit()
        self.scan_result.setReadOnly(True)
        fl.addRow(self.scan_result)
        layout.addWidget(gb)

        # System Scan
        gb2 = QGroupBox("💻 System Security Scan")
        vl = QVBoxLayout(gb2)
        sys_btn = QPushButton("Run system security check")
        sys_btn.clicked.connect(self._run_system_scan)
        vl.addWidget(sys_btn)
        self.sys_result = QPlainTextEdit()
        self.sys_result.setReadOnly(True)
        vl.addWidget(self.sys_result)
        layout.addWidget(gb2)

        layout.addStretch()
        return w

    def _settings_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)

        self.cb_clipboard = QCheckBox("Monitor clipboard for URLs")
        self.cb_tracker = QCheckBox("Tracker detection")
        self.cb_phishing = QCheckBox("Phishing detection")
        self.cb_download = QCheckBox("Download scanning")
        self.cb_url_scan = QCheckBox("URL scanning")
        self.cb_notifications = QCheckBox("Show notifications for threats")

        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItems(["Low", "Medium", "High", "Extreme"])

        for c in (self.cb_clipboard, self.cb_tracker, self.cb_phishing, self.cb_download, self.cb_url_scan, self.cb_notifications):
            layout.addWidget(c)
        layout.addWidget(QLabel("Sensitivity:"))
        layout.addWidget(self.sensitivity_combo)

        save_btn = QPushButton("Save settings")
        save_btn.clicked.connect(self._save_settings_clicked)
        layout.addWidget(save_btn)
        layout.addStretch()
        return w

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        self.tray.setToolTip("Cyber Defense")
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

    def _toggle_pause(self):
        self._paused = not self._paused
        if self._paused:
            self._service.stop()
            self.status_label.setText("⏸️ Monitoring Paused")
            self.btn_pause.setText("▶️ Resume")
        else:
            self._service.start()
            self.status_label.setText("🔒 Monitoring Active")
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
        self.lbl_threats.setText(f"🔴 Threats: {self._stats['threats']}")
        self.lbl_trackers.setText(f"🚫 Trackers: {self._stats['trackers']}")
        self.lbl_phishing.setText(f"🎣 Phishing: {self._stats['phishing']}")

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
    
    try:
        win = CyberDefenseApp()
        win.show()
        logger.info("Application window shown")
        return app.exec_()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    sys.exit(main())
