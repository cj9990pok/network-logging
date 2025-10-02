#!/usr/bin/env python3

"""
Analyze netlog.csv produced by netLogging.py and summarize outages.

Features:
- Parse CSV and group consecutive non-OK rows into outages
- Compute duration, counts, avg/min/max gateway_ms during outages
- Parse referenced trace files (mtr/traceroute) to extract first-hop stats
- Provide simple availability and hour-of-day breakdown

Usage:
  ./bin/python analyze_netlog.py  # when run from the project directory with venv
"""

from __future__ import annotations

import csv
import dataclasses as dc
import datetime as dt
import json
import os
import re
import statistics as stats
from typing import List, Optional, Tuple

ROOT = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(ROOT, "config.json")
DEFAULT_LOG_DIR = os.path.join(ROOT, "logs")
CSV_PATH = os.path.join(DEFAULT_LOG_DIR, "netlog.csv")


def load_config_log_dir() -> str:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg.get("log_dir", DEFAULT_LOG_DIR)
    except Exception:
        return DEFAULT_LOG_DIR


@dc.dataclass
class Row:
    local_ts: dt.datetime
    utc_ts: dt.datetime
    gateway_ms: Optional[float]
    targets_reachable: Tuple[int, int]
    dns_ok: bool
    http_ok: bool
    status: str
    trace_file: str
    root_cause_hint: str = ""
    isp_reachable: Optional[Tuple[int, int]] = None
    isp_detail: dict | None = None


def parse_targets_reachable(s: str) -> Tuple[int, int]:
    try:
        a, b = s.split("/")
        return int(a), int(b)
    except Exception:
        return (0, 0)


def read_rows(csv_path: str) -> List[Row]:
    rows: List[Row] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for d in r:
            try:
                local_ts = dt.datetime.strptime(d["local_timestamp"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                # Fallback if formatting differs
                local_ts = dt.datetime.fromisoformat(d["local_timestamp"]) if d.get("local_timestamp") else None
            utc_ts = dt.datetime.fromisoformat(d["utc_timestamp"]) if d.get("utc_timestamp") else None
            g_ms = None
            g_raw = d.get("gateway_ms")
            if g_raw:
                try:
                    g_ms = float(g_raw)
                except Exception:
                    g_ms = None
            tr = parse_targets_reachable(d.get("targets_reachable", "0/0"))
            # Parse isp_reachable if present, format like "1/2"
            isp_r = None
            s = d.get("isp_reachable")
            if s and "/" in s:
                try:
                    a, b = s.split("/")
                    isp_r = (int(a), int(b))
                except Exception:
                    isp_r = None

            # Parse isp_detail like "ip1:ok;ip2:down"
            isp_detail = None
            dstr = d.get("isp_detail", "")
            if dstr:
                try:
                    parts = [p for p in dstr.split(";") if p]
                    isp_detail = {}
                    for p in parts:
                        ip, state = p.split(":", 1)
                        isp_detail[ip] = state
                except Exception:
                    isp_detail = None

            rows.append(
                Row(
                    local_ts=local_ts or utc_ts,
                    utc_ts=utc_ts or local_ts,
                    gateway_ms=g_ms,
                    targets_reachable=tr,
                    dns_ok=d.get("dns_ok") in ("1", "True", "true"),
                    http_ok=d.get("http_ok") in ("1", "True", "true"),
                    status=d.get("overall_status", ""),
                    trace_file=d.get("trace_file", "").strip(),
                    root_cause_hint=d.get("root_cause_hint", "").strip(),
                    isp_reachable=isp_r,
                    isp_detail=isp_detail,
                )
            )
    return rows


@dc.dataclass
class Outage:
    start: dt.datetime
    end: dt.datetime
    reason_status: str
    rows: List[Row]

    @property
    def duration(self) -> dt.timedelta:
        return (self.end - self.start) if self.end and self.start else dt.timedelta(0)

    @property
    def gw_stats(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        vals = [r.gateway_ms for r in self.rows if r.gateway_ms is not None]
        if not vals:
            return (None, None, None)
        return (min(vals), stats.mean(vals), max(vals))

    @property
    def reachability(self) -> Tuple[int, int]:
        # average reachable/total across rows
        total = [r.targets_reachable[1] for r in self.rows if r.targets_reachable[1] > 0]
        good = [r.targets_reachable[0] for r in self.rows if r.targets_reachable[1] > 0]
        if not total:
            return (0, 0)
        return (round(stats.mean(good)), round(stats.mean(total)))


def group_outages(rows: List[Row]) -> Tuple[List[Outage], float]:
    outages: List[Outage] = []
    cur: Optional[Outage] = None
    total_rows = len(rows)
    ok_rows = 0
    for r in rows:
        if r.status == "OK":
            ok_rows += 1
            if cur:
                cur.end = r.local_ts
                outages.append(cur)
                cur = None
        else:
            if cur is None:
                cur = Outage(start=r.local_ts, end=r.local_ts, reason_status=r.status, rows=[r])
            else:
                cur.rows.append(r)
                cur.end = r.local_ts
    if cur:
        outages.append(cur)

    availability = ok_rows / total_rows if total_rows else 1.0
    return outages, availability


FIRST_HOP_RE = re.compile(r"^\s*1\.\|--\s+(?P<ip>\S+)\s+(?P<loss>\d+\.\d+)%\s+\S+\s+(?P<last>\d+\.\d+)\s+(?P<avg>\d+\.\d+)\s+(?P<best>\d+\.\d+)\s+(?P<worst>\d+\.\d+)\s+(?P<stdev>\d+\.\d+)")


def parse_mtr_first_hop(text: str) -> Optional[dict]:
    for line in text.splitlines():
        m = FIRST_HOP_RE.match(line)
        if m:
            d = m.groupdict()
            d["loss"] = float(d["loss"])  # percent
            for k in ("last", "avg", "best", "worst", "stdev"):
                d[k] = float(d[k])
            return d
    return None


def load_trace_first_hop(log_dir: str, filename: str) -> Optional[dict]:
    if not filename:
        return None
    path = filename
    if not os.path.isabs(path):
        path = os.path.join(log_dir, filename)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        fh = parse_mtr_first_hop(txt)
        if fh:
            return fh
        # Fallback: try to extract hop 1 ip from traceroute output
        for line in txt.splitlines():
            # e.g., " 1  192.168.2.1  0.6 ms"
            line = line.strip()
            if line.startswith("1 ") or line.startswith("1."):
                return {"ip": line.split()[1], "note": "parsed from traceroute"}
    except Exception:
        return None
    return None


def breakdown_by_hour(rows: List[Row]):
    by_hour = {h: {"total": 0, "non_ok": 0} for h in range(24)}
    for r in rows:
        h = r.local_ts.hour
        by_hour[h]["total"] += 1
        if r.status != "OK":
            by_hour[h]["non_ok"] += 1
    return by_hour


def main():
    import argparse
    p = argparse.ArgumentParser(description="Analyze netlog.csv and summarize outages")
    p.add_argument("--csv", dest="csv_path", help="Path to netlog.csv (overrides config)")
    p.add_argument("--log-dir", dest="log_dir", help="Directory containing netlog.csv and traces")
    args = p.parse_args()

    log_dir = args.log_dir or load_config_log_dir()
    csv_path = args.csv_path or os.path.join(log_dir, "netlog.csv")
    # Fallback if configured path doesn't exist in this environment
    if not os.path.exists(csv_path):
        fallback = os.path.join(DEFAULT_LOG_DIR, "netlog.csv")
        if os.path.exists(fallback):
            print(f"CSV not found at {csv_path}, using fallback {fallback}")
            csv_path = fallback
            log_dir = DEFAULT_LOG_DIR
        else:
            print(f"CSV not found: {csv_path}")
            return 2
    rows = read_rows(csv_path)
    if not rows:
        print("CSV is empty")
        return 0
    outages, availability = group_outages(rows)

    print("=== Netlog Summary ===")
    print(f"Rows: {len(rows)}  Availability (by row count): {availability*100:.2f}%")

    # Hourly breakdown
    by_hour = breakdown_by_hour(rows)
    worst_hours = sorted(by_hour.items(), key=lambda kv: (kv[1]["non_ok"], kv[1]["total"]), reverse=True)[:3]
    print("\nTop hours by non-OK counts:")
    for h, d in worst_hours:
        rate = (d["non_ok"] / d["total"] * 100) if d["total"] else 0
        print(f"  {h:02d}:00 - {h:02d}:59  non-OK {d['non_ok']}/{d['total']} ({rate:.1f}%)")

    if not outages:
        print("\nNo outages detected.")
        # Even without outages, we can show ISP-down ranking and heatmap if any rows exist
        # ISP down ranking across all rows
        isp_down_counts = {}
        isp_seen_counts = {}
        for r in rows:
            if r.isp_detail:
                for ip, state in r.isp_detail.items():
                    isp_seen_counts[ip] = isp_seen_counts.get(ip, 0) + 1
                    if state == "down":
                        isp_down_counts[ip] = isp_down_counts.get(ip, 0) + 1
        if isp_seen_counts:
            print("\nISP target down ranking (all rows):")
            for ip, seen in sorted(isp_seen_counts.items(), key=lambda kv: (isp_down_counts.get(kv[0],0), kv[1]), reverse=True):
                d = isp_down_counts.get(ip, 0)
                rate = d/seen*100
                print(f"  {ip}: down {d}/{seen} ({rate:.1f}%)")

        # Heatmap for hours where any ISP target was down
        isp_heatmap = {h: 0 for h in range(24)}
        for r in rows:
            if r.isp_detail and any(v == "down" for v in r.isp_detail.values()):
                isp_heatmap[r.local_ts.hour] += 1
        if any(isp_heatmap.values()):
            print("\nHours with ISP target down events:")
            for h in range(24):
                if isp_heatmap[h]:
                    print(f"  {h:02d}:00 - {h:02d}:59  {isp_heatmap[h]} events")
        return 0

    print("\n=== Outages ===")
    outage_causes = []  # (cause, duration)
    isp_impact_rows = {"partial": 0, "down": 0, "total_non_ok": 0}
    hop_issue_counter = {}
    for i, o in enumerate(outages, 1):
        gw_min, gw_avg, gw_max = o.gw_stats
        reach_g, reach_t = o.reachability
        # Try to load first trace in that episode
        first_trace = next((r.trace_file for r in o.rows if r.trace_file), "")
        first_hop = load_trace_first_hop(log_dir, first_trace) if first_trace else None
        print(f"#{i} {o.start} -> {o.end}  dur={o.duration}  status={o.reason_status}")
        print(f"   reach: ~{reach_g}/{reach_t} targets; gateway_ms min/avg/max: {gw_min} / {gw_avg} / {gw_max}")
        if first_trace:
            if first_hop:
                extra = f" loss={first_hop.get('loss','?')}% avg={first_hop.get('avg','?')}ms" if 'loss' in first_hop else ""
                print(f"   trace: {first_trace}  hop1 {first_hop.get('ip','?')}{extra}")
            else:
                print(f"   trace: {first_trace} (could not parse)")

        # Determine outage-level cause by majority vote over rows (ignore empty)
        hints = [r.root_cause_hint for r in o.rows if r.root_cause_hint]
        if hints:
            # Majority cause; tie -> Mixed
            from collections import Counter
            cnt = Counter(hints)
            cause, n = cnt.most_common(1)[0]
            # If tie between multiple top categories, set Mixed
            tops = [k for k, v in cnt.items() if v == n]
            cause = cause if len(tops) == 1 else "Mixed"
        else:
            cause = "Mixed" if o.reason_status != "OK" else ""
        outage_causes.append((cause, o.duration))

        # ISP impact within this outage: any row with isp_reachable < full
        for r in o.rows:
            if r.status != "OK" and r.isp_reachable:
                a, b = r.isp_reachable
                isp_impact_rows["total_non_ok"] += 1
                if b > 0:
                    if a == 0:
                        isp_impact_rows["down"] += 1
                    elif a < b:
                        isp_impact_rows["partial"] += 1

        # Hop-level hints from mtr/traceroute logs: count recurring first hop beyond local router
        # Note: We only look at first_hop parsed from mtr summary here
        # Skip private network IPs (192.168.x.x, 10.x.x.x, 172.16-31.x.x) and unknown hops
        if first_hop and "ip" in first_hop:
            hop_ip = first_hop["ip"]
            # Skip if it's a private IP or unknown
            if not (hop_ip.startswith("192.168.") or hop_ip.startswith("10.") or 
                    hop_ip.startswith("172.16.") or hop_ip.startswith("172.17.") or
                    hop_ip.startswith("172.18.") or hop_ip.startswith("172.19.") or
                    hop_ip.startswith("172.20.") or hop_ip.startswith("172.21.") or
                    hop_ip.startswith("172.22.") or hop_ip.startswith("172.23.") or
                    hop_ip.startswith("172.24.") or hop_ip.startswith("172.25.") or
                    hop_ip.startswith("172.26.") or hop_ip.startswith("172.27.") or
                    hop_ip.startswith("172.28.") or hop_ip.startswith("172.29.") or
                    hop_ip.startswith("172.30.") or hop_ip.startswith("172.31.") or
                    hop_ip == "???"):
                hop_issue_counter[hop_ip] = hop_issue_counter.get(hop_ip, 0) + 1

    # Root-cause summary
    cause_counts = {"DNS": 0, "ICMP-only": 0, "Transport": 0, "Mixed": 0, "": 0}
    for r in rows:
        if r.status != "OK":
            cause_counts[r.root_cause_hint] = cause_counts.get(r.root_cause_hint, 0) + 1
    print("\nRoot-cause counts (non-OK rows):")
    for k in ("DNS", "ICMP-only", "Transport", "Mixed"):
        print(f"  {k:11s}: {cause_counts.get(k,0)}")

    # Hour x RootCause heatmap for non-OK rows
    heatmap = {h: {"DNS": 0, "ICMP-only": 0, "Transport": 0, "Mixed": 0} for h in range(24)}
    for r in rows:
        if r.status != "OK":
            h = r.local_ts.hour
            key = r.root_cause_hint if r.root_cause_hint in heatmap[h] else "Mixed"
            heatmap[h][key] += 1
    print("\nNon-OK heatmap by hour and root cause:")
    print("  Hour  DNS  ICMP  Trans  Mixed  Total")
    for h in range(24):
        row = heatmap[h]
        total = sum(row.values())
        if total == 0:
            continue
        print(f"  {h:02d}    {row['DNS']:3d}   {row['ICMP-only']:4d}   {row['Transport']:5d}   {row['Mixed']:5d}   {total:5d}")

    # Summary by root cause across outages
    from collections import defaultdict
    cause_summary = defaultdict(lambda: {"count": 0, "total": dt.timedelta(0)})
    for cause, dur in outage_causes:
        if cause:
            cause_summary[cause]["count"] += 1
            cause_summary[cause]["total"] += dur
    if cause_summary:
        print("\nOutage summary by root cause:")
        for cause in ("DNS", "ICMP-only", "Transport", "Mixed"):
            if cause in cause_summary:
                total = cause_summary[cause]["total"]
                count = cause_summary[cause]["count"]
                avg = total / count if count else dt.timedelta(0)
                print(f"  {cause:11s}: {count} outages, total {total}, avg {avg}")

    # ISP impact summary across non-OK rows
    if isp_impact_rows["total_non_ok"]:
        total = isp_impact_rows["total_non_ok"]
        p_partial = isp_impact_rows["partial"] / total * 100
        p_down = isp_impact_rows["down"] / total * 100
        print(f"\nISP impact summary (non-OK rows with isp_targets): partial {isp_impact_rows['partial']} ({p_partial:.1f}%), down {isp_impact_rows['down']} ({p_down:.1f}%), total {total}")

    # Hop-level recurring hints
    if hop_issue_counter:
        print("\nRecurring first-hop issues beyond router (count across outages):")
        for ip, n in sorted(hop_issue_counter.items(), key=lambda kv: kv[1], reverse=True):
            print(f"  {ip}: {n}")

    # ISP target down ranking restricted to outage rows
    isp_down_counts = {}
    isp_seen_counts = {}
    for o in outages:
        for r in o.rows:
            if r.isp_detail:
                for ip, state in r.isp_detail.items():
                    isp_seen_counts[ip] = isp_seen_counts.get(ip, 0) + 1
                    if state == "down":
                        isp_down_counts[ip] = isp_down_counts.get(ip, 0) + 1
    if isp_seen_counts:
        print("\nISP target down ranking (outage rows):")
        for ip, seen in sorted(isp_seen_counts.items(), key=lambda kv: (isp_down_counts.get(kv[0],0), kv[1]), reverse=True):
            d = isp_down_counts.get(ip, 0)
            rate = d/seen*100
            print(f"  {ip}: down {d}/{seen} ({rate:.1f}%)")

    # Heatmap for hours where any ISP target was down in outages
    isp_heatmap = {h: 0 for h in range(24)}
    for o in outages:
        for r in o.rows:
            if r.isp_detail and any(v == "down" for v in r.isp_detail.values()):
                isp_heatmap[r.local_ts.hour] += 1
    if any(isp_heatmap.values()):
        print("\nHours with ISP target down events (outages):")
        for h in range(24):
            if isp_heatmap[h]:
                print(f"  {h:02d}:00 - {h:02d}:59  {isp_heatmap[h]} events")

    # High-level hypothesis
    gw_ok_when_down = [o for o in outages if (o.gw_stats[1] is not None and o.gw_stats[1] < 5.0)]
    if gw_ok_when_down:
        print("\nHypothesis: Local LAN and router are fine (low gateway latency during outages). Issue likely upstream (ISP/last mile or peering).")
    else:
        print("\nHypothesis: Gateway latency missing/high during outages. Could indicate LAN/router issues.")

    print("\nNext steps suggestions:")
    print("- Add a TCP connectivity check (e.g., TLS connect to 1.1.1.1:443) to distinguish ICMP filtering from real packet loss.")
    print("- Add an HTTP GET to an IP-only endpoint (e.g., https://1.1.1.1) to bypass DNS and separate DNS from transport.")
    print("- Run 'mtr -rwzc 20 1.1.1.1' during an outage to see where loss starts; consider longer samples (60-120 seconds).")
    print("- Log WAN interface state around outages: 'ip addr', 'ip -s link', 'dmesg | grep -i eth|enp', 'journalctl -u NetworkManager -r --since \"5 min ago\"'.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
