# Network Monitoring - Installation Guide

Complete step-by-step installation guide for the Network Monitoring integration for Home Assistant.

## Prerequisites

- Home Assistant 2023.9.0 or newer
- Access to your Home Assistant configuration directory
- Basic knowledge of YAML configuration

## Installation Methods

### Method 1: HACS (Recommended) 🌟

HACS (Home Assistant Community Store) is the easiest way to install and keep the integration updated.

#### Step 1: Install HACS

If you don't have HACS installed yet:
1. Visit [HACS Installation Guide](https://hacs.xyz/docs/setup/download)
2. Follow the instructions to install HACS
3. Restart Home Assistant

#### Step 2: Add Custom Repository

1. Open Home Assistant
2. Go to **HACS** → **Integrations**
3. Click the **three dots** (⋮) in the top right corner
4. Select **"Custom repositories"**
5. Add this repository:
   - **Repository URL**: `https://github.com/yourusername/network-logging`
   - **Category**: `Integration`
6. Click **"ADD"**

#### Step 3: Install Integration

1. Search for **"Network Monitoring"** in HACS
2. Click on the integration
3. Click **"DOWNLOAD"**
4. Select the latest version
5. Wait for download to complete
6. Restart Home Assistant

#### Step 4: Configure

1. Edit your `configuration.yaml` (see Configuration section below)
2. Restart Home Assistant again

✅ **Done!** Your sensors should now appear in Home Assistant.

---

### Method 2: Manual Installation

If you prefer manual installation or don't use HACS.

#### Step 1: Download Files

Download the latest release from GitHub:
```bash
cd /tmp
wget https://github.com/yourusername/network-logging/archive/refs/heads/main.zip
unzip main.zip
```

Or clone the repository:
```bash
git clone https://github.com/yourusername/network-logging.git
```

#### Step 2: Copy to Home Assistant

Copy the `network_logging` folder to your Home Assistant's `custom_components` directory:

**For Home Assistant OS / Supervised:**
```bash
# Via SSH or Terminal add-on
cp -r network-logging/custom_components/network_logging /config/custom_components/
```

**For Home Assistant Container:**
```bash
# Copy to your config volume
docker cp network-logging/custom_components/network_logging <container_name>:/config/custom_components/
```

**For Home Assistant Core (venv):**
```bash
cp -r network-logging/custom_components/network_logging ~/.homeassistant/custom_components/
```

#### Step 3: Verify Installation

Check that files are in place:
```bash
ls -la /config/custom_components/network_logging/
```

You should see:
```
__init__.py
network_utils.py
manifest.json
services.yaml
README.md
info.md
hacs.json
```

#### Step 4: Restart Home Assistant

Restart Home Assistant to load the integration:
- **Home Assistant OS/Supervised**: Settings → System → Restart
- **Container**: `docker restart homeassistant`
- **Core**: `sudo systemctl restart home-assistant`

#### Step 5: Configure

Edit `/config/configuration.yaml` (see Configuration section below)

#### Step 6: Restart Again

Restart Home Assistant one more time to activate the configuration.

✅ **Installation complete!**

---

## Configuration

### Basic Configuration

Add this to your `configuration.yaml`:

```yaml
network_logging:
  scan_interval: 300  # Check every 5 minutes (optional, default: 300)
  targets:            # IPs to monitor (optional, default: 1.1.1.1, 8.8.8.8)
    - "1.1.1.1"       # Cloudflare DNS
    - "8.8.8.8"       # Google DNS
```

### Advanced Configuration Examples

**Fast Monitoring (1 minute interval):**
```yaml
network_logging:
  scan_interval: 60
  targets:
    - "1.1.1.1"
    - "8.8.8.8"
    - "9.9.9.9"
```

**Multiple DNS Providers:**
```yaml
network_logging:
  scan_interval: 300
  targets:
    - "1.1.1.1"           # Cloudflare
    - "8.8.8.8"           # Google
    - "9.9.9.9"           # Quad9
    - "208.67.222.222"    # OpenDNS
    - "76.76.19.19"       # Alternate DNS
```

**Minimal Configuration (defaults):**
```yaml
network_logging: {}
```
This uses default values: 300s interval, 1.1.1.1 and 8.8.8.8 as targets.

### Configuration Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `scan_interval` | integer | No | `300` | How often to check connectivity (seconds) |
| `targets` | list | No | `["1.1.1.1", "8.8.8.8"]` | List of IP addresses or hostnames to monitor |

**scan_interval recommendations:**
- `60` - Real-time monitoring (high frequency)
- `300` - Default, balanced (5 minutes)
- `600` - Low frequency (10 minutes)
- `1800` - Very low frequency (30 minutes)

## Verification

### Check Integration is Loaded

1. Go to **Settings** → **System** → **Logs**
2. Look for: `"Network Logging integration loaded successfully"`
3. No errors should appear with `network_logging` in them

### Check Entities

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Filter by "network"
3. You should see:
   - `binary_sensor.network_gateway_reachable`
   - `binary_sensor.network_internet_connected`
   - `binary_sensor.network_target_1_1_1_1`
   - `binary_sensor.network_target_8_8_8_8`
   - `sensor.network_gateway_ip`
   - `sensor.network_average_latency`
   - `sensor.network_success_rate`

### Test Services

1. Go to **Developer Tools** → **Services**
2. Select `network_logging.run_test`
3. Click **"CALL SERVICE"**
4. Check logs for test results

## Uninstallation

### Remove Configuration

1. Remove the `network_logging:` section from `configuration.yaml`
2. Restart Home Assistant

### Remove Files (Manual Installation)

```bash
rm -rf /config/custom_components/network_logging
```

### Remove via HACS

1. Go to **HACS** → **Integrations**
2. Find **"Network Monitoring"**
3. Click the three dots (⋮)
4. Select **"Remove"**
5. Restart Home Assistant

## Updating

### Via HACS

1. HACS will notify you when updates are available
2. Click **"Update"** in HACS
3. Restart Home Assistant

### Manual Update

1. Download the latest version
2. Replace files in `/config/custom_components/network_logging/`
3. Restart Home Assistant twice

## Troubleshooting

### Integration doesn't load

**Check:**
1. Files are in correct location: `/config/custom_components/network_logging/`
2. `manifest.json` exists and is valid
3. Home Assistant has been restarted **twice** (once to detect, once to load)

**Solution:**
```bash
# Verify files
ls -la /config/custom_components/network_logging/

# Check logs
grep -i network_logging /config/home-assistant.log
```

### Sensors show "Unavailable"

**Causes:**
- Home Assistant can't run `ping` command
- Network access restricted
- Targets unreachable

**Solutions:**
1. Check if ping works: `docker exec homeassistant ping -c 1 1.1.1.1`
2. Try different targets (e.g., your router's IP)
3. Check firewall rules (ICMP packets)

### "Permission denied" errors

**For Docker installations:**
```bash
# Give container network capabilities
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN ...
```

**For Home Assistant OS:**
- This should work out of the box
- Check system logs: Settings → System → Logs

### Gateway IP shows "Unknown"

**Causes:**
- Container networking isolation
- `ip route` command not available

**Solutions:**
1. Check if command works: `docker exec homeassistant ip route`
2. Manually specify gateway in automations if needed

### Configuration errors

**Check YAML syntax:**
```bash
# Test configuration
ha core check
```

**Common mistakes:**
- Missing spaces in YAML (use spaces, not tabs)
- Incorrect indentation
- Quotes needed for IPs if they start with special chars

### Services not appearing

**Check:**
1. `services.yaml` exists in integration folder
2. No syntax errors in `services.yaml`
3. Integration loaded successfully (check logs)

**Solution:**
```bash
# Reload services
# Developer Tools → YAML → Services
```

## Support

### Get Help

- 📖 [Full Documentation](https://github.com/yourusername/network-logging)
- 🐛 [Report Issues](https://github.com/yourusername/network-logging/issues)
- 💬 [Home Assistant Community](https://community.home-assistant.io/)

### Before Asking for Help

Please provide:
1. Home Assistant version
2. Installation method (HACS/Manual)
3. Your `configuration.yaml` network_logging section
4. Relevant logs from Settings → System → Logs
5. Output of: `ls -la /config/custom_components/network_logging/`

### Debug Mode

Enable debug logging for detailed information:

```yaml
logger:
  default: info
  logs:
    custom_components.network_logging: debug
```

Then restart Home Assistant and check logs.

## Additional Resources

- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [YAML Syntax](https://www.home-assistant.io/docs/configuration/yaml/)
- [Automation Examples](README.md#automation-examples)
- [Lovelace Cards](README.md#lovelace-dashboard-card)

---

**Installation complete!** Enjoy monitoring your network in Home Assistant! 🎉
