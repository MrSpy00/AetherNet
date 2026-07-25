import socket
import ssl
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
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

class SslChecker:
    """SSL/TLS certificate validator and audit tool"""

    @staticmethod
    def inspect(domain: str, port: int = 443, timeout: float = 5.0) -> Optional[SslCertificateDetails]:
        context = ssl.create_default_context()
        try:
            with socket.create_connection((domain, port), timeout=timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    protocol = ssock.version()

                    # Extract Issuer and Subject details
                    issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                    subject_dict = dict(x[0] for x in cert.get("subject", []))

                    issuer_org = issuer_dict.get("organizationName", "Unknown Issuer")
                    subject_cn = subject_dict.get("commonName", domain)

                    # Date parsing
                    date_fmt = "%b %d %H:%M:%S %Y %Z"
                    not_before = datetime.strptime(cert["notBefore"], date_fmt)
                    not_after = datetime.strptime(cert["notAfter"], date_fmt)
                    now = datetime.utcnow()
                    days_left = (not_after - now).days
                    is_valid = days_left > 0

                    return SslCertificateDetails(
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
                        cipher_name=cipher[0] if cipher else "Unknown"
                    )
        except Exception as e:
            logger.error(f"SSL certificate inspection failed for {domain}:{port} -> {e}")
            return None
