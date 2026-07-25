from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt

class EnvironmentView(QWidget):
    """Nearby Wireless Environment Scanner View"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("Çevredeki Kablosuz Ağlar (Ortam Taraması)")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        btn_scan = QPushButton("🔍 Ağları Tara")
        btn_scan.setProperty("class", "btn-primary")
        btn_scan.clicked.connect(self.scan_environment)
        header_layout.addWidget(btn_scan)

        layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "SSID", "BSSID (MAC)", "Sinyal (%)", "Sinyal (dBm)", "Kanal", "Frekans Bandı", "Güvenlik Tipi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.scan_environment()

    def scan_environment(self):
        networks = self.adapter.scan_networks()
        self.table.setRowCount(len(networks))

        for idx, net in enumerate(networks):
            self.table.setItem(idx, 0, QTableWidgetItem(net.ssid))
            self.table.setItem(idx, 1, QTableWidgetItem(net.bssid))
            self.table.setItem(idx, 2, QTableWidgetItem(f"{net.signal_percent} %"))
            self.table.setItem(idx, 3, QTableWidgetItem(f"{net.signal_dbm} dBm"))
            self.table.setItem(idx, 4, QTableWidgetItem(str(net.channel)))
            self.table.setItem(idx, 5, QTableWidgetItem(net.band))
            self.table.setItem(idx, 6, QTableWidgetItem(f"{net.security} ({net.cipher})"))
