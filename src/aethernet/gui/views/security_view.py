from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame
)
from aethernet.security.security_scorer import SecurityScorer
from aethernet.security.rogue_ap_detector import RogueApDetector

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
        lbl_header = QLabel("Güvenlik ve Savunma Analizi")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(lbl_header)

        btn_eval = QPushButton("🛡️ Güvenlik Analizini Yenile")
        btn_eval.setProperty("class", "btn-primary")
        btn_eval.clicked.connect(self.run_security_audit)
        header_layout.addWidget(btn_eval)

        layout.addLayout(header_layout)

        self.txt_sec_report = QTextEdit()
        self.txt_sec_report.setReadOnly(True)
        layout.addWidget(self.txt_sec_report)

        self.run_security_audit()

    def run_security_audit(self):
        conn = self.adapter.get_current_connection()
        scanned = self.adapter.scan_networks()

        output = "=== AETHERNET GÜVENLİK VE SAVUNMA RAPORU ===\n\n"

        if conn:
            report = SecurityScorer.evaluate_connection(conn.security_protocol)
            output += f"--- AKTİF BAĞLANTI GÜVENLİK DEĞERLENDİRMESİ ---\n"
            output += f"Ağ Adı (SSID): {conn.ssid}\n"
            output += f"Güvenlik Skoru: {report.score} / 100 ({report.rating})\n"
            output += f"Güvenlik Protokolü: {conn.security_protocol} | Şifreleme: {conn.cipher}\n\n"

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
            output += "Aktif kablosuz ağ bağlantısı bulunamadı.\n\n"

        # Evil Twin AP Check
        rogue_alerts = RogueApDetector.detect_evil_twins(scanned)
        output += "--- SAHTE ERİŞİM NOKTASI (EVIL TWIN / ROGUE AP) TESPİTİ ---\n"
        if rogue_alerts:
            for alert in rogue_alerts:
                output += f"🔴 UYARI: {alert.description}\n"
        else:
            output += "🟢 Çevrenizde Sahte AP veya şüpheli çift SSID yayını tespit edilmedi.\n\n"

        # ARP Spoofing & MITM Guard Check
        from aethernet.security.arp_spoof_detector import ARPSpoofDetector
        arp_detector = ARPSpoofDetector()
        arp_res = arp_detector.analyze_arp_table()
        output += "--- ARP SPOOFING & MAN-IN-THE-MIDDLE (MITM) MUHAFIZI ---\n"
        if arp_res["is_spoofed"]:
            for alert in arp_res["alerts"]:
                output += f"🔴 TEHDİT: {alert}\n"
        else:
            output += f"🟢 ARP Tablosu Güvenli ({arp_res['total_entries']} aktif ARP kaydı incelendi, şüpheli çakışma yok).\n\n"

        # DNS Leak Check
        from aethernet.security.dns_leak_checker import DNSLeakChecker
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

