from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QMessageBox, QFrame, QLineEdit
)
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QDesktopServices
from aethernet.utils.config_loader import ConfigManager
from aethernet.gui.icon_manager import IconManager

class SettingsView(QWidget):
    """Application Settings, API Key Management & Developer Profile View"""

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = ConfigManager()
        self.keys_visible = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        lbl_header = QLabel("Uygulama Ayarları & Gelişmiş Yapılandırma")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(lbl_header)

        # Settings Panel Card
        card_settings = QFrame()
        card_settings.setProperty("class", "glass-panel")
        card_settings.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 18px;")
        card_layout = QVBoxLayout(card_settings)
        card_layout.setSpacing(14)

        # Language Selection
        row_lang = QHBoxLayout()
        row_lang.addWidget(QLabel("Arayüz Dili (Language):"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["TR (Türkçe)", "EN (English)", "DE (Deutsch)", "ES (Español)"])
        row_lang.addWidget(self.combo_lang)
        card_layout.addLayout(row_lang)

        # Theme Selection
        row_theme = QHBoxLayout()
        row_theme.addWidget(QLabel("Tema (Theme Palette):"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems([
            "Cyber-Noir Dark",
            "Digital Fortress",
            "Synthwave",
            "Solar Flare",
            "Tokyo Night",
            "Dracula Pro"
        ])
        row_theme.addWidget(self.combo_theme)
        card_layout.addLayout(row_theme)

        # AI Primary Provider Selection
        row_ai_primary = QHBoxLayout()
        row_ai_primary.addWidget(QLabel("Birincil AI Sağlayıcı (Primary AI):"))
        self.combo_ai_primary = QComboBox()
        self.combo_ai_primary.addItems([
            "DeepSeek AI",
            "Groq Cloud",
            "Mistral AI",
            "OpenAI",
            "Anthropic Claude",
            "Google Gemini",
            "Ollama Local"
        ])
        row_ai_primary.addWidget(self.combo_ai_primary)
        card_layout.addLayout(row_ai_primary)

        # AI Fallback Provider Selection
        row_ai_fallback = QHBoxLayout()
        row_ai_fallback.addWidget(QLabel("Yedek AI Sağlayıcı (Fallback AI):"))
        self.combo_ai_fallback = QComboBox()
        self.combo_ai_fallback.addItems([
            "Groq Cloud",
            "DeepSeek AI",
            "Ollama Local",
            "OpenAI",
            "Google Gemini",
            "Mistral AI"
        ])
        row_ai_fallback.addWidget(self.combo_ai_fallback)
        card_layout.addLayout(row_ai_fallback)

        # Scan Interval Slider
        row_interval = QHBoxLayout()
        row_interval.addWidget(QLabel("Yenileme Aralığı (Saniye):"))
        self.slider_interval = QSlider(Qt.Horizontal)
        self.slider_interval.setRange(2, 30)
        self.slider_interval.setValue(3)
        self.slider_interval.setFixedWidth(160)
        row_interval.addWidget(self.slider_interval)

        self.lbl_interval_val = QLabel("3 Sn")
        self.lbl_interval_val.setStyleSheet("color: #00f2fe; font-weight: bold;")
        self.slider_interval.valueChanged.connect(lambda v: self.lbl_interval_val.setText(f"{v} Sn"))
        row_interval.addWidget(self.lbl_interval_val)

        card_layout.addLayout(row_interval)
        layout.addWidget(card_settings)

        # API Keys Management Panel
        card_keys = QFrame()
        card_keys.setProperty("class", "glass-panel")
        card_keys.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 18px;")
        keys_layout = QVBoxLayout(card_keys)
        keys_layout.setSpacing(12)

        lbl_keys_title = QHBoxLayout()
        lbl_keys_header = QLabel("🔑 AI Servis API Anahtarları (API Key Management)")
        lbl_keys_header.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        lbl_keys_title.addWidget(lbl_keys_header)

        lbl_keys_title.addStretch()

        self.btn_toggle_keys = QPushButton(" Gözter/Gizle")
        self.btn_toggle_keys.setIcon(IconManager.get_icon("eye", color="#38bdf8", size=14))
        self.btn_toggle_keys.setIconSize(QSize(14, 14))
        self.btn_toggle_keys.setProperty("class", "btn-secondary")
        self.btn_toggle_keys.clicked.connect(self._toggle_keys_visibility)
        lbl_keys_title.addWidget(self.btn_toggle_keys)

        keys_layout.addLayout(lbl_keys_title)

        # DeepSeek API Key
        row_ds = QHBoxLayout()
        row_ds.addWidget(QLabel("DeepSeek API Key:"))
        self.input_ds_key = QLineEdit()
        self.input_ds_key.setEchoMode(QLineEdit.Password)
        self.input_ds_key.setPlaceholderText("sk-...")
        row_ds.addWidget(self.input_ds_key)
        keys_layout.addLayout(row_ds)

        # Groq API Key
        row_groq = QHBoxLayout()
        row_groq.addWidget(QLabel("Groq Cloud API Key:"))
        self.input_groq_key = QLineEdit()
        self.input_groq_key.setEchoMode(QLineEdit.Password)
        self.input_groq_key.setPlaceholderText("gsk_...")
        row_groq.addWidget(self.input_groq_key)
        keys_layout.addLayout(row_groq)

        # OpenAI API Key
        row_oai = QHBoxLayout()
        row_oai.addWidget(QLabel("OpenAI API Key:"))
        self.input_oai_key = QLineEdit()
        self.input_oai_key.setEchoMode(QLineEdit.Password)
        self.input_oai_key.setPlaceholderText("sk-proj-...")
        row_oai.addWidget(self.input_oai_key)
        keys_layout.addLayout(row_oai)

        # Save Button
        btn_save = QPushButton(" Ayarları & API Anahtarlarını Kaydet")
        btn_save.setIcon(IconManager.get_icon("export", color="#ffffff", size=16))
        btn_save.setIconSize(QSize(16, 16))
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(self._save_settings)
        keys_layout.addWidget(btn_save)

        layout.addWidget(card_keys)

        # Developer Info Box (GitHub Link)
        dev_box = QFrame()
        dev_box.setProperty("class", "glass-panel")
        dev_box.setStyleSheet("background-color: #0e131f; border: 1px solid #00f2fe; border-radius: 12px; padding: 16px;")
        dev_layout = QVBoxLayout(dev_box)

        lbl_dev_title = QLabel("Geliştirici ve Proje Künyesi")
        lbl_dev_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #00f2fe;")
        dev_layout.addWidget(lbl_dev_title)

        lbl_dev_info = QLabel(
            "<b>Uygulama:</b> AetherNet (WiFi & Ağ Yönetim Hub'ı)<br>"
            "<b>Geliştirici:</b> MrSpy00<br>"
            "<b>GitHub Deposu:</b> <a href='https://github.com/MrSpy00/AetherNet' style='color:#38bdf8;'>https://github.com/MrSpy00/AetherNet</a>"
        )
        lbl_dev_info.setOpenExternalLinks(True)
        lbl_dev_info.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 1.5;")
        dev_layout.addWidget(lbl_dev_info)

        btn_github = QPushButton(" GitHub Profilini Aç (https://github.com/MrSpy00)")
        btn_github.setIcon(IconManager.get_icon("folder", color="#00f2fe", size=16))
        btn_github.setIconSize(QSize(16, 16))
        btn_github.setProperty("class", "btn-secondary")
        btn_github.setCursor(Qt.PointingHandCursor)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/MrSpy00")))
        dev_layout.addWidget(btn_github)

        layout.addWidget(dev_box)

        self._load_saved_keys()

    def _toggle_keys_visibility(self):
        self.keys_visible = not self.keys_visible
        mode = QLineEdit.Normal if self.keys_visible else QLineEdit.Password
        self.input_ds_key.setEchoMode(mode)
        self.input_groq_key.setEchoMode(mode)
        self.input_oai_key.setEchoMode(mode)
        icon_name = "eye_off" if self.keys_visible else "eye"
        self.btn_toggle_keys.setIcon(IconManager.get_icon(icon_name, color="#38bdf8", size=14))

    def _load_saved_keys(self):
        self.input_ds_key.setText(self.config_mgr.get("ai.deepseek.api_key", ""))
        self.input_groq_key.setText(self.config_mgr.get("ai.groq.api_key", ""))
        self.input_oai_key.setText(self.config_mgr.get("ai.openai.api_key", ""))

    def _save_settings(self):
        lang_code = self.combo_lang.currentText().split()[0].lower()
        self.config_mgr.set("app.language", lang_code)
        self.config_mgr.set("app.refresh_interval", self.slider_interval.value())
        self.config_mgr.set("ai.primary_provider", self.combo_ai_primary.currentText())
        self.config_mgr.set("ai.fallback_provider", self.combo_ai_fallback.currentText())
        self.config_mgr.set("ai.deepseek.api_key", self.input_ds_key.text().strip())
        self.config_mgr.set("ai.groq.api_key", self.input_groq_key.text().strip())
        self.config_mgr.set("ai.openai.api_key", self.input_oai_key.text().strip())
        self.config_mgr.save()
        QMessageBox.information(self, "Başarılı", "Ayarlar ve API anahtarları başarıyla güncellendi.")
