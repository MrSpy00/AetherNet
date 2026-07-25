import logging
from typing import List, Optional
from aethernet.api_hub.models import PublicApiDefinition, ApiHealthStatus
from aethernet.api_hub.client import APIHttpClient

logger = logging.getLogger(__name__)

# Pre-curated high-value public APIs for networking, security, data, and developer productivity
CURATED_APIS = [
    # Security & Intelligence
    PublicApiDefinition(
        id="shodan_internetdb",
        name="Shodan InternetDB",
        description="Public IP açık portları, hostnameleri ve bilinen CVE zafiyetlerini ücretsiz sorgulama.",
        category="Güvenlik",
        url="https://internetdb.shodan.io/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="60 req/min",
        example_endpoint="https://internetdb.shodan.io/8.8.8.8",
        tags=["security", "ports", "cve", "shodan"]
    ),
    PublicApiDefinition(
        id="cisa_kev",
        name="CISA KEV Catalog",
        description="ABD Siber Güvenlik Kurumu (CISA) aktif sömürülen zafiyetler kataloğu.",
        category="Güvenlik",
        url="https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Limitsiz",
        example_endpoint="https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        tags=["cisa", "kev", "vulnerabilities", "cybersecurity"]
    ),
    PublicApiDefinition(
        id="abuseipdb",
        name="AbuseIPDB API",
        description="Kötü amaçlı IP zararlı skorlama, ihbar istatistikleri ve IP kontrolü.",
        category="Güvenlik",
        url="https://www.abuseipdb.com/",
        auth_type="API Key",
        cors="Hayır",
        rate_limit="1000 req/gün (Ücretsiz)",
        example_endpoint="https://api.abuseipdb.com/api/v2/check?ipAddress=1.1.1.1",
        tags=["abuse", "security", "ip-reputation"]
    ),
    PublicApiDefinition(
        id="urlscan_io",
        name="URLScan.io",
        description="Web siteleri ve URL'ler için güvenlik, tarama ve DOM analizi.",
        category="Güvenlik",
        url="https://urlscan.io/",
        auth_type="API Key",
        cors="Evet",
        rate_limit="100 req/gün",
        example_endpoint="https://urlscan.io/api/v1/search/?q=domain:google.com",
        tags=["url", "phishing", "scanner", "security"]
    ),
    PublicApiDefinition(
        id="threatfox",
        name="ThreatFox by abuse.ch",
        description="Açık kaynak tehdit göstergeleri (IOC - Indicators of Compromise) veritabanı.",
        category="Güvenlik",
        url="https://threatfox.abuse.ch/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Ücretsiz",
        example_endpoint="https://threatfox-api.abuse.ch/api/v1/",
        tags=["ioc", "malware", "threatfox", "security"]
    ),

    # IP & Network Diagnostics
    PublicApiDefinition(
        id="ip_api",
        name="IP-API Geolocation",
        description="Hızlı ve detaylı IP Coğrafi konum, ISP, ASN, Proxy ve Hosting sorgulama.",
        category="Ağ & IP",
        url="http://ip-api.com/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="45 req/min",
        example_endpoint="http://ip-api.com/json/8.8.8.8",
        tags=["ip", "geolocation", "isp", "asn"]
    ),
    PublicApiDefinition(
        id="ipify",
        name="IPify Public IP",
        description="Basit ve hızlı istemci kamusal IP adresi öğrenme servisi.",
        category="Ağ & IP",
        url="https://www.ipify.org/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Limitsiz",
        example_endpoint="https://api.ipify.org?format=json",
        tags=["ip", "public-ip", "myip"]
    ),
    PublicApiDefinition(
        id="cloudflare_doh",
        name="Cloudflare DNS-over-HTTPS",
        description="1.1.1.1 şifreli HTTPS üzerinden yüksek hızlı DNS sorgulama.",
        category="Ağ & IP",
        url="https://cloudflare-dns.com/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Limitsiz",
        example_endpoint="https://cloudflare-dns.com/dns-query?name=google.com&type=A",
        tags=["dns", "doh", "cloudflare", "privacy"]
    ),
    PublicApiDefinition(
        id="google_doh",
        name="Google Public DNS-over-HTTPS",
        description="Google 8.8.8.8 altyapısı ile şifreli DoH DNS sorgulama.",
        category="Ağ & IP",
        url="https://dns.google/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Limitsiz",
        example_endpoint="https://dns.google/resolve?name=google.com&type=A",
        tags=["dns", "doh", "google"]
    ),
    PublicApiDefinition(
        id="macvendors_co",
        name="MacVendors.co",
        description="MAC adresi OUI üretici firmasını çevrimiçi çözme API'si.",
        category="Ağ & IP",
        url="https://macvendors.co/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="1000 req/gün",
        example_endpoint="https://macvendors.co/api/00:11:22:33:44:55",
        tags=["mac", "oui", "vendor", "hardware"]
    ),
    PublicApiDefinition(
        id="httpbin",
        name="HTTPBin Test Engine",
        description="HTTP isteklerini, başlıklarını ve gövdelerini test etmek için yankı (echo) servisi.",
        category="Araçlar",
        url="https://httpbin.org/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Limitsiz",
        example_endpoint="https://httpbin.org/get",
        tags=["http", "testing", "echo", "tools"]
    ),

    # Cloud, AI & Data Services
    PublicApiDefinition(
        id="open_meteo",
        name="Open-Meteo Weather API",
        description="Konum bazlı hava durumu, sıcaklık ve atmosfer verileri (Ücretsiz, API Key istemez).",
        category="Veri & Sistem",
        url="https://open-meteo.com/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="10,000 req/gün",
        example_endpoint="https://api.open-meteo.com/v1/forecast?latitude=41.01&longitude=28.97&current_weather=true",
        tags=["weather", "geo", "meteorology", "free"]
    ),
    PublicApiDefinition(
        id="freeapi_app",
        name="FreeAPI.app Mock Hub",
        description="Geliştiriciler için hazır REST API mock uç noktaları ve veri setleri.",
        category="Geliştirici",
        url="https://freeapi.app/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Ücretsiz",
        example_endpoint="https://api.freeapi.app/api/v1/public/randomusers",
        tags=["mock", "api", "freeapi", "testing"]
    ),
    PublicApiDefinition(
        id="freepublicapis",
        name="FreePublicAPIs Directory",
        description="Kamusal ve açık API'lerin derlenmiş veritabanı uç noktası.",
        category="Geliştirici",
        url="https://www.freepublicapis.com/",
        auth_type="Yok",
        cors="Evet",
        rate_limit="Ücretsiz",
        example_endpoint="https://www.freepublicapis.com/api/apis",
        tags=["directory", "apis", "catalog"]
    ),
]


class PublicApiCatalog:
    """Catalog Manager for Curated Public & Free APIs."""

    def __init__(self, client: Optional[APIHttpClient] = None):
        self.client = client or APIHttpClient()
        self.apis: List[PublicApiDefinition] = list(CURATED_APIS)

    def list_categories(self) -> List[str]:
        """Returns unique categories."""
        cats = sorted(list(set(api.category for api in self.apis)))
        return ["Tümü"] + cats

    def search_apis(self, keyword: Optional[str] = None, category: Optional[str] = None) -> List[PublicApiDefinition]:
        """Filters public APIs by keyword or category."""
        results = []
        kw = keyword.lower().strip() if keyword else None
        cat = category if category and category != "Tümü" else None

        for api in self.apis:
            if cat and api.category != cat:
                continue

            if kw:
                searchable = f"{api.name} {api.description} {api.category} {' '.join(api.tags)}".lower()
                if kw not in searchable:
                    continue

            results.append(api)

        return results

    def check_api_health(self, api_def: PublicApiDefinition) -> ApiHealthStatus:
        """Pings API example endpoint to measure latency and reachability."""
        if not api_def.example_endpoint:
            return ApiHealthStatus(name=api_def.name, url=api_def.url, is_reachable=False)

        _, status_code, latency = self.client.get_json(api_def.example_endpoint, use_cache=False, timeout=4)
        is_reachable = (status_code >= 200 and status_code < 400) or status_code == 429
        return ApiHealthStatus(
            name=api_def.name,
            url=api_def.example_endpoint,
            is_reachable=is_reachable,
            status_code=status_code,
            latency_ms=round(latency, 2)
        )
