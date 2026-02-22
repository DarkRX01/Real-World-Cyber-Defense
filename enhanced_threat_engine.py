#!/usr/bin/env python3
"""
Enhanced Threat Detection Engine - Advanced Capabilities
Adds sophisticated detection for APT malware, zero-days, and advanced threats.
Includes: Domain reputation, PE anomalies, API hooking, shellcode detection, etc.
"""

import hashlib
import re
import struct
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

_log = logging.getLogger("CyberDefense.EnhancedThreatEngine")

# ==================== ADVANCED SIGNATURES ====================

# Known C2/APT command and control domain patterns
APT_DOMAIN_PATTERNS = [
    r"^[a-z0-9]{8,16}\-[a-z0-9]{4,8}\..*",  # Random-looking subdomains
    r"^update[a-z]*\.",  # Fake update domains
    r"^download[a-z]*\.",  # Fake download domains
    r"\.tk$|\.ml$|\.ga$|\.cf$|\.pw$",  # Free registrar abuse
]

# Suspicious Windows API patterns in PE files
SUSPICIOUS_API_IMPORTS = frozenset([
    "WriteProcessMemory", "CreateRemoteThread", "VirtualAllocEx", 
    "GetProcAddress", "LoadLibraryA", "SetWindowsHookEx",
    "WinExec", "ShellExecute", "RegSetValueEx", "RegDeleteKey",
    "GetModuleHandle", "UnmapViewOfFile", "MapViewOfFile",
])

# Known malware domains/IPs
KNOWN_MALWARE_DOMAINS = frozenset([
    "malwarebazaar.abuse.ch", "virustotal.com/api",  # AV test sites
    # Add more known bad domains from feeds
])

# Suspicious registry paths that malware commonly modifies
SUSPICIOUS_REG_PATHS = frozenset([
    r"HKLM\\System\\CurrentControlSet\\Control\\Terminal Server\\WinStations",
    r"HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon",
    r"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    r"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
    r"Software\\Microsoft\\WindowsNT\\CurrentVersion\\Image File Execution Options",
])

# Shellcode signatures (NOP sleds, JMP patterns, etc)
SHELLCODE_PATTERNS = [
    b"\x90" * 8,  # NOP sled (8+ consecutive)
    b"\xcc" * 4,  # INT3 breakpoint chain
    b"\xeb\xfe",  # Infinite loop (JMP -2)
]

# Suspicious file header patterns
SUSPICIOUS_HEADERS = {
    "xor_enc": b"^\x00.\x00.\x00.\x00",  # XOR-encoded PE (rare)
    "double_dos": b"MZ.*MZ",  # Multiple DOS headers
}

# ==================== ADVANCED DETECTION ====================

@dataclass
class AdvancedThreatResult:
    """Enhanced threat result with more detail."""
    is_threat: bool
    threat_type: str  # 'ransomware', 'trojan', 'apt', 'rootkit', 'adware', 'pup', etc
    severity: str  # 'critical', 'high', 'medium', 'low'
    confidence: int  # 0-100
    message: str
    techniques_detected: List[str]  # MITRE ATT&CK techniques
    iocs: Dict[str, List[str]]  # Indicators of Compromise
    remediation: str  # Suggested fix


class PEAnalyzer:
    """Advanced PE file analysis for malware detection."""
    
    @staticmethod
    def analyze_imports(pe_data: bytes) -> Tuple[List[str], bool]:
        """Extract imported APIs and check for suspicious patterns."""
        suspicious_imports = []
        has_abnormal_imports = False
        
        try:
            # Simple PE parser to extract import table
            if not pe_data.startswith(b'MZ'):
                return suspicious_imports, False
            
            pe_offset = struct.unpack('<I', pe_data[0x3C:0x40])[0]
            if pe_offset > len(pe_data) - 200:
                return suspicious_imports, True  # Suspicious PE structure
            
            # Check for suspicious import patterns
            import_section = pe_data[pe_offset:pe_offset+512]
            for api in SUSPICIOUS_API_IMPORTS:
                if api.encode() in import_section:
                    suspicious_imports.append(api)
            
            # Flag if multiple dangerous APIs imported together
            if len(suspicious_imports) >= 3:
                has_abnormal_imports = True
            
        except Exception as e:
            _log.debug(f"Error analyzing PE imports: {e}")
        
        return suspicious_imports, has_abnormal_imports
    
    @staticmethod
    def detect_code_caves(pe_data: bytes) -> Tuple[int, bool]:
        """Detect code caves used for code injection."""
        cave_count = 0
        has_suspicious_caves = False
        
        try:
            # Look for large blocks of NOP, INT3, or padding bytes
            null_blocks = re.findall(b'\x00{32,}', pe_data)
            nop_blocks = re.findall(b'\x90{32,}', pe_data)
            
            cave_count = len(null_blocks) + len(nop_blocks)
            
            # Large code caves in unusual sections is suspicious
            if cave_count > 5:
                has_suspicious_caves = True
                
        except Exception as e:
            _log.debug(f"Error detecting code caves: {e}")
        
        return cave_count, has_suspicious_caves
    
    @staticmethod
    def check_section_entropy(pe_data: bytes) -> Tuple[float, bool]:
        """Check PE sections for encrypted/suspicious content."""
        max_entropy = 0.0
        has_encrypted_section = False
        
        try:
            if not pe_data.startswith(b'MZ'):
                return 0.0, False
            
            pe_offset = struct.unpack('<I', pe_data[0x3C:0x40])[0]
            
            # Parse PE sections (simplified)
            for i in range(10):
                section_offset = pe_offset + 248 + (i * 40)
                if section_offset + 40 > len(pe_data):
                    break
                
                try:
                    section_data = pe_data[section_offset:section_offset+8]
                    if len(section_data) < 8:
                        break
                    
                    # Calculate entropy
                    byte_counts = {}
                    section_size = len(section_data)
                    entropy = 0.0
                    
                    for byte in section_data:
                        byte_counts[byte] = byte_counts.get(byte, 0) + 1
                    
                    for count in byte_counts.values():
                        p = count / section_size
                        entropy -= p * (1 if p == 0 else p.bit_length() - 1)
                    
                    max_entropy = max(max_entropy, entropy)
                except:
                    pass
            
            # Entropy > 7.5 suggests encryption/compression
            if max_entropy > 7.5:
                has_encrypted_section = True
                
        except Exception as e:
            _log.debug(f"Error checking section entropy: {e}")
        
        return max_entropy, has_encrypted_section


class DomainIntelligence:
    """Domain reputation and threat intelligence."""
    
    @staticmethod
    def check_domain_reputation(domain: str) -> Tuple[bool, str]:
        """Check domain against reputation patterns."""
        domain_lower = domain.lower()
        
        # Check against known malware domains
        for bad_domain in KNOWN_MALWARE_DOMAINS:
            if bad_domain in domain_lower:
                return True, f"Known malware domain: {bad_domain}"
        
        # Check APT patterns
        for pattern in APT_DOMAIN_PATTERNS:
            if re.match(pattern, domain_lower):
                return True, f"Suspicious domain pattern: {pattern}"
        
        # Check for homograph attacks (Cyrillic, Greek, etc)
        suspicious_chars = {}
        for char in domain:
            if ord(char) > 127:
                suspicious_chars[char] = ord(char)
        
        if suspicious_chars:
            return True, f"Unicode/homograph attack detected: {suspicious_chars}"
        
        return False, ""
    
    @staticmethod
    def check_certificate_anomalies(domain: str) -> Tuple[bool, List[str]]:
        """Check for certificate-based threats."""
        anomalies = []
        
        try:
            import ssl
            import socket
            
            sock = socket.create_connection((domain, 443), timeout=3)
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                
                # Check for self-signed certs on domains that shouldn't have them
                subject = dict(x[0] for x in cert.get('subject', []))
                issuer = dict(x[0] for x in cert.get('issuer', []))
                
                if subject == issuer:
                    anomalies.append("Self-signed certificate")
                
                # Check certificate validity period
                import datetime
                not_after = datetime.datetime.strptime(
                    cert.get('notAfter', ''), '%b %d %H:%M:%S %Y %Z'
                )
                if (not_after - datetime.datetime.now()).days < 7:
                    anomalies.append("Certificate about to expire")
                    
        except Exception as e:
            _log.debug(f"Error checking certificates: {e}")
        
        return len(anomalies) > 0, anomalies


class FileAnomalsyDetector:
    """Detect file-level anomalies."""
    
    @staticmethod
    def detect_suspicious_signatures(file_data: bytes) -> Tuple[bool, List[str]]:
        """Detect suspicious file signatures and patterns."""
        detections = []
        
        # Check for shellcode patterns
        for pattern in SHELLCODE_PATTERNS:
            if re.search(pattern, file_data):
                detections.append("Shellcode pattern detected")
                break
        
        # Check for code injection markers
        if b"WriteProcessMemory" in file_data or b"CreateRemoteThread" in file_data:
            detections.append("Process injection markers found")
        
        # Check for polymorph/metamorphic indicators
        entropy_samples = []
        for i in range(0, len(file_data), 256):
            chunk = file_data[i:i+256]
            if len(chunk) > 0:
                h = 0.0
                for byte in set(chunk):
                    p = chunk.count(byte) / len(chunk)
                    h -= p * (p.bit_length() if p > 0 else 0)
                entropy_samples.append(h)
        
        if entropy_samples:
            avg_entropy = sum(entropy_samples) / len(entropy_samples)
            if avg_entropy > 7.8:
                detections.append("Polymorphic/packed executable detected")
        
        return len(detections) > 0, detections
    
    @staticmethod
    def analyze_file_metadata(filepath: str) -> Dict[str, str]:
        """Extract and analyze file metadata."""
        metadata = {}
        
        try:
            from pathlib import Path
            p = Path(filepath)
            
            stat = p.stat()
            metadata['size'] = str(stat.st_size)
            metadata['created'] = str(stat.st_ctime)
            metadata['modified'] = str(stat.st_mtime)
            metadata['accessed'] = str(stat.st_atime)
            
            # Suspicious patterns
            if p.suffix.lower() not in ['.exe', '.dll', '.sys']:
                if stat.st_size > 100 * 1024 * 1024:  # >100MB non-exec
                    metadata['anomaly'] = 'Unusually large non-executable'
            
            # Double extension check
            if p.name.count('.') > 1:
                metadata['double_extension_warning'] = True
            
        except Exception as e:
            _log.debug(f"Error analyzing file metadata: {e}")
        
        return metadata


def perform_advanced_threat_analysis(
    filepath: str,
    file_data: Optional[bytes] = None
) -> AdvancedThreatResult:
    """
    Perform comprehensive advanced threat analysis on a file.
    
    Returns AdvancedThreatResult with detailed findings and MITRE ATT&CK mapping.
    """
    techniques = []
    iocs = {}
    threat_indicators = 0
    
    try:
        if file_data is None:
            file_data = Path(filepath).read_bytes()
    except Exception as e:
        return AdvancedThreatResult(
            is_threat=False,
            threat_type="error",
            severity="low",
            confidence=0,
            message=f"Could not read file: {e}",
            techniques_detected=[],
            iocs={},
            remediation=""
        )
    
    # 1. PE Analysis
    if file_data.startswith(b'MZ'):
        suspicious_apis, abnormal_imports = PEAnalyzer.analyze_imports(file_data)
        if suspicious_apis:
            threat_indicators += len(suspicious_apis)
            techniques.append("T1055 - Process Injection")
            iocs['suspicious_apis'] = suspicious_apis
        
        cave_count, has_caves = PEAnalyzer.detect_code_caves(file_data)
        if has_caves:
            threat_indicators += 2
            techniques.append("T1574 - Hijack Execution Flow")
            iocs['code_caves'] = [str(cave_count)]
        
        entropy, encrypted = PEAnalyzer.check_section_entropy(file_data)
        if encrypted:
            threat_indicators += 1
            techniques.append("T1027 - Obfuscated Files or Information")
    
    # 2. Suspicious signature detection
    is_suspicious, detections = FileAnomalsyDetector.detect_suspicious_signatures(file_data)
    if is_suspicious:
        threat_indicators += len(detections)
        techniques.append("T1027.010 - Obfuscated Files or Information: Polymorphic Code")
        iocs['signatures'] = detections
    
    # 3. File metadata analysis
    metadata = FileAnomalsyDetector.analyze_file_metadata(filepath)
    if metadata.get('anomaly'):
        threat_indicators += 1
    
    # Determine threat level
    threat_type = "unknown"
    severity = "low"
    confidence = 0
    
    if threat_indicators >= 5:
        threat_type = "trojan"
        severity = "critical"
        confidence = min(100, 60 + threat_indicators * 5)
    elif threat_indicators >= 3:
        threat_type = "suspicious"
        severity = "high"
        confidence = min(100, 50 + threat_indicators * 5)
    elif threat_indicators >= 1:
        threat_type = "pup"
        severity = "medium"
        confidence = min(100, 40 + threat_indicators * 5)
    
    message = f"Advanced threat analysis: {threat_indicators} indicators found"
    remediation = "Quarantine and analyze in isolated environment; Run YARA scan; Check VirusTotal"
    
    return AdvancedThreatResult(
        is_threat=threat_indicators > 0,
        threat_type=threat_type,
        severity=severity,
        confidence=confidence,
        message=message,
        techniques_detected=techniques,
        iocs=iocs,
        remediation=remediation
    )
