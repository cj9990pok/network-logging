# Quick Start Guide

Get up and running with Network Logging in 5 minutes!

> **💡 Best for Always-On Devices:** This tool works best on devices that run 24/7 like:
> - 🏠 Home servers
> - 🥧 Raspberry Pi (any model)
> - 💾 NAS devices (Synology, QNAP, etc.)
> - 🖥️ Dedicated monitoring PC/old laptop
> - ☁️ Cloud VMs

## Prerequisites

- Linux or macOS
- Python 3.8+
- `mtr` installed

## Step-by-Step Setup

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install mtr-tiny python3 python3-venv
```

**Fedora/RHEL:**
```bash
sudo dnf install mtr python3
```

**macOS:**
```bash
brew install mtr
```

### 2. Get the Code

```bash
git clone https://github.com/yourusername/network-logging.git
cd network-logging
```

### 3. Set Up Python Environment

> **⚠️ Important:** Always use a virtual environment! This keeps the project isolated from system Python.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # Currently no external deps needed!
```

### 4. Configure

```bash
cp config.example.json config.json
```

**Edit config.json:**
- Set `gateway` to your router IP (or use `"auto"`)
- Adjust `log_dir` if needed

**Optional - Discover your ISP hops:**
```bash
python discover_isp_hops.py
# Add suggested IPs to "isp_targets" in config.json
```

### 5. Test Run

```bash
python netLogging.py
```

Check the output - you should see:
```
Network logging gestartet um 2025-10-02 14:35:00
Logs werden gespeichert in: ./logs
Gateway: 192.168.2.1
```

Verify logs were created:
```bash
ls -l logs/
# Should see: netlog.csv and possibly mtr_*.log files
```

### 6. Set Up Automated Monitoring

**Using cron (recommended):**

```bash
# Edit crontab
crontab -e

# Add this line (adjust paths!):
* * * * * /path/to/venv/bin/python /path/to/netLogging.py >> /path/to/logs/cron.log 2>&1
```

**Or use the wrapper script:**

```bash
# Edit start_netlogging.sh with your paths
nano start_netlogging.sh

# Add to crontab
crontab -e
# Add: * * * * * /path/to/start_netlogging.sh
```

### 7. Let It Run!

Wait a few hours or days to collect data.

### 8. Analyze Results

```bash
python analyze_netlog.py
```

This will show:
- Overall availability
- Outage breakdown
- Gateway latency statistics
- Root cause analysis

## 🎉 You're Done!

Your network is now being monitored continuously. Check `logs/netlog.csv` anytime to see the data.

## Next Steps

- **Customize monitoring**: Edit `config.json` to adjust targets, intervals, and features
- **Review documentation**: See [README.md](README.md) for detailed configuration options
- **Optimize logging**: Reduce `isp_targets` to 1 IP to minimize disk usage

## Troubleshooting

### "Gateway could not be automatically detected"
Set it manually in config.json: `"gateway": "192.168.1.1"`

### "mtr: command not found"
Install mtr: `sudo apt install mtr-tiny` (Linux) or `brew install mtr` (macOS)

### Permission errors
Some operations may need sudo: `sudo python netLogging.py`

### No logs appearing
- Check `log_dir` path in config.json
- Verify write permissions to log directory
- Check cron logs: `tail -f logs/cron.log`

## Questions?

See the full [README.md](README.md) or open an issue on GitHub.

---

**Happy monitoring! 📊**
