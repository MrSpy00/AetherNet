"""Network Topology Visualization View for AetherNet with Interactive Glowing Canvas."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsItem, QSplitter
)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter, QRadialGradient
from aethernet.discovery.topology_mapper import NetworkTopologyMapper
from aethernet.discovery.arp_discovery import ArpDiscovery
import math

class GlowingNodeItem(QGraphicsEllipseItem):
    """Interactive Node Item on Topology Graph Canvas"""

    def __init__(self, x, y, radius, label: str, ip: str, node_type: str = "device", parent=None):
        super().__init__(-radius, -radius, radius * 2, radius * 2, parent)
        self.setPos(x, y)
        self.radius = radius
        self.label_text = label
        self.ip = ip
        self.node_type = node_type

        self.setFlags(
            QGraphicsItem.ItemIsMovable |
            QGraphicsItem.ItemIsSelectable |
            QGraphicsItem.ItemSendsGeometryChanges
        )

        # Set Colors
        if node_type == "gateway":
            self.main_color = QColor(0, 242, 254)       # Neon Cyan
        elif node_type == "wifi":
            self.main_color = QColor(56, 189, 248)      # Sky Blue
        elif node_type == "server":
            self.main_color = QColor(168, 85, 247)      # Neon Purple
        else:
            self.main_color = QColor(74, 222, 128)      # Emerald Green

        self.setPen(QPen(self.main_color, 2.5))
        self.setBrush(QBrush(QColor(16, 25, 42)))

        # Text Label
        self.text_item = QGraphicsTextItem(f"{label}\n({ip})", self)
        self.text_item.setDefaultTextColor(QColor(248, 250, 252))
        font = QFont("Segoe UI", 9, QFont.Bold)
        self.text_item.setFont(font)
        self.text_item.setPos(-radius, radius + 4)

        self.lines = []

    def add_line(self, line_item):
        self.lines.append(line_item)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for line in self.lines:
                line.update_positions()
        return super().itemChange(change, value)


class ConnectingLineItem(QGraphicsLineItem):
    """Glowing Line Connector between Nodes"""

    def __init__(self, node1: GlowingNodeItem, node2: GlowingNodeItem, parent=None):
        super().__init__(parent)
        self.node1 = node1
        self.node2 = node2
        self.setPen(QPen(QColor(0, 242, 254, 160), 2, Qt.DashLine))
        self.node1.add_line(self)
        self.node2.add_line(self)
        self.update_positions()

    def update_positions(self):
        self.setLine(
            self.node1.pos().x(), self.node1.pos().y(),
            self.node2.pos().x(), self.node2.pos().y()
        )


class TopologyView(QWidget):
    """Network Topology Visual & Tree Map View."""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n
        self.mapper = NetworkTopologyMapper()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        lbl_header = QLabel("🌐 Görsel Ağ Topolojisi Haritası")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        btn_refresh = QPushButton("🔄 Topolojiyi Yenile")
        btn_refresh.setProperty("class", "btn-primary")
        btn_refresh.clicked.connect(self.refresh_topology)
        header_layout.addWidget(btn_refresh)

        layout.addLayout(header_layout)

        # Splitter: Graph Canvas (Top) + Tree Breakdown (Bottom)
        splitter = QSplitter(Qt.Vertical)

        # Interactive Graphics View
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QBrush(QColor(8, 11, 16)))

        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.graphics_view.setStyleSheet("border: 1px solid #1a2336; border-radius: 10px; background-color: #080b10;")

        splitter.addWidget(self.graphics_view)

        # Tree breakdown table
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Cihaz / Host", "IP Adresi", "MAC Adresi", "Cihaz Tipi"])
        self.tree_widget.setColumnWidth(0, 250)
        self.tree_widget.setColumnWidth(1, 150)
        self.tree_widget.setColumnWidth(2, 180)
        splitter.addWidget(self.tree_widget)

        splitter.setSizes([450, 200])
        layout.addWidget(splitter)

        self.refresh_topology()

    def refresh_topology(self):
        self.scene.clear()
        self.tree_widget.clear()

        devices = ArpDiscovery.get_arp_table()

        # Gateway node at center
        gw_ip = "192.168.1.1"
        gw_mac = "00:11:22:33:44:55"

        nodes = self.mapper.build_topology(
            gateway_ip=gw_ip,
            gateway_mac=gw_mac,
            discovered_devices=devices
        )

        gw_node_item = GlowingNodeItem(0, 0, 26, "Ana Ağ Geçidi (Gateway)", gw_ip, "gateway")
        self.scene.addItem(gw_node_item)

        # Populate tree root
        gw_node = nodes.get(f"gw_{gw_ip}")
        if gw_node:
            root_item = QTreeWidgetItem([gw_node.hostname, gw_node.ip, gw_node.mac, gw_node.device_type])
            self.tree_widget.addTopLevelItem(root_item)

            children_count = len(gw_node.children)
            radius = 180

            for i, child_id in enumerate(gw_node.children):
                cnode = nodes[child_id]
                child_item = QTreeWidgetItem([cnode.hostname, cnode.ip, cnode.mac, cnode.device_type])
                root_item.addChild(child_item)

                # Radial layout on graphic scene
                angle = (2 * math.pi / max(children_count, 1)) * i
                cx = radius * math.cos(angle)
                cy = radius * math.sin(angle)

                node_type = "wifi" if "wifi" in cnode.hostname.lower() else "device"
                device_node_item = GlowingNodeItem(cx, cy, 20, cnode.hostname, cnode.ip, node_type)
                self.scene.addItem(device_node_item)

                # Connect line
                line = ConnectingLineItem(gw_node_item, device_node_item)
                self.scene.addItem(line)

            self.tree_widget.expandAll()
