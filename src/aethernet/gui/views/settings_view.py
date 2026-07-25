from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from aethernet.utils.config_loader import ConfigManager

class SettingsView(QWidget):
    """Application Settings & Developer Profile View"""

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.config_mgr = ConfigManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        lbl_header = QLabel("Uygulama Ayarları")
        lbl_header.setStyleSheet("font-size: 20px; font-weight: bold; color: #f8fafc;")
        layout.addWidget(lbl_header)

        # Language Selection
        row_lang = QHBoxLayout()
        row_lang.addWidget(QLabel("Arayüz Dili (Language):"))
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["TR (Türkçe)", "EN (English)", "DE (Deutsch)", "ES (Español)"])
        row_lang.addWidget(self.combo_lang)
        layout.addLayout(row_lang)

        # Theme Selection
        row_theme = QHBoxLayout()
        row_theme.addWidget(QLabel("Tema (Theme):"))
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Cyber-Noir Dark", "Digital Fortress", "Minimal Light"])
        row_theme.addWidget(self.combo_theme)
        layout.addLayout(row_theme)

        # Scan Interval
        row_interval = QHBoxLayout()
        row_interval.addWidget(QLabel("Otomatik Yenileme Aralığı (Saniye):"))
        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(2, 60)
        self.spin_interval.setValue(3)
        row_interval.addWidget(self.spin_interval)
        layout.addLayout(row_interval)

        # Save Button
        btn_save = QPushButton("💾 Ayarları Kaydet")
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(self._save_settings)
        layout.addWidget(btn_save)

        layout.addStretch()

        # Developer Info Box (Mandatory GitHub Link)
        dev_box = QWidget()
        dev_box.setStyleSheet("background-color: #141a26; border: 1px solid #00f2fe; border-radius: 12px; padding: 20px;")
        dev_layout = QVBoxLayout(dev_box)

        lbl_dev_title = QLabel("⚡ Geliştirici ve Proje Künyesi")
        lbl_dev_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00f2fe;")
        dev_layout.addWidget(lbl_dev_title)

        lbl_dev_info = QLabel(
            "<b>Uygulama:</b> AetherNet v0.1.0 (WiFi & Ağ Yönetim Hub'ı)<br>"
            "<b>Geliştirici:</b> MrSpy00<br>"
            "<b>GitHub:</b> <a href='https://github.com/MrSpy00' style='color:#38bdf8;'>https://github.com/MrSpy00</a>"
        )
        lbl_dev_info.setOpenExternalLinks(True)
        lbl_dev_info.setStyleSheet("color: #e2e8f0; font-size: 14px; line-height: 1.6;")
        dev_layout.addWidget(lbl_dev_info)

        btn_github = QPushButton("🌐 GitHub Profilini Aç (https://github.com/MrSpy00)")
        btn_github.setProperty("class", "btn-secondary")
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/MrSpy00")))
        dev_layout.addWidget(btn_github)

        layout.addWidget(dev_box)

    def _save_settings(self):
        lang_code = self.combo_lang.currentText().split()[0].lower()
        self.config_mgr.set("app.language", lang_code)
        self.config_mgr.set("app.refresh_interval", self.spin_interval.value())
        self.config_mgr.save()
        QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi.")
