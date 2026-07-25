from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame, QProgressBar
)
from PySide6.QtCore import Qt
from aethernet.security.security_scorer import SecurityScorer
from aethernet.security.rogue_ap_detector import RogueApDetector
from aethernet.security.arp_spoof_detector import ARPSpoofDetector
from aethernet.security.dns_leak_checker import DNSLeakChecker
from aethernet.gui.components.stat_card import StatCard

class SecurityView(QWidget):
    """Network Security Score & Defense Analysis View"""

    def __init__(self, platform_adapter, i18n, parent=None):
        super().__init__(parent)
        self.adapter = platform_adapter
        self.i18n = i18n

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        lbl_header = QLabel("🛡️ Güvenlik ve Savunma Analizi")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        header_layout.addStretch()

        btn_eval = QPushButton("🛡️ Güvenlik Analizini Yenile")
        btn_eval.setProperty("class", "btn-primary")
        btn_eval.clicked.connect(self.run_security_audit)
        header_layout.addWidget(btn_eval)

        layout.addLayout(header_layout)

        # Security Score Card Banner
        score_card = QFrame()
        score_card.setProperty("class", "glass-panel")
        score_card.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 16px;")
        score_layout = QHBoxLayout(score_card)

        self.card_sec_score = StatCard("GÜVENLİK PUANI", "-- / 100", "Ağ Durumu", "#4ade80")
        self.card_evil_twin = StatCard("ROGUE AP TESPİTİ", "TEMİZ", "Çevresel Tehdit", "#00f2fe")
        self.card_arp_spoof = StatCard("ARP / MITM KORUMASI", "GÜVENLİ", "Zehirlenme Riski", "#38bdf8")

        score_layout.addWidget(self.card_sec_score)
        score_layout.addWidget(self.card_evil_twin)
        score_layout.addWidget(self.card_arp_spoof)

        layout.addWidget(score_card)

        # Detailed Report Terminal Box
        self.txt_sec_report = QTextEdit()
        self.txt_sec_report.setReadOnly(True)
        self.txt_sec_report.setProperty("class", "terminal-out")
        layout.addWidget(self.txt_sec_report)

        self.run_security_audit()

    def run_security_audit(self):
        conn = self.adapter.get_current_connection()
        scanned = self.adapter.scan_networks()

        output = "=== AETHERNET GÜVENLİK VE SAVUNMA RAPORU ===\n\n"

        if conn:
            report = SecurityScorer.evaluate_connection(conn.security_protocol)
            self.card_sec_score.set_value(f"{report.score} / 100", report.rating)

            output += f"--- AKTİF BAĞLANTI GÜVENLİK DEĞERLENDİRMESİ ---\n"
            output += f"Ağ Adı (SSID)       : {conn.ssid}\n"
            output += f"Güvenlik Skoru      : {report.score} / 100 ({report.rating})\n"
            output += f"Güvenlik Protokolü  : {conn.security_protocol} | Şifreleme: {conn.cipher}\n\n"

            if report.issues:
                output += "⚠️ TESPİT EDİLEN GÜVENLİK RİSKLERİ:\n"
                for issue in report.issues:
                    output += f" - {issue}\n"
                output += "\n"

            if report.recommendations:
                output += "💡 ÖNERİLEN DEFANSİF İYİLEŞTİRMELER:\n"
                for rec in report.recommendations:
                    output += f" - {rec}\n"
                output += "\n"
        else:
            self.card_sec_score.set_value("0 / 100", "Bağlantı Yok")
            output += "Aktif kablosuz ağ bağlantısı bulunamadı.\n\n"

        # Evil Twin AP Check
        rogue_alerts = RogueApDetector.detect_evil_twins(scanned)
        output += "--- SAHTE ERİŞİM NOKTASI (EVIL TWIN / ROGUE AP) TESPİTİ ---\n"
        if rogue_alerts:
            self.card_evil_twin.set_value("TEHDİT!", f"{len(rogue_alerts)} Şüpheli AP")
            for alert in rogue_alerts:
                output += f"🔴 UYARI: {alert.description}\n"
        else:
            self.card_evil_twin.set_value("TEMİZ", "Şüpheli AP Yok")
            output += "🟢 Çevrenizde Sahte AP veya şüpheli çift SSID yayını tespit edilmedi.\n\n"

        # ARP Spoofing & MITM Guard Check
        arp_detector = ARPSpoofDetector()
        arp_res = arp_detector.analyze_arp_table()
        output += "--- ARP SPOOFING & MAN-IN-THE-MIDDLE (MITM) MUHAFIZI ---\n"
        if arp_res["is_spoofed"]:
            self.card_arp_spoof.set_value("RİSK!", "Çakışma Var")
            for alert in arp_res["alerts"]:
                output += f"🔴 TEHDİT: {alert}\n"
        else:
            self.card_arp_spoof.set_value("GÜVENLİ", f"{arp_res['total_entries']} ARP Kaydı")
            output += f"🟢 ARP Tablosu Güvenli ({arp_res['total_entries']} aktif ARP kaydı incelendi, şüpheli çakışma yok).\n\n"

        # DNS Leak Check
        dns_checker = DNSLeakChecker()
        dns_res = dns_checker.check_leak_status()
        output += "--- DNS SIZINTI (LEAK) KONTROLÜ ---\n"
        output += f"Aktif DNS Sunucuları: {', '.join(dns_res['resolvers']) if dns_res['resolvers'] else 'Varsayılan Sistem DNS'}\n"
        if dns_res["has_leak"]:
            for alert in dns_res["alerts"]:
                output += f"⚠️ {alert}\n"
        else:
            output += "🟢 DNS Sızıntısı veya şüpheli yönlendirme tespit edilmedi.\n"

        self.txt_sec_report.setText(output)
