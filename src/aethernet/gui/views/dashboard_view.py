from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from aethernet.gui.components.stat_card import StatCard
from aethernet.gui.components.graph_widget import LiveSignalGraphWidget

class DashboardView(QWidget):
    """Dashboard Main Overview View"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title Row
        header_row = QHBoxLayout()
        lbl_header = QLabel("⚡ Ağ ve WiFi Kontrol Paneli")
        lbl_header.setStyleSheet("font-size: 22px; font-weight: 800; color: #f8fafc;")
        header_row.addWidget(lbl_header)

        header_row.addStretch()

        btn_quick_scan = QPushButton("🔍 Çevreyi Tara")
        btn_quick_scan.setProperty("class", "btn-secondary")
        header_row.addWidget(btn_quick_scan)

        layout.addLayout(header_row)

        # Top Metric Stat Cards Grid
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_status = StatCard(self.i18n.t("status_connected"), "--", "SSID", "#00f2fe")
        self.card_signal = StatCard(self.i18n.t("signal_strength"), "-- %", "-- dBm", "#38bdf8")
        self.card_security = StatCard(self.i18n.t("security_score"), "-- / 100", "Güvenlik Puanı", "#4ade80")
        self.card_devices = StatCard(self.i18n.t("devices_online"), "-- Cihaz", "Yerel Ağ", "#a855f7")

        cards_layout.addWidget(self.card_status)
        cards_layout.addWidget(self.card_signal)
        cards_layout.addWidget(self.card_security)
        cards_layout.addWidget(self.card_devices)
        layout.addLayout(cards_layout)

        # Middle Content: Live Graph + Connection Card
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(16)

        self.graph_widget = LiveSignalGraphWidget("Canlı Sinyal Gücü Geçmişi (60 Saniye)")
        mid_layout.addWidget(self.graph_widget, stretch=3)

        # Quick Active Connection Summary Box
        self.summary_box = QFrame()
        self.summary_box.setProperty("class", "glass-panel")
        self.summary_box.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 18px;")
        box_layout = QVBoxLayout(self.summary_box)

        lbl_summary_title = QLabel("<b>Aktif Bağlantı Detayları</b>")
        lbl_summary_title.setStyleSheet("font-size: 15px; color: #00f2fe;")
        box_layout.addWidget(lbl_summary_title)

        self.lbl_details = QLabel("Tarama yapılıyor...")
        self.lbl_details.setWordWrap(True)
        self.lbl_details.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 1.6;")
        box_layout.addWidget(self.lbl_details)
        box_layout.addStretch()

        mid_layout.addWidget(self.summary_box, stretch=2)
        layout.addLayout(mid_layout)

    def refresh_data(self):
        conn = self.adapter.get_current_connection()
        if conn:
            self.card_status.set_value("Bağlı", conn.ssid, "OK")
            self.card_signal.set_value(f"{conn.signal_percent} %", f"{conn.signal_dbm} dBm | Kanal {conn.channel}")
            self.graph_widget.add_data_point(conn.signal_percent)

            detail_text = (
                f"<b>SSID:</b> <span style='color:#00f2fe;'>{conn.ssid}</span><br>"
                f"<b>BSSID:</b> {conn.bssid}<br>"
                f"<b>Radyo Tipi:</b> {conn.radio_type}<br>"
                f"<b>Güvenlik:</b> <span style='color:#4ade80;'>{conn.security_protocol}</span><br>"
                f"<b>Şifreleme:</b> {conn.cipher}<br>"
                f"<b>Alma / Gönderme:</b> {conn.receive_rate_mbps} / {conn.transmit_rate_mbps} Mbps<br>"
                f"<b>Frekans Bandı:</b> {conn.frequency_ghz} GHz"
            )
            self.lbl_details.setText(detail_text)
        else:
            self.card_status.set_value("Bağlı Değil", "Hiçbir ağa bağlı değilsiniz", "OFFLINE")
            self.card_signal.set_value("0 %", "-100 dBm")
            self.graph_widget.add_data_point(0)
            self.lbl_details.setText("<span style='color:#ef4444;'>Aktif bir kablosuz ağ bağlantısı bulunamadı.</span>")
