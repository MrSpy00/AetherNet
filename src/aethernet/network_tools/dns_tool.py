import requests
import dns.resolver
import dns.reversename
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from loguru import logger

@dataclass
class DnsRecord:
    record_type: str
    value: str
    ttl: int
    provider: str = "UDP (1.1.1.1)"

class DnsTool:
    """Multi-Provider & DNS-over-HTTPS (DoH) DNS Resolver Tool"""

    PUBLIC_RESOLVERS = {
        "Cloudflare": "1.1.1.1",
        "Google": "8.8.8.8",
        "Quad9": "9.9.9.9",
        "OpenDNS": "208.67.222.222"
    }

    @staticmethod
    def query(domain: str, record_type: str = "A", dns_server: str = "1.1.1.1") -> List[DnsRecord]:
        results: List[DnsRecord] = []
        seen_values = set()

        # Step 1: Query specified UDP/TCP DNS Resolver via dnspython
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = 2.5
            resolver.lifetime = 2.5

            answers = resolver.resolve(domain, record_type)
            for rdata in answers:
                val = rdata.to_text().rstrip(".")
                if val not in seen_values:
                    seen_values.add(val)
                    results.append(
                        DnsRecord(
                            record_type=record_type,
                            value=val,
                            ttl=answers.ttl,
                            provider=f"UDP Resolver ({dns_server})"
                        )
                    )
        except Exception as e:
            logger.debug(f"UDP DNS resolve error for {domain} ({record_type}): {e}")

        # Step 2: DoH Fallback 1 - Cloudflare DoH API
        if not results:
            doh_cf = DnsTool._query_doh_cloudflare(domain, record_type)
            for rec in doh_cf:
                if rec.value not in seen_values:
                    seen_values.add(rec.value)
                    results.append(rec)

        # Step 3: DoH Fallback 2 - Google DoH API
        if not results:
            doh_google = DnsTool._query_doh_google(domain, record_type)
            for rec in doh_google:
                if rec.value not in seen_values:
                    seen_values.add(rec.value)
                    results.append(rec)

        # Step 4: DoH Fallback 3 - AdGuard DoH API
        if not results:
            doh_adguard = DnsTool._query_doh_adguard(domain, record_type)
            for rec in doh_adguard:
                if rec.value not in seen_values:
                    seen_values.add(rec.value)
                    results.append(rec)

        return results

    @staticmethod
    def _query_doh_cloudflare(domain: str, record_type: str) -> List[DnsRecord]:
        results = []
        try:
            url = f"https://cloudflare-dns.com/dns-query?name={domain}&type={record_type}"
            headers = {"Accept": "application/dns-json"}
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                data = res.json()
                for ans in data.get("Answer", []):
                    results.append(
                        DnsRecord(
                            record_type=record_type,
                            value=str(ans.get("data", "")).rstrip("."),
                            ttl=int(ans.get("TTL", 300)),
                            provider="Cloudflare DoH (HTTPS)"
                        )
                    )
        except Exception as e:
            logger.debug(f"Cloudflare DoH error: {e}")
        return results

    @staticmethod
    def _query_doh_google(domain: str, record_type: str) -> List[DnsRecord]:
        results = []
        try:
            url = f"https://dns.google/resolve?name={domain}&type={record_type}"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                for ans in data.get("Answer", []):
                    results.append(
                        DnsRecord(
                            record_type=record_type,
                            value=str(ans.get("data", "")).rstrip("."),
                            ttl=int(ans.get("TTL", 300)),
                            provider="Google DoH (HTTPS)"
                        )
                    )
        except Exception as e:
            logger.debug(f"Google DoH error: {e}")
        return results

    @staticmethod
    def _query_doh_adguard(domain: str, record_type: str) -> List[DnsRecord]:
        results = []
        try:
            url = f"https://dns.adguard-dns.com/resolve?name={domain}&type={record_type}"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                for ans in data.get("Answer", []):
                    results.append(
                        DnsRecord(
                            record_type=record_type,
                            value=str(ans.get("data", "")).rstrip("."),
                            ttl=int(ans.get("TTL", 300)),
                            provider="AdGuard DoH (Security Filtered)"
                        )
                    )
        except Exception as e:
            logger.debug(f"AdGuard DoH error: {e}")
        return results


    @staticmethod
    def reverse_dns(ip_address: str) -> Optional[str]:
        try:
            rev_name = dns.reversename.from_address(ip_address)
            answers = dns.resolver.resolve(rev_name, "PTR")
            if answers:
                return str(answers[0]).rstrip(".")
        except Exception:
            pass
        return None

