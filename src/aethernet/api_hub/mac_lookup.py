import logging
from typing import Optional
from aethernet.api_hub.models import MacVendorResult
from aethernet.api_hub.client import APIHttpClient

logger = logging.getLogger(__name__)

class MacLookupEngine:
    """Multi-provider MAC Address Vendor Resolver using free online APIs."""

    def __init__(self, client: Optional[APIHttpClient] = None):
        self.client = client or APIHttpClient()

    def lookup(self, mac_address: str) -> MacVendorResult:
        """Resolves MAC vendor using online fallback APIs."""
        clean_mac = mac_address.upper().replace("-", ":").strip()
        
        # Provider 1: macvendors.co
        res = self._lookup_macvendors_co(clean_mac)
        if res and res.vendor != "Bilinmeyen Üretici":
            return res

        # Provider 2: api.macvendors.com
        res = self._lookup_macvendors_com(clean_mac)
        if res and res.vendor != "Bilinmeyen Üretici":
            return res

        return MacVendorResult(mac=clean_mac, vendor="Bilinmeyen Üretici", source="Online API")

    def _lookup_macvendors_co(self, mac: str) -> Optional[MacVendorResult]:
        url = f"https://macvendors.co/api/{mac}"
        data, status, _ = self.client.get_json(url, rate_limit_pm=30)
        if status == 200 and data and "result" in data:
            result = data["result"]
            vendor = result.get("company", "Bilinmeyen Üretici")
            addr = result.get("address", "")
            country = result.get("country", "")
            return MacVendorResult(mac=mac, vendor=vendor, address=addr, country=country, source="macvendors.co")
        return None

    def _lookup_macvendors_com(self, mac: str) -> Optional[MacVendorResult]:
        url = f"https://api.macvendors.com/{mac}"
        data, status, _ = self.client.get_json(url, rate_limit_pm=30)
        if status == 200 and data:
            if isinstance(data, str):
                return MacVendorResult(mac=mac, vendor=data.strip(), source="macvendors.com")
            elif isinstance(data, dict) and "raw" in data:
                return MacVendorResult(mac=mac, vendor=data["raw"].strip(), source="macvendors.com")
        return None
