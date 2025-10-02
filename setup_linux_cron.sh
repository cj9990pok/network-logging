#!/bin/bash
# Network Logging - Linux cron Setup Script
# This adds a cron job for automated monitoring

set -e

echo "=== Network Logging - Linux Setup ==="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WRAPPER_SCRIPT="$SCRIPT_DIR/start_netlogging.sh"
CONFIG_FILE="$SCRIPT_DIR/config.json"

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

echo "Configuration found. Now let's set up cron..."
echo ""

# Prompt for interval
echo "How often should network monitoring run?"
echo "1) Every 1 minute (recommended)"
echo "2) Every 2 minutes"
echo "3) Every 5 minutes"
echo "4) Every 10 minutes"
echo "5) Every 30 minutes"
echo "6) Every hour"
echo "7) Custom cron expression"
read -p "Enter choice (1-7): " choice

case $choice in
    1) cron_expr="* * * * *"; description="every minute" ;;
    2) cron_expr="*/2 * * * *"; description="every 2 minutes" ;;
    3) cron_expr="*/5 * * * *"; description="every 5 minutes" ;;
    4) cron_expr="*/10 * * * *"; description="every 10 minutes" ;;
    5) cron_expr="*/30 * * * *"; description="every 30 minutes" ;;
    6) cron_expr="0 * * * *"; description="every hour" ;;
    7) 
        echo ""
        echo "Enter custom cron expression (e.g., '*/5 * * * *' for every 5 minutes)"
        echo "Format: minute hour day month weekday"
        read -p "Cron expression: " cron_expr
        description="custom schedule: $cron_expr"
        ;;
    *) 
        echo "Invalid choice. Using every minute."
        cron_expr="* * * * *"
        description="every minute"
        ;;
esac

# Build cron job line
CRON_JOB="$cron_expr $WRAPPER_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"

echo ""
echo "Cron job to be added:"
echo "  $CRON_JOB"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -F "$WRAPPER_SCRIPT" > /dev/null; then
    echo "Existing network logging cron job found. Removing it first..."
    # Remove old job
    crontab -l 2>/dev/null | grep -v "$WRAPPER_SCRIPT" | crontab -
fi

# Add new cron job
echo "Adding cron job..."
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "SUCCESS! Cron job configured!"
echo ""
echo "Schedule: $description"
echo "Log file: $SCRIPT_DIR/logs/cron.log"
echo ""
echo "To view your crontab:"
echo "  crontab -l"
echo ""
echo "To edit your crontab manually:"
echo "  crontab -e"
echo ""
echo "To remove the cron job:"
echo "  crontab -l | grep -v '$WRAPPER_SCRIPT' | crontab -"
echo ""
echo "To view recent log output:"
echo "  tail -f $SCRIPT_DIR/logs/cron.log"
echo ""
echo "Setup complete! Network monitoring will start at the next scheduled time."
