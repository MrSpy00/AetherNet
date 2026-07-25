"""Network Topology Visualization View for AetherNet."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem
)
from aethernet.discovery.topology_mapper import NetworkTopologyMapper
from aethernet.discovery.lan_scanner import LANScanner


class TopologyView(QWidget):
    """Network Topology Node Tree View."""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n
        self.mapper = NetworkTopologyMapper()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("Visual Network Topology / Ağ Haritası")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        btn_refresh = QPushButton("🔄 Topolojiyi Yenile")
        btn_refresh.setProperty("class", "btn-primary")
        btn_refresh.clicked.connect(self.refresh_topology)
        header_layout.addWidget(btn_refresh)

        layout.addLayout(header_layout)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Cihaz / Host", "IP Adresi", "MAC Adresi", "Cihaz Tipi"])
        self.tree_widget.setColumnWidth(0, 250)
        self.tree_widget.setColumnWidth(1, 150)
        self.tree_widget.setColumnWidth(2, 180)
        layout.addWidget(self.tree_widget)

        self.refresh_topology()

    def refresh_topology(self):
        self.tree_widget.clear()
        devices = LANScanner.scan_arp()

        # Build topology tree
        nodes = self.mapper.build_topology(
            gateway_ip="192.168.1.1",
            gateway_mac="00:11:22:33:44:55",
            discovered_devices=devices
        )

        gw_node = nodes.get("gw_192.168.1.1")
        if gw_node:
            root_item = QTreeWidgetItem([gw_node.hostname, gw_node.ip, gw_node.mac, gw_node.device_type])
            self.tree_widget.addTopLevelItem(root_item)

            for child_id in gw_node.children:
                cnode = nodes[child_id]
                child_item = QTreeWidgetItem([cnode.hostname, cnode.ip, cnode.mac, cnode.device_type])
                root_item.addChild(child_item)

            self.tree_widget.expandAll()
