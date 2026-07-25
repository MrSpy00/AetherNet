from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QSplitter
)
from PySide6.QtCore import Qt
import pyqtgraph as pg
from collections import Counter

class EnvironmentView(QWidget):
    """Nearby Wireless Environment Scanner View with Channel Spectrum Density Graph"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header Row
        header_layout = QHBoxLayout()
        lbl_header = QLabel("🔍 Çevredeki Kablosuz Ağlar (Spektrum Taraması)")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        btn_scan = QPushButton("⚡ Ağları Tara")
        btn_scan.setProperty("class", "btn-primary")
        btn_scan.clicked.connect(self.scan_environment)
        header_layout.addWidget(btn_scan)

        layout.addLayout(header_layout)

        # Channel Recommendation Banner Card
        self.banner = QFrame()
        self.banner.setProperty("class", "glass-panel")
        self.banner.setStyleSheet("background-color: #0e131f; border: 1px solid #00f2fe; border-radius: 10px; padding: 12px 16px;")
        banner_layout = QHBoxLayout(self.banner)

        self.lbl_recommendation = QLabel("💡 <b>Kanal Önerisi:</b> Taranıyor...")
        self.lbl_recommendation.setStyleSheet("color: #00f2fe; font-size: 13px;")
        banner_layout.addWidget(self.lbl_recommendation)
        layout.addWidget(self.banner)

        splitter = QSplitter(Qt.Vertical)

        # Pyqtgraph Channel Spectrum Bar Graph
        pg.setConfigOption('background', '#080b10')
        pg.setConfigOption('foreground', '#64748b')

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Ağ Sayısı', color='#94a3b8')
        self.plot_widget.setLabel('bottom', 'WiFi Kanalları (2.4 GHz / 5 GHz)', color='#94a3b8')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        self.plot_widget.setYRange(0, 10)
        self.bargraph = pg.BarGraphItem(x=[], height=[], width=0.6, brush='#00f2fe', pen='#38bdf8')
        self.plot_widget.addItem(self.bargraph)

        splitter.addWidget(self.plot_widget)

        # Networks Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "SSID", "BSSID (MAC)", "Sinyal (%)", "Sinyal (dBm)", "Kanal", "Frekans Bandı", "Güvenlik Tipi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        splitter.addWidget(self.table)

        splitter.setSizes([260, 340])
        layout.addWidget(splitter)

        self.scan_environment()

    def scan_environment(self):
        networks = self.adapter.scan_networks()
        self.table.setRowCount(len(networks))

        channel_counts = Counter()

        for idx, net in enumerate(networks):
            self.table.setItem(idx, 0, QTableWidgetItem(net.ssid or "<Gizli SSID>"))
            self.table.setItem(idx, 1, QTableWidgetItem(net.bssid))
            self.table.setItem(idx, 2, QTableWidgetItem(f"{net.signal_percent} %"))
            self.table.setItem(idx, 3, QTableWidgetItem(f"{net.signal_dbm} dBm"))
            self.table.setItem(idx, 4, QTableWidgetItem(str(net.channel)))
            self.table.setItem(idx, 5, QTableWidgetItem(net.band))
            self.table.setItem(idx, 6, QTableWidgetItem(f"{net.security} ({net.cipher})"))

            if net.channel > 0:
                channel_counts[net.channel] += 1

        # Update Bar Chart
        if channel_counts:
            channels = list(channel_counts.keys())
            counts = list(channel_counts.values())
            self.bargraph.setOpts(x=channels, height=counts)
            self.plot_widget.setYRange(0, max(counts) + 2)

            # Recommend least congested channel among 1, 6, 11
            ch1 = channel_counts.get(1, 0)
            ch6 = channel_counts.get(6, 0)
            ch11 = channel_counts.get(11, 0)
            best_ch = min([(ch1, 1), (ch6, 6), (ch11, 11)])[1]

            self.lbl_recommendation.setText(
                f"💡 <b>Kanal Analizi:</b> Çevrede <b>{len(networks)}</b> aktif kablosuz ağ bulundu. "
                f"En az çakışma olan en ideal 2.4GHz kanalı: <b style='color:#4ade80;'>Kanal {best_ch}</b>"
            )
        else:
            self.lbl_recommendation.setText("💡 <b>Kanal Analizi:</b> Yakınlarda yayın yapan aktif kablosuz ağ bulunamadı.")
