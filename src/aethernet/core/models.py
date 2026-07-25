from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class NetworkInterfaceInfo:
    name: str
    description: str
    mac_address: str
    is_wifi: bool = False
    is_enabled: bool = True
    is_connected: bool = False
    driver_provider: Optional[str] = None
    driver_version: Optional[str] = None
    driver_date: Optional[str] = None
    supported_standards: List[str] = field(default_factory=list) # e.g. 802.11ax, 802.11ac
    supported_bands: List[str] = field(default_factory=list) # 2.4 GHz, 5 GHz, 6 GHz
    ipv4_address: Optional[str] = None
    ipv4_subnet: Optional[str] = None
    ipv4_gateway: Optional[str] = None
    dns_servers: List[str] = field(default_factory=list)
    dhcp_enabled: bool = True

@dataclass
class WifiConnectionDetails:
    adapter_name: str
    ssid: str
    bssid: str
    state: str  # connected, disconnected, associating
    signal_percent: int  # 0 - 100
    signal_dbm: int      # e.g. -65
    radio_type: str      # 802.11ax, 802.11ac, etc.
    channel: int
    frequency_ghz: float # 2.412, 5.180, etc.
    channel_width_mhz: int # 20, 40, 80, 160
    receive_rate_mbps: float
    transmit_rate_mbps: float
    security_protocol: str # WPA3-Personal, WPA2-Personal, Open, WEP
    cipher: str            # CCMP, GCMP-256, TKIP
    authentication: str    # WPA2-PSK, WPA3-SAE, 802.1X
    uptime_seconds: int = 0
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0

@dataclass
class WifiProfile:
    name: str
    ssid: str
    security_type: str
    auto_connect: bool = True
    is_hidden: bool = False
    password: Optional[str] = None

@dataclass
class ScannedNetwork:
    ssid: str
    bssid: str
    signal_percent: int
    signal_dbm: int
    channel: int
    band: str # "2.4 GHz", "5 GHz", "6 GHz"
    security: str
    cipher: str
    vendor: Optional[str] = None
    is_hidden: bool = False
    last_seen: datetime = field(default_factory=datetime.now)

@dataclass
class DiscoveredDevice:
    ip: str
    mac: str
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    device_type: str = "Bilinmiyor" # Telefon, Bilgisayar, Router, IoT, vb.
    open_ports: List[int] = field(default_factory=list)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    is_online: bool = True
    custom_label: Optional[str] = None
