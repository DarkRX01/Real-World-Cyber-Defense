#!/usr/bin/env python3
"""
Unified Threat Detection Orchestrator
Coordinates all detection engines and provides multi-layer defense.
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sys

_log = logging.getLogger("CyberDefense.ThreatDetectionOrchestrator")

# Import all detection engines
try:
    from enhanced_threat_engine import perform_advanced_threat_analysis
except ImportError:
    perform_advanced_threat_analysis = None

try:
    from network_monitor import NetworkMonitor, NetworkIntelligence
except ImportError:
    NetworkMonitor = None

try:
    from registry_monitor import WindowsRegistryMonitor
except ImportError:
    WindowsRegistryMonitor = None

try:
    from process_injection_detector import ProcessMonitor, MemoryAnalyzer
except ImportError:
    ProcessMonitor = None

try:
    from rootkit_detector import RootkitDetector
except ImportError:
    RootkitDetector = None

try:
    from advanced_ransomware_detector import AdvancedRansomwareDetector
except ImportError:
    AdvancedRansomwareDetector = None


# ==================== THREAT AGGREGATION ====================

class ThreatDetectionOrchestrator:
    """
    Unified threat detection system combining all detection engines.
    Provides:
    - Multi-layer detection
    - Threat correlation and scoring
    - Real-time threat assessment
    - Advanced threat hunting capabilities
    """
    
    def __init__(self):
        self.threat_log: List[Dict] = []
        self.threat_statistics: Dict = {
            'total_threats': 0,
            'by_type': {},
            'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'last_detected': None,
        }
        self.lock = threading.Lock()
        self.running = False
        self.threat_callbacks = []
        
        # Initialize all detection engines
        self.engines = {}
        self._init_engines()
    
    def _init_engines(self) -> None:
        """Initialize all available detection engines."""
        # File/binary analysis
        self.engines['enhanced_threat_engine'] = perform_advanced_threat_analysis is not None
        
        # Network monitoring
        if NetworkMonitor:
            self.engines['network_monitor'] = NetworkMonitor(on_threat=self._handle_threat)
        else:
            self.engines['network_monitor'] = False
        
        # Registry monitoring (Windows only)
        if WindowsRegistryMonitor and sys.platform == 'win32':
            self.engines['registry_monitor'] = WindowsRegistryMonitor(on_threat=self._handle_threat)
        else:
            self.engines['registry_monitor'] = False
        
        # Process injection detection
        if ProcessMonitor:
            self.engines['process_monitor'] = ProcessMonitor(on_threat=self._handle_threat)
        else:
            self.engines['process_monitor'] = False
        
        # Rootkit detection
        if RootkitDetector:
            self.engines['rootkit_detector'] = RootkitDetector(on_threat=self._handle_threat)
        else:
            self.engines['rootkit_detector'] = False
        
        # Ransomware detection
        if AdvancedRansomwareDetector:
            self.engines['ransomware_detector'] = AdvancedRansomwareDetector(on_threat=self._handle_threat)
        else:
            self.engines['ransomware_detector'] = False
        
        _log.info(f"Threat detection engines initialized: {self._get_active_engines()}")
    
    def _get_active_engines(self) -> List[str]:
        """Get list of active detection engines."""
        active = []
        for name, engine in self.engines.items():
            if engine is True or engine is not False:
                active.append(name)
        return active
    
    def start_all_detection(self) -> None:
        """Start all detection engines."""
        self.running = True
        
        for name, engine in self.engines.items():
            try:
                if hasattr(engine, 'start'):
                    engine.start()
                    _log.info(f"Started detection engine: {name}")
            except Exception as e:
                _log.warning(f"Failed to start {name}: {e}")
    
    def stop_all_detection(self) -> None:
        """Stop all detection engines."""
        self.running = False
        
        for name, engine in self.engines.items():
            try:
                if hasattr(engine, 'stop'):
                    engine.stop()
                    _log.info(f"Stopped detection engine: {name}")
            except Exception as e:
                _log.warning(f"Failed to stop {name}: {e}")
    
    def _handle_threat(self, threat_info: Dict) -> None:
        """Handle detected threat from any engine."""
        with self.lock:
            self.threat_log.append({
                'timestamp': time.time(),
                **threat_info
            })
            
            threat_type = threat_info.get('type', 'unknown')
            severity = threat_info.get('severity', 'unknown')
            
            self.threat_statistics['total_threats'] += 1
            self.threat_statistics['by_type'][threat_type] = \
                self.threat_statistics['by_type'].get(threat_type, 0) + 1
            
            if severity in self.threat_statistics['by_severity']:
                self.threat_statistics['by_severity'][severity] += 1
            
            self.threat_statistics['last_detected'] = time.time()
        
        # Trigger threat callbacks
        for callback in self.threat_callbacks:
            try:
                callback(threat_info)
            except Exception as e:
                _log.debug(f"Error in threat callback: {e}")
    
    def register_threat_callback(self, callback: callable) -> None:
        """Register a callback for threat detection."""
        self.threat_callbacks.append(callback)
    
    def scan_file(self, filepath: str) -> Tuple[bool, Dict]:
        """
        Comprehensive file scanning using all available engines.
        
        Returns: (is_threat, threat_data)
        """
        threat_detected = False
        threat_data = {
            'filepath': filepath,
            'timestamp': time.time(),
            'scans': {},
            'overall_threat': False,
            'overall_severity': 'low',
            'overall_confidence': 0,
        }
        
        # 1. Enhanced threat engine analysis
        if perform_advanced_threat_analysis:
            try:
                result = perform_advanced_threat_analysis(filepath)
                threat_data['scans']['enhanced_analysis'] = {
                    'is_threat': result.is_threat,
                    'threat_type': result.threat_type,
                    'severity': result.severity,
                    'confidence': result.confidence,
                    'techniques': result.techniques_detected,
                    'iocs': result.iocs,
                }
                
                if result.is_threat:
                    threat_detected = True
                    threat_data['overall_confidence'] = max(
                        threat_data['overall_confidence'],
                        result.confidence
                    )
            except Exception as e:
                _log.debug(f"Error in enhanced threat analysis: {e}")
        
        # 2. Memory/process injection analysis
        if ProcessMonitor and hasattr(self.engines.get('process_monitor'), 'detect_suspicious_process_creation'):
            try:
                # Would need process context for this
                pass
            except Exception as e:
                _log.debug(f"Error in process injection scan: {e}")
        
        # Set overall threat flag
        if threat_detected:
            threat_data['overall_threat'] = True
            if threat_data['overall_confidence'] >= 80:
                threat_data['overall_severity'] = 'critical'
            elif threat_data['overall_confidence'] >= 60:
                threat_data['overall_severity'] = 'high'
            elif threat_data['overall_confidence'] >= 40:
                threat_data['overall_severity'] = 'medium'
        
        return threat_detected, threat_data
    
    def get_threat_summary(self) -> Dict:
        """Get comprehensive threat summary."""
        with self.lock:
            return {
                'statistics': self.threat_statistics.copy(),
                'recent_threats': self.threat_log[-100:],  # Last 100 threats
                'threat_count': len(self.threat_log),
                'active_engines': self._get_active_engines(),
            }
    
    def get_system_health(self) -> Dict:
        """
        Comprehensive system health assessment.
        Analyzes all detection engines for threats.
        """
        health = {
            'timestamp': time.time(),
            'overall_risk': 'low',
            'components': {},
        }
        
        # Network threat level
        if self.engines.get('network_monitor'):
            try:
                stats = self.engines['network_monitor'].get_dns_statistics()
                dns_risk = 'high' if stats['suspicious_queries'] > 10 else 'low'
                health['components']['network'] = {
                    'risk': dns_risk,
                    'statistics': stats,
                }
            except Exception:
                pass
        
        # Ransomware threat level
        if self.engines.get('ransomware_detector'):
            try:
                risk, confidence = self.engines['ransomware_detector'].analyze_ransomware_risk()
                health['components']['ransomware'] = {
                    'risk': risk,
                    'confidence': confidence,
                }
            except Exception:
                pass
        
        # Rootkit threat level
        if self.engines.get('rootkit_detector'):
            try:
                risk, confidence = self.engines['rootkit_detector'].get_rootkit_risk_level()
                health['components']['rootkit'] = {
                    'risk': risk,
                    'confidence': confidence,
                }
            except Exception:
                pass
        
        # Determine overall risk
        risks = [comp.get('risk', 'low') for comp in health['components'].values()]
        risk_levels = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        
        if 'critical' in risks:
            health['overall_risk'] = 'critical'
        elif sum(1 for r in risks if r == 'high') >= 2:
            health['overall_risk'] = 'high'
        elif 'high' in risks:
            health['overall_risk'] = 'medium'
        else:
            health['overall_risk'] = 'low'
        
        health['threat_count'] = self.threat_statistics['total_threats']
        health['last_threat'] = self.threat_statistics['last_detected']
        
        return health


# ==================== CONVENIENCE FUNCTIONS ====================

_orchestrator: Optional[ThreatDetectionOrchestrator] = None


def get_orchestrator() -> ThreatDetectionOrchestrator:
    """Get or create the global threat detection orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ThreatDetectionOrchestrator()
    return _orchestrator


def start_threat_detection() -> None:
    """Start all threat detection engines."""
    orchestrator = get_orchestrator()
    orchestrator.start_all_detection()


def stop_threat_detection() -> None:
    """Stop all threat detection engines."""
    orchestrator = get_orchestrator()
    orchestrator.stop_all_detection()


def scan_file_comprehensive(filepath: str) -> Dict:
    """
    Comprehensive file scan using all available detection engines.
    """
    orchestrator = get_orchestrator()
    is_threat, details = orchestrator.scan_file(filepath)
    return details


def get_system_threat_assessment() -> Dict:
    """Get real-time system threat assessment."""
    orchestrator = get_orchestrator()
    return orchestrator.get_system_health()
