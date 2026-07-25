from dataclasses import dataclass
from typing import List, Dict
from aethernet.core.models import ScannedNetwork

@dataclass
class RogueApAlert:
    target_ssid: str
    legitimate_bssid: str
    rogue_bssid: str
    channel: int
    signal_dbm: int
    description: str

class RogueApDetector:
    """Evil Twin / Sahte AP tespit motoru"""

    @staticmethod
    def detect_evil_twins(scanned_networks: List[ScannedNetwork], known_home_bssid: str = "") -> List[RogueApAlert]:
        alerts: List[RogueApAlert] = []

        # Group networks by SSID
        ssid_map: Dict[str, List[ScannedNetwork]] = {}
        for net in scanned_networks:
            if not net.ssid or net.is_hidden or net.ssid == "<Gizli Ağ>":
                continue
            ssid_map.setdefault(net.ssid, []).append(net)

        for ssid, nets in ssid_map.items():
            if len(nets) > 1:
                # Multiple BSSIDs broadcasting identical SSID
                bssids = [n.bssid for n in nets]
                channels = [n.channel for n in nets]
                sec_types = set(n.security for n in nets)

                # Flag if security protocol differs across same SSID or unfamiliar BSSID matches known home SSID
                if len(sec_types) > 1 or (known_home_bssid and known_home_bssid not in bssids):
                    for net in nets:
                        if net.bssid != known_home_bssid:
                            alerts.append(
                                RogueApAlert(
                                    target_ssid=ssid,
                                    legitimate_bssid=known_home_bssid or bssids[0],
                                    rogue_bssid=net.bssid,
                                    channel=net.channel,
                                    signal_dbm=net.signal_dbm,
                                    description=f"Aynı SSID ('{ssid}') farklı güvenlik veya BSSID ({net.bssid}) ile yayın yapıyor!"
                                )
                            )
        return alerts
