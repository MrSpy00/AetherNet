from dataclasses import dataclass
from typing import Optional, List
import requests
from loguru import logger

@dataclass
class WhoisResult:
    domain: str
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiration_date: Optional[str] = None
    name_servers: List[str] = None
    org: Optional[str] = None
    country: Optional[str] = None
    asn: Optional[str] = None
    raw_text: Optional[str] = None

class WhoisTool:
    """WHOIS / RDAP and IP Geolocation provider tool"""

    @staticmethod
    def lookup_domain(domain: str) -> WhoisResult:
        # Try RDAP / WHOIS via public REST API endpoint first for reliability
        url = f"https://rdap.org/domain/{domain}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                events = data.get("events", [])
                created = None
                expires = None
                for ev in events:
                    if ev.get("eventAction") == "registration":
                        created = ev.get("eventDate")
                    elif ev.get("eventAction") == "expiration":
                        expires = ev.get("eventDate")

                ns_list = [ns.get("ldhName") for ns in data.get("nameservers", []) if ns.get("ldhName")]
                return WhoisResult(
                    domain=domain,
                    registrar=data.get("port43", "RDAP Record"),
                    creation_date=created,
                    expiration_date=expires,
                    name_servers=ns_list,
                    raw_text=resp.text[:1000]
                )
        except Exception as e:
            logger.warning(f"RDAP lookup failed for {domain}: {e}")

        return WhoisResult(domain=domain)

    @staticmethod
    def lookup_ip_geo(ip: str) -> dict:
        """Lookup IP Geolocation & ASN info via ip-api.com"""
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as,query"
            res = requests.get(url, timeout=4)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            logger.error(f"IP Geo lookup error: {e}")
        return {}
