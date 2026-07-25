import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Add src directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aethernet.platform.base import BasePlatformAdapter
from aethernet.core.models import (
    NetworkInterfaceInfo,
    WifiConnectionDetails,
    WifiProfile,
    ScannedNetwork,
)
from aethernet.gui.i18n_manager import I18nManager
from aethernet.gui.views.dashboard_view import DashboardView
from aethernet.gui.views.wifi_view import WifiView
from aethernet.gui.views.tools_view import ToolsView
from aethernet.gui.views.security_view import SecurityView
from aethernet.gui.views.api_hub_view import APIHubView
from aethernet.gui.views.pentest_view import PentestView
from aethernet.gui.theme_manager import ThemeManager

class MockDemoAdapter(BasePlatformAdapter):
    """Anonymized Demo Platform Adapter with safe placeholder data for screenshots."""

    def get_interfaces(self):
        return [
            NetworkInterfaceInfo(
                name="Wi-Fi 6E Ultra",
                description="Intel(R) Wi-Fi 6E AX211 160MHz",
                mac_address="00:11:22:33:44:55",
                is_wifi=True,
                is_enabled=True,
                is_connected=True,
                supported_standards=["802.11a", "802.11b", "802.11g", "802.11n", "802.11ac", "802.11ax"],
                supported_bands=["2.4 GHz", "5 GHz", "6 GHz"],
                ipv4_address="192.168.1.105",
                ipv4_subnet="255.255.255.0",
            ),
            NetworkInterfaceInfo(
                name="Ethernet Gigabit",
                description="Realtek PCIe GbE Family Controller",
                mac_address="00:11:22:AA:BB:CC",
                is_wifi=False,
                is_enabled=True,
                is_connected=False,
                supported_standards=[],
                supported_bands=[],
                ipv4_address=None,
                ipv4_subnet=None,
            ),
        ]

    def get_current_connection(self):
        return WifiConnectionDetails(
            adapter_name="Wi-Fi 6E Ultra",
            ssid="AetherNet_Cyber_5G",
            bssid="00:11:22:33:44:55",
            state="connected",
            signal_percent=94,
            signal_dbm=-48,
            radio_type="802.11ax (Wi-Fi 6)",
            channel=36,
            frequency_ghz=5.18,
            channel_width_mhz=160,
            receive_rate_mbps=1201.0,
            transmit_rate_mbps=1201.0,
            security_protocol="WPA3-Personal",
            cipher="CCMP",
            authentication="WPA3-SAE",
        )

    def get_saved_profiles(self):
        return [
            WifiProfile(name="AetherNet_Cyber_5G", ssid="AetherNet_Cyber_5G", security_type="WPA3-Personal", auto_connect=True),
            WifiProfile(name="SafeNet_Corporate", ssid="SafeNet_Corporate", security_type="WPA2-Enterprise", auto_connect=True),
            WifiProfile(name="Lab_Guest_WiFi", ssid="Lab_Guest_WiFi", security_type="WPA2-PSK", auto_connect=False),
            WifiProfile(name="Home_Fiber_Ultra", ssid="Home_Fiber_Ultra", security_type="WPA3-Personal", auto_connect=True),
        ]

    def get_profile_password(self, profile_name: str) -> str:
        return "SafeDemoPass2026!"

    def scan_networks(self):
        return [
            ScannedNetwork(ssid="AetherNet_Cyber_5G", bssid="00:11:22:33:44:55", signal_percent=94, signal_dbm=-48, channel=36, band="5 GHz", security="WPA3-Personal", cipher="CCMP"),
            ScannedNetwork(ssid="SafeNet_Corporate", bssid="00:11:22:AA:BB:11", signal_percent=88, signal_dbm=-52, channel=149, band="5 GHz", security="WPA2-Enterprise", cipher="AES"),
            ScannedNetwork(ssid="Neighbour_Mesh_2.4G", bssid="00:11:22:BB:CC:22", signal_percent=65, signal_dbm=-68, channel=6, band="2.4 GHz", security="WPA2-PSK", cipher="TKIP"),
            ScannedNetwork(ssid="IoT_Sensors_Net", bssid="00:11:22:CC:DD:33", signal_percent=45, signal_dbm=-78, channel=1, band="2.4 GHz", security="WPA2-PSK", cipher="AES"),
        ]

    def connect_profile(self, profile_name: str) -> bool:
        return True

    def disconnect(self, interface_name: str = "") -> bool:
        return True

    def set_adapter_state(self, interface_name: str, enable: bool) -> bool:
        return True

def capture_screenshots():
    app = QApplication.instance() or QApplication(sys.argv)
    adapter = MockDemoAdapter()

    screenshots_dir = Path("assets/screenshots")
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    views_to_capture = [
        ("dashboard", DashboardView),
        ("wifi", WifiView),
        ("tools", ToolsView),
        ("security", SecurityView),
        ("api_hub", APIHubView),
        ("pentest", PentestView),
    ]

    for lang in ["tr", "en"]:
        i18n = I18nManager(lang)
        for name, cls in views_to_capture:
            try:
                widget = cls(adapter, i18n)
                # Populate mock location data for API Hub
                if name == "api_hub":
                    widget.map_widget.update_location(
                        lat=50.1109,
                        lon=8.6821,
                        ip="198.51.100.42",
                        city="Frankfurt",
                        country="Germany",
                        isp="AetherNet Cloud Services"
                    )
            except Exception as e:
                print(f"Skipping {name} ({lang}): {e}")
                continue

            widget.setStyleSheet(ThemeManager.get_theme_stylesheet("cyber_dark"))
            widget.resize(1100, 700)
            widget.show()

            app.processEvents()

            pixmap = widget.grab()
            out_file = screenshots_dir / f"{name}_{lang}.png"
            pixmap.save(str(out_file))
            print(f"[OK] Captured anonymized screenshot: {out_file}")
            widget.close()

if __name__ == "__main__":
    capture_screenshots()
