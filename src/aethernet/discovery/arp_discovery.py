import subprocess
import re
import socket
from typing import List
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from aethernet.core.models import DiscoveredDevice
from aethernet.discovery.mac_vendor import MacVendorResolver

class ArpDiscovery:
    """ARP tablosu ayrıştırıcısı ve aktif IP yerel ağ tarayıcısı"""

    @staticmethod
    def get_arp_table() -> List[DiscoveredDevice]:
        devices: List[DiscoveredDevice] = []
        try:
            res = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            output = res.stdout

            # Parse lines matching IP and MAC
            lines = output.splitlines()
            for line in lines:
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})\s+(\w+)", line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).replace("-", ":").upper()
                    entry_type = match.group(3)

                    # Ignore multicast / broadcast addresses
                    if ip.startswith("224.") or ip.startswith("239.") or ip.endswith(".255") or mac == "FF:FF:FF:FF:FF:FF":
                        continue

                    vendor = MacVendorResolver.lookup(mac)
                    devices.append(
                        DiscoveredDevice(
                            ip=ip,
                            mac=mac,
                            vendor=vendor,
                            device_type=ArpDiscovery._estimate_device_type(vendor, ip)
                        )
                    )
        except Exception as e:
            logger.error(f"ARP table retrieval error: {e}")

        return devices

    @staticmethod
    def _estimate_device_type(vendor: str, ip: str) -> str:
        v_lower = vendor.lower()
        if ip.endswith(".1"):
            return "Router / Ağ Geçidi"
        if "apple" in v_lower or "samsung" in v_lower or "xiaomi" in v_lower:
            return "Mobil Cihaz / Akıllı Telefon"
        if "raspberry" in v_lower or "tp-link" in v_lower or "humax" in v_lower:
            return "IoT / Ağ Cihazı"
        if "vmware" in v_lower or "virtualbox" in v_lower:
            return "Sanal Makine"
        return "Bilgisayar / Ağ Üyesi"
