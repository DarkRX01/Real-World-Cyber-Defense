#!/usr/bin/env python3
"""
Test script to verify Cyber Defense application works
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def test_imports():
    """Test if all required modules can be imported"""
    print("[*] Testing imports...")

    try:
        import PyQt5
        print("[OK] PyQt5 imported successfully")
    except ImportError as e:
        print(f"[FAIL] PyQt5 import failed: {e}")
        return False

    try:
        import requests
        print("[OK] requests imported successfully")
    except ImportError as e:
        print(f"[FAIL] requests import failed: {e}")
        return False

    try:
        import psutil
        print("[OK] psutil imported successfully")
    except ImportError as e:
        print(f"[FAIL] psutil import failed: {e}")
        return False

    try:
        import pyperclip
        print("[OK] pyperclip imported successfully")
    except ImportError as e:
        print(f"[FAIL] pyperclip import failed: {e}")
        return False

    return True


def test_files():
    """Test if all required files exist"""
    print("\n[*] Testing files...")

    required_files = [
        "app_main.py",
        "threat_engine.py",
        "background_service.py",
        "requirements.txt",
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"[OK] {file} exists")
        else:
            print(f"[FAIL] {file} missing")
            all_exist = False

    return all_exist


def test_app_launch():
    """Test if the app can launch without errors"""
    print("\n[*] Testing app launch...")

    try:
        from app_main import CyberDefenseApp, main
        print("[OK] App imports successfully")
        print("[OK] Main function accessible")
        return True
    except Exception as e:
        print(f"[FAIL] App launch test failed: {e}")
        return False


def main():
    print("Cyber Defense Application Test")
    print("=" * 40)

    imports_ok = test_imports()
    files_ok = test_files()
    app_ok = test_app_launch()

    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"   Imports: {'[PASS]' if imports_ok else '[FAIL]'}")
    print(f"   Files:   {'[PASS]' if files_ok else '[FAIL]'}")
    print(f"   App:     {'[PASS]' if app_ok else '[FAIL]'}")

    if imports_ok and files_ok and app_ok:
        print("\nAll tests passed! The application should work correctly.")
        print("\nTo run the application:")
        print("   python app_main.py")
        print("\nIf the GUI does not appear:")
        print("   1. Make sure PyQt5 is installed: pip install PyQt5")
        print("   2. Try running as administrator")
        print("   3. Check for any error messages above")
    else:
        print("\nSome tests failed. Please check the errors above.")

    return imports_ok and files_ok and app_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
