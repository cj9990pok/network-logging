# Automated Scheduling Guide

Complete guide for setting up automated network monitoring on Windows, Linux, and macOS.

> **💡 Best Practice:** This tool is designed for **continuous 24/7 monitoring** and works best on an **always-on device** such as:
> - 🏠 Home server (any OS)
> - 🥧 Raspberry Pi (all models)
> - 💾 NAS (Synology, QNAP, FreeNAS)
> - 🖥️ Dedicated monitoring PC
> - ☁️ Cloud VPS/VM
> 
> **For laptops/desktops:** If your device sleeps or shuts down, monitoring will have gaps. Consider running only during working hours or using an always-on device.

## Table of Contents
- [Windows (Task Scheduler)](#windows-task-scheduler)
- [Linux (cron)](#linux-cron)
- [macOS (launchd)](#macos-launchd)
- [Custom Schedules](#custom-schedules)
- [Troubleshooting](#troubleshooting)

---

## Windows (Task Scheduler)

### Quick Setup (Recommended)

1. **Open PowerShell as Administrator**
   - Press `Win + X`, select "Windows PowerShell (Admin)"

2. **Navigate to project directory:**
   ```powershell
   cd C:\path\to\network-logging
   ```

3. **Run the setup script:**
   ```powershell
   .\setup_windows_scheduler.ps1
   ```

4. **Follow the prompts** to select your monitoring interval

### Manual Setup

If you prefer to configure Task Scheduler manually:

1. **Edit start_netlogging.bat:**
   - Update `SCRIPT_DIR` to your installation path
   - Update `VENV_PATH` if you named your venv differently

2. **Open Task Scheduler:**
   - Press `Win + R`, type `taskschd.msc`, press Enter

3. **Create Basic Task:**
   - Click "Create Basic Task" in right panel
   - Name: `Network Logging`
   - Description: `Automated network connectivity monitoring`

4. **Configure Trigger:**
   - Trigger: `Daily`
   - Start: `Today` at `00:00:00`
   - Recur every: `1 days`
   - Click "Next"

5. **Configure Action:**
   - Action: `Start a program`
   - Program/script: `cmd.exe`
   - Arguments: `/c "C:\path\to\network-logging\start_netlogging.bat"`
   - Click "Next" and "Finish"

6. **Set Repeat Interval:**
   - Right-click the new task, select "Properties"
   - Go to "Triggers" tab, double-click the trigger
   - Check "Repeat task every:" 
   - Select interval (e.g., `1 minute`)
   - Duration: `Indefinitely`
   - Click "OK"

7. **Advanced Settings (Conditions tab):**
   - ✅ Start only if the following network connection is available: `Any connection`
   - ✅ Wake the computer to run this task (optional)
   - ❌ Uncheck "Start the task only if the computer is on AC power"

8. **Start the task:**
   - Right-click task, select "Run"

### Common Time Schedules (Windows)

| Interval | Configuration |
|----------|---------------|
| Every minute | Repeat every: `1 minute`, Duration: `Indefinitely` |
| Every 2 minutes | Repeat every: `2 minutes`, Duration: `Indefinitely` |
| Every 5 minutes | Repeat every: `5 minutes`, Duration: `Indefinitely` |
| Every 10 minutes | Repeat every: `10 minutes`, Duration: `Indefinitely` |
| Every hour at :00 | Trigger: Daily, Start time: `00:00`, Repeat: `1 hour` |
| Only 9 AM - 5 PM | Use two triggers: Start at 9:00, Stop at 17:00 |
| Only weekdays | Advanced: Under "Conditions", use multiple triggers |

---

## Linux (cron)

### Quick Setup (Recommended)

1. **Navigate to project directory:**
   ```bash
   cd /path/to/network-logging
   ```

2. **Run the setup script:**
   ```bash
   ./setup_linux_cron.sh
   ```

3. **Follow the prompts** to select your monitoring interval

### Manual Setup

1. **Edit start_netlogging.sh:**
   ```bash
   nano start_netlogging.sh
   ```
   Update `SCRIPT_DIR` to your installation path

2. **Make script executable:**
   ```bash
   chmod +x start_netlogging.sh
   ```

3. **Edit crontab:**
   ```bash
   crontab -e
   ```

4. **Add cron job** (choose one):
   ```cron
   # Every minute (recommended)
   * * * * * /path/to/network-logging/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
   
   # Every 2 minutes
   */2 * * * * /path/to/network-logging/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
   
   # Every 5 minutes
   */5 * * * * /path/to/network-logging/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
   
   # Every 10 minutes
   */10 * * * * /path/to/network-logging/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
   
   # Every hour
   0 * * * * /path/to/network-logging/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
   ```

5. **Save and exit** (`Ctrl+X`, `Y`, `Enter` in nano)

### Common Time Schedules (Linux cron)

| Interval | Cron Expression | Description |
|----------|----------------|-------------|
| Every minute | `* * * * *` | Run every minute |
| Every 2 minutes | `*/2 * * * *` | Run every 2 minutes |
| Every 5 minutes | `*/5 * * * *` | Run every 5 minutes |
| Every 10 minutes | `*/10 * * * *` | Run every 10 minutes |
| Every 30 minutes | `*/30 * * * *` or `0,30 * * * *` | Run at :00 and :30 |
| Every hour | `0 * * * *` | Run at the start of every hour |
| Every 3 hours | `0 */3 * * *` | Run at 00:00, 03:00, 06:00, etc. |
| 9 AM - 5 PM only | `* 9-17 * * *` | Run every minute from 9 AM to 5 PM |
| Business hours, every 5 min | `*/5 9-17 * * 1-5` | Every 5 min, 9-5, Mon-Fri |
| Daily at 2 AM | `0 2 * * *` | Once per day at 2:00 AM |
| Weekdays only | `* * * * 1-5` | Every minute, Monday-Friday |
| Weekends only | `* * * * 0,6` | Every minute, Saturday-Sunday |

**Cron format:** `minute hour day month weekday`
- `*` = every
- `*/N` = every N units
- `N-M` = range from N to M
- `N,M` = values N and M

### Useful cron commands:

```bash
# View current crontab
crontab -l

# Edit crontab
crontab -e

# Remove all cron jobs (careful!)
crontab -r

# View cron logs (Ubuntu/Debian)
grep CRON /var/log/syslog | tail -20

# View application logs
tail -f /path/to/network-logging/logs/cron.log
```

---

## macOS (launchd)

### Quick Setup (Recommended)

1. **Navigate to project directory:**
   ```bash
   cd /path/to/network-logging
   ```

2. **Run the setup script:**
   ```bash
   ./setup_macos_launchd.sh
   ```

3. **Follow the prompts** to select your monitoring interval

### Manual Setup

1. **Edit start_netlogging.sh:**
   ```bash
   nano start_netlogging.sh
   ```
   Update `SCRIPT_DIR` to your installation path

2. **Make script executable:**
   ```bash
   chmod +x start_netlogging.sh
   ```

3. **Create plist file:**
   ```bash
   nano ~/Library/LaunchAgents/com.networklogging.monitor.plist
   ```

4. **Add configuration** (adjust paths and interval):
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.networklogging.monitor</string>
       
       <key>ProgramArguments</key>
       <array>
           <string>/path/to/network-logging/start_netlogging.sh</string>
       </array>
       
       <key>StartInterval</key>
       <integer>60</integer>  <!-- Seconds between runs -->
       
       <key>RunAtLoad</key>
       <true/>
       
       <key>StandardOutPath</key>
       <string>/path/to/network-logging/logs/launchd.log</string>
       
       <key>StandardErrorPath</key>
       <string>/path/to/network-logging/logs/launchd_error.log</string>
       
       <key>WorkingDirectory</key>
       <string>/path/to/network-logging</string>
   </dict>
   </plist>
   ```

5. **Load the service:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.networklogging.monitor.plist
   ```

### Common Time Schedules (macOS launchd)

| Interval | `StartInterval` Value | Description |
|----------|----------------------|-------------|
| Every minute | `60` | Run every 60 seconds |
| Every 2 minutes | `120` | Run every 120 seconds |
| Every 5 minutes | `300` | Run every 5 minutes |
| Every 10 minutes | `600` | Run every 10 minutes |
| Every 30 minutes | `1800` | Run every 30 minutes |
| Every hour | `3600` | Run every hour |

**Note:** For more complex schedules (like "only weekdays" or "only 9-5"), use `StartCalendarInterval` instead of `StartInterval`. Example:

```xml
<!-- Run every day at 9:00 AM -->
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### Useful launchd commands:

```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.networklogging.monitor.plist

# Unload the service
launchctl unload ~/Library/LaunchAgents/com.networklogging.monitor.plist

# View status
launchctl list | grep networklogging

# Start immediately (for testing)
launchctl start com.networklogging.monitor

# View logs
tail -f ~/path/to/network-logging/logs/launchd.log
```

---

## Custom Schedules

### Run Only During Specific Hours

**Linux (cron) - 8 AM to 6 PM only:**
```cron
# Every 5 minutes between 8 AM and 6 PM
*/5 8-18 * * * /path/to/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
```

**Windows** - Use two triggers:
1. Start trigger at 8:00 AM, repeat every 5 minutes
2. Stop trigger at 6:00 PM

**macOS** - Use `StartCalendarInterval` with multiple entries for each hour

### Run Only on Weekdays

**Linux (cron):**
```cron
# Every minute, Monday-Friday only
* * * * 1-5 /path/to/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
```

**Windows** - In Task Scheduler:
- Triggers tab → Select "Weekly"
- Check Monday through Friday

**macOS** - Use `StartCalendarInterval` with `<key>Weekday</key>`

### Run at Specific Times

**Linux (cron) - Every 2 hours starting at 9 AM:**
```cron
0 9,11,13,15,17 * * * /path/to/start_netlogging.sh >> /path/to/logs/cron.log 2>&1
```

**Windows** - Create multiple triggers with specific times

**macOS** - Use array of `StartCalendarInterval` entries

---

## Troubleshooting

### General Issues

**Monitoring not running:**
1. Check if scheduler service is running
2. Verify wrapper script paths are correct
3. Check permissions on wrapper script
4. Review scheduler logs

**No logs appearing:**
1. Verify `log_dir` in config.json exists and is writable
2. Check wrapper script redirects output correctly
3. Ensure Python script path is correct

**Permission errors:**
1. Linux/macOS: Ensure wrapper script is executable (`chmod +x`)
2. Windows: Run Task Scheduler as Administrator
3. Check file/directory permissions in log directory

### Platform-Specific

**Windows:**
- Task shows "Running" but nothing happens:
  - Check "History" tab in Task Scheduler for errors
  - Verify batch file paths (use full paths, no relative)
  - Run batch file manually to test

**Linux:**
- Cron job not running:
  ```bash
  # Check if cron service is running
  systemctl status cron  # or systemctl status crond
  
  # View cron logs
  grep CRON /var/log/syslog
  ```

**macOS:**
- launchd job not starting:
  ```bash
  # Check for plist errors
  plutil -lint ~/Library/LaunchAgents/com.networklogging.monitor.plist
  
  # View launchd logs
  tail -f ~/Library/Logs/launchd.log
  ```

### Testing Your Setup

**Run manually first:**
```bash
# Linux/macOS
cd /path/to/network-logging
./start_netlogging.sh

# Windows
cd C:\path\to\network-logging
start_netlogging.bat
```

**Check logs:**
```bash
# Linux/macOS
tail -f logs/cron.log

# Windows (PowerShell)
Get-Content logs\cron.log -Tail 20 -Wait
```

**Verify scheduler is configured:**
```bash
# Linux
crontab -l

# macOS
launchctl list | grep networklogging

# Windows (PowerShell)
Get-ScheduledTask -TaskName "NetworkLogging"
```

---

## Examples by Use Case

### Home User - Continuous Monitoring
- **Interval:** Every 1-2 minutes
- **Duration:** 24/7
- **Why:** Catch brief outages, build complete picture

### Remote Worker - Business Hours Only
- **Interval:** Every 1 minute
- **Duration:** 8 AM - 6 PM, weekdays only
- **Why:** Focus on work hours, reduce data

### Server Administrator - Periodic Checks
- **Interval:** Every 5-10 minutes
- **Duration:** 24/7
- **Why:** Balance detail with resource usage

### ISP Complaint Documentation
- **Interval:** Every 30 seconds to 1 minute
- **Duration:** During problem periods
- **Why:** Maximum detail for evidence

---

**Need help?** See [README.md](README.md) or open an issue on GitHub.
