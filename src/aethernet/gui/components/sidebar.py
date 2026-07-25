from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PySide6.QtCore import Signal

class Sidebar(QFrame):
    """Cyber Navigation Sidebar"""

    nav_changed = Signal(int)

    def __init__(self, i18n_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.i18n = i18n_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(8)

        # App Brand Header
        self.lbl_brand = QLabel("⚡ AetherNet")
        self.lbl_brand.setObjectName("SidebarHeader")
        layout.addWidget(self.lbl_brand)

        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        self.nav_items = [
            (0, "📊 " + self.i18n.t("dashboard")),
            (1, "📶 " + self.i18n.t("wifi_info")),
            (2, "🔑 " + self.i18n.t("wifi_profiles")),
            (3, "🔍 " + self.i18n.t("environment_scan")),
            (4, "💻 " + self.i18n.t("device_discovery")),
            (5, "🛠️ " + self.i18n.t("network_tools")),
            (6, "🛡️ " + self.i18n.t("security")),
            (7, "⚡ " + self.i18n.t("pentest")),
            (8, "⚙️ " + self.i18n.t("settings")),
        ]

        for index, label_text in self.nav_items:
            btn = QPushButton(label_text)
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            if index == 0:
                btn.setChecked(True)
                btn.setProperty("active", True)
            self.btn_group.addButton(btn, index)
            layout.addWidget(btn)

        layout.addStretch()

        self.lbl_version = QLabel("v0.1.0 | MrSpy00")
        self.lbl_version.setStyleSheet("color: #475569; font-size: 11px; padding: 8px;")
        layout.addWidget(self.lbl_version)

        self.btn_group.idClicked.connect(self._on_button_clicked)

    def _on_button_clicked(self, index: int):
        self.nav_changed.emit(index)
