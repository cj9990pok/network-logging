# GUI Usage Guide

Complete guide for using the Network Logging Monitor graphical interface.

## 🚀 Starting the GUI

### From Source (Python installed)
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run GUI
python network_logging_gui.py
```

### From Executable (.exe / binary)
Simply double-click the executable:
- **Windows:** `NetworkLoggingMonitor.exe`
- **Linux:** `./NetworkLoggingMonitor`
- **macOS:** `NetworkLoggingMonitor.app`

## 📊 Interface Overview

```
┌─────────────────────────────────────────────────────┐
│  🌐 Network Logging Monitor                         │
├─────────────────────────────────────────────────────┤
│  📊 Current Status                                  │
│  ┌─────────────────────────────────────────────┐  │
│  │ Monitoring: ● Running    [▶ Start] [⏹ Stop] │  │
│  │ Last Check: 2025-10-02 14:32:05             │  │
│  │ Gateway:    192.168.1.1 ✓                   │  │
│  │ Internet:   Connected ✓                      │  │
│  └─────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  📈 Quick Statistics                                │
│  ┌─────────────────────────────────────────────┐  │
│  │ Total Checks: 142    Success Rate: 98.5%    │  │
│  │ Session Uptime: 02:15:33   Last: Success    │  │
│  └─────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  📝 Recent Activity                                 │
│  ┌─────────────────────────────────────────────┐  │
│  │ [14:32:05] ✓ Internet connection OK        │  │
│  │ [14:32:05] ✓ Gateway reachable: 192.168.1.1│  │
│  │ [14:31:05] 🔄 Running monitoring check...  │  │
│  │ [14:30:05] ✓ Internet connection OK        │  │
│  └─────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  [🔬 Run Manual Test] [📄 View MTR Logs]          │
│  [📁 Open Logs Folder] [📊 Analyze Logs]          │
│  [🗑️ Clear Activity]                               │
├─────────────────────────────────────────────────────┤
│  ⚙️ Configuration                                   │
│  [📝 Edit config.json] [⏰ Setup Scheduler (Admin)]│
│  [🔍 Discover ISP Hops] [🔌 Probe TCP Hosts]      │
└─────────────────────────────────────────────────────┘
```

## 🎯 Main Features

### 1. Monitoring Control

**Start Monitoring:**
- Click **▶ Start** button
- Runs continuous checks in background
- Updates status every minute (configurable in config.json)
- Shows real-time connectivity status

**Stop Monitoring:**
- Click **⏹ Stop** button
- Stops background checks
- Session statistics are preserved

**Status Indicators:**
- **● Running** (green) = Active monitoring
- **● Stopped** (red) = Not monitoring
- **✓** (green) = Connection OK
- **✗** (red) = Connection failed

### 2. Status Display

**Current Status Section:**
- **Monitoring:** Whether monitoring is active
- **Last Check:** Timestamp of most recent check
- **Gateway:** Local network gateway status (192.168.x.x)
- **Internet:** External connectivity status

**Quick Statistics:**
- **Total Checks:** Number of checks performed this session
- **Success Rate:** Percentage of successful checks (color-coded)
  - Green: ≥95%
  - Orange: 80-94%
  - Red: <80%
- **Session Uptime:** How long monitoring has been running
- **Last Result:** Status of most recent check

### 3. Activity Log

Real-time log of all monitoring activities:
- Connectivity checks
- Gateway status
- Errors and warnings
- Manual test results

**Auto-scrolls** to show latest activity.

**Clear with:** 🗑️ Clear Activity button

### 4. Control Buttons

#### 🔬 Run Manual Test
- Executes a one-time full network diagnostic
- Runs `netLogging.py` in background
- Results appear in activity log
- Useful for testing configuration

#### 📄 View MTR Logs
Opens **Log Viewer Window** (see below)

#### 📁 Open Logs Folder
- Opens `logs/` directory in file explorer
- Quick access to all log files
- Platform-specific (Windows Explorer, Finder, Nautilus)

#### 📊 Analyze Logs
- Runs `analyze_netlog.py`
- Shows statistics from log files
- Results in popup window

#### 🗑️ Clear Activity
Clears the activity log display (doesn't delete log files)

### 5. Configuration Buttons

#### 📝 Edit config.json
- Opens configuration file in default editor
- Edit monitoring targets
- Change check intervals
- Modify timeout settings

**Example config.json:**
```json
{
  "mtr_targets": ["1.1.1.1"],
  "isp_targets": ["88.79.29.66"],
  "check_interval_seconds": 60,
  "ping_timeout_sec": 5
}
```

#### ⏰ Setup Scheduler (Admin)
**Requires Administrator/Root privileges!**

- **Windows:** Launches PowerShell script to setup Task Scheduler
- **Linux:** Opens terminal for cron setup with sudo
- **macOS:** Opens launchd setup with admin prompt

**Interactive setup** asks for monitoring interval:
- 1 minute
- 2 minutes
- 5 minutes
- 10 minutes
- Custom

**What it does:**
- Creates scheduled task/cron job/launchd plist
- Runs monitoring automatically at chosen interval
- Survives reboots (starts on boot)

**Troubleshooting:**
- If UAC/sudo prompt doesn't appear, run GUI as administrator
- Check SCHEDULING.md for manual setup instructions

#### 🔍 Discover ISP Hops
- Runs `discover_isp_hops.py`
- Identifies your ISP's network infrastructure
- Suggests optimal targets for monitoring
- Results in popup window

#### 🔌 Probe TCP Hosts
- Runs `probe_tcp_hosts.py`
- Tests TCP connectivity to configured hosts
- Useful for firewall debugging
- Results in popup window

## 📄 Log Viewer Window

Separate window for viewing and analyzing MTR log files.

### Features:

**File Selection:**
- Dropdown lists all `.log` files in `logs/` folder
- Sorted by date (newest first)
- Auto-loads most recent log

**Search/Filter:**
1. Enter search term (IP address, date, "error", etc.)
2. Click **🔍 Search** or press Enter
3. Matches highlighted in **yellow**
4. Status bar shows match count
5. Auto-scrolls to first match

**Syntax Highlighting:**
- **Blue:** IP addresses (192.168.1.1, 1.1.1.1)
- **Green:** Timestamps (2025-10-02 14:32:05)
- **Red:** Errors ("failed", "100.0% packet loss")
- **Purple Bold:** Separators (======)

**Controls:**
- **🔄 Refresh:** Reload file list
- **Clear:** Remove search highlighting

### Example Use Cases:

**Find all packet loss events:**
```
Search: "packet loss"
```

**Check specific date:**
```
Search: "2025-10-02"
```

**Find ISP hop issues:**
```
Search: "88.79.29.66"
```

**View errors only:**
```
Search: "error|failed"
```

## 💡 Usage Tips

### Best Practices

1. **Start on Boot:**
   - Use "Setup Scheduler" for automatic monitoring
   - Better than keeping GUI open 24/7

2. **Monitor ISP Hops:**
   - Run "Discover ISP Hops" first
   - Add suggested IPs to config.json
   - Helps identify WHERE failures occur

3. **Check Logs Weekly:**
   - Use "Analyze Logs" for summaries
   - Look for patterns (time of day, specific targets)

4. **Keep config.json Simple:**
   - 1-2 targets usually sufficient
   - More targets = more network traffic

5. **Manual Tests During Issues:**
   - When internet acts up, click "Run Manual Test"
   - Captures detailed diagnostics immediately

### Troubleshooting

**GUI won't start:**
- Check Python version: `python --version` (need 3.8+)
- Install Tkinter if missing (usually included)
  - Debian/Ubuntu: `sudo apt install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`

**"Admin" buttons don't work:**
- Run GUI as administrator/root
- Windows: Right-click .exe → "Run as administrator"
- Linux: `sudo python network_logging_gui.py`
- macOS: Enter password when prompted

**Monitoring doesn't detect outages:**
- Check config.json targets are reachable
- Try manual test first
- Increase check frequency (lower interval)

**High CPU usage:**
- Increase `check_interval_seconds` in config
- Reduce number of targets
- Check for stuck background threads

**Logs not appearing:**
- Verify `logs/` folder exists
- Check file permissions
- Look in activity log for errors

## ⌨️ Keyboard Shortcuts

Currently no keyboard shortcuts (future enhancement).

Suggested shortcuts for future versions:
- `Ctrl+S`: Start monitoring
- `Ctrl+T`: Manual test
- `Ctrl+L`: Open log viewer
- `Ctrl+E`: Edit config
- `Ctrl+Q`: Quit

## 🔄 Updates & Maintenance

**Check for Updates:**
- No auto-update (yet)
- Check GitHub for new releases
- Subscribe to repository for notifications

**Update Process:**
1. Download latest release
2. Replace executable/scripts
3. Keep existing config.json and logs/

**Backup Logs:**
```bash
# Before updating
cp -r logs/ logs_backup_$(date +%Y%m%d)/
```

## 📸 Screenshots

(Screenshots would go here in actual docs)

### Main Window
- Status indicators
- Activity log
- Control buttons

### Log Viewer
- Syntax highlighting
- Search results
- File selection

### Scheduler Setup
- Windows Task Scheduler
- Linux cron editor
- macOS launchd

## 🆘 Support

**Documentation:**
- README.md - Project overview
- SCHEDULING.md - Automated setup
- BUILD.md - Compilation guide
- CONTRIBUTING.md - Development guide

**Issues:**
- GitHub Issues: [your-repo]/issues
- Include:
  - Operating system
  - Python version (if from source)
  - Error messages from activity log
  - Steps to reproduce

**Community:**
- GitHub Discussions: [your-repo]/discussions
- Reddit: r/homelab, r/selfhosted

## 🎓 Video Tutorials

(Future: Link to YouTube tutorials)

Planned topics:
- First-time setup walkthrough
- ISP issue documentation workflow
- Advanced configuration
- Building from source

## ⚡ Advanced Features

### Running Headless
For servers without GUI:
```bash
# Use CLI version instead
python netLogging.py
```

### Remote Monitoring
- Run GUI on server via X forwarding (Linux)
- Access logs via file share (SMB/NFS)
- Future: Web interface

### Multiple Instances
Run multiple monitoring sessions:
```bash
# Create separate directories
mkdir monitor1 monitor2
cd monitor1
# Copy files, edit config
python network_logging_gui.py
```

## 🔮 Roadmap

Planned enhancements:
- [ ] Real-time graphs (matplotlib)
- [ ] Desktop notifications
- [ ] Email/webhook alerts
- [ ] Dark mode theme
- [ ] Web dashboard
- [ ] Mobile app companion
- [ ] Historical data export (CSV/JSON)
- [ ] Comparison mode (before/after ISP change)

---

**Enjoy monitoring!** 🌐📊

For more help, see README.md or open an issue on GitHub.
