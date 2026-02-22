#!/usr/bin/env python3
"""
CyberDefense Threat Detection Integration Guide
How to integrate the new advanced threat detection modules into your application.
"""

# ==================== EXAMPLE 1: SIMPLE INTEGRATION ====================
"""
For the quickest integration, use the threat detection orchestrator:
"""

from threat_detection_orchestrator import (
    start_threat_detection,
    stop_threat_detection,
    scan_file_comprehensive,
    get_system_threat_assessment,
    get_orchestrator,
)

def example_simple_integration():
    # Start all detection engines (one line!)
    start_threat_detection()
    
    # System is now protected with all threat detection running
    # Just keep your application running
    
    # When done, stop detection
    stop_threat_detection()


# ==================== EXAMPLE 2: CALLBACK-BASED INTEGRATION ====================
"""
Handle threat detection events in real-time
"""

def handle_threat_event(threat_info: dict):
    """Called when a threat is detected."""
    threat_type = threat_info.get('type', 'unknown')
    severity = threat_info.get('severity', 'unknown')
    
    if severity == 'critical':
        # Critical threats: immediate action
        send_alert_to_user(f"CRITICAL THREAT DETECTED: {threat_type}")
        quarantine_threat(threat_info)
    elif severity == 'high':
        # High severity: log and alert
        log_threat(threat_info)
        show_user_warning(threat_type)
    else:
        # Low severity: just log
        log_threat(threat_info)

def example_callback_integration():
    orchestrator = get_orchestrator()
    
    # Register callback for all threats
    orchestrator.register_threat_callback(handle_threat_event)
    
    # Start detection
    start_threat_detection()
    
    # Your application continues running
    # Threats will be reported via the callback


# ==================== EXAMPLE 3: FILE SCANNING ====================
"""
Scan files before allowing them to execute or open
"""

def scan_user_download(filepath: str) -> bool:
    """
    Scan a downloaded file before allowing user interaction.
    Returns True if safe, False if threat detected.
    """
    results = scan_file_comprehensive(filepath)
    
    if results['overall_threat']:
        severity = results['overall_severity']
        confidence = results['overall_confidence']
        
        # Alert user
        show_file_threat_alert(filepath, severity, confidence)
        
        # Quarantine the file
        quarantine_file(filepath)
        
        return False
    
    return True

def example_file_scanning():
    # Example: Download event handler
    downloaded_file = "C:\\Downloads\\document.exe"
    
    is_safe = scan_user_download(downloaded_file)
    if not is_safe:
        print("File is malicious - quarantined!")
    else:
        print("File is safe - executing!")


# ==================== EXAMPLE 4: SYSTEM HEALTH MONITORING ====================
"""
Get real-time system health assessments
"""

def example_health_monitoring():
    import time
    
    while True:
        health = get_system_threat_assessment()
        
        overall_risk = health['overall_risk']
        threat_count = health['threat_count']
        
        print(f"System Risk Level: {overall_risk}")
        print(f"Threats Detected: {threat_count}")
        
        # Show component status
        for component, status in health['components'].items():
            print(f"  {component}: {status['risk']}")
        
        # Update UI in your application
        update_status_display(health)
        
        time.sleep(10)  # Check every 10 seconds


# ==================== EXAMPLE 5: INDIVIDUAL ENGINE USAGE ====================
"""
Use specific detection engines directly
"""

from enhanced_threat_engine import perform_advanced_threat_analysis
from network_monitor import NetworkMonitor, NetworkIntelligence
from registry_monitor import WindowsRegistryMonitor
from process_injection_detector import ProcessMonitor
from rootkit_detector import RootkitDetector
from advanced_ransomware_detector import AdvancedRansomwareDetector
from advanced_behavioral_analysis import BehavioralAnalyzer

def example_individual_engines():
    # Advanced file analysis
    result = perform_advanced_threat_analysis("suspicious_file.exe")
    if result.is_threat:
        print(f"Threat detected: {result.threat_type}")
        print(f"Techniques: {result.techniques_detected}")
    
    # Network monitoring
    network_monitor = NetworkMonitor(on_threat=handle_network_threat)
    network_monitor.start()
    
    # Registry monitoring (Windows only)
    try:
        registry_monitor = WindowsRegistryMonitor(on_threat=handle_registry_change)
        registry_monitor.start()
    except:
        pass
    
    # Process injection detection
    process_monitor = ProcessMonitor(on_threat=handle_injection_detected)
    process_monitor.start()
    
    # Rootkit detection
    rootkit_detector = RootkitDetector(on_threat=handle_rootkit_detected)
    rootkit_detector.start()
    
    # Ransomware detection
    ransomware_detector = AdvancedRansomwareDetector(on_threat=handle_ransomware)
    ransomware_detector.start()
    
    # Behavioral analysis
    behavioral = BehavioralAnalyzer(on_threat=handle_behavior_anomaly)
    behavioral.start()


# ==================== EXAMPLE 6: INTEGRATION WITH EXISTING CODE ====================
"""
How to integrate with your existing threat_engine.py
"""

from threat_engine import scan_file_comprehensive as original_scan
from threat_detection_orchestrator import scan_file_comprehensive as advanced_scan

def scan_file_combined(filepath: str):
    """
    Use both old and new scanning methods.
    Trust the result if either finds a threat.
    """
    # Original scanning
    original_result = original_scan(filepath)
    if original_result.is_threat:
        return original_result
    
    # Advanced scanning (ONLY if original was safe)
    advanced_result = advanced_scan(filepath)
    if advanced_result['overall_threat']:
        # Convert to ThreatResult format for compatibility
        from threat_engine import ThreatResult
        return ThreatResult(
            is_threat=True,
            threat_type=advanced_result['scans']['enhanced_analysis']['threat_type'],
            severity=advanced_result['overall_severity'],
            confidence=advanced_result['overall_confidence'],
            message=f"Advanced analysis detected: {advanced_result}",
            details=advanced_result['scans']
        )
    
    # Safe
    from threat_engine import ThreatResult
    return ThreatResult(
        is_threat=False,
        threat_type='safe',
        severity='low',
        confidence=100,
        message='File is safe',
        details={}
    )


# ==================== EXAMPLE 7: THREAT INTELLIGENCE REPORTING ====================
"""
Report detected threats for threat intelligence
"""

def report_threats_to_feed():
    orchestrator = get_orchestrator()
    
    # Get threat summary
    summary = orchestrator.get_threat_summary()
    
    # Send to threat intelligence service
    threats = summary['recent_threats'][-100:]  # Last 100 threats
    
    for threat in threats:
        # Extract IOCs (Indicators of Compromise)
        iocs = {
            'file_hash': threat.get('file_hash'),
            'domain': threat.get('domain'),
            'ip_address': threat.get('ip_address'),
            'process_name': threat.get('process'),
            'registry_path': threat.get('registry_path'),
        }
        
        # Remove None values
        iocs = {k: v for k, v in iocs.items() if v is not None}
        
        # Send to MISP, AlienVault, etc.
        # submit_to_threat_feed(iocs, threat['type'], threat['severity'])


# ==================== EXAMPLE 8: COMPLIANCE & LOGGING ====================
"""
Log threats for compliance (GDPR, HIPAA, PCI-DSS, etc.)
"""

import json
from datetime import datetime

def log_threat_for_compliance(threat_info: dict):
    """Log threat for audit trail and compliance."""
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'threat_type': threat_info.get('type'),
        'severity': threat_info.get('severity'),
        'confidence': threat_info.get('confidence'),
        'process': threat_info.get('process'),
        'file_path': threat_info.get('file_path'),
        'domain': threat_info.get('domain'),
        'ip_address': threat_info.get('ip_address'),
        'action_taken': threat_info.get('action', 'logged'),
        'mitre_techniques': threat_info.get('techniques', []),
    }
    
    # Log to file for audit trail
    with open('/var/log/cyber-defense-audit.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Also log to syslog for SIEM integration
    import syslog
    syslog.syslog(
        f"CyberDefense: {log_entry['threat_type']} "
        f"({log_entry['severity']}) "
        f"on {log_entry['process']}"
    )


# ==================== EXAMPLE 9: QUARANTINE MANAGEMENT ====================
"""
Manage quarantined files
"""

from pathlib import Path
import shutil

class QuarantineManager:
    def __init__(self, quarantine_dir: str = "~/.cyber-defense/quarantine"):
        self.quarantine_dir = Path(quarantine_dir).expanduser()
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    def quarantine_file(self, filepath: str, threat_info: dict):
        """Move suspicious file to quarantine."""
        try:
            src = Path(filepath)
            # Use hash as quarantine filename to avoid conflicts
            import hashlib
            file_hash = hashlib.sha256(src.read_bytes()).hexdigest()
            dst = self.quarantine_dir / f"{file_hash}_{src.name}"
            
            shutil.move(str(src), str(dst))
            
            # Log quarantine metadata
            metadata = {
                'original_path': filepath,
                'quarantine_date': datetime.now().isoformat(),
                'threat_info': threat_info,
                'file_hash': file_hash,
            }
            
            with open(dst.with_suffix('.json'), 'w') as f:
                json.dump(metadata, f)
            
            return True
        except Exception as e:
            print(f"Error quarantining {filepath}: {e}")
            return False
    
    def restore_file(self, file_hash: str):
        """Restore a quarantined file (after analysis)."""
        quarantine_file = self.quarantine_dir / file_hash
        metadata_file = quarantine_file.with_suffix('.json')
        
        if not quarantine_file.exists():
            return False
        
        try:
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            original_path = metadata['original_path']
            shutil.move(str(quarantine_file), original_path)
            metadata_file.unlink()
            
            return True
        except Exception as e:
            print(f"Error restoring file: {e}")
            return False


# ==================== EXAMPLE 10: CONFIGURATION ====================
"""
Configure detection sensitivity and behavior
"""

class ThreatDetectionConfig:
    # Detection sensitivity (LOW, MEDIUM, HIGH, EXTREME)
    DETECTION_SENSITIVITY = "HIGH"
    
    # Enable/disable specific engines
    ENABLE_FILE_ANALYSIS = True
    ENABLE_NETWORK_MONITOR = True
    ENABLE_REGISTRY_MONITOR = True  # Windows only
    ENABLE_PROCESS_INJECTION = True
    ENABLE_ROOTKIT_DETECTION = True
    ENABLE_RANSOMWARE_DETECTION = True
    ENABLE_BEHAVIORAL_ANALYSIS = True
    
    # Alert thresholds
    FILE_THREAT_THRESHOLD = 60  # confidence 0-100
    NETWORK_THREAT_THRESHOLD = 70
    RANSOMWARE_ALERT_THRESHOLD = 85
    ROOTKIT_ALERT_THRESHOLD = 80
    
    # Logging
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FILE = "~/.cyber-defense/cyber-defense.log"
    LOG_MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    
    # Performance
    MAX_CPU_USAGE = 5  # Percent
    MAX_MEMORY_USAGE = 150 * 1024 * 1024  # 150 MB

---

## Quick Start Integration

### Option 1: Minimal Integration (5 lines)
```python
from threat_detection_orchestrator import start_threat_detection
start_threat_detection()
# That's it! Full protection enabled.
```

### Option 2: With Callbacks (10 lines)
```python
from threat_detection_orchestrator import get_orchestrator

orchestrator = get_orchestrator()
orchestrator.register_threat_callback(my_threat_handler)
orchestrator.start_all_detection()
```

### Option 3: Individual Engines (per-engine control)
```python
from threat_detection_orchestrator import get_orchestrator

orchestrator = get_orchestrator()
# Use specific engines as needed
orchestrator.engines['network_monitor'].start()
orchestrator.engines['ransomware_detector'].start()
```

---

## Integration Checklist

- [ ] Review the new modules
- [ ] Test basic integration
- [ ] Set up threat callbacks
- [ ] Configure sensitivity levels
- [ ] Set up logging/audit trail
- [ ] Create quarantine management
- [ ] Test with sample malware (eiCar)
- [ ] Integrate with existing UI
- [ ] Performance testing
- [ ] Production deployment

---

**Your antivirus just went from basic to ENTERPRISE-GRADE!** 🚀
"""
