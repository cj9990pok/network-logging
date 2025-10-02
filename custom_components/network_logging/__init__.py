"""
Home Assistant Integration for Network Monitoring.
Provides binary sensors and sensors for network connectivity monitoring.

Version: 1.0.0
"""

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .network_utils import async_ping, async_get_gateway_ip

_LOGGER = logging.getLogger(__name__)

DOMAIN = "network_logging"
CONF_TARGETS = "targets"

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
DEFAULT_TARGETS = ["1.1.1.1", "8.8.8.8"]  # Cloudflare, Google DNS

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema({
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            vol.Optional(CONF_TARGETS, default=DEFAULT_TARGETS): vol.All(cv.ensure_list, [cv.string]),
        })
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: Dict[str, Any]) -> bool:
    """Set up the Network Logging component."""
    if DOMAIN not in config:
        # Allow setup via UI without YAML config
        config[DOMAIN] = {}
    
    conf = config[DOMAIN]
    scan_interval = conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    targets = conf.get(CONF_TARGETS, DEFAULT_TARGETS)

    # Initialize coordinator
    coordinator = NetworkMonitoringCoordinator(
        hass,
        scan_interval=timedelta(seconds=scan_interval),
        targets=targets,
    )
    
    # Initial data fetch (deprecated method but still works in 2024.10)
    try:
        await coordinator.async_config_entry_first_refresh()
    except AttributeError:
        # Fallback for newer HA versions
        await coordinator.async_refresh()
    
    hass.data[DOMAIN] = {
        "coordinator": coordinator,
        "config": conf,
    }

    # Register services
    async def handle_run_test(call: ServiceCall) -> None:
        """Handle the run_test service call."""
        target = call.data.get("target")
        if target:
            success, latency = await async_ping(target, count=3)
            _LOGGER.info(
                "Manual test for %s: %s (%.2f ms)",
                target,
                "Success" if success else "Failed",
                latency
            )
        else:
            # Test all targets
            await coordinator.async_request_refresh()

    async def handle_check_gateway(call: ServiceCall) -> None:
        """Handle the check_gateway service call."""
        gateway = await async_get_gateway_ip()
        if gateway:
            success, latency = await async_ping(gateway, count=3)
            _LOGGER.info(
                "Gateway %s: %s (%.2f ms)",
                gateway,
                "Reachable" if success else "Unreachable",
                latency
            )

    hass.services.async_register(DOMAIN, "run_test", handle_run_test)
    hass.services.async_register(DOMAIN, "check_gateway", handle_check_gateway)

    # Create sensors
    from homeassistant.helpers.entity_component import EntityComponent
    from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
    from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
    
    # Binary sensors
    binary_entities = [
        NetworkBinarySensor(coordinator, "gateway_reachable", "Gateway Reachable"),
        NetworkBinarySensor(coordinator, "internet_connected", "Internet Connected"),
    ]
    
    # Add target-specific binary sensors
    for target in targets:
        safe_name = target.replace(".", "_")
        binary_entities.append(
            NetworkBinarySensor(
                coordinator,
                f"target_{safe_name}",
                f"Target {target}"
            )
        )
    
    binary_component = EntityComponent(_LOGGER, BINARY_SENSOR_DOMAIN, hass)
    await binary_component.async_add_entities(binary_entities)
    
    # Regular sensors
    sensor_entities = [
        NetworkSensor(coordinator, "gateway_ip", "Gateway IP"),
        NetworkSensor(coordinator, "average_latency", "Average Latency", "ms"),
        NetworkSensor(coordinator, "success_rate", "Success Rate", "%"),
    ]
    
    sensor_component = EntityComponent(_LOGGER, SENSOR_DOMAIN, hass)
    await sensor_component.async_add_entities(sensor_entities)

    _LOGGER.info("Network Logging integration loaded successfully")
    return True


class NetworkMonitoringCoordinator(DataUpdateCoordinator):
    """Coordinator to manage network monitoring data updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        scan_interval: timedelta,
        targets: list,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=scan_interval,
        )
        self.targets = targets

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from network monitoring."""
        try:
            data = {}

            # Check gateway
            gateway = await async_get_gateway_ip()
            data["gateway_ip"] = gateway or "Unknown"
            
            if gateway:
                success, latency = await async_ping(gateway, count=1, timeout=5)
                data["gateway_reachable"] = success
                data["gateway_latency"] = latency
            else:
                data["gateway_reachable"] = False
                data["gateway_latency"] = 0.0

            # Check internet targets
            target_results = []
            latencies = []
            
            for target in self.targets:
                success, latency = await async_ping(target, count=1, timeout=5)
                safe_name = target.replace(".", "_")
                data[f"target_{safe_name}"] = success
                data[f"target_{safe_name}_latency"] = latency
                
                target_results.append(success)
                if success and latency > 0:
                    latencies.append(latency)
            
            # Overall internet connectivity
            data["internet_connected"] = any(target_results)
            
            # Calculate statistics
            if target_results:
                success_count = sum(1 for r in target_results if r)
                data["success_rate"] = round((success_count / len(target_results)) * 100, 1)
            else:
                data["success_rate"] = 0.0
            
            if latencies:
                data["average_latency"] = round(sum(latencies) / len(latencies), 2)
            else:
                data["average_latency"] = 0.0

            _LOGGER.debug("Network monitoring update: %s", data)
            return data

        except Exception as err:
            _LOGGER.error("Error updating network monitoring data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}")


class NetworkBinarySensor(Entity):
    """Binary sensor for network connectivity."""

    def __init__(self, coordinator: NetworkMonitoringCoordinator, data_key: str, name: str):
        """Initialize the binary sensor."""
        self._coordinator = coordinator
        self._data_key = data_key
        self._attr_name = f"Network {name}"
        self._attr_unique_id = f"{DOMAIN}_{data_key}"
        self._attr_device_class = "connectivity"
        
    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self._coordinator.data.get(self._data_key, False)
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success
    
    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False
    
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional attributes."""
        attrs = {}
        
        # Add latency if available
        latency_key = f"{self._data_key}_latency"
        if latency_key in self._coordinator.data:
            latency = self._coordinator.data[latency_key]
            if latency > 0:
                attrs["latency_ms"] = latency
        
        return attrs
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )
    
    async def async_update(self) -> None:
        """Update the entity."""
        await self._coordinator.async_request_refresh()


class NetworkSensor(Entity):
    """Sensor for network statistics."""

    def __init__(
        self,
        coordinator: NetworkMonitoringCoordinator,
        data_key: str,
        name: str,
        unit: Optional[str] = None,
    ):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._data_key = data_key
        self._attr_name = f"Network {name}"
        self._attr_unique_id = f"{DOMAIN}_{data_key}"
        self._attr_unit_of_measurement = unit
        
        # Set icon based on sensor type
        if "latency" in data_key:
            self._attr_icon = "mdi:speedometer"
        elif "success" in data_key or "rate" in data_key:
            self._attr_icon = "mdi:percent"
        elif "ip" in data_key:
            self._attr_icon = "mdi:ip-network"
        else:
            self._attr_icon = "mdi:network"
    
    @property
    def state(self) -> Any:
        """Return the state of the sensor."""
        return self._coordinator.data.get(self._data_key, "unknown")
    
    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._coordinator.last_update_success
    
    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False
    
    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(
                self.async_write_ha_state
            )
        )
    
    async def async_update(self) -> None:
        """Update the entity."""
        await self._coordinator.async_request_refresh()
