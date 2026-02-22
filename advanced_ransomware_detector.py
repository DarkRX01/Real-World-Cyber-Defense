#!/usr/bin/env python3
"""
Advanced Ransomware Detection - Sophisticated ransomware pattern detection.
Detects encryption behavior, shadow copy manipulation, backup access, etc.
"""

import logging
import threading
import time
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from collections import deque, defaultdict
from pathlib import Path
import re

_log = logging.getLogger("CyberDefense.AdvancedRansomwareDetector")

# ==================== RANSOMWARE SIGNATURES ====================

# Known ransomware note filenames
RANSOMWARE_NOTE_NAMES = frozenset([
    'README.txt', 'READ_ME.txt', 'DECRYPT.txt', 'HOW_TO_RESTORE.txt',
    'HELP_TO_SAVE_FILES.txt', 'RESTORE_FILES.txt', 'DATA_RECOVERY.txt',
    'IMPORTANT.txt', 'WARNING.txt', 'PAYMENT.txt', 'RANSOM.txt',
    'decrypt_instruction.txt', 'files_encrypted.txt',
    '.txt', '.html', '.htm', 'how_to_decrypt_files.txt',
    'LOCKED.txt', 'CRYPTED.txt', 'ENCRYPTED.txt',
])

# File extensions added by ransomware
RANSOMWARE_EXTENSIONS = frozenset([
    '.locked', '.encrypted', '.crypto', '.cryptolocker',
    '.odin', '.dharma', '.crjob', '.cerber',
    '.crypt', '.crinf', '.locky', '.zerocrypt',
    '.aaa', '.abc', '.xyz', '.zzz',
    '.extension', '.extension_id', '.wallet', '.id_[a-f0-9]+',
])

# Registry paths ransomware typically modifies
RANSOMWARE_REG_MODIFICATIONS = frozenset([
    r'HKLM\\System\\CurrentControlSet\\Control\\SafeBoot',
    r'HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options',
    r'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
])

# Suspicious processes known to be associated with ransomware
RANSOMWARE_PROCESSES = frozenset([
    'explorer.exe',  # When doing unusual file ops
    'svchost.exe',   # When spawning child processes
    'system.exe',    # When accessing shadow copies
    'services.exe',  # When disabling security services
    'dwm.exe',       # Rarely does file operations
])

# Commands associated with ransomware attacks
RANSOMWARE_COMMANDS = [
    r'vssadmin.*delete.*shadows',  # Shadow copy deletion
    r'wmic.*shadowcopy.*delete',   # Shadow copy deletion
    r'diskshadow.*delete',         # Shadow copy deletion
    r'bcdedit.*disable safeboot',  # Disable SafeBoot
    r'netsh.*firewall.*off',       # Firewall tampering
    r'net.*share.*delete',         # Share deletion
    r'schtasks.*delete',           # Task deletion
    r'cd.*cmd.*del.*rd.*s',        # Recursive deletion
    r'powershell.*Remove-Item',    # File deletion via PowerShell
]

# ==================== DATA STRUCTURES ====================

@dataclass
class FileEncryptionActivity:
    """Represents potential file encryption activity."""
    timestamp: float
    filepath: str
    process_name: str
    operation: str  # 'create', 'modify', 'encrypt_pattern'
    file_size_before: int
    file_size_after: int
    entropy_change: float


@dataclass
class RansomwareIndicator:
    """Represents a ransomware detection indicator."""
    indicator_type: str  # 'mass_encryption', 'shadow_copy_access', 'backup_access', etc
    severity: str
    confidence: int  # 0-100
    timestamp: float
    details: Dict


# ==================== RANSOMWARE ANALYSIS ====================

class EncryptionDetector:
    """Detect active file encryption."""
    
    @staticmethod
    def analyze_file_modifications(
        file_modifications: List[Dict],
        window_seconds: int = 60
    ) -> List[RansomwareIndicator]:
        """
        Analyze file modification patterns for encryption behavior.
        
        Expected file_modifications format:
        [{
            'path': str,
            'process': str,
            'timestamp': float,
            'size_before': int,
            'size_after': int
        }, ...]
        """
        indicators = []
        
        if not file_modifications:
            return indicators
        
        # Filter by time window
        current_time = time.time()
        recent = [m for m in file_modifications 
                 if current_time - m.get('timestamp', 0) <= window_seconds]
        
        if len(recent) == 0:
            return indicators
        
        # Detection 1: Mass file modification in short time window
        modification_count = len(recent)
        if modification_count >= 100:  # Aggressive threshold
            indicators.append(RansomwareIndicator(
                indicator_type='mass_file_modification',
                severity='critical',
                confidence=90,
                timestamp=current_time,
                details={'modifications_in_window': modification_count, 'window_seconds': window_seconds}
            ))
        elif modification_count >= 50:
            indicators.append(RansomwareIndicator(
                indicator_type='high_file_activity',
                severity='high',
                confidence=75,
                timestamp=current_time,
                details={'modifications_in_window': modification_count}
            ))
        
        # Detection 2: Suspicious file size changes (encrypted = larger or same)
        size_increases = []
        for mod in recent:
            size_before = mod.get('size_before', 0)
            size_after = mod.get('size_after', 0)
            
            if size_before > 0 and size_after >= size_before:
                size_increases.append(mod)
        
        if size_increases and len(size_increases) / len(recent) > 0.8:
            indicators.append(RansomwareIndicator(
                indicator_type='suspicious_file_size_changes',
                severity='high',
                confidence=70,
                timestamp=current_time,
                details={'files_with_size_increase': len(size_increases)}
            ))
        
        # Detection 3: Modification of unusual file types
        unusual_extensions = defaultdict(int)
        common_types = {'.txt', '.doc', '.jpg', '.png', '.pdf', '.xls', '.ppt'}
        
        for mod in recent:
            fp = mod.get('path', '')
            ext = Path(fp).suffix.lower() if fp else ''
            
            if ext not in common_types and ext:
                unusual_extensions[ext] += 1
        
        if unusual_extensions and sum(unusual_extensions.values()) > 10:
            indicators.append(RansomwareIndicator(
                indicator_type='unusual_file_extensions_modified',
                severity='medium',
                confidence=60,
                timestamp=current_time,
                details={'unusual_extensions': dict(list(unusual_extensions.items())[:5])}
            ))
        
        # Detection 4: Single process causing massive changes
        process_counts = defaultdict(int)
        for mod in recent:
            proc = mod.get('process', '')
            process_counts[proc] += 1
        
        for proc, count in process_counts.items():
            if count > 80:
                indicators.append(RansomwareIndicator(
                    indicator_type='single_process_mass_modification',
                    severity='critical',
                    confidence=85,
                    timestamp=current_time,
                    details={'process': proc, 'modification_count': count}
                ))
        
        return indicators


class RansomwareCommandDetector:
    """Detect ransomware-related commands."""
    
    @staticmethod
    def scan_command_line(cmdline: str) -> List[RansomwareIndicator]:
        """Scan command line for ransomware indicators."""
        indicators = []
        cmdline_lower = cmdline.lower()
        
        # Check against ransomware command patterns
        for pattern in RANSOMWARE_COMMANDS:
            if re.search(pattern, cmdline_lower):
                severity = 'critical' if 'shadowcopy' in pattern or 'bcdedit' in pattern else 'high'
                indicators.append(RansomwareIndicator(
                    indicator_type='ransomware_command_detected',
                    severity=severity,
                    confidence=85,
                    timestamp=time.time(),
                    details={'command_pattern': pattern, 'actual_command': cmdline[:100]}
                ))
        
        # Detect chained dangerous commands
        dangerous_keywords = ['vssadmin', 'wmic', 'shadowcopy', 'delete', 'diskshadow', 'bcdedit']
        found_keywords = [kw for kw in dangerous_keywords if kw in cmdline_lower]
        
        if len(found_keywords) >= 2:
            indicators.append(RansomwareIndicator(
                indicator_type='chained_dangerous_commands',
                severity='critical',
                confidence=90,
                timestamp=time.time(),
                details={'dangerous_keywords': found_keywords}
            ))
        
        return indicators


class ShadowCopyMonitor:
    """Detect shadow copy access and deletion (signature of ransomware)."""
    
    @staticmethod
    def detect_shadow_copy_access(file_accesses: List[Dict]) -> List[RansomwareIndicator]:
        """Detect access to shadow copy files and metadata."""
        indicators = []
        
        shadow_copy_paths = frozenset([
            r'\\?\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy',
            r'Volume{', '.shadow', 'shadowcopy',
            r'System Volume Information',
        ])
        
        shadow_copy_accesses = []
        for access in file_accesses:
            path = access.get('path', '').lower()
            
            if any(sc_path in path for sc_path in shadow_copy_paths):
                shadow_copy_accesses.append(access)
        
        if shadow_copy_accesses:
            indicators.append(RansomwareIndicator(
                indicator_type='shadow_copy_access',
                severity='critical',
                confidence=90,
                timestamp=time.time(),
                details={'shadow_copy_access_count': len(shadow_copy_accesses)}
            ))
        
        return indicators
    
    @staticmethod
    def detect_backup_access(file_accesses: List[Dict]) -> List[RansomwareIndicator]:
        """Detect access to backup files/folders."""
        indicators = []
        
        backup_paths = frozenset([
            'backup', '.backup', '_backup', '-backup',
            '.bak', '.old', '.archive', 'archive',
            'restore', '.restore', '_restore',
        ])
        
        backup_accesses = []
        for access in file_accesses:
            path = access.get('path', '').lower()
            
            if any(bp in path for bp in backup_paths):
                if access.get('operation', '').lower() in ['delete', 'modify', 'encrypt']:
                    backup_accesses.append(access)
        
        if backup_accesses and len(backup_accesses) >= 5:
            indicators.append(RansomwareIndicator(
                indicator_type='backup_file_targeting',
                severity='critical',
                confidence=85,
                timestamp=time.time(),
                details={'backup_accesses': len(backup_accesses)}
            ))
        
        return indicators


class RansomwareNoteDetector:
    """Detect creation of ransom notes."""
    
    @staticmethod
    def detect_ransom_note_creation(file_creations: List[Dict]) -> List[RansomwareIndicator]:
        """Detect creation of ransom note files."""
        indicators = []
        
        ransom_notes = []
        for creation in file_creations:
            filename = Path(creation.get('path', '')).name.lower()
            
            if any(note_name in filename for note_name in RANSOMWARE_NOTE_NAMES):
                ransom_notes.append(creation)
        
        if ransom_notes:
            indicators.append(RansomwareIndicator(
                indicator_type='ransom_note_created',
                severity='critical',
                confidence=95,
                timestamp=time.time(),
                details={
                    'note_count': len(ransom_notes),
                    'examples': [Path(r.get('path', '')).name for r in ransom_notes[:3]]
                }
            ))
        
        return indicators


# ==================== ADVANCED RANSOMWARE DETECTOR ====================

class AdvancedRansomwareDetector:
    """Comprehensive ransomware detection engine."""
    
    def __init__(self, on_threat: Optional[callable] = None):
        self.on_threat = on_threat or (lambda x: None)
        self.file_modifications: deque = deque(maxlen=10000)
        self.file_accesses: deque = deque(maxlen=10000)
        self.file_creations: deque = deque(maxlen=10000)
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        self.detectionCount = 0
    
    def start(self) -> None:
        """Start ransomware detection."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        _log.info("Advanced ransomware detection started")
    
    def stop(self) -> None:
        """Stop ransomware detection."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _log.info("Advanced ransomware detection stopped")
    
    def record_file_modification(
        self,
        filepath: str,
        process_name: str,
        size_before: int,
        size_after: int
    ) -> None:
        """Record a file modification for analysis."""
        with self.lock:
            self.file_modifications.append({
                'path': filepath,
                'process': process_name,
                'timestamp': time.time(),
                'size_before': size_before,
                'size_after': size_after
            })
    
    def record_file_access(
        self,
        filepath: str,
        operation: str,  # 'read', 'write', 'delete', 'encrypt'
        process_name: str
    ) -> None:
        """Record a file access event."""
        with self.lock:
            self.file_accesses.append({
                'path': filepath,
                'operation': operation,
                'process': process_name,
                'timestamp': time.time()
            })
    
    def record_file_creation(
        self,
        filepath: str,
        process_name: str
    ) -> None:
        """Record a file creation event."""
        with self.lock:
            self.file_creations.append({
                'path': filepath,
                'process': process_name,
                'timestamp': time.time()
            })
    
    def analyze_ransomware_risk(self) -> Tuple[str, int]:
        """
        Analyze current ransomware risk based on detected indicators.
        
        Returns: (risk_level: 'critical'|'high'|'medium'|'low', confidence: 0-100)
        """
        all_indicators = []
        
        with self.lock:
            mods = list(self.file_modifications)
            accesses = list(self.file_accesses)
            creates = list(self.file_creations)
        
        # 1. Encryption activity
        indicators = EncryptionDetector.analyze_file_modifications(mods, window_seconds=60)
        all_indicators.extend(indicators)
        
        # 2. Shadow copy access
        indicators = ShadowCopyMonitor.detect_shadow_copy_access(accesses)
        all_indicators.extend(indicators)
        
        # 3. Backup targeting
        indicators = ShadowCopyMonitor.detect_backup_access(accesses)
        all_indicators.extend(indicators)
        
        # 4. Ransom note creation
        indicators = RansomwareNoteDetector.detect_ransom_note_creation(creates)
        all_indicators.extend(indicators)
        
        # Report all indicators
        for indicator in all_indicators:
            self.on_threat({
                'type': 'ransomware_indicator',
                'indicator_type': indicator.indicator_type,
                'severity': indicator.severity,
                'confidence': indicator.confidence,
                'details': indicator.details
            })
        
        # Calculate overall risk
        if not all_indicators:
            return 'low', 10
        
        critical_count = len([i for i in all_indicators if i.severity == 'critical'])
        high_count = len([i for i in all_indicators if i.severity == 'high'])
        
        if critical_count >= 2:
            return 'critical', min(100, 90 + critical_count * 5)
        elif critical_count >= 1:
            return 'high', 80
        elif high_count >= 3:
            return 'high', 75
        elif high_count >= 1:
            return 'medium', 60
        else:
            return 'low', 30
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                # Periodic ransomware risk assessment
                risk, confidence = self.analyze_ransomware_risk()
                
                if risk == 'critical' or (risk == 'high' and confidence >= 75):
                    self.on_threat({
                        'type': 'ransomware_risk_elevated',
                        'risk_level': risk,
                        'confidence': confidence
                    })
                
                time.sleep(5)
            
            except Exception as e:
                _log.debug(f"Error in ransomware monitoring loop: {e}")
                time.sleep(5)
