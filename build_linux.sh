#!/bin/bash
# Build script for Linux binary using PyInstaller

echo "========================================"
echo " Network Logging Monitor - Build Script"
echo " Building Linux binary with PyInstaller"
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

echo "[2/4] Building executable..."
pyinstaller --clean network_logging_gui.spec

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed!"
    exit 1
fi

echo "[3/4] Copying additional files..."
if [ -f "dist/NetworkLoggingMonitor" ]; then
    cp config.json dist/ 2>/dev/null || true
    cp README.md dist/ 2>/dev/null || true
    cp LICENSE dist/ 2>/dev/null || true
    mkdir -p dist/logs
    mkdir -p dist/setup_scripts
    cp setup_linux_cron.sh dist/setup_scripts/ 2>/dev/null || true
    chmod +x dist/NetworkLoggingMonitor
    chmod +x dist/setup_scripts/setup_linux_cron.sh 2>/dev/null || true
fi

echo "[4/4] Creating AppImage (optional)..."
echo "Note: AppImage creation requires additional tools (appimagetool)"
echo "Skipping AppImage for now. Binary is ready at: dist/NetworkLoggingMonitor"

echo ""
echo "========================================"
echo " Build successful!"
echo " Location: dist/NetworkLoggingMonitor"
echo " Size: ~20-40 MB (includes Python runtime)"
echo "========================================"
echo ""
echo "You can now run: ./dist/NetworkLoggingMonitor"
echo "Or distribute the 'dist' folder."
echo ""
