# Network Monitoring for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

A Home Assistant custom integration for monitoring network connectivity, gateway reachability, and internet connection status.

## ✨ Features

- 🌐 **Internet Connectivity Monitoring** - Track connectivity to multiple targets (Cloudflare DNS, Google DNS, etc.)
- 🚪 **Gateway Monitoring** - Automatically detects and monitors your default gateway
- 📊 **Network Statistics** - Success rate, average latency, and real-time status
- 🔔 **Automation Ready** - Use sensors in automations to detect network issues
- 🎯 **Lightweight** - No external dependencies, uses only built-in tools
- 🔧 **Customizable** - Configure scan interval and target IPs via YAML

## 📸 Screenshots

### Sensors in Home Assistant
```
🟢 Network Gateway Reachable: ON (12.3 ms)
🟢 Network Internet Connected: ON
🟢 Network Target 1.1.1.1: ON (8.5 ms)
🟢 Network Target 8.8.8.8: ON (15.2 ms)
```

### Statistics
```
📡 Network Gateway IP: 192.168.1.1
⚡ Network Average Latency: 11.8 ms
✅ Network Success Rate: 100%
```

## 🚀 Installation

### Manual Installation

1. Download the `network_logging` folder from this repository
2. Copy it to your Home Assistant's `custom_components` directory:
   ```
   /config/custom_components/network_logging/
   ```
3. Restart Home Assistant
4. Add configuration to your `configuration.yaml` (see below)
5. Restart Home Assistant again

### HACS Installation (Coming Soon)

This integration will be available via HACS in the future.

## ⚙️ Configuration

### Basic Configuration

Add to your `configuration.yaml`:

```yaml
network_logging:
  scan_interval: 300  # Check every 5 minutes (default)
  targets:  # IPs to monitor (default: Cloudflare and Google DNS)
    - "1.1.1.1"
    - "8.8.8.8"
```

### Advanced Configuration

```yaml
network_logging:
  scan_interval: 60  # Check every minute
  targets:
    - "1.1.1.1"      # Cloudflare DNS
    - "8.8.8.8"      # Google DNS  
    - "9.9.9.9"      # Quad9 DNS
    - "208.67.222.222"  # OpenDNS
```

### Configuration Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `scan_interval` | No | `300` | How often to check connectivity (in seconds) |
| `targets` | No | `["1.1.1.1", "8.8.8.8"]` | List of IPs/hostnames to monitor |

## 📊 Sensors

### Binary Sensors (on/off)

- `binary_sensor.network_gateway_reachable` - Is your router reachable?
- `binary_sensor.network_internet_connected` - Is internet working?
- `binary_sensor.network_target_X_X_X_X` - Per-target connectivity (one for each configured target)

**Attributes:**
- `latency_ms` - Response time in milliseconds (when reachable)

### Regular Sensors

- `sensor.network_gateway_ip` - Your router's IP address
- `sensor.network_average_latency` - Average ping time across all targets (ms)
- `sensor.network_success_rate` - Percentage of successful connectivity checks (%)

## 🎯 Services

### `network_logging.run_test`

Run a manual network test.

**Service Data (Optional):**
```yaml
service: network_logging.run_test
data:
  target: "1.1.1.1"  # Optional: specific target to test
```

### `network_logging.check_gateway`

Check gateway connectivity and log result.

```yaml
service: network_logging.check_gateway
data: {}
```

## 🤖 Automation Examples

### Alert on Internet Loss

```yaml
automation:
  - alias: "Internet Down Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.network_internet_connected
        to: "off"
        for: "00:02:00"  # Wait 2 minutes before alerting
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Network Alert"
          message: "Internet connection lost!"
```

### Alert on High Latency

```yaml
automation:
  - alias: "High Latency Warning"
    trigger:
      - platform: numeric_state
        entity_id: sensor.network_average_latency
        above: 100  # Alert if latency > 100ms
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          title: "🐌 Slow Network"
          message: "Network latency is {{ states('sensor.network_average_latency') }} ms"
```

### Gateway Unreachable Alert

```yaml
automation:
  - alias: "Router Unreachable"
    trigger:
      - platform: state
        entity_id: binary_sensor.network_gateway_reachable
        to: "off"
    action:
      - service: notify.mobile_app
        data:
          title: "🚪 Gateway Down"
          message: "Cannot reach router at {{ states('sensor.network_gateway_ip') }}"
```

## 🎨 Lovelace Dashboard Card

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Network Status
    show_header_toggle: false
    entities:
      - entity: binary_sensor.network_gateway_reachable
        name: Router
      - entity: binary_sensor.network_internet_connected
        name: Internet
      - entity: sensor.network_gateway_ip
        name: Gateway IP
        
  - type: entities
    title: Internet Targets
    show_header_toggle: false
    entities:
      - entity: binary_sensor.network_target_1_1_1_1
        name: Cloudflare DNS
      - entity: binary_sensor.network_target_8_8_8_8
        name: Google DNS
        
  - type: glance
    title: Network Statistics
    columns: 3
    entities:
      - entity: sensor.network_success_rate
        name: Success Rate
      - entity: sensor.network_average_latency
        name: Avg Latency
      - entity: sensor.network_gateway_ip
        name: Gateway
        
  - type: button
    name: Test Network Now
    tap_action:
      action: call-service
      service: network_logging.run_test
      service_data: {}
    icon: mdi:network-check
```

## 🛠️ Troubleshooting

### Sensors show "Unavailable"

**Causes:**
- Home Assistant doesn't have permission to run `ping` command
- Firewall blocking ICMP packets
- Targets are unreachable

**Solutions:**
1. Check Home Assistant logs: Settings → System → Logs
2. Try different targets (e.g., your router's IP)
3. Ensure container/user has network access

### Gateway IP shows "Unknown"

**Causes:**
- Home Assistant running in restricted container
- Network tools not available

**Solutions:**
- Check logs for specific error messages
- Verify `ip route` (Linux) or `ipconfig` (Windows) works on your system

### Integration doesn't load

**Solutions:**
1. Check configuration syntax in `configuration.yaml`
2. Look for errors in logs
3. Verify files are in correct location: `/config/custom_components/network_logging/`
4. Restart Home Assistant twice (once to load, once to activate)

## 🔧 Development

### File Structure

```
custom_components/network_logging/
├── __init__.py              # Main integration code
├── network_utils.py         # Network utility functions (ping, gateway detection)
├── manifest.json            # Integration metadata
├── services.yaml            # Service definitions
├── README.md                # This file
└── INSTALLATION.md          # Detailed installation guide
```

### Requirements

- Home Assistant 2023.9.0 or newer
- Python 3.11+
- Standard system tools: `ping`, `ip`/`ipconfig`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 💖 Support

If you find this integration useful, please consider:
- ⭐ Starring this repository
- 🐛 Reporting bugs via [Issues](https://github.com/yourusername/network-logging/issues)
- 💡 Suggesting features
- 📖 Improving documentation

## 🔗 Links

- [Home Assistant](https://www.home-assistant.io/)
- [HACS](https://hacs.xyz/)
- [Issue Tracker](https://github.com/yourusername/network-logging/issues)

---

Made with ❤️ for the Home Assistant community

[releases-shield]: https://img.shields.io/github/release/yourusername/network-logging.svg?style=for-the-badge
[releases]: https://github.com/yourusername/network-logging/releases
[license-shield]: https://img.shields.io/github/license/yourusername/network-logging.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
