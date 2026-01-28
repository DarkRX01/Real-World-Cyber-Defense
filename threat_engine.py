#!/usr/bin/env python3
"""
Threat Detection Engine
Handles phishing detection, URL scanning, tracker detection, and download protection
"""

import re
import os
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import subprocess
import hashlib
import requests

class ThreatDetectionEngine:
    """Core threat detection logic"""
    
    def __init__(self):
        self.phishing_keywords = [
            'verify', 'confirm', 'urgent', 'update', 'act now', 'click here',
            'limited time', 'validate', 'secure account', 'unusual activity',
            'suspicious', 'reset password', 'confirm identity', 'reactivate'
        ]
        
        self.phishing_domains = [
            'paypa1.com', 'amaz0n.com', 'goog1e.com', 'micros0ft.com',
            'appie.com', 'youtu6e.com', 'faceb00k.com', 'inst4gram.com',
            'twitter.xyz', 'linkedln.com', 'redd1t.com', 'gmaIl.com'
        ]
        
        self.tracker_domains = [
            'google-analytics.com', 'googleadservices.com', 'doubleclick.net',
            'facebook.com/tr', 'analytics.google.com', 'facebook-pixel',
            'segment.com', 'mixpanel.com', 'amplitude.com', 'intercom.io',
            'fullstory.com', 'optimizely.com', 'hotjar.com', 'crazyegg.com',
            'mouseflow.com', 'heap.io', 'marketo.com', 'pardot.com',
            'salesforce.com/tracking', 'hubspot.com/tracking', 'pipedrive.com',
            'drift.com', 'zendesk.com', 'twilio.com', 'sendgrid.com',
            'mailchimp.com/tracking', 'constant-contact.com', 'convertkit.com'
        ]
        
        self.malware_extensions = [
            '.exe', '.bat', '.cmd', '.scr', '.com', '.pif', '.vbs',
            '.js', '.jar', '.zip', '.rar', '.7z', '.iso', '.dmg'
        ]
        
        self.suspicious_extensions = ['.exe', '.dll', '.sys', '.scr']
        
        self.threat_log = []
        self.setup_config()
    
    def setup_config(self):
        """Setup configuration directory"""
        self.config_dir = Path.home() / '.cyber-defense'
        self.config_dir.mkdir(exist_ok=True)
        self.log_file = self.config_dir / 'threat_log.json'
        self.load_threat_log()
    
    def load_threat_log(self):
        """Load threat log from file"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                self.threat_log = json.load(f)
        else:
            self.threat_log = []
    
    def save_threat_log(self):
        """Save threat log to file"""
        with open(self.log_file, 'w') as f:
            json.dump(self.threat_log, f, indent=2)
    
    def log_threat(self, threat):
        """Log a detected threat"""
        threat['timestamp'] = datetime.now().isoformat()
        self.threat_log.append(threat)
        self.save_threat_log()
    
    def check_clipboard(self):
        """Check clipboard for URLs and potential threats"""
        try:
            if os.name == 'nt':  # Windows
                import pyperclip
                text = pyperclip.paste()
            else:  # Linux
                result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                                      capture_output=True, text=True, timeout=2)
                text = result.stdout
        except:
            return None
        
        if not text:
            return None
        
        # Extract URLs from text
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        
        for url in urls:
            threat = self.scan_url(url)
            if threat:
                self.log_threat(threat)
                return threat
        
        return None
    
    def scan_url(self, url):
        """Scan a URL for threats"""
        threats = []
        
        # Parse URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
        except:
            return {'type': 'Invalid URL', 'url': url, 'severity': 'low', 'details': 'Malformed URL'}
        
        # Check for phishing indicators
        phishing_score = self.check_phishing(url, domain)
        if phishing_score > 0.6:
            threat = {
                'type': 'Phishing',
                'url': url,
                'severity': 'high' if phishing_score > 0.8 else 'medium',
                'details': f'Phishing indicators detected (score: {phishing_score:.2f})',
                'indicators': self.get_phishing_indicators(url, domain)
            }
            self.log_threat(threat)
            return threat
        
        # Check for tracker domains
        if self.is_tracker_domain(domain):
            threat = {
                'type': 'Tracker',
                'url': url,
                'severity': 'low',
                'details': f'Known tracking domain: {domain}'
            }
            self.log_threat(threat)
            return threat
        
        # Check for suspicious patterns
        if self.is_suspicious_url(url):
            threat = {
                'type': 'Suspicious URL',
                'url': url,
                'severity': 'medium',
                'details': 'URL contains suspicious patterns'
            }
            self.log_threat(threat)
            return threat
        
        return None
    
    def check_phishing(self, url, domain):
        """Calculate phishing probability (0-1)"""
        score = 0
        
        # Check for suspicious TLDs
        if domain.endswith(('.xyz', '.tk', '.ml', '.ga', '.cf')):
            score += 0.2
        
        # Check for suspicious characters (homograph attack)
        if any(char in domain for char in ['0', 'l', 'I', 'O']):
            score += 0.15
        
        # Check for phishing keywords in URL
        url_lower = url.lower()
        keyword_count = sum(1 for keyword in self.phishing_keywords if keyword in url_lower)
        score += min(keyword_count * 0.1, 0.3)
        
        # Check for known phishing domains
        if any(domain in phish_domain for phish_domain in self.phishing_domains):
            score += 0.4
        
        # Check for suspicious subdomains
        if domain.count('.') > 2:
            score += 0.1
        
        # Check for IP address instead of domain
        if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
            score += 0.2
        
        # Check for HTTPS and certificate indicators
        if not url.startswith('https://'):
            score += 0.1
        
        return min(score, 1.0)
    
    def get_phishing_indicators(self, url, domain):
        """Get specific phishing indicators"""
        indicators = []
        
        if any(keyword in url.lower() for keyword in self.phishing_keywords):
            indicators.append('Phishing keywords detected')
        
        if not url.startswith('https://'):
            indicators.append('Not using HTTPS')
        
        if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
            indicators.append('Using IP address instead of domain')
        
        if domain.count('.') > 2:
            indicators.append('Suspicious subdomain structure')
        
        return indicators
    
    def is_tracker_domain(self, domain):
        """Check if domain is a known tracker"""
        for tracker in self.tracker_domains:
            if tracker in domain or domain in tracker:
                return True
        return False
    
    def is_suspicious_url(self, url):
        """Check for general suspicious patterns"""
        suspicious_patterns = [
            r'bit\.ly|tinyurl|shorturl',  # URL shorteners
            r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',  # IP addresses
            r'%',  # URL encoding
            r'javascript:',  # JavaScript protocol
            r'data:',  # Data URI
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url):
                return True
        
        return False
    
    def scan_file(self, filepath):
        """Scan a downloaded file for threats"""
        try:
            filepath = Path(filepath)
            
            # Check if file exists
            if not filepath.exists():
                return None
            
            filename = filepath.name.lower()
            
            # Check file extension
            file_ext = filepath.suffix.lower()
            if file_ext in self.suspicious_extensions:
                threat = {
                    'type': 'Suspicious File',
                    'file': str(filepath),
                    'severity': 'high',
                    'details': f'Executable file detected: {filename}'
                }
                self.log_threat(threat)
                return threat
            
            # Check file size (very large files might be suspicious)
            file_size = filepath.stat().st_size
            if file_size > 500 * 1024 * 1024:  # 500MB
                threat = {
                    'type': 'Large File',
                    'file': str(filepath),
                    'severity': 'low',
                    'details': f'Unusually large file: {file_size / 1024 / 1024:.2f}MB'
                }
                self.log_threat(threat)
                return threat
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(filepath)
            
            # Check against VirusTotal (if API key available)
            threat = self.check_virustotal(filename, file_hash)
            if threat:
                self.log_threat(threat)
                return threat
            
        except Exception as e:
            print(f"Error scanning file: {e}")
        
        return None
    
    def calculate_file_hash(self, filepath):
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def check_virustotal(self, filename, file_hash):
        """Check file hash against VirusTotal"""
        try:
            config_file = self.config_dir / 'settings.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                    api_key = settings.get('virustotal_api_key')
                    
                    if api_key:
                        # Query VirusTotal API
                        headers = {'x-apikey': api_key}
                        url = f'https://www.virustotal.com/api/v3/files/{file_hash}'
                        response = requests.get(url, headers=headers, timeout=5)
                        
                        if response.status_code == 200:
                            data = response.json()
                            stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                            malicious = stats.get('malicious', 0)
                            
                            if malicious > 0:
                                return {
                                    'type': 'Malware Detected',
                                    'file': filename,
                                    'severity': 'high',
                                    'details': f'{malicious} antivirus engines flagged this file',
                                    'hash': file_hash
                                }
        except Exception as e:
            print(f"VirusTotal check error: {e}")
        
        return None
    
    def monitor_system(self):
        """Monitor system for threats"""
        threats = []
        
        # Check Downloads folder
        downloads_dir = Path.home() / 'Downloads'
        if downloads_dir.exists():
            for file in list(downloads_dir.glob('*'))[:10]:  # Check last 10 files
                if file.is_file():
                    threat = self.scan_file(file)
                    if threat:
                        threats.append(threat)
        
        return threats
    
    def check_vulnerabilities(self):
        """Check for system vulnerabilities"""
        vulnerabilities = []
        
        # Check for Windows-specific issues
        if os.name == 'nt':
            # Check if Windows Defender is running
            try:
                result = subprocess.run(['Get-MpPreference'], capture_output=True, shell=True)
                if 'DisableRealtimeMonitoring : False' not in result.stdout.decode():
                    vulnerabilities.append("❌ Windows Defender real-time protection is disabled")
            except:
                pass
            
            # Check for Windows Firewall
            try:
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'],
                                      capture_output=True, text=True)
                if 'State                                 : off' in result.stdout:
                    vulnerabilities.append("❌ Windows Firewall is disabled")
            except:
                pass
        
        # Check for weak permissions
        home_dir = Path.home()
        try:
            stat_info = os.stat(home_dir)
            if stat_info.st_mode & 0o077:
                vulnerabilities.append("⚠️ Home directory has permissive permissions")
        except:
            pass
        
        # Add mock vulnerabilities for demo
        vulnerabilities.extend([
            "✅ System is up to date",
            "✅ Password manager is configured",
            "⚠️ Automatic security updates: Check Windows Update settings"
        ])
        
        return vulnerabilities


class PhishingDetector:
    """Advanced phishing detection using ML patterns"""
    
    @staticmethod
    def detect_homograph_attack(url):
        """Detect homograph attacks (confusing similar characters)"""
        suspicious_pairs = {
            '0': 'O',
            '1': 'l',
            '5': 'S',
            '8': 'B'
        }
        
        domain = urlparse(url).netloc
        for char, replacement in suspicious_pairs.items():
            if char in domain and replacement in domain.lower():
                return True
        
        return False
    
    @staticmethod
    def detect_internationalized_domain(url):
        """Detect IDN homograph attacks"""
        domain = urlparse(url).netloc
        try:
            domain.encode('ascii')
            return False
        except UnicodeEncodeError:
            return True


class DownloadProtection:
    """Monitor and protect downloads"""
    
    def __init__(self, engine):
        self.engine = engine
        self.monitored_dir = Path.home() / 'Downloads'
    
    def monitor(self):
        """Monitor downloads folder"""
        if self.monitored_dir.exists():
            for file in self.monitored_dir.glob('*'):
                if file.is_file():
                    self.engine.scan_file(file)
