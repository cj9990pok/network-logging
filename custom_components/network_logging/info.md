# Network Monitoring for Home Assistant

Monitor your network connectivity, gateway reachability, and internet connection status directly in Home Assistant.

## Features

- 🌐 **Internet Connectivity Monitoring** - Track multiple DNS targets
- 🚪 **Gateway Monitoring** - Auto-detect and monitor your router
- 📊 **Statistics** - Success rate, latency, real-time status
- 🔔 **Automation Ready** - Create alerts for network issues
- 🎯 **Lightweight** - No external dependencies
- 🔧 **Customizable** - Configure scan interval and targets

## Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click "Integrations"
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add this repository URL
6. Click "Download"
7. Restart Home Assistant
8. Add to `configuration.yaml` (see below)
9. Restart Home Assistant again

### Manual Installation

1. Download the `custom_components/network_logging` folder
2. Copy it to `/config/custom_components/network_logging/`
3. Restart Home Assistant
4. Add configuration (see below)
5. Restart Home Assistant again

## Configuration

Add to your `configuration.yaml`:

```yaml
network_logging:
  scan_interval: 300  # seconds (default: 300)
  targets:
    - "1.1.1.1"      # Cloudflare DNS
    - "8.8.8.8"      # Google DNS
```

## Sensors Created

### Binary Sensors
- `binary_sensor.network_gateway_reachable` - Router connectivity
- `binary_sensor.network_internet_connected` - Internet status
- `binary_sensor.network_target_*` - Per-target connectivity

### Regular Sensors
- `sensor.network_gateway_ip` - Your router's IP
- `sensor.network_average_latency` - Avg ping time (ms)
- `sensor.network_success_rate` - Connection success (%)

## Example Automation

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

## Lovelace Card

```yaml
type: entities
title: Network Status
entities:
  - binary_sensor.network_gateway_reachable
  - binary_sensor.network_internet_connected
  - sensor.network_gateway_ip
  - sensor.network_average_latency
  - sensor.network_success_rate
```

## Services

- `network_logging.run_test` - Manual network test
- `network_logging.check_gateway` - Check gateway connectivity

## Support

- [Documentation](https://github.com/yourusername/network-logging)
- [Issues](https://github.com/yourusername/network-logging/issues)
- [Changelog](https://github.com/yourusername/network-logging/blob/main/CHANGELOG.md)

---

**Made with ❤️ for the Home Assistant community**
