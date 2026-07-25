import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QTextEdit, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from aethernet.api_hub.ip_intel import IPIntelligenceEngine
from aethernet.api_hub.threat_intel import ThreatIntelligenceEngine
from aethernet.api_hub.shodan_engine import ShodanEngine
from aethernet.api_hub.dns_over_https import DoHEngine
from aethernet.api_hub.public_api_catalog import PublicApiCatalog
from aethernet.gui.components.stat_card import StatCard
from aethernet.gui.components.map_widget import MapViewerWidget

logger = logging.getLogger(__name__)


class APIHubView(QWidget):
    """Cyber-Noir External API, Shodan & Threat Intelligence Hub View"""

    def __init__(self, platform_adapter, i18n_manager, parent=None):
        super().__init__(parent)
        self.platform = platform_adapter
        self.i18n = i18n_manager

        self.ip_engine = IPIntelligenceEngine()
        self.threat_engine = ThreatIntelligenceEngine()
        self.shodan_engine = ShodanEngine()
        self.doh_engine = DoHEngine()
        self.catalog = PublicApiCatalog()

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header Title Banner (Clean Typography - No Emoji)
        header = QLabel("External API & Threat Intelligence Hub")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #00f2fe;")
        main_layout.addWidget(header)

        sub_header = QLabel("Shodan istihbarat motoru, IP coğrafi konum, CISA KEV zafiyet veritabanı, şifreli DoH ve kamusal API dizini.")
        sub_header.setStyleSheet("color: #94a3b8; font-size: 13px;")
        main_layout.addWidget(sub_header)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #1e293b;
                background-color: #0f172a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #00f2fe;
                color: #090d16;
            }
        """)

        # 1. IP & Coğrafi Konum Tab
        self.tab_ip = QWidget()
        self._build_ip_tab()
        self.tabs.addTab(self.tab_ip, "IP & Coğrafi Konum")

        # 2. Shodan İstihbarat & Arama Tab
        self.tab_shodan = QWidget()
        self._build_shodan_tab()
        self.tabs.addTab(self.tab_shodan, "Shodan Intel & Explorer")

        # 3. Tehdit & CISA KEV Tab
        self.tab_threat = QWidget()
        self._build_threat_tab()
        self.tabs.addTab(self.tab_threat, "Tehdit & CISA KEV")

        # 4. DoH Şifreli DNS Tab
        self.tab_doh = QWidget()
        self._build_doh_tab()
        self.tabs.addTab(self.tab_doh, "Şifreli DNS (DoH)")

        # 5. Kamusal API Explorer Tab
        self.tab_catalog = QWidget()
        self._build_catalog_tab()
        self.tabs.addTab(self.tab_catalog, "Kamusal API Explorer")

        main_layout.addWidget(self.tabs)

    # ----------------------------------------------------
    # TAB 1: IP Intelligence UI
    # ----------------------------------------------------
    def _build_ip_tab(self):
        layout = QVBoxLayout(self.tab_ip)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        search_layout = QHBoxLayout()
        self.txt_ip = QLineEdit()
        self.txt_ip.setPlaceholderText("IP adresi girin (örn: 8.8.8.8 veya kendi IP'niz için boş bırakın)")
        self.txt_ip.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")

        btn_lookup = QPushButton("IP Analiz Et")
        btn_lookup.setCursor(Qt.PointingHandCursor)
        btn_lookup.setStyleSheet("padding: 8px 16px; background-color: #00f2fe; color: #090d16; font-weight: bold; border-radius: 6px;")
        btn_lookup.clicked.connect(self._on_ip_lookup)

        btn_my_ip = QPushButton("Kendi IP'm")
        btn_my_ip.setCursor(Qt.PointingHandCursor)
        btn_my_ip.setStyleSheet("padding: 8px 16px; background-color: #3b82f6; color: white; font-weight: bold; border-radius: 6px;")
        btn_my_ip.clicked.connect(self._on_my_ip_lookup)

        search_layout.addWidget(self.txt_ip)
        search_layout.addWidget(btn_lookup)
        search_layout.addWidget(btn_my_ip)
        layout.addLayout(search_layout)

        cards_layout = QHBoxLayout()
        self.card_country = StatCard("Ülke / Konum", "-", "globe")
        self.card_isp = StatCard("ISP / Ağ", "-", "network")
        self.card_asn = StatCard("ASN", "-", "server")
        self.card_proxy = StatCard("Proxy / VPN", "Temiz", "shield")

        cards_layout.addWidget(self.card_country)
        cards_layout.addWidget(self.card_isp)
        cards_layout.addWidget(self.card_asn)
        cards_layout.addWidget(self.card_proxy)
        layout.addLayout(cards_layout)

        # Map & Details Horizontal Splitter
        content_split = QHBoxLayout()

        self.map_widget = MapViewerWidget()
        content_split.addWidget(self.map_widget, stretch=1)

        self.txt_ip_details = QTextEdit()
        self.txt_ip_details.setReadOnly(True)
        self.txt_ip_details.setStyleSheet("background-color: #090d16; color: #38bdf8; font-family: Consolas; font-size: 13px; border: 1px solid #1e293b; border-radius: 6px;")
        content_split.addWidget(self.txt_ip_details, stretch=1)

        layout.addLayout(content_split)

    def _on_ip_lookup(self):
        target = self.txt_ip.text().strip()
        res = self.ip_engine.lookup_ip(target)
        threat_res = self.threat_engine.analyze_target(res.ip)

        self.card_country.set_value(f"{res.country} ({res.city})" if res.city else res.country)
        self.card_isp.set_value(res.isp)
        self.card_asn.set_value(res.asn or "Bilinmiyor")
        
        proxy_state = "VPN/Proxy Tespit Edildi" if res.is_proxy or res.is_vpn else "Temiz"
        self.card_proxy.set_value(proxy_state)

        # Update Map View Pin
        self.map_widget.update_location(res.latitude, res.longitude, res.ip, res.city, res.country, res.isp)

        details = [
            f"=== IP İSTİHBARAT RAPORU ===",
            f"IP Adresi: {res.ip}",
            f"Ülke: {res.country} ({res.country_code})",
            f"Bölge / Şehir: {res.region} / {res.city}",
            f"Enlem / Boylam: {res.latitude}, {res.longitude}",
            f"Zaman Dilimi: {res.timezone}",
            f"ISP / İnternet Sağlayıcı: {res.isp}",
            f"Organizasyon / ASN: {res.org} ({res.asn})",
            f"Hosting / Datacenter: {'Evet' if res.is_hosting else 'Hayır'}",
            f"Veri Kaynağı: {res.provider}",
            "",
            f"=== SHODAN INTERNETDB ZAFİYET TARAMASI ===",
            f"Açık Portlar: {threat_res.shodan_open_ports or 'Yok'}",
            f"Hostnameler: {threat_res.shodan_hostnames or 'Yok'}",
            f"Taraf Verilen CVE Zafiyetleri: {threat_res.shodan_cves or 'Yok'}",
            f"Özet Tehdit Durumu: {threat_res.summary}"
        ]
        self.txt_ip_details.setText("\n".join(details))

    def _on_my_ip_lookup(self):
        self.txt_ip.clear()
        self._on_ip_lookup()

    # ----------------------------------------------------
    # TAB 2: Shodan Intel & Explorer UI
    # ----------------------------------------------------
    def _build_shodan_tab(self):
        layout = QVBoxLayout(self.tab_shodan)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        shodan_search_layout = QHBoxLayout()
        self.txt_shodan_target = QLineEdit()
        self.txt_shodan_target.setPlaceholderText("IP adresi veya Shodan arama terimi girin (örn: 1.1.1.1 veya port:21 product:Apache)")
        self.txt_shodan_target.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")

        btn_shodan_scan = QPushButton("Shodan Tarama Yap")
        btn_shodan_scan.setCursor(Qt.PointingHandCursor)
        btn_shodan_scan.setStyleSheet("padding: 8px 16px; background-color: #f59e0b; color: #090d16; font-weight: bold; border-radius: 6px;")
        btn_shodan_scan.clicked.connect(self._on_shodan_scan)

        shodan_search_layout.addWidget(self.txt_shodan_target)
        shodan_search_layout.addWidget(btn_shodan_scan)
        layout.addLayout(shodan_search_layout)

        self.txt_shodan_output = QTextEdit()
        self.txt_shodan_output.setReadOnly(True)
        self.txt_shodan_output.setStyleSheet("background-color: #090d16; color: #f59e0b; font-family: Consolas; font-size: 13px; border: 1px solid #1e293b; border-radius: 6px;")
        layout.addWidget(self.txt_shodan_output)

    def _on_shodan_scan(self):
        target = self.txt_shodan_target.text().strip()
        if not target:
            target = "8.8.8.8"

        res = self.shodan_engine.query_ip_free(target)
        output = [
            f"=== SHODAN INTERNETDB İSTİHBARAT SONUÇLARI ===",
            f"Hedef IP: {res['ip']}",
            f"Veri Kaynağı: {res['source']}",
            f"Tespit Edilen Açık Portlar: {res['ports'] or 'Açık port bulunamadı'}",
            f"Hostnameler: {res['hostnames'] or 'Hostname bulunamadı'}",
            f"CPE Donanım / Yazılım Tanımları: {res['cpes'] or 'CPE tanımı yok'}",
            f"Tespit Edilen CVE Zafiyetleri: {res['cves'] or 'Zafiyet (CVE) kaydı temiz'}",
            f"Etiketler: {res['tags'] or 'Yok'}",
            "",
            "İpucu: Shodan API Key yapılandırıldığında derinlemesine banner analizi ve global arama aktifleşir."
        ]
        self.txt_shodan_output.setText("\n".join(output))

    # ----------------------------------------------------
    # TAB 3: Threat Intelligence & CISA KEV UI
    # ----------------------------------------------------
    def _build_threat_tab(self):
        layout = QVBoxLayout(self.tab_threat)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        search_layout = QHBoxLayout()
        self.txt_kev_search = QLineEdit()
        self.txt_kev_search.setPlaceholderText("CISA KEV Kataloğunda CVE veya Ürün Ara (örn: Windows, Cisco, CVE-2024)")
        self.txt_kev_search.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")

        btn_search_kev = QPushButton("Zafiyet Ara")
        btn_search_kev.setCursor(Qt.PointingHandCursor)
        btn_search_kev.setStyleSheet("padding: 8px 16px; background-color: #ef4444; color: white; font-weight: bold; border-radius: 6px;")
        btn_search_kev.clicked.connect(self._on_search_kev)

        search_layout.addWidget(self.txt_kev_search)
        search_layout.addWidget(btn_search_kev)
        layout.addLayout(search_layout)

        self.table_kev = QTableWidget()
        self.table_kev.setColumnCount(5)
        self.table_kev.setHorizontalHeaderLabels(["CVE Kodu", "Üretici", "Ürün", "Zafiyet Adı", "Tarih"])
        self.table_kev.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_kev.setStyleSheet("""
            QTableWidget {
                background-color: #090d16;
                color: #e2e8f0;
                gridline-color: #1e293b;
                border: 1px solid #1e293b;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #00f2fe;
                padding: 6px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table_kev)

        self._on_search_kev()

    def _on_search_kev(self):
        kw = self.txt_kev_search.text().strip()
        items = self.threat_engine.fetch_cisa_kev(limit=40, keyword=kw)

        self.table_kev.setRowCount(0)
        for row_idx, item in enumerate(items):
            self.table_kev.insertRow(row_idx)
            self.table_kev.setItem(row_idx, 0, QTableWidgetItem(item.get("cve_id", "")))
            self.table_kev.setItem(row_idx, 1, QTableWidgetItem(item.get("vendor", "")))
            self.table_kev.setItem(row_idx, 2, QTableWidgetItem(item.get("product", "")))
            self.table_kev.setItem(row_idx, 3, QTableWidgetItem(item.get("name", "")))
            self.table_kev.setItem(row_idx, 4, QTableWidgetItem(item.get("date_added", "")))

    # ----------------------------------------------------
    # TAB 4: DoH (DNS-over-HTTPS) UI
    # ----------------------------------------------------
    def _build_doh_tab(self):
        layout = QVBoxLayout(self.tab_doh)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        input_layout = QHBoxLayout()
        self.txt_doh_domain = QLineEdit("google.com")
        self.txt_doh_domain.setPlaceholderText("Domain adresi (örn: google.com)")
        self.txt_doh_domain.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")

        self.cmb_doh_provider = QComboBox()
        self.cmb_doh_provider.addItems(["Cloudflare", "Google", "Quad9"])
        self.cmb_doh_provider.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")

        self.cmb_doh_type = QComboBox()
        self.cmb_doh_type.addItems(["A", "AAAA", "MX", "TXT", "NS", "CNAME"])
        self.cmb_doh_type.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")

        btn_doh_query = QPushButton("DoH Sorgula")
        btn_doh_query.setCursor(Qt.PointingHandCursor)
        btn_doh_query.setStyleSheet("padding: 8px 16px; background-color: #10b981; color: white; font-weight: bold; border-radius: 6px;")
        btn_doh_query.clicked.connect(self._on_doh_query)

        input_layout.addWidget(self.txt_doh_domain)
        input_layout.addWidget(self.cmb_doh_provider)
        input_layout.addWidget(self.cmb_doh_type)
        input_layout.addWidget(btn_doh_query)
        layout.addLayout(input_layout)

        self.txt_doh_output = QTextEdit()
        self.txt_doh_output.setReadOnly(True)
        self.txt_doh_output.setStyleSheet("background-color: #090d16; color: #10b981; font-family: Consolas; font-size: 13px; border: 1px solid #1e293b; border-radius: 6px;")
        layout.addWidget(self.txt_doh_output)

    def _on_doh_query(self):
        domain = self.txt_doh_domain.text().strip()
        provider = self.cmb_doh_provider.currentText()
        rec_type = self.cmb_doh_type.currentText()

        res = self.doh_engine.query(domain, record_type=rec_type, provider_name=provider)

        output = [
            f"=== DNS-OVER-HTTPS (DoH) SORGUSUNU TAMAMLADI ===",
            f"Domain: {res.domain}",
            f"Kayıt Tipi: {res.record_type}",
            f"DoH Sağlayıcı: {res.provider}",
            f"Yanıt Süresi: {res.response_time_ms} ms",
            f"DNSSEC Doğrulandı: {'Evet' if res.dnssec_valid else 'Hayır'}",
            f"Quad9 Zararlı Engeli: {'Engellendi (Malware)' if res.quad9_blocked else 'Temiz / İzin Verildi'}",
            f"TTL (Saniye): {res.ttl}",
            "",
            f"--- Yanıt Değerleri ---"
        ]
        for val in res.answers:
            output.append(f" -> {val}")

        if not res.answers:
            output.append(" (Yanıt bulunamadı veya NXDOMAIN)")

        self.txt_doh_output.setText("\n".join(output))

    # ----------------------------------------------------
    # TAB 5: Public API Explorer UI
    # ----------------------------------------------------
    def _build_catalog_tab(self):
        layout = QVBoxLayout(self.tab_catalog)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        filter_layout = QHBoxLayout()
        self.txt_api_search = QLineEdit()
        self.txt_api_search.setPlaceholderText("API ismi veya anahtar kelime ara (örn: security, ip, weather)")
        self.txt_api_search.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")
        self.txt_api_search.textChanged.connect(self._on_filter_catalog)

        self.cmb_api_cat = QComboBox()
        self.cmb_api_cat.addItems(self.catalog.list_categories())
        self.cmb_api_cat.setStyleSheet("padding: 8px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 6px;")
        self.cmb_api_cat.currentIndexChanged.connect(self._on_filter_catalog)

        filter_layout.addWidget(self.txt_api_search)
        filter_layout.addWidget(self.cmb_api_cat)
        layout.addLayout(filter_layout)

        self.table_api = QTableWidget()
        self.table_api.setColumnCount(5)
        self.table_api.setHorizontalHeaderLabels(["API Adı", "Kategori", "Açıklama", "Yetkilendirme", "Rate Limit"])
        self.table_api.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_api.setStyleSheet("""
            QTableWidget {
                background-color: #090d16;
                color: #e2e8f0;
                gridline-color: #1e293b;
                border: 1px solid #1e293b;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #00f2fe;
                padding: 6px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table_api)

        self._on_filter_catalog()

    def _on_filter_catalog(self):
        kw = self.txt_api_search.text().strip()
        cat = self.cmb_api_cat.currentText()

        apis = self.catalog.search_apis(keyword=kw, category=cat)

        self.table_api.setRowCount(0)
        for row_idx, api in enumerate(apis):
            self.table_api.insertRow(row_idx)
            self.table_api.setItem(row_idx, 0, QTableWidgetItem(api.name))
            self.table_api.setItem(row_idx, 1, QTableWidgetItem(api.category))
            self.table_api.setItem(row_idx, 2, QTableWidgetItem(api.description))
            self.table_api.setItem(row_idx, 3, QTableWidgetItem(api.auth_type))
            self.table_api.setItem(row_idx, 4, QTableWidgetItem(api.rate_limit))
