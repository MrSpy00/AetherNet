from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QProgressBar, QSlider, QFrame
)
from PySide6.QtCore import Qt, QTimer, QSize
from aethernet.discovery.arp_discovery import ArpDiscovery
from aethernet.gui.icon_manager import IconManager

class DiscoveryView(QWidget):
    """Local LAN Device Inventory & Discovery View with Vector Icons"""

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

        header_layout.addStretch()

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText(" Cihaz veya IP Ara...")
        self.input_search.setFixedWidth(220)
        self.input_search.textChanged.connect(self._filter_table)
        header_layout.addWidget(self.input_search)

        self.btn_scan = QPushButton(" Taramayı Başlat")
        self.btn_scan.setIcon(IconManager.get_icon("search", color="#ffffff", size=16))
        self.btn_scan.setIconSize(QSize(16, 16))
        self.btn_scan.setProperty("class", "btn-primary")
        self.btn_scan.clicked.connect(self.run_discovery)
        header_layout.addWidget(self.btn_scan)

        layout.addLayout(header_layout)

        # Control Panel: Scan Depth Slider + Progress Bar
        ctrl_card = QFrame()
        ctrl_card.setProperty("class", "glass-panel")
        ctrl_card.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 10px; padding: 12px 16px;")
        ctrl_layout = QHBoxLayout(ctrl_card)

        ctrl_layout.addWidget(QLabel("Tarama Derinliği (Subnet /24):"))
        self.slider_depth = QSlider(Qt.Horizontal)
        self.slider_depth.setRange(1, 254)
        self.slider_depth.setValue(254)
        self.slider_depth.setFixedWidth(160)
        ctrl_layout.addWidget(self.slider_depth)

        self.lbl_depth_val = QLabel("254 IP")
        self.lbl_depth_val.setStyleSheet("color: #00f2fe; font-weight: bold; font-family: monospace;")
        self.slider_depth.valueChanged.connect(lambda v: self.lbl_depth_val.setText(f"{v} IP"))
        ctrl_layout.addWidget(self.lbl_depth_val)

        ctrl_layout.addSpacing(20)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(100)
        self.progress_bar.setFixedHeight(12)
        ctrl_layout.addWidget(self.progress_bar)

        layout.addWidget(ctrl_card)

        # Devices Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "IP Adresi", "MAC Adresi", "Üretici (OUI)", "Tahmini Cihaz Tipi", "Durum"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.run_discovery()

    def run_discovery(self):
        self.progress_bar.setValue(0)
        self.btn_scan.setEnabled(False)
        self.btn_scan.setText(" Taranıyor...")

        # Animated progress bar tick
        self.progress_val = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_progress_step)
        self.timer.start(30)

    def _on_progress_step(self):
        self.progress_val += 5
        self.progress_bar.setValue(self.progress_val)

        if self.progress_val >= 100:
            self.timer.stop()
            self.btn_scan.setEnabled(True)
            self.btn_scan.setText(" Taramayı Başlat")

            devices = ArpDiscovery.get_arp_table()
            self.table.setRowCount(len(devices))

            for idx, dev in enumerate(devices):
                self.table.setItem(idx, 0, QTableWidgetItem(dev.ip))
                self.table.setItem(idx, 1, QTableWidgetItem(dev.mac))
                
                vendor_text = dev.vendor or "Bilinmiyor"
                item_vendor = QTableWidgetItem(vendor_text)
                item_vendor.setIcon(IconManager.get_icon("discovery", color="#38bdf8", size=16))
                self.table.setItem(idx, 2, item_vendor)

                item_type = QTableWidgetItem(dev.device_type)
                item_type.setIcon(IconManager.get_icon("network", color="#00f2fe", size=16))
                self.table.setItem(idx, 3, item_type)

                status_str = "Çevrimiçi" if dev.is_online else "Çevrimdışı"
                item_status = QTableWidgetItem(status_str)
                color_hex = "#4ade80" if dev.is_online else "#ef4444"
                item_status.setIcon(IconManager.get_icon("wifi", color=color_hex, size=16))
                self.table.setItem(idx, 4, item_status)

    def _filter_table(self, query: str):
        query = query.lower()
        for row in range(self.table.rowCount()):
            text = " ".join([self.table.item(row, c).text() for c in range(self.table.columnCount()) if self.table.item(row, c)])
            if query in text.lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
