from pathlib import Path
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPainterPath
from aethernet.gui.icon_manager import IconManager
from aethernet.gui.theme_manager import ThemeManager
from aethernet.utils.path_utils import get_asset_path

class Sidebar(QFrame):
    """Cyber Navigation Sidebar with Rounded Brand Logo & Vector SVG Icons"""

    nav_changed = Signal(int)

    def __init__(self, i18n_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.i18n = i18n_manager
        self.is_collapsed = False
        self.current_theme = "cyber_dark"
        self.section_labels = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 12)
        layout.setSpacing(4)

        # Header Row: Logo + Brand Title + Collapse Button
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(40)
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(4, 0, 4, 0)
        self.header_layout.setSpacing(6)

        # Rounded Logo Widget
        self.lbl_logo = QLabel()
        self.lbl_logo.setFixedSize(28, 28)
        logo_path = get_asset_path("assets/logo.png")
        if not logo_path.exists():
            logo_path = get_asset_path("assets/icon.ico")
        
        pix = None
        if logo_path.exists():
            pix = QPixmap(str(logo_path))

        if not pix or pix.isNull():
            pix = IconManager.get_pixmap("network", color="#00f2fe", size=28)

        pix_scaled = pix.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        rounded_pix = QPixmap(28, 28)
        rounded_pix.fill(Qt.transparent)
        painter = QPainter(rounded_pix)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, 28, 28, 7, 7)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pix_scaled)
        painter.end()
        self.lbl_logo.setPixmap(rounded_pix)

        self.header_layout.addWidget(self.lbl_logo)

        # Brand Title
        self.lbl_brand = QLabel("AetherNet")
        self.lbl_brand.setObjectName("SidebarHeader")
        self.header_layout.addWidget(self.lbl_brand)
        self.header_layout.addStretch()

        # Collapse / Expand Button
        self.btn_collapse = QPushButton()
        self.btn_collapse.setIcon(IconManager.get_icon("chevron_left", color="#00f2fe", size=14))
        self.btn_collapse.setIconSize(QSize(14, 14))
        self.btn_collapse.setFixedSize(28, 28)
        self.btn_collapse.setCursor(Qt.PointingHandCursor)
        self.btn_collapse.setStyleSheet("""
            QPushButton {
                background-color: #141c2e;
                border: 1px solid #1d273c;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1e293d;
                border-color: #00f2fe;
            }
        """)
        self.btn_collapse.clicked.connect(self.toggle_collapse)
        self.header_layout.addWidget(self.btn_collapse)
        layout.addWidget(self.header_frame)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.icon_mapping = {
            0: ("dashboard", self.i18n.t("dashboard")),
            1: ("wifi", self.i18n.t("wifi_info")),
            2: ("profiles", self.i18n.t("wifi_profiles")),
            3: ("environment", self.i18n.t("environment_scan")),
            4: ("discovery", self.i18n.t("device_discovery")),
            8: ("topology", self.i18n.t("topology_map", "Ağ Topolojisi")),
            11: ("router", "Modem Yönetimi"),
            5: ("tools", self.i18n.t("network_tools")),
            6: ("security", self.i18n.t("security")),
            7: ("pentest", self.i18n.t("pentest")),
            12: ("globe", "API & Tehdit Hub'ı"),
            9: ("settings", self.i18n.t("settings")),
            10: ("logs", "Loglar && Oturumlar")
        }

        # Nav Sections
        self._add_section_label(layout, "GENEL")
        self._add_nav_btn(layout, 0)
        self._add_nav_btn(layout, 1)
        self._add_nav_btn(layout, 2)

        self._add_section_label(layout, "ANALİZ & TESPİT")
        self._add_nav_btn(layout, 3)
        self._add_nav_btn(layout, 4)
        self._add_nav_btn(layout, 8)
        self._add_nav_btn(layout, 11)

        self._add_section_label(layout, "GÜVENLİK & ARAÇLAR")
        self._add_nav_btn(layout, 5)
        self._add_nav_btn(layout, 6)
        self._add_nav_btn(layout, 7)
        self._add_nav_btn(layout, 12)

        self._add_section_label(layout, "SİSTEM")
        self._add_nav_btn(layout, 9)
        self._add_nav_btn(layout, 10)

        layout.addStretch()

        self.lbl_version = QLabel("v0.1.0 | MrSpy00")
        self.lbl_version.setStyleSheet("color: #475569; font-size: 11px; padding: 6px; background: transparent;")
        layout.addWidget(self.lbl_version)

        self.btn_group.idClicked.connect(self._on_button_clicked)

    def _add_section_label(self, layout, text: str):
        lbl = QLabel(text)
        lbl.setProperty("class", "section-label")
        layout.addWidget(lbl)
        self.section_labels.append(lbl)

    def _add_nav_btn(self, layout, index: int):
        icon_name, label_text = self.icon_mapping[index]
        accent = ThemeManager.get_accent_color(self.current_theme)
        btn = QPushButton(f"  {label_text}")
        btn.setIcon(IconManager.get_icon(icon_name, color="#94a3b8", size=18))
        btn.setIconSize(QSize(18, 18))
        btn.setProperty("class", "nav-btn")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        if index == 0:
            btn.setChecked(True)
            btn.setProperty("active", True)
            btn.setIcon(IconManager.get_icon(icon_name, color=accent, size=18))

        self.btn_group.addButton(btn, index)
        layout.addWidget(btn)

    def update_theme(self, theme_name: str):
        self.current_theme = theme_name
        accent = ThemeManager.get_accent_color(theme_name)
        self.btn_collapse.setIcon(IconManager.get_icon("chevron_left" if not self.is_collapsed else "chevron_right", color=accent, size=14))
        
        active_id = self.btn_group.checkedId()
        for btn in self.btn_group.buttons():
            actual_id = self.btn_group.id(btn)
            icon_name, _ = self.icon_mapping[actual_id]
            if actual_id == active_id:
                btn.setIcon(IconManager.get_icon(icon_name, color=accent, size=18))
            else:
                btn.setIcon(IconManager.get_icon(icon_name, color="#94a3b8", size=18))

    def _on_button_clicked(self, index: int):
        accent = ThemeManager.get_accent_color(self.current_theme)
        for btn in self.btn_group.buttons():
            actual_id = self.btn_group.id(btn)
            icon_name, _ = self.icon_mapping[actual_id]
            if actual_id == index:
                btn.setIcon(IconManager.get_icon(icon_name, color=accent, size=18))
            else:
                btn.setIcon(IconManager.get_icon(icon_name, color="#94a3b8", size=18))
        self.nav_changed.emit(index)

    def toggle_collapse(self):
        self.is_collapsed = not self.is_collapsed
        accent = ThemeManager.get_accent_color(self.current_theme)
        if self.is_collapsed:
            self.setFixedWidth(64)
            self.lbl_logo.hide()
            self.lbl_brand.hide()
            self.btn_collapse.setIcon(IconManager.get_icon("chevron_right", color=accent, size=14))
            self.lbl_version.hide()
            for lbl in self.section_labels:
                lbl.hide()
            for btn in self.btn_group.buttons():
                btn.setText("")
        else:
            self.setFixedWidth(240)
            self.lbl_logo.show()
            self.lbl_brand.show()
            self.btn_collapse.setIcon(IconManager.get_icon("chevron_left", color=accent, size=14))
            self.lbl_version.show()
            for lbl in self.section_labels:
                lbl.show()
            for btn in self.btn_group.buttons():
                actual_id = self.btn_group.id(btn)
                _, label_text = self.icon_mapping[actual_id]
                btn.setText(f"  {label_text}")
