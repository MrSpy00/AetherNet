# ⚡ AetherNet - WiFi & Ağ Yönetim Hub'ı

**AetherNet**, Python 3.11+ ve PySide6 (Qt6) ile geliştirilmiş, modern masaüstü GUI arayüzüne sahip, modüler, kapsamlı bir WiFi ve Ağ Yönetim Hub'ıdır.

---

## 🌟 Öne Çıkan Özellikler

- **📶 WiFi Adaptör & Bağlantı Detayları**: Adaptör listesi, MAC adresi, sürücü bilgileri, anlık RSSI (dBm ve %), canlı sinyal gücü grafiği, link hızları (Mbps), kanal, bant (2.4/5/6 GHz) ve şifreleme protokolü (WPA3/WPA2/Open).
- **🔑 Kayıtlı WiFi Profilleri**: Sistemdeki kayıtlı profillerin yönetimi ve yönetici onaylı şifre görüntüleme.
- **🔍 Çevre Taraması & Ortam Analizi**: Görünür tüm kablosuz ağların canlı taraması, kanal doluluk takibi ve gizli SSID tespiti.
- **💻 Yerel Ağ Keşfi (ARP Inventory)**: Ağdaki aktif cihazların tespiti, MAC-OUI üretici çözümlemesi ve cihaz tipi tahminleme.
- **🛠️ Ağ Araçları Paketi**:
  - **📍 Ping & Jitter**: Gecikme istatistikleri ve paket kaybı.
  - **🌐 DNS Sorgulama**: A, AAAA, MX, TXT, NS, CNAME, SOA ve PTR kayıtları.
  - **🔎 WHOIS / RDAP & IP Geolocation**: Domain ve IP kayıt/coğrafi konum bilgileri.
  - **🔌 Port Tarayıcı**: Çok izlekli (multithreaded) TCP connect taraması.
  - **🚀 Hız Testi**: İndirme, yükleme ve ping hızı ölçümü.
  - **🔒 SSL/TLS Denetleyici**: Sertifika geçerliliği, kalan gün sayısı ve şifreleme paketleri.
- **🛡️ Güvenlik & Sahte AP (Evil Twin) Tespiti**: Otomatik ağ güvenlik puanlaması ve şüpheli çift SSID/BSSID tespiti.
- **⚡ Certified Pentest Orchestrator**: Nmap vb. araçlar için yetkilendirme onay kapısı (Authorization Gate) ve Audit Loglama.
- **🎨 Modern Cyber-Noir Tema & Çoklu Dil**: PySide6 QSS stili, `pyqtgraph` canlı grafikleri ve Türkçe, İngilizce, Almanca, İspanyolca dil desteği.

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.11+
- Windows 10/11 (Önerilen)

### Adımlar

1. Depoyu klonlayın:
```bash
git clone https://github.com/MrSpy00/AetherNet.git
cd AetherNet
```

2. Sanal ortam oluşturun ve aktif edin:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -e .
```

4. Uygulamayı başlatın:
```bash
python src/aethernet/main.py
```

---

## 👨‍💻 Geliştirici

- **Geliştirici**: MrSpy00
- **GitHub**: [https://github.com/MrSpy00](https://github.com/MrSpy00)

---

## ⚖️ Yasal & Etik Kullanım Uyarısı

AetherNet içerisindeki ağ tarama ve pentest araçları yalnızca **kendi mülkiyetinizde olan veya açık yazılı izin aldığınız ağlarda** kullanılmak üzere tasarlanmıştır. İzinsiz ağ analizi veya müdahalesi yasal sorumluluk doğurabilir.
