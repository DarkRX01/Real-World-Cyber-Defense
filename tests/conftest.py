#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for Cyber Defense tests.
"""

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


@pytest.fixture
def sample_phishing_urls():
    """Sample phishing URLs for testing."""
    return [
        "https://paypa1.com/login",
        "https://amaz0n.com/signin",
        "https://micr0soft.com/account",
        "http://192.168.1.1/login",
        "https://secure-bank.xyz/verify",
    ]


@pytest.fixture
def sample_safe_urls():
    """Sample safe URLs for testing."""
    return [
        "https://www.google.com",
        "https://www.wikipedia.org",
        "https://github.com",
        "https://www.python.org",
        "https://stackoverflow.com",
    ]


@pytest.fixture
def sample_tracker_urls():
    """Sample tracker URLs for testing."""
    return [
        "https://www.google-analytics.com/collect",
        "https://connect.facebook.net/en_US/fbevents.js",
        "https://static.hotjar.com/c/hotjar.js",
        "https://cdn.segment.com/analytics.js",
        "https://bat.bing.com/bat.js",
    ]


@pytest.fixture
def sample_dangerous_files():
    """Sample dangerous file names for testing."""
    return [
        "malware.exe",
        "trojan.dll",
        "script.bat",
        "payload.ps1",
        "virus.scr",
        "backdoor.vbs",
    ]


@pytest.fixture
def sample_safe_files():
    """Sample safe file names for testing."""
    return [
        "document.pdf",
        "report.docx",
        "image.png",
        "photo.jpg",
        "data.csv",
        "readme.txt",
    ]
