from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QComboBox, QFrame
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt, QSize, QThread, Signal
from aethernet.network_tools.ping_tool import PingTool
from aethernet.network_tools.dns_tool import DnsTool
from aethernet.network_tools.whois_tool import WhoisTool
from aethernet.network_tools.port_scanner import PortScanner
from aethernet.network_tools.ssl_checker import SslChecker
from aethernet.network_tools.speedtest_tool import SpeedtestTool
from aethernet.gui.icon_manager import IconManager
from aethernet.gui.components.toast import ToastNotification

class SpeedtestWorkerThread(QThread):
    finished_signal = Signal(object)

    def run(self):
        res = SpeedtestTool.run_test()
        self.finished_signal.emit(res)

class ToolsView(QWidget):
    """Network Diagnostic Tools Suite View with Cyber Terminal Output & Vector Icons"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n
        self.speed_worker = None

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

    def closeEvent(self, event):
        if hasattr(self, 'speed_worker') and self.speed_worker is not None and self.speed_worker.isRunning():
            self.speed_worker.quit()
            self.speed_worker.wait(1000)
        super().closeEvent(event)

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

        def _do_copy():
            text = txt_out.toPlainText()
            if text:
                QGuiApplication.clipboard().setText(text)
                ToastNotification.show_toast(self, "✓ Konsol Çıktısı Panoya Kopyalandı!", is_success=True)

        btn_copy.clicked.connect(_do_copy)
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
            f"--- [PING ANALİZİ: {res.target}] ---\n"
            f"Gönderilen Paket : {res.sent}\n"
            f"Alınan Paket     : {res.received}\n"
            f"Paket Kaybı      : %{res.loss_percent}\n"
            f"En Düşük Latency : {res.min_ms} ms\n"
            f"En Yüksek Latency: {res.max_ms} ms\n"
            f"Ortalama Latency : {res.avg_ms} ms\n"
            f"Jitter           : {res.jitter_ms} ms\n"
        )
        self.txt_ping_out.setText(out)

    def _setup_dns_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_dns_domain = QLineEdit("google.com")
        self.combo_dns_type = QComboBox()
        self.combo_dns_type.addItems(["A", "AAAA", "MX", "TXT", "NS", "CNAME"])
        btn = QPushButton(" Dns Sorgula")
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
        out = f"--- [DNS SORGUSU: {domain} ({rtype})] ---\n"
        if records:
            out += "\n".join([f" - {r}" for r in records])
        else:
            out += "Kayıt bulunamadı veya sorgu zaman aşımına uğradı."
        self.txt_dns_out.setText(out)

    def _setup_whois_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_whois_target = QLineEdit("google.com")
        btn = QPushButton(" WHOIS / RDAP SORGULA")
        btn.setIcon(IconManager.get_icon("whois", color="#ffffff", size=16))
        btn.setIconSize(QSize(16, 16))
        btn.setProperty("class", "btn-primary")
        btn.clicked.connect(self._run_whois)
        row.addWidget(QLabel("Domain / IP:"))
        row.addWidget(self.input_whois_target)
        row.addWidget(btn)
        t_layout.addLayout(row)

        self.txt_whois_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "WHOIS & RDAP")
        self.tabs.setTabIcon(idx, IconManager.get_icon("whois", color="#38bdf8", size=16))

    def _run_whois(self):
        target = self.input_whois_target.text().strip()
        res = WhoisTool.lookup_domain(target)
        out = (
            f"--- [WHOIS / RDAP REGISTRY SORGUSU: {res.domain}] ---\n"
            f"Registrar           : {res.registrar or 'Bilinmiyor'}\n"
            f"Kayıt Tarihi        : {res.creation_date or 'Bilinmiyor'}\n"
            f"Bitiş Tarihi        : {res.expiration_date or 'Bilinmiyor'}\n"
            f"İnternet Servis/Org : {res.org or 'Bilinmiyor'}\n"
            f"Ülke / Şehir        : {res.country or 'Bilinmiyor'} / {res.city or 'Bilinmiyor'}\n"
            f"IP Adresi           : {res.ip or 'Bilinmiyor'}\n"
            f"ASN                 : {res.asn or 'Bilinmiyor'}\n"
            f"Ad Sunucuları (NS)  : {', '.join(res.name_servers) if res.name_servers else 'Yok'}\n"
            f"Danışılan Kaynaklar : {', '.join(res.sources_consulted) if res.sources_consulted else 'Yok'}\n"
        )
        if res.raw_text:
            out += f"\n--- Ham WHOIS / RDAP Yanıtı ---\n{res.raw_text}"
        self.txt_whois_out.setText(out)

    def _setup_port_scan_tab(self):
        tab = QWidget()
        t_layout = QVBoxLayout(tab)
        row = QHBoxLayout()
        self.input_port_target = QLineEdit("127.0.0.1")
        btn = QPushButton(" Port Taraması Başlat")
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
        results = PortScanner.scan_common_ports(target)
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
        self.btn_speed = QPushButton(" En Yakın Sunucudan Hız Testini Başlat")
        self.btn_speed.setIcon(IconManager.get_icon("speed", color="#ffffff", size=16))
        self.btn_speed.setIconSize(QSize(16, 16))
        self.btn_speed.setProperty("class", "btn-primary")
        self.btn_speed.clicked.connect(self._run_speedtest)
        t_layout.addWidget(self.btn_speed)

        self.txt_speed_out = self._create_terminal_widget(t_layout)
        idx = self.tabs.addTab(tab, "Hız Testi")
        self.tabs.setTabIcon(idx, IconManager.get_icon("speed", color="#38bdf8", size=16))

    def _run_speedtest(self):
        self.btn_speed.setEnabled(False)
        self.txt_speed_out.setText("En yakın ve en hızlı Speedtest sunucusu aranıyor ve bant genişliği ölçülüyor...\nLütfen bekleyin...")
        
        self.speed_worker = SpeedtestWorkerThread()
        self.speed_worker.finished_signal.connect(self._on_speedtest_finished)
        self.speed_worker.start()

    def _on_speedtest_finished(self, res):
        self.btn_speed.setEnabled(True)
        if res:
            out = (
                f"--- [HIZ TESTİ SONUÇLARI] ---\n"
                f"İndirme Hızı (Download) : {res.download_mbps} Mbps\n"
                f"Yükleme Hızı (Upload)   : {res.upload_mbps} Mbps\n"
                f"Ping / Gecikme          : {res.ping_ms} ms\n"
                f"Seçilen En Yakın Sunucu : {res.server_name}\n"
                f"İnternet IP             : {res.client_ip}\n"
            )
            ToastNotification.show_toast(self, "✓ Hız Testi Başarıyla Tamamlandı!", is_success=True)
        else:
            out = "Hız testi sırasında hata oluştu. Ağ bağlantınızı kontrol edin."
            ToastNotification.show_toast(self, "Hız Testi Tamamlanamadı", is_success=False)
        self.txt_speed_out.setText(out)
