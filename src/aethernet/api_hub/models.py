from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class IPIntelligence:
    ip: str
    country: str = "Bilinmiyor"
    country_code: str = ""
    region: str = ""
    city: str = ""
    zip_code: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    timezone: str = ""
    isp: str = "Bilinmiyor"
    org: str = ""
    asn: str = ""
    is_proxy: bool = False
    is_vpn: bool = False
    is_tor: bool = False
    is_hosting: bool = False
    provider: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    fetched_at: datetime = field(default_factory=datetime.now)

@dataclass
class ThreatIntelligence:
    target: str # IP or Domain
    abuse_score: int = 0 # 0 - 100
    total_reports: int = 0
    last_reported_at: Optional[str] = None
    is_whitelisted: bool = False
    is_blacklisted: bool = False
    shodan_open_ports: List[int] = field(default_factory=list)
    shodan_cves: List[str] = field(default_factory=list)
    shodan_hostnames: List[str] = field(default_factory=list)
    cisa_exploited_vulnerabilities: List[Dict[str, str]] = field(default_factory=list)
    threat_tags: List[str] = field(default_factory=list)
    summary: str = "Tehdit kaydı bulunamadı veya temiz."

@dataclass
class DoHRecord:
    domain: str
    record_type: str # A, AAAA, MX, TXT, NS, CNAME
    answers: List[str] = field(default_factory=list)
    ttl: int = 0
    provider: str = "" # Cloudflare, Google, Quad9
    status_code: int = 0 # 0 = NOERROR, 3 = NXDOMAIN, etc.
    dnssec_valid: bool = False
    quad9_blocked: bool = False
    response_time_ms: float = 0.0

@dataclass
class MacVendorResult:
    mac: str
    vendor: str
    address: str = ""
    country: str = ""
    source: str = "Local" # Local IEEE, Online API

@dataclass
class PublicApiDefinition:
    id: str
    name: str
    description: str
    category: str # Security, Network, Cloud, AI, Tools, Data
    url: str
    auth_type: str # None, apiKey, OAuth
    cors: str # yes, no, unknown
    rate_limit: str # e.g. "45 req/min", "Free 1000/day"
    example_endpoint: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class ApiHealthStatus:
    name: str
    url: str
    is_reachable: bool
    status_code: int = 0
    latency_ms: float = 0.0
    last_check: datetime = field(default_factory=datetime.now)
