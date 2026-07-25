from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from aethernet.discovery.arp_discovery import ArpDiscovery

class DiscoveryView(QWidget):
    """Local LAN Device Inventory & Discovery View"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("Yerel Ağ Cihaz Keşfi (ARP Envanteri)")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        btn_scan = QPushButton("📡 Taramayı Başlat")
        btn_scan.setProperty("class", "btn-primary")
        btn_scan.clicked.connect(self.run_discovery)
        header_layout.addWidget(btn_scan)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "IP Adresi", "MAC Adresi", "Üretici (OUI)", "Tahmini Cihaz Tipi", "Durum"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.run_discovery()

    def run_discovery(self):
        devices = ArpDiscovery.get_arp_table()
        self.table.setRowCount(len(devices))

        for idx, dev in enumerate(devices):
            self.table.setItem(idx, 0, QTableWidgetItem(dev.ip))
            self.table.setItem(idx, 1, QTableWidgetItem(dev.mac))
            self.table.setItem(idx, 2, QTableWidgetItem(dev.vendor or "Bilinmiyor"))
            self.table.setItem(idx, 3, QTableWidgetItem(dev.device_type))
            self.table.setItem(idx, 4, QTableWidgetItem("🟢 Çevrimiçi" if dev.is_online else "🔴 Çevrimdışı"))
