"""Comprehensive Unit Tests for Network Tools, Security Scorer, and Discovery modules."""

from aethernet.network_tools.ping_tool import PingTool
from aethernet.network_tools.dns_tool import DnsTool
from aethernet.network_tools.port_scanner import PortScanner
from aethernet.network_tools.ssl_checker import SslChecker
from aethernet.security.security_scorer import SecurityScorer
from aethernet.security.rogue_ap_detector import RogueApDetector
from aethernet.discovery.mac_vendor import MacVendorResolver
from aethernet.core.models import ScannedNetwork


def test_ping_tool_struct():
    res = PingTool.ping("127.0.0.1", count=1)
    assert res.target == "127.0.0.1"
    assert res.sent == 1


def test_mac_vendor_lookup():
    vendor = MacVendorResolver.lookup("00:50:56:00:00:00")
    assert "VMware" in vendor



def test_security_scorer():
    wep_res = SecurityScorer.evaluate_connection("WEP")
    assert wep_res.score <= 60
    assert wep_res.rating == "Orta"

    wpa3_res = SecurityScorer.evaluate_connection("WPA3-SAE")
    assert wpa3_res.score >= 90
    assert wpa3_res.rating == "Mükemmel"


def test_rogue_ap_detector():
    networks = [
        ScannedNetwork(ssid="CorpWiFi", bssid="00:11:22:33:44:55", signal_percent=80, signal_dbm=-60, channel=6, band="2.4 GHz", security="WPA2", cipher="CCMP"),
        ScannedNetwork(ssid="CorpWiFi", bssid="AA:BB:CC:DD:EE:FF", signal_percent=75, signal_dbm=-62, channel=6, band="2.4 GHz", security="OPEN", cipher="NONE"),
    ]
    alerts = RogueApDetector.detect_evil_twins(networks)
    assert len(alerts) > 0
