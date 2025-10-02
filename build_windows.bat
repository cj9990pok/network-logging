@echo off
REM Build script for Windows .exe using PyInstaller
REM Run this script after installing PyInstaller in your venv

echo ========================================
echo  Network Logging Monitor - Build Script
echo  Building Windows .exe with PyInstaller
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ERROR] PyInstaller not found!
    echo Please install it first: pip install pyinstaller
    pause
    exit /b 1
)

echo [1/4] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [2/4] Building executable...
pyinstaller --clean network_logging_gui.spec

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo [3/4] Copying additional files...
if exist "dist\NetworkLoggingMonitor.exe" (
    copy config.json dist\ >nul 2>&1
    copy README.md dist\ >nul 2>&1
    copy LICENSE dist\ >nul 2>&1
    mkdir dist\logs >nul 2>&1
    mkdir dist\setup_scripts >nul 2>&1
    copy setup_windows_scheduler.ps1 dist\setup_scripts\ >nul 2>&1
    copy start_netlogging.bat dist\setup_scripts\ >nul 2>&1
)

echo [4/4] Build complete!
echo.
echo ========================================
echo  Build successful!
echo  Location: dist\NetworkLoggingMonitor.exe
echo  Size: ~20-40 MB (includes Python runtime)
echo ========================================
echo.
echo You can now distribute the 'dist' folder or just the .exe file.
echo Note: Windows may show SmartScreen warning (unsigned app).
echo.
pause
