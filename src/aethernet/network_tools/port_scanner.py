import socket
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict
from loguru import logger

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    1433: "MSSQL",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt"
}

@dataclass
class PortScanResult:
    port: int
    service: str
    is_open: bool

class PortScanner:
    """Multi-threaded TCP connect port scanner"""

    @staticmethod
    def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                res = s.connect_ex((host, port))
                return res == 0
        except Exception:
            return False

    @classmethod
    def scan_target(
        cls,
        host: str,
        ports: List[int] = None,
        max_workers: int = 50,
        timeout: float = 1.0
    ) -> List[PortScanResult]:
        if ports is None:
            ports = list(COMMON_PORTS.keys())

        results: List[PortScanResult] = []

        def worker(p: int):
            is_open = cls.check_port(host, p, timeout)
            if is_open:
                service = COMMON_PORTS.get(p, "Bilinmeyen Servis")
                results.append(PortScanResult(port=p, service=service, is_open=True))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(worker, ports)

        results.sort(key=lambda x: x.port)
        return results
