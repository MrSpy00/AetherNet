from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from aethernet.gui.animations import GlowEffectHelper

class StatCard(QFrame):
    """Modern glassmorphic metric summary card widget with glow & trend badge"""

    def __init__(self, title: str, value: str = "--", subtitle: str = "", accent_color: str = "#00f2fe", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setProperty("class", "stat-card")
        self.accent_color = accent_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        # Header Row: Title + Badge
        header_row = QHBoxLayout()
        self.lbl_title = QLabel(title)
        self.lbl_title.setProperty("class", "stat-title")
        header_row.addWidget(self.lbl_title)

        self.lbl_badge = QLabel("LIVE")
        self.lbl_badge.setStyleSheet(f"""
            QLabel {{
                background-color: rgba(0, 242, 254, 0.12);
                color: {accent_color};
                border: 1px solid {accent_color};
                border-radius: 8px;
                padding: 1px 6px;
                font-size: 9.5px;
                font-weight: bold;
            }}
        """)
        header_row.addWidget(self.lbl_badge)
        header_row.addStretch()
        layout.addLayout(header_row)

        # Value Label
        self.lbl_value = QLabel(value)
        self.lbl_value.setProperty("class", "stat-value")
        self.lbl_value.setStyleSheet(f"color: {accent_color}; font-size: 26px; font-weight: 800;")
        layout.addWidget(self.lbl_value)

        # Subtitle
        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 500;")
        layout.addWidget(self.lbl_sub)

        # Glow shadow
        GlowEffectHelper.apply_glow(self, accent_color, blur_radius=15, offset_y=2)

    def set_value(self, value: str, subtitle: str = None, badge_text: str = None):
        self.lbl_value.setText(value)
        if subtitle is not None:
            self.lbl_sub.setText(subtitle)
        if badge_text is not None:
            self.lbl_badge.setText(badge_text)
