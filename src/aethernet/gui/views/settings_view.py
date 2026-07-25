from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QDesktopServices
from aethernet.utils.config_loader import ConfigManager
from aethernet.gui.icon_manager import IconManager

class SettingsView(QWidget):
    """Application Settings & Developer Profile View with Vector Icons"""

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = ConfigManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        lbl_header = QLabel("Uygulama Ayarları & Geliştirici Künyesi")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(lbl_header)

        # Settings Panel Card
        card_settings = QFrame()
        card_settings.setProperty("class", "glass-panel")
        card_settings.setStyleSheet("background-color: #0e131f; border: 1px solid #1a2336; border-radius: 12px; padding: 20px;")
        card_layout = QVBoxLayout(card_settings)
        card_layout.setSpacing(16)

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

        # AI Provider Selection
        row_ai = QHBoxLayout()
        row_ai.addWidget(QLabel("AI Sağlayıcı (AI Provider):"))
        self.combo_ai_provider = QComboBox()
        self.combo_ai_provider.addItems([
            "DeepSeek AI",
            "Groq Cloud",
            "Mistral AI",
            "OpenAI",
            "Anthropic Claude",
            "Google Gemini",
            "Ollama Local"
        ])
        row_ai.addWidget(self.combo_ai_provider)
        card_layout.addLayout(row_ai)

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

        # Save Button
        btn_save = QPushButton(" Ayarları Kaydet")
        btn_save.setIcon(IconManager.get_icon("export", color="#ffffff", size=16))
        btn_save.setIconSize(QSize(16, 16))
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(self._save_settings)
        card_layout.addWidget(btn_save)

        layout.addWidget(card_settings)

        layout.addStretch()

        # Developer Info Box (GitHub Link)
        dev_box = QFrame()
        dev_box.setProperty("class", "glass-panel")
        dev_box.setStyleSheet("background-color: #0e131f; border: 1px solid #00f2fe; border-radius: 12px; padding: 20px;")
        dev_layout = QVBoxLayout(dev_box)

        lbl_dev_title = QLabel("⚡ Geliştirici ve Proje Künyesi")
        lbl_dev_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f2fe;")
        dev_layout.addWidget(lbl_dev_title)

        lbl_dev_info = QLabel(
            "<b>Uygulama:</b> AetherNet v0.1.0 PRO (WiFi & Ağ Yönetim Hub'ı)<br>"
            "<b>Geliştirici:</b> MrSpy00<br>"
            "<b>GitHub:</b> <a href='https://github.com/MrSpy00' style='color:#38bdf8;'>https://github.com/MrSpy00</a>"
        )
        lbl_dev_info.setOpenExternalLinks(True)
        lbl_dev_info.setStyleSheet("color: #e2e8f0; font-size: 14px; line-height: 1.6;")
        dev_layout.addWidget(lbl_dev_info)

        btn_github = QPushButton(" GitHub Profilini Aç (https://github.com/MrSpy00)")
        btn_github.setIcon(IconManager.get_icon("folder", color="#00f2fe", size=16))
        btn_github.setIconSize(QSize(16, 16))
        btn_github.setProperty("class", "btn-secondary")
        btn_github.setCursor(Qt.PointingHandCursor)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/MrSpy00")))
        dev_layout.addWidget(btn_github)

        layout.addWidget(dev_box)

    def _save_settings(self):
        lang_code = self.combo_lang.currentText().split()[0].lower()
        self.config_mgr.set("app.language", lang_code)
        self.config_mgr.set("app.refresh_interval", self.slider_interval.value())
        self.config_mgr.save()
        QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi.")
