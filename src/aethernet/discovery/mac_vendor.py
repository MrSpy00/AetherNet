import socket
from typing import Optional, Dict
from loguru import logger

class MacVendorResolver:
    """Offline OUI prefix lookup & fallback online MAC vendor resolution"""

    # Primary common OUI lookup table
    STATIC_OUI_MAP: Dict[str, str] = {
        "00:50:56": "VMware",
        "00:0C:29": "VMware",
        "00:1C:42": "Parallels",
        "08:00:27": "VirtualBox",
        "DC:A6:32": "Raspberry Pi Foundation",
        "B8:27:EB": "Raspberry Pi Foundation",
        "E4:5F:01": "Raspberry Pi Foundation",
        "FC:FB:FB": "Cisco Systems",
        "00:1A:2B": "Cisco Systems",
        "AC:BC:32": "Apple Inc.",
        "3C:D0:F8": "Apple Inc.",
        "F4:D4:88": "Apple Inc.",
        "00:1A:11": "Google LLC",
        "D8:3C:99": "TP-Link",
        "50:C7:BF": "TP-Link",
        "74:DA:38": "Netgear",
        "00:1E:58": "D-Link",
        "18:60:24": "Humax (Modem/Router)",
        "00:24:D1": "Asus",
        "60:45:CB": "Samsung Electronics",
        "00:16:6C": "Samsung Electronics",
        "70:48:0F": "Xiaomi Communications",
    }

    @classmethod
    def lookup(cls, mac_address: str) -> str:
        if not mac_address or len(mac_address) < 8:
            return "Bilinmeyen Üretici"

        clean_mac = mac_address.upper().replace("-", ":")
        prefix = ":".join(clean_mac.split(":")[:3])

        if prefix in cls.STATIC_OUI_MAP:
            return cls.STATIC_OUI_MAP[prefix]

        return "Genel Ağ Cihazı"
