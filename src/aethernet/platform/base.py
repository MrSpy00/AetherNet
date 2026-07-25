from abc import ABC, abstractmethod
from typing import List, Optional
from aethernet.core.models import (
    NetworkInterfaceInfo,
    WifiConnectionDetails,
    WifiProfile,
    ScannedNetwork,
)

class BasePlatformAdapter(ABC):
    """Platform-independent abstract interface for WiFi operations"""

    @abstractmethod
    def get_interfaces(self) -> List[NetworkInterfaceInfo]:
        """Sistemdeki tüm ağ arayüzlerini ve WiFi adaptörlerini döndürür"""
        pass

    @abstractmethod
    def get_current_connection(self) -> Optional[WifiConnectionDetails]:
        """Aktif WiFi bağlantı detaylarını döndürür"""
        pass

    @abstractmethod
    def get_saved_profiles(self, include_passwords: bool = False) -> List[WifiProfile]:
        """Kayıtlı WiFi profillerini döndürür"""
        pass

    @abstractmethod
    def scan_networks(self) -> List[ScannedNetwork]:
        """Çevredeki kablosuz ağları tarar ve liste olarak döndürür"""
        pass

    @abstractmethod
    def connect_profile(self, ssid: str) -> bool:
        """Kayıtlı bir ağa bağlanmayı tetikler"""
        pass

    @abstractmethod
    def disconnect(self, interface_name: Optional[str] = None) -> bool:
        """Mevcut WiFi bağlantısını keser"""
        pass

    @abstractmethod
    def set_adapter_state(self, adapter_name: str, enable: bool) -> bool:
        """Adaptörü yazılımsal olarak açar veya kapatır"""
        pass
