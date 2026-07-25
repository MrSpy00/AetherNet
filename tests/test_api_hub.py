import pytest
import time
from aethernet.api_hub.client import APIHttpClient, RateLimiter, SimpleTTLCache
from aethernet.api_hub.ip_intel import IPIntelligenceEngine
from aethernet.api_hub.threat_intel import ThreatIntelligenceEngine
from aethernet.api_hub.dns_over_https import DoHEngine
from aethernet.api_hub.mac_lookup import MacLookupEngine
from aethernet.api_hub.public_api_catalog import PublicApiCatalog, PublicApiDefinition
from aethernet.api_hub.models import IPIntelligence, ThreatIntelligence, DoHRecord


def test_rate_limiter():
    limiter = RateLimiter(requests_per_minute=60)
    assert limiter.acquire() is True
    # Consume all tokens
    limiter.tokens = 0.0
    assert limiter.acquire() is False


def test_ttl_cache():
    cache = SimpleTTLCache(default_ttl=1)
    cache.set("key1", "value1", ttl=1)
    assert cache.get("key1") == "value1"
    time.sleep(1.1)
    assert cache.get("key1") is None


def test_public_api_catalog():
    catalog = PublicApiCatalog()
    categories = catalog.list_categories()
    assert "Tümü" in categories
    assert "Güvenlik" in categories

    results = catalog.search_apis(keyword="shodan")
    assert len(results) >= 1
    assert results[0].id == "shodan_internetdb"


def test_ip_intel_mock_or_live():
    engine = IPIntelligenceEngine()
    res = engine.lookup_ip("8.8.8.8")
    assert isinstance(res, IPIntelligence)
    assert res.ip == "8.8.8.8"
    assert res.country != "Bilinmiyor" or res.provider != ""


def test_threat_intel():
    engine = ThreatIntelligenceEngine()
    intel = engine.analyze_target("8.8.8.8")
    assert isinstance(intel, ThreatIntelligence)
    assert intel.target == "8.8.8.8"

    kev_items = engine.fetch_cisa_kev(limit=5)
    assert isinstance(kev_items, list)


def test_doh_engine():
    engine = DoHEngine()
    record = engine.query("google.com", record_type="A", provider_name="Cloudflare")
    assert isinstance(record, DoHRecord)
    assert record.domain == "google.com"


def test_mac_lookup():
    engine = MacLookupEngine()
    res = engine.lookup("00:50:56:00:00:01")
    assert res.mac == "00:50:56:00:00:01"


def test_shodan_engine():
    from aethernet.api_hub.shodan_engine import ShodanEngine
    shodan = ShodanEngine()
    data = shodan.query_ip_free("8.8.8.8")
    assert isinstance(data, dict)
    assert data["ip"] == "8.8.8.8"

