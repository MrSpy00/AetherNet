import requests
from typing import Optional, Dict
from loguru import logger

class MacVendorResolver:
    """Multi-Provider MAC Vendor Resolver with Offline OUI & Online API Fallbacks"""

    CACHE: Dict[str, str] = {}

    STATIC_OUI_MAP: Dict[str, str] = {
        "00:50:56": "VMware Inc.",
        "00:0C:29": "VMware Inc.",
        "00:1C:42": "Parallels Desktop",
        "08:00:27": "Oracle VirtualBox",
        "DC:A6:32": "Raspberry Pi Trading Ltd",
        "B8:27:EB": "Raspberry Pi Foundation",
        "E4:5F:01": "Raspberry Pi Trading Ltd",
        "FC:FB:FB": "Cisco Systems",
        "00:1A:2B": "Cisco Systems",
        "00:07:0E": "Cisco Systems",
        "AC:BC:32": "Apple Inc.",
        "3C:D0:F8": "Apple Inc.",
        "F4:D4:88": "Apple Inc.",
        "A4:83:E7": "Apple Inc.",
        "00:1A:11": "Google LLC",
        "3C:5A:B4": "Google LLC",
        "D8:3C:99": "TP-Link Technologies",
        "50:C7:BF": "TP-Link Technologies",
        "C0:25:E9": "TP-Link Technologies",
        "74:DA:38": "Netgear Inc.",
        "28:80:88": "Netgear Inc.",
        "00:1E:58": "D-Link Corporation",
        "18:60:24": "Humax (Router/STB)",
        "00:24:D1": "ASUSTeK Computer Inc.",
        "04:D4:C4": "ASUSTeK Computer Inc.",
        "60:45:CB": "Samsung Electronics",
        "00:16:6C": "Samsung Electronics",
        "70:48:0F": "Xiaomi Communications",
        "64:09:80": "Xiaomi Communications",
        "98:DA:C4": "Intel Corporation",
        "00:1B:21": "Intel Corporation",
        "00:23:24": "GIGA-BYTE Technology",
        "00:1D:7D": "GIGA-BYTE Technology",
        "E0:D5:5E": "Realtek Semiconductor",
        "00:E0:4C": "Realtek Semiconductor",
        "74:83:C2": "Ubiquiti Networks",
        "18:E8:29": "Ubiquiti Networks",
        "B4:FB:E4": "Ubiquiti Networks",
        "64:D1:54": "MikroTik (RouterBOARD)",
        "48:8E:42": "MikroTik (RouterBOARD)",
        "00:0C:42": "MikroTik (RouterBOARD)",
        "00:E0:FC": "Huawei Technologies",
        "F8:4A:BF": "Huawei Technologies",
        "88:E3:AB": "Huawei Technologies",
        "34:4B:50": "ZTE Corporation",
        "70:9F:2D": "ZTE Corporation",
        "18:20:12": "Dell Inc.",
        "00:14:22": "Dell Inc.",
        "00:1C:25": "HP Inc. / Hewlett-Packard",
        "3C:D9:2B": "HP Inc. / Hewlett-Packard",
        "A4:4C:C8": "Lenovo Mobile / PC",
        "FC:F8:AE": "Amazon Technologies",
        "68:54:5A": "Amazon Technologies",
        "00:04:76": "3Com Corporation",
        "00:13:E8": "Intel Corporate",
        "60:66:82": "TP-Link Corporation",
        "C0:C9:E3": "TP-Link Corporation",
        "00:11:32": "Synology Inc.",
        "28:6B:35": "Apple Inc.",
        "D4:6E:0E": "TP-Link Technologies",
        "00:1F:D0": "GIGA-BYTE Technology",
        "AC:84:C6": "TP-Link Technologies",
        "04:42:1A": "Android / OEM Device",
        "84:16:F9": "TP-Link Technologies",
        "54:AF:97": "Shenzhen Bilian Electronic",
        "78:8C:B5": "Ubiquiti Networks",
        "DC:9B:9C": "Huawei Technologies",
        "10:7B:44": "Xiaomi Communications"
    }


    @classmethod
    def lookup(cls, mac_address: str) -> str:
        if not mac_address or len(mac_address) < 8:
            return "Bilinmeyen Üretici"

        clean_mac = mac_address.upper().replace("-", ":").strip()
        prefix = ":".join(clean_mac.split(":")[:3])

        # Step 1: Check In-Memory Cache
        if prefix in cls.CACHE:
            return cls.CACHE[prefix]

        # Step 2: Check Static OUI Map
        if prefix in cls.STATIC_OUI_MAP:
            vendor = cls.STATIC_OUI_MAP[prefix]
            cls.CACHE[prefix] = vendor
            return vendor

        # Step 3: Provider 1 - maclookup.app API (Faster & Higher Rate Limits)
        try:
            url = f"https://api.maclookup.app/v2/macs/{clean_mac}"
            res = requests.get(url, timeout=2.0)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, dict):
                    vendor = data.get("company", "")
                    if vendor and isinstance(vendor, str):
                        cls.CACHE[prefix] = vendor
                        return vendor
        except Exception as e:
            logger.debug(f"maclookup.app failed: {e}")

        # Step 4: Provider 2 - api.macvendors.com
        try:
            url = f"https://api.macvendors.com/{clean_mac}"
            res = requests.get(url, timeout=2.0)
            if res.status_code == 200 and res.text:
                vendor = res.text.strip()
                if vendor and isinstance(vendor, str):
                    cls.CACHE[prefix] = vendor
                    return vendor
            elif res.status_code == 429:
                logger.debug(f"macvendors.com rate-limited (429) for {clean_mac}")
        except Exception as e:
            logger.debug(f"macvendors.com failed: {e}")

        # Default fallback
        fallback_vendor = "Genel Ağ Cihazı"
        cls.CACHE[prefix] = fallback_vendor
        return fallback_vendor

