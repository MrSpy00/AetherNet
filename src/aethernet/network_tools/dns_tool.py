import dns.resolver
import dns.reversename
from dataclasses import dataclass
from typing import List, Dict, Any
from loguru import logger

@dataclass
class DnsRecord:
    record_type: str
    value: str
    ttl: int

class DnsTool:
    """DNS kayıt sorgulama (A, AAAA, MX, TXT, NS, CNAME, SOA, PTR)"""

    @staticmethod
    def query(domain: str, record_type: str = "A", dns_server: str = "1.1.1.1") -> List[DnsRecord]:
        results: List[DnsRecord] = []
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = 3.0
        resolver.lifetime = 3.0

        try:
            answers = resolver.resolve(domain, record_type)
            for rdata in answers:
                results.append(
                    DnsRecord(
                        record_type=record_type,
                        value=rdata.to_text(),
                        ttl=answers.ttl
                    )
                )
        except Exception as e:
            logger.warning(f"DNS resolve error for {domain} ({record_type}): {e}")

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
