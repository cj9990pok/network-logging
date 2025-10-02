#!/usr/bin/env python3
"""
Probe TCP:443 (and optional TLS handshake) for a list of IPs.

Sources of hosts:
- --hosts "ip1,ip2,..."
- --from-config: use isp_targets + targets from config.json
- --from-candidates: use logs/isp_candidates.json suggestions

Outputs:
- Human-readable summary
- JSON report in logs/tcp_probe_<timestamp>.json
"""

import argparse
import json
import os
import socket
import ssl
import time
from typing import List, Dict

ROOT = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(ROOT, "config.json")
CANDIDATES_PATH = os.path.join(ROOT, "logs", "isp_candidates.json")
LOG_DIR = os.path.join(ROOT, "logs")


def load_config_hosts() -> List[str]:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        hosts = []
        hosts += cfg.get("isp_targets", []) or []
        hosts += cfg.get("targets", []) or []
        # de-duplicate
        return list(dict.fromkeys(hosts))
    except Exception:
        return []


def load_candidate_hosts() -> List[str]:
    try:
        with open(CANDIDATES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        sugg = data.get("suggestions", [])
        return [s.get("ip") for s in sugg if s.get("ip")]
    except Exception:
        return []


def tcp_connect(ip: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False


def tls_handshake(ip: str, port: int, timeout: float = 5.0) -> bool:
    try:
        ctx = ssl.create_default_context()
        # disable verification for IP-only probe (cert won't match IP)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((ip, port), timeout=timeout) as s:
            with ctx.wrap_socket(s, server_hostname=ip, do_handshake_on_connect=True) as ss:
                # if handshake succeeds, it's OK
                return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description="Probe TCP:443 connectivity for IPs")
    ap.add_argument("--hosts", help="Comma-separated list of IPs")
    ap.add_argument("--from-config", action="store_true", help="Include hosts from config.json (isp_targets + targets)")
    ap.add_argument("--from-candidates", action="store_true", help="Include hosts from logs/isp_candidates.json")
    ap.add_argument("--port", type=int, default=443, help="TCP port to probe (default 443)")
    ap.add_argument("--tls", action="store_true", help="Attempt TLS handshake (no cert verification)")
    args = ap.parse_args()

    hosts: List[str] = []
    if args.hosts:
        hosts += [h.strip() for h in args.hosts.split(",") if h.strip()]
    if args.from_config:
        config_hosts = load_config_hosts()
        hosts += config_hosts
        if config_hosts:
            print(f"📋 Loaded {len(config_hosts)} hosts from config.json")
    if args.from_candidates:
        candidate_hosts = load_candidate_hosts()
        hosts += candidate_hosts
        if candidate_hosts:
            print(f"📋 Loaded {len(candidate_hosts)} hosts from isp_candidates.json")
    
    # de-duplicate
    hosts = list(dict.fromkeys(hosts))

    if not hosts:
        print("⚠️ No hosts to probe!")
        print("")
        print("💡 Try one of these options:")
        print("   --hosts 1.1.1.1,8.8.8.8")
        print("   --from-config  (uses targets from config.json)")
        print("   --from-candidates  (uses ISP discovery results)")
        print("")
        print("Example: python3 probe_tcp_hosts.py --from-config --port 443 --tls")
        return 1

    print(f"🔌 Probing {len(hosts)} host(s) on port {args.port}...")
    print("")
    
    os.makedirs(LOG_DIR, exist_ok=True)
    results: Dict[str, dict] = {}
    
    for ip in hosts:
        r = {"tcp": False, "tls": None}
        print(f"  Testing {ip}...", end=" ", flush=True)
        r["tcp"] = tcp_connect(ip, args.port)
        if args.tls:
            r["tls"] = tls_handshake(ip, args.port)
        results[ip] = r
        
        # Pretty output
        tcp_status = "✓ TCP OK" if r["tcp"] else "✗ TCP Failed"
        tls_status = ""
        if args.tls:
            tls_status = " | ✓ TLS OK" if r["tls"] else " | ✗ TLS Failed"
        print(f"{tcp_status}{tls_status}")

    print("")
    ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    out_path = os.path.join(LOG_DIR, f"tcp_probe_{ts}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"port": args.port, "tls": args.tls, "results": results}, f, indent=2)
    print(f"✓ Report saved: {out_path}")
    
    # Summary
    success = sum(1 for r in results.values() if r["tcp"])
    print(f"📊 Summary: {success}/{len(hosts)} hosts reachable on port {args.port}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
