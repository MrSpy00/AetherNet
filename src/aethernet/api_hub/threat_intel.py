import logging
from typing import Optional, List, Dict, Any
from aethernet.api_hub.models import ThreatIntelligence
from aethernet.api_hub.client import APIHttpClient

logger = logging.getLogger(__name__)

class ThreatIntelligenceEngine:
    """Threat Intelligence Engine incorporating Shodan InternetDB, CISA KEV, AbuseIPDB, and IOCs."""

    def __init__(self, client: Optional[APIHttpClient] = None, abuseipdb_key: Optional[str] = None):
        self.client = client or APIHttpClient()
        self.abuseipdb_key = abuseipdb_key
        self._cisa_kev_cache: Optional[List[Dict[str, Any]]] = None

    def analyze_target(self, target: str) -> ThreatIntelligence:
        """Analyzes an IP or Domain across free threat intelligence feeds."""
        target_clean = target.strip()
        intel = ThreatIntelligence(target=target_clean)

        # 1. Query Shodan InternetDB (Free open ports & CVEs lookup for public IP)
        if self._is_valid_ip(target_clean):
            shodan_res = self._query_shodan_internetdb(target_clean)
            if shodan_res:
                intel.shodan_open_ports = shodan_res.get("ports", [])
                intel.shodan_cves = shodan_res.get("vulns", [])
                intel.shodan_hostnames = shodan_res.get("hostnames", [])
                if intel.shodan_cves:
                    intel.threat_tags.append("CVE-Zafiyetli")
                if intel.shodan_open_ports:
                    intel.threat_tags.append("Açık-Portlar")

        # 2. Query AbuseIPDB if API Key is configured
        if self.abuseipdb_key and self._is_valid_ip(target_clean):
            abuse_res = self._query_abuseipdb(target_clean)
            if abuse_res:
                intel.abuse_score = abuse_res.get("abuseConfidenceScore", 0)
                intel.total_reports = abuse_res.get("totalReports", 0)
                intel.last_reported_at = abuse_res.get("lastReportedAt")
                intel.is_whitelisted = abuse_res.get("isWhitelisted", False)

        # Summary computation
        tags_str = ", ".join(intel.threat_tags) if intel.threat_tags else "Temiz / Bilinen Tehdit Yok"
        ports_str = f"{len(intel.shodan_open_ports)} Açık Port" if intel.shodan_open_ports else "Port Yok"
        cve_str = f"{len(intel.shodan_cves)} Zafiyet (CVE)" if intel.shodan_cves else "CVE Yok"
        intel.summary = f"Skor: %{intel.abuse_score} | {ports_str} | {cve_str} | Etiketler: {tags_str}"

        return intel

    def _query_shodan_internetdb(self, ip: str) -> Optional[Dict[str, Any]]:
        """Queries Shodan InternetDB API (100% Free public API)."""
        url = f"https://internetdb.shodan.io/{ip}"
        data, status, _ = self.client.get_json(url, rate_limit_pm=60)
        if status == 200 and isinstance(data, dict):
            return data
        return None

    def _query_abuseipdb(self, ip: str) -> Optional[Dict[str, Any]]:
        """Queries AbuseIPDB API v2."""
        url = "https://api.abuseipdb.com/api/v2/check"
        headers = {
            "Key": self.abuseipdb_key,
            "Accept": "application/json"
        }
        params = {"ipAddress": ip, "maxAgeInDays": "90"}
        data, status, _ = self.client.get_json(url, headers=headers, params=params, rate_limit_pm=30)
        if status == 200 and data and "data" in data:
            return data["data"]
        return None

    def fetch_cisa_kev(self, limit: int = 50, keyword: Optional[str] = None) -> List[Dict[str, str]]:
        """Fetches and filters CISA Known Exploited Vulnerabilities (KEV) Catalog."""
        if self._cisa_kev_cache is None:
            url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
            data, status, _ = self.client.get_json(url, use_cache=True, cache_ttl=3600, rate_limit_pm=10)
            if status == 200 and data and "vulnerabilities" in data:
                self._cisa_kev_cache = data["vulnerabilities"]
            else:
                self._cisa_kev_cache = []

        vulnerabilities = self._cisa_kev_cache or []
        results = []

        kw = keyword.lower().strip() if keyword else None
        for item in vulnerabilities:
            cve_id = item.get("cveID", "")
            vendor = item.get("vendorProject", "")
            product = item.get("product", "")
            name = item.get("vulnerabilityName", "")
            date_added = item.get("dateAdded", "")

            if kw:
                search_target = f"{cve_id} {vendor} {product} {name}".lower()
                if kw not in search_target:
                    continue

            results.append({
                "cve_id": cve_id,
                "vendor": vendor,
                "product": product,
                "name": name,
                "date_added": date_added,
                "action": item.get("requiredAction", "")
            })

            if len(results) >= limit:
                break

        return results

    @staticmethod
    def _is_valid_ip(target: str) -> bool:
        parts = target.split(".")
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            return False
