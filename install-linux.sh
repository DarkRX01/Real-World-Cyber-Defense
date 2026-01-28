#!/bin/bash

# Real-World Cyber Defense - Linux Installer
# Installs Python, PyQt5, and sets up the desktop security app

set -e

echo "============================================"
echo "  Cyber Defense - Linux Installer"
echo "============================================"
echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "❌ Unable to detect Linux distribution"
    exit 1
fi

echo "📊 Detected OS: $OS $VER"
echo ""

# Install Python and dependencies
echo "📦 Installing Python and dependencies..."
echo ""

case "$OS" in
    ubuntu|debian)
        sudo apt-get update -qq
        sudo apt-get install -y \
            python3.11 \
            python3-pip \
            python3-dev \
            libpython3-dev \
            xclip \
            python3-pyqt5 \
            build-essential
        ;;
    fedora)
        sudo dnf install -y \
            python3.11 \
            python3-pip \
            python3-devel \
            xclip \
            python3-pyqt5 \
            gcc \
            g++ \
            make
        ;;
    arch)
        sudo pacman -Sy --noconfirm \
            python \
            python-pip \
            xclip \
            python-pyqt5 \
            base-devel
        ;;
    manjaro)
        sudo pacman -Sy --noconfirm \
            python \
            python-pip \
            xclip \
            python-pyqt5 \
            base-devel
        ;;
    *)
        echo "❌ Unsupported distribution: $OS"
        echo "Please install Python 3.9+ and PyQt5 manually"
        exit 1
        ;;
esac

echo "✅ System packages installed"
echo ""

# Install Python packages
echo "📥 Installing Python packages..."
pip3 install --upgrade pip setuptools wheel -q
pip3 install PyQt5 requests pyperclip -q
echo "✅ Python packages installed"
echo ""

# Check for Chrome/Chromium
echo "🌐 Checking for Chrome/Chromium..."
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✅ Chrome found: $CHROME_VERSION"
elif command -v chromium &> /dev/null; then
    CHROMIUM_VERSION=$(chromium --version)
    echo "✅ Chromium found: $CHROMIUM_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROMIUM_VERSION=$(chromium-browser --version)
    echo "✅ Chromium Browser found: $CHROMIUM_VERSION"
else
    echo "⚠️ Chrome/Chromium not found (optional)"
    echo "   Install: sudo apt install chromium-browser (Ubuntu/Debian)"
fi
echo ""

# Create application directory
APP_DIR="$HOME/.cyber-defense"
mkdir -p "$APP_DIR"
echo "✅ Created app directory: $APP_DIR"
echo ""

# Create desktop launcher
LAUNCHER_DIR="$HOME/.local/share/applications"
mkdir -p "$LAUNCHER_DIR"

LAUNCHER_FILE="$LAUNCHER_DIR/cyber-defense.desktop"
cat > "$LAUNCHER_FILE" << 'EOF'
[Desktop Entry]
Type=Application
Name=Cyber Defense
Comment=Real-World Cyber Defense - Desktop Security Tool
Exec=python3 -m cyber_defense.app_main
Icon=shield
Terminal=false
Categories=Security;Utility;
Keywords=security;threat;phishing;tracker;
EOF

chmod +x "$LAUNCHER_FILE"
echo "✅ Created desktop launcher: $LAUNCHER_FILE"
echo ""

# Create helper script in /usr/local/bin (optional with sudo)
echo "🔗 Setting up command-line launcher..."
sudo tee /usr/local/bin/cyber-defense > /dev/null << 'EOF'
#!/bin/bash
python3 -m cyber_defense.app_main "$@"
EOF

sudo chmod +x /usr/local/bin/cyber-defense
echo "✅ Command 'cyber-defense' available"
echo ""

# Setup auto-start (optional)
read -p "🔄 Enable auto-start on boot? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p "$HOME/.config/systemd/user"
    
    SYSTEMD_FILE="$HOME/.config/systemd/user/cyber-defense.service"
    cat > "$SYSTEMD_FILE" << EOF
[Unit]
Description=Real-World Cyber Defense
After=graphical-session.target
Wants=graphical-session-target.service

[Service]
Type=simple
ExecStart=$(which python3) -m cyber_defense.app_main
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical-session.target
EOF

    chmod 644 "$SYSTEMD_FILE"
    systemctl --user daemon-reload
    systemctl --user enable cyber-defense.service
    echo "✅ Auto-start enabled (systemd service installed)"
else
    echo "ℹ️ Auto-start not enabled"
fi
echo ""

# Create installation summary
echo "================================================"
echo "  ✅ INSTALLATION COMPLETE!"
echo "================================================"
echo ""
echo "🚀 To start Cyber Defense:"
echo "   1. Click 'Cyber Defense' in Applications menu"
echo "   2. Or run: cyber-defense"
echo "   3. Or run: python3 -m cyber_defense.app_main"
echo ""
echo "🔧 Features:"
echo "   ✓ Real-time URL scanning"
echo "   ✓ Phishing detection"
echo "   ✓ Tracker blocking"
echo "   ✓ Download protection"
echo "   ✓ Background monitoring (optional)"
echo "   ✓ System tray integration"
echo ""
echo "⚙️ First Launch Tips:"
echo "   - Check Settings to enable/disable features"
echo "   - Customize threat sensitivity level"
echo "   - Enable 'Auto-start on boot' in settings if desired"
echo ""
echo "📖 Documentation:"
echo "   - See README.md for detailed guide"
echo "   - Check GETTING_STARTED.md for setup"
echo "   - View TROUBLESHOOTING.md if issues occur"
echo ""
echo "📝 App Location: $APP_DIR"
echo "💾 Logs Location: $APP_DIR/logs"
echo "⚙️ Settings Location: $APP_DIR/settings.json"
echo ""
echo "================================================"
echo ""
echo "Press Enter to finish..."
read
