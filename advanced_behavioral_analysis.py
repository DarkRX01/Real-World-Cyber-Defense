#!/usr/bin/env python3
"""
Advanced Behavioral Analysis - ML-free machine learning style threat detection
Uses statistical analysis, pattern matching, and behavior correlation to detect threats.
No ML libraries required - pure statistical analysis.
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
import statistics
import math

_log = logging.getLogger("CyberDefense.BehavioralAnalysis")

# ==================== THREAT PATTERNS ====================

# Process behavior baselines (normal activity thresholds)
PROCESS_BASELINES = {
    'explorer.exe': {
        'max_file_ops': 100,
        'max_registry_ops': 20,
        'max_network_conn': 10,
        'max_child_processes': 5,
    },
    'svchost.exe': {
        'max_file_ops': 50,
        'max_registry_ops': 10,
        'max_network_conn': 20,
        'max_child_processes': 2,
    },
    'chrome.exe': {
        'max_file_ops': 200,
        'max_registry_ops': 50,
        'max_network_conn': 100,
        'max_child_processes': 10,
    },
    'firefox.exe': {
        'max_file_ops': 200,
        'max_registry_ops': 50,
        'max_network_conn': 100,
        'max_child_processes': 10,
    },
}

# Suspicious behavior patterns
SUSPICIOUS_BEHAVIORS = {
    'encryption_activity': {
        'indicators': ['WriteFile', 'CreateFile', 'ReadFile', 'SetFilePointer'],
        'threshold': 100,  # file ops
        'time_window': 30,  # seconds
        'severity': 'high'
    },
    'privilege_escalation': {
        'indicators': ['CreateProcessAsUser', 'GetTokenInformation', 'ImpersonateLoggedOnUser'],
        'threshold': 5,
        'time_window': 60,
        'severity': 'critical'
    },
    'persistence': {
        'indicators': ['RegSetValueEx', 'RegCreateKeyEx', 'WriteFile'],
        'paths': ['Run', 'Startup', 'Services'],
        'threshold': 3,
        'severity': 'high'
    },
    'data_exfiltration': {
        'indicators': ['send', 'recv', 'connect'],
        'threshold': 50,  # MB sent
        'time_window': 60,
        'severity': 'critical'
    }
}

# ==================== DATA STRUCTURES ====================

@dataclass
class ProcessBehavior:
    """Represents a process's behavior profile."""
    process_name: str
    pid: int
    timestamp: float
    file_operations: int = 0
    registry_operations: int = 0
    network_connections: int = 0
    child_processes: int = 0
    memory_growth: float = 0.0
    cpu_usage: float = 0.0
    suspicious_apis: List[str] = None
    suspicious_commands: List[str] = None
    anomaly_score: float = 0.0
    
    def __post_init__(self):
        if self.suspicious_apis is None:
            self.suspicious_apis = []
        if self.suspicious_commands is None:
            self.suspicious_commands = []


@dataclass
class BehavioralAlert:
    """Represents a behavioral threat alert."""
    alert_type: str  # 'anomaly', 'pattern', 'correlation'
    process_name: str
    pid: int
    severity: str
    confidence: float
    timestamp: float
    details: Dict


# ==================== BEHAVIORAL ANALYSIS ====================

class AnomalyScorer:
    """
    Calculates anomaly scores using statistical analysis.
    No ML required - pure stats!
    """
    
    @staticmethod
    def calculate_z_score(value: float, baseline: List[float]) -> float:
        """
        Calculate Z-score for anomaly detection.
        Z = (value - mean) / stdev
        Z > 3 is highly anomalous
        """
        if not baseline or len(baseline) < 2:
            return 0.0
        
        try:
            mean = statistics.mean(baseline)
            stdev = statistics.stdev(baseline)
            
            if stdev == 0:
                return 0.0
            
            z_score = (value - mean) / stdev
            return abs(z_score)
        
        except Exception as e:
            _log.debug(f"Error calculating Z-score: {e}")
            return 0.0
    
    @staticmethod
    def calculate_iqr_anomaly(value: float, baseline: List[float]) -> float:
        """
        Interquartile Range (IQR) method for outlier detection.
        More robust to extreme values than Z-score.
        """
        if not baseline or len(baseline) < 4:
            return 0.0
        
        try:
            sorted_data = sorted(baseline)
            q1 = sorted_data[len(sorted_data) // 4]
            q3 = sorted_data[3 * len(sorted_data) // 4]
            iqr = q3 - q1
            
            if iqr == 0:
                return 0.0
            
            # Outlier if > 1.5 * IQR away from quartiles
            outlier_score = max(
                abs(value - q3) / (1.5 * iqr) if value > q3 else 0,
                abs(q1 - value) / (1.5 * iqr) if value < q1 else 0
            )
            
            return min(outlier_score, 10.0)  # Cap at 10
        
        except Exception as e:
            _log.debug(f"Error calculating IQR: {e}")
            return 0.0
    
    @staticmethod
    def calculate_entropy(data: List) -> float:
        """
        Calculate Shannon entropy of data.
        High entropy = randomness = suspicious for some operations.
        """
        if not data:
            return 0.0
        
        counts = defaultdict(int)
        for item in data:
            counts[item] += 1
        
        entropy = 0.0
        total = len(data)
        
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        
        return entropy


class PatternMatcher:
    """Matches behaviors against known threat patterns."""
    
    @staticmethod
    def match_encryption_pattern(
        file_operations: int,
        file_types_modified: Set[str],
        time_window_seconds: float
    ) -> Tuple[bool, float]:
        """
        Detect encryption behavior pattern:
        - Many files being written
        - Mixed file types
        - Rapid sequence
        """
        score = 0.0
        
        # File operation count
        if file_operations > 50:
            score += min(100, (file_operations / 50) * 20)
        
        # File type diversity (encrypted files hit everything)
        if len(file_types_modified) > 10:
            score += 20
        
        # Speed of operations
        if time_window_seconds > 0 and file_operations / time_window_seconds > 2:
            score += 20
        
        is_pattern = score >= 40
        confidence = min(100, score)
        
        return is_pattern, confidence
    
    @staticmethod
    def match_persistence_pattern(
        registry_modifications: List[str],
        startup_paths: int,
        service_installs: int
    ) -> Tuple[bool, float]:
        """
        Detect persistence mechanism:
        - Registry modification for auto-start
        - Multiple persistence methods
        - Hidden/suspicious paths
        """
        score = 0.0
        
        # Registry persistence
        suspicious_reg_keywords = ['run', 'startup', 'autorun', 'boot', 'init']
        suspicious_regs = sum(1 for reg in registry_modifications
                             if any(kw in reg.lower() for kw in suspicious_reg_keywords))
        
        if suspicious_regs >= 2:
            score += 30
        
        # Service installation
        if service_installs > 0:
            score += 20
        
        # Startup folder modification
        if startup_paths > 0:
            score += 20
        
        is_pattern = score >= 40
        confidence = min(100, score)
        
        return is_pattern, confidence
    
    @staticmethod
    def match_lateral_movement_pattern(
        network_connections: int,
        file_access_attempts: int,
        account_enumeration: bool
    ) -> Tuple[bool, float]:
        """
        Detect lateral movement indicators:
        - Many network connections
        - Remote file access
        - Account/host enumeration
        """
        score = 0.0
        
        # Network activity
        if network_connections > 20:
            score += min(50, (network_connections / 20) * 25)
        
        # File access attempts
        if file_access_attempts > 10:
            score += 20
        
        # Account enumeration
        if account_enumeration:
            score += 30
        
        is_pattern = score >= 40
        confidence = min(100, score)
        
        return is_pattern, confidence
    
    @staticmethod
    def match_data_exfiltration_pattern(
        bytes_sent: int,
        bytes_received: int,
        connection_count: int,
        unique_destinations: int
    ) -> Tuple[bool, float]:
        """
        Detect data exfiltration:
        - High upload ratio
        - Multiple connections
        - Unusual volume
        """
        score = 0.0
        
        # Upload to download ratio
        if bytes_received > 0:
            ratio = bytes_sent / bytes_received
            if ratio > 10:
                score += min(50, (ratio / 10) * 25)
        elif bytes_sent > 10 * 1024 * 1024:  # >10MB upload
            score += 30
        
        # Multiple connections for exfilt
        if connection_count > 50:
            score += 20
        
        # Diverse destinations
        if unique_destinations > 10:
            score += 20
        
        is_pattern = score >= 40
        confidence = min(100, score)
        
        return is_pattern, confidence


# ==================== BEHAVIORAL MONITOR ====================

class BehavioralAnalyzer:
    """
    Advanced behavioral analysis without ML.
    Uses statistical methods and pattern matching.
    """
    
    def __init__(self, on_threat: Optional[callable] = None):
        self.on_threat = on_threat or (lambda x: None)
        self.process_histories: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.baseline_data: Dict[str, List[float]] = defaultdict(list)
        self.running = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        self.learning_period = 300  # 5 minutes
        self.start_time = time.time()
    
    def start(self) -> None:
        """Start behavioral analysis."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        _log.info("Behavioral analysis started")
    
    def stop(self) -> None:
        """Stop behavioral analysis."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _log.info("Behavioral analysis stopped")
    
    def record_process_behavior(self, behavior: ProcessBehavior) -> None:
        """Record a process behavior snapshot."""
        with self.lock:
            self.process_histories[behavior.process_name].append(behavior)
    
    def analyze_process(
        self,
        process_name: str,
        current_behavior: ProcessBehavior
    ) -> Optional[BehavioralAlert]:
        """
        Analyze a process for behavioral anomalies.
        """
        with self.lock:
            history = list(self.process_histories[process_name])
        
        if len(history) < 3:
            return None  # Need baseline
        
        is_in_learning = (time.time() - self.start_time) < self.learning_period
        
        # Calculate baseline from historical data
        file_op_baseline = [b.file_operations for b in history[-100:]]
        registry_op_baseline = [b.registry_operations for b in history[-100:]]
        network_baseline = [b.network_connections for b in history[-100:]]
        
        # Score components
        score = 0.0
        reasoning = []
        
        # 1. Anomaly scoring
        file_z_score = AnomalyScorer.calculate_z_score(
            current_behavior.file_operations,
            file_op_baseline
        )
        
        if file_z_score > 3:  # 3 sigma
            score += 20
            reasoning.append(f"Unusual file operations: Z={file_z_score:.1f}")
        
        # 2. Pattern matching
        is_encryption, enc_conf = PatternMatcher.match_encryption_pattern(
            current_behavior.file_operations,
            set(),  # would need file types
            30  # typical time window
        )
        
        if is_encryption and enc_conf >= 60:
            score += 30
            reasoning.append(f"Encryption-like pattern: {enc_conf:.0f}%")
        
        # 3. API usage anomalies
        if len(current_behavior.suspicious_apis) >= 3:
            score += 20
            reasoning.append(f"Suspicious APIs used: {len(current_behavior.suspicious_apis)}")
        
        # 4. Memory growth
        if current_behavior.memory_growth > 500:  # >500MB
            score += 15
            reasoning.append(f"Large memory growth: {current_behavior.memory_growth}MB")
        
        # 5. CPU usage
        if current_behavior.cpu_usage > 80:
            score += 10
            reasoning.append(f"High CPU usage: {current_behavior.cpu_usage}%")
        
        # Create alert if suspicious
        if score >= 40 and not is_in_learning:
            severity = 'critical' if score >= 70 else 'high' if score >= 50 else 'medium'
            
            return BehavioralAlert(
                alert_type='behavioral_anomaly',
                process_name=process_name,
                pid=current_behavior.pid,
                severity=severity,
                confidence=min(100, score),
                timestamp=current_behavior.timestamp,
                details={
                    'anomaly_score': score,
                    'reasoning': reasoning,
                    'file_operations': current_behavior.file_operations,
                    'suspicious_apis': current_behavior.suspicious_apis[:5],
                }
            )
        
        return None
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop for behavioral analysis."""
        while self.running:
            try:
                import psutil
                
                for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_num']):
                    if not self.running:
                        break
                    
                    try:
                        behavior = ProcessBehavior(
                            process_name=proc.name(),
                            pid=proc.pid,
                            timestamp=time.time(),
                            memory_growth=proc.memory_info().rss / (1024 * 1024),
                        )
                        
                        # Record behavior
                        self.record_process_behavior(behavior)
                        
                        # Analyze if we have history
                        alert = self.analyze_process(behavior.process_name, behavior)
                        if alert:
                            self.on_threat({
                                'type': 'behavioral_anomaly',
                                'process': alert.process_name,
                                'pid': alert.pid,
                                'severity': alert.severity,
                                'confidence': alert.confidence,
                                'reasoning': alert.details['reasoning']
                            })
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                time.sleep(10)
            
            except ImportError:
                _log.warning("psutil not available for behavioral monitoring")
                break
            except Exception as e:
                _log.debug(f"Error in behavioral analysis loop: {e}")
                time.sleep(10)
    
    def get_process_risk_score(self, process_name: str) -> float:
        """Get overall risk score for a process (0-100)."""
        with self.lock:
            history = list(self.process_histories[process_name])
        
        if not history:
            return 0.0
        
        # Average anomaly scores
        scores = [b.anomaly_score for b in history[-50:] if b.anomaly_score > 0]
        
        if scores:
            return sum(scores) / len(scores)
        
        return 0.0
