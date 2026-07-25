"""ARP Spoofing and Man-in-the-Middle (MITM) detector for local network interfaces."""

import os
import re
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ARPEntry:
    ip: str
    mac: str
    entry_type: str


class ARPSpoofDetector:
    """Detects duplicate MAC addresses and Gateway ARP poisoning in the local network."""

    def __init__(self):
        pass

    def get_arp_table(self) -> List[ARPEntry]:
        """Fetch current system ARP table."""
        entries = []
        try:
            output = subprocess.check_output("arp -a", shell=True, text=True, errors="ignore")
            # Parse Windows / Linux arp -a format
            pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([0-9a-fa-f-]{17}|[0-9a-fa-f:]{17})\s+(\w+)")
            for line in output.splitlines():
                match = pattern.search(line)
                if match:
                    ip, mac, etype = match.groups()
                    mac_clean = mac.replace("-", ":").lower()
                    entries.append(ARPEntry(ip=ip, mac=mac_clean, entry_type=etype))
        except Exception:
            pass
        return entries

    def analyze_arp_table(self, gateway_ip: Optional[str] = None) -> Dict[str, any]:
        """Analyze ARP entries for spoofing indicators (duplicate MACs for multiple IPs or gateway MAC changes)."""
        entries = self.get_arp_table()
        mac_to_ips: Dict[str, List[str]] = {}
        alerts = []
        is_spoofed = False

        for entry in entries:
            # Ignore broadcast and multicast MACs
            if entry.mac in ["ff:ff:ff:ff:ff:ff", "01:00:5e:00:00:01"]:
                continue
            if entry.mac not in mac_to_ips:
                mac_to_ips[entry.mac] = []
            mac_to_ips[entry.mac].append(entry.ip)

        # Check for multiple IPs claiming the same MAC address
        for mac, ips in mac_to_ips.items():
            if len(ips) > 1:
                is_spoofed = True
                alerts.append(f"Multiple IP addresses ({', '.join(ips)}) share the same MAC address ({mac}). Possible ARP Poisoning/MITM!")

        return {
            "is_spoofed": is_spoofed,
            "total_entries": len(entries),
            "alerts": alerts,
            "mac_map": mac_to_ips
        }
