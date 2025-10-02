#!/bin/bash

# Wrapper script for Network Logging
# Generic paths - adjust SCRIPT_DIR to your installation

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/netLogging.py"
LOG_FILE="$SCRIPT_DIR/logs/cron.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Change to script directory
cd "$SCRIPT_DIR" || {
    echo "$(date): ERROR: Could not change to $SCRIPT_DIR" >> "$LOG_FILE"
    exit 1
}

# Check if virtual environment exists
VENV_PATH="$SCRIPT_DIR/venv"
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "$(date): WARNING: Virtual environment not found. Using system Python." >> "$LOG_FILE"
    PYTHON_CMD="python3"
else
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    PYTHON_CMD="python3"
fi

# Start network logging script
echo "$(date): Starting network logging..." >> "$LOG_FILE"
$PYTHON_CMD "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?
echo "$(date): Network logging finished with exit code $EXIT_CODE" >> "$LOG_FILE"

exit $EXIT_CODE
exit $EXIT_CODE
