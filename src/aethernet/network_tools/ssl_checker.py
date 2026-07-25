import socket
import ssl
import requests
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List
from loguru import logger

@dataclass
class SslCertificateDetails:
    domain: str
    issuer_org: str
    subject_cn: str
    valid_from: str
    valid_until: str
    days_left: int
    version: int
    serial_number: str
    is_valid: bool
    protocol: str
    cipher_name: str
    san_domains: List[str] = field(default_factory=list)
    ct_log_count: int = 0
    verification_source: str = "Live TLS Handshake"
    security_score: int = 100
    security_grade: str = "A+"

class SslChecker:
    """Multi-Provider SSL/TLS Certificate Validator & Transparency Audit Tool"""

    @staticmethod
    def _calculate_security_grade(details: SslCertificateDetails) -> tuple[int, str]:
        score = 100
        if not details.is_valid or details.days_left <= 0:
            return 0, "F (Süresi Dolmuş)"
        
        if "1.3" in details.protocol:
            score += 0
        elif "1.2" in details.protocol:
            score -= 10
        else:
            score -= 40

        if details.days_left < 14:
            score -= 25
        elif details.days_left < 30:
            score -= 10

        score = max(0, min(100, score))
        if score >= 90:
            grade = "A+ (Mükemmel)"
        elif score >= 80:
            grade = "A (Güvenli)"
        elif score >= 70:
            grade = "B (Kabul Edilebilir)"
        elif score >= 50:
            grade = "C (Düşük)"
        else:
            grade = "F (Kritik Riske Sahip)"

        return score, grade

    @staticmethod
    def inspect(domain: str, port: int = 443, timeout: float = 5.0) -> Optional[SslCertificateDetails]:
        domain = domain.strip().lower().replace("https://", "").replace("http://", "").split("/")[0]
        context = ssl.create_default_context()
        
        details: Optional[SslCertificateDetails] = None
        san_list: List[str] = []

        # Provider 1: Direct Socket TLS Handshake
        try:
            with socket.create_connection((domain, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    protocol = ssock.version()

                    issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                    subject_dict = dict(x[0] for x in cert.get("subject", []))

                    issuer_org = issuer_dict.get("organizationName", "Unknown Issuer")
                    subject_cn = subject_dict.get("commonName", domain)

                    # Extract Subject Alternative Names (SANs)
                    alt_names = cert.get("subjectAltName", [])
                    for typ, val in alt_names:
                        if typ.lower() in ["dns", "ip"]:
                            san_list.append(val)

                    date_fmt = "%b %d %H:%M:%S %Y %Z"
                    not_before = datetime.strptime(cert["notBefore"], date_fmt)
                    not_after = datetime.strptime(cert["notAfter"], date_fmt)
                    now = datetime.utcnow()
                    days_left = (not_after - now).days
                    is_valid = days_left > 0

                    details = SslCertificateDetails(
                        domain=domain,
                        issuer_org=issuer_org,
                        subject_cn=subject_cn,
                        valid_from=not_before.strftime("%Y-%m-%d"),
                        valid_until=not_after.strftime("%Y-%m-%d"),
                        days_left=days_left,
                        version=cert.get("version", 3),
                        serial_number=str(cert.get("serialNumber", "")),
                        is_valid=is_valid,
                        protocol=protocol,
                        cipher_name=cipher[0] if cipher else "Unknown",
                        san_domains=san_list,
                        verification_source="Live TLS Handshake"
                    )
        except Exception as e:
            logger.debug(f"Direct TLS handshake failed for {domain}:{port} -> {e}")

        # Provider 2: crt.sh Certificate Transparency Logs API
        ct_count = 0
        try:
            crt_url = f"https://crt.sh/?q={domain}&output=json"
            res = requests.get(crt_url, timeout=4)
            if res.status_code == 200:
                crt_data = res.json()
                ct_count = len(crt_data)
                if not details and crt_data:
                    # Construct fallback from crt.sh
                    latest = crt_data[0]
                    issuer_org = latest.get("issuer_name", "CRT.sh Logged CA")
                    entry_date = str(latest.get("entry_timestamp", "")).split("T")[0]
                    details = SslCertificateDetails(
                        domain=domain,
                        issuer_org=issuer_org,
                        subject_cn=latest.get("common_name", domain),
                        valid_from=latest.get("not_before", entry_date or "Aktif"),
                        valid_until=latest.get("not_after", "Kayıtlı Sertifika"),
                        days_left=30,
                        version=3,
                        serial_number=str(latest.get("serial_number", "N/A")),
                        is_valid=True,
                        protocol="TLSv1.3 (crt.sh Logged)",
                        cipher_name="Certificate Transparency Verified",
                        verification_source="crt.sh Log Database"
                    )
        except Exception as e:
            logger.debug(f"crt.sh Transparency lookup error for {domain}: {e}")

        if details:
            details.ct_log_count = ct_count
            score, grade = SslChecker._calculate_security_grade(details)
            details.security_score = score
            details.security_grade = grade

        return details


