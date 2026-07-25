from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
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

        # Header Title
        lbl_header = QLabel("Ağ ve WiFi Kontrol Paneli")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(lbl_header)

        # Top Metric Stat Cards Grid
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_status = StatCard(self.i18n.t("status_connected"), "--", "SSID", "#00f2fe")
        self.card_signal = StatCard(self.i18n.t("signal_strength"), "-- %", "-- dBm", "#38bdf8")
        self.card_security = StatCard(self.i18n.t("security_score"), "-- / 100", "Ağ Güvensizliği", "#4ade80")
        self.card_devices = StatCard(self.i18n.t("devices_online"), "-- Cihaz", "Yerel Ağ", "#a855f7")

        cards_layout.addWidget(self.card_status)
        cards_layout.addWidget(self.card_signal)
        cards_layout.addWidget(self.card_security)
        cards_layout.addWidget(self.card_devices)
        layout.addLayout(cards_layout)

        # Middle Content: Live Graph + Details
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(16)

        self.graph_widget = LiveSignalGraphWidget("Canlı Sinyal Gücü Geçmişi (60 Saniye)")
        mid_layout.addWidget(self.graph_widget, stretch=3)

        # Quick Active Connection Summary Box
        self.summary_box = QWidget()
        self.summary_box.setStyleSheet("background-color: #141a26; border: 1px solid #1e293d; border-radius: 12px; padding: 16px;")
        box_layout = QVBoxLayout(self.summary_box)
        box_layout.addWidget(QLabel("<b>Aktif Bağlantı Detayları</b>"))
        
        self.lbl_details = QLabel("Tarama yapılıyor...")
        self.lbl_details.setWordWrap(True)
        self.lbl_details.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 1.5;")
        box_layout.addWidget(self.lbl_details)
        box_layout.addStretch()

        mid_layout.addWidget(self.summary_box, stretch=2)
        layout.addLayout(mid_layout)

    def refresh_data(self):
        conn = self.adapter.get_current_connection()
        if conn:
            self.card_status.set_value("Bağlı", conn.ssid)
            self.card_signal.set_value(f"{conn.signal_percent} %", f"{conn.signal_dbm} dBm | Kanal {conn.channel}")
            self.graph_widget.add_data_point(conn.signal_percent)

            detail_text = (
                f"<b>SSID:</b> {conn.ssid}<br>"
                f"<b>BSSID:</b> {conn.bssid}<br>"
                f"<b>Radyo Tipi:</b> {conn.radio_type}<br>"
                f"<b>Güvenlik:</b> {conn.security_protocol}<br>"
                f"<b>Şifreleme:</b> {conn.cipher}<br>"
                f"<b>Alma / Gönderme:</b> {conn.receive_rate_mbps} / {conn.transmit_rate_mbps} Mbps<br>"
                f"<b>Frekans:</b> {conn.frequency_ghz} GHz"
            )
            self.lbl_details.setText(detail_text)
        else:
            self.card_status.set_value("Bağlı Değil", "Hiçbir ağa bağlı değilsiniz")
            self.card_signal.set_value("0 %", "-100 dBm")
            self.graph_widget.add_data_point(0)
            self.lbl_details.setText("Aktif bir kablosuz ağ bağlantısı bulunamadı.")
