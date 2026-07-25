import logging
from typing import Optional, Dict, Any
from aethernet.api_hub.models import IPIntelligence
from aethernet.api_hub.client import APIHttpClient

logger = logging.getLogger(__name__)

class IPIntelligenceEngine:
    """Multi-provider IP Geolocation & Network Intelligence Engine with Automatic Failover."""

    def __init__(self, client: Optional[APIHttpClient] = None):
        self.client = client or APIHttpClient()

    def get_public_ip(self) -> Optional[str]:
        """Discovers host public IP address using failover public endpoints."""
        endpoints = [
            "https://api.ipify.org?format=json",
            "http://ip-api.com/json/",
            "https://api.ip2location.io/",
        ]
        for url in endpoints:
            data, status, _ = self.client.get_json(url, rate_limit_pm=30, timeout=5)
            if status == 200 and data:
                if "ip" in data:
                    return data["ip"]
                elif "query" in data:
                    return data["query"]
        return None

    def lookup_ip(self, ip: Optional[str] = None) -> IPIntelligence:
        """
        Queries IP intelligence (location, ISP, ASN, security flags) with failover mechanism.
        If ip is None or empty, resolves caller's public IP first.
        """
        target_ip = ip.strip() if ip else ""
        if not target_ip or target_ip.lower() == "myip":
            discovered = self.get_public_ip()
            if discovered:
                target_ip = discovered
            else:
                return IPIntelligence(ip="127.0.0.1", country="Yerel Ağ", isp="Loopback")

        # 1. Primary Provider: IP-API.com
        res = self._query_ip_api_com(target_ip)
        if res:
            return res

        # 2. Secondary Provider: DB-IP.com
        res = self._query_db_ip(target_ip)
        if res:
            return res

        # 3. Tertiary Provider: IP2Location.io
        res = self._query_ip2location(target_ip)
        if res:
            return res

        # Fallback default if all external APIs fail
        return IPIntelligence(ip=target_ip, country="Bilinmiyor", provider="None")

    def _query_ip_api_com(self, ip: str) -> Optional[IPIntelligence]:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting,query"
        data, status, _ = self.client.get_json(url, rate_limit_pm=45)
        if status == 200 and data and data.get("status") == "success":
            return IPIntelligence(
                ip=data.get("query", ip),
                country=data.get("country", "Bilinmiyor"),
                country_code=data.get("countryCode", ""),
                region=data.get("regionName", ""),
                city=data.get("city", ""),
                zip_code=data.get("zip", ""),
                latitude=float(data.get("lat", 0.0)),
                longitude=float(data.get("lon", 0.0)),
                timezone=data.get("timezone", ""),
                isp=data.get("isp", "Bilinmiyor"),
                org=data.get("org", ""),
                asn=data.get("as", ""),
                is_proxy=bool(data.get("proxy", False)),
                is_hosting=bool(data.get("hosting", False)),
                provider="ip-api.com",
                raw_data=data
            )
        return None

    def _query_db_ip(self, ip: str) -> Optional[IPIntelligence]:
        url = f"https://api.db-ip.com/v2/free/{ip}"
        data, status, _ = self.client.get_json(url, rate_limit_pm=30)
        if status == 200 and data and "ipAddress" in data:
            return IPIntelligence(
                ip=data.get("ipAddress", ip),
                country=data.get("countryName", "Bilinmiyor"),
                country_code=data.get("countryCode", ""),
                city=data.get("city", ""),
                isp=data.get("isp", "Bilinmiyor"),
                provider="db-ip.com",
                raw_data=data
            )
        return None

    def _query_ip2location(self, ip: str) -> Optional[IPIntelligence]:
        url = f"https://api.ip2location.io/?ip={ip}"
        data, status, _ = self.client.get_json(url, rate_limit_pm=30)
        if status == 200 and data and "ip" in data:
            return IPIntelligence(
                ip=data.get("ip", ip),
                country=data.get("country_name", "Bilinmiyor"),
                country_code=data.get("country_code", ""),
                region=data.get("region_name", ""),
                city=data.get("city_name", ""),
                latitude=float(data.get("latitude", 0.0)),
                longitude=float(data.get("longitude", 0.0)),
                timezone=data.get("time_zone", ""),
                isp=data.get("isp", "Bilinmiyor"),
                asn=data.get("asn", ""),
                is_proxy=bool(data.get("is_proxy", False)),
                provider="ip2location.io",
                raw_data=data
            )
        return None
