from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QPushButton, QMessageBox, QFrame, QLineEdit, QFormLayout, QScrollArea
)
from PySide6.QtCore import Qt, QUrl, QSize, Signal
from PySide6.QtGui import QDesktopServices
from aethernet.utils.config_loader import ConfigManager
from aethernet.gui.icon_manager import IconManager
from aethernet.gui.theme_manager import ThemeManager

class SettingsView(QWidget):
    """Application Settings, API Key Management & Developer Profile View"""

    theme_changed = Signal(str)
    language_changed = Signal(str)

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = ConfigManager()
        self.keys_visible = False

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        lbl_header = QLabel("Uygulama Ayarları & Yapılandırma")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        main_layout.addWidget(lbl_header)

        # Scroll Area Wrapper
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(4, 4, 16, 4)
        layout.setSpacing(16)

        # Settings Card 1: General & Appearance
        card_general = QFrame()
        card_general.setProperty("class", "glass-panel")
        card_general.setStyleSheet("background-color: #0d081a; border: 1px solid #1e1333; border-radius: 12px; padding: 18px;")
        gen_layout = QVBoxLayout(card_general)
        gen_layout.setSpacing(14)

        lbl_gen_title = QLabel("Görünüm ve Tarama Tercihleri")
        lbl_gen_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #a855f7;")
        gen_layout.addWidget(lbl_gen_title)

        form_gen = QFormLayout()
        form_gen.setSpacing(14)
        form_gen.setLabelAlignment(Qt.AlignLeft)

        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["TR (Türkçe)", "EN (English)", "DE (Deutsch)", "ES (Español)"])
        self.combo_lang.setMinimumWidth(260)
        self.combo_lang.setStyleSheet("padding: 6px; background-color: #1a102b; color: white; border: 1px solid #331f54; border-radius: 6px;")
        self.combo_lang.currentTextChanged.connect(self._on_lang_combo_changed)
        form_gen.addRow("Arayüz Dili (Language):", self.combo_lang)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems([
            "Aegis Violet AMOLED (Mor / Siyah)",
            "Cyber-Noir Dark",
            "Digital Fortress",
            "Synthwave",
            "Solar Flare",
            "Tokyo Night",
            "Dracula Pro"
        ])
        self.combo_theme.setMinimumWidth(260)
        self.combo_theme.setStyleSheet("padding: 6px; background-color: #1a102b; color: white; border: 1px solid #331f54; border-radius: 6px;")
        self.combo_theme.currentTextChanged.connect(self._on_theme_combo_changed)
        form_gen.addRow("Tema Paleti (Theme Palette):", self.combo_theme)

        slider_row = QHBoxLayout()
        self.slider_interval = QSlider(Qt.Horizontal)
        self.slider_interval.setRange(2, 30)
        self.slider_interval.setValue(3)
        self.slider_interval.setMinimumWidth(180)
        slider_row.addWidget(self.slider_interval)

        self.lbl_interval_val = QLabel("3 Saniye")
        self.lbl_interval_val.setStyleSheet("color: #a855f7; font-weight: bold;")
        self.slider_interval.valueChanged.connect(lambda v: self.lbl_interval_val.setText(f"{v} Saniye"))
        slider_row.addWidget(self.lbl_interval_val)
        slider_row.addStretch()

        form_gen.addRow("Otomatik Yenileme Aralığı:", slider_row)
        gen_layout.addLayout(form_gen)
        layout.addWidget(card_general)

        # Settings Card 2: AI & API Key Management
        card_ai = QFrame()
        card_ai.setProperty("class", "glass-panel")
        card_ai.setStyleSheet("background-color: #0d081a; border: 1px solid #1e1333; border-radius: 12px; padding: 18px;")
        ai_layout = QVBoxLayout(card_ai)
        ai_layout.setSpacing(14)

        header_ai = QHBoxLayout()
        lbl_ai_title = QLabel("Yapay Zeka (AI) ve API Anahtarı Yönetimi")
        lbl_ai_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #00f2fe;")
        header_ai.addWidget(lbl_ai_title)
        header_ai.addStretch()

        self.btn_toggle_keys = QPushButton(" Keys Göster / Gizle")
        self.btn_toggle_keys.setIcon(IconManager.get_icon("eye", color="#00f2fe", size=14))
        self.btn_toggle_keys.setIconSize(QSize(14, 14))
        self.btn_toggle_keys.setStyleSheet("padding: 6px 12px; background-color: #1a102b; color: #00f2fe; border: 1px solid #331f54; border-radius: 6px;")
        self.btn_toggle_keys.clicked.connect(self._toggle_keys_visibility)
        header_ai.addWidget(self.btn_toggle_keys)

        ai_layout.addLayout(header_ai)

        form_ai = QFormLayout()
        form_ai.setSpacing(12)

        self.combo_ai_primary = QComboBox()
        self.combo_ai_primary.addItems([
            "DeepSeek AI", "Groq Cloud", "Mistral AI", "OpenAI", "Anthropic Claude", "Google Gemini", "Ollama Local"
        ])
        self.combo_ai_primary.setMinimumWidth(260)
        self.combo_ai_primary.setStyleSheet("padding: 6px; background-color: #1a102b; color: white; border: 1px solid #331f54; border-radius: 6px;")
        form_ai.addRow("Birincil AI Sağlayıcı (Primary):", self.combo_ai_primary)

        self.combo_ai_fallback = QComboBox()
        self.combo_ai_fallback.addItems([
            "Groq Cloud", "DeepSeek AI", "Ollama Local", "OpenAI", "Google Gemini", "Mistral AI"
        ])
        self.combo_ai_fallback.setMinimumWidth(260)
        self.combo_ai_fallback.setStyleSheet("padding: 6px; background-color: #1a102b; color: white; border: 1px solid #331f54; border-radius: 6px;")
        form_ai.addRow("Yedek AI Sağlayıcı (Fallback):", self.combo_ai_fallback)

        self.input_ds_key = QLineEdit()
        self.input_ds_key.setEchoMode(QLineEdit.Password)
        self.input_ds_key.setPlaceholderText("sk-...")
        self.input_ds_key.setStyleSheet("padding: 6px; background-color: #1a102b; color: white; border: 1px solid #331f54; border-radius: 6px;")
        form_ai.addRow("DeepSeek API Key:", self.input_ds_key)

        self.input_groq_key = QLineEdit()
        self.input_groq_key.setEchoMode(QLineEdit.Password)
        self.input_groq_key.setPlaceholderText("gsk_...")
        self.input_groq_key.setStyleSheet("padding: 6px; background-color: #1a102b; color: white; border: 1px solid #331f54; border-radius: 6px;")
        form_ai.addRow("Groq Cloud API Key:", self.input_groq_key)

        self.input_oai_key = QLineEdit()
        self.input_oai_key.setEchoMode(QLineEdit.Password)
        self.input_oai_key.setPlaceholderText("sk-proj-...")
        self.input_oai_key.setStyleSheet("padding: 6px; background-color: #1a102b; color: white; border: 1px solid #331f54; border-radius: 6px;")
        form_ai.addRow("OpenAI API Key:", self.input_oai_key)

        ai_layout.addLayout(form_ai)

        btn_save = QPushButton(" Ayarları & API Anahtarlarını Güncelle")
        btn_save.setIcon(IconManager.get_icon("export", color="#ffffff", size=16))
        btn_save.setIconSize(QSize(16, 16))
        btn_save.setStyleSheet("padding: 10px; background-color: #7c3aed; color: white; font-weight: bold; border-radius: 6px;")
        btn_save.clicked.connect(self._save_settings)
        ai_layout.addWidget(btn_save)

        layout.addWidget(card_ai)

        # Settings Card 3: Developer & App Info
        card_dev = QFrame()
        card_dev.setProperty("class", "glass-panel")
        card_dev.setStyleSheet("background-color: #0d081a; border: 1px solid #1e1333; border-radius: 12px; padding: 16px;")
        dev_layout = QVBoxLayout(card_dev)
        dev_layout.setSpacing(10)

        lbl_dev_title = QLabel("Geliştirici ve Sistem Bilgileri")
        lbl_dev_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #4ade80;")
        dev_layout.addWidget(lbl_dev_title)

        lbl_dev_info = QLabel(
            "<b>Uygulama:</b> AetherNet (WiFi & Ağ Yönetim Hub'ı)<br>"
            "<b>Geliştirici:</b> MrSpy00<br>"
            "<b>GitHub Deposu:</b> <a href='https://github.com/MrSpy00/AetherNet' style='color:#a855f7;'>https://github.com/MrSpy00/AetherNet</a>"
        )
        lbl_dev_info.setOpenExternalLinks(True)
        lbl_dev_info.setStyleSheet("color: #e2e8f0; font-size: 13px; line-height: 1.6;")
        dev_layout.addWidget(lbl_dev_info)

        btn_github = QPushButton(" GitHub Profilini Aç (https://github.com/MrSpy00)")
        btn_github.setIcon(IconManager.get_icon("folder", color="#a855f7", size=16))
        btn_github.setIconSize(QSize(16, 16))
        btn_github.setStyleSheet("padding: 8px; background-color: #1a102b; color: #a855f7; border: 1px solid #331f54; border-radius: 6px;")
        btn_github.setCursor(Qt.PointingHandCursor)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/MrSpy00")))
        dev_layout.addWidget(btn_github)

        layout.addWidget(card_dev)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self._load_saved_keys()

    def _toggle_keys_visibility(self):
        self.keys_visible = not self.keys_visible
        mode = QLineEdit.Normal if self.keys_visible else QLineEdit.Password
        self.input_ds_key.setEchoMode(mode)
        self.input_groq_key.setEchoMode(mode)
        self.input_oai_key.setEchoMode(mode)
        icon_name = "eye_off" if self.keys_visible else "eye"
        self.btn_toggle_keys.setIcon(IconManager.get_icon(icon_name, color="#00f2fe", size=14))

    def _load_saved_keys(self):
        self.input_ds_key.setText(self.config_mgr.get("ai.deepseek.api_key", ""))
        self.input_groq_key.setText(self.config_mgr.get("ai.groq.api_key", ""))
        self.input_oai_key.setText(self.config_mgr.get("ai.openai.api_key", ""))

    def _save_settings(self):
        self.config_mgr.set("ai.deepseek.api_key", self.input_ds_key.text().strip())
        self.config_mgr.set("ai.groq.api_key", self.input_groq_key.text().strip())
        self.config_mgr.set("ai.openai.api_key", self.input_oai_key.text().strip())
        self.config_mgr.save_config()
        QMessageBox.information(self, "Başarılı", "Uygulama ayarları ve API anahtarları güncellendi.")

    def update_theme(self, theme_key: str):
        key = ThemeManager.normalize_theme_key(theme_key)
        self.combo_theme.blockSignals(True)
        for i in range(self.combo_theme.count()):
            item_text = self.combo_theme.itemText(i)
            if ThemeManager.normalize_theme_key(item_text) == key:
                self.combo_theme.setCurrentIndex(i)
                break
        self.combo_theme.blockSignals(False)

    def _on_theme_combo_changed(self, text: str):
        theme_key = ThemeManager.normalize_theme_key(text)
        self.theme_changed.emit(theme_key)

    def _on_lang_combo_changed(self, text: str):
        lang_code = "tr" if "TR" in text else ("en" if "EN" in text else ("de" if "DE" in text else "es"))
        self.language_changed.emit(lang_code)
