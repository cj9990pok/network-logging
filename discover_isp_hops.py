#!/usr/bin/env python3
"""
Discover likely ISP next-hop IPs near your router using traceroute and mtr.

This script runs lightweight probes to common stable targets (1.1.1.1, 8.8.8.8),
parses early hops (2..5), and suggests candidate ISP targets that are stable
and responsive. Use the suggestions to populate `isp_targets` in config.json.

It is safe to run when the internet works; it does not depend on an outage.

Outputs:
- A summary of early hops across multiple runs
- A short list of suggested ISP hop IPs
- Optional: writes a JSON file with suggestions for later reference
"""

import subprocess
import time
import os
import json
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(__file__)
SUGGEST_PATH = os.path.join(ROOT, "logs", "isp_candidates.json")
TARGETS = ["1.1.1.1", "8.8.8.8"]
RUNS_PER_TARGET = 6
HOP_RANGE = range(2, 10)  # consider hops 1..9 as ISP vicinity

TR_RE = re.compile(r"^\s*(?P<hop>\d+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)")


def run_traceroute(target: str, timeout: int = 25) -> str:
    try:
        out = subprocess.check_output(["traceroute", "-n", target], text=True, timeout=timeout, errors="ignore")
        return out
    except Exception as e:
        return f"TRACE_FAILED {target}: {e}"


def parse_early_hops(text: str):
    hops = {}
    for line in text.splitlines():
        m = TR_RE.match(line.strip())
        if not m:
            continue
        hop = int(m.group("hop"))
        ip = m.group("ip")
        hops[hop] = ip
    return {h: hops[h] for h in sorted(hops) if h in HOP_RANGE}


def main():
    os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
    seen = defaultdict(Counter)  # hop -> Counter(ip)

    for t in TARGETS:
        for i in range(RUNS_PER_TARGET):
            txt = run_traceroute(t)
            hops = parse_early_hops(txt)
            for h, ip in hops.items():
                seen[h][ip] += 1
            time.sleep(1)

    suggestions = []
    for hop in sorted(seen):
        cnt = seen[hop]
        if not cnt:
            continue
        ip, n = cnt.most_common(1)[0]
        # Heuristic: seen in at least half the probes
        if n >= max(1, RUNS_PER_TARGET // 2):
            suggestions.append({"hop": hop, "ip": ip, "seen": n})

    print("Early hop observations (IP: count):")
    for hop in sorted(seen):
        entries = ", ".join([f"{ip}:{n}" for ip, n in seen[hop].most_common()])
        if entries:
            print(f"  hop {hop}: {entries}")

    if suggestions:
        print("\nSuggested isp_targets (consider adding to config.json):")
        for s in suggestions:
            print(f"  hop {s['hop']}: {s['ip']} (seen {s['seen']})")
    else:
        print("\nNo stable early-hop IPs observed. Try increasing RUNS_PER_TARGET or using mtr.")

    # Save to JSON for reference
    with open(SUGGEST_PATH, "w", encoding="utf-8") as f:
        json.dump({"seen": {str(k): dict(v) for k, v in seen.items()}, "suggestions": suggestions}, f, indent=2)
    print(f"\nWrote suggestions to {SUGGEST_PATH}")


if __name__ == "__main__":
    main()
