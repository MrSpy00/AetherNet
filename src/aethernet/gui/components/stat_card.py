from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class StatCard(QFrame):
    """Modern metric summary card widget"""

    def __init__(self, title: str, value: str = "--", subtitle: str = "", accent_color: str = "#00f2fe", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setProperty("class", "stat-card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        self.lbl_title = QLabel(title)
        self.lbl_title.setProperty("class", "stat-title")

        self.lbl_value = QLabel(value)
        self.lbl_value.setProperty("class", "stat-value")
        self.lbl_value.setStyleSheet(f"color: {accent_color};")

        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet("color: #64748b; font-size: 11px;")

        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_value)
        if subtitle:
            layout.addWidget(self.lbl_sub)

    def set_value(self, value: str, subtitle: str = None):
        self.lbl_value.setText(value)
        if subtitle is not None:
            self.lbl_sub.setText(subtitle)
