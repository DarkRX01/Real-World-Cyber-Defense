"""
Real-World Cyber Defense - Desktop Application
Version: 2.0.0
License: MIT

A powerful, lightweight desktop security tool for Windows and Linux
providing real-time threat detection, phishing prevention, and tracking protection.

Author: DarkRX01
Repository: https://github.com/DarkRX01/Real-World-Cyber-Defense
"""

__version__ = "2.0.0"
__author__ = "DarkRX01"
__license__ = "MIT"

from .app_main import CyberDefenseApp
from .threat_engine import ThreatDetectionEngine
from .background_service import BackgroundService

__all__ = ['CyberDefenseApp', 'ThreatDetectionEngine', 'BackgroundService']
