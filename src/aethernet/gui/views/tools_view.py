from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QComboBox, QFrame
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt, QSize
from aethernet.network_tools.ping_tool import PingTool
from aethernet.network_tools.dns_tool import DnsTool
from aethernet.network_tools.whois_tool import WhoisTool
from aethernet.network_tools.port_scanner import PortScanner
from aethernet.network_tools.ssl_checker import SslChecker
from aethernet.network_tools.speedtest_tool import SpeedtestTool
from aethernet.gui.icon_manager import IconManager

class ToolsView(QWidget):
    """Network Diagnostic Tools Suite View with Cyber Terminal Output & Vector Icons"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_header = QLabel("İnternet ve Ağ Tanılama Araçları")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc; margin-bottom: 10px;")
        layout.addWidget(lbl_header)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._setup_ping_tab()
        self._setup_dns_tab()
        self._setup_whois_tab()
        self._setup_port_scan_tab()
        self._setup_ssl_tab()
        self._setup_speedtest_tab()

    def _create_terminal_widget(self, parent_layout):
        term_box = QFrame()
        term_box.setProperty("class", "glass-panel")
        term_layout = QVBoxLayout(term_box)
        term_layout.setContentsMargins(10, 10, 10, 10)

        top_bar = QHBoxLayout()
        lbl_term_title = QLabel("KONSOL ÇIKTISI")
        lbl_term_title.setStyleSheet("color: #00f2fe; font-size: 11px; font-weight: bold; font-family: monospace;")
        top_bar.addWidget(lbl_term_title)
        top_bar.addStretch()

        btn_copy = QPushButton(" Kopyala")
        btn_copy.setIcon(IconManager.get_icon("copy", color="#38bdf8", size=14))
        btn_copy.setIconSize(QSize(14, 14))
        btn_copy.setProperty("class", "btn-secondary")
        btn_copy.setFixedHeight(28)
        
        btn_clear = QPushButton(" Temizle")
        btn_clear.setIcon(IconManager.get_icon("trash", color="#f43f5e", size=14))
        btn_clear.setIconSize(QSize(14, 14))
        btn_clear.setProperty("class", "btn-secondary")
        btn_clear.setFixedHeight(28)

        top_bar.addWidget(btn_copy)
        top_bar.addWidget(btn_clear)
        term_layout.addLayout(top_bar)

        txt_out = QTextEdit()
        txt_out.setReadOnly(True)
        txt_out.setProperty("class", "terminal-out")
        term_layout.addWidget(txt_out)

        btn_copy.clicked.connect(lambda: QGuiApplication.clipboard().setText(txt_out.toPlainText()))
        btn_clear.clicked.connect(lambda: txt_out.clear())

        parent_layout.addWidget(term_box)
        return txt_out

    def _setup_ping_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        
        row = QHBoxLayout()
        self.input_ping = QLineEdit("8.8.8.8")
        btn = QPushButton(" Ping Gönder")
        btn.setIcon(IconManager.get_icon("ping", color="#ffffff", size=16))
        btn.setIconSize(QSize(16, 16))
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_ping)
        row.addWidget(QLabel("Hedef IP / Domain:"))
        row.addWidget(self.input_ping)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_ping_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "Ping")
        self.tabs.setTabIcon(idx, IconManager.get_icon("ping", color="#38bdf8", size=16))

    def _run_ping(self):
        target = self.input_ping.text().strip()
        res = PingTool.ping(target)
        out = (
            f"--- [PING TESTİ BAŞLATILDI]: {res.target} ---\n"
            f"Paket Durumu   : Gönderilen: {res.sent} | Alınan: {res.received} | Kayıp: %{res.loss_percent}\n"
            f"Gecikme (RTT)  : Min: {res.min_ms} ms | Max: {res.max_ms} ms | Ortalama: {res.avg_ms} ms\n"
            f"Jitter (Seğirme): {res.jitter_ms} ms\n"
            f"Yanıt Detayları: {res.replies}\n"
            f"-----------------------------------------------\n"
        )
        self.txt_ping_out.setText(out)

    def _setup_dns_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)

        row = QHBoxLayout()
        self.input_dns_domain = QLineEdit("google.com")
        self.combo_dns_type = QComboBox()
        self.combo_dns_type.addItems(["A", "AAAA", "MX", "TXT", "NS", "CNAME", "SOA"])
        btn = QPushButton(" DNS Sorgula")
        btn.setIcon(IconManager.get_icon("dns", color="#ffffff", size=16))
        btn.setIconSize(QSize(16, 16))
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_dns)

        row.addWidget(QLabel("Domain:"))
        row.addWidget(self.input_dns_domain)
        row.addWidget(QLabel("Kayıt Tipi:"))
        row.addWidget(self.combo_dns_type)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_dns_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "DNS Sorgulama")
        self.tabs.setTabIcon(idx, IconManager.get_icon("dns", color="#38bdf8", size=16))

    def _run_dns(self):
        domain = self.input_dns_domain.text().strip()
        rtype = self.combo_dns_type.currentText()
        records = DnsTool.query(domain, rtype)
        if records:
            out = f"--- [DNS SORGUSU: {domain} ({rtype})] ---\n" + "\n".join([f"[{r.record_type}] TTL: {r.ttl}s -> {r.value}" for r in records])
        else:
            out = "Kayıt bulunamadı veya DNS sorgusu zaman aşımına uğradı."
        self.txt_dns_out.setText(out)

    def _setup_whois_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_whois = QLineEdit("aegissoft.com.tr")
        btn = QPushButton(" WHOIS / RDAP Sorgula")
        btn.setIcon(IconManager.get_icon("whois", color="#ffffff", size=16))
        btn.setIconSize(QSize(16, 16))
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_whois)
        row.addWidget(QLabel("Domain veya IP:"))
        row.addWidget(self.input_whois)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_whois_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "WHOIS / RDAP")
        self.tabs.setTabIcon(idx, IconManager.get_icon("whois", color="#38bdf8", size=16))

    def _run_whois(self):
        target = self.input_whois.text().strip()
        res = WhoisTool.lookup_domain(target)
        out = (
            f"--- [WHOIS / RDAP KAYDI: {res.domain}] ---\n"
            f"Çözümlenen IP : {res.ip or 'Bilinmiyor'}\n"
            f"Registrar    : {res.registrar or 'N/A'}\n"
            f"Kayıt Tarihi : {res.creation_date or 'N/A'}\n"
            f"Son Kullanma : {res.expiration_date or 'N/A'}\n"
            f"Name Servers : {res.name_servers or []}\n"
        )
        self.txt_whois_out.setText(out)

    def _setup_port_scan_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_port_target = QLineEdit("127.0.0.1")
        btn = QPushButton(" Port Taramasını Başlat")
        btn.setIcon(IconManager.get_icon("port", color="#ffffff", size=16))
        btn.setIconSize(QSize(16, 16))
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_port_scan)
        row.addWidget(QLabel("Hedef IP:"))
        row.addWidget(self.input_port_target)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_port_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "Port Tarayıcı")
        self.tabs.setTabIcon(idx, IconManager.get_icon("port", color="#38bdf8", size=16))

    def _run_port_scan(self):
        target = self.input_port_target.text().strip()
        results = PortScanner.scan_target(target)
        if results:
            out = f"--- [PORT TARAMA SONUÇLARI: {target}] ---\n" + "\n".join([f"Port {r.port}/TCP: AÇIK ({r.service})" for r in results])
        else:
            out = f"--- [PORT TARAMA SONUÇLARI: {target}] ---\nYaygın portlardan hiçbiri açık bulunamadı."
        self.txt_port_out.setText(out)

    def _setup_ssl_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_ssl_domain = QLineEdit("github.com")
        btn = QPushButton(" SSL Sertifikası İncele")
        btn.setIcon(IconManager.get_icon("ssl", color="#ffffff", size=16))
        btn.setIconSize(QSize(16, 16))
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_ssl_check)
        row.addWidget(QLabel("Domain:"))
        row.addWidget(self.input_ssl_domain)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_ssl_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "SSL/TLS Denetleyici")
        self.tabs.setTabIcon(idx, IconManager.get_icon("ssl", color="#38bdf8", size=16))

    def _run_ssl_check(self):
        domain = self.input_ssl_domain.text().strip()
        cert = SslChecker.inspect(domain)
        if cert:
            out = (
                f"--- [SSL/TLS SERTİFİKA ANALİZİ: {cert.domain}] ---\n"
                f"Sertifika Sağlayıcı (Issuer): {cert.issuer_org}\n"
                f"Geçerlilik Başlangıcı      : {cert.valid_from}\n"
                f"Geçerlilik Bitişi          : {cert.valid_until}\n"
                f"Kalan Gün Sayısı           : {cert.days_left} Gün\n"
                f"Protokol Versiyonu         : {cert.protocol}\n"
                f"Şifre Paketi (Cipher)      : {cert.cipher_name}\n"
                f"Durum                      : {'Geçerli Sertifika' if cert.is_valid else 'Süresi Dolmuş / Geçersiz'}\n"
            )
        else:
            out = "SSL/TLS sertifikası alınamadı."
        self.txt_ssl_out.setText(out)

    def _setup_speedtest_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        btn = QPushButton(" Hız Testini Başlat")
        btn.setIcon(IconManager.get_icon("speed", color="#ffffff", size=16))
        btn.setIconSize(QSize(16, 16))
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_speedtest)
        t_layout.addWidget(btn)

        self.txt_speed_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "Hız Testi")
        self.tabs.setTabIcon(idx, IconManager.get_icon("speed", color="#38bdf8", size=16))

    def _run_speedtest(self):
        self.txt_speed_out.setText("Hız testi çalıştırılıyor... Lütfen bekleyin...")
        res = SpeedtestTool.run_test()
        if res:
            out = (
                f"--- [HIZ TESTİ SONUÇLARI] ---\n"
                f"İndirme Hızı (Download) : {res.download_mbps} Mbps\n"
                f"Yükleme Hızı (Upload)   : {res.upload_mbps} Mbps\n"
                f"Ping / Gecikme          : {res.ping_ms} ms\n"
                f"Test Sunucusu           : {res.server_name}\n"
                f"İnternet IP             : {res.client_ip}\n"
            )
        else:
            out = "Hız testi sırasında hata oluştu. Ağ bağlantınızı kontrol edin."
        self.txt_speed_out.setText(out)
