"""Unit tests for WiFi QR, SLA Monitor, and Topology Mapper."""

from aethernet.utils.wifi_qr import WiFiQRGenerator
from aethernet.network_tools.sla_monitor import SLAMonitor
from aethernet.discovery.topology_mapper import NetworkTopologyMapper


def test_wifi_qr_payload():
    payload = WiFiQRGenerator.generate_qr_payload("MyWiFi", "secret123", "WPA")
    assert payload == "WIFI:S:MyWiFi;T:WPA;P:secret123;;"

    payload_open = WiFiQRGenerator.generate_qr_payload("OpenWiFi", "", "NOPASS")
    assert payload_open == "WIFI:S:OpenWiFi;T:nopass;;"


def test_sla_monitor():
    monitor = SLAMonitor(target_host="8.8.8.8")
    monitor.record_ping_sample(latency_ms=15.5, packet_loss_pct=0.0)
    monitor.record_ping_sample(latency_ms=25.0, packet_loss_pct=0.0)
    summary = monitor.get_summary()

    assert summary["uptime_pct"] == 100.0
    assert summary["avg_latency_ms"] == 20.25
    assert summary["samples_count"] == 2


def test_topology_mapper():
    mapper = NetworkTopologyMapper()
    devices = [
        {"ip": "192.168.1.1", "mac": "00:11:22:33:44:55", "hostname": "Gateway", "device_type": "Gateway"},
        {"ip": "192.168.1.10", "mac": "AA:BB:CC:DD:EE:FF", "hostname": "Desktop-PC", "device_type": "PC"}
    ]
    tree = mapper.build_topology(
        gateway_ip="192.168.1.1",
        gateway_mac="00:11:22:33:44:55",
        discovered_devices=devices
    )

    assert "gw_192.168.1.1" in tree
    assert len(tree["gw_192.168.1.1"].children) == 1
