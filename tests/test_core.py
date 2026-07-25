import pytest
from aethernet.core.models import NetworkInterfaceInfo, WifiConnectionDetails, ScannedNetwork
from aethernet.security.security_scorer import SecurityScorer
from aethernet.security.rogue_ap_detector import RogueApDetector
from aethernet.discovery.mac_vendor import MacVendorResolver
from aethernet.network_tools.ping_tool import PingTool

def test_security_scorer_wpa3():
    report = SecurityScorer.evaluate_connection("WPA3-Personal")
    assert report.score >= 90
    assert report.rating == "Mükemmel"

def test_security_scorer_open_network():
    report = SecurityScorer.evaluate_connection("Open", is_open_network=True)
    assert report.score <= 50

def test_mac_vendor_resolver():
    vendor = MacVendorResolver.lookup("DC:A6:32:00:11:22")
    assert "Raspberry Pi" in vendor

def test_rogue_ap_detector():
    nets = [
        ScannedNetwork("Ev_WiFi", "AA:BB:CC:DD:EE:01", 80, -60, 6, "2.4 GHz", "WPA2", "CCMP"),
        ScannedNetwork("Ev_WiFi", "AA:BB:CC:DD:EE:02", 70, -65, 11, "2.4 GHz", "WEP", "TKIP"),
    ]
    alerts = RogueApDetector.detect_evil_twins(nets)
    assert len(alerts) > 0
    assert alerts[0].target_ssid == "Ev_WiFi"

def test_ping_result_structure():
    res = PingTool.ping("127.0.0.1", count=1)
    assert res.target == "127.0.0.1"
    assert res.sent == 1
