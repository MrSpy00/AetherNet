from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QComboBox
from PySide6.QtCore import Signal, Qt, QSize
from aethernet.gui.icon_manager import IconManager
from aethernet.gui.theme_manager import ThemeManager

class TopBar(QFrame):
    """Modern Top Navigation & Status Header Bar with Vector Icons & Theme Sync"""

    refresh_requested = Signal()
    theme_changed = Signal(str)

    def __init__(self, i18n_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("TopBar")
        self.i18n = i18n_manager
        self.current_theme = "cyber_dark"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(14)

        # Active Network Status Pill
        self.status_pill = QFrame()
        self.status_pill.setStyleSheet("""
            QFrame {
                background-color: #141c2e;
                border: 1px solid #1d273c;
                border-radius: 16px;
                padding: 4px 12px;
            }
        """)
        pill_layout = QHBoxLayout(self.status_pill)
        pill_layout.setContentsMargins(8, 2, 8, 2)
        pill_layout.setSpacing(8)

        accent = ThemeManager.get_accent_color(self.current_theme)
        self.lbl_status_icon = QLabel()
        self.lbl_status_icon.setPixmap(IconManager.get_pixmap("wifi", color=accent, size=16))
        self.lbl_status_text = QLabel("Ağ Durumu: Taranıyor...")
        self.lbl_status_text.setStyleSheet(f"color: {accent}; font-weight: bold; font-size: 12px; background: transparent;")

        pill_layout.addWidget(self.lbl_status_icon)
        pill_layout.addWidget(self.lbl_status_text)
        layout.addWidget(self.status_pill)

        # IP Address Badge
        self.lbl_ip_badge = QLabel("IP: ---.---.---.---")
        self.lbl_ip_badge.setStyleSheet("""
            QLabel {
                background-color: #0d1522;
                color: #94a3b8;
                border: 1px solid #1a2538;
                border-radius: 12px;
                padding: 4px 12px;
                font-family: 'Consolas', monospace;
                font-size: 11.5px;
            }
        """)
        layout.addWidget(self.lbl_ip_badge)

        layout.addStretch()

        # Quick Refresh Button
        self.btn_refresh = QPushButton(" Refresh")
        self.btn_refresh.setIcon(IconManager.get_icon("refresh", color=accent, size=16))
        self.btn_refresh.setIconSize(QSize(16, 16))
        self.btn_refresh.setProperty("class", "btn-secondary")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.clicked.connect(lambda: self.refresh_requested.emit())
        layout.addWidget(self.btn_refresh)

        # Theme Switcher Dropdown
        self.combo_theme = QComboBox()
        self.combo_theme.addItems([
            "Cyber-Noir",
            "Digital Fortress",
            "Synthwave",
            "Solar Flare",
            "Tokyo Night",
            "Dracula Pro"
        ])
        self.combo_theme.setStyleSheet("padding: 4px 8px; font-size: 12px;")
        self.combo_theme.currentTextChanged.connect(self._on_theme_changed)
        layout.addWidget(self.combo_theme)

    def update_status(self, connected: bool, ssid: str = "", ip: str = ""):
        accent = ThemeManager.get_accent_color(self.current_theme)
        if connected:
            self.lbl_status_icon.setPixmap(IconManager.get_pixmap("wifi", color=accent, size=16))
            self.lbl_status_text.setText(f"Bağlı: {ssid}")
            self.lbl_status_text.setStyleSheet(f"color: {accent}; font-weight: bold; font-size: 12px; background: transparent;")
            self.lbl_ip_badge.setText(f"IP: {ip or 'Etkin'}")
        else:
            self.lbl_status_icon.setPixmap(IconManager.get_pixmap("wifi", color="#ef4444", size=16))
            self.lbl_status_text.setText("Bağlantı Yok")
            self.lbl_status_text.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 12px; background: transparent;")
            self.lbl_ip_badge.setText("IP: Çevrimdışı")

    def update_theme(self, theme_name: str):
        self.current_theme = theme_name
        accent = ThemeManager.get_accent_color(theme_name)
        self.btn_refresh.setIcon(IconManager.get_icon("refresh", color=accent, size=16))

    def _on_theme_changed(self, text: str):
        mapping = {
            "Cyber-Noir": "cyber_dark",
            "Digital Fortress": "digital_fortress",
            "Synthwave": "synthwave",
            "Solar Flare": "solar_flare",
            "Tokyo Night": "tokyo_night",
            "Dracula Pro": "dracula_pro"
        }
        theme_key = mapping.get(text, "cyber_dark")
        self.update_theme(theme_key)
        self.theme_changed.emit(theme_key)
