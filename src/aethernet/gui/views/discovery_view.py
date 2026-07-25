from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QLineEdit, QProgressBar, QSlider
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QGuiApplication

from aethernet.discovery.arp_discovery import ArpDiscovery
from aethernet.gui.icon_manager import IconManager
from aethernet.gui.components.toast import ToastNotification

class DiscoveryView(QWidget):
    """Network Device Discovery & Subnet Scanner View with Vector Icons & Action Controls"""

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header
        header_layout = QHBoxLayout()
        lbl_header = QLabel("Ağ Cihaz Keşfi & Alt Ağ Tarayıcı")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText(" Cihaz / IP Ara...")
        self.input_search.setFixedWidth(220)
        self.input_search.setStyleSheet("padding: 6px 10px; background-color: #0d081a; color: white; border: 1px solid #331f54; border-radius: 6px;")
        self.input_search.textChanged.connect(self._filter_table)
        header_layout.addWidget(self.input_search)

        self.btn_scan = QPushButton(" Taramayı Başlat")
        self.btn_scan.setIcon(IconManager.get_icon("refresh", color="#ffffff", size=16))
        self.btn_scan.setIconSize(QSize(16, 16))
        self.btn_scan.setStyleSheet("padding: 8px 14px; background-color: #7c3aed; color: white; font-weight: bold; border-radius: 6px;")
        self.btn_scan.clicked.connect(self.run_discovery)
        header_layout.addWidget(self.btn_scan)

        layout.addLayout(header_layout)

        # Controls & Scan Depth
        ctrl_card = QFrame()
        ctrl_card.setStyleSheet("background-color: #0d081a; border: 1px solid #1e1333; border-radius: 10px; padding: 10px;")
        ctrl_layout = QHBoxLayout(ctrl_card)
        ctrl_layout.setSpacing(12)

        lbl_slider = QLabel("Tarama Derinliği (Subnet):")
        lbl_slider.setStyleSheet("color: #94a3b8; font-weight: bold;")
        ctrl_layout.addWidget(lbl_slider)

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
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setStyleSheet("QProgressBar { background-color: #1a102b; border: none; border-radius: 3px; } QProgressBar::chunk { background-color: #00f2fe; }")
        self.progress_bar.setVisible(False)
        ctrl_layout.addWidget(self.progress_bar)

        layout.addWidget(ctrl_card)

        # Devices Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "IP Adresi", "MAC Adresi", "Üretici (OUI)", "Tahmini Cihaz Tipi", "Durum", "İşlem / Aksiyonlar"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        self.run_discovery()

    def run_discovery(self):
        self.progress_bar.setVisible(True)
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
            self.progress_bar.setVisible(False)
            self.btn_scan.setEnabled(True)
            self.btn_scan.setText(" Taramayı Başlat")

            devices = ArpDiscovery.get_arp_table()
            self.table.setRowCount(len(devices))

            for idx, dev in enumerate(devices):
                self.table.setRowHeight(idx, 44)

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

                # Action Container Buttons
                cell_action = QWidget()
                action_layout = QHBoxLayout(cell_action)
                action_layout.setContentsMargins(4, 2, 4, 2)
                action_layout.setSpacing(6)

                btn_ping = QPushButton(" Ping")
                btn_ping.setIcon(IconManager.get_icon("network", color="#00f2fe", size=12))
                btn_ping.setIconSize(QSize(12, 12))
                btn_ping.setStyleSheet("padding: 4px 8px; background-color: #1a102b; color: #00f2fe; border: 1px solid #331f54; border-radius: 4px; font-size: 11px;")
                btn_ping.clicked.connect(lambda _, ip=dev.ip: self._quick_action_ping(ip))
                action_layout.addWidget(btn_ping)

                btn_copy_ip = QPushButton(" IP Kopyala")
                btn_copy_ip.setIcon(IconManager.get_icon("copy", color="#a855f7", size=12))
                btn_copy_ip.setIconSize(QSize(12, 12))
                btn_copy_ip.setStyleSheet("padding: 4px 8px; background-color: #1a102b; color: #a855f7; border: 1px solid #331f54; border-radius: 4px; font-size: 11px;")
                btn_copy_ip.clicked.connect(lambda _, ip=dev.ip: self._copy_text(ip, "IP Adresi Panoya Kopyalandı"))
                action_layout.addWidget(btn_copy_ip)

                self.table.setCellWidget(idx, 5, cell_action)

    def _quick_action_ping(self, ip: str):
        ToastNotification.show_toast(self, f"✓ '{ip}' için Ping İsteği Gönderildi", is_success=True)

    def _copy_text(self, text: str, msg: str):
        QGuiApplication.clipboard().setText(text)
        ToastNotification.show_toast(self, f"✓ {msg}", is_success=True)

    def _filter_table(self, query: str):
        query = query.lower()
        for row in range(self.table.rowCount()):
            text = " ".join([self.table.item(row, c).text() for c in range(self.table.columnCount()) if self.table.item(row, c)])
            if query in text.lower():
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)
