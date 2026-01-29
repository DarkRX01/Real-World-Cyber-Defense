#!/usr/bin/env python3
"""
Test if all dependencies are installed and the app can run
"""

import sys
import traceback

print("=" * 70)
print("🔍 Cyber Defense - Dependency Checker")
print("=" * 70)
print()

# Test imports
dependencies = [
    ("PyQt5", "PyQt5"),
    ("PyQt5.QtCore", "PyQt5"),
    ("PyQt5.QtGui", "PyQt5"),
    ("PyQt5.QtWidgets", "PyQt5"),
    ("pyperclip", "pyperclip"),
]

missing = []
print("Checking dependencies...")
for module, package in dependencies:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except ImportError:
        print(f"  ❌ {module} (install with: pip install {package})")
        missing.append(package)

print()

# Check local modules
local_modules = ["threat_engine", "background_service"]
print("Checking local modules...")
for module in local_modules:
    try:
        __import__(module)
        print(f"  ✅ {module}.py")
    except Exception as e:
        print(f"  ❌ {module}.py - Error: {e}")
        missing.append(module)

print()
print("=" * 70)

if missing:
    print("❌ MISSING DEPENDENCIES!")
    print()
    print("Install missing packages with:")
    unique_missing = list(set(p for p in missing if p not in local_modules))
    if unique_missing:
        print(f"  pip install {' '.join(unique_missing)}")
    print()
    sys.exit(1)
else:
    print("✅ ALL DEPENDENCIES PRESENT!")
    print()
    print("Now testing if the app can start...")
    print("-" * 70)
    print()
    
    # Try to import and initialize the app
    try:
        from app_main import setup_logging, load_settings
        
        logger = setup_logging()
        logger.info("Logger initialized successfully")
        
        settings = load_settings()
        print(f"✅ Settings loaded: {settings}")
        
        print()
        print("✅ APP CAN INITIALIZE!")
        print()
        print("The app should work. If the EXE still doesn't run:")
        print("  1. Build a DEBUG version: python build-debug-exe.py")
        print("  2. Run the DEBUG exe and check console output")
        print("  3. Check if antivirus is blocking it")
        print()
        
    except Exception as e:
        print(f"❌ ERROR DURING APP INITIALIZATION:")
        print()
        traceback.print_exc()
        print()
        print("Fix this error before building the EXE!")
        sys.exit(1)
