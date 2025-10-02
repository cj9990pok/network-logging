# Home Assistant Integration - Testing Guide

## 📋 Prerequisites

- Home Assistant installed (Core, Supervised, Container, or OS)
- SSH access to your Home Assistant server
- Network access to copy files

## 🧪 Testing Steps

### 1. Copy Integration Files

```bash
# Create directory
mkdir -p /config/custom_components

# Copy integration (adjust path to your clone)
cp -r /path/to/network-logging/custom_components/network_logging /config/custom_components/
```

### 2. Configure

Edit `/config/configuration.yaml`:

```yaml
network_logging:
  scan_interval: 300
  targets:
    - "1.1.1.1"
    - "8.8.8.8"
```

### 3. Restart Home Assistant

```bash
# Via UI: Settings → System → Restart
# Or CLI:
ha core restart
```

### 4. Verify

Check logs: `/config/home-assistant.log`

Expected entities:
- `binary_sensor.network_gateway_reachable`
- `binary_sensor.network_internet_connected`
- `sensor.network_average_latency`

## �� Troubleshooting

### Integration not loading

```bash
# Check files
ls -la /config/custom_components/network_logging/

# Check permissions
chmod -R 755 /config/custom_components/network_logging

# Check logs
tail -f /config/home-assistant.log | grep network_logging
```

### Gateway detection fails

Explicitly set in config:

```yaml
network_logging:
  gateway: "192.168.1.1"  # Your router IP
  targets:
    - "1.1.1.1"
```

## ✅ Success Checklist

- [ ] Integration loads without errors
- [ ] Gateway IP detected
- [ ] Binary sensors created
- [ ] Regular sensors show values
- [ ] Services available in Developer Tools

See [README.md](README.md) for full documentation.
