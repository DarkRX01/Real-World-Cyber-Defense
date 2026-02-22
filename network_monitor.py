#!/usr/bin/env python3
"""
Network Traffic Monitoring - Detect C2 connections, DNS tunneling, data exfiltration.
Real-time monitoring of network traffic for malicious patterns.
"""

import socket
import struct
import logging
import threading
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
from pathlib import Path

_log = logging.getLogger("CyberDefense.NetworkMonitor")

# ==================== THREAT INDICATORS ====================

# Known malicious IPs and ranges (from feeds like Shodan, Shadowserver, etc)
KNOWN_MALICIOUS_IPS = frozenset([
    # Add known C2 servers, botnets, ransomware C2
    # This would normally be pulled from threat feeds
])

# Suspicious port patterns
SUSPICIOUS_PORT_COMBINATIONS = {
    (53, 443): "DNS-over-HTTPS tunnel",
    (53, 8080): "DNS exfiltration",
    (25, 53): "Port blending (mail + DNS)",
    (80, 443): "Mixed protocol",
    (4444, 5555): "Backdoor ports",
}

# Known DNS sinkhole IPs
DNS_SINKHOLE_IPS = frozenset([
    "0.0.0.0",
    "127.0.0.1",
    "192.0.2.0",
    "198.51.100.0",
])

# Suspicious TLDs for DNS exfiltration
EXFILTRATION_TLDS = frozenset([
    ".xyz", ".tk", ".ml", ".ga", ".cf",  # Free registrars
    ".dev", ".click", ".link",  # Cheap TLDs often used for C2
])

# DGA (Domain Generation Algorithm) patterns
DGA_PATTERNS = [
    lambda domain: len(domain) > 20 and domain.count(c) == 1 for c in 'aeiou',
    lambda domain: sum(1 for c in domain if c in 'bcdfghjklmnpqrstvwxyz') > 15,
]

# ==================== DATA STRUCTURES ====================

@dataclass
class NetworkConnection:
    """Represents a network connection."""
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    protocol: str  # 'TCP', 'UDP'
    process_name: str
    timestamp: float
    bytes_sent: int = 0
    bytes_received: int = 0
    flags: Set[str] = None  # anomaly flags
    
    def __post_init__(self):
        if self.flags is None:
            self.flags = set()


@dataclass
class DNSQuery:
    """Represents a DNS query."""
    timestamp: float
    domain: str
    query_type: str  # 'A', 'AAAA', 'MX', etc
    response: Optional[str]  # IP or error
    source_ip: str
    process_name: str
    is_suspicious: bool = False


# ==================== NETWORK ANALYZER ====================

class NetworkIntelligence:
    """Threat intelligence for network connections."""
    
    @staticmethod
    def check_ip_reputation(ip: str) -> Tuple[bool, str]:
        """Check IP against threat databases."""
        # Check against known malicious IPs
        if ip in KNOWN_MALICIOUS_IPS:
            return True, f"Known malicious IP: {ip}"
        
        # Check if private IP
        try:
            ip_addr = socket.inet_aton(ip)
            # Check private ranges
            if ip.startswith(('10.', '172.16.', '192.168.')):
                return False, "Private IP"
            if ip.startswith('127.'):
                return False, "Localhost"
        except socket.error:
            return True, "Invalid IP address"
        
        # Check if in sinkhole range
        if ip in DNS_SINKHOLE_IPS:
            return True, "DNS sinkhole IP"
        
        return False, ""
    
    @staticmethod
    def analyze_dns_query(domain: str) -> Tuple[bool, List[str]]:
        """Analyze DNS query for suspicious patterns."""
        alerts = []
        domain_lower = domain.lower()
        
        # Check for unusual length (DGA indicator)
        if len(domain) > 30:
            alerts.append("Unusually long domain name (DGA indicator)")
        
        # Check for randomness
        vowel_count = sum(1 for c in domain_lower if c in 'aeiou')
        if len(domain) > 10 and vowel_count < 2:
            alerts.append("Low vowel count (possible DGA)")
        
        # Check TLD
        tld = domain.split('.')[-1] if '.' in domain else ""
        if f".{tld}".lower() in EXFILTRATION_TLDS:
            alerts.append(f"Suspicious TLD: .{tld}")
        
        # Check for rapid subdomain changes (DNS tunneling)
        if domain.count('.') > 3:
            alerts.append("Multiple subdomains (DNS tunneling indicator)")
        
        # Check for homograph attacks
        suspicious_chars = any(ord(c) > 127 for c in domain)
        if suspicious_chars:
            alerts.append("Unicode characters in domain (homograph attack)")
        
        return len(alerts) > 0, alerts
    
    @staticmethod
    def detect_data_exfiltration(
        bytes_sent: int,
        bytes_received: int,
        duration_seconds: float,
        process_name: str
    ) -> Tuple[bool, str]:
        """Detect potential data exfiltration based on traffic patterns."""
        
        # Suspicious ratio: much more sent than received
        if bytes_sent > 0 and bytes_received > 0:
            ratio = bytes_sent / bytes_received
            if ratio > 10:  # 10:1 ratio
                return True, "High upload-to-download ratio (exfiltration)"
        
        # High throughput from unusual process
        if duration_seconds > 0:
            throughput = (bytes_sent + bytes_received) / duration_seconds
            if throughput > 10 * 1024 * 1024:  # >10 MB/s
                if process_name not in ['svchost.exe', 'explorer.exe', 'chrome.exe']:
                    return True, "Unusually high throughput from suspicious process"
        
        # Consistent data flows outbound (C2 beacon)
        if bytes_sent > 100 * 1024 and bytes_received < 10 * 1024:
            return True, "Consistent outbound traffic pattern (C2 beacon)"
        
        return False, ""
    
    @staticmethod
    def detect_c2_connection(
        dest_port: int,
        conn_frequency: int,
        bytes_per_conn: int,
        domain: str
    ) -> Tuple[bool, List[str]]:
        """Detect C2 communication patterns."""
        indicators = []
        
        # Regular beacon-like connections (every 5-60 seconds)
        if 5 < conn_frequency < 60:
            indicators.append("Regular connection interval (C2 beacon)")
        
        # Small, consistent data transfers (C2 heartbeat)
        if 50 < bytes_per_conn < 1000:
            indicators.append("Small, consistent packet sizes (C2 heartbeat)")
        
        # Suspicious ports
        suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999, 31337]
        if dest_port in suspicious_ports:
            indicators.append(f"Known backdoor port: {dest_port}")
        
        # Check if domain has known C2 characteristics
        if domain:
            if any(keyword in domain.lower() for keyword in ['update', 'check', 'sync']):
                indicators.append("Suspicious domain pattern for C2")
        
        return len(indicators) > 0, indicators
    
    @staticmethod
    def detect_dns_tunneling(dns_queries: List[DNSQuery]) -> Tuple[bool, List[str]]:
        """Detect DNS tunneling/exfiltration."""
        indicators = []
        
        if not dns_queries:
            return False, []
        
        # Check for rapid DNS queries (DNS amplification)
        timestamps = [q.timestamp for q in dns_queries]
        if len(timestamps) > 1:
            time_diff = max(timestamps) - min(timestamps)
            if time_diff > 0 and len(timestamps) / time_diff > 100:
                indicators.append("Rapid DNS queries (amplification attack)")
        
        # Check for high entropy domains
        domains = [q.domain for q in dns_queries]
        entropy_count = sum(1 for d in domains 
                           if len(d) > 20 and sum(1 for c in d.lower() 
                           if c in 'aeiou') < 2)
        if entropy_count > len(domains) * 0.5:
            indicators.append("High-entropy domains (DNS tunneling)")
        
        # Check for unusual query types
        query_types = [q.query_type for q in dns_queries]
        if 'TXT' in query_types or 'CNAME' in query_types:
            indicators.append("Unusual DNS query type for exfiltration")
        
        return len(indicators) > 0, indicators


class ConnectionProfiler:
    """Build and analyze connection profiles to detect anomalies."""
    
    def __init__(self, window_size: int = 3600):
        self.window_size = window_size
        self.connections: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.Lock()
    
    def record_connection(self, conn: NetworkConnection) -> None:
        """Record a connection for analysis."""
        key = f"{conn.dest_ip}:{conn.dest_port}"
        with self.lock:
            self.connections[key].append(conn)
    
    def analyze_patterns(self, process_name: str) -> Dict[str, any]:
        """Analyze connection patterns for a process."""
        analysis = {
            'total_connections': 0,
            'unique_ips': set(),
            'protocols': defaultdict(int),
            'ports_contacted': defaultdict(int),
            'anomalies': []
        }
        
        with self.lock:
            for conns in self.connections.values():
                for conn in conns:
                    if conn.process_name == process_name:
                        analysis['total_connections'] += 1
                        analysis['unique_ips'].add(conn.dest_ip)
                        analysis['protocols'][conn.protocol] += 1
                        analysis['ports_contacted'][conn.dest_port] += 1
        
        # Check for anomalies
        if len(analysis['unique_ips']) > 100:
            analysis['anomalies'].append(f"Contacted {len(analysis['unique_ips'])} unique IPs")
        
        return analysis


class NetworkMonitor:
    """Main network monitoring class."""
    
    def __init__(self, on_threat: Optional[callable] = None):
        self.on_threat = on_threat or (lambda x: None)
        self.profiler = ConnectionProfiler()
        self.dns_queries: deque = deque(maxlen=10000)
        self.lock = threading.Lock()
        self.running = False
        self.monitor_thread = None
    
    def start(self) -> None:
        """Start network monitoring."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        _log.info("Network monitoring started")
    
    def stop(self) -> None:
        """Stop network monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        _log.info("Network monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        # Try to use Scapy for packet capture if available
        try:
            from scapy.all import sniff, IP, ICMP, TCP, UDP, DNS, DNSQR
            
            def packet_callback(packet):
                if not self.running:
                    return
                
                try:
                    if IP in packet:
                        ip_src = packet[IP].src
                        ip_dst = packet[IP].dst
                        
                        # Skip local traffic
                        if ip_src.startswith('127.') or ip_dst.startswith('127.'):
                            return
                        
                        # Analyze DNS
                        if DNSQR in packet:
                            query = packet[DNSQR].qname.decode().rstrip('.')
                            is_suspicious, alerts = NetworkIntelligence.analyze_dns_query(query)
                            
                            if is_suspicious:
                                dns_entry = DNSQuery(
                                    timestamp=time.time(),
                                    domain=query,
                                    query_type='DNS',
                                    response=ip_dst,
                                    source_ip=ip_src,
                                    process_name='unknown',
                                    is_suspicious=True
                                )
                                with self.lock:
                                    self.dns_queries.append(dns_entry)
                                
                                self.on_threat({
                                    'type': 'suspicious_dns',
                                    'domain': query,
                                    'alerts': alerts,
                                    'severity': 'medium'
                                })
                        
                        # Analyze TCP/UDP
                        if TCP in packet or UDP in packet:
                            proto = 'TCP' if TCP in packet else 'UDP'
                            port = packet[TCP].dport if TCP in packet else packet[UDP].dport
                            
                            # Check IP reputation
                            is_bad, reason = NetworkIntelligence.check_ip_reputation(ip_dst)
                            if is_bad:
                                self.on_threat({
                                    'type': 'malicious_connection',
                                    'ip': ip_dst,
                                    'port': port,
                                    'protocol': proto,
                                    'reason': reason,
                                    'severity': 'high'
                                })
                
                except Exception as e:
                    _log.debug(f"Error processing packet: {e}")
            
            # Start packet sniffing (requires admin/root)
            sniff(prn=packet_callback, store=False)
            
        except ImportError:
            _log.warning("Scapy not available for packet monitoring")
            # Fall back to using psutil for connection monitoring
            self._monitor_connections_psutil()
    
    def _monitor_connections_psutil(self) -> None:
        """Monitor connections using psutil (lower-level than Scapy)."""
        try:
            import psutil
            
            seen_connections = set()
            
            while self.running:
                try:
                    for conn in psutil.net_connections(kind='inet'):
                        if conn.status != 'ESTABLISHED':
                            continue
                        
                        conn_key = (conn.laddr.ip, conn.laddr.port, conn.raddr.ip, conn.raddr.port)
                        
                        if conn_key not in seen_connections:
                            seen_connections.add(conn_key)
                            
                            # Check if connection is malicious
                            is_bad, reason = NetworkIntelligence.check_ip_reputation(conn.raddr.ip)
                            if is_bad:
                                self.on_threat({
                                    'type': 'malicious_connection',
                                    'ip': conn.raddr.ip,
                                    'port': conn.raddr.port,
                                    'protocol': 'TCP',
                                    'reason': reason,
                                    'severity': 'high'
                                })
                    
                    time.sleep(5)
                    
                except Exception as e:
                    _log.debug(f"Error monitoring connections: {e}")
                    time.sleep(5)
        
        except ImportError:
            _log.warning("psutil not available for network monitoring")
    
    def get_dns_statistics(self) -> Dict:
        """Get DNS query statistics."""
        with self.lock:
            queries = list(self.dns_queries)
        
        stats = {
            'total_queries': len(queries),
            'unique_domains': len(set(q.domain for q in queries)),
            'suspicious_queries': len([q for q in queries if q.is_suspicious]),
        }
        
        return stats
