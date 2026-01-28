#!/usr/bin/env python3
"""
CyberDefense Unified Installer
Creates ONE EXE that handles everything:
- Downloads Python if needed
- Installs dependencies
- Extracts and runs the app
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import urllib.request
import zipfile
import json

def check_python():
    """Check if Python is installed"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        return True
    except:
        return False

def download_python():
    """Download Python 3.11"""
    print("📥 Downloading Python 3.11...")
    url = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    temp_path = os.path.join(tempfile.gettempdir(), "python-installer.exe")
    
    try:
        urllib.request.urlretrieve(url, temp_path)
        print("✅ Python downloaded")
        return temp_path
    except Exception as e:
        print(f"❌ Failed to download Python: {e}")
        return None

def install_python(exe_path):
    """Install Python silently"""
    print("⚙️  Installing Python (this takes 1-2 minutes)...")
    try:
        subprocess.run([exe_path, "/quiet", "InstallAllUsers=1", "PrependPath=1"], 
                      capture_output=True, timeout=300)
        print("✅ Python installed")
        return True
    except Exception as e:
        print(f"❌ Python installation failed: {e}")
        return False

def install_dependencies():
    """Install PyQt5 and other dependencies"""
    print("📦 Installing dependencies (1 minute)...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", 
                       "PyQt5==5.15.9", "requests==2.31.0", "pyperclip==1.8.2"],
                      capture_output=True, timeout=300)
        print("✅ Dependencies installed")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def launch_app():
    """Launch the Cyber Defense application"""
    print("🚀 Launching Cyber Defense...")
    try:
        subprocess.Popen([sys.executable, "app_main.py"], 
                        start_new_session=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        print("✅ Application started!")
        return True
    except Exception as e:
        print(f"❌ Failed to launch app: {e}")
        return False

def main():
    print("=" * 60)
    print("🛡️  CYBER DEFENSE - INSTALLER")
    print("=" * 60)
    print()
    
    # Check Python
    if not check_python():
        print("Python not found, downloading...")
        python_exe = download_python()
        if python_exe:
            install_python(python_exe)
            try:
                os.remove(python_exe)
            except:
                pass
    else:
        print("✅ Python already installed")
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check your internet connection.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print()
    
    # Launch app
    if launch_app():
        print("Window should open in a few seconds...")
        print("Enjoy protected browsing!")
        sys.exit(0)
    else:
        print("Failed to start application")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
