#!/usr/bin/env python3
"""
Process Injection & Code Hooking Detection - Detect code injection, DLL hooking, API hooking.
Monitors for runtime code modification and process manipulation attacks.
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path

_log = logging.getLogger("CyberDefense.ProcessInjectionDetector")

# ==================== THREAT SIGNATURES ====================

# Known legitimate processes (whitelist for false positive reduction)
LEGITIMATE_INJECTORS = frozenset([
    'explorer.exe',      # Windows Explorer (legitimate window hooks)
    'dwm.exe',           # Desktop Window Manager
    'svchost.exe',       # Windows Service Host
    'lsass.exe',         # Local Security Authority
    'services.exe',      # Services process
    'winlogon.exe',      # Windows Logon
])

# Suspicious injection techniques
INJECTION_TECHNIQUES = {
    'CreateRemoteThread': 'T1055.001 - Process Injection: Dynamic-link Library Injection',
    'NtCreateThreadEx': 'T1055.001 - Process Injection: Dynamic-link Library Injection',
    'QueueUserAPC': 'T1055.004 - Process Injection: Asynchronous Procedure Call',
    'SetWindowsHookEx': 'T1055.014 - Process Injection: Hooking',
    'WriteProcessMemory': 'T1578 - Modify Cloud Compute Infrastructure',
    'VirtualAllocEx': 'T1027 - Obfuscated Files or Information',
    'RtlCreateUserThread': 'T1055.001 - Process Injection',
}

# Suspicious DLL patterns
SUSPICIOUS_DLL_PATTERNS = [
    r'.*\.temp\.*\.dll$',
    r'.*\AppData.*\.dll$',
    r'.*%TEMP%.*\.dll$',
    r'^[a-f0-9]{32}\.dll$',  # GUID-named DLL
    r'^[a-z0-9]{16,}\.dll$',  # Random text DLL
    r'.*\.(exe\.dll|scr\.dll)$',  # Double extensions
]

# APIs commonly hooked by malware
COMMONLY_HOOKED_APIS = frozenset([
    'CreateProcessA', 'CreateProcessW', 'CreateProcessAsUserA', 'CreateProcessAsUserW',
    'LoadLibraryA', 'LoadLibraryW', 'GetModuleHandleA', 'GetModuleHandleW',
    'WinExec', 'ShellExecuteA', 'ShellExecuteW',
    'WriteFile', 'ReadFile', 'ReadProcessMemory', 'WriteProcessMemory',
    'RegOpenKeyA', 'RegOpenKeyW', 'RegSetValueEx', 'RegQueryValueEx',
    'GetFileAttributesA', 'GetFileAttributesW',
])

# ==================== DATA STRUCTURES ====================

@dataclass
class ProcessSnapshot:
    """Snapshot of process state."""
    pid: int
    name: str
    exe_path: str
    timestamp: float
    loaded_dlls: Set[str]
    opened_handles: Set[str]
    threads: Dict[int, bool]  # thread_id -> is_suspended
    memory_regions: List[Dict]  # [{address, size, protect, type}]
    hooked_apis: Dict[str, str]  # {api_name: hooked_module}


@dataclass
class InjectionIndicator:
    """Represents a detected injection indicator."""
    detection_type: str  # 'dll_injection', 'code_cave', 'api_hook', etc
    target_process: str
    source_process: str
    severity: str  # 'critical', 'high', 'medium'
    confidence: int  # 0-100
    timestamp: float
    details: Dict


class MemoryAnalyzer:
    """Analyze process memory for injection indicators."""
    
    @staticmethod
    def detect_code_injection(process_id: int) -> List[InjectionIndicator]:
        """Detect code injection in process memory."""
        indicators = []
        
        try:
            import psutil
            
            proc = psutil.Process(process_id)
            
            # Check for suspicious memory patterns
            memory_info = proc.memory_info()
            
            # Detection 1: Unusual memory allocation patterns
            if memory_info.private > memory_info.shared:
                ratio = memory_info.private / max(memory_info.shared, 1)
                if ratio > 100:  # Highly unusual ratio
                    indicators.append(InjectionIndicator(
                        detection_type='unusual_memory_ratio',
                        target_process=proc.name(),
                        source_process='unknown',
                        severity='medium',
                        confidence=50,
                        timestamp=time.time(),
                        details={'private_mb': memory_info.private / 1024 / 1024,
                                'shared_mb': memory_info.shared / 1024 / 1024}
                    ))
            
            # Detection 2: Check for RWX (read-write-execute) memory regions
            try:
                # This requires elevated privileges
                for segment in proc.memory_maps():
                    if 'rwx' in segment.perms.lower():
                        indicators.append(InjectionIndicator(
                            detection_type='executable_memory_cave',
                            target_process=proc.name(),
                            source_process='unknown',
                            severity='critical',
                            confidence=90,
                            timestamp=time.time(),
                            details={'address': segment.addr, 'size': segment.size}
                        ))
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        
        except Exception as e:
            _log.debug(f"Error analyzing memory: {e}")
        
        return indicators
    
    @staticmethod
    def detect_api_hooking(process_id: int) -> List[InjectionIndicator]:
        """Detect API hooking (IAT, EAT hooks)."""
        indicators = []
        
        try:
            import psutil
            
            proc = psutil.Process(process_id)
            
            # Check for suspicious module loads
            try:
                dlls = proc.memory_maps()
                suspicious_dlls = []
                
                for dll in dlls:
                    # Check for DLLs in temp/cache
                    if any(path in dll.path.lower() for path in 
                           ['temp', 'appdata', 'programdata', 'cache']):
                        suspicious_dlls.append(dll.path)
                    
                    # Check for random-named DLLs
                    import re
                    filename = Path(dll.path).name
                    if re.match(r'^[a-f0-9]{8,}\.dll$', filename.lower()):
                        suspicious_dlls.append(dll.path)
                
                if suspicious_dlls:
                    indicators.append(InjectionIndicator(
                        detection_type='suspicious_dll_load',
                        target_process=proc.name(),
                        source_process='unknown',
                        severity='high',
                        confidence=75,
                        timestamp=time.time(),
                        details={'suspicious_dlls': suspicious_dlls}
                    ))
            
            except Exception as e:
                _log.debug(f"Error checking DLLs: {e}")
        
        except Exception as e:
            _log.debug(f"Error detecting API hooks: {e}")
        
        return indicators
    
    @staticmethod
    def detect_dll_injection(process_id: int, previous_dlls: Optional[Set[str]] = None) -> List[InjectionIndicator]:
        """Detect DLL injection by comparing loaded modules."""
        indicators = []
        
        try:
            import psutil
            
            proc = psutil.Process(process_id)
            current_dlls = set()
            
            try:
                for dll in proc.memory_maps():
                    if dll.path.endswith('.dll'):
                        current_dlls.add(dll.path)
            except psutil.AccessDenied:
                return indicators
            
            if previous_dlls:
                new_dlls = current_dlls - previous_dlls
                
                # New DLLs loaded
                for dll in new_dlls:
                    dll_path = Path(dll)
                    
                    # Check for suspicious patterns
                    if any(pattern in dll.lower() for pattern in 
                           ['temp', 'appdata', '%temp%', 'random', 'uuid']):
                        indicators.append(InjectionIndicator(
                            detection_type='suspicious_dll_injection',
                            target_process=proc.name(),
                            source_process='unknown',
                            severity='high',
                            confidence=80,
                            timestamp=time.time(),
                            details={'injected_dll': dll}
                        ))
            
            return indicators
        
        except Exception as e:
            _log.debug(f"Error detecting DLL injection: {e}")
        
        return indicators


class ProcessMonitor:
    """Monitor processes for injection and hooking attacks."""
    
    def __init__(self, on_threat: Optional[callable] = None):
        self.on_threat = on_threat or (lambda x: None)
        self.snapshots: Dict[int, ProcessSnapshot] = {}
        self.lock = threading.Lock()
        self.running = False
        self.monitor_thread = None
    
    def start(self) -> None:
        """Start process monitoring."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        _log.info("Process injection/hooking monitoring started")
    
    def stop(self) -> None:
        """Stop process monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _log.info("Process injection/hooking monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        try:
            import psutil
            
            while self.running:
                try:
                    for proc in psutil.process_iter(['pid', 'name']):
                        if not self.running:
                            break
                        
                        try:
                            pid = proc.pid
                            
                            # Skip system processes on whitelist
                            if proc.name() in LEGITIMATE_INJECTORS:
                                continue
                            
                            # Check for code injection
                            indicators = MemoryAnalyzer.detect_code_injection(pid)
                            for indicator in indicators:
                                self.on_threat({
                                    'type': 'code_injection',
                                    'process': proc.name(),
                                    'pid': pid,
                                    'detection': indicator.detection_type,
                                    'severity': indicator.severity,
                                    'confidence': indicator.confidence,
                                    'details': indicator.details
                                })
                            
                            # Check for API hooking
                            indicators = MemoryAnalyzer.detect_api_hooking(pid)
                            for indicator in indicators:
                                self.on_threat({
                                    'type': 'api_hooking',
                                    'process': proc.name(),
                                    'pid': pid,
                                    'detection': indicator.detection_type,
                                    'severity': indicator.severity,
                                    'details': indicator.details
                                })
                        
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    time.sleep(10)
                
                except Exception as e:
                    _log.debug(f"Error in process monitoring loop: {e}")
                    time.sleep(10)
        
        except ImportError:
            _log.warning("psutil not available for process monitoring")
    
    def detect_suspicious_process_creation(
        self,
        parent_process: str,
        child_process: str,
        cmdline: str
    ) -> Tuple[bool, List[str]]:
        """Detect suspicious process creation patterns."""
        alerts = []
        
        # Known parent-child anomalies
        suspicious_spawns = {
            'explorer.exe': ['powershell.exe', 'cmd.exe', 'wscript.exe', 'cscript.exe'],
            'svchost.exe': ['cmd.exe', 'powershell.exe', 'notepad.exe'],
            'dwm.exe': ['cmd.exe', 'powershell.exe'],
            'winlogon.exe': ['cmd.exe', 'powershell.exe'],
        }
        
        parent_lower = parent_process.lower()
        child_lower = child_process.lower()
        
        if parent_lower in suspicious_spawns:
            if any(child.lower() in child_lower for child in suspicious_spawns[parent_lower]):
                alerts.append(f"Suspicious child process: {parent_process} -> {child_process}")
        
        # Suspicious command line patterns
        suspicious_patterns = [
            'powershell.*-enc',  # Encoded PowerShell
            'cmd.*&&',            # Command chaining
            'rundll32.*http',     # RUNDLL32 executing scripts
            'regsvr32.*http',     # REGSVR32 proxy execution
        ]
        
        import re
        for pattern in suspicious_patterns:
            if re.search(pattern, cmdline, re.IGNORECASE):
                alerts.append(f"Suspicious command line pattern: {pattern}")
        
        return len(alerts) > 0, alerts
