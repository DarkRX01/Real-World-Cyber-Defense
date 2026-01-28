#!/usr/bin/env python3
"""
Threat Detection Engine for Real-World Cyber Defense
Provides URL scanning, phishing detection, tracker blocking, and download analysis.
All processing is local; no cloud dependency for core features.
"""

import re
import ipaddress
from urllib.parse import urlparse
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import Enum

# Sensitivity affects how aggressive detection is
class Sensitivity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4


@dataclass
class ThreatResult:
    """Result of a threat scan."""
    is_threat: bool
    threat_type: str  # 'phishing' | 'tracker' | 'malware' | 'suspicious_url' | 'safe'
    severity: str     # 'low' | 'medium' | 'high'
    confidence: int   # 0-100
    message: str
    details: dict = field(default_factory=dict)


# Known tracking domains (25+)
TRACKER_DOMAINS = frozenset([
    "analytics.google.com", "www.google-analytics.com", "google-analytics.com",
    "googletagmanager.com", "www.googletagmanager.com",
    "connect.facebook.net", "www.facebook.com/tr", "facebook.com/tr",
    "pixel.facebook.com", "analytics.twitter.com", "twitter.com/i/ads",
    "doubleclick.net", "www.doubleclick.net", "googleadservices.com",
    "adservice.google.com", "pagead2.googlesyndication.com",
    "static.ads-twitter.com", "t.co", "platform.twitter.com",
    "hotjar.com", "static.hotjar.com", "script.hotjar.com",
    "mixpanel.com", "cdn.mxpnl.com", "amplitude.com", "cdn.amplitude.com",
    "segment.io", "cdn.segment.com", "segment.com",
    "intercom.io", "widget.intercom.io", "fullstory.com", "api.fullstory.com",
    "mouseflow.com", "crazyegg.com", "optimizely.com",
    "clarity.ms", "www.clarity.ms", "linkedin.com/li/track",
    "bat.bing.com", "snap.licdn.com", "px.ads.linkedin.com",
    "tiktok.com/i18n/pixel", "analytics.tiktok.com",
    "reddit.com/static/pixel", "pixel.redditmedia.com",
])

# Suspicious TLDs often used in phishing
SUSPICIOUS_TLDS = frozenset([
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".work", ".click",
    ".link", ".top", ".win", ".loan", ".download", ".racing", ".stream",
    ".gq", ".tk", ".ml", ".ga", ".cf", ".cc", ".buzz", ".rest",
])

# Phishing / social engineering keywords (urgent language)
PHISHING_KEYWORDS = frozenset([
    "verify", "confirm", "account", "suspend", "suspended", "urgent",
    "immediately", "action required", "verify your", "confirm your",
    "update your", "secure your", "validate", "authenticate",
    "paypal", "amazon", "microsoft", "apple", "bank", "login",
    "password", "credentials", "wire transfer", "limited time",
])

# Homograph-style lookalikes (common typosquatting)
LOOKALIKE_PATTERNS = [
    (r"paypa1\.", "paypal"), (r"paypaI\.", "paypal"), (r"paypai\.", "paypal"),
    (r"amaz0n\.", "amazon"), (r"arnazon\.", "amazon"), (r"amazorn\.", "amazon"),
    (r"micr0soft\.", "microsoft"), (r"micros0ft\.", "microsoft"),
    (r"apple\.", "apple"),  # plus idn homographs - we keep it simple with regex
    (r"g00gle\.", "google"), (r"goog1e\.", "google"),
    (r"netf1ix\.", "netflix"), (r"netfl1x\.", "netflix"),
]

# Dangerous file extensions for downloads
DANGEROUS_EXTENSIONS = frozenset([
    ".exe", ".dll", ".scr", ".bat", ".cmd", ".vbs", ".vbe", ".js", ".jse",
    ".ws", ".wsf", ".wsc", ".wsh", ".ps1", ".ps1xml", ".ps2", ".ps2xml",
    ".msi", ".msp", ".com", ".pif", ".jar", ".msc", ".cpl", ".scf",
    ".hta", ".reg", ".inf",
])


def _extract_host(url: str) -> Optional[str]:
    try:
        p = urlparse(url)
        if not p.scheme and "//" not in url:
            url = "https://" + url
            p = urlparse(url)
        return (p.netloc or p.path or "").lower().split(":")[0]
    except Exception:
        return None


def _normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def is_ip_url(url: str) -> bool:
    """Check if URL uses IP address instead of domain."""
    host = _extract_host(url)
    if not host:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def check_tracker(url: str) -> Optional[ThreatResult]:
    """Check if URL is a known tracker. Returns ThreatResult if tracker else None."""
    url = _normalize_url(url)
    host = _extract_host(url)
    if not host:
        return None
    # Strip leading 'www.'
    if host.startswith("www."):
        host = host[4:]
    check = host
    for domain in TRACKER_DOMAINS:
        if domain == check or check.endswith("." + domain):
            return ThreatResult(
                is_threat=True,
                threat_type="tracker",
                severity="low",
                confidence=95,
                message=f"Tracker detected: {domain}",
                details={"domain": domain},
            )
    return None


def get_phishing_confidence(url: str, sensitivity: Sensitivity = Sensitivity.MEDIUM) -> ThreatResult:
    """
    Heuristic phishing check. Returns ThreatResult with confidence 0-100.
    Does NOT call any external API.
    """
    url = _normalize_url(url)
    if not url:
        return ThreatResult(False, "safe", "low", 0, "Empty URL", {})

    host = _extract_host(url)
    score = 0
    details = {}

    # IP-based URL
    if is_ip_url(url):
        score += 40
        details["ip_based"] = True

    # Suspicious TLD
    low = (url or "").lower()
    if host:
        for tld in SUSPICIOUS_TLDS:
            if host.endswith(tld):
                score += 25
                details["suspicious_tld"] = tld
                break

    # Lookalike domains
    for pattern, _ in LOOKALIKE_PATTERNS:
        if re.search(pattern, low):
            score += 50
            details["lookalike"] = pattern
            break

    # Phishing keywords in path/query
    for kw in PHISHING_KEYWORDS:
        if kw in low:
            score += 15
            details["keyword"] = kw
            break

    # Excessive encoding
    if "%" in url and url.count("%") > 5:
        score += 20
        details["encoding"] = True

    # No HTTPS (only if we have scheme)
    try:
        p = urlparse(url)
        if p.scheme == "http":
            score += 30
            details["no_https"] = True
    except Exception:
        pass

    # Cap and scale by sensitivity
    score = min(100, score)
    if sensitivity == Sensitivity.LOW:
        score = int(score * 0.5)
    elif sensitivity == Sensitivity.HIGH:
        score = min(100, int(score * 1.2))
    elif sensitivity == Sensitivity.EXTREME:
        score = min(100, int(score * 1.4))

    is_phishing = score >= 50
    if is_phishing:
        sev = "high" if score >= 75 else "medium"
        return ThreatResult(
            is_threat=True,
            threat_type="phishing",
            severity=sev,
            confidence=score,
            message=f"Possible phishing (confidence {score}%): {url[:80]}...",
            details=details,
        )
    return ThreatResult(
        is_threat=False,
        threat_type="safe",
        severity="low",
        confidence=100 - score,
        message="URL appears safe",
        details=details,
    )


def scan_url(url: str, sensitivity: Sensitivity = Sensitivity.MEDIUM) -> ThreatResult:
    """
    Full URL scan: tracker check first, then phishing heuristics.
    Returns ThreatResult.
    """
    t = check_tracker(url)
    if t:
        return t
    return get_phishing_confidence(url, sensitivity)


def analyze_download(
    filename: str,
    download_url: str = "",
    file_size_bytes: Optional[int] = None,
) -> ThreatResult:
    """
    Analyze a download. Checks extension and optionally URL.
    Returns ThreatResult.
    """
    name = (filename or "").lower().strip()
    ext = ""
    if "." in name:
        ext = "." + name.rsplit(".", 1)[-1]

    if ext in DANGEROUS_EXTENSIONS:
        return ThreatResult(
            is_threat=True,
            threat_type="malware",
            severity="high",
            confidence=85,
            message=f"Dangerous file type: {ext}",
            details={"extension": ext, "filename": filename},
        )

    # Optional: unusually large executable-like name
    if file_size_bytes is not None and file_size_bytes > 300 * 1024 * 1024:
        if any(name.endswith(x) for x in (".exe", ".msi", ".dll")):
            return ThreatResult(
                is_threat=True,
                threat_type="malware",
                severity="medium",
                confidence=60,
                message=f"Unusually large executable: {file_size_bytes // (1024*1024)} MB",
                details={"filename": filename, "size_mb": file_size_bytes / (1024 * 1024)},
            )

    if download_url:
        res = scan_url(download_url)
        if res.is_threat and res.threat_type != "tracker":
            return res

    return ThreatResult(
        is_threat=False,
        threat_type="safe",
        severity="low",
        confidence=90,
        message="Download appears safe",
        details={"filename": filename},
    )


def get_system_security_summary() -> dict:
    """
    Basic system security checks (firewall, etc.).
    Uses psutil and platform where available; avoids suspicious syscalls.
    """
    out = {
        "firewall_active": None,
        "defender_active": None,
        "issues": [],
        "recommendations": [],
    }
    try:
        import platform
        system = platform.system()
        if system != "Windows":
            out["issues"].append("System checks optimized for Windows.")
            return out

        import subprocess
        # Check Windows Firewall profile
        r = subprocess.run(
            ["netsh", "advfirewall", "show", "allprofiles", "state"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and "ON" in (r.stdout or "").upper():
            out["firewall_active"] = True
        else:
            out["firewall_active"] = False
            out["issues"].append("Windows Firewall may be off.")
            out["recommendations"].append("Enable Windows Firewall in Security settings.")

        # Check Windows Defender (WMI / PowerShell would be more reliable; keep it simple)
        r2 = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "Get-MpComputerStatus | Select-Object -ExpandProperty AntivirusEnabled"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r2.returncode == 0 and "true" in (r2.stdout or "").lower():
            out["defender_active"] = True
        else:
            out["defender_active"] = False
            out["recommendations"].append("Ensure Windows Defender real-time protection is on.")
    except Exception as e:
        out["issues"].append(f"Could not run system checks: {e}")
    return out
