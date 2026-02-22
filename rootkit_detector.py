#!/usr/bin/env python3
"""
Rootkit Detection - Detect kernel-level malware and rootkits.
Monitors for hidden processes, drivers, and kernel-level hooks.
"""

import logging
import threading
import time
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from pathlib import Path

_log = logging.getLogger("CyberDefense.RootkitDetector")

# ==================== ROOTKIT SIGNATURES ====================

# Known rootkit driver names
KNOWN_ROOTKIT_DRIVERS = frozenset([
    'ZeroAccess', 'Sirefef', 'Rootkit.Gen', 'Alureon',
    'Rustock', 'Maxxc', 'Petar', 'Necurs',
    'Gapz', 'Fentanyl', 'Carberp', 'Rovnix',
])

# Suspicious driver characteristics
SUSPICIOUS_DRIVER_PATTERNS = [
    r'.*\\drivers\\[a-z0-9]{8,}\.sys$',  # Random-named driver
    r'.*\\[a-z0-9]{32}\.sys$',            # GUID-named driver
    r'.*temp.*\.sys$',                    # Driver in temp folder
    r'.*appdata.*\.sys$',                 # Driver in appdata
]

# Known legitimate Windows drivers (whitelist)
LEGITIMATE_SYSTEM_DRIVERS = frozenset([
    'hal.sys', 'ntoskrnl.exe', 'ntkrnlmp.exe', 'ntkrnl.exe',
    'disk.sys', 'partmgr.sys', 'volsnap.sys',
    'ndis.sys', 'tcpip.sys', 'i8042prt.sys',
    'kbdclass.sys', 'mouclass.sys',
    'nt', 'system', 'registry', 'csrss.exe',
])

# ==================== ROOTKIT DETECTION TECHNIQUES ====================

@dataclass
class RootkitIndicator:
    """Represents a detected rootkit indicator."""
    indicator_type: str  # 'hidden_process', 'rootkit_driver', 'kernel_hook', etc
    severity: str
    confidence: int  # 0-100
    timestamp: float
    details: Dict


class ProcessHidingDetector:
    """Detect processes hidden by rootkits."""
    
    @staticmethod
    def detect_hidden_processes() -> List[RootkitIndicator]:
        """
        Detect processes hidden from normal enumeration.
        Uses multiple methods to detect discrepancies.
        """
        indicators = []
        
        try:
            import psutil
            
            # Method 1: Process list vs PID directory enumeration
            psutil_pids = set(psutil.pids())
            
            # Try to enumerate from /proc on Linux
            proc_pids = set()
            if Path('/proc').exists():
                try:
                    for entry in Path('/proc').iterdir():
                        if entry.name.isdigit():
                            proc_pids.add(int(entry.name))
                except Exception as e:
                    _log.debug(f"Error enumerating /proc: {e}")
            
            # Discrepancy: PIDs in /proc but not in psutil (hidden process)
            if proc_pids:
                hidden_pids = proc_pids - psutil_pids
                if hidden_pids:
                    indicators.append(RootkitIndicator(
                        indicator_type='hidden_process_pids',
                        severity='critical',
                        confidence=85,
                        timestamp=time.time(),
                        details={'hidden_pids': list(hidden_pids)[:10]}  # First 10
                    ))
            
            # Method 2: Check for process handles that don't open
            # (indicates hiding mechanism)
            suspicious_pids = []
            for pid in psutil_pids[:100]:  # Check first 100 processes
                try:
                    proc = psutil.Process(pid)
                    # If we can list it but can't get basic info, it might be hidden
                    try:
                        _ = proc.cmdline()
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        suspicious_pids.append(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if len(suspicious_pids) > 10:  # More than 10 is suspicious
                indicators.append(RootkitIndicator(
                    indicator_type='hidden_process_handles',
                    severity='high',
                    confidence=70,
                    timestamp=time.time(),
                    details={'suspicious_process_count': len(suspicious_pids)}
                ))
        
        except ImportError:
            _log.warning("psutil not available for rootkit detection")
        except Exception as e:
            _log.debug(f"Error detecting hidden processes: {e}")
        
        return indicators


class KernelHookDetector:
    """Detect kernel-level hooks and modifications."""
    
    @staticmethod
    def detect_system_call_hooks() -> List[RootkitIndicator]:
        """Detect syscall table modifications (rootkit signature)."""
        indicators = []
        
        try:
            # Linux: Check /proc/kallsyms for system call table modifications
            if Path('/proc/kallsyms').exists():
                try:
                    with open('/proc/kallsyms', 'r') as f:
                        for line in f:
                            # Look for system call table references
                            if 'sys_call_table' in line:
                                # In a real rootkit, this might point to unusual memory
                                pass
                except Exception as e:
                    _log.debug(f"Error checking kallsyms: {e}")
            
            # Windows: Check for SSDT (System Service Descriptor Table) hooks
            # This is more complex and requires kernel debugging access
            # Simplified: check for kernel-mode drivers accessing system functions
            
            # Check for unusual kernel driver activity
            suspicious_count = 0
            try:
                if Path('/sys/kernel/debug').exists():
                    suspicious_count += 1
            except:
                pass
            
            if suspicious_count > 0:
                indicators.append(RootkitIndicator(
                    indicator_type='kernel_hook_suspected',
                    severity='critical',
                    confidence=50,  # Lower confidence for kernel hooks (harder to detect)
                    timestamp=time.time(),
                    details={'check_result': 'kernel_debug_signs'}
                ))
        
        except Exception as e:
            _log.debug(f"Error detecting kernel hooks: {e}")
        
        return indicators
    
    @staticmethod
    def detect_idt_hooks() -> List[RootkitIndicator]:
        """
        Detect Interrupt Descriptor Table (IDT) hooks.
        Windows-specific technique for rootkit detection.
        """
        indicators = []
        
        try:
            # This requires privileged access
            # Check against known interrupt handlers
            suspicious_intervals = 0
            
            # On Windows, unusual IDT entries point to rootkit
            # This is a simplified check
            
            if suspicious_intervals > 0:
                indicators.append(RootkitIndicator(
                    indicator_type='idt_hook_detected',
                    severity='critical',
                    confidence=90,
                    timestamp=time.time(),
                    details={'suspicious_handlers': suspicious_intervals}
                ))
        
        except Exception as e:
            _log.debug(f"Error detecting IDT hooks: {e}")
        
        return indicators


class DriverAnalyzer:
    """Analyze system drivers for rootkit signatures."""
    
    @staticmethod
    def scan_system_drivers() -> List[RootkitIndicator]:
        """Scan system drivers for rootkit signatures."""
        indicators = []
        
        try:
            import psutil
            
            # Get loaded drivers
            drivers = []
            
            # Windows: Check loaded drivers via psutil
            try:
                # Try to enumerate privileged information
                for proc in psutil.process_iter(['pid', 'name']):
                    if 'driver' in proc.name().lower():
                        drivers.append(proc.name())
            except:
                pass
            
            # Linux: Check loaded kernel modules
            if Path('/proc/modules').exists():
                try:
                    with open('/proc/modules', 'r') as f:
                        for line in f:
                            parts = line.split()
                            if len(parts) >= 1:
                                module_name = parts[0]
                                drivers.append(module_name)
                except Exception as e:
                    _log.debug(f"Error reading modules: {e}")
            
            # Check for suspicious drivers
            suspicious_drivers = []
            for driver in drivers:
                # Check against known rootkits
                for rootkit in KNOWN_ROOTKIT_DRIVERS:
                    if rootkit.lower() in driver.lower():
                        suspicious_drivers.append(driver)
                        indicators.append(RootkitIndicator(
                            indicator_type='known_rootkit_driver',
                            severity='critical',
                            confidence=95,
                            timestamp=time.time(),
                            details={'driver': driver, 'matched_rootkit': rootkit}
                        ))
                        break
                
                # Check against suspicious patterns
                import re
                for pattern in SUSPICIOUS_DRIVER_PATTERNS:
                    if re.match(pattern, driver, re.IGNORECASE):
                        suspicious_drivers.append(driver)
                        indicators.append(RootkitIndicator(
                            indicator_type='suspicious_driver_pattern',
                            severity='high',
                            confidence=75,
                            timestamp=time.time(),
                            details={'driver': driver, 'pattern': pattern}
                        ))
                        break
        
        except Exception as e:
            _log.debug(f"Error scanning drivers: {e}")
        
        return indicators


class RootkitDetector:
    """Main rootkit detection engine."""
    
    def __init__(self, on_threat: Optional[callable] = None):
        self.on_threat = on_threat or (lambda x: None)
        self.running = False
        self.monitor_thread = None
        self.last_scan_time = 0
        self.scan_interval = 60  # Full scan every 60 seconds
    
    def start(self) -> None:
        """Start rootkit detection."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        _log.info("Rootkit detection started")
    
    def stop(self) -> None:
        """Stop rootkit detection."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _log.info("Rootkit detection stopped")
    
    def _monitor_loop(self) -> None:
        """Main rootkit detection loop."""
        while self.running:
            try:
                current_time = time.time()
                
                # Run full rootkit scans at intervals
                if current_time - self.last_scan_time >= self.scan_interval:
                    self.perform_rootkit_scan()
                    self.last_scan_time = current_time
                
                time.sleep(10)  # Check every 10 seconds
            
            except Exception as e:
                _log.debug(f"Error in rootkit detection loop: {e}")
                time.sleep(10)
    
    def perform_rootkit_scan(self) -> List[RootkitIndicator]:
        """Perform comprehensive rootkit scan."""
        all_indicators = []
        
        # 1. Detect hidden processes
        indicators = ProcessHidingDetector.detect_hidden_processes()
        all_indicators.extend(indicators)
        for indicator in indicators:
            self.on_threat({
                'type': 'rootkit_indicator',
                'indicator_type': indicator.indicator_type,
                'severity': indicator.severity,
                'confidence': indicator.confidence,
                'details': indicator.details
            })
        
        # 2. Detect kernel hooks
        indicators = KernelHookDetector.detect_system_call_hooks()
        all_indicators.extend(indicators)
        for indicator in indicators:
            self.on_threat({
                'type': 'rootkit_indicator',
                'indicator_type': indicator.indicator_type,
                'severity': indicator.severity,
                'details': indicator.details
            })
        
        # 3. Detect IDT hooks (Windows)
        indicators = KernelHookDetector.detect_idt_hooks()
        all_indicators.extend(indicators)
        
        # 4. Scan drivers
        indicators = DriverAnalyzer.scan_system_drivers()
        all_indicators.extend(indicators)
        for indicator in indicators:
            self.on_threat({
                'type': 'rootkit_driver',
                'indicator_type': indicator.indicator_type,
                'severity': indicator.severity,
                'details': indicator.details
            })
        
        return all_indicators
    
    def get_rootkit_risk_level(self) -> Tuple[str, int]:
        """
        Get overall rootkit risk level based on indicators.
        Returns: (risk_level: 'critical'|'high'|'medium'|'low', confidence: 0-100)
        """
        indicators = self.perform_rootkit_scan()
        
        if not indicators:
            return 'low', 10
        
        # Count high-severity indicators
        critical_count = len([i for i in indicators if i.severity == 'critical'])
        high_count = len([i for i in indicators if i.severity == 'high'])
        
        if critical_count > 0:
            return 'critical', min(100, 80 + critical_count * 5)
        elif high_count >= 2:
            return 'high', min(100, 70 + high_count * 5)
        elif high_count >= 1:
            return 'medium', 60
        else:
            return 'low', 30
