# ⚡ AetherNet - WiFi & Ağ Yönetim Hub'ı (WiFi & Network Management Hub)

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20%28Qt6%29-green.svg)](https://pypi.org/project/PySide6/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Developer](https://img.shields.io/badge/Developer-MrSpy00-cyan.svg)](https://github.com/MrSpy00)

> **AetherNet**, kablosuz ağ adaptörlerinizi, aktif bağlantılarınızı, kayıtlı profillerinizi ve çevrenizdeki WiFi ortamını eksiksiz görüntüleyip yönetmenizi sağlayan; aynı zamanda gelişmiş ağ tanılamaları, yerel cihaz envanteri, güvenlik/savunma analizleri ve yetkilendirilmiş pentest araç entegrasyonlarını tek bir Cyber-Noir arayüzde birleştiren profesyonel, masaüstü bir ağ yönetim hub'ıdır.

---

## 🇹🇷 Türkçe Dokümantasyon

### 📋 İçindekiler
1. [Proje Vizyonu](#-proje-vizyonu)
2. [Modül ve Özellik Detayları](#-mod%C3%BCl-ve-%C3%B6zellik-detaylar%C4%B1)
3. [Proje Mimarisi ve Klasör Yapısı](#-proje-mimarisi-ve-klas%C3%B6r-yap%C4%B1s%C4%B1)
4. [Sistem Gereksinimleri ve Kurulum](#-sistem-gereksinimleri-ve-kurulum)
5. [Kullanım Rehberi](#-kullan%C4%B1m-rehberi)
6. [Güvenlik, Gizlilik ve Etik Onay](#-g%C3%BCvenlik-gizlilik-ve-etik-onay)
7. [Geliştirici Künyesi](#-geli%C5%9Ftirici-k%C3%BCnyesi)

---

### 🌐 Proje Vizyonu
AetherNet, hem günlük kullanıcılar için *"WiFi'ım neden yavaş?"* veya *"Ağımda kimler var?"* sorularına anında yanıt veren pratik bir kontrol paneli, hem de sistem yöneticileri ve güvenlik uzmanları için genişletilebilir, tip güvenli bir ağ analiz platformudur.

---

### 🛠️ Modül ve Özellik Detayları

#### 1. 📶 WiFi Adaptör & Bağlantı Yönetimi
- **Adaptör İnceleme**: Sistemdeki tüm ağ arayüzlerinin listelenmesi (WiFi, Ethernet, Sanal Adaptörler), MAC adresleri, sürücü sürümleri ve işletim durumları.
- **Canlı Sinyal Takibi**: `pyqtgraph` ile donmadan güncellenen 60 saniyelik sinyal geçmişi grafiği (% ve dBm cinsinden RSSI).
- **Bağlantı Parametreleri**: Aktif SSID, BSSID, radyo standartları (802.11a/b/g/n/ac/ax/be), frekans bandı (2.4/5/6 GHz), kanal genişliği (20/40/80/160 MHz) ve şifreleme tipleri (WPA3-Personal, WPA2-PSK, WEP, Open).
- **Bant Genişliği Sayaçları**: Anlık indirme/yükleme link hızları (Mbps) ve alınan/gönderilen toplam byte/paket sayıları.

#### 2. 🔑 Kayıtlı WiFi Profilleri Yönetimi
- **Profil Listesi**: Sistemde kayıtlı tüm WiFi ağlarının ve güvenlik tiplerinin listelenmesi.
- **Parola Görüntüleme**: Yerel makinede kayıtlı ağ şifrelerinin yönetici (Administrator) izniyle güvenli şekilde görüntülenmesi.
- **Profil Kontrolü**: Ağ bağlantısını tetikleme veya mevcut bağlantıyı kesme.

#### 3. 🔍 Çevresel Ağ & Ortam Taraması
- **Canlı Ortam Taraması**: Çevredeki tüm görünür ve gizli (hidden) SSID/BSSID'lerin listelenmesi.
- **Kanal Çakışma Analizi**: 2.4 GHz ve 5 GHz bantlarında kanal yoğunlukları ve en uygun kanal önerileri.

#### 4. 💻 Yerel Ağ Keşfi & Cihaz Envanteri (ARP Inventory)
- **ARP Taraması**: Aynı alt ağdaki tüm aktif IP ve MAC adreslerinin tespiti.
- **MAC → OUI Üretici Eşleştirme**: Cihazların üreticilerini (Apple, Samsung, Raspberry Pi, TP-Link, Cisco vb.) otomatik tespit etme.
- **Cihaz Tipi Tahminleme**: Router, Akıllı Telefon, IoT cihazı, Sanal Makine veya Bilgisayar sınıflandırması.

#### 5. 🛠️ İnternet ve Ağ Tanılama Araçları
- **📍 Ping & Jitter**: Min/Max/Avg gecikme süreleri, paket kaybı ve seğirme (jitter) analizi.
- **🌐 DNS Sorgulama**: A, AAAA, MX, TXT, NS, CNAME, SOA ve PTR (Ters DNS) kayıtları.
- **🔎 WHOIS & RDAP**: Alan adı kayıt süreleri, registrar ve kamuya açık IP coğrafi konum/ASN bilgileri.
- **🔌 TCP Port Tarayıcı**: Yaygın ve özel portlar için çok izlekli (multithreaded) bağlantı testi.
- **🔒 SSL/TLS Denetleyici**: Sertifika geçerliliği, bitiş tarihi, son gün sayısı, TLS versiyonu ve cipher paketleri.
- **🚀 Bandwidth Speedtest**: İndirme, yükleme ve ping hızı ölçümü.

#### 6. 🛡️ Güvenlik & Savunma Modülleri
- **Ağ Güvenlik Skoru**: Şifreleme standartları, açık ağ riski ve WPS durumuna göre 0-100 arası güvenlik skoru.
- **Sahte AP (Evil Twin / Rogue AP) Tespiti**: Aynı SSID'nin yetkisiz BSSID'lerden veya farklı şifreleme yöntemleriyle yayınlanması durumunda otomatik uyarı.

#### 7. ⚡ Certified Pentest Orchestrator
- **Yetkilendirme Kapısı (Authorization Gate)**: Kullanıcının yalnızca sahibi olduğu veya yazılı izin aldığı ağlarda tarama yapacağını taahhüt ettiği yasal onay ekranı.
- **Harici Araç Entegrasyonu**: Nmap ve Tshark gibi endüstri standardı güvenlik araçlarının güvenli subprocess orkestrasyonu.
- **Audit Logging**: Tüm tarama eylemlerinin zaman damgalı olarak `logs/audit.jsonl` dosyasına kaydedilmesi.

#### 8. 🎨 PySide6 GUI & UX
- **Cyber-Noir Dark Tema**: Neon vurgulara sahip modern QSS arayüz tasarımı.
- **Çoklu Dil (i18n)**: Türkçe (Varsayılan), İngilizce, Almanca ve İspanyolca dil desteği.
- **Geliştirici İmzası**: Ayarlar menüsünde yer alan geliştirici profili ([https://github.com/MrSpy00](https://github.com/MrSpy00)).

---

### 📐 Proje Mimarisi ve Klasör Yapısı

```
AetherNet/
├── .env.example              # Örnek çevre değişkenleri dosyası
├── .gitignore                # Güvenli .gitignore yapılandırması
├── pyproject.toml            # Proje bağımlılıkları ve pytest ayarları
├── README.md                 # Çift dilli proje dokümantasyonu
├── config/
│   └── config.default.yaml   # Varsayılan konfigürasyon dosyası
├── src/
│   └── aethernet/
│       ├── __init__.py
│       ├── main.py           # Uygulama giriş noktası
│       ├── core/             # Veri modelleri (models.py)
│       ├── network_tools/    # Ping, DNS, WHOIS, PortScanner, Speedtest, SSL
│       ├── discovery/        # ARP Discovery & MAC Vendor OUI resolver
│       ├── security/         # Güvenlik puanlayıcı & Evil Twin dedektörü
│       ├── pentest/          # Authorization Gate, Audit Logger & Tool Orchestrator
│       ├── gui/              # PySide6 Arayüzü (ThemeManager, i18n, Views, Components)
│       ├── platform/         # OS Soyutlama katmanı (windows.py)
│       └── utils/            # Logger (loguru) & ConfigLoader
├── tests/
│   └── test_core.py          # Pytest birim testleri
└── scripts/
    └── build_exe.py          # PyInstaller derleme betiği
```

---

### 💻 Sistem Gereksinimleri ve Kurulum

#### Gereksinimler
- **İşletim Sistemi**: Windows 10/11 (Birincil destek), Linux/macOS (Soyutlama katmanı ile genişletilebilir)
- **Python**: v3.11 veya üzeri

#### Adım Adım Kurulum

1. Repoyu bilgisayarınıza klonlayın:
```bash
git clone https://github.com/MrSpy00/AetherNet.git
cd AetherNet
```

2. Sanal bir Python ortamı (venv) oluşturun ve aktifleştirin:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

3. Gerekli bağımlılıkları yükleyin:
```bash
pip install -e .
```

4. Uygulamayı çalıştırın:
```bash
python src/aethernet/main.py
```

5. Birim testleri çalıştırmak için:
```bash
pytest
```

---

### 🔒 Güvenlik, Gizlilik ve Etik Onay

- **Sıfır Veri Sızıntısı**: Kayıtlı profiller, ağ verileri ve tarama geçmişi tamamen yerel makinenizde kalır.
- **Hassas Veri Gizliliği**: `.env` dosyası ve yerel veritabanları varsayılan olarak `.gitignore` ile korunmaktadır.
- **Etik Kullanım Taahhüdü**: Pentest modülü, kullanıcının yasal sorumluluk reddini onaylamaması durumunda çalışmaz.

---

### 👨‍💻 Geliştirici Künyesi

- **Geliştirici / Mimar**: MrSpy00
- **GitHub Profil**: [https://github.com/MrSpy00](https://github.com/MrSpy00)
- **Proje Deposu**: [https://github.com/MrSpy00/AetherNet](https://github.com/MrSpy00/AetherNet)

---
---

## 🇬🇧 English Documentation

### 📋 Table of Contents
1. [Project Vision](#-project-vision)
2. [Modules and Feature Details](#-modules-and-feature-details)
3. [Project Architecture and Directory Structure](#-project-architecture-and-directory-structure)
4. [System Requirements and Installation](#-system-requirements-and-installation)
5. [Usage Guide](#-usage-guide)
6. [Security, Privacy and Ethical Compliance](#-security-privacy-and-ethical-compliance)
7. [Developer Profile](#-developer-profile)

---

### 🌐 Project Vision
AetherNet is an all-in-one desktop network management hub designed to provide immediate answers for everyday questions like *"Why is my WiFi slow?"* or *"Who is on my network?"*, while simultaneously serving as an extensible, type-safe network analysis platform for system administrators and security professionals.

---

### 🛠️ Modules and Feature Details

#### 1. 📶 WiFi Adapter & Connection Management
- **Adapter Inspector**: Enumeration of all system network interfaces (WiFi, Ethernet, Virtual Adapters), MAC addresses, driver versions, and operational statuses.
- **Real-Time Signal Monitor**: Smooth 60-second signal strength history chart powered by `pyqtgraph` (% and dBm RSSI).
- **Connection Parameters**: Detailed active SSID, BSSID, radio standards (802.11a/b/g/n/ac/ax/be), frequency bands (2.4/5/6 GHz), channel width (20/40/80/160 MHz), and security protocols (WPA3-Personal, WPA2-PSK, WEP, Open).
- **Bandwidth Metrics**: Real-time link rates (Mbps) and cumulative sent/received byte and packet counts.

#### 2. 🔑 Saved WiFi Profiles Management
- **Profile Manager**: List all saved WiFi profiles and security types stored on the local machine.
- **Password Revealer**: Securely view saved network passwords with administrative privileges.
- **Connection Trigger**: Seamlessly connect to saved profiles or disconnect from the current network.

#### 3. 🔍 Wireless Environment & Congestion Scanner
- **Live Environment Scanner**: List all visible and hidden SSIDs/BSSIDs in the vicinity.
- **Channel Congestion Analysis**: Analyze channel utilization across 2.4 GHz and 5 GHz bands to suggest optimal channels.

#### 4. 💻 Local Network Discovery & Device Inventory (ARP Inventory)
- **ARP Discovery**: Scan the local subnet to identify active IP and MAC addresses.
- **MAC → OUI Vendor Resolver**: Automatically map device MAC addresses to manufacturers (Apple, Samsung, Raspberry Pi, TP-Link, Cisco, etc.).
- **Device Classification**: Categorize devices into Routers, Smartphones, IoT devices, Virtual Machines, or PCs.

#### 5. 🛠️ Network Diagnostic Tools Suite
- **📍 Ping & Jitter**: Latency statistics (min/max/avg), packet loss percentages, and jitter metrics.
- **🌐 DNS Query**: Query A, AAAA, MX, TXT, NS, CNAME, SOA, and PTR (Reverse DNS) records.
- **🔎 WHOIS & RDAP**: Domain registration dates, registrar info, and public IP geolocation/ASN data.
- **🔌 TCP Port Scanner**: Multi-threaded TCP connect port scanner for common and custom ports.
- **🔒 SSL/TLS Inspector**: Audit SSL/TLS certificate validity, expiration dates, protocol versions, and cipher suites.
- **🚀 Bandwidth Speedtest**: Test download, upload, and latency speeds.

#### 6. 🛡️ Security & Defense Modules
- **Security Scorer**: Calculate a 0-100 network security score based on encryption strength, open network risks, and WPS status.
- **Evil Twin / Rogue AP Detector**: Automatic detection and alerts for rogue access points broadcasting identical SSIDs from unauthorized BSSIDs.

#### 7. ⚡ Certified Pentest Orchestrator
- **Authorization Gate**: Mandatory disclaimer gate requiring user explicit consent to operate only on owned or legally authorized networks.
- **Tool Orchestration**: Safe subprocess orchestration layer for industry-standard tools like Nmap and Tshark.
- **Audit Logging**: Time-stamped JSONL audit trail recorded in `logs/audit.jsonl`.

#### 8. 🎨 PySide6 GUI & UX
- **Cyber-Noir Dark Theme**: Sleek QSS desktop user interface featuring neon cyan accents.
- **Multilingual Support (i18n)**: Native support for Turkish (Default), English, German, and Spanish.
- **Developer Attribution**: Dedicated developer profile card and GitHub link ([https://github.com/MrSpy00](https://github.com/MrSpy00)).

---

### 📐 Project Architecture and Directory Structure

```
AetherNet/
├── .env.example              # Sample environment variables file
├── .gitignore                # Secure gitignore configuration
├── pyproject.toml            # Project dependencies and pytest config
├── README.md                 # Bilingual documentation
├── config/
│   └── config.default.yaml   # Default configuration file
├── src/
│   └── aethernet/
│       ├── __init__.py
│       ├── main.py           # Application entry point
│       ├── core/             # Data models (models.py)
│       ├── network_tools/    # Ping, DNS, WHOIS, PortScanner, Speedtest, SSL
│       ├── discovery/        # ARP Discovery & MAC Vendor OUI resolver
│       ├── security/         # Security Scorer & Evil Twin detector
│       ├── pentest/          # Authorization Gate, Audit Logger & Tool Orchestrator
│       ├── gui/              # PySide6 GUI (ThemeManager, i18n, Views, Components)
│       ├── platform/         # OS Abstraction layer (windows.py)
│       └── utils/            # Logger (loguru) & ConfigLoader
├── tests/
│   └── test_core.py          # Pytest unit tests
└── scripts/
    └── build_exe.py          # PyInstaller build script
```

---

### 💻 System Requirements and Installation

#### Requirements
- **Operating System**: Windows 10/11 (Primary target), Linux/macOS (Extensible via abstraction layer)
- **Python**: v3.11 or higher

#### Step-by-Step Installation

1. Clone the repository:
```bash
git clone https://github.com/MrSpy00/AetherNet.git
cd AetherNet
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

3. Install project dependencies:
```bash
pip install -e .
```

4. Run the application:
```bash
python src/aethernet/main.py
```

5. Run unit tests:
```bash
pytest
```

---

### 🔒 Security, Privacy and Ethical Compliance

- **Zero Remote Data Leakage**: All network scan records, profiles, and logs remain strictly on your local machine.
- **Credential Protection**: The `.env` file and local databases are strictly excluded via `.gitignore`.
- **Ethical Compliance**: The Pentest module remains completely disabled until explicit authorized consent is accepted.

---

### 👨‍💻 Developer Profile

- **Developer / Architect**: MrSpy00
- **GitHub Profile**: [https://github.com/MrSpy00](https://github.com/MrSpy00)
- **Project Repository**: [https://github.com/MrSpy00/AetherNet](https://github.com/MrSpy00/AetherNet)
