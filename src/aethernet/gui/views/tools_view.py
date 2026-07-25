from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QComboBox
)
from aethernet.network_tools.ping_tool import PingTool
from aethernet.network_tools.dns_tool import DnsTool
from aethernet.network_tools.whois_tool import WhoisTool
from aethernet.network_tools.port_scanner import PortScanner
from aethernet.network_tools.ssl_checker import SslChecker
from aethernet.network_tools.speedtest_tool import SpeedtestTool

class ToolsView(QWidget):
    """Network Diagnostic Tools Suite View"""

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

    def _setup_ping_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        
        row = QHBoxLayout()
        self.input_ping = QLineEdit("8.8.8.8")
        btn = QPushButton("Ping Gönder")
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_ping)
        row.addWidget(QLabel("Hedef IP / Domain:"))
        row.addWidget(self.input_ping)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_ping_out = QTextEdit()
        self.txt_ping_out.setReadOnly(True)
        t_layout.addWidget(self.txt_ping_out)
        self.tabs.addTab(tab, "📍 Ping")

    def _run_ping(self):
        target = self.input_ping.text().strip()
        res = PingTool.ping(target)
        out = (
            f"--- PING SONUÇLARI: {res.target} ---\n"
            f"Gönderilen: {res.sent} | Alınan: {res.received} | Paket Kaybı: %{res.loss_percent}\n"
            f"Min Gecikme: {res.min_ms} ms | Max Gecikme: {res.max_ms} ms | Ortalama: {res.avg_ms} ms\n"
            f"Jitter (Seğirme): {res.jitter_ms} ms\n"
            f"Yanıt Süreleri: {res.replies}\n"
        )
        self.txt_ping_out.setText(out)

    def _setup_dns_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)

        row = QHBoxLayout()
        self.input_dns_domain = QLineEdit("google.com")
        self.combo_dns_type = QComboBox()
        self.combo_dns_type.addItems(["A", "AAAA", "MX", "TXT", "NS", "CNAME", "SOA"])
        btn = QPushButton("DNS Sorgula")
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_dns)

        row.addWidget(QLabel("Domain:"))
        row.addWidget(self.input_dns_domain)
        row.addWidget(QLabel("Kayıt Tipi:"))
        row.addWidget(self.combo_dns_type)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_dns_out = QTextEdit()
        self.txt_dns_out.setReadOnly(True)
        t_layout.addWidget(self.txt_dns_out)
        self.tabs.addTab(tab, "🌐 DNS Sorgulama")

    def _run_dns(self):
        domain = self.input_dns_domain.text().strip()
        rtype = self.combo_dns_type.currentText()
        records = DnsTool.query(domain, rtype)
        if records:
            out = "\n".join([f"[{r.record_type}] TTL: {r.ttl}s -> {r.value}" for r in records])
        else:
            out = "Kayıt bulunamadı veya DNS sorgusu zaman aşımına uğradı."
        self.txt_dns_out.setText(out)

    def _setup_whois_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_whois = QLineEdit("github.com")
        btn = QPushButton("WHOIS / RDAP Sorgula")
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_whois)
        row.addWidget(QLabel("Domain veya IP:"))
        row.addWidget(self.input_whois)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_whois_out = QTextEdit()
        self.txt_whois_out.setReadOnly(True)
        t_layout.addWidget(self.txt_whois_out)
        self.tabs.addTab(tab, "🔎 WHOIS / RDAP")

    def _run_whois(self):
        target = self.input_whois.text().strip()
        res = WhoisTool.lookup_domain(target)
        out = (
            f"Domain: {res.domain}\n"
            f"Registrar: {res.registrar or 'N/A'}\n"
            f"Kayıt Tarihi: {res.creation_date or 'N/A'}\n"
            f"Son Kullanma: {res.expiration_date or 'N/A'}\n"
            f"Name Servers: {res.name_servers or []}\n"
        )
        self.txt_whois_out.setText(out)

    def _setup_port_scan_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_port_target = QLineEdit("127.0.0.1")
        btn = QPushButton("Port Taramasını Başlat")
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_port_scan)
        row.addWidget(QLabel("Hedef IP:"))
        row.addWidget(self.input_port_target)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_port_out = QTextEdit()
        self.txt_port_out.setReadOnly(True)
        t_layout.addWidget(self.txt_port_out)
        self.tabs.addTab(tab, "🔌 Port Tarayıcı")

    def _run_port_scan(self):
        target = self.input_port_target.text().strip()
        results = PortScanner.scan_target(target)
        if results:
            out = "\n".join([f"Port {r.port}/TCP: AÇIK ({r.service})" for r in results])
        else:
            out = "Yaygın portlardan hiçbiri açık bulunamadı."
        self.txt_port_out.setText(out)

    def _setup_ssl_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_ssl_domain = QLineEdit("github.com")
        btn = QPushButton("SSL Sertifikası İncele")
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_ssl_check)
        row.addWidget(QLabel("Domain:"))
        row.addWidget(self.input_ssl_domain)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_ssl_out = QTextEdit()
        self.txt_ssl_out.setReadOnly(True)
        t_layout.addWidget(self.txt_ssl_out)
        self.tabs.addTab(tab, "🔒 SSL/TLS Denetleyici")

    def _run_ssl_check(self):
        domain = self.input_ssl_domain.text().strip()
        cert = SslChecker.inspect(domain)
        if cert:
            out = (
                f"Domain: {cert.domain}\n"
                f"Sertifika Sağlayıcı (Issuer): {cert.issuer_org}\n"
                f"Geçerlilik Başlangıcı: {cert.valid_from}\n"
                f"Geçerlilik Bitişi: {cert.valid_until}\n"
                f"Kalan Gün Sayısı: {cert.days_left} Gün\n"
                f"Protokol Versiyonu: {cert.protocol}\n"
                f"Şifre Paketi (Cipher): {cert.cipher_name}\n"
                f"Durum: {'🟢 Geçerli Sertifika' if cert.is_valid else '🔴 Süresi Dolmuş / Geçersiz'}\n"
            )
        else:
            out = "SSL/TLS sertifikası alınamadı."
        self.txt_ssl_out.setText(out)

    def _setup_speedtest_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        btn = QPushButton("⚡ Hız Testini Başlat")
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_speedtest)
        t_layout.addWidget(btn)

        self.txt_speed_out = QTextEdit()
        self.txt_speed_out.setReadOnly(True)
        t_layout.addWidget(self.txt_speed_out)
        self.tabs.addTab(tab, "🚀 Hız Testi")

    def _run_speedtest(self):
        self.txt_speed_out.setText("Hız testi çalıştırılıyor... Lütfen bekleyin...")
        res = SpeedtestTool.run_test()
        if res:
            out = (
                f"--- HIZ TESTİ SONUÇLARI ---\n"
                f"İndirme Hızı (Download): {res.download_mbps} Mbps\n"
                f"Yükleme Hızı (Upload): {res.upload_mbps} Mbps\n"
                f"Ping / Gecikme: {res.ping_ms} ms\n"
                f"Test Sunucusu: {res.server_name}\n"
                f"İnternet IP: {res.client_ip}\n"
            )
        else:
            out = "Hız testi sırasında hata oluştu. Ağ bağlantınızı kontrol edin."
        self.txt_speed_out.setText(out)
