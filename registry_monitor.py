#!/usr/bin/env python3
"""
Windows Registry Monitoring - Detect malware persistence and configuration changes.
Monitors registry for common malware indicators and persistence mechanisms.
Windows only.
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

_log = logging.getLogger("CyberDefense.RegistryMonitor")

# ==================== MALWARE REGISTRY PATTERNS ====================

# Registry paths commonly modified by malware for persistence
PERSISTENCE_REGISTRY_PATHS = frozenset([
    r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
    r"HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce",
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce",
    r"HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon",
    r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\Winlogon",
    r"HKLM\System\CurrentControlSet\Services",
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Run",
    r"HKLM\Software\Classes\*\ShellEx\ContextMenuHandlers",
    r"HKLM\Software\Classes\.exe\shell\open\command",
])

# Registry paths used for UAC bypass
UAC_BYPASS_PATHS = frozenset([
    r"HKCU\Software\Classes\mscfile\shell\open\command",
    r"HKCU\Software\Classes\exefile\shell\open\command",
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\CommandStore",
])

# Registry paths for COM object hijacking
COM_HIJACKING_PATHS = frozenset([
    r"HKCU\Software\Classes\CLSID",
    r"HKCU\Software\Classes\Interface",
    r"HKCU\Software\Microsoft\Office",
])

# Registry paths for IE/Browser hijacking
BROWSER_HIJACKING_PATHS = frozenset([
    r"HKCU\Software\Microsoft\Internet Explorer\Main",
    r"HKCU\Software\Microsoft\Internet Explorer\SearchScopes",
    r"HKLM\Software\Microsoft\Internet Explorer\SearchScopes",
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings",
])

# Registry paths for credential harvesting
CREDENTIAL_PATHS = frozenset([
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Search",
])

# Suspicious registry values that enable malware features
SUSPICIOUS_VALUES = {
    "DisableRealtimeMonitoring": "Disables Windows Defender",
    "DisableBehaviorMonitoring": "Disables behavioral monitoring",
    "UseLogicalProcessorCount": "Disables multi-core CPU protection",
    "DisableIOAVProtection": "Disables IOAV protection",
    "DisableOnAccessProtection": "Disables on-access scanning",
    "DisableScanOnRealtimeEnable": "Disables real-time scanning",
    "Start": "Service startup mode",
    "ImagePath": "Service binary path modification",
}

# Legitimate services that shouldn't be modified
PROTECTED_SERVICES = frozenset([
    "WinDefend",  # Windows Defender
    "MpsSvc",     # Windows Firewall
    "SharedAccess",  # ICS
    "BITS",       # Background Intelligent Transfer
    "cryptsvc",   # Cryptographic Services
    "NtLmSsp",    # NTLM Security Support Provider
])

# ==================== THREAT PATTERNS ====================

@dataclass
class RegistryChange:
    """Represents a registry value change."""
    timestamp: float
    hive: str  # HKLM, HKCU, etc
    path: str
    value_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    operation: str  # 'set', 'delete', 'create'
    process_name: str
    suspicious: bool = False
    threat_type: str = ""


class RegistryIntelligence:
    """Analyze registry changes for threat indicators."""
    
    @staticmethod
    def check_persistence_mechanism(path: str, value: str) -> Tuple[bool, str]:
        """Check if registry change indicates persistence mechanism."""
        path_lower = path.lower()
        
        # Check persistence paths
        for persist_path in PERSISTENCE_REGISTRY_PATHS:
            if persist_path.lower() in path_lower:
                # Check if value points to executable in temp/appdata
                if any(bad in value.lower() for bad in 
                       ['temp', 'appdata', 'programdata', '%temp%', '%appdata%']):
                    return True, "Persistence mechanism in temp/appdata folder"
                
                # Check for obfuscated paths
                if '%' in value or '\x00' in value:
                    return True, "Obfuscated persistence path"
                
                # Check for network paths
                if value.startswith('\\\\'):
                    return True, "Network-based persistence"
        
        return False, ""
    
    @staticmethod
    def check_injection_pattern(path: str, value: str) -> Tuple[bool, str]:
        """Check for code injection patterns."""
        path_lower = path.lower()
        
        # Check AppInit_DLLs (DLL injection)
        if "appinit_dlls" in path_lower:
            return True, "AppInit_DLLs injection detected"
        
        # Check COM object hijacking
        for com_path in COM_HIJACKING_PATHS:
            if com_path.lower() in path_lower:
                if "inprocserver32" in path_lower:
                    return True, "COM object hijacking detected"
        
        # Check for IFEO (Image File Execution Options) debugger
        if "image file execution options" in path_lower and "debugger" in path_lower:
            return True, "Debugger substitution (IFEO) detected"
        
        return False, ""
    
    @staticmethod
    def check_uac_bypass(path: str) -> Tuple[bool, str]:
        """Check for UAC bypass attempts."""
        path_lower = path.lower()
        
        for uac_path in UAC_BYPASS_PATHS:
            if uac_path.lower() in path_lower:
                return True, "UAC bypass registry path modified"
        
        # Check for specific UAC bypass techniques
        if "eventvwr" in path_lower or "fodhelper" in path_lower:
            return True, "Known UAC bypass path accessed"
        
        return False, ""
    
    @staticmethod
    def check_av_tampering(path: str, value_name: str) -> Tuple[bool, str]:
        """Check for attempts to disable antivirus."""
        path_lower = path.lower()
        value_lower = value_name.lower()
        
        # Check Windows Defender paths
        if "windows defender" in path_lower or "windefend" in path_lower:
            if any(disable in value_lower for disable in 
                   ["disable", "disablereatime", "disablebehavior"]):
                return True, "Windows Defender tampering detected"
        
        # Check for AMSI bypass
        if "amsi" in path_lower or "antimalware" in path_lower:
            if "disable" in value_lower or "false" in value_lower:
                return True, "AMSI bypass attempt detected"
        
        # Check for Defender policy modifications
        if "windows defender" in path_lower and "policy" in path_lower:
            return True, "Windows Defender policy modification"
        
        return False, ""
    
    @staticmethod
    def check_browser_hijacking(path: str, value: str) -> Tuple[bool, str]:
        """Check for browser hijacking."""
        path_lower = path.lower()
        
        for browser_path in BROWSER_HIJACKING_PATHS:
            if browser_path.lower() in path_lower:
                # Check if homepage/search settings are changed
                if any(setting in path_lower for setting in 
                       ['homepage', 'searchscopes', 'start page']):
                    if value and not any(trusted in value.lower() for trusted in
                                        ['google.com', 'bing.com', 'duckduckgo']):
                        return True, "Suspicious browser homepage/search engine"
        
        return False, ""
    
    @staticmethod
    def check_ransomware_indicators(path: str, value_name: str) -> Tuple[bool, str]:
        """Check for ransomware-related registry changes."""
        path_lower = path.lower()
        value_lower = value_name.lower()
        
        # Disable backup/recovery features (WannaCry, Notpetya)
        ransomware_keywords = [
            "shadowcopy", "vss", "backup", "recovery", "restore",
            "safemode", "bootmanager", "bootloader"
        ]
        
        if any(keyword in path_lower for keyword in ransomware_keywords):
            if any(disable in value_lower for disable in 
                   ["disable", "delete", "false", "0"]):
                return True, "Ransomware indicator: disabling backup/recovery"
        
        # Check for file association tampering
        if "extension" in path_lower or ".lnk" in path_lower:
            return True, "File association tampering (ransomware behavior)"
        
        return False, ""
    
    @staticmethod
    def check_service_tampering(path: str, service_name: str) -> Tuple[bool, str]:
        """Check for suspicious service modifications."""
        path_lower = path.lower()
        
        # Protected services shouldn't be modified
        for protected in PROTECTED_SERVICES:
            if protected.lower() in path_lower:
                return True, f"Modification of protected service: {protected}"
        
        # Check for startup type changes to services
        if "start" in path.lower():
            return True, "Service startup type modification"
        
        # Check for image path modifications
        if "imagepath" in path_lower:
            return True, "Service binary path modification"
        
        return False, ""


class WindowsRegistryMonitor:
    """Monitor Windows registry for malware indicators."""
    
    def __init__(self, on_threat: Optional[callable] = None):
        self.on_threat = on_threat or (lambda x: None)
        self.registry_changes = []
        self.lock = threading.Lock()
        self.running = False
        self.monitor_thread = None
    
    def start(self) -> None:
        """Start registry monitoring (Windows only)."""
        import sys
        if sys.platform != "win32":
            _log.warning("Registry monitoring only available on Windows")
            return
        
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        _log.info("Registry monitoring started")
    
    def stop(self) -> None:
        """Stop registry monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _log.info("Registry monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        try:
            # Try to use WMI for registry monitoring
            import wmi
            
            c = wmi.WMI()
            watcher = c.watch_for(
                event_type="modification",
                wmi_class="Win32_RegistryKeyChangeEvent",
                delay_secs=1
            )
            
            while self.running:
                try:
                    event = watcher(timeout_ms=1000)
                    if event:
                        self._process_registry_change(event)
                except Exception as e:
                    _log.debug(f"Error monitoring registry: {e}")
        
        except ImportError:
            _log.warning("WMI not available, falling back to polling")
            self._monitor_via_polling()
    
    def _monitor_via_polling(self) -> None:
        """Poll registry for changes (less efficient but works everywhere)."""
        try:
            import winreg
            
            # Monitor key persistence paths
            while self.running:
                try:
                    for hive_name in ['HKCU', 'HKLM']:
                        hive = winreg.HKEY_CURRENT_USER if hive_name == 'HKCU' else winreg.HKEY_LOCAL_MACHINE
                        
                        for persist_path in list(PERSISTENCE_REGISTRY_PATHS)[:5]:  # Limit for performance
                            if hive_name not in persist_path:
                                continue
                            
                            try:
                                path = persist_path.replace(f"{hive_name}\\", "")
                                key = winreg.OpenKey(hive, path, 0, winreg.KEY_READ)
                                
                                # Check for suspicious values
                                index = 0
                                while True:
                                    try:
                                        value_name, value_data, value_type = winreg.EnumValue(key, index)
                                        index += 1
                                        
                                        # Check if suspicious
                                        is_suspicious, reason = self._analyze_registry_value(
                                            persist_path, value_name, str(value_data)
                                        )
                                        
                                        if is_suspicious:
                                            self.on_threat({
                                                'type': 'registry_anomaly',
                                                'path': persist_path,
                                                'value': value_name,
                                                'reason': reason,
                                                'severity': 'high'
                                            })
                                    
                                    except OSError:
                                        break
                                
                                winreg.CloseKey(key)
                            
                            except Exception as e:
                                _log.debug(f"Error monitoring {persist_path}: {e}")
                    
                    time.sleep(30)  # Check every 30 seconds
                
                except Exception as e:
                    _log.debug(f"Error in registry polling: {e}")
                    time.sleep(30)
        
        except ImportError:
            _log.warning("Registry monitoring not available")
    
    def _process_registry_change(self, event) -> None:
        """Process a registry change event."""
        try:
            path = getattr(event, 'TargetInstance', None)
            if not path:
                return
            
            is_suspicious, reason = self._analyze_registry_value(
                str(path), "", ""
            )
            
            if is_suspicious:
                self.on_threat({
                    'type': 'registry_change',
                    'path': str(path),
                    'reason': reason,
                    'severity': 'high'
                })
        
        except Exception as e:
            _log.debug(f"Error processing registry change: {e}")
    
    def _analyze_registry_value(
        self,
        path: str,
        value_name: str,
        value_data: str
    ) -> Tuple[bool, str]:
        """Analyze registry value for malware indicators."""
        
        # Check all threat patterns
        checks = [
            RegistryIntelligence.check_persistence_mechanism(path, value_data),
            RegistryIntelligence.check_injection_pattern(path, value_data),
            RegistryIntelligence.check_uac_bypass(path),
            RegistryIntelligence.check_av_tampering(path, value_name),
            RegistryIntelligence.check_browser_hijacking(path, value_data),
            RegistryIntelligence.check_ransomware_indicators(path, value_name),
        ]
        
        for is_threat, reason in checks:
            if is_threat:
                return True, reason
        
        return False, ""
