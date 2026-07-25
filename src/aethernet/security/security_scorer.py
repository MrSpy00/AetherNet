from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class SecurityReport:
    score: int  # 0 to 100
    rating: str # "Mükemmel", "İyi", "Orta", "Zayıf", "Kritik"
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class SecurityScorer:
    """Ağ güvenlik skorlayıcı ve tavsiye motoru"""

    @classmethod
    def evaluate_connection(
        cls,
        security_protocol: str,
        is_open_network: bool = False,
        has_wps: bool = False,
        dns_servers: List[str] = None
    ) -> SecurityReport:
        score = 100
        issues = []
        recommendations = []

        sec_upper = security_protocol.upper()

        if is_open_network or "OPEN" in sec_upper or "AÇIK" in sec_upper:
            score -= 50
            issues.append("Ağ parola korumasına sahip değil (Açık Ağ).")
            recommendations.append("Açık ağlarda hassas veri iletiminden kaçının veya bir VPN kullanın.")
        elif "WEP" in sec_upper:
            score -= 40
            issues.append("Ağ modası geçmiş ve güvensiz WEP şifrelemesi kullanıyor.")
            recommendations.append("Yönlendirici ayarlarından WPA2-AES veya WPA3 şifrelemesine geçin.")
        elif "WPA-PERSONAL" in sec_upper or "TKIP" in sec_upper:
            score -= 20
            issues.append("Ağ eski WPA1 veya TKIP şifrelemesi kullanıyor.")
            recommendations.append("Şifreleme modunu WPA2-PSK (AES/CCMP) olarak güncelleyin.")
        elif "WPA3" in sec_upper:
            score += 0 # Full score maintained
        elif "WPA2" in sec_upper:
            score -= 5
            recommendations.append("Mümkünse yönlendiricinizde WPA3 (SAE) desteğini aktif edin.")

        if has_wps:
            score -= 15
            issues.append("Yönlendiricide WPS (Wi-Fi Protected Setup) aktif olabilir.")
            recommendations.append("WPS, brute-force PIN saldırılarına karşı kırılabilirdir; modem arayüzünden WPS'i kapatın.")

        score = max(0, min(100, score))

        if score >= 90:
            rating = "Mükemmel"
        elif score >= 75:
            rating = "İyi"
        elif score >= 50:
            rating = "Orta"
        elif score >= 30:
            rating = "Zayıf"
        else:
            rating = "Kritik Güvenlik Riski"

        return SecurityReport(
            score=score,
            rating=rating,
            issues=issues,
            recommendations=recommendations
        )
