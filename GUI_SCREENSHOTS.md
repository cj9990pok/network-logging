# Network Logging Monitor v3.1 - GUI Demo

## Screenshots (ASCII Preview)

### Main Window - Monitoring Active
```
╔══════════════════════════════════════════════════════════════════════╗
║                   🌐 Network Logging Monitor v3.1                    ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  ┌────────────────── 📊 Current Status ──────────────────────┐     ║
║  │                                                             │     ║
║  │  Monitoring: ● Running      [▶ Start] [⏹ Stop]            │     ║
║  │  Last Check: 2025-10-02 14:32:05                           │     ║
║  │  Gateway:    192.168.1.1 ✓                                 │     ║
║  │  Internet:   Connected ✓ (12ms)                            │     ║
║  │                                                             │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                                                                      ║
║  ┌────────────────── 📈 Quick Statistics ─────────────────────┐     ║
║  │                                                             │     ║
║  │  Total Checks: 142        Success Rate: 98.5% ✓            │     ║
║  │  Session Uptime: 02:15:33      Last Result: Success        │     ║
║  │                                                             │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                                                                      ║
║  ┌─────────────────── 📝 Recent Activity ──────────────────────┐    ║
║  │ [14:32:05] 🔄 Running monitoring check...                   │    ║
║  │ [14:32:05] ✓ Gateway reachable: 192.168.1.1                │    ║
║  │ [14:32:05] ✓ Internet connection OK                         │    ║
║  │ [14:31:05] 🔄 Running monitoring check...                   │    ║
║  │ [14:31:05] ✓ Gateway reachable: 192.168.1.1                │    ║
║  │ [14:31:05] ✓ Internet connection OK                         │    ║
║  │ [14:30:05] 🔄 Running monitoring check...                   │    ║
║  │ [14:30:05] ✓ Gateway reachable: 192.168.1.1                │    ║
║  │ [14:30:05] ✓ Internet connection OK                         │    ║
║  │ [14:29:05] ⚠️ Packet loss detected (3%)                     │    ║
║  └─────────────────────────────────────────────────────────────┘    ║
║                                                                      ║
║  [🔬 Run Manual Test] [📄 View MTR Logs] [📁 Open Logs Folder]     ║
║  [📊 Analyze Logs] [🗑️ Clear Activity]                             ║
║                                                                      ║
║  ┌───────────────────── ⚙️ Configuration ─────────────────────┐     ║
║  │                                                             │     ║
║  │  [📝 Edit config.json]  [⏰ Setup Scheduler (Admin)]        │     ║
║  │  [🔍 Discover ISP Hops] [🔌 Probe TCP Hosts]               │     ║
║  │                                                             │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Log Viewer Window
```
╔══════════════════════════════════════════════════════════════════════╗
║                        📄 MTR Log Viewer                             ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Select Log File: [mtr_1.1.1.1_continuous.log ▼]  [🔄 Refresh]     ║
║                                                                      ║
║  Search/Filter: [packet loss            ]  [🔍 Search] [Clear]      ║
║                                                                      ║
║  ┌─────────────────────── Log Content ──────────────────────────┐   ║
║  │ ==================== MTR Report ====================          │   ║
║  │ Start: 2025-10-02 14:32:05                                    │   ║
║  │ Host: 1.1.1.1                                                 │   ║
║  │                                                               │   ║
║  │ Hop  IP Address        Loss%  Snt  Last  Avg  Best  Wrst     │   ║
║  │  1.  192.168.1.1       0.0%   60   1.2   1.5  1.0   3.2      │   ║
║  │  2.  10.0.0.1          0.0%   60   8.5   9.2  7.8  15.3      │   ║
║  │  3.  88.79.29.66       0.0%   60  12.3  13.1 11.5  18.7      │   ║
║  │  4.  1.1.1.1           3.0%   60  15.8  16.2 14.9  22.1      │   ║
║  │                                                               │   ║
║  │ ==================== MTR Report ====================          │   ║
║  │ Start: 2025-10-02 14:31:05                                    │   ║
║  │ Host: 1.1.1.1                                                 │   ║
║  │                                                               │   ║
║  │ Hop  IP Address        Loss%  Snt  Last  Avg  Best  Wrst     │   ║
║  │  1.  192.168.1.1       0.0%   60   1.3   1.6  1.1   3.5      │   ║
║  │                                                               │   ║
║  └───────────────────────────────────────────────────────────────┘   ║
║                                                                      ║
║  Status: Found 2 matches for "packet loss"                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### Analysis Results Window
```
╔══════════════════════════════════════════════════════════════════════╗
║                     📊 Log Analysis Results                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Analysis Period: 2025-10-01 to 2025-10-02                          ║
║  Total Checks: 2,880 (2 days, every minute)                         ║
║                                                                      ║
║  ┌─────────────────── Overall Statistics ─────────────────────┐     ║
║  │                                                             │     ║
║  │  ✓ Successful Checks:  2,837 (98.5%)                       │     ║
║  │  ✗ Failed Checks:         43 (1.5%)                        │     ║
║  │                                                             │     ║
║  │  Average Latency:      15.3 ms                              │     ║
║  │  Maximum Latency:      87.2 ms                              │     ║
║  │  Packet Loss:           0.8%                                │     ║
║  │                                                             │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                                                                      ║
║  ┌──────────────────── Outage Events ──────────────────────────┐    ║
║  │                                                             │     ║
║  │  Total Outages: 3                                           │     ║
║  │                                                             │     ║
║  │  1. 2025-10-02 03:15:00 - 03:18:00 (3 minutes)             │     ║
║  │     Type: ISP Hop Failure                                   │     ║
║  │     Affected: 88.79.29.66                                   │     ║
║  │                                                             │     ║
║  │  2. 2025-10-01 14:22:00 - 14:25:00 (3 minutes)             │     ║
║  │     Type: Complete Internet Loss                            │     ║
║  │     Gateway: OK, ISP: Down                                  │     ║
║  │                                                             │     ║
║  │  3. 2025-10-01 08:45:00 - 08:46:00 (1 minute)              │     ║
║  │     Type: High Latency (>100ms)                             │     ║
║  │                                                             │     ║
║  └─────────────────────────────────────────────────────────────┘     ║
║                                                                      ║
║  [Export CSV] [View Details] [Close]                                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

## Features Demonstrated

### ✅ Real-Time Monitoring
- Live status updates every second
- Color-coded indicators (green=good, red=bad)
- Session statistics with success rate percentage
- Uptime counter (HH:MM:SS format)

### ✅ User-Friendly Controls
- Large, clear buttons with emoji icons
- One-click start/stop
- Disabled/enabled states prevent accidental clicks
- Activity log auto-scrolls to latest

### ✅ Log Viewer
- Dropdown file selection
- Real-time search with yellow highlighting
- Match counter in status bar
- Syntax highlighting:
  - Blue: IP addresses
  - Green: Timestamps
  - Red: Errors/failures
  - Purple: Separators

### ✅ Integration
- All helper scripts accessible from GUI
- Opens external programs (editor, file explorer)
- Admin elevation for scheduler setup
- Background threading for non-blocking operations

## Technical Highlights

**Threading Model:**
- Main thread: GUI updates (1 second refresh)
- Background thread: Monitoring loop
- Daemon threads: One-off operations (tests, analysis)

**Cross-Platform:**
- Windows: Task Scheduler via PowerShell
- Linux: cron via pkexec/sudo
- macOS: launchd via osascript

**Error Handling:**
- Try/except blocks for all external operations
- User-friendly error messages in activity log
- Graceful degradation (MTR → pathping → traceroute)

## User Experience

**For Beginners:**
1. Double-click NetworkLoggingMonitor.exe
2. Click "▶ Start"
3. Watch status update in real-time
4. Click "📄 View MTR Logs" to see results

**For Advanced Users:**
1. Click "⏰ Setup Scheduler (Admin)"
2. Select interval (1/2/5/10 min)
3. Let it run 24/7
4. Periodically check "📊 Analyze Logs"
5. Present evidence to ISP if issues persist

**For Developers:**
1. Edit config.json via GUI button
2. Run "🔍 Discover ISP Hops" to find targets
3. "🔌 Probe TCP Hosts" for firewall debugging
4. Analyze source code for customization

## Future Enhancements

Planned for v4.0:
- [ ] Real-time graphs (matplotlib integration)
- [ ] Desktop notifications on outages
- [ ] Email/webhook alerts
- [ ] Dark mode theme toggle
- [ ] Minimize to system tray
- [ ] Export reports (PDF/CSV)
- [ ] Historical data comparison
- [ ] Multi-target simultaneous monitoring
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Mobile companion app

## Performance

**Resource Usage:**
- Idle: ~30-50 MB RAM, <1% CPU
- Monitoring: ~50-80 MB RAM, ~2-5% CPU
- Executable Size: ~25-35 MB (includes Python runtime)

**Tested On:**
- Windows 10/11 (x64)
- Ubuntu 20.04/22.04 (x64)
- Debian 11/12 (x64, ARM for Raspberry Pi)
- macOS 12+ (x64, ARM)

**Recommended Hardware:**
- 1 GHz CPU or faster
- 512 MB RAM minimum (1 GB recommended)
- 100 MB disk space
- Network connection (obviously!)

Perfect for Raspberry Pi 3/4/5, old laptops, NAS devices, or any always-on machine! 🎯
