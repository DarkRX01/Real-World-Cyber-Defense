#!/usr/bin/env python3
"""
Real-World Cyber Defense - Desktop Application
Cross-platform threat detection tool for Windows and Linux
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QStatusBar, QSystemTrayIcon, QMenu, QTabWidget, QFormLayout,
    QSpinBox, QCheckBox, QComboBox, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSettings
from PyQt5.QtGui import QIcon, QColor, QFont
from threat_engine import ThreatDetectionEngine
from background_service import BackgroundService

class ThreatMonitorThread(QThread):
    """Background thread for continuous monitoring"""
    threat_detected = pyqtSignal(dict)
    status_changed = pyqtSignal(str)
    
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.running = True
    
    def run(self):
        """Continuous monitoring loop"""
        self.status_changed.emit("🔒 Monitoring Active")
        while self.running:
            try:
                # Monitor clipboard for URLs
                threat = self.engine.check_clipboard()
                if threat:
                    self.threat_detected.emit(threat)
                
                # Monitor system
                threats = self.engine.monitor_system()
                for threat in threats:
                    self.threat_detected.emit(threat)
                
                self.msleep(2000)  # Check every 2 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
    
    def stop(self):
        self.running = False


class SettingsDialog(QDialog):
    """Settings/Customization window"""
    
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("⚙️ Cyber Defense Settings")
        self.setGeometry(100, 100, 400, 500)
        layout = QFormLayout()
        
        # Threat Level
        self.sensitivity = QComboBox()
        self.sensitivity.addItems(["🟢 Low", "🟡 Medium", "🔴 High", "⚫ Extreme"])
        self.sensitivity.setCurrentIndex(self.settings.get('sensitivity', 1))
        layout.addRow("Threat Sensitivity:", self.sensitivity)
        
        # Features
        self.phishing_check = QCheckBox("Enable Phishing Detection")
        self.phishing_check.setChecked(self.settings.get('phishing_enabled', True))
        layout.addRow(self.phishing_check)
        
        self.tracker_block = QCheckBox("Block Trackers")
        self.tracker_block.setChecked(self.settings.get('tracker_blocking', True))
        layout.addRow(self.tracker_block)
        
        self.download_scan = QCheckBox("Scan Downloads")
        self.download_scan.setChecked(self.settings.get('download_scanning', True))
        layout.addRow(self.download_scan)
        
        self.url_scan = QCheckBox("Scan URLs")
        self.url_scan.setChecked(self.settings.get('url_scanning', True))
        layout.addRow(self.url_scan)
        
        # Background Service
        self.background_service = QCheckBox("Run in Background (System Tray)")
        self.background_service.setChecked(self.settings.get('background_service', True))
        layout.addRow(self.background_service)
        
        self.auto_start = QCheckBox("Auto-Start on Boot")
        self.auto_start.setChecked(self.settings.get('auto_start', False))
        layout.addRow(self.auto_start)
        
        # Notifications
        self.notifications = QCheckBox("Enable Notifications")
        self.notifications.setChecked(self.settings.get('notifications', True))
        layout.addRow(self.notifications)
        
        # API Keys (optional)
        self.api_key_label = QLabel("Optional: Add API Keys for Enhanced Detection")
        layout.addRow(self.api_key_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def save_settings(self):
        self.settings['sensitivity'] = self.sensitivity.currentIndex()
        self.settings['phishing_enabled'] = self.phishing_check.isChecked()
        self.settings['tracker_blocking'] = self.tracker_block.isChecked()
        self.settings['download_scanning'] = self.download_scan.isChecked()
        self.settings['url_scanning'] = self.url_scan.isChecked()
        self.settings['background_service'] = self.background_service.isChecked()
        self.settings['auto_start'] = self.auto_start.isChecked()
        self.settings['notifications'] = self.notifications.isChecked()
        
        # Save to config file
        config_dir = Path.home() / '.cyber-defense'
        config_dir.mkdir(exist_ok=True)
        with open(config_dir / 'settings.json', 'w') as f:
            json.dump(self.settings, f, indent=2)
        
        QMessageBox.information(self, "✅ Success", "Settings saved successfully!")
        self.accept()


class CyberDefenseApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.engine = ThreatDetectionEngine()
        self.load_settings()
        self.monitor_thread = None
        self.init_ui()
        self.setup_tray()
        self.start_monitoring()
    
    def load_settings(self):
        """Load user settings from config file"""
        config_dir = Path.home() / '.cyber-defense'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'settings.json'
        self.default_settings = {
            'sensitivity': 1,  # Medium
            'phishing_enabled': True,
            'tracker_blocking': True,
            'download_scanning': True,
            'url_scanning': True,
            'background_service': True,
            'auto_start': False,
            'notifications': True
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = self.default_settings.copy()
            with open(config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("🛡️ Real-World Cyber Defense")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(self.get_stylesheet())
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("🛡️ CYBER DEFENSE DASHBOARD")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        
        # Dashboard Tab
        dashboard = self.create_dashboard()
        tabs.addTab(dashboard, "📊 Dashboard")
        
        # Threat Log Tab
        threat_log = self.create_threat_log()
        tabs.addTab(threat_log, "🔴 Threats")
        
        # Tools Tab
        tools = self.create_tools()
        tabs.addTab(tools, "🔧 Tools")
        
        layout.addWidget(tabs)
        
        # Settings Button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)
        
        main_widget.setLayout(layout)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("✅ Cyber Defense Ready")
    
    def create_dashboard(self):
        """Create dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Stats
        stats_layout = QHBoxLayout()
        
        self.threats_detected_label = QLabel("🔴 Threats Detected: 0")
        self.threats_detected_label.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.threats_detected_label)
        
        self.trackers_blocked_label = QLabel("🚫 Trackers Blocked: 0")
        self.trackers_blocked_label.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.trackers_blocked_label)
        
        self.phishing_blocked_label = QLabel("🎣 Phishing Blocked: 0")
        self.phishing_blocked_label.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.phishing_blocked_label)
        
        layout.addLayout(stats_layout)
        
        # Status Panel
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("🔒 Monitoring Active")
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.status_label.setStyleSheet("color: green;")
        status_layout.addWidget(self.status_label)
        
        self.toggle_monitor = QPushButton("⏸️ Pause Monitoring")
        self.toggle_monitor.clicked.connect(self.toggle_monitoring)
        status_layout.addWidget(self.toggle_monitor)
        
        layout.addLayout(status_layout)
        
        # Recent Activity
        recent_label = QLabel("📋 Recent Activity")
        recent_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(recent_label)
        
        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Type", "Status", "Details"])
        self.activity_table.setMaximumHeight(250)
        layout.addWidget(self.activity_table)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_threat_log(self):
        """Create threat log tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("🔴 Detected Threats")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)
        
        self.threat_table = QTableWidget()
        self.threat_table.setColumnCount(5)
        self.threat_table.setHorizontalHeaderLabels(["Time", "Threat Type", "URL/File", "Severity", "Action"])
        layout.addWidget(self.threat_table)
        
        clear_btn = QPushButton("🗑️ Clear Log")
        clear_btn.clicked.connect(self.clear_threat_log)
        layout.addWidget(clear_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_tools(self):
        """Create tools tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel("🔧 Security Tools")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)
        
        # URL Scanner
        url_label = QLabel("🔗 URL Scanner")
        layout.addWidget(url_label)
        scan_url_btn = QPushButton("Scan URL from Clipboard")
        scan_url_btn.clicked.connect(self.scan_clipboard_url)
        layout.addWidget(scan_url_btn)
        
        # System Scan
        system_label = QLabel("💻 System Scanner")
        layout.addWidget(system_label)
        scan_system_btn = QPushButton("Full System Scan")
        scan_system_btn.clicked.connect(self.full_system_scan)
        layout.addWidget(scan_system_btn)
        
        # Vulnerability Check
        vuln_label = QLabel("⚠️ Vulnerability Check")
        layout.addWidget(vuln_label)
        vuln_btn = QPushButton("Check for Vulnerabilities")
        vuln_btn.clicked.connect(self.check_vulnerabilities)
        layout.addWidget(vuln_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def setup_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(16))  # Use default icon
        
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.showNormal)
        
        pause_action = tray_menu.addAction("Pause")
        pause_action.triggered.connect(self.toggle_monitoring)
        
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings)
        
        tray_menu.addSeparator()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_app)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.monitor_thread is None or not self.monitor_thread.isRunning():
            self.monitor_thread = ThreatMonitorThread(self.engine)
            self.monitor_thread.threat_detected.connect(self.on_threat_detected)
            self.monitor_thread.status_changed.connect(self.on_status_changed)
            self.monitor_thread.start()
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if self.monitor_thread and self.monitor_thread.isRunning():
            self.monitor_thread.stop()
            self.status_label.setText("⏸️ Monitoring Paused")
            self.status_label.setStyleSheet("color: orange;")
            self.toggle_monitor.setText("▶️ Resume Monitoring")
        else:
            self.start_monitoring()
            self.status_label.setText("🔒 Monitoring Active")
            self.status_label.setStyleSheet("color: green;")
            self.toggle_monitor.setText("⏸️ Pause Monitoring")
    
    def on_threat_detected(self, threat):
        """Handle threat detection"""
        # Update tables
        self.add_to_activity_table(threat)
        self.add_to_threat_log(threat)
        
        # Update stats
        threat_type = threat.get('type', 'unknown').lower()
        if 'phishing' in threat_type:
            count = int(self.phishing_blocked_label.text().split(': ')[1])
            self.phishing_blocked_label.setText(f"🎣 Phishing Blocked: {count + 1}")
        elif 'tracker' in threat_type:
            count = int(self.trackers_blocked_label.text().split(': ')[1])
            self.trackers_blocked_label.setText(f"🚫 Trackers Blocked: {count + 1}")
        else:
            count = int(self.threats_detected_label.text().split(': ')[1])
            self.threats_detected_label.setText(f"🔴 Threats Detected: {count + 1}")
        
        # Notification
        if self.settings.get('notifications', True):
            self.tray_icon.showMessage(
                "🚨 Threat Detected",
                f"{threat.get('type', 'Unknown')}: {threat.get('details', 'Check dashboard')}",
                2000
            )
    
    def add_to_activity_table(self, threat):
        """Add threat to activity table"""
        row = self.activity_table.rowCount()
        self.activity_table.insertRow(row)
        
        self.activity_table.setItem(row, 0, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
        self.activity_table.setItem(row, 1, QTableWidgetItem(threat.get('type', 'Unknown')))
        self.activity_table.setItem(row, 2, QTableWidgetItem("🛡️ Blocked"))
        self.activity_table.setItem(row, 3, QTableWidgetItem(threat.get('details', '')[:50]))
    
    def add_to_threat_log(self, threat):
        """Add threat to detailed log"""
        row = self.threat_table.rowCount()
        self.threat_table.insertRow(row)
        
        severity_map = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        severity = threat.get('severity', 'low')
        severity_icon = severity_map.get(severity, '⚪')
        
        self.threat_table.setItem(row, 0, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
        self.threat_table.setItem(row, 1, QTableWidgetItem(threat.get('type', 'Unknown')))
        self.threat_table.setItem(row, 2, QTableWidgetItem(threat.get('url', threat.get('file', 'N/A'))[:40]))
        self.threat_table.setItem(row, 3, QTableWidgetItem(f"{severity_icon} {severity.upper()}"))
        self.threat_table.setItem(row, 4, QTableWidgetItem("✅ Blocked"))
    
    def on_status_changed(self, status):
        """Update status"""
        self.statusBar.showMessage(status)
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.settings)
        dialog.exec_()
    
    def scan_clipboard_url(self):
        """Scan URL from clipboard"""
        threat = self.engine.check_clipboard()
        if threat:
            QMessageBox.warning(self, "⚠️ Threat Detected", f"Potential threat detected:\n\n{threat}")
        else:
            QMessageBox.information(self, "✅ Safe", "URL in clipboard is safe!")
    
    def full_system_scan(self):
        """Perform full system scan"""
        threats = self.engine.monitor_system()
        if threats:
            msg = f"Found {len(threats)} potential threats:\n\n"
            for t in threats[:5]:
                msg += f"- {t.get('type')}: {t.get('details')}\n"
            QMessageBox.warning(self, "🔴 Scan Complete", msg)
        else:
            QMessageBox.information(self, "✅ Scan Complete", "No threats detected!")
    
    def check_vulnerabilities(self):
        """Check for system vulnerabilities"""
        vulns = self.engine.check_vulnerabilities()
        if vulns:
            msg = "Found potential vulnerabilities:\n\n" + "\n".join(vulns[:5])
            QMessageBox.warning(self, "⚠️ Vulnerabilities Found", msg)
        else:
            QMessageBox.information(self, "✅ Secure", "No known vulnerabilities found!")
    
    def clear_threat_log(self):
        """Clear threat log"""
        self.threat_table.setRowCount(0)
        QMessageBox.information(self, "✅ Cleared", "Threat log cleared!")
    
    def exit_app(self):
        """Exit application"""
        if self.monitor_thread:
            self.monitor_thread.stop()
        QApplication.quit()
    
    def changeEvent(self, event):
        """Handle window state change (minimize to tray)"""
        if event.type() == 2:  # QEvent.WindowStateChange
            if self.isMinimized():
                self.hide()
                event.ignore()
    
    @staticmethod
    def get_stylesheet():
        """Return application stylesheet"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QTableWidget {
            background-color: white;
            alternate-background-color: #f9f9f9;
            gridline-color: #ddd;
        }
        QHeaderView::section {
            background-color: #007bff;
            color: white;
            padding: 5px;
            border: none;
        }
        QTabBar::tab {
            background-color: #e9ecef;
            padding: 8px 20px;
            border: none;
        }
        QTabBar::tab:selected {
            background-color: #007bff;
            color: white;
        }
        """


def main():
    app = QApplication(sys.argv)
    window = CyberDefenseApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
