#!/usr/bin/env python3
"""
Network Logging - Comprehensive Internet Connectivity Monitor

Cross-platform network monitoring tool for Windows, Linux, and macOS.
Continuously monitors network connectivity across multiple layers:
- ICMP (ping) to gateway, ISP hops, and public targets
- DNS resolution tests
- HTTP(S) connectivity (both DNS-based and IP-based)
- TCP socket connectivity tests

Logs all results to CSV and triggers detailed MTR traces during outages.
Designed for automated execution (cron/Task Scheduler/launchd).

Author: Conrad Heilmann
License: MIT
"""

import time, csv, subprocess, socket, datetime, os, json, sys, platform

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def is_windows():
    """Check if running on Windows."""
    return platform.system().lower() == "windows"

def is_macos():
    """Check if running on macOS."""
    return platform.system().lower() == "darwin"

def is_linux():
    """Check if running on Linux."""
    return platform.system().lower() == "linux"

def load_config():
    """Load configuration from config.json."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    """Save configuration to config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)

def get_gateway_ip():
    """
    Auto-detect the default gateway IP address (cross-platform).
    
    Returns:
        str: Gateway IP address, or None if detection fails
    """
    try:
        if is_windows():
            # Windows: route print | findstr 0.0.0.0
            out = subprocess.check_output(["route", "print"], text=True, errors="ignore")
            for line in out.splitlines():
                if "0.0.0.0" in line and "0.0.0.0" in line.split()[0]:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]  # Gateway is typically 3rd column
        elif is_macos():
            # macOS: route -n get default | grep gateway
            out = subprocess.check_output(["route", "-n", "get", "default"], text=True)
            for line in out.splitlines():
                if "gateway:" in line.lower():
                    return line.split()[-1]
        else:  # Linux
            # Linux: ip route | grep default
            out = subprocess.check_output(["ip", "route"], text=True)
            for line in out.splitlines():
                if line.startswith("default"):
                    return line.split()[2]
    except Exception:
        pass
    return None

def ping(host, timeout=4):
    """
    Ping a host and return RTT in seconds (cross-platform).
    
    Args:
        host (str): IP address or hostname to ping
        timeout (int): Timeout in seconds
        
    Returns:
        float: Round-trip time in seconds, or None if ping failed
    """
    try:
        if is_windows():
            # Windows: ping -n 1 -w timeout_ms host
            result = subprocess.run(
                ["ping", "-n", "1", "-w", str(int(timeout*1000)), host],
                capture_output=True,
                text=True,
                timeout=timeout+1
            )
            if result.returncode == 0:
                # Parse "Average = XXms" or "time=XXms"
                for line in result.stdout.split('\n'):
                    if 'Average' in line or 'time=' in line:
                        import re
                        match = re.search(r'(\d+)ms', line)
                        if match:
                            return float(match.group(1)) / 1000
                return 0.001
        else:
            # Linux/macOS: ping -c 1 -W timeout host
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(int(timeout)), host], 
                capture_output=True, 
                text=True, 
                timeout=timeout+1
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        time_str = line.split('time=')[1].split(' ')[0]
                        return float(time_str) / 1000
                return 0.001
        return None
    except Exception:
        return None

def http_ok(url, timeout=5):
    """
    Test HTTP(S) connectivity to a URL.
    
    Args:
        url (str): Full URL to test (e.g., "https://example.com")
        timeout (int): Timeout in seconds
        
    Returns:
        bool: True if HTTP status is 2xx or 3xx, False otherwise
    """
    import urllib.request, ssl
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(url, timeout=timeout, context=ctx) as r:
            return 200 <= r.status < 400
    except Exception:
        return False

def tcp_connect_ok(host: str, port: int, timeout: float = 5.0) -> bool:
    """
    Test TCP socket connectivity.
    
    Args:
        host: IP address or hostname
        port: TCP port number
        timeout: Connection timeout in seconds
        
    Returns:
        bool: True if TCP connection succeeds, False otherwise
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def dns_ok(hostname="example.com"):
    """
    Test DNS resolution by resolving a hostname.
    
    Args:
        hostname (str): Hostname to resolve
        
    Returns:
        bool: True if DNS resolution succeeds, False otherwise
    """
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False

def run_traceroute(host, log_dir, cooldown_sec, last_trace_ts):
    """
    Run traceroute/tracert/mtr to a host (cross-platform).
    
    Args:
        host: Target IP or hostname
        log_dir: Directory to store trace logs
        cooldown_sec: Minimum seconds between traces
        last_trace_ts: Timestamp of last trace
        
    Returns:
        tuple: (filename, new_timestamp) or (None, old_timestamp)
    """
    now = time.time()
    if now - last_trace_ts < cooldown_sec:
        return None, last_trace_ts
    last_trace_ts = now
    try:
        # Try MTR first (best option, works on all platforms if installed)
        mtr_check = subprocess.run(
            ["mtr", "--version"] if not is_windows() else ["where", "mtr"],
            capture_output=True,
            timeout=2
        )
        if mtr_check.returncode == 0:
            cmd = ["mtr", "-n", "-r", "-c", "5", host]
        elif is_windows():
            cmd = ["tracert", "-d", "-w", "1000", host]
        else:
            cmd = ["traceroute", "-n", "-w", "1", host]
        
        out = subprocess.check_output(cmd, timeout=60, text=True, errors="ignore")
        fname = f"trace_{host}_{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.log"
        trace_path = os.path.join(log_dir, fname)
        with open(trace_path, "w", encoding="utf-8") as f:
            f.write(out)
        return fname, last_trace_ts
    except Exception:
        return None, last_trace_ts

def ensure_log_directory(log_dir):
    """
    Ensure log directory exists, create if needed (cross-platform).
    
    Args:
        log_dir: Desired log directory path
        
    Returns:
        str: Actual log directory path used
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    except PermissionError:
        # Fallback to a logs directory next to this script
        fallback = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(fallback, exist_ok=True)
        return fallback

def ensure_log_header(logfile):
    try:
        with open(logfile, newline="", encoding="utf-8") as f:
            # Header exists if file is non-empty; we won't rewrite to avoid duplicating
            pass
    except FileNotFoundError:
        with open(logfile,"w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "local_timestamp","utc_timestamp","gateway_ms","targets_reachable",
                "dns_ok","http_dns_ok","http_ip_ok","tcp443_ok",
                "overall_status","trace_file","intensive_trace_bundle","wan_diag_file","root_cause_hint","isp_reachable","isp_tcp_ok","baseline_mtr_bundle","isp_detail"
            ])

def append_row(logfile, row):
    # Ensure header columns exist; if file was created earlier with old header, we still append in new format
    # Downstream analysis should handle missing columns gracefully.
    with open(logfile, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(row)

def write_text(path, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def run_cmd_capture(cmd, timeout=30) -> str:
    try:
        out = subprocess.check_output(cmd, text=True, errors="ignore", timeout=timeout)
        return out
    except Exception as e:
        return f"COMMAND FAILED: {' '.join(cmd)}\n{e}"

def collect_wan_diagnostics(log_dir):
    """
    Collect system network diagnostics (cross-platform).
    
    Args:
        log_dir: Directory to store diagnostic logs
        
    Returns:
        str: Filename of diagnostic log
    """
    ts = datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')
    fname = f"wan_diag_{ts}.log"
    path = os.path.join(log_dir, fname)
    parts = []
    
    if is_windows():
        # Windows diagnostics
        parts.append("==== ipconfig /all ====" + "\n" + run_cmd_capture(["ipconfig", "/all"]))
        parts.append("\n==== route print ====" + "\n" + run_cmd_capture(["route", "print"]))
        parts.append("\n==== netstat -s ====" + "\n" + run_cmd_capture(["netstat", "-s"]))
        parts.append("\n==== Get-NetAdapter (PowerShell) ====" + "\n" + run_cmd_capture(
            ["powershell", "-Command", "Get-NetAdapter | Format-List"]))
    elif is_macos():
        # macOS diagnostics
        parts.append("==== ifconfig ====" + "\n" + run_cmd_capture(["ifconfig"]))
        parts.append("\n==== netstat -rn ====" + "\n" + run_cmd_capture(["netstat", "-rn"]))
        parts.append("\n==== networksetup -listallnetworkservices ====" + "\n" + run_cmd_capture(
            ["networksetup", "-listallnetworkservices"]))
    else:
        # Linux diagnostics
        parts.append("==== ip addr ====" + "\n" + run_cmd_capture(["ip", "addr"]))
        parts.append("\n==== ip -s link ====" + "\n" + run_cmd_capture(["ip", "-s", "link"]))
        parts.append("\n==== ip route ====" + "\n" + run_cmd_capture(["ip", "route"]))
        # Try NetworkManager logs (may not exist on all systems)
        parts.append("\n==== journalctl NetworkManager (last 10m) ====" + "\n" + run_cmd_capture(
            ["journalctl", "-u", "NetworkManager", "--since", "10 minutes ago", "-n", "200"]))
    
    write_text(path, "\n\n".join(parts))
    return fname

def run_mtr_intensive(targets, log_dir, count=60):
    """
    Run intensive MTR (My Traceroute) to specified targets (cross-platform).
    
    New behavior: Appends to single continuous log file per target
    instead of creating new timestamped files for each run.
    
    Fallback: Uses pathping on Windows if MTR not available.
    
    Args:
        targets (list): List of IP addresses to trace
        log_dir (str): Directory to store log files
        count (int): Number of packets to send per target
        
    Returns:
        list: Filenames of log files created/updated
    """
    bundle_files = []
    
    # Check if MTR is available
    try:
        if is_windows():
            mtr_available = subprocess.run(["where", "mtr"], capture_output=True).returncode == 0
        else:
            mtr_available = subprocess.run(["which", "mtr"], capture_output=True).returncode == 0
    except Exception:
        mtr_available = False
    
    if not mtr_available:
        # On Windows, try pathping as fallback
        if is_windows():
            print("Warning: MTR not found, using pathping (slower). Install MTR for better results.")
        else:
            print("Warning: MTR not installed. Please install: apt install mtr (Linux) or brew install mtr (macOS)")
            return bundle_files
    
    ts = datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')
    for t in targets:
        try:
            if mtr_available:
                out = subprocess.check_output(
                    ["mtr", "-n", "-r", "-w", "-z", "-c", str(int(count)), t],
                    text=True,
                    errors="ignore",
                    timeout=count*2
                )
            elif is_windows():
                # Fallback to pathping on Windows (much slower!)
                out = subprocess.check_output(
                    ["pathping", "-n", "-q", str(min(int(count), 10)), t],
                    text=True,
                    errors="ignore",
                    timeout=300  # pathping is VERY slow
                )
            else:
                continue
            
            # Use single continuous log file per target instead of timestamped files
            fname = f"mtr_{t.replace('.', '_')}.log"
            path = os.path.join(log_dir, fname)
            # Append to existing file with timestamp separator
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Run at: {ts}\n")
                f.write(f"{'='*60}\n")
                f.write(out)
            bundle_files.append(fname)
        except Exception as e:
            print(f"Warning: Failed to run MTR/pathping for {t}: {e}")
            continue
    return bundle_files

def run_analyzer_on_outage(log_dir: str, logfile: str, cfg: dict):
    """Invoke analyze_netlog.py and persist its output when an outage is detected.
    Controlled by cfg['analyze_on_outage'] (default True) and cfg['analyze_cooldown_sec'] (default 300).
    """
    if not cfg.get("analyze_on_outage", True):
        return None

    # Cooldown marker to avoid running too frequently
    cooldown = int(cfg.get("analyze_cooldown_sec", 300))
    marker = os.path.join(log_dir, "analyze_last.txt")
    now = int(time.time())
    try:
        if os.path.exists(marker):
            last = int(open(marker, "r", encoding="utf-8").read().strip() or "0")
            if now - last < cooldown:
                return None
    except Exception:
        pass

    analyzer = os.path.join(os.path.dirname(__file__), "analyze_netlog.py")
    if not os.path.exists(analyzer):
        return None

    ts = datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')
    out_path = os.path.join(log_dir, f"analysis_on_outage_{ts}.log")
    cmd = [sys.executable, analyzer, "--csv", logfile, "--log-dir", log_dir]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=int(cfg.get("analyze_timeout_sec", 120)))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(proc.stdout)
            if proc.stderr:
                f.write("\n=== STDERR ===\n")
                f.write(proc.stderr)
        try:
            with open(marker, "w", encoding="utf-8") as m:
                m.write(str(now))
        except Exception:
            pass
        return os.path.basename(out_path)
    except Exception:
        return None
    
def mtr_to_first_hop(target, log_dir):
    """Run short MTR (10 packets) to just the first ISP hop."""
    ts = datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')
    fname = f"mtr_hop1_{target.replace('.','_')}_{ts}.log"
    path = os.path.join(log_dir, fname)
    try:
        cmd = ["mtr", "-n", "-r", "-c", "10", target]
        out = subprocess.check_output(cmd, text=True, timeout=15, errors="ignore")
        write_text(path, out)
        return fname
    except Exception:
        return ""

def main():
    cfg = load_config()
    # Gateway automatisch ermitteln
    if cfg["gateway"] == "auto":
        gw_ip = get_gateway_ip()
        if gw_ip and ping(gw_ip):
            cfg["gateway"] = gw_ip
            save_config(cfg)
            print(f"Gateway automatisch erkannt und gespeichert: {gw_ip}")
        else:
            print("Gateway konnte nicht automatisch ermittelt werden!")
            return
    else:
        gw_ip = cfg["gateway"]

    LOG_DIR = ensure_log_directory(cfg["log_dir"])
    LOGFILE = os.path.join(LOG_DIR, "netlog.csv")
    ensure_log_header(LOGFILE)

    print(f"Network logging gestartet um {datetime.datetime.now()}")
    print(f"Logs werden gespeichert in: {LOG_DIR}")
    print(f"Gateway: {gw_ip}")
    print(f"Zeitzone: {datetime.datetime.now().astimezone().tzinfo}")

    # Single-shot execution for cron control
    ts_utc = datetime.datetime.now(datetime.UTC)
    ts_local = datetime.datetime.now()
    
    ping_timeout = int(cfg.get("ping_timeout_sec", 4))
    gw_rtt = ping(gw_ip, timeout=ping_timeout)
    target_results = []
    for t in cfg["targets"]:
        r = ping(t, timeout=ping_timeout)
        target_results.append((t, r))

    # ISP targets reachability (optional)
    isp_targets = cfg.get("isp_targets", []) or []
    isp_results = []
    for t in isp_targets:
        r = ping(t, timeout=ping_timeout)
        isp_results.append((t, r))

    dns_test_hostname = cfg.get("dns_test_hostname", "example.com")
    dns_ok_flag = dns_ok(dns_test_hostname)
    
    http_timeout = int(cfg.get("http_timeout_sec", 5))
    http_dns_ok_flag = http_ok(cfg["http_url"], timeout=http_timeout)
    http_ip_ok_flag = http_ok(cfg.get("http_ip_url", "https://1.1.1.1"), timeout=http_timeout)
    
    tcp_timeout = int(cfg.get("tcp_timeout_sec", 5))
    tcp443_ok_flag = tcp_connect_ok(
        cfg.get("tcp_test_ip", "1.1.1.1"), 
        int(cfg.get("tcp_test_port", 443)),
        timeout=tcp_timeout
    )

    if len(isp_results) < len(isp_targets) // 2:
        # Mehr als die Hälfte der ISP-Hops nicht erreichbar → kurzes MTR
        for ip in isp_targets[:2]:  # nur erste 2 Hops
            mtr_to_first_hop(ip, LOG_DIR)

    reachable_targets = sum(1 for _, r in target_results if r is not None)
    if gw_rtt is None:
        status = "LAN_DOWN"
    elif reachable_targets == 0:
        status = "WAN_DOWN"
    elif not http_dns_ok_flag:
        # If DNS URL fails but IP URL ok, flag DNS issue
        status = "DNS_APP_FAIL" if http_ip_ok_flag else "APP_LAYER_FAIL"
    else:
        status = "OK"

    trace_file = ""
    intensive_bundle = []
    wan_diag_file = ""
    if status != "OK":
        # Quick trace
        tf, _ = run_traceroute(cfg["trace_host"], LOG_DIR, cfg["trace_cooldown_sec"], 0)
        if tf:
            trace_file = tf
        # Intensive mtr run (optional)
        if cfg.get("mtr_intensive_enabled", True):
            mtr_targets = list(dict.fromkeys((cfg.get("mtr_targets", [cfg["trace_host"]]) or []) + isp_targets))
            intensive_bundle = run_mtr_intensive(mtr_targets, LOG_DIR, int(cfg.get("mtr_intensive_count", 60)))
        # WAN diagnostics
        wan_diag_file = collect_wan_diagnostics(LOG_DIR)
        # Trigger analyzer (optional, with cooldown)
        analysis_file = run_analyzer_on_outage(LOG_DIR, LOGFILE, cfg)
    else:
        # Baseline MTR runs on isp_targets when OK, rate-limited by a period
        baseline_bundle = []
        if cfg.get("mtr_baseline_enabled", False) and isp_targets:
            period = int(cfg.get("mtr_baseline_period_sec", 900))
            count = int(cfg.get("mtr_baseline_count", 20))
            marker = os.path.join(LOG_DIR, "mtr_baseline_last.txt")
            last = 0
            try:
                if os.path.exists(marker):
                    last = int(open(marker, "r", encoding="utf-8").read().strip() or "0")
            except Exception:
                last = 0
            now = int(time.time())
            if now - last >= period:
                baseline_bundle = run_mtr_intensive(isp_targets, LOG_DIR, count)
                try:
                    with open(marker, "w", encoding="utf-8") as f:
                        f.write(str(now))
                except Exception:
                    pass

    # Root cause inference
    # Heuristics:
    # - DNS: http_dns_ok=0, http_ip_ok=1 (Transport ok, DNS/Name-Resolution/Hostname-Path failt)
    # - ICMP-only: targets=0, aber tcp443_ok=1 UND http_ip_ok=1 (ICMP evtl. gefiltert, Transport ok)
    # - Transport: http_ip_ok=0 UND tcp443_ok=0 (Layer3/4 Problem Upstream)
    # - Mixed: anderes Muster, nicht eindeutig
    root_cause_hint = ""
    if status == "OK":
        root_cause_hint = ""
    else:
        reachable_total = len(cfg["targets"])
        icmp_all_down = (reachable_targets == 0)
        if not http_dns_ok_flag and http_ip_ok_flag:
            root_cause_hint = "DNS"
        elif icmp_all_down and tcp443_ok_flag and http_ip_ok_flag:
            root_cause_hint = "ICMP-only"
        elif not http_ip_ok_flag and not tcp443_ok_flag:
            root_cause_hint = "Transport"
        else:
            root_cause_hint = "Mixed"

    # ISP TCP check (optional)
    isp_tcp_ok = None
    isp_tcp_ip = cfg.get("isp_tcp_ip")
    isp_tcp_port = int(cfg.get("isp_tcp_port", 443)) if cfg.get("isp_tcp_ip") else None
    if isp_tcp_ip:
        isp_tcp_ok = tcp_connect_ok(isp_tcp_ip, isp_tcp_port)

    # Build isp_detail string
    isp_detail = ";".join([f"{ip}:{'ok' if r is not None else 'down'}" for ip, r in isp_results]) if isp_results else ""

    append_row(LOGFILE, [
        ts_local.strftime('%Y-%m-%d %H:%M:%S'),
        ts_utc.isoformat(),
        round(gw_rtt*1000,2) if gw_rtt else "",
        f"{reachable_targets}/{len(cfg['targets'])}",
        int(dns_ok_flag),
        int(http_dns_ok_flag),
        int(http_ip_ok_flag),
        int(tcp443_ok_flag),
        status,
        trace_file,
        ";".join(intensive_bundle) if intensive_bundle else "",
        wan_diag_file,
        root_cause_hint,
        f"{sum(1 for _,r in isp_results if r is not None)}/{len(isp_results)}" if isp_results else "",
        (int(isp_tcp_ok) if isp_tcp_ok is not None else ""),
        ";".join(baseline_bundle) if 'baseline_bundle' in locals() and baseline_bundle else "",
        isp_detail
    ])

    isp_reach_str = f" isp={sum(1 for _,r in isp_results if r is not None)}/{len(isp_results)}" if isp_results else ""
    isp_tcp_str = f" isp_tcp={int(isp_tcp_ok)}" if isp_tcp_ok is not None else ""
    baseline_str = " baseline_mtr=yes" if 'baseline_bundle' in locals() and baseline_bundle else ""
    analysis_str = " analyzer_ran=yes" if 'analysis_file' in locals() and analysis_file else ""
    print(f"{ts_local.strftime('%H:%M:%S')} {status} gw={gw_rtt*1000 if gw_rtt else 'NA'}ms targets={reachable_targets}/{len(cfg['targets'])} dns={int(dns_ok_flag)} http_dns={int(http_dns_ok_flag)} http_ip={int(http_ip_ok_flag)} tcp443={int(tcp443_ok_flag)} root={root_cause_hint}{isp_reach_str}{isp_tcp_str}{baseline_str}{analysis_str}")

if __name__ == "__main__":
    main()