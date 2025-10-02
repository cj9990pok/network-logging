#!/bin/bash
# Network Logging - macOS launchd Setup Script
# This creates a launchd plist file for automated monitoring

set -e

echo "=== Network Logging - macOS Setup ==="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WRAPPER_SCRIPT="$SCRIPT_DIR/start_netlogging.sh"
CONFIG_FILE="$SCRIPT_DIR/config.json"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$PLIST_DIR/com.networklogging.monitor.plist"

# Check if config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: config.json not found!"
    echo "Please copy config.example.json to config.json and configure it."
    exit 1
fi

# Check if wrapper script exists
if [ ! -f "$WRAPPER_SCRIPT" ]; then
    echo "ERROR: start_netlogging.sh not found!"
    exit 1
fi

# Make wrapper script executable
chmod +x "$WRAPPER_SCRIPT"

echo "Configuration found. Now let's set up launchd..."
echo ""

# Prompt for interval
echo "How often should network monitoring run?"
echo "1) Every 1 minute (recommended)"
echo "2) Every 2 minutes"
echo "3) Every 5 minutes"
echo "4) Every 10 minutes"
echo "5) Custom interval"
read -p "Enter choice (1-5): " choice

case $choice in
    1) interval=60; description="every minute" ;;
    2) interval=120; description="every 2 minutes" ;;
    3) interval=300; description="every 5 minutes" ;;
    4) interval=600; description="every 10 minutes" ;;
    5) 
        read -p "Enter interval in seconds: " interval
        description="every $interval seconds"
        ;;
    *) 
        echo "Invalid choice. Using 60 seconds (1 minute)."
        interval=60
        description="every minute"
        ;;
esac

echo ""
echo "Creating launchd plist for network monitoring ($description)..."

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$PLIST_DIR"

# Create plist file
cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.networklogging.monitor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$WRAPPER_SCRIPT</string>
    </array>
    
    <key>StartInterval</key>
    <integer>$interval</integer>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/launchd.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/launchd_error.log</string>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF

echo "Plist created: $PLIST_FILE"
echo ""

# Load the launchd job
echo "Loading launchd job..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo ""
echo "SUCCESS! launchd configured!"
echo ""
echo "Label: com.networklogging.monitor"
echo "Interval: $description"
echo "Log files:"
echo "  - $SCRIPT_DIR/logs/launchd.log"
echo "  - $SCRIPT_DIR/logs/launchd_error.log"
echo ""
echo "To view status:"
echo "  launchctl list | grep networklogging"
echo ""
echo "To stop monitoring:"
echo "  launchctl unload $PLIST_FILE"
echo ""
echo "To start monitoring:"
echo "  launchctl load $PLIST_FILE"
echo ""
echo "To remove completely:"
echo "  launchctl unload $PLIST_FILE"
echo "  rm $PLIST_FILE"
echo ""
echo "Setup complete! Network monitoring is now active."
