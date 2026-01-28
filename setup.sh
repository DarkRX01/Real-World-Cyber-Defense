#!/bin/bash

################################
# Real-World Cyber Defense Extension Setup
# For Linux systems
################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo "========================================"
    echo "Real-World Cyber Defense Installer"
    echo "========================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Start installation
print_header

# Check if Chrome/Chromium is installed
echo "Checking for Chrome/Chromium..."

if command -v google-chrome &> /dev/null; then
    print_success "Google Chrome found!"
    CHROME_PATH=$(command -v google-chrome)
elif command -v chromium &> /dev/null; then
    print_success "Chromium found!"
    CHROME_PATH=$(command -v chromium)
elif command -v chromium-browser &> /dev/null; then
    print_success "Chromium Browser found!"
    CHROME_PATH=$(command -v chromium-browser)
else
    print_error "Chrome/Chromium not found!"
    echo ""
    echo "Please install Google Chrome or Chromium first:"
    echo ""
    echo "For Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install google-chrome-stable"
    echo ""
    echo "For Fedora:"
    echo "  sudo dnf install google-chrome-stable"
    echo ""
    echo "For Arch:"
    echo "  sudo pacman -S chromium"
    echo ""
    exit 1
fi

# Check if unzip is installed
if ! command -v unzip &> /dev/null; then
    print_error "unzip not found!"
    echo "Please install unzip:"
    echo "  Ubuntu/Debian: sudo apt-get install unzip"
    echo "  Fedora: sudo dnf install unzip"
    echo "  Arch: sudo pacman -S unzip"
    exit 1
fi

# Create installation directory
echo ""
echo "Creating installation directory..."

INSTALL_DIR="$HOME/.config/cyber-defense-extension"

if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    print_success "Directory created: $INSTALL_DIR"
else
    print_success "Directory exists: $INSTALL_DIR"
fi

# Find the zip file
echo ""
echo "Looking for extension zip file..."

ZIP_FILE=""

if [ -f "cyber-defense-extension-v1.0.0.zip" ]; then
    ZIP_FILE="$(pwd)/cyber-defense-extension-v1.0.0.zip"
    print_success "Found: $ZIP_FILE"
elif [ -f "$SCRIPT_DIR/cyber-defense-extension-v1.0.0.zip" ]; then
    ZIP_FILE="$SCRIPT_DIR/cyber-defense-extension-v1.0.0.zip"
    print_success "Found: $ZIP_FILE"
else
    print_error "ZIP file not found!"
    echo ""
    echo "Please make sure cyber-defense-extension-v1.0.0.zip is in:"
    echo "  - Current directory"
    echo "  - Same folder as this setup script"
    echo ""
    echo "Download from:"
    echo "  https://github.com/DarkRX01/Real-World-Cyber-Defense/releases"
    echo ""
    exit 1
fi

# Extract the zip file
echo ""
echo "Extracting files..."

if unzip -q -o "$ZIP_FILE" -d "$INSTALL_DIR"; then
    print_success "Files extracted successfully!"
else
    print_error "Extraction failed!"
    echo "Please ensure the ZIP file is valid."
    exit 1
fi

# Make setup script executable if it exists
if [ -f "$INSTALL_DIR/setup.sh" ]; then
    chmod +x "$INSTALL_DIR/setup.sh"
fi

# Create installation guide text file
GUIDE_FILE="$HOME/Desktop/Cyber-Defense-Setup-Instructions.txt"

if [ ! -d "$HOME/Desktop" ]; then
    GUIDE_FILE="$HOME/Cyber-Defense-Setup-Instructions.txt"
fi

cat > "$GUIDE_FILE" << 'GUIDE'

===== CYBER DEFENSE EXTENSION INSTALLATION COMPLETE =====

NEXT STEPS:

1. Open Google Chrome (or Chromium)

2. Type this in the address bar and press Enter:
   chrome://extensions/

3. Turn ON "Developer mode" (toggle at top-right)

4. Click "Load unpacked"

5. Navigate to:
   ~/.config/cyber-defense-extension

6. Click "Select Folder"

7. Done! The extension is now active!

TROUBLESHOOTING:
If you need help, visit:
https://github.com/DarkRX01/Real-World-Cyber-Defense/issues

DOCUMENTATION:
Installation guide: ~/.config/cyber-defense-extension/FIRST-TIME-USERS.md
Troubleshooting: ~/.config/cyber-defense-extension/TROUBLESHOOTING.md

GUIDE

print_success "Instructions saved to: $GUIDE_FILE"

# Display final instructions
clear
echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "The extension has been installed to:"
echo "$INSTALL_DIR"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Open Google Chrome or Chromium"
echo ""
echo "2. Go to: chrome://extensions/"
echo ""
echo "3. Enable 'Developer mode' (top right)"
echo ""
echo "4. Click 'Load unpacked'"
echo ""
echo "5. Select this folder:"
echo "   $INSTALL_DIR"
echo ""
echo "6. Your extension is now active!"
echo ""
echo "QUICK COMMAND:"
echo "You can also open the extension settings page directly:"
echo "$CHROME_PATH chrome://extensions/"
echo ""
echo "For questions, visit:"
echo "https://github.com/DarkRX01/Real-World-Cyber-Defense/issues"
echo ""
echo "========================================"
echo ""
