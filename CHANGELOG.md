# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2025-10-02

### Added - Home Assistant Integration Standalone! 🏠
- **Standalone Home Assistant Integration** - Production-ready custom component
  - `custom_components/network_logging/__init__.py` - Complete integration (10KB)
  - `custom_components/network_logging/network_utils.py` - Standalone ping & gateway detection (4.7KB)
  - No external dependencies - uses only built-in Python tools
  - Async/await throughout for optimal performance
  - Cross-platform: Windows, Linux, macOS support
  
- **Binary Sensors**
  - `binary_sensor.network_gateway_reachable` - Router connectivity with latency attribute
  - `binary_sensor.network_internet_connected` - Overall internet status
  - `binary_sensor.network_target_*` - Per-target connectivity (one for each configured target)
  
- **Regular Sensors**
  - `sensor.network_gateway_ip` - Default gateway IP address
  - `sensor.network_average_latency` - Average ping time across all targets (ms)
  - `sensor.network_success_rate` - Connection success percentage (%)
  
- **Services**
  - `network_logging.run_test` - Manual network test with optional target parameter
  - `network_logging.check_gateway` - Check gateway connectivity and log result
  
- **HACS Support**
  - `hacs.json` - HACS metadata for easy installation
  - `info.md` - HACS store display page
  - Ready for HACS submission
  
- **Documentation**
  - `custom_components/network_logging/README.md` - Complete integration documentation (8.4KB)
  - `custom_components/network_logging/INSTALLATION.md` - Detailed installation guide with troubleshooting
  - Automation examples for internet loss, high latency, gateway alerts
  - Lovelace dashboard card examples
  - Troubleshooting section with common issues and solutions
  
### Changed
- **Home Assistant Integration** - Completely rewritten for standalone operation
  - Removed dependency on `netLogging.py` 
  - Implemented native ping and gateway detection in `network_utils.py`
  - Uses subprocess calls to system ping command (cross-platform)
  - Gateway detection via `ip route` (Linux), `netstat` (macOS), `ipconfig` (Windows)
  - Version bumped to 1.0.0 in `manifest.json`
  - manifest.json: `requirements=[]` (no external packages)
  - manifest.json: Added `integration_type: "hub"`
  
- **Main README.md** - Added comprehensive Home Assistant section
  - Installation instructions (HACS + Manual)
  - Quick configuration example
  - Example automation for internet down alerts
  - Link to full HA integration documentation
  
### Fixed
- Home Assistant `async_config_entry_first_refresh()` - Added fallback for newer HA versions
- services.yaml updated with better descriptions and examples
- Removed deprecated `analyze_logs` service (not applicable for standalone)

## [3.1.0] - 2025-10-02

### Added - Graphical User Interface! 🎉
- **Complete Tkinter GUI** (`network_logging_gui.py`)
  - Real-time monitoring dashboard with live status updates
  - Start/Stop monitoring with one click
  - Session statistics (success rate, uptime, check counts)
  - Activity log with real-time event feed
  - Integrated log viewer with syntax highlighting
  - Search and filter functionality in log viewer
  - Manual test execution from GUI
  - Config editor launcher
  - Scheduler setup with admin elevation (Windows UAC, Linux pkexec/sudo, macOS osascript)
  - ISP discovery and TCP probing from GUI
  - Analyze logs with popup results
  - Open logs folder in file explorer
  - **Context menus** - Right-click to copy text from activity log and log viewer
  - **Select All** functionality in context menus
  - **Export selection** to file from log viewer
  
- **Home Assistant Integration** 🏠 (Initial Release - v0.1.0)
  - Custom component in `custom_components/network_logging/`
  - Binary sensors for connectivity (gateway, internet, per-target)
  - Statistics sensors (success rate, latency, packet loss, checks count)
  - Gateway IP sensor
  - Services: `run_test` and `analyze_logs`
  - DataUpdateCoordinator for efficient polling
  - Full automation support
  - Complete HA documentation and examples
  
- **PyInstaller Support**
  - `network_logging_gui.spec` - Build configuration
  - `build_windows.bat` - Windows executable builder
  - `build_linux.sh` - Linux binary builder
  - `build_macos.sh` - macOS app bundle builder
  - Standalone executables (~25-35 MB, no Python required)
  
- **Documentation**
  - `GUI_USAGE.md` - Complete GUI usage guide
  - `BUILD.md` - Compilation instructions for all platforms
  - `GUI_SCREENSHOTS.md` - ASCII art mockups
  - `GUI_INSTALLATION.md` - Tkinter setup guide
  - `VERSION_3.1_SUMMARY.md` - Release summary
  - `custom_components/network_logging/README.md` - Home Assistant docs
  - `custom_components/network_logging/INSTALLATION.md` - HA setup guide
  - Updated README.md with GUI and HA sections
  - Enhanced GITHUB_TAGS.md with GUI-related topics

### Fixed
- **ping() function call** - Corrected to use netLogging.ping() without unsupported arguments
- **tuple/bool handling** - Proper handling of ping() return value (can be bool or tuple)
- **Error handling** - Better error messages in monitoring loop

### Enhanced
- Cross-platform admin rights elevation in GUI
- Syntax highlighting for IPs, timestamps, errors in log viewer
- Threaded operations to prevent GUI freezing
- Auto-scroll in activity log
- Context menu support with clipboard integration
- Platform-specific file/folder opening
- Admin elevation via PowerShell (Windows), pkexec/sudo (Linux), osascript (macOS)

### Technical Details
- GUI runs monitoring in background thread
- No blocking operations in main thread
- Platform-specific file/folder opening
- Admin elevation via PowerShell (Windows), pkexec/sudo (Linux), osascript (macOS)
- Home Assistant DataUpdateCoordinator pattern
- Async/await support for HA integration

## [3.0.0] - 2025-10-01log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-10-02

### 🎉 Major Release - Full Cross-Platform Support

### Added
- **Full Windows support** with automatic detection and fallbacks
- **Full macOS support** with platform-specific commands
- **Cross-platform gateway detection** (Windows: route print, macOS: route -n get, Linux: ip route)
- **Cross-platform ping** with OS-specific parsing (Windows uses -n/-w, Unix uses -c/-W)
- **Cross-platform traceroute** (mtr → tracert/traceroute fallback)
- **Cross-platform diagnostics** (ipconfig/ifconfig/ip addr based on OS)
- **Pathping fallback on Windows** when MTR not available
- **Automated scheduling setup scripts:**
  - `setup_windows_scheduler.ps1` - PowerShell script for Task Scheduler
  - `setup_linux_cron.sh` - Bash script for cron setup
  - `setup_macos_launchd.sh` - Bash script for launchd setup
- **start_netlogging.bat** - Windows batch wrapper script
- **SCHEDULING.md** - Comprehensive scheduling guide for all platforms
- **Platform detection functions** (is_windows(), is_macos(), is_linux())
- **Flexible time scheduling** with interactive prompts (every minute, custom intervals, business hours, etc.)
- Warning messages for missing tools with installation instructions

### Changed
- `ping()` now detects OS and uses appropriate command-line arguments
- `get_gateway_ip()` now works on Windows, macOS, and Linux
- `run_traceroute()` tries MTR first, falls back to tracert (Windows) or traceroute (Unix)
- `collect_wan_diagnostics()` collects OS-appropriate network information
- `run_mtr_intensive()` uses pathping fallback on Windows if MTR unavailable
- README.md updated with cross-platform installation and usage
- All setup instructions now include Windows PowerShell commands

### Removed
- Linux-only assumptions throughout codebase
- Hardcoded "ip route" and Unix-specific commands

## [2.0.0] - 2025-10-02

### 🎉 Major Release - GitHub Ready

### Added
- MIT License
- Comprehensive README.md with full documentation
- config.example.json with detailed explanations
- .gitignore for clean repository
- requirements.txt for dependency management
- Docstrings and type hints throughout codebase
- Configurable timeouts for all network operations
- `dns_test_hostname` configuration option
- `ping_timeout_sec`, `http_timeout_sec`, `tcp_timeout_sec` config options

### Changed
- **BREAKING**: MTR logs now append to single continuous files per target instead of creating new timestamped files
  - Old: `mtr_1.1.1.1_20251001_213702_c60.log` (hundreds of files)
  - New: `mtr_1_1_1_1.log` (one file, timestamped entries)
- All hardcoded timeouts and magic numbers moved to config.json
- Default `isp_targets` reduced to 1 IP to minimize logging overhead
- Default `mtr_targets` reduced to 1 IP
- Improved error handling and fallbacks throughout

### Fixed
- Log file explosion issue (now uses continuous append mode)
- Excessive disk I/O from creating new files every 15 minutes
- Missing configuration options for network timeouts

### Removed
- Hardcoded IP addresses and timeouts from source code

## [1.0.0] - 2025-10-01

### Initial Release

### Added
- Core network monitoring functionality
- Multi-layer connectivity testing (ICMP, TCP, HTTP, DNS)
- ISP hop monitoring with MTR
- Automatic root cause analysis
- CSV logging with detailed metrics
- ISP hop discovery tool
- TCP host probing utility
- Automated outage analysis
- Cron-friendly single-shot execution mode
- Baseline MTR monitoring during normal operation

---

## Migration Guide: 2.0 → 3.0

### No Breaking Changes!
Version 3.0 is fully backward compatible. Existing configurations and logs work as-is.

### New Features to Adopt

1. **Use automated setup scripts** for easier scheduling:
   ```bash
   # Linux
   ./setup_linux_cron.sh
   
   # macOS
   ./setup_macos_launchd.sh
   ```
   
   ```powershell
   # Windows
   .\setup_windows_scheduler.ps1
   ```

2. **Windows users** can now use the project without WSL!

3. **Review SCHEDULING.md** for advanced scheduling options

---

## Migration Guide: 1.0 → 2.0

### Log File Cleanup
The new version uses continuous log files. You can safely remove old timestamped MTR files:

```bash
# Backup old logs (optional)
tar -czf mtr_logs_backup_$(date +%Y%m%d).tar.gz logs/mtr_*_202*.log

# Remove old timestamped files
rm logs/mtr_*_202*.log

# Keep only the new continuous files: mtr_*.log (no date in filename)
```

### Configuration Updates
Add new timeout settings to your `config.json`:

```json
{
  "ping_timeout_sec": 4,
  "http_timeout_sec": 5,
  "tcp_timeout_sec": 5,
  "dns_test_hostname": "example.com"
}
```
