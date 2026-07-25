import subprocess
import re
import psutil
from typing import List, Optional
from loguru import logger

from aethernet.platform.base import BasePlatformAdapter
from aethernet.core.models import (
    NetworkInterfaceInfo,
    WifiConnectionDetails,
    WifiProfile,
    ScannedNetwork,
)

class WindowsPlatformAdapter(BasePlatformAdapter):
    """Windows implementation of WiFi and network operations using netsh and Win32 tools"""

    def _run_netsh(self, args: List[str]) -> str:
        """Helper to run netsh command with UTF-8 / CP857/CP1254 fallback decoding"""
        cmd = ["netsh"] + args
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Try utf-8 first, fallback to cp857 / cp1254 for Turkish Windows
            for encoding in ["utf-8", "cp857", "cp1254", "latin-1"]:
                try:
                    return res.stdout.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return res.stdout.decode("utf-8", errors="replace")
        except Exception as e:
            logger.error(f"Error running netsh {args}: {e}")
            return ""

    def get_interfaces(self) -> List[NetworkInterfaceInfo]:
        interfaces = []
        ps_addrs = psutil.net_if_addrs()
        ps_stats = psutil.net_if_stats()

        # Call netsh wlan show interfaces to flag WiFi adapters
        netsh_output = self._run_netsh(["wlan", "show", "interfaces"])
        wifi_names = set(re.findall(r"^\s*Name\s*:\s*(.+)$", netsh_output, re.MULTILINE))

        for name, addrs in ps_addrs.items():
            mac = ""
            ipv4 = ""
            subnet = ""
            for addr in addrs:
                if addr.family.name == "AF_LINK":
                    mac = addr.address
                elif addr.family.name == "AF_INET":
                    ipv4 = addr.address
                    subnet = addr.netmask

            stat = ps_stats.get(name)
            is_enabled = stat.isup if stat else False
            is_wifi = name in wifi_names or "wi-fi" in name.lower() or "wlan" in name.lower()

            interfaces.append(
                NetworkInterfaceInfo(
                    name=name,
                    description=name,
                    mac_address=mac or "N/A",
                    is_wifi=is_wifi,
                    is_enabled=is_enabled,
                    is_connected=is_enabled and bool(ipv4),
                    supported_standards=["802.11n", "802.11ac", "802.11ax"] if is_wifi else [],
                    supported_bands=["2.4 GHz", "5 GHz", "6 GHz"] if is_wifi else [],
                    ipv4_address=ipv4 or None,
                    ipv4_subnet=subnet or None,
                )
            )
        return interfaces

    def get_current_connection(self) -> Optional[WifiConnectionDetails]:
        output = self._run_netsh(["wlan", "show", "interfaces"])
        if not output or "State" not in output:
            return None

        # Check if connected
        state_match = re.search(r"^\s*State\s*:\s*(.+)$", output, re.MULTILINE)
        state = state_match.group(1).strip() if state_match else "disconnected"

        if "connected" not in state.lower():
            return None

        def extract(pattern: str, default: str = "") -> str:
            m = re.search(pattern, output, re.MULTILINE)
            return m.group(1).strip() if m else default

        ssid = extract(r"^\s*SSID\s*:\s*(.+)$")
        bssid = extract(r"^\s*BSSID\s*:\s*(.+)$")
        radio = extract(r"^\s*Radio type\s*:\s*(.+)$", "802.11ax")
        channel_str = extract(r"^\s*Channel\s*:\s*(.+)$", "0")
        signal_str = extract(r"^\s*Signal\s*:\s*(\d+)%", "0")
        rx_str = extract(r"^\s*Receive rate \(Mbps\)\s*:\s*(.+)$", "0")
        tx_str = extract(r"^\s*Transmit rate \(Mbps\)\s*:\s*(.+)$", "0")
        auth = extract(r"^\s*Authentication\s*:\s*(.+)$", "WPA2-Personal")
        cipher = extract(r"^\s*Cipher\s*:\s*(.+)$", "CCMP")
        adapter_name = extract(r"^\s*Name\s*:\s*(.+)$", "Wi-Fi")

        try:
            channel = int(channel_str)
        except ValueError:
            channel = 0

        try:
            signal_pct = int(signal_str)
        except ValueError:
            signal_pct = 0

        # Rough dBm calculation from percent: dBm ≈ (percent / 2) - 100
        signal_dbm = (signal_pct // 2) - 100 if signal_pct > 0 else -100

        try:
            rx_rate = float(rx_str)
            tx_rate = float(tx_str)
        except ValueError:
            rx_rate, tx_rate = 0.0, 0.0

        # Frequency calculation based on channel
        freq = 2.412 + (channel - 1) * 0.005 if 1 <= channel <= 14 else (5.180 + (channel - 36) * 0.005 if channel >= 36 else 5.0)

        # Retrieve cumulative byte stats via psutil
        io_counters = psutil.net_io_counters(pernic=True)
        adapter_io = io_counters.get(adapter_name)

        return WifiConnectionDetails(
            adapter_name=adapter_name,
            ssid=ssid,
            bssid=bssid,
            state=state,
            signal_percent=signal_pct,
            signal_dbm=signal_dbm,
            radio_type=radio,
            channel=channel,
            frequency_ghz=round(freq, 3),
            channel_width_mhz=80 if "ax" in radio.lower() or "ac" in radio.lower() else 20,
            receive_rate_mbps=rx_rate,
            transmit_rate_mbps=tx_rate,
            security_protocol=auth,
            cipher=cipher,
            authentication=auth,
            bytes_sent=adapter_io.bytes_sent if adapter_io else 0,
            bytes_recv=adapter_io.bytes_recv if adapter_io else 0,
            packets_sent=adapter_io.packets_sent if adapter_io else 0,
            packets_recv=adapter_io.packets_recv if adapter_io else 0,
        )

    def get_saved_profiles(self, include_passwords: bool = False) -> List[WifiProfile]:
        output = self._run_netsh(["wlan", "show", "profiles"])
        profile_names = re.findall(r"All User Profile\s*:\s*(.+)", output)
        if not profile_names:
            profile_names = re.findall(r"Tüm Kullanıcı Profili\s*:\s*(.+)", output)

        profiles = []
        for p_name in profile_names:
            p_name = p_name.strip()
            password = None
            sec_type = "WPA2-Personal"

            if include_passwords:
                detail_out = self._run_netsh(["wlan", "show", "profile", f'name="{p_name}"', "key=clear"])
                pass_match = re.search(r"Key Content\s*:\s*(.+)", detail_out)
                if not pass_match:
                    pass_match = re.search(r"Anahtar İçeriği\s*:\s*(.+)", detail_out)
                if pass_match:
                    password = pass_match.group(1).strip()

                sec_match = re.search(r"Authentication\s*:\s*(.+)", detail_out)
                if not sec_match:
                    sec_match = re.search(r"Kimlik doğrulaması\s*:\s*(.+)", detail_out)
                if sec_match:
                    sec_type = sec_match.group(1).strip()

            profiles.append(
                WifiProfile(
                    name=p_name,
                    ssid=p_name,
                    security_type=sec_type,
                    password=password
                )
            )
        return profiles

    def scan_networks(self) -> List[ScannedNetwork]:
        output = self._run_netsh(["wlan", "show", "networks", "mode=bssid"])
        scanned = []
        
        # Split by SSID blocks
        ssid_blocks = re.split(r"SSID \d+ : ", output)[1:]
        for block in ssid_blocks:
            lines = block.splitlines()
            if not lines:
                continue
            ssid = lines[0].strip()
            if not ssid:
                ssid = "<Gizli Ağ>"
                is_hidden = True
            else:
                is_hidden = False

            sec_match = re.search(r"Authentication\s*:\s*(.+)", block)
            if not sec_match:
                sec_match = re.search(r"Kimlik doğrulama\s*:\s*(.+)", block)
            security = sec_match.group(1).strip() if sec_match else "Unknown"

            cipher_match = re.search(r"Encryption\s*:\s*(.+)", block)
            if not cipher_match:
                cipher_match = re.search(r"Şifreleme\s*:\s*(.+)", block)
            cipher = cipher_match.group(1).strip() if cipher_match else "CCMP"

            # Parse BSSIDs
            bssid_blocks = re.split(r"BSSID \d+\s*:\s*", block)[1:]
            for b_block in bssid_blocks:
                b_lines = b_block.splitlines()
                bssid = b_lines[0].strip()
                
                sig_match = re.search(r"Signal\s*:\s*(\d+)%", b_block)
                if not sig_match:
                    sig_match = re.search(r"Sinyal\s*:\s*(\d+)%", b_block)
                sig_pct = int(sig_match.group(1)) if sig_match else 0
                sig_dbm = (sig_pct // 2) - 100 if sig_pct > 0 else -100

                chan_match = re.search(r"Channel\s*:\s*(\d+)", b_block)
                if not chan_match:
                    chan_match = re.search(r"Kanal\s*:\s*(\d+)", b_block)
                chan = int(chan_match.group(1)) if chan_match else 1

                band = "5 GHz" if chan >= 36 else ("6 GHz" if chan > 14 else "2.4 GHz")

                scanned.append(
                    ScannedNetwork(
                        ssid=ssid,
                        bssid=bssid,
                        signal_percent=sig_pct,
                        signal_dbm=sig_dbm,
                        channel=chan,
                        band=band,
                        security=security,
                        cipher=cipher,
                        is_hidden=is_hidden
                    )
                )
        return scanned

    def connect_profile(self, ssid: str) -> bool:
        res = self._run_netsh(["wlan", "connect", f'name="{ssid}"'])
        return "successfully" in res.lower() or "başarıyla" in res.lower()

    def disconnect(self, interface_name: Optional[str] = None) -> bool:
        cmd = ["wlan", "disconnect"]
        if interface_name:
            cmd.append(f'interface="{interface_name}"')
        res = self._run_netsh(cmd)
        return "successfully" in res.lower() or "başarıyla" in res.lower()

    def set_adapter_state(self, adapter_name: str, enable: bool) -> bool:
        state = "enable" if enable else "disable"
        try:
            cmd = ["netsh", "interface", "set", "interface", f'name="{adapter_name}"', f"admin={state}"]
            res = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return res.returncode == 0
        except Exception as e:
            logger.error(f"Failed to set adapter state: {e}")
            return False
