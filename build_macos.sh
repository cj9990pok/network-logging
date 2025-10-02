#!/bin/bash
# Build script for macOS .app bundle using PyInstaller

echo "========================================"
echo " Network Logging Monitor - Build Script"
echo " Building macOS .app with PyInstaller"
echo "========================================"
echo ""

# Check if PyInstaller is installed
python3 -c "import PyInstaller" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERROR] PyInstaller not found!"
    echo "Please install it first: pip install pyinstaller"
    exit 1
fi

echo "[1/4] Cleaning previous builds..."
rm -rf build dist __pycache__

echo "[2/4] Building application..."
pyinstaller --clean network_logging_gui.spec

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

echo "[3/4] Copying additional files to app bundle..."
if [ -d "dist/NetworkLoggingMonitor.app" ]; then
    cp config.json dist/NetworkLoggingMonitor.app/Contents/MacOS/ 2>/dev/null || true
    cp README.md dist/NetworkLoggingMonitor.app/Contents/MacOS/ 2>/dev/null || true
    cp LICENSE dist/NetworkLoggingMonitor.app/Contents/MacOS/ 2>/dev/null || true
    mkdir -p dist/NetworkLoggingMonitor.app/Contents/MacOS/logs
    mkdir -p dist/NetworkLoggingMonitor.app/Contents/MacOS/setup_scripts
    cp setup_macos_launchd.sh dist/NetworkLoggingMonitor.app/Contents/MacOS/setup_scripts/ 2>/dev/null || true
    chmod +x dist/NetworkLoggingMonitor.app/Contents/MacOS/setup_scripts/setup_macos_launchd.sh 2>/dev/null || true
fi

echo "[4/4] Creating DMG (optional)..."
echo "Note: DMG creation requires additional tools (create-dmg or hdiutil)"
echo "Skipping DMG for now. App bundle is ready at: dist/NetworkLoggingMonitor.app"

echo ""
echo "========================================"
echo " Build successful!"
echo " Location: dist/NetworkLoggingMonitor.app"
echo " Size: ~20-40 MB (includes Python runtime)"
echo "========================================"
echo ""
echo "You can now run: open dist/NetworkLoggingMonitor.app"
echo "Or drag it to /Applications folder."
echo ""
echo "Note: macOS may block unsigned apps (Gatekeeper)."
echo "To allow: System Preferences > Security & Privacy > Open Anyway"
echo ""
