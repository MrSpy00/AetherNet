"""Unit tests for ARP Spoofing Detector and DNS Leak Checker."""

from aethernet.security.arp_spoof_detector import ARPSpoofDetector, ARPEntry
from aethernet.security.dns_leak_checker import DNSLeakChecker


def test_arp_spoof_detection():
    detector = ARPSpoofDetector()
    res = detector.analyze_arp_table()
    assert "is_spoofed" in res
    assert "alerts" in res
    assert isinstance(res["alerts"], list)


def test_dns_leak_checker():
    checker = DNSLeakChecker()
    res = checker.check_leak_status(is_vpn_active=False)
    assert "has_leak" in res
    assert "resolvers" in res
    assert res["has_leak"] is False
