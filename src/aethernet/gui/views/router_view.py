import socket
import urllib.request
import re
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QSize
from PySide6.QtGui import QDesktopServices
from aethernet.gui.components.stat_card import StatCard
from aethernet.gui.icon_manager import IconManager
from aethernet.network_tools.ping_tool import PingTool

DEFAULT_ROUTER_CREDS = [
    {"brand": "Türk Telekom / TTNet", "ip": "192.168.1.1", "username": "admin", "password": "turktelekom / ttnet"},
    {"brand": "Superonline / Huawei", "ip": "192.168.1.1 / 192.168.2.1", "username": "admin", "password": "superonline / admin"},
    {"brand": "Vodafone / Netmaster", "ip": "192.168.1.1 / 192.168.0.1", "username": "admin", "password": "vodafone / admin"},
    {"brand": "TP-Link", "ip": "192.168.1.1 / 192.168.0.1", "username": "admin", "password": "admin"},
    {"brand": "ASUS", "ip": "192.168.1.1 / 192.168.50.1", "username": "admin", "password": "admin"},
    {"brand": "Keenetic", "ip": "192.168.1.1 / my.keenetic.net", "username": "admin", "password": "kurulumda belirlenir"},
    {"brand": "Zyxel", "ip": "192.168.1.1", "username": "admin", "password": "1234 / turktelekom"},
    {"brand": "ZTE", "ip": "192.168.1.1", "username": "admin", "password": "admin / turktelekom"},
    {"brand": "AirTies", "ip": "192.168.2.1", "username": "admin", "password": "boş (şifresiz) / admin"},
    {"brand": "Netgear", "ip": "192.168.1.1 / 192.168.0.1", "username": "admin", "password": "password"},
    {"brand": "Fritz!Box", "ip": "192.168.178.1 / fritz.box", "username": "admin", "password": "modem etiketinde yazar"},
    {"brand": "Xiaomi / Tenda", "ip": "192.168.31.1 / 192.168.0.1", "username": "admin", "password": "admin / kurulumda belirlenir"},
    {"brand": "MikroTik RouterOS", "ip": "192.168.88.1", "username": "admin", "password": "boş (şifresiz)"}
]

class GatewayDetectWorker(QThread):
    finished = Signal(str, str, float)

    def __init__(self, target_ip: str = ""):
        super().__init__()
        self.target_ip = target_ip

    def run(self):
        gw_ip = self.target_ip
        if not gw_ip:
            gw_ip = self._detect_default_gateway()

        brand_info = "Bilinmeyen Ağ Geçidi / Modem"
        latency = -1.0

        if gw_ip:
            # Measure Ping Latency to Gateway
            ping_res = PingTool.ping(gw_ip, count=2, timeout_ms=1500)
            if ping_res and ping_res.received > 0:
                latency = ping_res.avg_ms

            # Detect Brand HTTP Title
            try:
                url = f"http://{gw_ip}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    html = resp.read().decode('utf-8', errors='ignore')
                    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1).strip()
                        if title:
                            brand_info = f"Tespit Edilen: {title}"
                    
                    server_hdr = resp.headers.get("Server", "")
                    if server_hdr:
                        brand_info += f" ({server_hdr})"
            except Exception:
                pass

        self.finished.emit(gw_ip or "192.168.1.1", brand_info, latency)

    def _detect_default_gateway(self) -> str:
        try:
            # Quick socket test to public IP to infer local gateway interface
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            parts = local_ip.split(".")
            parts[-1] = "1"
            return ".".join(parts)
        except Exception:
            return "192.168.1.1"

class RouterView(QWidget):
    """Modem & Ağ Geçidi Yönetim Sekmesi (Router & Gateway Management Hub)"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n
        self.current_gw_ip = "192.168.1.1"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        # Header Title
        header_layout = QHBoxLayout()
        lbl_header = QLabel("Modem & Ağ Geçidi Yönetimi (Router & Gateway Portal)")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        btn_detect = QPushButton(" Ağ Geçidini Yeniden Tespiti Et")
        btn_detect.setIcon(IconManager.get_icon("refresh", color="#00f2fe", size=16))
        btn_detect.setIconSize(QSize(16, 16))
        btn_detect.setProperty("class", "btn-secondary")
        btn_detect.clicked.connect(self._run_gateway_detection)
        header_layout.addWidget(btn_detect)

        layout.addLayout(header_layout)

        # Gateway Status Banner
        banner_card = QFrame()
        banner_card.setProperty("class", "glass-panel")
        banner_card.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 14px;")
        banner_layout = QHBoxLayout(banner_card)

        self.card_gw_ip = StatCard("AĞ GEÇİDİ (GATEWAY) IP", "192.168.1.1", "Varsayılan IP", "#00f2fe")
        self.card_gw_brand = StatCard("MARKA / MODEL", "Taranıyor...", "HTTP Başlık Analizi", "#38bdf8")
        self.card_gw_latency = StatCard("MODEM GECİKMESİ (PING)", "-- ms", "Yerel Latency", "#4ade80")

        banner_layout.addWidget(self.card_gw_ip)
        banner_layout.addWidget(self.card_gw_brand)
        banner_layout.addWidget(self.card_gw_latency)

        layout.addWidget(banner_card)

        # Gateway Quick Action Box
        action_card = QFrame()
        action_card.setProperty("class", "glass-panel")
        action_card.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 16px;")
        action_layout = QHBoxLayout(action_card)

        action_layout.addWidget(QLabel("Modem IP Arayüzü:"))
        self.input_gw_ip = QLineEdit("192.168.1.1")
        self.input_gw_ip.setFixedWidth(160)
        action_layout.addWidget(self.input_gw_ip)

        btn_open_portal = QPushButton(" Tarayıcıda Modem Paneline Git (http://...)")
        btn_open_portal.setIcon(IconManager.get_icon("router", color="#ffffff", size=16))
        btn_open_portal.setIconSize(QSize(16, 16))
        btn_open_portal.setProperty("class", "btn-primary")
        btn_open_portal.clicked.connect(self._open_router_in_browser)
        action_layout.addWidget(btn_open_portal)

        btn_copy_ip = QPushButton(" IP Kopyala")
        btn_copy_ip.setIcon(IconManager.get_icon("copy", color="#38bdf8", size=16))
        btn_copy_ip.setIconSize(QSize(16, 16))
        btn_copy_ip.setProperty("class", "btn-secondary")
        btn_copy_ip.clicked.connect(lambda: self.input_gw_ip.selectAll() or self.input_gw_ip.copy())
        action_layout.addWidget(btn_copy_ip)

        layout.addWidget(action_card)

        # Default Router Passwords Reference Table Section
        lbl_table_title = QLabel("🔑 Türkiye ve Dünya Varsayılan Modem Kullanıcı Adı & Şifre Veritabanı")
        lbl_table_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8; margin-top: 6px;")
        layout.addWidget(lbl_table_title)

        # Filter box for router database
        filter_layout = QHBoxLayout()
        self.input_search_creds = QLineEdit()
        self.input_search_creds.setPlaceholderText("Modem Markası veya IP Ara (ör: Türk Telekom, Huawei, TP-Link, 192.168.1.1)...")
        self.input_search_creds.textChanged.connect(self._filter_creds_table)
        filter_layout.addWidget(self.input_search_creds)
        layout.addLayout(filter_layout)

        self.table_creds = QTableWidget()
        self.table_creds.setColumnCount(4)
        self.table_creds.setHorizontalHeaderLabels(["Marka / ISS Servis Sağlayıcı", "Varsayılan IP", "Kullanıcı Adı", "Varsayılan Şifre"])
        self.table_creds.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_creds)

        self._populate_creds_table(DEFAULT_ROUTER_CREDS)
        self._run_gateway_detection()

    def closeEvent(self, event):
        if hasattr(self, 'worker') and self.worker is not None and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait(1000)
        super().closeEvent(event)

    def _run_gateway_detection(self):

        self.card_gw_brand.set_value("Taranıyor...", "Lütfen Bekleyin")
        self.worker = GatewayDetectWorker(self.input_gw_ip.text().strip())
        self.worker.finished.connect(self._on_detection_finished)
        self.worker.start()

    def _on_detection_finished(self, gw_ip: str, brand: str, latency: float):
        self.current_gw_ip = gw_ip
        self.input_gw_ip.setText(gw_ip)
        self.card_gw_ip.set_value(gw_ip, "Etkin Ağ Geçidi")
        self.card_gw_brand.set_value(brand[:32], "HTTP Header")
        
        if latency > 0:
            self.card_gw_latency.set_value(f"{latency:.1f} ms", "Yerel Ping")
        else:
            self.card_gw_latency.set_value("Yanıt Yok", "Erişilemedi")

    def _open_router_in_browser(self):
        ip = self.input_gw_ip.text().strip() or "192.168.1.1"
        url_str = f"http://{ip}"
        QDesktopServices.openUrl(QUrl(url_str))

    def _populate_creds_table(self, data):
        self.table_creds.setRowCount(len(data))
        for row, item in enumerate(data):
            self.table_creds.setItem(row, 0, QTableWidgetItem(item["brand"]))
            self.table_creds.setItem(row, 1, QTableWidgetItem(item["ip"]))
            self.table_creds.setItem(row, 2, QTableWidgetItem(item["username"]))
            self.table_creds.setItem(row, 3, QTableWidgetItem(item["password"]))

    def _filter_creds_table(self, text: str):
        query = text.strip().lower()
        filtered = [
            item for item in DEFAULT_ROUTER_CREDS
            if query in item["brand"].lower() or query in item["ip"].lower() or query in item["username"].lower() or query in item["password"].lower()
        ]
        self._populate_creds_table(filtered)
