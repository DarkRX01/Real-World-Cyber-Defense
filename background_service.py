#!/usr/bin/env python3
"""
Background Service Handler
Manages running the app in background with system tray and auto-start capabilities
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class BackgroundService:
    """Handles background service functionality"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.cyber-defense'
        self.config_file = self.config_dir / 'service.json'
        self.config_dir.mkdir(exist_ok=True)
    
    def setup_autostart_windows(self):
        """Setup auto-start for Windows"""
        try:
            import winreg
            
            startup_path = Path.home() / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            app_path = Path(sys.executable).parent / 'cyber-defense.exe'
            
            # Create shortcut (simplified)
            bat_content = f'@echo off\nstart "" "{app_path}"\n'
            startup_bat = startup_path / 'cyber-defense-startup.bat'
            
            startup_path.mkdir(parents=True, exist_ok=True)
            with open(startup_bat, 'w') as f:
                f.write(bat_content)
            
            print(f"✅ Auto-start configured for Windows")
            return True
        except Exception as e:
            print(f"❌ Failed to setup auto-start: {e}")
            return False
    
    def setup_autostart_linux(self):
        """Setup auto-start for Linux using systemd"""
        try:
            systemd_dir = Path.home() / '.config' / 'systemd' / 'user'
            systemd_dir.mkdir(parents=True, exist_ok=True)
            
            service_file = systemd_dir / 'cyber-defense.service'
            app_path = Path(sys.executable).parent / 'cyber-defense'
            
            service_content = f"""[Unit]
Description=Real-World Cyber Defense
After=graphical-session.target
Wants=graphical-session-target.service

[Service]
Type=simple
ExecStart={app_path}
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical-session.target
"""
            
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            os.chmod(service_file, 0o644)
            
            # Enable the service
            subprocess.run(['systemctl', '--user', 'enable', 'cyber-defense.service'],
                         capture_output=True)
            
            print(f"✅ Auto-start configured for Linux (systemd)")
            return True
        except Exception as e:
            print(f"❌ Failed to setup auto-start: {e}")
            return False
    
    def start_service(self):
        """Start the background service"""
        if os.name == 'nt':
            return self.start_service_windows()
        else:
            return self.start_service_linux()
    
    def start_service_windows(self):
        """Start service on Windows"""
        try:
            subprocess.Popen(['pythonw.exe', '-m', 'cyber_defense.app_main'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           start_new_session=True)
            return True
        except Exception as e:
            print(f"Error starting service: {e}")
            return False
    
    def start_service_linux(self):
        """Start service on Linux"""
        try:
            subprocess.Popen(['python3', '-m', 'cyber_defense.app_main'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           preexec_fn=os.setpgrp)
            return True
        except Exception as e:
            print(f"Error starting service: {e}")
            return False
    
    def is_running(self):
        """Check if service is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'cyber-defense'],
                                  capture_output=True, text=True)
            return bool(result.stdout.strip())
        except:
            return False
    
    def stop_service(self):
        """Stop the background service"""
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/IM', 'cyber-defense.exe'],
                         capture_output=True)
        else:
            subprocess.run(['pkill', '-f', 'cyber-defense'],
                         capture_output=True)
    
    def save_config(self, config):
        """Save service configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        """Load service configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_service_info(self):
        """Get service information"""
        return {
            'running': self.is_running(),
            'platform': 'Windows' if os.name == 'nt' else 'Linux',
            'config': self.load_config()
        }


class SystemTrayIntegration:
    """Handle system tray integration"""
    
    @staticmethod
    def create_tray_icon():
        """Create system tray icon"""
        try:
            # This is handled by PyQt5's QSystemTrayIcon
            # Icon is set in the main app
            pass
        except Exception as e:
            print(f"Tray icon error: {e}")
    
    @staticmethod
    def show_notification(title, message, duration=3000):
        """Show system notification"""
        if os.name == 'nt':
            # Windows notification
            try:
                from win10toast import ToastNotifier
                notifier = ToastNotifier()
                notifier.show_toast(title, message, duration=duration//1000)
            except:
                print(f"{title}: {message}")
        else:
            # Linux notification
            try:
                subprocess.run(['notify-send', title, message],
                             capture_output=True, timeout=2)
            except:
                print(f"{title}: {message}")


class LogManager:
    """Manage application logs"""
    
    def __init__(self):
        self.log_dir = Path.home() / '.cyber-defense' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log = self.log_dir / f"cyber-defense-{datetime.now().strftime('%Y%m%d')}.log"
    
    def log(self, level, message):
        """Write log message"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.current_log, 'a') as f:
            f.write(log_entry)
        
        if level == 'ERROR':
            print(f"❌ {message}")
        elif level == 'WARNING':
            print(f"⚠️ {message}")
        elif level == 'INFO':
            print(f"ℹ️ {message}")
    
    def info(self, message):
        self.log('INFO', message)
    
    def warning(self, message):
        self.log('WARNING', message)
    
    def error(self, message):
        self.log('ERROR', message)
    
    def get_logs(self, days=7):
        """Get recent logs"""
        logs = []
        for log_file in sorted(self.log_dir.glob('*.log')):
            with open(log_file, 'r') as f:
                logs.extend(f.readlines())
        
        return logs[-100:]  # Return last 100 entries


class CrashHandler:
    """Handle application crashes and recovery"""
    
    def __init__(self, logger):
        self.logger = logger
        self.recovery_file = Path.home() / '.cyber-defense' / 'recovery.json'
    
    def handle_crash(self, exception):
        """Handle unexpected crash"""
        self.logger.error(f"Application crash: {str(exception)}")
        self.save_recovery_state()
    
    def save_recovery_state(self):
        """Save state for recovery"""
        recovery_data = {
            'crash_time': datetime.now().isoformat(),
            'recovery': True
        }
        
        with open(self.recovery_file, 'w') as f:
            json.dump(recovery_data, f)
    
    def should_recover(self):
        """Check if recovery is needed"""
        if self.recovery_file.exists():
            with open(self.recovery_file, 'r') as f:
                data = json.load(f)
                return data.get('recovery', False)
        
        return False
    
    def clear_recovery(self):
        """Clear recovery flag"""
        if self.recovery_file.exists():
            self.recovery_file.unlink()
