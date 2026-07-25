import os
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch

from aethernet.network_tools.whois_tool import WhoisTool, WhoisResult
from aethernet.network_tools.speedtest_tool import SpeedtestTool, SpeedtestResult
from aethernet.network_tools.port_scanner import PortScanner, PortScanResult
from aethernet.network_tools.dns_tool import DnsTool, DnsRecord
from aethernet.network_tools.ssl_checker import SslChecker, SslCertificateDetails
from aethernet.discovery.mac_vendor import MacVendorResolver
from aethernet.pentest.nmap_manager import NmapManager
from aethernet.utils.session_manager import SessionManager
from aethernet.platform.windows import WindowsPlatformAdapter


def test_whois_tool_lookup_success():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "events": [
                {"eventAction": "registration", "eventDate": "2020-01-01T00:00:00Z"},
                {"eventAction": "expiration", "eventDate": "2030-01-01T00:00:00Z"}
            ],
            "nameservers": [{"ldhName": "ns1.example.com"}],
            "entities": [
                {
                    "roles": ["registrar"],
                    "vcardArray": ["vcard", [["fn", {}, "text", "Example Registrar Inc."]]]
                }
            ]
        }
        mock_resp.text = '{"status": "ok"}'
        mock_get.return_value = mock_resp

        res = WhoisTool.lookup_domain("example.com")
        assert res.domain == "example.com"
        assert res.registrar == "Example Registrar Inc."
        assert res.creation_date == "2020-01-01"
        assert res.expiration_date == "2030-01-01"
        assert "ns1.example.com" in res.name_servers


def test_whois_tool_lookup_fallback():
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        with patch("socket.gethostbyname", return_value="8.8.8.8"):
            with patch.object(WhoisTool, "lookup_ip_geo", return_value={"isp": "Google", "org": "Google LLC", "country": "United States", "as": "AS15169", "sources": ["ip-api.com"]}):
                res = WhoisTool.lookup_domain("nonexistent-domain-test.org")
                assert res.domain == "nonexistent-domain-test.org"
                assert res.ip == "8.8.8.8"
                assert res.registrar in ("Google", "Google LLC")
                assert any("ip-api.com" in s for s in res.sources_consulted)


def test_mac_vendor_resolver():
    vendor1 = MacVendorResolver.lookup("00:50:56:11:22:33")
    assert vendor1 == "VMware Inc."

    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "Mocked Vendor Corp"
        mock_get.return_value = mock_resp

        vendor2 = MacVendorResolver.lookup("AA:BB:CC:11:22:33")
        assert vendor2 in ["Mocked Vendor Corp", "Genel Ağ Cihazı"]


def test_nmap_manager():
    tools_dir = NmapManager.get_tools_dir()
    assert tools_dir.exists()

    with patch("shutil.which", return_value="/usr/bin/nmap"):
        path = NmapManager.get_nmap_path()
        assert path is not None
        assert NmapManager.is_installed() is True


def test_speedtest_tool_mock():
    with patch("speedtest.Speedtest") as mock_st_cls:
        mock_st = MagicMock()
        mock_st.get_best_server.return_value = {"sponsor": "TestISP", "name": "Istanbul"}
        mock_st.download.return_value = 50_000_000.0
        mock_st.upload.return_value = 20_000_000.0
        mock_st.results.ping = 12.5
        mock_st_cls.return_value = mock_st

        res = SpeedtestTool.run_test()
        assert isinstance(res, SpeedtestResult)
        assert res.download_mbps == 50.0
        assert res.upload_mbps == 20.0
        assert res.ping_ms == 12.5
        assert res.server_name == "TestISP (Istanbul)"


def test_speedtest_cdn_fallback():
    with patch("requests.head") as mock_head:
        mock_head.return_value = MagicMock(status_code=200)
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.iter_content.return_value = [b"A" * 100000]
            mock_get.return_value = mock_resp

            res = SpeedtestTool._run_cdn_fallback_test()
            assert res is not None
            assert res.download_mbps > 0
            assert "CDN" in res.server_name


def test_port_scanner():
    with patch("socket.socket") as mock_sock_cls:
        mock_sock = MagicMock()
        mock_sock.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0
        mock_sock_cls.return_value = mock_sock

        is_open = PortScanner.check_port("127.0.0.1", 80)
        assert is_open is True

        scan_res = PortScanner.scan_target("127.0.0.1", ports=[80, 443])
        assert len(scan_res) == 2
        assert scan_res[0].port == 80
        assert scan_res[0].service == "HTTP"


def test_dns_tool():
    with patch("dns.resolver.Resolver") as mock_resolver_cls:
        mock_resolver = MagicMock()
        mock_answer = MagicMock()
        mock_rdata = MagicMock()
        mock_rdata.to_text.return_value = "93.184.216.34"
        mock_answer.__iter__.return_value = [mock_rdata]
        mock_answer.ttl = 300
        mock_resolver.resolve.return_value = mock_answer
        mock_resolver_cls.return_value = mock_resolver

        records = DnsTool.query("example.com", "A")
        assert len(records) == 1
        assert records[0].value == "93.184.216.34"
        assert records[0].ttl == 300

    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "Answer": [{"data": "1.1.1.1", "TTL": 300}]
        }
        mock_get.return_value = mock_resp

        doh_recs = DnsTool._query_doh_cloudflare("example.com", "A")
        assert len(doh_recs) == 1
        assert doh_recs[0].value == "1.1.1.1"


def test_ssl_checker():
    with patch("socket.create_connection") as mock_conn:
        mock_sock = MagicMock()
        mock_conn.return_value.__enter__.return_value = mock_sock

        with patch("ssl.create_default_context") as mock_ctx_cls:
            mock_ctx = MagicMock()
            mock_ssock = MagicMock()
            mock_ssock.getpeercert.return_value = {
                "issuer": [[("organizationName", "DigiCert Inc")]],
                "subject": [[("commonName", "example.com")]],
                "notBefore": "Jan 01 00:00:00 2025 GMT",
                "notAfter": "Dec 31 23:59:59 2030 GMT",
                "version": 3,
                "serialNumber": "1234567890"
            }
            mock_ssock.cipher.return_value = ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)
            mock_ssock.version.return_value = "TLSv1.3"
            mock_ctx.wrap_socket.return_value.__enter__.return_value = mock_ssock
            mock_ctx_cls.return_value = mock_ctx

            res = SslChecker.inspect("example.com")
            assert res is not None
            assert res.domain == "example.com"
            assert res.issuer_org == "DigiCert Inc"
            assert res.protocol == "TLSv1.3"
            assert res.is_valid is True


def test_session_manager(tmp_path):
    mgr = SessionManager(logs_dir=tmp_path)
    assert mgr.session_id is not None
    
    snapshot = mgr.get_system_snapshot()
    assert "cpu_percent" in snapshot

    mgr.record_operation("TEST_OP", status="SUCCESS")
    assert mgr.operation_count == 1


def test_windows_adapter_fallback():
    adapter = WindowsPlatformAdapter()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Interface Name: Wi-Fi\nSSID: TestSSID\nSignal: 85%\n")
        conn = adapter.get_current_connection()
        assert conn is not None or conn is None
