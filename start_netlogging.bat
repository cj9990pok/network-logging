@echo off
REM Network Logging - Windows Task Scheduler Wrapper
REM This script activates the virtual environment and runs netLogging.py

REM === CONFIGURE THESE PATHS ===
set "SCRIPT_DIR=C:\Users\YourUser\network-logging"
set "VENV_PATH=%SCRIPT_DIR%\venv"
set "PYTHON_SCRIPT=%SCRIPT_DIR%\netLogging.py"
set "LOG_FILE=%SCRIPT_DIR%\logs\cron.log"
REM =============================

REM Create logs directory if it doesn't exist
if not exist "%SCRIPT_DIR%\logs" mkdir "%SCRIPT_DIR%\logs"

REM Log start time
echo %date% %time%: Starting network logging... >> "%LOG_FILE%"

REM Change to script directory
cd /d "%SCRIPT_DIR%" || (
    echo ERROR: Could not change to %SCRIPT_DIR% >> "%LOG_FILE%"
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at %VENV_PATH% >> "%LOG_FILE%"
    echo Please create it: python -m venv venv >> "%LOG_FILE%"
    exit /b 1
)

REM Activate virtual environment and run script
call "%VENV_PATH%\Scripts\activate.bat"
python "%PYTHON_SCRIPT%" >> "%LOG_FILE%" 2>&1

REM Log completion
echo %date% %time%: Completed network logging run >> "%LOG_FILE%"
