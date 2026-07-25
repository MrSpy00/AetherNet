import logging
from typing import Optional, Dict, Any, List
from aethernet.api_hub.client import APIHttpClient

logger = logging.getLogger(__name__)

class ShodanEngine:
    """Comprehensive Shodan Intelligence, Vulnerability & Search Engine."""

    INTERNETDB_URL = "https://internetdb.shodan.io"
    SHODAN_API_URL = "https://api.shodan.io"

    def __init__(self, client: Optional[APIHttpClient] = None, api_key: Optional[str] = None):
        self.client = client or APIHttpClient()
        self.api_key = api_key

    def query_ip_free(self, ip: str) -> Dict[str, Any]:
        """Free Shodan InternetDB lookup (Open ports, hostnames, CPEs, CVEs). No API key required."""
        clean_ip = ip.strip()
        url = f"{self.INTERNETDB_URL}/{clean_ip}"
        data, status, _ = self.client.get_json(url, rate_limit_pm=60, timeout=6)
        if status == 200 and isinstance(data, dict):
            return {
                "ip": data.get("ip", clean_ip),
                "ports": data.get("ports", []),
                "cves": data.get("vulns", []),
                "hostnames": data.get("hostnames", []),
                "cpes": data.get("cpes", []),
                "tags": data.get("tags", []),
                "source": "Shodan InternetDB (Free)"
            }
        return {
            "ip": clean_ip,
            "ports": [],
            "cves": [],
            "hostnames": [],
            "cpes": [],
            "tags": [],
            "source": "None"
        }

    def host_details(self, ip: str) -> Dict[str, Any]:
        """Queries detailed Shodan host info. Uses API Key if provided, else falls back to InternetDB."""
        clean_ip = ip.strip()
        if self.api_key:
            url = f"{self.SHODAN_API_URL}/shodan/host/{clean_ip}?key={self.api_key}"
            data, status, _ = self.client.get_json(url, rate_limit_pm=30, timeout=8)
            if status == 200 and isinstance(data, dict):
                return {
                    "ip": clean_ip,
                    "os": data.get("os", "Bilinmiyor"),
                    "isp": data.get("isp", "Bilinmiyor"),
                    "org": data.get("org", ""),
                    "asn": data.get("asn", ""),
                    "ports": data.get("ports", []),
                    "cves": list(data.get("vulns", {}).keys()) if isinstance(data.get("vulns"), dict) else data.get("vulns", []),
                    "hostnames": data.get("hostnames", []),
                    "data_banners": [
                        {
                            "port": item.get("port"),
                            "product": item.get("product", ""),
                            "version": item.get("version", ""),
                            "banner": item.get("data", "")[:200]
                        }
                        for item in data.get("data", [])
                    ],
                    "source": "Shodan REST API"
                }

        return self.query_ip_free(clean_ip)

    def dns_domain(self, domain: str) -> Dict[str, Any]:
        """Resolves subdomains & DNS records for a domain via Shodan API."""
        clean_domain = domain.strip().lower()
        if self.api_key:
            url = f"{self.SHODAN_API_URL}/dns/domain/{clean_domain}?key={self.api_key}"
            data, status, _ = self.client.get_json(url, rate_limit_pm=20, timeout=8)
            if status == 200 and isinstance(data, dict):
                return {
                    "domain": clean_domain,
                    "subdomains": [f"{sub}.{clean_domain}" for sub in data.get("subdomains", [])],
                    "records": data.get("data", []),
                    "source": "Shodan DNS API"
                }

        return {"domain": clean_domain, "subdomains": [], "records": [], "source": "Shodan (API Key Gerekli)"}

    def search_devices(self, query: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Searches global Shodan database by query string (e.g. port:21, product:Apache)."""
        if not self.api_key or not query.strip():
            return []

        url = f"{self.SHODAN_API_URL}/shodan/host/search"
        params = {"key": self.api_key, "query": query.strip()}
        data, status, _ = self.client.get_json(url, params=params, rate_limit_pm=20, timeout=10)

        results = []
        if status == 200 and isinstance(data, dict) and "matches" in data:
            for match in data["matches"][:limit]:
                results.append({
                    "ip": match.get("ip_str"),
                    "port": match.get("port"),
                    "org": match.get("org", ""),
                    "country": match.get("location", {}).get("country_name", ""),
                    "product": match.get("product", ""),
                    "banner_snippet": match.get("data", "")[:150]
                })
        return results
