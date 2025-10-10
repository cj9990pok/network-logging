# Network Logging & ISP Outage Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)](https://github.com/connyTheOne/network-logging)

A comprehensive **cross-platform** network monitoring tool that continuously tracks internet connectivity, diagnoses outages, and identifies whether problems originate from your local network, ISP, or external services. Works on **Windows, Linux, and macOS**. Perfect for documenting ISP reliability issues with detailed evidence.

> **💡 Best Practice:** This tool is designed for **continuous monitoring** and works best on an **always-on device** like a home server, Raspberry Pi, NAS, or dedicated monitoring PC. For laptops/desktops that sleep or shut down, monitoring gaps will occur.

## 🎯 Key Features

- **🖥️ Graphical User Interface**: Easy-to-use GUI with real-time monitoring dashboard (NEW in v3.1!)
- **🏠 Home Assistant Integration**: Full integration as custom component with sensors and automations (NEW in v3.1!)
- **📊 Live Status Display**: Monitor gateway, internet, and statistics in real-time
- **🔘 One-Click Controls**: Start/Stop monitoring, run tests, view logs - all from GUI
- **📄 Integrated Log Viewer**: Browse and search MTR logs with syntax highlighting
- **📋 Context Menus**: Right-click to copy selected text from logs and activity
- **⚙️ GUI Configuration**: Edit settings and setup scheduler without touching terminal
- **📦 Standalone Executables**: Optional .exe/.app builds - no Python installation needed!
- **Cross-Platform Support**: Works on Windows, Linux, and macOS with automatic OS detection
- **Multi-Layer Connectivity Testing**: ICMP (ping), TCP, HTTP, and DNS validation
- **ISP Hop Monitoring**: Track your ISP's network hops to detect upstream issues
- **Automatic Root Cause Analysis**: Distinguishes between LAN, WAN, DNS, and transport layer problems
- **Continuous MTR Logging**: Records traceroute data during outages and periodic baselines (with Windows fallback)
- **Automated Scheduling**: Easy setup scripts for Task Scheduler, cron, and launchd
- **Flexible Timing**: Configure to run every minute, specific hours, weekdays only, etc.
- **Detailed Analysis Reports**: Automated outage summaries with statistics
- **ISP Discovery Tool**: Automatically identify your ISP's network hops

## 📋 Table of Contents

- [Graphical Interface (GUI)](#-graphical-interface-gui-new)
- [Home Assistant Integration](#-home-assistant-integration-new)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Understanding the Output](#-understanding-the-output)
- [Advanced Features](#-advanced-features)
- [Building Executables](#-building-executables)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🖥️ Graphical Interface (GUI) **NEW!**

### Using the GUI

**For users who prefer a graphical interface**, we now offer a full-featured GUI application!

#### Starting the GUI:

**From Python (source):**
```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Run GUI
python network_logging_gui.py
```

**From Executable (no Python needed):**
- **Windows:** Double-click `NetworkLoggingMonitor.exe`
- **Linux:** Run `./NetworkLoggingMonitor`
- **macOS:** Open `NetworkLoggingMonitor.app`

#### GUI Features:

- **📊 Real-Time Dashboard**: Live status of gateway, internet connectivity, and statistics
- **▶️ Start/Stop Monitoring**: One-click continuous monitoring
- **📈 Session Statistics**: Success rate, uptime, total checks
- **📝 Activity Log**: Real-time feed of all monitoring events
- **📄 Log Viewer**: Browse and search MTR logs with syntax highlighting
- **🔬 Manual Tests**: Run on-demand diagnostics
- **📁 Quick Access**: Open logs folder, edit config, analyze results
- **⏰ Scheduler Setup**: Configure automated monitoring with admin rights (GUI prompts)
- **🔍 ISP Discovery**: Find optimal monitoring targets
- **🔌 TCP Probing**: Test firewall and port connectivity
- **📋 Context Menus**: Right-click to copy selected text from any log window

**See [GUI_USAGE.md](GUI_USAGE.md) for complete documentation with screenshots.**

### Building Standalone Executables

Want to distribute the GUI as a single .exe/.app file?

```bash
# Install PyInstaller
pip install pyinstaller

# Windows
build_windows.bat

# Linux
./build_linux.sh

# macOS
./build_macos.sh
```

**See [BUILD.md](BUILD.md) for detailed build instructions.**

---

## 🏠 Home Assistant Integration **NEW!**

### Monitor Your Network in Home Assistant!

We now provide a **native Home Assistant custom integration** for seamless network monitoring!

#### Features:

- ✅ **Binary Sensors**: Gateway reachable, Internet connected, Per-target status
- ✅ **Statistics Sensors**: Gateway IP, Average latency, Success rate
- ✅ **Services**: Manual tests, Gateway checks
- ✅ **Automations**: Create alerts for network issues
- ✅ **Lovelace Cards**: Beautiful dashboard widgets
- ✅ **No External Dependencies**: Pure Python, uses built-in tools

#### Quick Install:

**Via HACS (Recommended):**
1. Add custom repository: `https://github.com/yourusername/network-logging`
2. Download "Network Monitoring" integration
3. Restart Home Assistant
4. Add to `configuration.yaml`:
   ```yaml
   network_logging:
     scan_interval: 300
     targets:
       - "1.1.1.1"
       - "8.8.8.8"
   ```
5. Restart Home Assistant again

**Manual Installation:**
1. Copy `custom_components/network_logging/` to `/config/custom_components/`
2. Restart Home Assistant
3. Configure (see above)
4. Restart again

#### Example Automation:

```yaml
automation:
  - alias: "Internet Down Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.network_internet_connected
        to: "off"
        for: "00:02:00"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Network Alert"
          message: "Internet connection lost!"
```

**See [custom_components/network_logging/README.md](custom_components/network_logging/README.md) for complete Home Assistant documentation.**

---


**See [BUILD.md](BUILD.md) for detailed compilation instructions.**

**Result:** Single ~25-35 MB executable with no Python installation required!

## 🏠 Home Assistant Integration **NEW!**

Integrate with Home Assistant for smart home automation and monitoring!

### Quick Setup

1. **Copy integration:**
   ```bash
   cp -r custom_components/network_logging /config/custom_components/
   ```

2. **Add to configuration.yaml:**
   ```yaml
   network_logging:
     project_path: "/path/to/network-logging"
     scan_interval: 60
     targets:
       - "1.1.1.1"
       - "8.8.8.8"
   ```

3. **Restart Home Assistant**

### Available Entities

**Binary Sensors:**
- `binary_sensor.network_gateway` - Gateway connectivity
- `binary_sensor.internet_connection` - Internet status
- Per-target sensors (e.g., `binary_sensor.internet_1_1_1_1`)

**Sensors:**
- `sensor.gateway_ip` - Gateway IP address
- `sensor.success_rate_today` - Success percentage
- `sensor.average_latency` - Latency in ms
- `sensor.packet_loss` - Packet loss percentage

**Services:**
- `network_logging.run_test` - Manual diagnostic
- `network_logging.analyze_logs` - Log analysis

### Example Automation

```yaml
automation:
  - alias: "Internet Down Alert"
    trigger:
      platform: state
      entity_id: binary_sensor.internet_connection
      from: "on"
      to: "off"
    action:
      service: notify.notify
      data:
        title: "🌐 Internet Outage"
        message: "Internet connection lost!"
```

**See [custom_components/network_logging/README.md](custom_components/network_logging/README.md) and [INSTALLATION.md](custom_components/network_logging/INSTALLATION.md) for complete Home Assistant documentation.**

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11, Linux, or macOS
- `mtr` (My Traceroute) - recommended for best results (optional on Windows, uses pathping fallback)
- Admin/sudo access for some network operations (especially on Windows)
- **Recommended:** Always-on device (server, Raspberry Pi, NAS) for continuous monitoring

### System Dependencies

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install mtr-tiny python3 python3-venv python3-tk  # python3-tk für GUI!
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install mtr python3 python3-tkinter  # python3-tkinter für GUI!
```

**macOS:**
```bash
brew install mtr
```

**Windows:**
```powershell
# MTR for Windows (optional, uses pathping as fallback)
# Download from: https://github.com/traviscross/mtr/releases
# Or use Chocolatey:
choco install mtr
```

### Project Setup

1. **Clone or download this repository:**
   
   ```bash
   # Linux/macOS
   git clone https://github.com/yourusername/network-logging.git
   cd network-logging
   ```
   
   ```powershell
   # Windows (PowerShell)
   git clone https://github.com/yourusername/network-logging.git
   cd network-logging
   ```

2. **Create a virtual environment (recommended):**
   
   > **⚠️ Important:** Always run this project in a virtual environment to avoid conflicts with system Python packages.
   
   ```bash
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   ```powershell
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: This project uses only Python standard library, so requirements.txt is minimal)*

4. **Create your configuration file:**
   
   ```bash
   # Linux/macOS
   cp config.example.json config.json
   ```
   
   ```powershell
   # Windows
   copy config.example.json config.json
   ```

5. **Discover your ISP hops (recommended):**
   ```bash
   python discover_isp_hops.py
   ```
   This will suggest ISP hop IPs to add to your `config.json`.

## ⚡ Quick Start

### Basic Usage

**Single monitoring cycle:**
```bash
python netLogging.py
```

This will:
- Test connectivity to your gateway and configured targets
- Log results to `logs/netlog.csv`
- Create detailed MTR logs if issues are detected
- Append to continuous per-target log files (no file spam!)

### Automated Monitoring (Platform-Specific)

For continuous monitoring, use the automated setup scripts:

> **💡 Tip:** These scripts are designed for **always-on devices**. If your device sleeps or shuts down, monitoring will stop. Consider using a Raspberry Pi, home server, or NAS for 24/7 monitoring.

**Windows (Task Scheduler):**
```powershell
# Run PowerShell as Administrator
.\setup_windows_scheduler.ps1
# Follow prompts to select interval
```

**Linux (cron):**
```bash
./setup_linux_cron.sh
# Follow prompts to select interval
```

**macOS (launchd):**
```bash
./setup_macos_launchd.sh
# Follow prompts to select interval
```

**See [SCHEDULING.md](SCHEDULING.md) for:**
- Detailed setup instructions
- Custom time schedules (business hours only, weekdays, etc.)
- Advanced configuration
- Troubleshooting

### Analyze Results

After collecting data:
```bash
python analyze_netlog.py
```

This generates a comprehensive report including:
- Outage timeline and statistics
- Availability percentages
- Gateway latency analysis
- Root cause breakdown
- Hourly distribution

## ⚙️ Configuration

Edit `config.json` to customize monitoring behavior. See `config.example.json` for detailed documentation.

### Essential Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `gateway` | Your router IP or `"auto"` | `"192.168.1.1"` |
| `targets` | Public IPs to test (e.g., DNS servers) | `["1.1.1.1", "8.8.8.8"]` |
| `log_dir` | Where to store logs | `"./logs"` |
| `ping_interval_sec` | Seconds between tests (for loop mode) | `20` |

### ISP Monitoring Settings

| Setting | Description | Recommendation |
|---------|-------------|----------------|
| `isp_targets` | ISP hop IPs to monitor | **Keep to 1-2 IPs max!** Use `discover_isp_hops.py` |
| `mtr_baseline_enabled` | Periodic MTR even when OK | `true` |
| `mtr_baseline_period_sec` | Seconds between baseline MTR | `900` (15 min) |

### Advanced Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `mtr_intensive_enabled` | Run detailed MTR during outages | `true` |
| `mtr_intensive_count` | Packets per MTR run | `60` |
| `analyze_on_outage` | Auto-run analysis on outage | `true` |
| `dns_test_hostname` | Hostname for DNS tests | `"example.com"` |

## 📊 Understanding the Output

### Main Log File: `logs/netlog.csv`

CSV columns include:
- **local_timestamp / utc_timestamp**: When the test ran
- **gateway_ms**: Latency to your router (ms)
- **targets_reachable**: Fraction of targets responding (e.g., "3/4")
- **dns_ok / http_dns_ok / http_ip_ok / tcp443_ok**: Layer-specific test results (1=pass, 0=fail)
- **overall_status**: `OK`, `LAN_DOWN`, `WAN_DOWN`, `DNS_APP_FAIL`, `APP_LAYER_FAIL`
- **root_cause_hint**: `DNS`, `ICMP-only`, `Transport`, `Mixed`
- **isp_reachable / isp_detail**: ISP hop status

### MTR Log Files: `logs/mtr_*.log`

**New: Consolidated format!** Instead of creating hundreds of files, each target gets ONE continuous log file:
- `logs/mtr_1_1_1_1.log` - All MTR runs to 1.1.1.1
- `logs/mtr_88_79_29_66.log` - All MTR runs to ISP hop

Each run is separated by timestamp headers:
```
============================================================
Run at: 20251002_143502
============================================================
Start: 2025-10-02T14:35:02+0200
HOST: your-server            Loss%   Snt   Last   Avg  Best  Wrst StDev
  1. AS???    192.168.1.1      0.0%    60    0.6   0.6   0.5   0.9   0.1
  2. AS???    ???             100.0    60    0.0   0.0   0.0   0.0   0.0
  3. AS3209   88.79.29.66      0.0%    60   13.8  13.9  13.6  14.4   0.2
...
```

### Analysis Output

Run `python analyze_netlog.py` to get:
```
=== Network Outage Analysis ===
Analysis period: 2025-10-01 22:36:08 to 2025-10-02 23:40:17
Total test cycles: 1,234
Total outages detected: 5

Overall availability: 99.18%
  OK cycles: 1,224 (99.18%)
  Outage cycles: 10 (0.82%)

Outage breakdown by root cause:
  DNS: 2 (0.16%)
  Transport: 3 (0.24%)
  ICMP-only: 5 (0.41%)

Gateway statistics:
  Average latency: 0.65 ms
  Min: 0.50 ms | Max: 2.30 ms
...
```

## 🔧 Advanced Features

### 1. ISP Hop Discovery

Find the best ISP hops to monitor:
```bash
python discover_isp_hops.py
```

This runs multiple traceroutes and suggests stable IPs in hops 2-5 (your ISP's network). Add these to `isp_targets` in config.json.

**Important:** Keep `isp_targets` to 1-2 IPs maximum to avoid log file explosion!

### 2. TCP Host Probing

Test TCP connectivity to multiple hosts:
```bash
# From config.json isp_targets + targets
python probe_tcp_hosts.py --from-config

# Custom hosts
python probe_tcp_hosts.py --hosts "1.1.1.1,8.8.8.8,9.9.9.9"

# From ISP discovery candidates
python probe_tcp_hosts.py --from-candidates
```

Outputs:
- Console summary
- `logs/tcp_probe_<timestamp>.json` with detailed results

### 3. On-Demand Analysis

Analyze specific time periods:
```bash
python analyze_netlog.py --csv logs/netlog.csv --log-dir logs
```

### 4. Custom Log Directory

Use a different log location:
```json
{
  "log_dir": "/var/log/network-monitoring"
}
```

The script will attempt to create this directory or fall back to `./logs`.

## 🐛 Troubleshooting

### "Gateway could not be automatically detected"

**Solution:** Set gateway manually in config.json:
```json
{
  "gateway": "192.168.1.1"
}
```

**Windows users:** The script tries `route print` to detect gateway. If this fails, set manually.

### "mtr: command not found"

**Solution:** Install mtr (or use built-in fallbacks):

**Linux:**
```bash
# Debian/Ubuntu
sudo apt install mtr-tiny

# RHEL/Fedora
sudo dnf install mtr
```

**macOS:**
```bash
brew install mtr
```

**Windows:**
- Download from: https://github.com/traviscross/mtr/releases
- Or the script will automatically use `pathping` as fallback (slower but works)

### Permission denied for network operations

**Linux/macOS:**
Some operations require elevated privileges:
```bash
sudo python netLogging.py
```

Or configure capabilities (Linux):
```bash
sudo setcap cap_net_raw+ep $(which mtr)
```

**Windows:**
Run PowerShell or Command Prompt as Administrator

### High CPU usage

**Solutions:**
- Increase `ping_interval_sec` in config.json (default: 20)
- Reduce `mtr_intensive_count` (default: 60)
- Disable baseline MTR: set `mtr_baseline_enabled` to `false`
- Reduce `isp_targets` to just 1 IP

### Scheduler not running tasks

**Windows:**
- Verify Task Scheduler service is running
- Check task history for errors
- Ensure paths in .bat file are absolute paths

**Linux:**
- Check cron service: `systemctl status cron`
- View cron logs: `grep CRON /var/log/syslog`

**macOS:**
- Check plist syntax: `plutil -lint ~/Library/LaunchAgents/com.networklogging.monitor.plist`
- View launchd errors: `launchctl list | grep networklogging`

## 📝 Example Workflow

**Documenting ISP Issues:**

> **Ideal Setup:** Run on a Raspberry Pi, home server, NAS (Synology, QNAP), or old PC that stays on 24/7.

1. **Set up monitoring:**
   ```bash
   python discover_isp_hops.py  # Find your ISP hops
   # Edit config.json with suggested ISP targets
   crontab -e  # Add cron job (Linux) or use setup scripts
   ```

2. **Let it run for days/weeks** - it logs automatically

3. **When you experience issues:**
   ```bash
   python analyze_netlog.py > outage_report_$(date +%Y%m%d).txt
   ```

4. **Submit evidence to ISP** with:
   - `outage_report_*.txt` - Summary statistics
   - `logs/netlog.csv` - Complete timeline
   - `logs/mtr_*.log` - Network path analysis during outages
   - `logs/wan_diag_*.log` - System diagnostics

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/yourusername/network-logging.git
cd network-logging
python3 -m venv venv
source venv/bin/activate
# Make changes and test
python netLogging.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Uses [mtr](https://github.com/traviscross/mtr) for network path analysis
- Inspired by the need to document ISP reliability issues
- Built with Python standard library only

## 📧 Contact

connyTheOne - Project Maintainer

GitHub: [@yourusername](https://github.com/connyTheOne)

---

**Star this repository if it helped you document your ISP's outages! ⭐**
