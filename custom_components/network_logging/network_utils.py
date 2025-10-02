"""
Network utility functions for Home Assistant integration.
Standalone implementation without external dependencies.
"""

import asyncio
import logging
import platform
import re
import subprocess
from typing import Optional, Tuple

_LOGGER = logging.getLogger(__name__)


async def async_ping(host: str, count: int = 1, timeout: int = 5) -> Tuple[bool, float]:
    """
    Ping a host asynchronously.
    
    Args:
        host: IP address or hostname to ping
        count: Number of ping packets
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (success: bool, avg_latency: float in ms)
    """
    try:
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
        else:  # Linux, macOS, etc.
            cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
        
        # Run ping command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout + 2
        )
        
        if process.returncode != 0:
            return False, 0.0
        
        # Parse average latency from output
        output = stdout.decode('utf-8', errors='ignore')
        
        # Try to extract average latency
        latency = 0.0
        if system == "windows":
            # Windows: "Average = 12ms"
            match = re.search(r'Average\s*=\s*(\d+)ms', output, re.IGNORECASE)
            if match:
                latency = float(match.group(1))
        else:
            # Linux/macOS: "rtt min/avg/max/mdev = 1.234/5.678/9.012/1.234 ms"
            match = re.search(r'min/avg/max/[a-z]+ = [\d.]+/([\d.]+)/', output)
            if match:
                latency = float(match.group(1))
        
        return True, latency
        
    except asyncio.TimeoutError:
        _LOGGER.warning("Ping timeout for %s", host)
        return False, 0.0
    except Exception as e:
        _LOGGER.error("Ping error for %s: %s", host, e)
        return False, 0.0


async def async_get_gateway_ip() -> Optional[str]:
    """
    Get the default gateway IP address asynchronously.
    
    Returns:
        Gateway IP address or None if not found
    """
    try:
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ipconfig"]
            pattern = r'Default Gateway[^:]*:\s*(\d+\.\d+\.\d+\.\d+)'
        elif system == "darwin":  # macOS
            cmd = ["netstat", "-nr"]
            pattern = r'^default\s+(\d+\.\d+\.\d+\.\d+)'
        else:  # Linux
            cmd = ["ip", "route", "show", "default"]
            pattern = r'default via (\d+\.\d+\.\d+\.\d+)'
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=10
        )
        
        if process.returncode != 0:
            return None
        
        output = stdout.decode('utf-8', errors='ignore')
        
        # Search for gateway IP
        match = re.search(pattern, output, re.MULTILINE)
        if match:
            gateway = match.group(1)
            _LOGGER.debug("Found gateway: %s", gateway)
            return gateway
        
        return None
        
    except asyncio.TimeoutError:
        _LOGGER.warning("Gateway detection timeout")
        return None
    except Exception as e:
        _LOGGER.error("Gateway detection error: %s", e)
        return None


def sync_ping(host: str, count: int = 1, timeout: int = 5) -> Tuple[bool, float]:
    """
    Synchronous ping wrapper for backward compatibility.
    
    Args:
        host: IP address or hostname to ping
        count: Number of ping packets
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (success: bool, avg_latency: float in ms)
    """
    try:
        return asyncio.run(async_ping(host, count, timeout))
    except Exception as e:
        _LOGGER.error("Sync ping error: %s", e)
        return False, 0.0


def sync_get_gateway_ip() -> Optional[str]:
    """
    Synchronous gateway detection wrapper.
    
    Returns:
        Gateway IP address or None if not found
    """
    try:
        return asyncio.run(async_get_gateway_ip())
    except Exception as e:
        _LOGGER.error("Sync gateway detection error: %s", e)
        return None
