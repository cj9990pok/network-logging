# Home Assistant Integration - Testing Guide

## 📋 Prerequisites

- Home Assistant installed (Core, Supervised, or OS)
- SSH access to your Home Assistant server (for file copying)
- Network Logging project running on same machine or network-accessible

## 🧪 Local Testing Instructions

### Step 1: Install Required Python Packages

First, ensure the required Python packages are available in your Home Assistant environment:

```bash
# For Home Assistant Core (venv installation)
cd /path/to/homeassistant
source bin/activate
pip install voluptuous>=0.13.1

# For Home Assistant OS/Supervised
# Packages are typically pre-installed, but you can check:
ha core restart
```

### Step 2: Copy Integration Files

Copy the custom component to your Home Assistant configuration directory:

```bash
# SSH into your Home Assistant server
ssh your-ha-user@your-ha-ip

# Create custom_components directory if it doesn't exist
mkdir -p /config/custom_components

# Copy the network_logging integration
# Option A: If project is on same machine
cp -r /media/homeserver/Family/Conrad/Python/netlogging_env/custom_components/network_logging /config/custom_components/

# Option B: Use SCP from your development machine
# (run this on your dev machine, not on HA server)
scp -r /media/homeserver/Family/Conrad/Python/netlogging_env/custom_components/network_logging your-ha-user@your-ha-ip:/config/custom_components/
```

### Step 3: Configure Integration

Edit your Home Assistant `configuration.yaml`:

```bash
# On Home Assistant server
nano /config/configuration.yaml
```

Add the network_logging configuration:

```yaml
# Network Logging Integration
network_logging:
  project_path: "/media/homeserver/Family/Conrad/Python/netlogging_env"
  scan_interval: 300  # Check every 5 minutes
```

**Important:** Adjust `project_path` to match the actual location of your Network Logging project on the Home Assistant server.

### Step 4: Restart Home Assistant

```bash
# For Home Assistant Core
sudo systemctl restart home-assistant

# For Home Assistant OS/Supervised
ha core restart

# Or use the UI: Settings → System → Restart
```

### Step 5: Verify Installation

#### A. Check Logs

```bash
# Watch logs in real-time
tail -f /config/home-assistant.log

# Or in UI: Settings → System → Logs
# Look for:
# - "Setting up network_logging"
# - "Network Logging initialized"
# - Any errors related to network_logging
```

#### B. Check Developer Tools

1. Go to **Settings → Devices & Services**
2. Search for "Network Logging" in integrations list
3. Go to **Developer Tools → States**
4. Filter by `network_logging` - you should see:

**Binary Sensors:**
- `binary_sensor.network_gateway_reachable`
- `binary_sensor.network_internet_connected`
- `binary_sensor.network_target_1_1_1_1` (for each target in config.json)
- `binary_sensor.network_target_8_8_8_8`

**Regular Sensors:**
- `sensor.network_gateway_ip`
- `sensor.network_success_rate_today`
- `sensor.network_average_latency`
- `sensor.network_packet_loss`

#### C. Test Services

Go to **Developer Tools → Services** and test these services:

**1. Run Manual Test:**
```yaml
service: network_logging.run_test
data:
  target: "1.1.1.1"
```

**2. Analyze Logs:**
```yaml
service: network_logging.analyze_logs
data: {}
```

### Step 6: View in Lovelace Dashboard

Create a test dashboard to view your sensors:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Network Status
    entities:
      - binary_sensor.network_gateway_reachable
      - binary_sensor.network_internet_connected
      - sensor.network_gateway_ip
      
  - type: entities
    title: Network Statistics
    entities:
      - sensor.network_success_rate_today
      - sensor.network_average_latency
      - sensor.network_packet_loss
      
  - type: entities
    title: Target Connectivity
    entities:
      - binary_sensor.network_target_1_1_1_1
      - binary_sensor.network_target_8_8_8_8
      - binary_sensor.network_target_9_9_9_9
      
  - type: button
    name: Run Network Test
    tap_action:
      action: call-service
      service: network_logging.run_test
      service_data:
        target: "1.1.1.1"
```

## 🐛 Troubleshooting

### Integration Not Loading

**Symptoms:** No network_logging entities appear in States

**Check:**
1. Verify path in `configuration.yaml` is correct
2. Check logs for Python errors
3. Ensure `config.json` exists in project directory
4. Verify file permissions (Home Assistant must be able to read project files)

**Fix:**
```bash
# Fix permissions
chmod -R 755 /media/homeserver/Family/Conrad/Python/netlogging_env
chown -R homeassistant:homeassistant /config/custom_components/network_logging
```

### Sensors Show "Unavailable"

**Symptoms:** Entities exist but show as unavailable

**Check:**
1. Monitor logs during coordinator update cycle (every scan_interval)
2. Verify `netLogging.py` is importable:

```bash
# On HA server
cd /media/homeserver/Family/Conrad/Python/netlogging_env
python3 -c "import netLogging; print('OK')"
```

3. Check if Network Logging scripts work standalone:

```bash
cd /media/homeserver/Family/Conrad/Python/netlogging_env
python3 netLogging.py
```

**Fix:**
- If imports fail, install dependencies in HA venv:
```bash
# For Core installation
source /srv/homeassistant/bin/activate
pip install -r /media/homeserver/Family/Conrad/Python/netlogging_env/requirements.txt
```

### Services Not Working

**Symptoms:** Services appear but fail when called

**Check:**
1. Look at service call response in Developer Tools
2. Check logs immediately after service call
3. Verify network_logging process isn't already running

**Fix:**
- Ensure only one instance of netLogging is running
- Check `logs/cron.log` for conflicts with cron jobs

### Permission Errors

**Symptoms:** `Permission denied` errors in logs

**Fix:**
```bash
# Allow HA user to access project directory
chmod -R 755 /media/homeserver/Family/Conrad/Python/netlogging_env

# If using Home Assistant OS, mount project directory with proper permissions
# Edit your docker-compose.yml or add to Supervisor config
```

## 🔍 Advanced Debugging

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.network_logging: debug
```

Restart Home Assistant and check logs for detailed debugging output.

### Manual Component Test

Test the component directly:

```bash
# On HA server
cd /config/custom_components/network_logging
python3 -c "
import sys
sys.path.insert(0, '/media/homeserver/Family/Conrad/Python/netlogging_env')
from __init__ import NetworkLoggingCoordinator
print('Import successful')
"
```

### Check Coordinator Updates

Monitor the coordinator's update cycle:

```bash
# Watch for updates in log
tail -f /config/home-assistant.log | grep network_logging
```

You should see updates every `scan_interval` seconds (default 300s).

## ✅ Verification Checklist

- [ ] Files copied to `/config/custom_components/network_logging/`
- [ ] `configuration.yaml` updated with correct `project_path`
- [ ] Home Assistant restarted successfully
- [ ] No errors in logs related to network_logging
- [ ] Binary sensors appear in Developer Tools → States
- [ ] Regular sensors appear in Developer Tools → States
- [ ] `run_test` service executes successfully
- [ ] `analyze_logs` service executes successfully
- [ ] Sensors update every scan_interval
- [ ] Lovelace dashboard displays sensor values

## 📞 Getting Help

If you encounter issues:

1. **Check logs first:** Settings → System → Logs
2. **Enable debug logging** (see above)
3. **Verify standalone operation:**
   ```bash
   cd /media/homeserver/Family/Conrad/Python/netlogging_env
   python3 netLogging.py  # Should work without errors
   ```
4. **Test imports:**
   ```bash
   python3 -c "import netLogging; import json; import subprocess; print('All imports OK')"
   ```
5. **Check file structure:**
   ```bash
   ls -la /config/custom_components/network_logging/
   # Should show: __init__.py, manifest.json, services.yaml
   ```

## 🎯 Quick Test Commands

```bash
# 1. Verify integration loaded
ha core check

# 2. Restart Home Assistant
ha core restart

# 3. View logs
ha core logs -f

# 4. Test from command line (if accessible)
echo "Testing netLogging..."
cd /media/homeserver/Family/Conrad/Python/netlogging_env
python3 netLogging.py

# 5. Check sensor states via API
curl -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN" \
  http://your-ha-ip:8123/api/states/binary_sensor.network_gateway_reachable
```

## 🚀 Next Steps

Once testing is successful:

1. **Create Automations:** Use network status to trigger actions
2. **Setup Notifications:** Alert on internet disconnects
3. **Historical Graphs:** Add recorder/history for sensors
4. **Mobile Dashboard:** Create Home Assistant app widget

Example automation:

```yaml
automation:
  - alias: "Internet Down Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.network_internet_connected
        to: "off"
        for: "00:02:00"  # Wait 2 minutes
    action:
      - service: notify.mobile_app
        data:
          title: "Network Alert"
          message: "Internet connection lost!"
```

Happy testing! 🎉
