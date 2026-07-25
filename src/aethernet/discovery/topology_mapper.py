"""Network Topology Mapper for constructing node visual hierarchies."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class TopologyNode:
    id: str
    ip: str
    mac: str
    hostname: str
    device_type: str  # Gateway, Router, Switch, PC, Phone, IoT
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)


class NetworkTopologyMapper:
    """Constructs network node relationship tree from ARP/Gateway scan data."""

    def __init__(self):
        pass

    def build_topology(self, gateway_ip: str, gateway_mac: str, discovered_devices: List[Dict[str, str]]) -> Dict[str, TopologyNode]:
        """Build hierarchical node tree placing Gateway as root node."""
        nodes: Dict[str, TopologyNode] = {}

        # Root Gateway Node
        gw_id = f"gw_{gateway_ip}"
        nodes[gw_id] = TopologyNode(
            id=gw_id,
            ip=gateway_ip,
            mac=gateway_mac,
            hostname="Network Gateway / Router",
            device_type="Gateway",
            parent_id=None
        )

        for dev in discovered_devices:
            ip = dev.get("ip", "0.0.0.0")
            mac = dev.get("mac", "00:00:00:00:00:00")
            hostname = dev.get("hostname", ip)
            dtype = dev.get("device_type", "Host")

            if ip == gateway_ip:
                continue

            node_id = f"node_{ip}"
            nodes[node_id] = TopologyNode(
                id=node_id,
                ip=ip,
                mac=mac,
                hostname=hostname,
                device_type=dtype,
                parent_id=gw_id
            )
            nodes[gw_id].children.append(node_id)

        return nodes
