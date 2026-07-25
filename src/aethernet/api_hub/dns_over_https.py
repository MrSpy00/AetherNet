import time
import logging
from typing import Optional, List
from aethernet.api_hub.models import DoHRecord
from aethernet.api_hub.client import APIHttpClient

logger = logging.getLogger(__name__)

class DoHEngine:
    """Encrypted DNS-over-HTTPS (DoH) Engine supporting Cloudflare, Google, and Quad9."""

    PROVIDERS = {
        "Cloudflare": "https://cloudflare-dns.com/dns-query",
        "Google": "https://dns.google/resolve",
        "Quad9": "https://dns.quad9.net:5053/dns-query"
    }

    TYPE_MAP = {
        "A": 1,
        "AAAA": 28,
        "MX": 15,
        "TXT": 16,
        "NS": 2,
        "CNAME": 5,
        "SOA": 6
    }

    def __init__(self, client: Optional[APIHttpClient] = None):
        self.client = client or APIHttpClient()

    def query(self, domain: str, record_type: str = "A", provider_name: str = "Cloudflare") -> DoHRecord:
        """Queries DNS record via encrypted HTTPS API."""
        domain_clean = domain.strip().rstrip(".")
        rec_type = record_type.upper()

        provider_url = self.PROVIDERS.get(provider_name, self.PROVIDERS["Cloudflare"])
        
        headers = {"Accept": "application/dns-json"}
        params = {"name": domain_clean, "type": rec_type}

        data, status, latency = self.client.get_json(
            provider_url,
            headers=headers,
            params=params,
            rate_limit_pm=120,
            timeout=5
        )

        record = DoHRecord(
            domain=domain_clean,
            record_type=rec_type,
            provider=provider_name,
            response_time_ms=round(latency, 2)
        )

        if status == 200 and isinstance(data, dict):
            record.status_code = data.get("Status", 0)
            record.dnssec_valid = bool(data.get("AD", False))
            
            answers = []
            ttl = 0
            for ans in data.get("Answer", []):
                if "data" in ans:
                    answers.append(ans["data"])
                if "TTL" in ans:
                    ttl = ans["TTL"]

            record.answers = answers
            record.ttl = ttl

            # Quad9 returns NXDOMAIN (Status 3) or 0.0.0.0 for malicious domains
            if provider_name == "Quad9" and (record.status_code == 3 or "0.0.0.0" in record.answers):
                record.quad9_blocked = True

        return record

    def test_dns_leak(self, domain: str = "whoami.akamai.net") -> List[DoHRecord]:
        """Queries multiple DoH providers simultaneously to analyze DNS resolution path & leak."""
        results = []
        for name in self.PROVIDERS.keys():
            rec = self.query(domain, record_type="A", provider_name=name)
            results.append(rec)
        return results
